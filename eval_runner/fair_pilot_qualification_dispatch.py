"""Explicit, one-time runner for the frozen Jev qualification screen.

The default preflight remains offline. This module requires runtime authorization,
exact reviewed input hashes, a one-time claim, and an explicitly supplied key.
It never stores request or response text in its result artifacts.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib
import json
import math
import os
import tempfile
import time
from collections.abc import Callable
from pathlib import Path
from typing import Any, cast
from urllib.error import HTTPError, URLError
from urllib.request import HTTPRedirectHandler, Request, build_opener

from eval_runner.fair_pilot_qualification import (
    CONTRACT,
    DOSSIER,
    build_qualification_report,
)

MODEL = "jev-1.13.0"
ENDPOINT = "https://api.typesafe.ai/v1/systemone"
DOSSIER_SHA256 = "fdf5ab99a7dfda1ddff9318ce62e0bd2b738c172f8b0ba37975e36dae477d77c"
CONTRACT_SHA256 = "fd1cfccc6e565a175fa3e891982aee6d4751e3130ddc3b56ba64a5f3c6769fa4"
MAX_ATTEMPTS = 12


class _NoRedirectHandler(HTTPRedirectHandler):
    """Do not forward the bearer credential through an HTTP redirect."""

    def redirect_request(
        self, req: Request, fp: Any, code: int, msg: str, headers: Any, newurl: str
    ) -> None:
        return None


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def atomic_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            json.dump(value, stream, indent=2, sort_keys=True, allow_nan=False)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def validate_verdict(request: dict[str, Any], response: Any) -> dict[str, Any]:
    """Validate response shape and return only the whitelisted numeric fields."""
    scripts = Path(__file__).resolve().parents[1] / "system-one" / "scripts"
    import sys

    if str(scripts) not in sys.path:
        sys.path.insert(0, str(scripts))
    systemone_probe = importlib.import_module("systemone_probe")

    systemone_probe.validate_response(request, response)
    if response.get("model") != MODEL:
        raise ValueError("model_mismatch")
    answer = response["answers"]["a0"]
    probabilities = answer["probabilities"]
    if set(probabilities) != {"met", "not_met", "not_shown"}:
        raise ValueError("probability_keys_invalid")
    if any(
        isinstance(value, bool)
        or not isinstance(value, (int, float))
        or not math.isfinite(value)
        or value < 0
        or value > 1
        for value in probabilities.values()
    ):
        raise ValueError("probabilities_invalid")
    confidence = answer["confidence"]
    if isinstance(confidence, bool) or not isinstance(confidence, (int, float)):
        raise ValueError("confidence_invalid")
    return {
        "model": MODEL,
        "verdict": answer["choice"],
        "probabilities": {
            key: float(probabilities[key]) for key in ("met", "not_met", "not_shown")
        },
        "provider_confidence": float(confidence),
    }


def execute(
    *,
    authorize: bool,
    dossier_sha256: str,
    contract_sha256: str,
    api_key: str | None,
    claim_exists: bool,
    counter_path: Path,
    transport: Callable[[str, dict[str, Any], str, float], tuple[int, dict[str, Any], float]],
) -> dict[str, Any]:
    """Run serially; persist attempt count immediately before every POST."""
    base: dict[str, Any] = {
        "schema_version": 1,
        "model": MODEL,
        "endpoint": ENDPOINT,
        "dossier_sha256": None,
        "contract_sha256": None,
        "attempted": 0,
        "validated": 0,
        "results": [],
        "errors": [],
    }
    try:
        if not authorize:
            raise ValueError("authorization_required")
        if dossier_sha256 != DOSSIER_SHA256 or contract_sha256 != CONTRACT_SHA256:
            raise ValueError("approved_hash_input_mismatch")
        actual_dossier = sha256(DOSSIER.read_bytes())
        actual_contract = sha256(CONTRACT.read_bytes())
        base["dossier_sha256"] = actual_dossier
        base["contract_sha256"] = actual_contract
        if (actual_dossier, actual_contract) != (DOSSIER_SHA256, CONTRACT_SHA256):
            raise ValueError("frozen_file_hash_mismatch")

        report = build_qualification_report(include_request_payloads=True)
        requests = report.get("_request_payloads")
        if (
            report.get("request_count") != MAX_ATTEMPTS
            or report.get("split_counts") != {"development": 7, "held_out": 5}
            or report.get("model") != MODEL
            or report.get("endpoint") != ENDPOINT
            or report.get("question_variant") != "deployed"
            or not isinstance(requests, list)
            or len(requests) != MAX_ATTEMPTS
        ):
            raise ValueError("roster_model_source_or_split_validation_failed")

        # Preserve dossier order within each split, with all development first.
        entries = report["requests"]
        if not isinstance(entries, list) or len(entries) != MAX_ATTEMPTS:
            raise ValueError("roster_model_source_or_split_validation_failed")
        by_hash = {entry["request_payload_sha256"]: entry for entry in entries}
        ordered = sorted(
            zip(
                requests,
                (by_hash[entry["request_payload_sha256"]] for entry in entries),
                strict=True,
            ),
            key=lambda pair: (pair[1]["split"] != "development", entries.index(pair[1])),
        )
        if [meta["split"] for _, meta in ordered] != ["development"] * 7 + ["held_out"] * 5:
            raise ValueError("development_before_held_out_order_invalid")
        if len({meta["id"] for _, meta in ordered}) != MAX_ATTEMPTS:
            raise ValueError("roster_model_source_or_split_validation_failed")

        # Validate every exact payload before the first call. Do not move any
        # member-specific check into the transport loop.
        prepared: list[tuple[dict[str, Any], dict[str, Any], str]] = []
        for request, meta in ordered:
            encoded = json.dumps(
                request, ensure_ascii=False, sort_keys=True, separators=(",", ":")
            ).encode()
            request_hash = sha256(encoded)
            if request_hash != meta["request_payload_sha256"]:
                raise ValueError("request_payload_hash_mismatch")
            questions = request.get("questions")
            if (
                request.get("model") != MODEL
                or not isinstance(questions, dict)
                or set(questions) != {"a0"}
                or questions["a0"].get("type") != "choice"
            ):
                raise ValueError("request_model_or_question_invalid")
            prepared.append((request, meta, request_hash))

        if claim_exists:
            raise ValueError("duplicate_screen_claim_exists")
        if not isinstance(api_key, str) or not api_key:
            raise ValueError("credential_missing")

        for request, meta, request_hash in prepared:
            # Count and persist before entering the transport/HTTP call.
            base["attempted"] += 1
            atomic_json(
                counter_path, {"attempted": base["attempted"], "max_attempts": MAX_ATTEMPTS}
            )
            try:
                status, response, latency = transport(ENDPOINT, request, api_key, 20.0)
                if not 200 <= status < 300:
                    raise ValueError("provider_http_error")
                verdict = validate_verdict(request, response)
                base["validated"] += 1
                base["results"].append(
                    {
                        "id": meta["id"],
                        "split": meta["split"],
                        "request_sha256": request_hash,
                        "question_input_sha256": meta["question_input_sha256"],
                        "latency_ms": round(float(latency), 1),
                        **verdict,
                    }
                )
            except Exception as exc:  # no retries; error text may contain sensitive body text
                category = getattr(exc, "args", [None])[0]
                if not isinstance(category, str) or not category.replace("_", "").isalnum():
                    category = "provider_or_validation_error"
                allowed = {
                    "model_mismatch",
                    "probability_keys_invalid",
                    "probabilities_invalid",
                    "confidence_invalid",
                    "provider_http_error",
                }
                base["errors"].append(
                    {
                        "id": meta["id"],
                        "split": meta["split"],
                        "category": category
                        if category in allowed
                        else "provider_or_validation_error",
                    }
                )
                break
    except Exception as exc:
        category = getattr(exc, "args", [None])[0]
        allowed_preflight = {
            "authorization_required",
            "approved_hash_input_mismatch",
            "frozen_file_hash_mismatch",
            "roster_model_source_or_split_validation_failed",
            "duplicate_screen_claim_exists",
            "credential_missing",
            "development_before_held_out_order_invalid",
            "request_payload_hash_mismatch",
            "request_model_or_question_invalid",
        }
        base["errors"].append(
            {"category": category if category in allowed_preflight else "preflight_error"}
        )
    base["status"] = (
        "complete"
        if base["validated"] == MAX_ATTEMPTS
        else ("stopped" if base["errors"] else "incomplete")
    )
    return base


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--authorize", action="store_true", help="runtime dispatch authorization")
    parser.add_argument("--dossier-sha256", required=True)
    parser.add_argument("--contract-sha256", required=True)
    parser.add_argument("--claim-exists", action="store_true")
    parser.add_argument("--counter", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    api_key = os.environ.get("TYPESAFE_API_KEY")
    # This is a non-disclosing presence check; the key is never printed or serialized.
    result = execute(
        authorize=args.authorize,
        dossier_sha256=args.dossier_sha256,
        contract_sha256=args.contract_sha256,
        api_key=api_key,
        claim_exists=args.claim_exists,
        counter_path=args.counter,
        transport=_live_call,
    )
    atomic_json(args.output, result)
    print(
        json.dumps(
            {key: result[key] for key in ("status", "attempted", "validated", "errors")},
            sort_keys=True,
        )
    )
    return 0 if result["status"] == "complete" else 1


def _live_call(
    url: str, request: dict[str, Any], key: str, timeout: float
) -> tuple[int, dict[str, Any], float]:
    if url != ENDPOINT:
        raise ValueError("endpoint_mismatch")
    body = json.dumps(request, ensure_ascii=False).encode("utf-8")
    outbound = Request(
        url,
        data=body,
        method="POST",
        headers={
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "system-one-probe/1.0",
        },
    )
    started = time.monotonic()
    try:
        with build_opener(_NoRedirectHandler()).open(outbound, timeout=timeout) as response:
            raw = response.read()
            status = response.status
    except HTTPError as exc:
        # Ignore error bodies; they are neither needed nor safe to persist.
        return exc.code, {}, (time.monotonic() - started) * 1000
    except (URLError, TimeoutError, OSError):
        raise RuntimeError("provider_transport_error") from None
    try:
        response_payload = json.loads(raw)
    except (json.JSONDecodeError, UnicodeDecodeError):
        raise RuntimeError("provider_invalid_json") from None
    return status, cast(dict[str, Any], response_payload), (time.monotonic() - started) * 1000


if __name__ == "__main__":
    raise SystemExit(main())
