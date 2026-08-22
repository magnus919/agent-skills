#!/usr/bin/env python3
"""Read-only profiling for CSV and JSONL risk-modeling inputs."""
from __future__ import annotations

import argparse
import csv
import json
import math
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

MISSING = {"", "na", "n/a", "null", "none", "nan", "missing"}
NUMBER = re.compile(r"^[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?$")


def rows_from(path: Path, limit: Optional[int]) -> Iterable[Dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        if path.suffix.lower() in {".jsonl", ".ndjson"}:
            for i, line in enumerate(handle):
                if limit is not None and i >= limit:
                    break
                if line.strip():
                    value = json.loads(line)
                    if not isinstance(value, dict):
                        raise ValueError(f"JSONL line {i + 1} is not an object")
                    yield {str(k): "" if v is None else str(v) for k, v in value.items()}
        else:
            reader = csv.DictReader(handle)
            if reader.fieldnames is None:
                raise ValueError("CSV has no header")
            for i, row in enumerate(reader):
                if limit is not None and i >= limit:
                    break
                yield {str(k): "" if v is None else str(v) for k, v in row.items()}


def numeric_summary(values: List[float]) -> Dict[str, Any]:
    values = sorted(values)
    n = len(values)
    def q(p: float) -> float:
        if n == 1:
            return values[0]
        pos = (n - 1) * p
        lo, hi = math.floor(pos), math.ceil(pos)
        return values[lo] + (values[hi] - values[lo]) * (pos - lo)
    mean = sum(values) / n
    variance = sum((x - mean) ** 2 for x in values) / max(1, n - 1)
    sd = math.sqrt(variance)
    skew = (sum((x - mean) ** 3 for x in values) / n) / (sd ** 3) if sd else None
    return {"n": n, "min": values[0], "q25": q(.25), "median": q(.5), "q75": q(.75), "max": values[-1], "mean": mean, "sd": sd, "skewness_rough": skew}


def profile(path: Path, limit: Optional[int]) -> Dict[str, Any]:
    rows = list(rows_from(path, limit))
    fields = sorted({key for row in rows for key in row})
    columns: Dict[str, Any] = {}
    for field in fields:
        raw = [row.get(field, "") for row in rows]
        missing = sum(value.strip().lower() in MISSING for value in raw)
        candidates = [float(value) for value in raw if value.strip() and NUMBER.fullmatch(value.strip())]
        numeric = len(candidates) == len(raw) - missing and bool(candidates)
        item: Dict[str, Any] = {"rows": len(raw), "missing": missing, "missing_rate": missing / len(raw) if raw else 0.0, "unique_nonmissing": len(set(value for value in raw if value.strip().lower() not in MISSING))}
        if numeric:
            item["type"] = "numeric"
            item["numeric"] = numeric_summary(candidates)
            item["zero_count"] = sum(value == 0 for value in candidates)
            item["negative_count"] = sum(value < 0 for value in candidates)
            item["positive_count"] = sum(value > 0 for value in candidates)
        else:
            item["type"] = "text"
            counts = Counter(value for value in raw if value.strip().lower() not in MISSING)
            item["top_values"] = [{"value": value, "count": count} for value, count in counts.most_common(10)]
        columns[field] = item
    return {"source": str(path), "rows_profiled": len(rows), "row_limit": limit, "columns": columns}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("--limit", type=int, default=10000)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        result = profile(args.input, args.limit)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
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
