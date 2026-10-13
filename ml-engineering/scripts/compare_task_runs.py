#!/usr/bin/env python3
"""Compare pinned, complete single-attempt task receipts; not a release gate."""

import argparse
import hashlib
import json
import math
import random
from pathlib import Path

MAX_BYTES = 32 * 1024 * 1024
PINS = ("dataset_sha256", "harness_sha256", "decoding_sha256", "budget_sha256")
STATUSES = {"passed", "failed", "timeout", "infrastructure_error", "not_run"}


def is_hash(value):
    return (
        isinstance(value, str) and len(value) == 64 and all(c in "0123456789abcdef" for c in value)
    )


def load(path):
    with Path(path).open("rb") as stream:
        raw = stream.read(MAX_BYTES + 1)
    if len(raw) > MAX_BYTES:
        raise ValueError("size_limit")
    try:
        record = json.loads(raw)
    except (ValueError, UnicodeError) as exc:
        raise ValueError("invalid_json") from exc
    validate(record)
    return record, hashlib.sha256(raw).hexdigest()


def validate(record):
    if (
        not isinstance(record, dict)
        or type(record.get("schema_version")) is not int
        or record["schema_version"] != 1
    ):
        raise ValueError("invalid_contract")
    if not all(is_hash(record.get(k)) for k in (*PINS, "artifact_sha256")):
        raise ValueError("missing_immutable_pin")
    roster = record.get("expected_case_ids")
    if (
        not isinstance(roster, list)
        or not roster
        or any(not isinstance(i, str) or not i.strip() for i in roster)
        or len(set(roster)) != len(roster)
    ):
        raise ValueError("invalid_expected_roster")
    cases = record.get("cases")
    if not isinstance(cases, list) or len(cases) > 100000:
        raise ValueError("invalid_cases")
    expected = set(roster)
    seen = set()
    for case in cases:
        if not isinstance(case, dict) or case.get("id") not in expected or case["id"] in seen:
            raise ValueError("duplicate_or_unexpected_case")
        seen.add(case["id"])
        if not isinstance(case.get("group_id"), str) or not case["group_id"].strip():
            raise ValueError("missing_group")
        status = case.get("status")
        if status not in STATUSES or type(case.get("critical_failure")) is not bool:
            raise ValueError("invalid_status")
        latency = case.get("latency_seconds")
        if status in {"not_run", "infrastructure_error"}:
            if latency is not None:
                raise ValueError("incomplete_latency_must_be_null")
        elif type(latency) not in (float, int) or not math.isfinite(latency) or latency < 0:
            raise ValueError("invalid_latency")


def percentile(values, q):
    values = sorted(values)
    position = (len(values) - 1) * q
    low = int(position)
    high = min(low + 1, len(values) - 1)
    return values[low] + (values[high] - values[low]) * (position - low)


def summarize(cases):
    return {
        "total": len(cases),
        "solve_rate": sum(c["status"] == "passed" for c in cases) / len(cases),
        "timeouts": sum(c["status"] == "timeout" for c in cases),
        "critical_failures": sum(c["critical_failure"] for c in cases),
        "latency_p50_seconds": percentile([c["latency_seconds"] for c in cases], 0.5),
        "latency_p95_seconds": percentile([c["latency_seconds"] for c in cases], 0.95),
    }


def compare(base, candidate, bootstrap=2000, seed=3407):
    validate(base)
    validate(candidate)
    findings = []
    for pin in PINS:
        if base[pin] != candidate[pin]:
            findings.append({"code": "comparison_pin_mismatch", "field": pin})
    if set(base["expected_case_ids"]) != set(candidate["expected_case_ids"]):
        findings.append({"code": "expected_roster_mismatch"})
    left = {c["id"]: c for c in base["cases"]}
    right = {c["id"]: c for c in candidate["cases"]}
    for record, side in ((base, "baseline"), (candidate, "candidate")):
        if {c["id"] for c in record["cases"]} != set(record["expected_case_ids"]):
            findings.append({"code": "missing_cases", "side": side})
        if any(c["status"] in {"infrastructure_error", "not_run"} for c in record["cases"]):
            findings.append({"code": "incomplete_execution", "side": side})
    if any(left[i]["group_id"] != right[i]["group_id"] for i in left.keys() & right.keys()):
        findings.append({"code": "group_mismatch"})
    report = {
        "schema_version": 1,
        "comparison_status": "inconclusive" if findings else "complete",
        "findings": findings,
        "release": "not_assessed",
    }
    if findings:
        return report
    ids = sorted(left)
    groups = {}
    gains = losses = 0
    for i in ids:
        delta = int(right[i]["status"] == "passed") - int(left[i]["status"] == "passed")
        groups.setdefault(left[i]["group_id"], []).append(delta)
        gains += delta == 1
        losses += delta == -1
    report.update(
        {
            "baseline": summarize(list(left.values())),
            "candidate": summarize(list(right.values())),
            "paired_gains": gains,
            "paired_losses": losses,
            "solve_rate_delta": (gains - losses) / len(ids),
        }
    )
    # Resample independent groups, preserving task pairs and within-group dependence.
    # A single group cannot estimate between-group uncertainty.
    if len(groups) < 2:
        report["uncertainty"] = {"status": "not_assessed", "reason": "fewer_than_two_groups"}
    else:
        rng = random.Random(seed)
        clusters = list(groups.values())
        estimates = []
        for _ in range(bootstrap):
            sample = [rng.choice(clusters) for _ in clusters]
            estimates.append(sum(sum(c) for c in sample) / sum(len(c) for c in sample))
        report["uncertainty"] = {
            "status": "descriptive",
            "method": "paired_group_percentile_bootstrap",
            "replicates": bootstrap,
            "seed": seed,
            "groups": len(groups),
            "delta_interval_95": [percentile(estimates, 0.025), percentile(estimates, 0.975)],
            "limitation": "Conditional on supplied groups and one attempt; not training-seed uncertainty or release approval.",
        }
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("baseline", type=Path)
    parser.add_argument("candidate", type=Path)
    parser.add_argument("--bootstrap", type=int, default=2000)
    parser.add_argument("--seed", type=int, default=3407)
    args = parser.parse_args()
    if not 100 <= args.bootstrap <= 10000:
        parser.error("bootstrap must be between 100 and 10000")
    try:
        baseline, baseline_hash = load(args.baseline)
        candidate, candidate_hash = load(args.candidate)
        report = compare(baseline, candidate, args.bootstrap, args.seed)
        report["input_sha256"] = {"baseline": baseline_hash, "candidate": candidate_hash}
    except (OSError, ValueError, TypeError) as exc:
        report = {
            "schema_version": 1,
            "comparison_status": "inconclusive",
            "findings": [
                {"code": str(exc) if type(exc) is ValueError else "invalid_or_unreadable_input"}
            ],
            "release": "not_assessed",
        }
    print(json.dumps(report, indent=2, allow_nan=False))
    return 0 if report["comparison_status"] == "complete" else 1


if __name__ == "__main__":
    raise SystemExit(main())
