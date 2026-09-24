#!/usr/bin/env python3
"""Evaluate the advisory semantic-assertion question on frozen labeled cases."""

from __future__ import annotations

import argparse
import json
import os
import sys
from collections import Counter
from pathlib import Path

from jev_eval_audit import ENDPOINT, MODEL, QUESTION_VARIANTS, build_request, read_key_file
from systemone_probe import live_call, validate_response

LABELS = {"met", "not_met", "not_shown"}
THRESHOLDS = (0.5, 0.7, 0.8, 0.9, 0.95, 0.99)


def load_cases(path: Path, split: str) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("schema_version") != 1 or not isinstance(data.get("cases"), list):
        raise ValueError("invalid benchmark fixture")
    ids = [case.get("id") for case in data["cases"]]
    if len(ids) != len(set(ids)):
        raise ValueError("benchmark case IDs must be unique")
    for case in data["cases"]:
        if not isinstance(case, dict) or case.get("label") not in LABELS or case.get("split") not in {"dev", "test"}:
            raise ValueError("benchmark case lacks valid label or split")
        if not isinstance(case.get("response"), str) or not isinstance(case.get("assertion"), str):
            raise ValueError("benchmark case lacks response or assertion text")
    return [case for case in data["cases"] if case["split"] == split]


def metrics(rows: list[dict]) -> dict:
    completed = [row for row in rows if "prediction" in row]
    n = len(completed)
    correct = sum(row["prediction"] == row["label"] for row in completed)
    brier = sum((row["met_probability"] - int(row["label"] == "met")) ** 2 for row in completed) / n if n else None
    selective = []
    for threshold in THRESHOLDS:
        accepted = [row for row in completed if row["prediction"] == "met" and row["met_probability"] >= threshold]
        hits = sum(row["label"] == "met" for row in accepted)
        selective.append({"threshold": threshold, "accepted_met": len(accepted), "false_accepts": len(accepted) - hits, "precision": hits / len(accepted) if accepted else None})
    return {
        "total": len(rows),
        "completed": n,
        "accuracy": correct / n if n else None,
        "brier_met": brier,
        "label_counts": dict(Counter(row["label"] for row in completed)),
        "predicted_counts": dict(Counter(row["prediction"] for row in completed)),
        "selective_met": selective,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fixture", required=True, type=Path)
    parser.add_argument("--split", required=True, choices=["dev", "test"])
    parser.add_argument("--question-variant", choices=tuple(QUESTION_VARIANTS), default="deployed")
    parser.add_argument("--live", action="store_true")
    parser.add_argument("--key-file", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--max-calls", type=int, default=100)
    args = parser.parse_args()
    if args.max_calls <= 0:
        parser.error("--max-calls must be positive")
    try:
        cases = load_cases(args.fixture, args.split)
        key = (read_key_file(args.key_file) if args.key_file else os.environ.get("TYPESAFE_API_KEY")) if args.live else None
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"benchmark input error: {exc}", file=sys.stderr)
        return 2
    if args.live and not key:
        parser.error("--live requires --key-file or TYPESAFE_API_KEY")
    rows = []
    for case in cases[: args.max_calls]:
        row = {"id": case["id"], "split": args.split, "slice": case.get("slice"), "label": case["label"]}
        if args.live:
            request = build_request({"response": case["response"], "assertions": [case["assertion"]]}, args.question_variant)
            try:
                _, response, latency = live_call(ENDPOINT, request, key or "", 12.0)
                validate_response(request, response)
                if response.get("model") != MODEL:
                    raise ValueError("response model differs from pinned model")
                answer = response["answers"]["a0"]
                row.update({"prediction": answer["choice"], "met_probability": answer["probabilities"]["met"],
                            "provider_confidence": answer["confidence"], "latency_ms": round(latency, 1)})
            except (ValueError, RuntimeError) as exc:
                row["error"] = str(exc)
                rows.append(row)
                break
        rows.append(row)
    result = {"schema_version": 1, "split": args.split, "model": MODEL if args.live else None,
              "question_variant": args.question_variant,
              "fixture_note": "author-constructed synthetic, not independent operational ground truth",
              "metrics": metrics(rows), "cases": rows}
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    return 1 if any("error" in row for row in rows) else 0


if __name__ == "__main__":
    raise SystemExit(main())
