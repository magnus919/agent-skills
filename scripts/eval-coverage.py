#!/usr/bin/env python3
"""Report eval coverage across skills and enforce ratchet thresholds.

Phase 2: informational coverage report (always passes).
Phase 3: ratchet — warn at 25%, fail-on-modify at 50%.

Usage:
  python3 scripts/eval-coverage.py                    # human-readable report
  python3 scripts/eval-coverage.py --json             # machine-readable
  python3 scripts/eval-coverage.py --modified-from REF  # ratchet check
"""

import argparse
import io
import json
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path

from eval_validation import NOT_ASSESSED, STATE_NAMES, ValidationResult, validate_manifest

ROOT = Path(__file__).resolve().parent.parent

# Phase 3 ratchet thresholds (percent of skills with evals)
WARN_THRESHOLD = 25  # modified skills without evals get a warning
FAIL_THRESHOLD = 50  # modified skills without evals fail CI

# Pathspec that matches every tracked file under a canonical skill directory.
# A canonical skill lives at <root>/<skill-name>/SKILL.md or
# <root>/bundles/<bundle-name>/skills/<skill-name>/SKILL.md.  The glob
# ``*/SKILL.md`` covers the first shape; ``bundles/*/skills/*/SKILL.md``
# covers the second.  We use the same glob for both ls-files and diff so
# that modified-skill detection sees the same universe as find_skills().
SKILL_PATHSPEC = ":(glob)**/SKILL.md"


def find_skills() -> list[Path]:
    """Find all canonical skill directories via git-tracked SKILL.md files."""
    result = subprocess.run(
        ["git", "ls-files", "-z", "--", SKILL_PATHSPEC],
        cwd=ROOT,
        check=True,
        capture_output=True,
    )
    skills = []
    for name in result.stdout.decode().split("\0"):
        if not name or "/agent-council/profiles/skills/" in name:
            continue
        skills.append(Path(name).parent)
    return sorted(skills)


def resolve_ref_to_commit(ref: str) -> str:
    """Resolve *ref* to a commit SHA or raise ValueError.

    The caller must use only the returned SHA in subsequent git commands.
    """
    result = subprocess.run(
        ["git", "rev-parse", "--verify", "--end-of-options", f"{ref}^{{commit}}"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise ValueError(f"invalid --modified-from ref: {ref!r} is not an existing commit")
    return result.stdout.strip()


def find_skills_at(ref: str) -> list[Path]:
    """Find canonical skill directories tracked at a git revision."""
    result = subprocess.run(
        ["git", "ls-tree", "-r", "--name-only", ref, "--"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    skills = []
    for name in result.stdout.splitlines():
        if name.endswith("/SKILL.md") and "/agent-council/profiles/skills/" not in name:
            skills.append(Path(name).parent)
    return sorted(skills)


def check_eval_states(skill_dir: Path) -> ValidationResult:
    """Return validation and evidence states for one skill."""
    evals_file = ROOT / skill_dir / "evals" / "evals.json"
    return validate_manifest(evals_file, ROOT)


def check_evals(skill_dir: Path) -> tuple[bool, int]:
    """Return (has_schema_valid_manifest, case_count) for compatibility."""
    result = check_eval_states(skill_dir)
    return result.states["schema_valid"] is True, result.case_count


def count_references(skill_name: str, all_skill_dirs: list[Path]) -> int:
    """Count how many other SKILL.md files mention this skill name."""
    count = 0
    for skill_dir in all_skill_dirs:
        skill_md = ROOT / skill_dir / "SKILL.md"
        if not skill_md.exists():
            continue
        try:
            if skill_name in skill_md.read_text(encoding="utf-8"):
                count += 1
        except OSError:
            pass
    return count


def modified_skills(base_ref_commit: str) -> set[Path]:
    """Return skill directories with any tracked file changed since base_ref.

    A skill is considered modified when *any* file under its directory
    changes — not just SKILL.md.  This covers references, scripts,
    fixtures, README, and eval manifests.
    """
    result = subprocess.run(
        ["git", "diff", "--name-only", base_ref_commit, "HEAD", "--"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    changed_files = [
        line
        for line in result.stdout.strip().splitlines()
        if line and "/agent-council/profiles/skills/" not in line
    ]
    # Map each changed file to its owning skill directory by checking
    # whether the file path starts with a known skill directory prefix.
    # Include skills from both revisions so complete directory deletions
    # remain observable under their old name.
    known_skills = sorted(
        set(find_skills()) | set(find_skills_at(base_ref_commit)),
        key=lambda path: len(path.parts),
        reverse=True,
    )
    modified: set[Path] = set()
    for changed in changed_files:
        changed_path = Path(changed)
        for skill_dir in known_skills:
            try:
                changed_path.relative_to(skill_dir)
                modified.add(skill_dir)
                break
            except ValueError:
                continue
    return modified


def evaluate_ratchet(
    modified: set[Path],
    current: set[Path],
    without_evals: set[Path],
    coverage_pct: float,
) -> tuple[list[str], list[str]]:
    """Apply warning and failure thresholds to modified current skills."""
    warnings: list[str] = []
    errors: list[str] = []
    for skill_dir in sorted(modified & current & without_evals):
        name = str(skill_dir)
        if coverage_pct >= FAIL_THRESHOLD:
            errors.append(
                f"{name}: modified skill has no schema-valid eval manifest "
                f"(coverage {coverage_pct:.1f}% >= {FAIL_THRESHOLD}% — "
                "evals required on modification)"
            )
        elif coverage_pct >= WARN_THRESHOLD:
            warnings.append(
                f"{name}: modified skill has no schema-valid eval manifest "
                f"(coverage {coverage_pct:.1f}% >= {WARN_THRESHOLD}% — "
                "evals recommended)"
            )
    return warnings, errors


def coverage_decreased(base_ref_commit: str) -> tuple[bool, float, float]:
    """Compare schema-valid eval coverage for skills retained across revisions.

    Removed skills do not count as a regression; retained skills losing a
    valid manifest do. New skills are governed by the modified-skill ratchet.
    """
    head_skills = find_skills()

    # Compare only skills present at both revisions. Removing a skill should
    # not count as a coverage regression, while removing or invalidating the
    # eval manifest of a retained skill still must fail the ratchet.
    base_skill_dirs = set(find_skills_at(base_ref_commit))
    retained_skill_dirs = base_skill_dirs & set(head_skills)
    base_with = 0
    archive = subprocess.run(
        ["git", "archive", "--format=tar", base_ref_commit, "--"],
        cwd=ROOT,
        check=True,
        capture_output=True,
    ).stdout
    with tempfile.TemporaryDirectory() as tmp:
        snapshot = Path(tmp)
        with tarfile.open(fileobj=io.BytesIO(archive), mode="r:") as tar:
            tar.extractall(snapshot, filter="data")
        subprocess.run(["git", "init", "-q"], cwd=snapshot, check=True)
        subprocess.run(
            ["git", "add", "-f", "--all"],
            cwd=snapshot,
            check=True,
            capture_output=True,
        )
        for skill_dir in retained_skill_dirs:
            manifest = snapshot / skill_dir / "evals" / "evals.json"
            if validate_manifest(manifest, snapshot).states["schema_valid"] is True:
                base_with += 1

    # Use the same retained-skill population on both sides of the comparison.
    # New and deleted skills are handled by their own ratchet rules.
    head_with_retained = sum(1 for skill_dir in retained_skill_dirs if check_evals(skill_dir)[0])
    base_pct = base_with / len(retained_skill_dirs) * 100 if retained_skill_dirs else 0.0
    head_pct = head_with_retained / len(retained_skill_dirs) * 100 if retained_skill_dirs else 0.0
    return head_pct < base_pct, base_pct, head_pct


def main() -> int:
    parser = argparse.ArgumentParser(description="Eval coverage report and ratchet")
    parser.add_argument("--json", action="store_true", help="JSON output")
    parser.add_argument(
        "--modified-from",
        metavar="REF",
        help="Apply ratchet only to skills modified since REF",
    )
    args = parser.parse_args()

    resolved_base_ref = None
    if args.modified_from:
        try:
            resolved_base_ref = resolve_ref_to_commit(args.modified_from)
        except ValueError as exc:
            print(f"ERROR: {exc}", file=sys.stderr)
            return 2

    skills = find_skills()

    total = len(skills)
    skill_states: list[dict[str, object]] = []
    without_evals: list[str] = []

    for skill_dir in skills:
        validation = check_eval_states(skill_dir)
        has = validation.states["schema_valid"]
        count = validation.case_count
        name = str(skill_dir)
        skill_states.append({"skill": name, "cases": count, **validation.states})
        if has is not True:
            without_evals.append(name)

    supported_states = ("manifest_present", "schema_valid")
    state_summary: dict[str, dict[str, object]] = {}
    for state in supported_states:
        count = sum(1 for entry in skill_states if entry[state] is True)
        state_summary[state] = {
            "assessment": "supported",
            "count": count,
            "percentage": round((count / total * 100) if total else 0.0, 1),
        }

    not_assessed_reasons = {
        "executable_grader_bindings_present": "No repository contract for executable grader bindings in schema v1.",
        "recent_run_evidence_present": "No versioned provenance/freshness contract is defined for schema v1.",
        "release_gated_evidence_present": "No versioned release-gate contract is defined for schema v1.",
    }
    for state in STATE_NAMES:
        if state in state_summary:
            continue
        state_summary[state] = {
            "assessment": NOT_ASSESSED,
            "count": None,
            "percentage": None,
            "reason": not_assessed_reasons[state],
        }
    coverage_pct = state_summary["schema_valid"]["percentage"]
    coverage_pct_float: float = float(coverage_pct) if coverage_pct is not None else 0.0  # type: ignore[arg-type]

    # Sort skills without evals: most-referenced first, then alphabetical
    ref_counts = {name: count_references(Path(name).name, skills) for name in without_evals}
    without_evals.sort(key=lambda n: (-ref_counts[n], n))

    # Phase 3 ratchet check
    ratchet_warnings: list[str] = []
    ratchet_errors: list[str] = []
    if resolved_base_ref:
        modified = modified_skills(resolved_base_ref)
        ratchet_warnings, ratchet_errors = evaluate_ratchet(
            modified=modified,
            current=set(skills),
            without_evals={Path(name) for name in without_evals},
            coverage_pct=coverage_pct_float,
        )

        # Monotonic coverage floor: fail if coverage decreased.
        decreased, base_pct, head_pct = coverage_decreased(resolved_base_ref)
        if decreased:
            ratchet_errors.append(
                f"eval coverage decreased from {base_pct:.1f}% to {head_pct:.1f}% "
                f"(base {args.modified_from} → HEAD) — coverage must not regress"
            )

    if args.json:
        print(
            json.dumps(
                {
                    "total_skills": total,
                    "states": state_summary,
                    "skills": skill_states,
                    "ratchet": {
                        "warn_threshold": WARN_THRESHOLD,
                        "fail_threshold": FAIL_THRESHOLD,
                        "warnings": ratchet_warnings,
                        "errors": ratchet_errors,
                    },
                },
                indent=2,
            )
        )
    else:
        print("Eval evidence states (a manifest alone does not prove behavioral quality):")
        for state in STATE_NAMES:
            summary = state_summary[state]
            if summary["assessment"] == "supported":
                print(
                    f"  {state}: {summary['count']}/{total} skills ({summary['percentage']:.1f}%)"
                )
                continue
            print(f"  {state}: not assessed ({summary['reason']})")
        print()
        print(
            f"Skills WITHOUT schema-valid eval manifests ({len(without_evals)}), by reference count:"
        )
        for name in without_evals:
            refs = ref_counts.get(name, 0)
            print(f"  - {name} (referenced by {refs} skills)")
        print()
        print(f"Ratchet: warn at {WARN_THRESHOLD}%, fail-on-modify at {FAIL_THRESHOLD}%")
        if ratchet_warnings:
            print()
            print("Ratchet warnings:")
            for w in ratchet_warnings:
                print(f"  WARNING: {w}")
        if ratchet_errors:
            print()
            print("Ratchet errors:")
            for e in ratchet_errors:
                print(f"  ERROR: {e}")

    return 1 if ratchet_errors else 0


if __name__ == "__main__":
    sys.exit(main())
