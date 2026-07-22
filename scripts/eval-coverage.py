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


def find_skills() -> list[Path]:
    """Find all canonical skill directories via git-tracked SKILL.md files."""
    result = subprocess.run(
        ["git", "ls-files", "-z", "--", "*/SKILL.md"],
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
    """Return skill directories with changes between base_ref and HEAD."""
    result = subprocess.run(
        ["git", "diff", "--name-only", base_ref, "HEAD", "--", "*/SKILL.md"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    modified = set()
    for line in result.stdout.strip().splitlines():
        if line and "/agent-council/profiles/skills/" not in line:
            modified.add(Path(line).parent)
    return modified


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
        for skill_dir in sorted(modified):
            name = str(skill_dir)
            has, _ = check_evals(skill_dir)
            if not has:
                if coverage_pct >= FAIL_THRESHOLD:
                    ratchet_errors.append(
                        f"{name}: modified skill has no evals "
                        f"(coverage {coverage_pct:.1f}% >= {FAIL_THRESHOLD}% — evals required on modification)"
                    )
                elif coverage_pct >= WARN_THRESHOLD:
                    ratchet_warnings.append(
                        f"{name}: modified skill has no evals "
                        f"(coverage {coverage_pct:.1f}% >= {WARN_THRESHOLD}% — evals recommended)"
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
