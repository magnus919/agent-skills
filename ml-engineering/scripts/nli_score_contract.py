#!/usr/bin/env python3
"""Recompute standard NLI zero-shot scores from saved logits; no model calls."""

import argparse
import json
import math
from pathlib import Path

MAX_BYTES = 8 * 1024 * 1024


def softmax(values):
    if not values or any(type(v) not in (int, float) or not math.isfinite(v) for v in values):
        raise ValueError("invalid_logits")
    peak = max(values)
    weights = [math.exp(v - peak) for v in values]
    total = math.fsum(weights)
    return [v / total for v in weights]


def score(record):
    if (
        not isinstance(record, dict)
        or type(record.get("schema_version")) is not int
        or record["schema_version"] != 1
    ):
        raise ValueError("invalid_contract")
    labels = record.get("candidate_labels")
    mapping = record.get("nli_label_ids")
    mode = record.get("mode")
    if (
        not isinstance(labels, list)
        or not labels
        or len(labels) > 1000
        or any(not isinstance(x, str) or not x.strip() for x in labels)
        or len(set(labels)) != len(labels)
    ):
        raise ValueError("invalid_candidate_roster")
    if not isinstance(mapping, dict) or set(mapping) not in (
        {"entailment", "contradiction"},
        {"entailment", "contradiction", "neutral"},
    ):
        raise ValueError("ambiguous_label_mapping")
    width = len(mapping)
    if any(type(v) is not int for v in mapping.values()) or set(mapping.values()) != set(
        range(width)
    ):
        raise ValueError("ambiguous_label_mapping")
    if mode not in {"single_label", "multi_label"}:
        raise ValueError("invalid_mode")
    revision = record.get("model_revision")
    if (
        not isinstance(revision, str)
        or len(revision) not in (40, 64)
        or any(c not in "0123456789abcdef" for c in revision)
    ):
        raise ValueError("unpinned_model_revision")
    rows = record.get("rows")
    if not isinstance(rows, list) or not rows or len(rows) * len(labels) > 100000:
        raise ValueError("invalid_or_oversized_rows")
    ent = mapping["entailment"]
    contra = mapping["contradiction"]
    neutral = mapping.get("neutral")
    out = []
    independent = mode == "multi_label" or len(labels) == 1
    for index, row in enumerate(rows, 1):
        logits = row.get("logits") if isinstance(row, dict) else None
        if (
            not isinstance(logits, list)
            or len(logits) != len(labels)
            or any(not isinstance(v, list) or len(v) != width for v in logits)
        ):
            raise ValueError("logit_shape_mismatch")
        for triple in logits:
            softmax(triple)
        values = (
            [softmax([x[contra], x[ent]])[1] for x in logits]
            if independent
            else softmax([x[ent] for x in logits])
        )
        out.append(
            {
                "row": index,
                "scores_in_candidate_order": values,
                "top_index": max(range(len(values)), key=values.__getitem__),
                "neutral_argmax_pairs": None
                if neutral is None
                else sum(max(range(width), key=x.__getitem__) == neutral for x in logits),
            }
        )
    return {
        "schema_version": 1,
        "score_semantics": "independent_entailment_vs_contradiction"
        if independent
        else "candidate_relative_entailment_softmax",
        "rows": out,
        "model_execution": "not_performed",
        "calibration": "not_assessed",
        "label_map_provenance": "not_verified",
        "task_correctness": "not_assessed",
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("record", type=Path)
    a = p.parse_args()
    try:
        with a.record.open("rb") as f:
            raw = f.read(MAX_BYTES + 1)
        if len(raw) > MAX_BYTES:
            raise ValueError("size_limit")
        report = score(json.loads(raw))
        code = 0
    except (OSError, ValueError, TypeError, KeyError):
        report = {"error": "invalid_or_unreadable_contract", "model_execution": "not_performed"}
        code = 1
    print(json.dumps(report, indent=2, allow_nan=False))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
