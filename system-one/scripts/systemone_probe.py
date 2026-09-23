#!/usr/bin/env python3
"""Validate a System One request, or explicitly probe a live endpoint.

Offline validation is the default. A live call requires --live and an API-key
environment variable. The script intentionally uses urllib only so it can be
used during early deployment checks without installing a provider SDK.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import sys
import time
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


QUESTION_TYPES = {"choice", "score", "noul"}


def fail(message: str) -> None:
    raise ValueError(message)


def nonempty_criterion(value: Any) -> bool:
    return (isinstance(value, str) and bool(value.strip())) or (isinstance(value, (dict, list)) and bool(value))


def validate_request(payload: Any) -> dict[str, Any]:
    if not isinstance(payload, dict):
        fail("request must be a JSON object")
    if "state" not in payload:
        fail("request is missing state")
    questions = payload.get("questions")
    if not isinstance(questions, dict) or not questions:
        fail("questions must be a non-empty object")
    for qid, question in questions.items():
        if not isinstance(qid, str) or not qid:
            fail("question IDs must be non-empty strings")
        if not isinstance(question, dict):
            fail(f"question {qid!r} must be an object")
        qtype = question.get("type")
        if qtype not in QUESTION_TYPES:
            fail(f"question {qid!r} has unsupported type {qtype!r}")
        if not nonempty_criterion(question.get("instructions")):
            fail(f"question {qid!r} needs non-empty instructions (string, object, or array)")
        if qtype == "choice":
            criteria = question.get("criteria")
            if isinstance(criteria, dict):
                options = list(criteria)
            elif isinstance(criteria, list):
                options = criteria
            else:
                fail(f"choice question {qid!r} needs criteria")
            if len(options) < 2 or any(not isinstance(option, str) or not option for option in options):
                fail(f"choice question {qid!r} needs at least two non-empty options")
            if isinstance(criteria, dict) and any(not nonempty_criterion(value) for value in criteria.values()):
                fail(f"choice question {qid!r} needs non-empty option criteria")
            if len(set(options)) != len(options):
                fail(f"choice question {qid!r} has duplicate options")
        elif qtype == "score":
            criteria = question.get("criteria")
            if not isinstance(criteria, list) or not 2 <= len(criteria) <= 10 or any(not nonempty_criterion(item) for item in criteria):
                fail(f"score question {qid!r} needs 2-10 non-empty ordered levels")
            if len({json.dumps(item, sort_keys=True) for item in criteria}) != len(criteria):
                fail(f"score question {qid!r} has duplicate levels")
    return payload


def finite_probability(value: Any, path: str) -> float:
    if not isinstance(value, (int, float)) or isinstance(value, bool) or not math.isfinite(value) or not 0 <= value <= 1:
        fail(f"{path} must be a finite number in [0, 1]")
    return float(value)


def validate_distribution(values: Any, path: str) -> None:
    if not isinstance(values, dict) or not values:
        fail(f"{path} must be a non-empty probability object")
    total = sum(finite_probability(value, f"{path}.{key}") for key, value in values.items())
    if abs(total - 1.0) > 0.02:
        fail(f"{path} must sum to approximately 1.0 (got {total:.4f})")


def validate_response(request: dict[str, Any], response: Any) -> dict[str, Any]:
    if not isinstance(response, dict) or not isinstance(response.get("answers"), dict):
        fail("response must contain an answers object")
    answers = response["answers"]
    if set(answers) != set(request["questions"]):
        fail("response answer IDs do not match requested question IDs")
    for qid, question in request["questions"].items():
        answer = answers.get(qid)
        if not isinstance(answer, dict):
            fail(f"response is missing answer {qid!r}")
        if answer.get("type") != question["type"]:
            fail(f"answer {qid!r} type does not match request")
        if question["type"] in {"choice", "score"}:
            validate_distribution(answer.get("probabilities"), f"answers.{qid}.probabilities")
            finite_probability(answer.get("confidence"), f"answers.{qid}.confidence")
        if question["type"] == "choice":
            options = question["criteria"] if isinstance(question["criteria"], list) else list(question["criteria"])
            if set(answer["probabilities"]) != set(options):
                fail(f"answer {qid!r} probability keys do not match requested options")
            if answer.get("choice") not in options:
                fail(f"answer {qid!r} selected an option not in the request")
            if answer["probabilities"][answer["choice"]] < max(answer["probabilities"].values()) - 1e-6:
                fail(f"answer {qid!r} choice is not a top-probability option")
        elif question["type"] == "score":
            score = answer.get("score")
            levels = question["criteria"]
            expected_keys = {str(i) for i in range(len(levels))}
            if set(answer["probabilities"]) != expected_keys:
                fail(f"answer {qid!r} probability keys do not match score levels")
            if answer.get("legend") != {str(i): label for i, label in enumerate(levels)}:
                fail(f"answer {qid!r} legend does not match requested score levels")
            if not isinstance(score, (int, float)) or isinstance(score, bool) or not math.isfinite(score) or not 0 <= score <= len(levels) - 1:
                fail(f"answers.{qid}.score must be finite and within the rubric")
            expected_score = sum(int(index) * probability for index, probability in answer["probabilities"].items())
            if abs(score - expected_score) > 0.03:
                fail(f"answers.{qid}.score does not match its probability-weighted level")
        else:
            finite_probability(answer.get("noul"), f"answers.{qid}.noul")
    return response


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise ValueError(f"cannot read {path}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid JSON in {path}: {exc}") from exc


def live_call(url: str, payload: dict[str, Any], key: str, timeout: float) -> tuple[int, dict[str, Any], float]:
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    request = Request(url, data=body, method="POST", headers={
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": "system-one-probe/1.0",
    })
    started = time.monotonic()
    try:
        with urlopen(request, timeout=timeout) as response:
            raw = response.read()
            status = response.status
    except HTTPError as exc:
        raise RuntimeError(f"endpoint returned HTTP {exc.code}") from exc
    except (URLError, TimeoutError, OSError) as exc:
        raise RuntimeError(f"endpoint request failed: {exc}") from exc
    elapsed_ms = (time.monotonic() - started) * 1000
    try:
        response_payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise RuntimeError("endpoint returned non-JSON response") from exc
    return status, response_payload, elapsed_ms


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--request", required=True, type=Path, help="JSON file containing state and questions")
    parser.add_argument("--live", action="store_true", help="perform one live POST; omitted means offline validation")
    parser.add_argument("--url", default="https://api.typesafe.ai/v1/systemone", help="System One endpoint")
    parser.add_argument("--api-key-env", default="TYPESAFE_API_KEY", help="environment variable for the bearer key")
    parser.add_argument("--timeout", type=float, default=10.0, help="live request timeout in seconds")
    parser.add_argument("--show-response", action="store_true", help="print full live response; may contain sensitive data")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        payload = validate_request(load_json(args.request))
        if not args.live:
            print(json.dumps({"valid": True, "mode": "offline", "questions": list(payload["questions"])}, indent=2))
            return 0
        key = os.environ.get(args.api_key_env)
        if not key:
            raise ValueError(f"--live requires non-empty ${args.api_key_env}")
        status, response, elapsed_ms = live_call(args.url, payload, key, args.timeout)
        validate_response(payload, response)
        report = {"valid": True, "mode": "live", "status": status, "latency_ms": round(elapsed_ms, 2), "model": response.get("model"), "questions": list(payload["questions"])}
        if args.show_response:
            report["response"] = response
        print(json.dumps(report, indent=2))
        return 0
    except (ValueError, RuntimeError) as exc:
        print(json.dumps({"valid": False, "error": str(exc)}, indent=2), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
