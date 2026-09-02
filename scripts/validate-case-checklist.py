#!/usr/bin/env python3
"""Validate that the reviewed case checklist exactly covers eval manifests."""

from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CHECKLIST = ROOT / "lifecycle-evals/references/case-quality-checklist.json"


def manifest_cases() -> set[tuple[str, str]]:
    cases: set[tuple[str, str]] = set()
    for path in ROOT.glob("*/evals/evals.json"):
        data = json.loads(path.read_text())
        skill = path.parent.parent.name
        cases.update((skill, case["id"]) for case in data["evals"])
    return cases


def validate(path: Path = CHECKLIST) -> list[str]:
    data = json.loads(path.read_text())
    rows = data.get("rows")
    errors: list[str] = []
    if not isinstance(rows, list):
        return ["checklist rows must be a list"]
    keys = [(row.get("skill"), row.get("case_id")) for row in rows if isinstance(row, dict)]
    duplicates = sorted(key for key, count in Counter(keys).items() if count > 1)
    expected = manifest_cases()
    actual = set(keys)
    if duplicates:
        errors.append(f"duplicate checklist rows: {duplicates}")
    if expected - actual:
        errors.append(f"missing checklist rows: {sorted(expected - actual)}")
    if actual - expected:
        errors.append(f"orphan checklist rows: {sorted(actual - expected)}")
    return errors


def main() -> int:
    errors = validate()
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print("case-quality checklist matches every manifest case exactly once")
    return 0


if __name__ == "__main__":
    sys.exit(main())
