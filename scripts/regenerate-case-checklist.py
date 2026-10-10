#!/usr/bin/env python3
"""Report checklist omissions or add one explicitly selected pending review row.

Bulk regeneration is intentionally unsupported. A missing row is a review gap,
not permission to synthesize reviewer identity, date, verdict, or oracle status.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
CHECKLIST = ROOT / "lifecycle-evals/references/case-quality-checklist.json"
EXCLUDED_PARTS = {".git", ".venv", "node_modules", "__pycache__"}


def _manifest_prompts(root: Path) -> dict[tuple[str, str], str]:
    prompts: dict[tuple[str, str], str] = {}
    for path in root.rglob("evals/evals.json"):
        relative = path.relative_to(root)
        if EXCLUDED_PARTS.intersection(relative.parts):
            continue
        if "agent-council/profiles/skills" in relative.as_posix():
            continue
        skill_root = path.parent.parent
        if not (skill_root / "SKILL.md").is_file():
            continue
        skill = skill_root.relative_to(root).as_posix()
        data = json.loads(path.read_text(encoding="utf-8"))
        for case in data.get("evals", []):
            if isinstance(case, dict) and isinstance(case.get("id"), str):
                prompts[(skill, case["id"])] = str(case.get("prompt", ""))
    return prompts


def checklist_state(
    checklist_path: Path = CHECKLIST,
    root: Path = ROOT,
) -> tuple[dict[str, Any], dict[tuple[str, str], str], list[str]]:
    """Return existing records and prompts for all canonical cases."""
    try:
        document = json.loads(checklist_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return {}, {}, [f"cannot read checklist: {exc}"]
    rows = document.get("rows") if isinstance(document, dict) else None
    if not isinstance(rows, list):
        return document, {}, ["checklist rows must be a list"]
    prompts = _manifest_prompts(root)
    errors: list[str] = []
    seen: set[tuple[str, str]] = set()
    for index, row in enumerate(rows):
        if (
            not isinstance(row, dict)
            or not isinstance(row.get("skill"), str)
            or not isinstance(row.get("case_id"), str)
        ):
            errors.append(f"checklist row {index + 1} needs string skill and case_id fields")
            continue
        key = (row["skill"], row["case_id"])
        if key in seen:
            errors.append(f"duplicate checklist row: {key}")
            continue
        seen.add(key)
        if key not in prompts:
            errors.append(f"orphan checklist row: {key}")
            continue
    return document, prompts, errors


def add_pending_case(
    checklist_path: Path,
    root: Path,
    case_ref: str,
) -> tuple[int, list[str]]:
    """Append one explicitly named case as pending, preserving all existing rows."""
    document, prompts, errors = checklist_state(checklist_path, root)
    if errors:
        return 0, errors
    skill, separator, case_id = case_ref.partition("/")
    if not separator or not skill or not case_id:
        return 0, ["--add-case must be SKILL_PATH/CASE_ID"]
    key = (skill, case_id)
    if key not in prompts:
        return 0, [f"unknown canonical case: {case_ref}"]
    rows = document.get("rows", [])
    if any(row.get("skill") == skill and row.get("case_id") == case_id for row in rows):
        return 0, [f"case already has a checklist row: {case_ref}"]
    rows.append(
        {
            "skill": skill,
            "case_id": case_id,
            "capability": prompts[key],
            "classification": "untriaged",
            "reviewer": "unassigned",
            "reviewed_on": None,
            "verdict": "pending",
            "assertions_grounded": None,
        }
    )
    document["rows"] = rows
    checklist_path.write_text(
        json.dumps(document, indent=2, ensure_ascii=True) + "\n", encoding="utf-8"
    )
    return 1, []


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--add-case", help="add exactly one SKILL_PATH/CASE_ID as pending review")
    args = parser.parse_args()
    if args.add_case:
        added, errors = add_pending_case(CHECKLIST, ROOT, args.add_case)
        if errors:
            print("\n".join(errors), file=sys.stderr)
            return 1
        print(f"added {added} pending review row; no other checklist rows changed")
        return 0
    document, prompts, errors = checklist_state()
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    rows = document.get("rows", [])
    recorded = {(row.get("skill"), row.get("case_id")) for row in rows if isinstance(row, dict)}
    unlisted = len(set(prompts) - recorded)
    print(
        f"{len(rows)} curated rows; {unlisted} canonical cases remain outside the register. "
        "No rows were written. Add one selected case at a time with --add-case."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
