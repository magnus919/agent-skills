"""Select changed skill eval manifests without silently dropping excess work."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

SKILL_NAME = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*\Z")
PATHS = ("*/SKILL.md", "*/evals/evals.json", "*/scripts/**")


def manifests_for_paths(paths: list[str], root: Path) -> list[str]:
    skills = set()
    for path in paths:
        parts = Path(path).parts
        if len(parts) < 2 or not SKILL_NAME.fullmatch(parts[0]):
            continue
        eligible_change = (
            (len(parts) == 2 and parts[1] == "SKILL.md")
            or (len(parts) == 3 and parts[1:] == ("evals", "evals.json"))
            or (len(parts) >= 3 and parts[1] == "scripts")
        )
        if eligible_change and (root / parts[0] / "evals" / "evals.json").is_file():
            skills.add(parts[0])
    return [f"{skill}/evals/evals.json" for skill in sorted(skills)]


def changed_paths(root: Path, base: str, head: str) -> list[str]:
    if not base or not head:
        raise ValueError("base and head revisions are required")
    result = subprocess.run(
        ["git", "-C", str(root), "diff", "--name-only", base, head, "--", *PATHS],
        capture_output=True, text=True, check=False,
    )
    if result.returncode:
        raise ValueError(f"git diff failed: {result.stderr.strip() or 'unknown Git error'}")
    return result.stdout.splitlines()


def select(manifests: list[str], limit: int) -> dict[str, object]:
    if limit <= 0:
        raise ValueError("--max-skills must be positive")
    if len(manifests) > limit:
        return {"status": "over_limit", "eligible_count": len(manifests), "max_skills": limit,
                "selected_count": 0, "manifests": [], "eligible_manifests": manifests}
    return {"status": "selected" if manifests else "none", "eligible_count": len(manifests),
            "max_skills": limit, "selected_count": len(manifests),
            "manifests": manifests, "eligible_manifests": manifests}


def render_summary(selection: dict[str, object]) -> str:
    count = selection["eligible_count"]
    limit = selection["max_skills"]
    if selection["status"] == "over_limit":
        lead = (f"**No paired evals started.** {count} changed skills have eval manifests, "
                f"exceeding the {limit}-skill resource cap. Split the change or review an explicit cap increase.")
    elif selection["status"] == "none":
        lead = "No changed skills with eval manifests were found; no paired evals started."
    else:
        lead = f"Selected all {count}/{count} changed skills with eval manifests."
    names = ", ".join(selection["eligible_manifests"]) or "none"
    return f"## Paired-eval selection\n\n{lead}\n\nEligible manifests: {names}.\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", required=True, help="Git revision before the change")
    parser.add_argument("--head", default="HEAD", help="Git revision to evaluate")
    parser.add_argument("--max-skills", type=int, default=5)
    parser.add_argument("--github-output", type=Path, help="append manifests/count outputs for GitHub Actions")
    parser.add_argument("--summary-output", type=Path, help="append coverage to a GitHub job summary")
    args = parser.parse_args()
    try:
        selection = select(manifests_for_paths(changed_paths(Path.cwd(), args.base, args.head), Path.cwd()), args.max_skills)
        if args.github_output:
            with args.github_output.open("a", encoding="utf-8") as stream:
                stream.write(f"manifests={' '.join(selection['manifests'])}\n")
                stream.write(f"eligible_count={selection['eligible_count']}\n")
                stream.write(f"selected_count={selection['selected_count']}\n")
        if args.summary_output:
            with args.summary_output.open("a", encoding="utf-8") as stream:
                stream.write(render_summary(selection))
    except (OSError, ValueError) as exc:
        print(f"paired-eval selection error: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(selection))
    if selection["status"] == "over_limit":
        print("paired-eval selection error: resource cap would omit changed skills", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
