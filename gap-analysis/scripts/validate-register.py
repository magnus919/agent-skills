#!/usr/bin/env python3
"""Validate the required fields of a JSON gap register."""
import argparse
import json
import sys
from pathlib import Path

REQUIRED = ("id", "question", "target", "current", "evidence", "priority", "owner", "closure_test")

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", type=Path)
    args = parser.parse_args()
    try:
        data = json.loads(args.path.read_text())
    except (OSError, json.JSONDecodeError) as exc:
        print(f"error: cannot read JSON register: {exc}", file=sys.stderr)
        return 2
    gaps = data.get("gaps") if isinstance(data, dict) else None
    if not isinstance(gaps, list):
        print("error: top-level 'gaps' must be an array", file=sys.stderr)
        return 2
    errors = []
    ids = set()
    for index, gap in enumerate(gaps, 1):
        prefix = f"gaps[{index}]"
        if not isinstance(gap, dict):
            errors.append(f"{prefix}: must be an object")
            continue
        for field in REQUIRED:
            if not isinstance(gap.get(field), str) or not gap[field].strip():
                errors.append(f"{prefix}: missing non-empty {field!r}")
        gap_id = gap.get("id")
        if gap_id in ids:
            errors.append(f"{prefix}: duplicate id {gap_id!r}")
        ids.add(gap_id)
        evidence = gap.get("evidence")
        if isinstance(evidence, str) and evidence.strip().lower() in {"tbd", "unknown", "none"}:
            if not isinstance(gap.get("evidence_gap"), str) or not gap["evidence_gap"].strip():
                errors.append(f"{prefix}: unknown evidence requires an explicit evidence_gap")
    if errors:
        print("\n".join(f"error: {error}" for error in errors), file=sys.stderr)
        return 1
    print(f"validated {len(gaps)} gap(s)")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
