"""Select changed skill eval manifests without silently dropping excess work."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path, PurePosixPath
from typing import Literal, TypedDict

from .evidence_contract import build_judgment_context, load_evidence_contracts
from .runner import load_cases


class Selection(TypedDict):
    status: Literal["over_limit", "selected", "none"]
    eligible_count: int
    max_skills: int
    selected_count: int
    manifests: list[str]
    eligible_manifests: list[str]


SKILL_NAME = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*\Z")
PATHS = ("*/**",)


def manifests_for_paths(paths: list[str], root: Path) -> list[str]:
    skills = set()
    for path in paths:
        relative = PurePosixPath(path)
        parts = relative.parts
        if relative.is_absolute() or len(parts) < 2 or any(part in {".", ".."} for part in parts):
            continue
        # A path may be nested under a valid skill (for example
        # tailscale/skills/headscale-deploy). Attribute it to the deepest
        # manifest root so a child skill is not silently represented by its
        # parent collection.
        for depth in range(len(parts) - 1, 0, -1):
            prefix = parts[:depth]
            if not SKILL_NAME.fullmatch(prefix[-1]):
                continue
            skill_root = root.joinpath(*prefix)
            manifest = skill_root / "evals" / "evals.json"
            if (skill_root / "SKILL.md").is_file() and manifest.is_file():
                skills.add("/".join((*prefix, "evals", "evals.json")))
                break
    return sorted(skills)


def changed_paths(root: Path, base: str, head: str) -> list[str]:
    if not base or not head:
        raise ValueError("base and head revisions are required")
    result = subprocess.run(
        ["git", "-C", str(root), "diff", "--name-only", base, head, "--", *PATHS],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode:
        raise ValueError(f"git diff failed: {result.stderr.strip() or 'unknown Git error'}")
    return result.stdout.splitlines()


def select(manifests: list[str], limit: int) -> Selection:
    if limit <= 0:
        raise ValueError("--max-skills must be positive")
    if len(manifests) > limit:
        return {
            "status": "over_limit",
            "eligible_count": len(manifests),
            "max_skills": limit,
            "selected_count": 0,
            "manifests": [],
            "eligible_manifests": manifests,
        }
    return {
        "status": "selected" if manifests else "none",
        "eligible_count": len(manifests),
        "max_skills": limit,
        "selected_count": len(manifests),
        "manifests": manifests,
        "eligible_manifests": manifests,
    }


def render_summary(selection: Selection) -> str:
    count = selection["eligible_count"]
    limit = selection["max_skills"]
    if selection["status"] == "over_limit":
        lead = (
            f"**No paired evals started.** {count} changed skills have eval manifests, "
            f"exceeding the {limit}-skill resource cap. Split the change or review an explicit cap increase."
        )
    elif selection["status"] == "none":
        lead = "No changed skills with eval manifests were found; no paired evals started."
    else:
        lead = f"Selected all {count}/{count} changed skills with eval manifests."
    names = ", ".join(selection["eligible_manifests"]) or "none"
    return f"## Paired-eval selection\n\n{lead}\n\nEligible manifests: {names}.\n"


def selection_evidence(selection: Selection, root: Path) -> dict[str, object]:
    """Freeze expected case IDs before generation so downstream coverage has a denominator."""
    expected_cases: dict[str, list[str]] = {}
    skill_roots: list[dict[str, object]] = []
    judgment_context: dict[str, dict[str, dict[str, object]]] = {}
    for manifest in selection["manifests"]:
        manifest_path = root / manifest
        skill_root = manifest_path.parent.parent
        skill = skill_root.name
        if skill in expected_cases:
            raise ValueError(f"selected skills must have unique names: {skill}")
        cases = load_cases(manifest_path)
        ids = [case.id for case in cases]
        if not ids or len(ids) != len(set(ids)):
            raise ValueError(f"{manifest} must have nonempty, unique case IDs")
        expected_cases[skill] = ids
        contracts = load_evidence_contracts(skill_root, cases)
        if contracts:
            judgment_context[skill] = {
                case.id: build_judgment_context(skill_root, case, contracts[case.id])
                for case in cases
                if case.id in contracts
            }
        manifest_hash = hashlib.sha256(manifest_path.read_bytes()).hexdigest()
        skill_roots.append(
            {
                "skill_name": skill,
                "skill_root": skill_root.relative_to(root).as_posix(),
                "manifest": manifest,
                "manifest_sha256": manifest_hash,
                "case_ids": ids,
            }
        )
    return {
        "schema_version": 1,
        **selection,
        "expected_cases": expected_cases,
        "skill_roots": skill_roots,
        "judgment_context": judgment_context,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", required=True, help="Git revision before the change")
    parser.add_argument("--head", default="HEAD", help="Git revision to evaluate")
    parser.add_argument("--max-skills", type=int, default=5)
    parser.add_argument(
        "--github-output", type=Path, help="append manifests/count outputs for GitHub Actions"
    )
    parser.add_argument(
        "--summary-output", type=Path, help="append coverage to a GitHub job summary"
    )
    parser.add_argument("--json-output", type=Path, help="write expected-case selection evidence")
    args = parser.parse_args()
    try:
        selection = select(
            manifests_for_paths(changed_paths(Path.cwd(), args.base, args.head), Path.cwd()),
            args.max_skills,
        )
        if args.json_output:
            evidence = selection_evidence(selection, Path.cwd())
            args.json_output.parent.mkdir(parents=True, exist_ok=True)
            args.json_output.write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8")
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
        print(
            "paired-eval selection error: resource cap would omit changed skills", file=sys.stderr
        )
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
