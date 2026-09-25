#!/usr/bin/env python3
"""Compare frozen end-to-end decision pipelines, including routing and fallback."""

from __future__ import annotations

import argparse
import json
import math
import random
from collections import defaultdict
from pathlib import Path
from typing import Any


def _number(value: Any, where: str) -> float:
    if type(value) not in (int, float) or not math.isfinite(value) or value < 0:
        raise ValueError(f"{where} must be a finite non-negative number")
    return float(value)


def _optional_number(value: Any, where: str) -> float | None:
    return None if value is None else _number(value, where)


def _optional_tokens(value: Any, where: str) -> int | None:
    if value is None:
        return None
    if type(value) is not int or value < 0:
        raise ValueError(f"{where} must be a non-negative integer or null")
    return value


def read_cases(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    raw = path.read_text(encoding="utf-8")
    if path.suffix.lower() == ".json":
        try:
            document = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise ValueError(f"invalid JSON report: {exc.msg}") from exc
        if not isinstance(document, dict) or not isinstance(document.get("cases"), list):
            raise ValueError("JSON report must contain a cases array")
        for line_no, row in enumerate(document["cases"], 1):
            rows.append(row)
    else:
        source_lines = enumerate(raw.splitlines(), 1)
        for line_no, line in source_lines:
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"line {line_no}: invalid JSON: {exc.msg}") from exc
            rows.append(row)
    for line_no, row in enumerate(rows, 1):
        where = f"line {line_no}"
        if not isinstance(row, dict) or not isinstance(row.get("id"), str) or not row["id"]:
            raise ValueError(f"{where}: id must be a non-empty string")
        if not isinstance(row.get("label"), str) or not row["label"]:
            raise ValueError(f"{where}: label must be a non-empty string")
        if not isinstance(row.get("slice", "all"), str):
            raise ValueError(f"{where}: slice must be a string")
        policies = row.get("policies")
        if not isinstance(policies, dict) or not policies:
            raise ValueError(f"{where}: policies must be a non-empty object")
        for policy, run in policies.items():
            pwhere = f"{where}, policy {policy!r}"
            if not isinstance(policy, str) or not policy or not isinstance(run, dict):
                raise ValueError(f"{where}: policy names and runs must be non-empty/object values")
            decision = run.get("decision")
            if decision is not None and (not isinstance(decision, str) or not decision):
                raise ValueError(f"{pwhere}: decision must be a non-empty string or null (abstain)")
            total_cost = _optional_number(run.get("cost_usd"), f"{pwhere} cost_usd")
            _number(run.get("latency_ms"), f"{pwhere} latency_ms")
            stages = run.get("stages")
            if not isinstance(stages, list):
                raise ValueError(f"{pwhere}: stages must be a list")
            stage_cost = 0.0
            all_stage_costs_known = True
            for index, stage in enumerate(stages):
                sw = f"{pwhere}, stages[{index}]"
                if not isinstance(stage, dict) or not isinstance(stage.get("name"), str) or not stage["name"]:
                    raise ValueError(f"{sw}: name must be a non-empty string")
                calls = stage.get("calls")
                if type(calls) is not int or calls < 0:
                    raise ValueError(f"{sw}: calls must be a non-negative integer")
                cost = _optional_number(stage.get("cost_usd"), f"{sw} cost_usd")
                _number(stage.get("latency_ms"), f"{sw} latency_ms")
                for token_field in ("input_tokens", "output_tokens", "total_tokens"):
                    _optional_tokens(stage.get(token_field), f"{sw} {token_field}")
                if type(stage.get("fallback", False)) is not bool:
                    raise ValueError(f"{sw}: fallback must be boolean")
                if calls == 0 and (cost != 0 or stage["latency_ms"] != 0 or any(
                    stage.get(field, 0) != 0 for field in ("input_tokens", "output_tokens", "total_tokens")
                )):
                    raise ValueError(f"{sw}: an uncalled stage must have zero cost and latency")
                if cost is None:
                    all_stage_costs_known = False
                else:
                    stage_cost += cost
            if all_stage_costs_known and total_cost is None:
                raise ValueError(f"{pwhere}: cost_usd must be reported when all stage costs are known")
            if not all_stage_costs_known and total_cost is not None:
                raise ValueError(f"{pwhere}: cost_usd must be null when any called stage cost is unknown")
            if all_stage_costs_known and not math.isclose(total_cost, stage_cost, rel_tol=1e-7, abs_tol=1e-9):
                raise ValueError(f"{pwhere}: cost_usd must equal the sum of stage costs")
    if not rows:
        raise ValueError("cases must not be empty")
    ids = [row["id"] for row in rows]
    if len(set(ids)) != len(ids):
        raise ValueError("case ids must be unique")
    expected = set(rows[0]["policies"])
    for row in rows[1:]:
        if set(row["policies"]) != expected:
            raise ValueError("every case must contain the same policy names for paired comparison")
    return rows


def _quantile(values: list[float], q: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    # Nearest-rank quantile: rank = ceil(q*n), with one-based ranks.
    return ordered[max(0, math.ceil(q * len(ordered)) - 1)]


def _round(value: float | None, digits: int = 6) -> float | None:
    return round(value, digits) if value is not None else None


def _summarize(rows: list[dict[str, Any]], policy: str) -> dict[str, Any]:
    runs = [row["policies"][policy] for row in rows]
    n = len(rows)
    resolved = [(row, run) for row, run in zip(rows, runs) if run["decision"] is not None]
    correct = sum(run["decision"] == row["label"] for row, run in resolved)
    costs = [run["cost_usd"] for run in runs if run["cost_usd"] is not None]
    latencies = [run["latency_ms"] for run in runs]
    fallback_cases = sum(any(stage.get("fallback", False) and stage["calls"] > 0
                             for stage in run["stages"]) for run in runs)
    stage_totals: dict[str, dict[str, Any]] = defaultdict(lambda: {
        "calls": 0, "cost_usd": 0.0, "unpriced_calls": 0,
        "input_tokens": 0, "input_tokens_calls_missing": 0,
        "output_tokens": 0, "output_tokens_calls_missing": 0,
        "total_tokens": 0, "total_tokens_calls_missing": 0,
    })
    for run in runs:
        for stage in run["stages"]:
            data = stage_totals[stage["name"]]
            calls = stage["calls"]
            data["calls"] += calls
            if stage["cost_usd"] is None:
                data["unpriced_calls"] += calls
            else:
                data["cost_usd"] += stage["cost_usd"]
            for token_field in ("input_tokens", "output_tokens", "total_tokens"):
                value = stage.get(token_field)
                if value is None:
                    data[f"{token_field}_calls_missing"] += calls
                else:
                    data[token_field] += value
    all_priced = len(costs) == n
    return {
        "n": n,
        "resolved": len(resolved),
        "abstained": n - len(resolved),
        "coverage": _round(len(resolved) / n),
        "correct": correct,
        "accuracy_all_cases": _round(correct / n),
        "accuracy_when_resolved": _round(correct / len(resolved)) if resolved else None,
        "fallback_cases": fallback_cases,
        "fallback_rate": _round(fallback_cases / n),
        "priced_cases": len(costs),
        "unpriced_cases": n - len(costs),
        "price_coverage": _round(len(costs) / n),
        "total_cost_usd": _round(sum(costs), 9) if all_priced else None,
        "known_total_cost_usd": _round(sum(costs), 9) if costs else None,
        "mean_cost_per_case_usd": _round(sum(costs) / n, 9) if all_priced else None,
        "mean_cost_per_priced_case_usd": _round(sum(costs) / len(costs), 9) if costs else None,
        "mean_cost_per_resolved_case_usd": _round(sum(costs) / len(resolved), 9)
        if all_priced and resolved else None,
        "latency_ms": {"p50": _round(_quantile(latencies, .50)),
                       "p95": _round(_quantile(latencies, .95)),
                       "p99": _round(_quantile(latencies, .99)),
                       "mean": _round(sum(latencies) / n)},
        "stages": {
            name: {
                "calls": data["calls"],
                "total_cost_usd": _round(data["cost_usd"], 9) if data["unpriced_calls"] == 0 else None,
                "known_total_cost_usd": _round(data["cost_usd"], 9)
                if data["unpriced_calls"] == 0 or data["unpriced_calls"] < data["calls"] else None,
                "unpriced_calls": data["unpriced_calls"],
                "tokens": {
                    field: _token_total(data[field], data[f"{field}_calls_missing"])
                    for field in ("input_tokens", "output_tokens", "total_tokens")
                },
            }
            for name, data in sorted(stage_totals.items())
        },
    }


def _token_total(total: int, missing_calls: int) -> dict[str, int | None]:
    return {"known_total": total if missing_calls == 0 else None,
            "partial_total": total, "calls_missing_usage": missing_calls}


def _paired_bootstrap(
    rows: list[dict[str, Any]], baseline: str, candidates: list[str], replicates: int, seed: int
) -> dict[str, dict[str, Any]]:
    rng = random.Random(seed)
    n = len(rows)
    samples: dict[str, dict[str, list[float]]] = {
        policy: {"accuracy_all_cases": [], "mean_cost_per_case_usd": [], "mean_latency_ms": []}
        for policy in candidates
    }
    for _ in range(replicates):
        # One case-index sample is shared by every policy comparison in this replicate.
        indices = [rng.randrange(n) for _ in range(n)]
        for policy in candidates:
            accuracy_delta = cost_delta = latency_delta = 0.0
            for index in indices:
                row = rows[index]
                baseline_run = row["policies"][baseline]
                candidate_run = row["policies"][policy]
                label = row["label"]
                accuracy_delta += int(candidate_run["decision"] is not None and candidate_run["decision"] == label)
                accuracy_delta -= int(baseline_run["decision"] is not None and baseline_run["decision"] == label)
                latency_delta += candidate_run["latency_ms"] - baseline_run["latency_ms"]
            samples[policy]["accuracy_all_cases"].append(accuracy_delta / n)
            samples[policy]["mean_latency_ms"].append(latency_delta / n)
            priced_population = [index for index, row in enumerate(rows)
                                 if row["policies"][policy]["cost_usd"] is not None
                                 and row["policies"][baseline]["cost_usd"] is not None]
            if priced_population:
                cost_draw = [rng.choice(priced_population) for _ in priced_population]
                for index in cost_draw:
                    cost_delta += rows[index]["policies"][policy]["cost_usd"] - rows[index]["policies"][baseline]["cost_usd"]
                samples[policy]["mean_cost_per_case_usd"].append(cost_delta / len(cost_draw))

    output: dict[str, dict[str, Any]] = {}
    for policy, by_metric in samples.items():
        output[policy] = {}
        for metric, values in by_metric.items():
            output[policy][metric] = {
                "low": _round(_quantile(values, 0.025), 9 if "cost" in metric else 6),
                "high": _round(_quantile(values, 0.975), 9 if "cost" in metric else 6),
            } if values else {"low": None, "high": None}
        output[policy]["mean_cost_per_case_usd"]["n_paired_priced_cases"] = sum(
            row["policies"][policy]["cost_usd"] is not None and row["policies"][baseline]["cost_usd"] is not None
            for row in rows
        )
    return output


def evaluate(
    rows: list[dict[str, Any]], baseline: str, bootstrap_replicates: int = 2000, seed: int = 20260925
) -> dict[str, Any]:
    if type(bootstrap_replicates) is not int or bootstrap_replicates < 1:
        raise ValueError("bootstrap_replicates must be a positive integer")
    if type(seed) is not int:
        raise ValueError("bootstrap seed must be an integer")
    policies = list(rows[0]["policies"])
    if baseline not in policies:
        raise ValueError(f"baseline {baseline!r} is not present in every case")
    summaries = {name: _summarize(rows, name) for name in policies}
    pairs: dict[str, Any] = {}
    candidates = [name for name in policies if name != baseline]
    intervals = _paired_bootstrap(rows, baseline, candidates, bootstrap_replicates, seed)
    for name in policies:
        if name == baseline:
            continue
        wins = losses = ties = 0
        correctness_deltas: list[int] = []
        cost_deltas: list[float] = []
        latency_deltas: list[float] = []
        paired_priced_rows = 0
        for row in rows:
            base, candidate, label = row["policies"][baseline]["decision"], row["policies"][name]["decision"], row["label"]
            base_correct = base is not None and base == label
            candidate_correct = candidate is not None and candidate == label
            correctness_deltas.append(int(candidate_correct) - int(base_correct))
            candidate_cost = row["policies"][name]["cost_usd"]
            baseline_cost = row["policies"][baseline]["cost_usd"]
            if candidate_cost is not None and baseline_cost is not None:
                cost_deltas.append(candidate_cost - baseline_cost)
                paired_priced_rows += 1
            latency_deltas.append(row["policies"][name]["latency_ms"] - row["policies"][baseline]["latency_ms"])
            if candidate_correct and not base_correct:
                wins += 1
            elif base_correct and not candidate_correct:
                losses += 1
            else:
                ties += 1
        pairs[name] = {
            "baseline": baseline,
            "paired_correctness_wins": wins,
            "paired_correctness_losses": losses,
            "paired_correctness_ties": ties,
            "paired_priced_cases": paired_priced_rows,
            "delta_total_cost_usd": _round(sum(cost_deltas), 9) if paired_priced_rows == len(rows) else None,
            "known_delta_total_cost_usd": _round(sum(cost_deltas), 9) if cost_deltas else None,
            "delta_mean_cost_per_case_usd": _round(sum(cost_deltas) / paired_priced_rows, 9) if paired_priced_rows else None,
            "delta_mean_latency_ms": _round(sum(latency_deltas) / len(rows)),
            "paired_bootstrap_95": {
                "delta_accuracy_all_cases": {
                    "estimate": _round(sum(correctness_deltas) / len(rows)),
                    **intervals[name]["accuracy_all_cases"],
                },
                "delta_mean_cost_per_case_usd": {
                    "estimate": _round(sum(cost_deltas) / paired_priced_rows, 9) if paired_priced_rows else None,
                    **intervals[name]["mean_cost_per_case_usd"],
                },
                "delta_mean_latency_ms": {
                    "estimate": _round(sum(latency_deltas) / len(rows)),
                    **intervals[name]["mean_latency_ms"],
                },
            },
        }
    slices: dict[str, Any] = {}
    for slice_name in sorted({row.get("slice", "all") for row in rows}):
        group = [row for row in rows if row.get("slice", "all") == slice_name]
        slices[slice_name] = {name: _summarize(group, name) for name in policies}
    return {
        "cases": len(rows),
        "baseline": baseline,
        "bootstrap": {
            "method": "paired case-level percentile bootstrap; accuracy and latency resample all n cases with replacement; cost resamples only cases with prices for both candidate and baseline",
            "resamples": bootstrap_replicates,
            "seed": seed,
            "interval": "nearest-rank 2.5th and 97.5th percentiles",
            "warning": "Intervals describe case-sampling variability for the supplied rows only; they do not include model, label, or corpus uncertainty. Intervals from tiny synthetic fixtures are mechanics checks only.",
        },
        "policies": summaries,
        "paired_vs_baseline": pairs,
        "slices": slices,
        "interpretation": "Offline accounting of supplied decisions and traces only. No model is called; synthetic or author-labeled cases do not establish field quality.",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cases", type=Path, required=True, help="JSONL frozen outcomes and per-policy execution traces")
    parser.add_argument("--baseline", required=True, help="named policy used for paired deltas")
    parser.add_argument("--bootstrap-replicates", type=int, default=2000, help="paired case resamples (default: 2000)")
    parser.add_argument("--bootstrap-seed", type=int, default=20260925, help="fixed random seed for reproducible intervals")
    args = parser.parse_args(argv)
    try:
        result = evaluate(read_cases(args.cases), args.baseline, args.bootstrap_replicates, args.bootstrap_seed)
    except (OSError, ValueError) as exc:
        parser.error(str(exc))
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
