#!/usr/bin/env python3
"""Check exact source spans or summary assessment receipts without model calls."""

import argparse
import hashlib
import json
import math
from pathlib import Path

MAX_BYTES = 16 * 1024 * 1024


def source(record):
    if (
        not isinstance(record, dict)
        or type(record.get("schema_version")) is not int
        or record["schema_version"] != 1
    ):
        raise ValueError("invalid_contract")
    text = record.get("source")
    if not isinstance(text, str) or not text.strip():
        raise ValueError("missing_source")
    if hashlib.sha256(text.encode()).hexdigest() != record.get("source_sha256"):
        raise ValueError("source_hash_mismatch")
    return text


def span_key(span, text, labels):
    if not isinstance(span, dict) or span.get("label") not in labels:
        raise ValueError("invalid_label")
    start, end = span.get("start"), span.get("end")
    if type(start) is not int or type(end) is not int or not 0 <= start < end <= len(text):
        raise ValueError("invalid_offsets")
    if span.get("text") != text[start:end]:
        raise ValueError("source_text_mismatch")
    return span["label"], start, end


def spans(record):
    text = source(record)
    labels = record.get("labels")
    if (
        not isinstance(labels, list)
        or not labels
        or any(not isinstance(x, str) or not x.strip() for x in labels)
        or len(set(labels)) != len(labels)
    ):
        raise ValueError("invalid_label_set")
    predictions = record.get("entities")
    gold = record.get("gold_entities")
    if not isinstance(predictions, list) or not isinstance(gold, list):
        raise ValueError("missing_roster")
    provenance = record.get("gold_provenance")
    if (
        not isinstance(provenance, dict)
        or provenance.get("kind") not in {"human", "reference"}
        or not isinstance(provenance.get("evidence"), str)
        or not provenance["evidence"].strip()
    ):
        raise ValueError("untrusted_gold")
    expected = set()
    actual = set()
    findings = []
    for span in gold:
        k = span_key(span, text, labels)
        if k in expected:
            raise ValueError("duplicate_gold")
        expected.add(k)
    for index, span in enumerate(predictions, 1):
        try:
            k = span_key(span, text, labels)
            score = span.get("score")
            if type(score) not in (int, float) or not math.isfinite(score) or not 0 <= score <= 1:
                raise ValueError("invalid_score")
            if k in actual:
                findings.append({"code": "duplicate_prediction", "entity": index})
            actual.add(k)
        except (ValueError, TypeError, KeyError):
            findings.append({"code": "invalid_source_span", "entity": index})
    missing = len(expected - actual)
    extra = len(actual - expected)
    if missing:
        findings.append({"code": "missing_gold_spans", "count": missing})
    if extra:
        findings.append({"code": "extra_spans", "count": extra})
    return {
        "mode": "spans",
        "predicted": len(predictions),
        "gold": len(gold),
        "exact_matches": len(actual & expected),
        "findings": findings,
        "checks_clear": not findings,
        "score_calibration": "not_assessed",
        "semantic_gold_quality": "not_assessed",
    }


def summaries(record):
    source(record)
    if not isinstance(record.get("summary"), str) or not record["summary"].strip():
        raise ValueError("missing_summary")
    if hashlib.sha256(record["summary"].encode()).hexdigest() != record.get("summary_sha256"):
        raise ValueError("summary_hash_mismatch")
    roster = record.get("expected_fact_ids")
    cases = record.get("assessments")
    if (
        not isinstance(roster, list)
        or not roster
        or any(not isinstance(x, str) or not x.strip() for x in roster)
        or len(set(roster)) != len(roster)
        or not isinstance(cases, list)
    ):
        raise ValueError("invalid_fact_roster")
    expected = set(roster)
    seen = set()
    findings = []
    counts = {"supported": 0, "contradicted": 0, "missing": 0, "unresolved": 0}
    for index, row in enumerate(cases, 1):
        if (
            not isinstance(row, dict)
            or row.get("fact_id") not in expected
            or row["fact_id"] in seen
        ):
            raise ValueError("invalid_fact_identity")
        seen.add(row["fact_id"])
        if type(row.get("critical")) is not bool or row.get("relation") not in {
            "supported",
            "contradicted",
            "missing",
            "unresolved",
        }:
            raise ValueError("invalid_assessment")
        if (
            row.get("reviewer_kind") not in {"human", "reference"}
            or not isinstance(row.get("evidence"), str)
            or not row["evidence"].strip()
        ):
            findings.append({"code": "unresolved_provenance", "assessment": index})
        counts[row["relation"]] += 1
        if row["relation"] != "supported":
            findings.append(
                {
                    "code": "fact_" + row["relation"],
                    "assessment": index,
                    "critical": row["critical"],
                }
            )
    if seen != set(roster):
        findings.append({"code": "missing_assessments", "count": len(set(roster) - seen)})
    return {
        "mode": "summary_receipts",
        "counts": counts,
        "findings": findings,
        "checks_clear": not findings,
        "semantic_execution": "not_performed",
        "release": "not_assessed",
        "limitation": "Trusts supplied assessments; does not detect invented summary claims or verify reviewer evidence.",
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("mode", choices=("spans", "summary"))
    p.add_argument("record", type=Path)
    a = p.parse_args()
    try:
        with a.record.open("rb") as f:
            raw = f.read(MAX_BYTES + 1)
        if len(raw) > MAX_BYTES:
            raise ValueError("size_limit")
        record = json.loads(raw)
        report = spans(record) if a.mode == "spans" else summaries(record)
        code = 0 if report["checks_clear"] else 1
    except (OSError, ValueError, TypeError, KeyError):
        report = {"checks_clear": False, "error": "invalid_or_unreadable_record"}
        code = 1
    print(json.dumps(report, indent=2, allow_nan=False))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
