#!/usr/bin/env python3
"""Audit chronological train/test windows without modifying the input."""
from __future__ import annotations

import argparse
import csv
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import List


def parse_time(value: str) -> datetime:
    value = value.strip()
    if value.endswith("Z"):
        value = value[:-1] + "+00:00"
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%Y-%m", "%Y%m%d"):
            try:
                return datetime.strptime(value, fmt)
            except ValueError:
                pass
        raise ValueError(f"cannot parse time value: {value!r}")


def read_times(path: Path, column: str) -> List[datetime]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames or column not in reader.fieldnames:
            raise ValueError(f"missing time column {column!r}")
        return [parse_time(row[column]) for row in reader if row.get(column, "").strip()]


def audit(times: List[datetime], test_size: int, step: int, gap: int) -> dict:
    if not times:
        raise ValueError("no parseable observations")
    ordered = sorted(times)
    windows = []
    train_end = test_size + gap
    while train_end < len(ordered):
        test_start = train_end + gap
        test_end = min(test_start + test_size, len(ordered))
        if test_start >= test_end:
            break
        train_values = ordered[:train_end]
        test_values = ordered[test_start:test_end]
        windows.append({
            "train_rows": len(train_values),
            "test_rows": len(test_values),
            "train_start": train_values[0].isoformat(),
            "train_end": train_values[-1].isoformat(),
            "test_start": test_values[0].isoformat(),
            "test_end": test_values[-1].isoformat(),
            "gap_rows": test_start - train_end,
            "chronological": train_values[-1] < test_values[0],
        })
        train_end += step
    return {
        "rows": len(times),
        "unique_timestamps": len(set(times)),
        "duplicate_timestamp_count": len(times) - len(set(times)),
        "input_was_sorted": times == ordered,
        "test_size": test_size,
        "step": step,
        "gap": gap,
        "windows": windows,
        "all_windows_chronological": all(item["chronological"] for item in windows),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("--time-column", required=True)
    parser.add_argument("--test-size", type=int, default=1)
    parser.add_argument("--step", type=int, default=1)
    parser.add_argument("--gap", type=int, default=0)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if min(args.test_size, args.step, args.gap) < 0 or args.test_size == 0 or args.step == 0:
        parser.error("test-size and step must be positive; gap must be non-negative")
    try:
        result = audit(read_times(args.input, args.time_column), args.test_size, args.step, args.gap)
    except (OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    rendered = json.dumps(result, indent=2, sort_keys=True)
    if args.output:
        args.output.write_text(rendered + "\n", encoding="utf-8")
    else:
        print(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
