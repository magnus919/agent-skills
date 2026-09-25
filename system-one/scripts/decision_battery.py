#!/usr/bin/env python3
"""Run or score a portable synthetic System One classification battery."""

from __future__ import annotations

import argparse
import json
import os
import statistics
import time
import urllib.error
import urllib.request
from collections import defaultdict
from pathlib import Path

from systemone_probe import validate_request, validate_response


def read_cases(path: Path) -> list[dict]:
    cases = []
    seen = set()
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        row = json.loads(line)
        if not isinstance(row, dict):
            raise ValueError(f"line {line_number}: expected object")
        case_id, task, text = (row.get(key) for key in ("id", "task", "text"))
        choices, expected = row.get("choices"), row.get("expected")
        if not all(isinstance(x, str) and x for x in (case_id, task, text)):
            raise ValueError(f"line {line_number}: id, task, text must be nonempty strings")
        if case_id in seen:
            raise ValueError(f"line {line_number}: duplicate id {case_id}")
        if row.get("schema_version") not in (None, 2):
            raise ValueError(f"line {line_number}: unsupported schema_version")
        if not isinstance(choices, list) or len(choices) < 2 or any(
            not isinstance(x, str) or not x for x in choices
        ) or len(set(choices)) != len(choices):
            raise ValueError(f"line {line_number}: choices must be unique strings")
        if expected not in choices:
            raise ValueError(f"line {line_number}: expected must be a choice")
        if not isinstance(row.get("slice"), str) or not row["slice"]:
            raise ValueError(f"line {line_number}: slice must be a nonempty string")
        if row.get("schema_version") == 2:
            for key in ("domain", "difficulty", "primitive", "question", "rationale", "scenario"):
                if not isinstance(row.get(key), str) or not row[key]:
                    raise ValueError(f"line {line_number}: {key} must be a nonempty string")
            if row["difficulty"] not in {"easy", "medium", "hard"}:
                raise ValueError(f"line {line_number}: invalid difficulty")
            if row["primitive"] not in {"choice", "noul", "score"}:
                raise ValueError(f"line {line_number}: invalid primitive")
            if task != row["primitive"]:
                raise ValueError(f"line {line_number}: v2 task must equal primitive")
            if row["primitive"] == "noul" and choices != ["yes", "no"]:
                raise ValueError(f"line {line_number}: noul choices must be yes, no")
            if row["primitive"] == "score" and choices != ["0", "1", "2", "3"]:
                raise ValueError(f"line {line_number}: score choices must be 0 through 3")
        seen.add(case_id)
        cases.append(row)
    if not cases:
        raise ValueError("battery is empty")
    return cases


def read_predictions(path: Path) -> dict[str, dict]:
    predictions = {}
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        row = json.loads(line)
        if not isinstance(row, dict) or not isinstance(row.get("id"), str):
            raise ValueError(f"prediction line {number}: expected id")
        if row["id"] in predictions:
            raise ValueError(f"prediction line {number}: duplicate id {row['id']}")
        predictions[row["id"]] = row
    return predictions


def query_endpoint(
    cases: list[dict], endpoint: str, timeout: float, adapter: str = "gliner",
    api_key: str | None = None, model: str | None = None,
) -> dict[str, dict]:
    predictions = {}
    groups = []
    for case in cases:
        if case.get("schema_version") == 2 and groups and groups[-1][0].get("scenario") == case["scenario"]:
            if groups[-1][0]["text"] != case["text"]:
                raise ValueError(f"scenario {case['scenario']} has inconsistent text")
            if case["task"] in {item["task"] for item in groups[-1]}:
                raise ValueError(f"scenario {case['scenario']} repeats task {case['task']}")
            groups[-1].append(case)
        else:
            groups.append([case])
    for group in groups:
        request_id = group[0].get("scenario", group[0]["id"])
        if adapter == "gliner":
            heads = {}
            for case in group:
                heads[case["task"]] = (case["choices"] if case.get("schema_version") != 2 else
                                       {"labels": case["choices"], "prompt": case["question"]})
            request_payload = {"text": group[0]["text"], "heads": heads}
            url = endpoint.rstrip("/") + "/classify"
        elif adapter == "systemone":
            questions = {}
            for case in group:
                primitive = case.get("primitive", "choice")
                question = {
                    "type": primitive,
                    "instructions": case.get("question") or (
                        f"Classify the supplied text for {case['task']}; "
                        "select exactly one of the listed labels."
                    ),
                }
                if primitive == "choice":
                    question["criteria"] = {label: label for label in case["choices"]}
                elif primitive == "score":
                    question["criteria"] = case["choices"]
                questions[case["task"]] = question
            request_payload = {
                "state": {"text": group[0]["text"]},
                "questions": questions,
            }
            if model:
                request_payload["model"] = model
            validate_request(request_payload)
            url = endpoint
        else:
            raise ValueError(f"unknown adapter: {adapter}")
        body = json.dumps(request_payload).encode()
        headers = {"Content-Type": "application/json", "Accept": "application/json"}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
        request = urllib.request.Request(
            url, data=body, headers=headers, method="POST",
        )
        start = time.perf_counter()
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                payload = json.load(response)
            if adapter == "systemone":
                validate_response(request_payload, payload)
            elapsed = round((time.perf_counter() - start) * 1000, 1)
            for case in group:
                primitive = case.get("primitive", "choice")
                if adapter == "gliner":
                    answer = payload["result"][case["task"]]
                else:
                    typed_answer = payload["answers"][case["task"]]
                    if primitive == "choice":
                        answer = typed_answer["choice"]
                    elif primitive == "noul":
                        answer = "yes" if typed_answer["noul"] >= 0.5 else "no"
                    else:
                        answer = max(typed_answer["probabilities"], key=typed_answer["probabilities"].get)
                predictions[case["id"]] = {
                    "id": case["id"], "answer": answer,
                    "latency_ms": elapsed,
                    "request_id": request_id,
                    "model": payload.get("model"), "revision": payload.get("revision"),
                    "request_group_size": len(group),
                }
                if isinstance(payload.get("latency_ms"), (int, float)):
                    predictions[case["id"]]["server_latency_ms"] = payload["latency_ms"]
                if adapter == "systemone" and primitive == "noul":
                    predictions[case["id"]]["noul"] = typed_answer["noul"]
                if adapter == "systemone" and primitive == "score":
                    predictions[case["id"]]["score"] = typed_answer["score"]
                    predictions[case["id"]]["probabilities"] = typed_answer["probabilities"]
        except (urllib.error.URLError, TimeoutError, ValueError, KeyError, TypeError) as exc:
            elapsed = round((time.perf_counter() - start) * 1000, 1)
            for case in group:
                predictions[case["id"]] = {
                    "id": case["id"], "error": type(exc).__name__,
                    "request_id": request_id, "request_group_size": len(group),
                    "latency_ms": elapsed,
                }
    return predictions


def score(cases: list[dict], predictions: dict[str, dict]) -> dict:
    extra = sorted(set(predictions) - {case["id"] for case in cases})
    if extra:
        raise ValueError(f"unknown prediction ids: {extra}")
    grouped = defaultdict(list)
    sliced = defaultdict(list)
    domains = defaultdict(list)
    difficulties = defaultdict(list)
    primitives = defaultdict(list)
    errors = []
    request_latencies = {}
    server_latencies = {}
    noul_brier = []
    score_absolute_error = []
    scenario_outcomes = defaultdict(list)
    invalid = 0
    for case in cases:
        pred = predictions.get(case["id"], {})
        answer = pred.get("answer")
        valid = isinstance(answer, str) and answer in case["choices"]
        correct = valid and answer == case["expected"]
        grouped[case["task"]].append(correct)
        sliced[f"{case['task']}:{case['slice']}"].append(correct)
        if case.get("schema_version") == 2:
            domains[case["domain"]].append(correct)
            difficulties[case["difficulty"]].append(correct)
            primitives[case["primitive"]].append(correct)
            scenario_outcomes[case["scenario"]].append(correct)
            if case["primitive"] == "noul" and isinstance(pred.get("noul"), (int, float)):
                noul_brier.append((pred["noul"] - (case["expected"] == "yes")) ** 2)
            if case["primitive"] == "score" and isinstance(pred.get("score"), (int, float)):
                score_absolute_error.append(abs(pred["score"] - int(case["expected"])))
        if not valid:
            invalid += 1
        if not correct:
            errors.append({
                "id": case["id"], "task": case["task"], "slice": case["slice"],
                "expected": case["expected"], "answer": answer,
                "error": pred.get("error") if not valid else None,
            })
        request_id = pred.get("request_id", case["id"])
        if isinstance(pred.get("latency_ms"), (int, float)):
            request_latencies[request_id] = pred["latency_ms"]
        if isinstance(pred.get("server_latency_ms"), (int, float)):
            server_latencies[request_id] = pred["server_latency_ms"]
    total = len(cases)
    def latency_report(values):
        if not values:
            return None
        ordered = sorted(values)
        def quantile(fraction):
            position = (len(ordered)-1) * fraction
            lower = int(position)
            upper = min(lower+1, len(ordered)-1)
            return round(ordered[lower] + (ordered[upper]-ordered[lower])*(position-lower), 1)
        return {"n": len(ordered), "min": round(ordered[0], 1),
                "p50": quantile(0.5), "p95": quantile(0.95),
                "p99": quantile(0.99), "max": round(ordered[-1], 1)}
    def grouped_report(groups):
        return {name: {"correct": sum(outcomes), "n": len(outcomes),
                       "accuracy": round(sum(outcomes) / len(outcomes), 4)}
                for name, outcomes in sorted(groups.items())}
    return {
        "n": total, "correct": total - len(errors),
        "accuracy": round((total - len(errors)) / total, 4),
        "invalid_or_missing": invalid,
        "by_task": grouped_report(grouped),
        "by_slice": grouped_report(sliced),
        "by_domain": grouped_report(domains),
        "by_difficulty": grouped_report(difficulties),
        "by_primitive": grouped_report(primitives),
        "all_three_correct": {"n": len(scenario_outcomes),
                              "correct": sum(all(values) for values in scenario_outcomes.values())},
        "typed_metrics": {
            "noul_brier": round(statistics.mean(noul_brier), 4) if noul_brier else None,
            "noul_n": len(noul_brier),
            "score_mae": round(statistics.mean(score_absolute_error), 4) if score_absolute_error else None,
            "score_n": len(score_absolute_error),
        },
        "handoff_false_negatives": sum(
            item["task"] == "handoff" and item["expected"] == "yes" for item in errors
        ),
        "client_latency_ms": latency_report(request_latencies.values()),
        "server_latency_ms": latency_report(server_latencies.values()),
        "errors": errors,
        "warning": "Synthetic diagnostic battery; accuracy is not a production error-rate estimate.",
    }


def compare(cases: list[dict], primary: dict[str, dict], other: dict[str, dict]) -> dict:
    # Score both inputs first so unknown IDs cannot disappear from comparison.
    score(cases, primary)
    score(cases, other)
    counts = defaultdict(int)
    disagreements = []
    for case in cases:
        left = primary.get(case["id"], {}).get("answer")
        right = other.get(case["id"], {}).get("answer")
        left_ok = left == case["expected"]
        right_ok = right == case["expected"]
        category = (
            "both_correct" if left_ok and right_ok else
            "primary_only" if left_ok else
            "comparison_only" if right_ok else "both_wrong"
        )
        counts[category] += 1
        if left != right:
            disagreements.append({
                "id": case["id"], "task": case["task"], "expected": case["expected"],
                "primary": left, "comparison": right,
            })
    return {
        **{name: counts[name] for name in
           ("both_correct", "primary_only", "comparison_only", "both_wrong")},
        "agreement": len(cases) - len(disagreements),
        "disagreements": disagreements,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cases", type=Path, required=True)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--endpoint", help="GLiNER base URL or exact System One POST URL")
    source.add_argument("--predictions", type=Path, help="JSONL rows with id and answer")
    parser.add_argument("--compare-predictions", type=Path, help="second prediction JSONL for paired case comparison")
    parser.add_argument("--adapter", choices=("gliner", "systemone"), default="gliner")
    parser.add_argument("--model", help="requested System One model identifier, when applicable")
    parser.add_argument("--api-key-env", help="environment variable containing endpoint bearer token")
    parser.add_argument("--output", type=Path, help="Write raw predictions, without fixture text or gold labels")
    parser.add_argument("--timeout", type=float, default=15.0)
    args = parser.parse_args(argv)
    if args.timeout <= 0:
        parser.error("--timeout must be positive")
    if args.adapter == "gliner" and args.model:
        parser.error("--model applies only to the systemone adapter")
    api_key = None
    if args.endpoint and args.api_key_env:
        api_key = os.environ.get(args.api_key_env)
        if not api_key:
            parser.error(f"--api-key-env requires a non-empty ${args.api_key_env}")
    cases = read_cases(args.cases)
    started = time.perf_counter()
    predictions = (
        query_endpoint(cases, args.endpoint, args.timeout, args.adapter, api_key, args.model)
        if args.endpoint else read_predictions(args.predictions)
    )
    wall_ms = round((time.perf_counter() - started) * 1000, 1) if args.endpoint else None
    if args.output:
        args.output.write_text(
            "".join(json.dumps(predictions[case["id"]]) + "\n" for case in cases if case["id"] in predictions),
            encoding="utf-8",
        )
    report = score(cases, predictions)
    if wall_ms is not None:
        requests = report["client_latency_ms"]["n"] if report["client_latency_ms"] else 0
        report["run_performance"] = {
            "wall_ms": wall_ms,
            "requests": requests,
            "cases_per_second": round(len(cases) * 1000 / wall_ms, 2) if wall_ms else None,
            "requests_per_second": round(requests * 1000 / wall_ms, 2) if wall_ms else None,
            "sequential_requests": True,
        }
    if args.compare_predictions:
        report["comparison"] = compare(cases, predictions, read_predictions(args.compare_predictions))
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
