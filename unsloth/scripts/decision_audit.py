#!/usr/bin/env python3
"""Read-only, bounded hard-label decision JSONL audit; no model/runtime claims."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

MAX_LINE_BYTES = 1 << 20
MAX_ROWS = 100000


def _object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON key")
        result[key] = value
    return result


def _constant(value):
    raise ValueError("nonfinite JSON number")


def _finite_float(value):
    number = float(value)
    if not math.isfinite(number):
        raise ValueError("nonfinite JSON number")
    return number


def _canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _digest(value):
    return hashlib.sha256(_canonical(value).encode()).hexdigest()


def validate_row(row):
    """Conservative subset: string states, object questions/gold, hard labels."""
    if not isinstance(row, dict):
        raise ValueError("row must be an object")
    state = row.get("state")
    if not isinstance(state, str) or not state.strip():
        raise ValueError("nonempty string state required")
    if "group_id" in row and (not isinstance(row["group_id"], str) or not row["group_id"].strip()):
        raise ValueError("group_id must be a nonempty string")
    questions, gold = row.get("questions"), row.get("gold")
    if not isinstance(questions, dict) or not questions:
        raise ValueError("nonempty object questions required")
    if not isinstance(gold, dict) or set(gold) != set(questions):
        raise ValueError("gold must cover exactly the question IDs")
    counts = {"choice": 0, "noul": 0, "score": 0}
    for qid, question in questions.items():
        if not isinstance(qid, str) or not qid.strip() or not isinstance(question, dict):
            raise ValueError("nonempty question ID and object required")
        instructions = question.get("instructions")
        if not isinstance(instructions, str) or not instructions.strip():
            raise ValueError("nonempty question instructions required")
        kind, criteria, target = question.get("type"), question.get("criteria"), gold[qid]
        if kind not in counts:
            raise ValueError("unsupported question type")
        if kind == "choice":
            if (
                not isinstance(criteria, dict)
                or len(criteria) < 2
                or not all(
                    isinstance(k, str) and k.strip() and isinstance(v, str) and v.strip()
                    for k, v in criteria.items()
                )
            ):
                raise ValueError("choice needs at least two described options")
            if not isinstance(target, str) or target not in criteria:
                raise ValueError("choice hard label must name an option")
        elif kind == "noul":
            if criteria is not None or type(target) is not bool:
                raise ValueError("noul needs a boolean hard label and no criteria")
        else:
            if (
                not isinstance(criteria, list)
                or len(criteria) < 2
                or not all(isinstance(level, str) and level.strip() for level in criteria)
            ):
                raise ValueError("score needs at least two described levels")
            if type(target) is not int or not 0 <= target < len(criteria):
                raise ValueError("score hard label must be a zero-based integer level")
        counts[kind] += 1
    return counts


def scan(path, *, max_rows=MAX_ROWS, max_line_bytes=MAX_LINE_BYTES):
    result = {
        "rows": 0,
        "valid_rows": 0,
        "complete": True,
        "findings": [],
        "questions": {"choice": 0, "noul": 0, "score": 0},
    }
    states, groups, records = {}, {}, {}

    def finding(line, code):
        result["findings"].append({"line": line, "code": code})

    try:
        with Path(path).open("rb") as source:
            while True:
                raw = source.readline(max_line_bytes + 1)
                if not raw:
                    break
                line = result["rows"] + 1
                if line > max_rows or len(raw) > max_line_bytes:
                    result["complete"] = False
                    finding(line, "scan_limit")
                    break
                result["rows"] = line
                try:
                    row = json.loads(
                        raw,
                        object_pairs_hook=_object,
                        parse_constant=_constant,
                        parse_float=_finite_float,
                    )
                    counts = validate_row(row)
                    key = _digest({k: row[k] for k in ("state", "questions", "gold")})
                    state_key = _digest(row["state"])
                    group_key = _digest(row["group_id"]) if "group_id" in row else None
                except (ValueError, UnicodeError, RecursionError):
                    finding(line, "invalid_hard_label_row")
                    continue
                result["valid_rows"] += 1
                for kind, count in counts.items():
                    result["questions"][kind] += count
                if key in records:
                    finding(line, "duplicate_content")
                records.setdefault(key, line)
                states.setdefault(state_key, line)
                if "group_id" in row:
                    groups.setdefault(group_key, line)
    except OSError:
        result["complete"] = False
        finding(None, "input_unreadable")
    if not result["valid_rows"]:
        finding(None, "empty_valid_split")
    return result, states, groups


def audit(paths, *, max_rows=MAX_ROWS, max_line_bytes=MAX_LINE_BYTES):
    report = {
        "schema_version": 1,
        "kind": "hard_label_decision_audit",
        "splits": {},
        "overlap": [],
        "runtime_status": "not_run",
    }
    fingerprints = {}
    for name, path in paths.items():
        result, states, groups = scan(path, max_rows=max_rows, max_line_bytes=max_line_bytes)
        report["splits"][name] = result
        fingerprints[name] = (states, groups)
    names = list(paths)
    for i, left in enumerate(names):
        for right in names[i + 1 :]:
            for field, index in (("state", 0), ("group_id", 1)):
                a, b = fingerprints[left][index], fingerprints[right][index]
                for key in sorted(a.keys() & b.keys()):
                    report["overlap"].append(
                        {
                            "left": left,
                            "right": right,
                            "field": field,
                            "left_line": a[key],
                            "right_line": b[key],
                        }
                    )
    report["ok"] = not report["overlap"] and all(
        r["complete"] and not r["findings"] for r in report["splits"].values()
    )
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("train_file", type=Path)
    parser.add_argument("--calibration-file", required=True, type=Path)
    parser.add_argument("--test-file", required=True, type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = audit(
        {"train": args.train_file, "calibration": args.calibration_file, "test": args.test_file}
    )
    print(
        json.dumps(result, indent=2)
        if args.json
        else f"Hard-label audit: {'pass' if result['ok'] else 'findings'}; runtime not run"
    )
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
