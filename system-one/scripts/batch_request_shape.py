#!/usr/bin/env python3
"""Compare frozen solo and batched classifier outputs without calling a model.

Input is JSONL with one row per requested question. See
``references/request-shape-evaluation.md`` for the schema and study design.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import random
from collections import defaultdict
from pathlib import Path
from typing import Any


PAIR_FIELDS = ("model", "model_revision", "split", "replicate", "case_id",
               "question_id", "contract_sha256", "state_sha256", "question_sha256")
HASH_FIELDS = ("contract_sha256", "state_sha256", "question_sha256", "request_sha256")


def _nonempty(row: dict[str, Any], name: str) -> str:
    value = row.get(name)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be a non-empty string")
    return value


def read_rows(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    raw = path.read_text(encoding="utf-8")
    if path.suffix.lower() == ".json":
        try:
            document = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise ValueError(f"invalid capture report JSON: {exc.msg}") from exc
        if not isinstance(document, dict) or not isinstance(document.get("captured_rows"), list):
            raise ValueError("JSON capture report must contain a captured_rows array")
        source_rows = [(line_no, row) for line_no, row in enumerate(document["captured_rows"], 1)]
    else:
        source_rows = []
        for line_no, line in enumerate(raw.splitlines(), 1):
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"line {line_no}: invalid JSON: {exc.msg}") from exc
            source_rows.append((line_no, row))
    for line_no, row in source_rows:
        if not isinstance(row, dict):
            raise ValueError(f"line {line_no}: each row must be an object")
        for name in (*PAIR_FIELDS[:3], "condition", "request_id", "case_id", "question_id"):
            _nonempty(row, name)
        if row["condition"] not in ("solo", "batch"):
            raise ValueError(f"line {line_no}: condition must be solo or batch")
        if type(row.get("replicate")) is not int or row["replicate"] < 0:
            raise ValueError(f"line {line_no}: replicate must be a non-negative integer")
        if type(row.get("batch_size")) is not int or row["batch_size"] < 1:
            raise ValueError(f"line {line_no}: batch_size must be a positive integer")
        if type(row.get("position")) is not int or not 0 <= row["position"] < row["batch_size"]:
            raise ValueError(f"line {line_no}: position must be in [0, batch_size)")
        if row["condition"] == "solo" and (row["batch_size"] != 1 or row["position"] != 0):
            raise ValueError(f"line {line_no}: solo rows require batch_size=1 and position=0")
        for field in HASH_FIELDS:
            value = row.get(field)
            if not isinstance(value, str) or len(value) != 64 or any(c not in "0123456789abcdef" for c in value):
                raise ValueError(f"line {line_no}: {field} must be a lowercase SHA-256 hex digest")
        label = row.get("label")
        if not isinstance(label, str) or not label:
            raise ValueError(f"line {line_no}: label must be a non-empty canonical class")
        status = row.get("status", "ok")
        if status not in ("ok", "error"):
            raise ValueError(f"line {line_no}: status must be ok or error")
        if status == "error":
            if not isinstance(row.get("error"), str) or not row["error"].strip():
                raise ValueError(f"line {line_no}: error rows require an error description")
            if row.get("prediction") is not None or row.get("probabilities") is not None:
                raise ValueError(f"line {line_no}: error rows cannot include predictions")
        else:
            prediction = row.get("prediction")
            probs = row.get("probabilities")
            if not isinstance(prediction, str) or not prediction:
                raise ValueError(f"line {line_no}: successful rows need a prediction")
            if not isinstance(probs, dict) or label not in probs or prediction not in probs or len(probs) < 2:
                raise ValueError(f"line {line_no}: probabilities must include label and prediction classes")
            if any(not isinstance(k, str) or not k or type(v) not in (int, float) or not math.isfinite(v) or not 0 <= v <= 1
                   for k, v in probs.items()):
                raise ValueError(f"line {line_no}: probabilities need finite values in [0,1]")
            if abs(sum(probs.values()) - 1.0) > 1e-5:
                raise ValueError(f"line {line_no}: probabilities must sum to 1 within 1e-5")
        rows.append({**row, "status": status})
    if not rows:
        raise ValueError("input must contain at least one JSONL row")
    validate_requests(rows)
    class_sets: dict[tuple[Any, ...], set[str]] = {}
    for row in rows:
        if row["status"] != "ok":
            continue
        key = (row["model"], row["model_revision"], row["split"], row["question_id"], row["contract_sha256"])
        observed = set(row["probabilities"])
        if key in class_sets and class_sets[key] != observed:
            raise ValueError("successful outputs for one question contract must use the same class set")
        class_sets[key] = observed
    return rows


def validate_requests(rows: list[dict[str, Any]]) -> None:
    keys = set()
    requests: dict[tuple[Any, ...], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        key = tuple(row.get(field) for field in
                    ("model", "model_revision", "split", "condition", "batch_size",
                     "replicate", "case_id", "question_id"))
        if key in keys:
            raise ValueError("duplicate row for model/revision/split/condition/replicate/case/question")
        keys.add(key)
        request_key = (row["model"], row["model_revision"], row["split"], row["condition"],
                       row["replicate"], row["request_id"])
        requests[request_key].append(row)
    for rows_in_request in requests.values():
        expected = rows_in_request[0]["batch_size"]
        if any(row["batch_size"] != expected for row in rows_in_request):
            raise ValueError("all questions in one request must declare the same batch_size")
        if len(rows_in_request) != expected or sorted(row["position"] for row in rows_in_request) != list(range(expected)):
            raise ValueError("each request must contain exactly batch_size rows at positions 0..batch_size-1")
        if len({row["request_sha256"] for row in rows_in_request}) != 1:
            raise ValueError("all rows in one request must share request_sha256")
        if len({(row["case_id"], row["question_id"]) for row in rows_in_request}) != expected:
            raise ValueError("a request must contain distinct case/question pairs")
        if rows_in_request[0]["condition"] == "batch" and expected < 2:
            raise ValueError("batch condition requires batch_size >= 2")


def _calibration(rows: list[dict[str, Any]], bins: int = 10) -> dict[str, Any]:
    good = [r for r in rows if r["status"] == "ok"]
    if not good:
        return {"n_success": 0, "accuracy": None, "brier": None, "log_loss": None,
                "ece": None, "bins": []}
    classes = sorted({key for row in good for key in row["probabilities"]})
    if any(set(row["probabilities"]) != set(classes) for row in good):
        raise ValueError("all successful rows for a model study must use the same class set")
    n = len(good)
    eps = 1e-15
    correct = [r["prediction"] == r["label"] for r in good]
    brier = sum(sum((r["probabilities"][c] - (1.0 if r["label"] == c else 0.0)) ** 2 for c in classes)
                for r in good) / n
    loss = -sum(math.log(max(r["probabilities"][r["label"]], eps)) for r in good) / n
    bucket: list[list[tuple[float, bool]]] = [[] for _ in range(bins)]
    for row, hit in zip(good, correct):
        conf = row["probabilities"][row["prediction"]]
        bucket[min(int(conf * bins), bins - 1)].append((conf, hit))
    entries, ece = [], 0.0
    for i, values in enumerate(bucket):
        if values:
            confidence = sum(x[0] for x in values) / len(values)
            accuracy = sum(x[1] for x in values) / len(values)
            ece += len(values) / n * abs(confidence - accuracy)
        else:
            confidence = accuracy = None
        entries.append({"range": [round(i / bins, 2), round((i + 1) / bins, 2)],
                        "n": len(values), "mean_confidence": round(confidence, 6) if confidence is not None else None,
                        "accuracy": round(accuracy, 6) if accuracy is not None else None})
    return {"n_success": n, "accuracy": round(sum(correct) / n, 6),
            "accuracy_all_attempts": round(sum(correct) / len(rows), 6),
            "error_rate": round(sum(r["status"] == "error" for r in rows) / len(rows), 6),
            "brier": round(brier, 6), "log_loss": round(loss, 6), "ece": round(ece, 6), "bins": entries}


def _overall(rows: list[dict[str, Any]]) -> dict[str, Any]:
    successes = [r for r in rows if r["status"] == "ok"]
    correct = sum(r["prediction"] == r["label"] for r in successes)
    return {"n_questions": len(rows), "n_success": len(successes),
            "accuracy": round(correct / len(successes), 6) if successes else None,
            "accuracy_all_attempts": round(correct / len(rows), 6) if rows else None,
            "error_rate": round((len(rows) - len(successes)) / len(rows), 6) if rows else None}


def _bootstrap_delta(pairs: list[tuple[dict[str, Any], dict[str, Any]]], seed: int, samples: int = 2000) -> dict[str, Any]:
    by_case: dict[str, list[float]] = defaultdict(list)
    for solo, batch in pairs:
        solo_ok = solo["status"] == "ok" and solo["prediction"] == solo["label"]
        batch_ok = batch["status"] == "ok" and batch["prediction"] == batch["label"]
        by_case[solo["case_id"]].append(float(batch_ok) - float(solo_ok))
    cases = sorted(by_case)
    if not cases:
        return {"case_clusters": 0, "mean_accuracy_delta": None, "ci95": None}
    cluster_means = {case: sum(by_case[case]) / len(by_case[case]) for case in cases}
    observed = sum(cluster_means.values()) / len(cases)
    rng = random.Random(seed)
    draws = []
    for _ in range(samples):
        draws.append(sum(cluster_means[rng.choice(cases)] for _ in cases) / len(cases))
    draws.sort()
    lo, hi = draws[int(.025 * (samples - 1))], draws[int(.975 * (samples - 1))]
    return {"case_clusters": len(cases), "mean_accuracy_delta": round(observed, 6),
            "ci95": [round(lo, 6), round(hi, 6)],
            "method": f"paired case-cluster percentile bootstrap, {samples} draws; fixed seed {seed}"}


def analyze(rows: list[dict[str, Any]], seed: int = 20260925) -> dict[str, Any]:
    results = []
    inventory = []
    study_groups: dict[tuple[str, str, str, int], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        study_groups[(row["model"], row["model_revision"], row["split"], row["replicate"])].append(row)
    for (model, revision, split, replicate), group in sorted(study_groups.items()):
        solo = [r for r in group if r["condition"] == "solo"]
        batch_sizes = sorted({r["batch_size"] for r in group if r["condition"] == "batch"})
        inventory.append({"model": model, "model_revision": revision, "split": split,
                          "replicate": replicate, "solo_rows": len(solo),
                          "batch_rows": sum(r["condition"] == "batch" for r in group),
                          "batch_sizes": batch_sizes,
                          "status": "paired" if solo and batch_sizes else "incomplete_conditions"})
        solo_index = {(r["case_id"], r["question_id"]): r for r in solo}
        for batch_size in batch_sizes:
            batch = [r for r in group if r["condition"] == "batch" and r["batch_size"] == batch_size]
            batch_index = {(r["case_id"], r["question_id"]): r for r in batch}
            common = sorted(solo_index.keys() & batch_index.keys())
            missing_solo = sorted(batch_index.keys() - solo_index.keys())
            missing_batch = sorted(solo_index.keys() - batch_index.keys())
            pairs = [(solo_index[k], batch_index[k]) for k in common]
            if any(any(a.get(field) != b.get(field) for field in HASH_FIELDS[:3]) or a["label"] != b["label"]
                   for a, b in pairs):
                raise ValueError("paired solo/batch rows differ in state, question, contract hash, or gold label")
            solo_only = [a for a, _ in pairs]
            batch_only = [b for _, b in pairs]
            question_ids = sorted({a["question_id"] for a, _ in pairs})
            solo_by_question = {qid: _calibration([a for a, _ in pairs if a["question_id"] == qid])
                                for qid in question_ids}
            batch_by_question = {qid: _calibration([b for a, b in pairs if a["question_id"] == qid])
                                 for qid in question_ids}
            flips = [{"case_id": a["case_id"], "question_id": a["question_id"],
                      "solo_status": a["status"], "batch_status": b["status"],
                      "solo_prediction": a.get("prediction"), "batch_prediction": b.get("prediction"),
                      "gold": a["label"], "position": b["position"]}
                     for a, b in pairs if a["status"] != b["status"] or
                     (a["status"] == "ok" and b["status"] == "ok" and a["prediction"] != b["prediction"])]
            results.append({"model": model, "model_revision": revision, "split": split,
                "replicate": replicate, "batch_size": batch_size, "paired_questions": len(pairs),
                "missing_solo": len(missing_solo), "missing_batch": len(missing_batch),
                "solo_overall": _overall(solo_only), "batch_overall": _overall(batch_only),
                "solo_by_question": solo_by_question, "batch_by_question": batch_by_question,
                "paired_accuracy_delta": _bootstrap_delta(pairs, seed + replicate + batch_size),
                "changed_or_failed_outputs": flips})
    return {"schema_version": 1, "advisory_only": True, "seed": seed,
            "interpretation": "Offline paired analysis; no provider calls. ECE uses fixed-width top-confidence bins; small samples make all calibration estimates noisy.",
            "study_inventory": inventory, "comparisons": results}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cases", type=Path, required=True, help="JSONL captured outputs; see the reference schema")
    parser.add_argument("--output", type=Path, help="write report JSON here; stdout if omitted")
    parser.add_argument("--seed", type=int, default=20260925, help="fixed paired-bootstrap seed")
    args = parser.parse_args(argv)
    try:
        report = analyze(read_rows(args.cases), args.seed)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        parser.error(str(exc))
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
