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
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GRANDFATHER_FILE = ROOT / "scripts" / "grandfathered-skills.txt"

# Phase 3 ratchet thresholds (percent of skills with evals)
WARN_THRESHOLD = 25   # modified skills without evals get a warning
FAIL_THRESHOLD = 50   # modified skills without evals fail CI

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


def find_skills_at(ref: str) -> list[Path]:
    """Find canonical skill directories tracked at a git revision."""
    result = subprocess.run(
        ["git", "ls-tree", "-r", "--name-only", ref],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    skills = []
    for name in result.stdout.splitlines():
        if (
            name.endswith("/SKILL.md")
            and "/agent-council/profiles/skills/" not in name
        ):
            skills.append(Path(name).parent)
    return sorted(skills)


def load_grandfathered() -> set[str]:
    if not GRANDFATHER_FILE.exists():
        return set()
    return {
        line.strip()
        for line in GRANDFATHER_FILE.read_text().splitlines()
        if line.strip() and not line.strip().startswith("#")
    }


def check_evals(skill_dir: Path) -> tuple[bool, int]:
    """Return (has_valid_evals, case_count) for a skill directory."""
    evals_file = ROOT / skill_dir / "evals" / "evals.json"
    if not evals_file.exists():
        return False, 0
    try:
        data = json.loads(evals_file.read_text(encoding="utf-8"))
        if isinstance(data, dict) and isinstance(data.get("evals"), list):
            count = len(data["evals"])
            return count > 0, count
        return False, 0
    except (json.JSONDecodeError, OSError):
        return False, 0


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


def modified_skills(base_ref: str) -> set[Path]:
    """Return skill directories with any tracked file changed since base_ref.

    A skill is considered modified when *any* file under its directory
    changes — not just SKILL.md.  This covers references, scripts,
    fixtures, README, and eval manifests.
    """
    result = subprocess.run(
        ["git", "diff", "--name-only", base_ref, "HEAD"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    changed_files = [
        line for line in result.stdout.strip().splitlines()
        if line and "/agent-council/profiles/skills/" not in line
    ]
    # Map each changed file to its owning skill directory by checking
    # whether the file path starts with a known skill directory prefix.
    # Include skills from both revisions so complete directory deletions
    # remain observable under their old name.
    known_skills = sorted(
        set(find_skills()) | set(find_skills_at(base_ref)),
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
                f"{name}: modified skill has no evals "
                f"(coverage {coverage_pct:.1f}% >= {FAIL_THRESHOLD}% — "
                "evals required on modification)"
            )
        elif coverage_pct >= WARN_THRESHOLD:
            warnings.append(
                f"{name}: modified skill has no evals "
                f"(coverage {coverage_pct:.1f}% >= {WARN_THRESHOLD}% — "
                "evals recommended)"
            )
    return warnings, errors


def coverage_decreased(base_ref: str) -> tuple[bool, float, float]:
    """Compare eval coverage between base_ref and HEAD.

    Returns (decreased, base_pct, head_pct).  Coverage is the percentage
    of canonical skills that have a non-empty evals/evals.json.
    """
    head_skills = find_skills()
    head_with = sum(1 for s in head_skills if check_evals(s)[0])
    head_pct = (head_with / len(head_skills) * 100) if head_skills else 0.0

    # Count skills with evals at the base revision.
    result = subprocess.run(
        ["git", "ls-tree", "-r", "--name-only", base_ref],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    base_skill_dirs: set[Path] = set()
    for line in result.stdout.strip().splitlines():
        if (
            line
            and line.endswith("/SKILL.md")
            and "/agent-council/profiles/skills/" not in line
        ):
            base_skill_dirs.add(Path(line).parent)

    base_with = 0
    for skill_dir in base_skill_dirs:
        evals_path = f"{skill_dir}/evals/evals.json"
        cat = subprocess.run(
            ["git", "show", f"{base_ref}:{evals_path}"],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        if cat.returncode != 0:
            continue
        try:
            data = json.loads(cat.stdout)
            if isinstance(data, dict) and isinstance(data.get("evals"), list) and len(data["evals"]) > 0:
                base_with += 1
        except (json.JSONDecodeError, ValueError):
            pass

    base_pct = (base_with / len(base_skill_dirs) * 100) if base_skill_dirs else 0.0
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

    skills = find_skills()
    grandfathered = load_grandfathered()

    total = len(skills)
    with_evals: list[dict] = []
    without_evals: list[str] = []

    for skill_dir in skills:
        has, count = check_evals(skill_dir)
        name = str(skill_dir)
        if has:
            with_evals.append({"skill": name, "cases": count})
        else:
            without_evals.append(name)

    coverage_pct = (len(with_evals) / total * 100) if total else 0.0

    # Sort skills without evals: most-referenced first, then alphabetical
    ref_counts = {
        name: count_references(Path(name).name, skills) for name in without_evals
    }
    without_evals.sort(key=lambda n: (-ref_counts[n], n))

    # Phase 3 ratchet check
    ratchet_warnings: list[str] = []
    ratchet_errors: list[str] = []
    if args.modified_from:
        modified = modified_skills(args.modified_from)
        ratchet_warnings, ratchet_errors = evaluate_ratchet(
            modified=modified,
            current=set(skills),
            without_evals={Path(name) for name in without_evals},
            coverage_pct=coverage_pct,
        )

        # Monotonic coverage floor: fail if coverage decreased.
        decreased, base_pct, head_pct = coverage_decreased(args.modified_from)
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
                    "skills_with_evals": len(with_evals),
                    "skills_without_evals": len(without_evals),
                    "coverage_pct": round(coverage_pct, 1),
                    "with_evals": with_evals,
                    "without_evals": [
                        {"skill": n, "references": ref_counts.get(n, 0)}
                        for n in without_evals
                    ],
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
        print(f"Eval coverage: {len(with_evals)}/{total} skills ({coverage_pct:.1f}%)")
        print()
        if with_evals:
            print("Skills WITH evals:")
            for entry in with_evals:
                print(f"  + {entry['skill']} ({entry['cases']} cases)")
            print()
        print(f"Skills WITHOUT evals ({len(without_evals)}), by reference count:")
        for name in without_evals:
            refs = ref_counts.get(name, 0)
            print(f"  - {name} (referenced by {refs} skills)")
        print()
        print(
            f"Ratchet: warn at {WARN_THRESHOLD}%, "
            f"fail-on-modify at {FAIL_THRESHOLD}%"
        )
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
