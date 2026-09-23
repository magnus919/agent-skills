#!/usr/bin/env python3
"""Evaluate frozen binary Noul probabilities without calling a model."""

from __future__ import annotations

import argparse
import json
import math
from collections import defaultdict
from pathlib import Path
from typing import Any


def read_cases(path: Path) -> list[dict[str, Any]]:
    rows = []
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        row = json.loads(line)
        if not isinstance(row, dict) or not isinstance(row.get("id"), str) or not row["id"]:
            raise ValueError(f"line {number}: id must be a non-empty string")
        p, label = row.get("probability"), row.get("label")
        if type(p) not in (int, float) or not math.isfinite(p) or not 0 <= p <= 1:
            raise ValueError(f"line {number}: probability must be finite in [0,1]")
        if type(label) is not int or label not in (0, 1):
            raise ValueError(f"line {number}: label must be 0 or 1")
        if not isinstance(row.get("slice", "all"), str):
            raise ValueError(f"line {number}: slice must be a string")
        rows.append(row)
    if not rows or len({row["id"] for row in rows}) != len(rows):
        raise ValueError("cases must be non-empty with unique ids")
    return rows


def metrics(rows: list[dict[str, Any]], threshold: float) -> dict[str, Any]:
    n = len(rows)
    positives = sum(r["label"] for r in rows)
    accepted = [r for r in rows if r["probability"] >= threshold]
    true_accepted = sum(r["label"] for r in accepted)
    eps = 1e-15
    brier = sum((r["probability"] - r["label"]) ** 2 for r in rows) / n
    loss = -sum(r["label"] * math.log(max(r["probability"], eps)) +
                (1 - r["label"]) * math.log(max(1 - r["probability"], eps)) for r in rows) / n
    base_rate = positives / n
    return {
        "n": n, "positive_rate": round(base_rate, 6),
        "brier": round(brier, 6), "constant_rate_brier": round(base_rate * (1 - base_rate), 6),
        "log_loss": round(loss, 6), "threshold": threshold,
        "accepted": len(accepted), "coverage": round(len(accepted) / n, 6),
        "accepted_precision": round(true_accepted / len(accepted), 6) if accepted else None,
        "false_accepts": len(accepted) - true_accepted,
    }


def evaluate(rows: list[dict[str, Any]], threshold: float) -> dict[str, Any]:
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        groups[row.get("slice", "all")].append(row)
    return {"overall": metrics(rows, threshold),
            "slices": {name: metrics(group, threshold) for name, group in sorted(groups.items())},
            "warning": "Illustrative metrics only; do not fit and test a threshold on the same cases."}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cases", type=Path, required=True, help="JSONL with id, probability, label, optional slice")
    parser.add_argument("--threshold", type=float, required=True, help="preselected automation threshold")
    args = parser.parse_args(argv)
    if not math.isfinite(args.threshold) or not 0 <= args.threshold <= 1:
        parser.error("threshold must be finite in [0,1]")
    print(json.dumps(evaluate(read_cases(args.cases), args.threshold), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
