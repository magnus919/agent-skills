from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from eval_runner import fair_pilot_qualification_dispatch as dispatch


def _response(request: dict[str, Any]) -> dict[str, Any]:
    return {
        "model": dispatch.MODEL,
        "answers": {
            "a0": {
                "type": "choice",
                "choice": "met",
                "confidence": 0.8,
                "probabilities": {"met": 0.8, "not_met": 0.1, "not_shown": 0.1},
            }
        },
    }


def _kwargs(tmp_path: Path, transport):
    return {
        "authorize": True,
        "dossier_sha256": dispatch.DOSSIER_SHA256,
        "contract_sha256": dispatch.CONTRACT_SHA256,
        "api_key": "test-secret-do-not-print",
        "claim_exists": False,
        "counter_path": tmp_path / "attempt-counter.json",
        "transport": transport,
    }


def test_complete_screen_preflights_then_persists_counter_before_each_post(tmp_path):
    seen: list[tuple[str, int]] = []

    def transport(url, request, key, timeout):
        counter = json.loads((tmp_path / "attempt-counter.json").read_text())
        seen.append((url, counter["attempted"]))
        assert key == "test-secret-do-not-print"
        assert timeout == 20.0
        return 200, _response(request), 12.34

    result = dispatch.execute(**_kwargs(tmp_path, transport))
    assert result["status"] == "complete"
    assert result["attempted"] == result["validated"] == 12
    assert [attempt for _, attempt in seen] == list(range(1, 13))
    assert all(url == dispatch.ENDPOINT for url, _ in seen)
    assert [row["split"] for row in result["results"]] == ["development"] * 7 + ["held_out"] * 5
    serialized = json.dumps(result)
    assert "test-secret" not in serialized
    assert "response" not in serialized
    assert "assertion" not in serialized


def test_hard_cap_rejects_any_roster_above_twelve_before_call(tmp_path, monkeypatch):
    called = []
    original = dispatch.build_qualification_report

    def too_many(*, include_request_payloads=False):
        report = original(include_request_payloads=include_request_payloads)
        report["request_count"] = 13
        report["_request_payloads"].append(report["_request_payloads"][0])
        return report

    monkeypatch.setattr(dispatch, "build_qualification_report", too_many)
    result = dispatch.execute(**_kwargs(tmp_path, lambda *args: called.append(args)))
    assert result["attempted"] == 0
    assert result["errors"] == [{"category": "roster_model_source_or_split_validation_failed"}]
    assert called == []


def test_missing_secret_fails_before_transport(tmp_path):
    called = []
    result = dispatch.execute(
        **{**_kwargs(tmp_path, lambda *args: called.append(args)), "api_key": None}
    )
    assert result["errors"] == [{"category": "credential_missing"}]
    assert result["attempted"] == 0
    assert called == []


def test_hash_mismatch_fails_before_transport(tmp_path):
    called = []
    result = dispatch.execute(
        **{**_kwargs(tmp_path, lambda *args: called.append(args)), "dossier_sha256": "0" * 64}
    )
    assert result["errors"] == [{"category": "approved_hash_input_mismatch"}]
    assert called == []


def test_duplicate_claim_fails_before_transport(tmp_path):
    called = []
    result = dispatch.execute(
        **{**_kwargs(tmp_path, lambda *args: called.append(args)), "claim_exists": True}
    )
    assert result["errors"] == [{"category": "duplicate_screen_claim_exists"}]
    assert called == []


def test_invalid_response_stops_on_first_error_and_does_not_retry(tmp_path):
    calls = 0

    def transport(url, request, key, timeout):
        nonlocal calls
        calls += 1
        response = _response(request)
        response["model"] = "unexpected-model"
        return 200, response, 1.0

    result = dispatch.execute(**_kwargs(tmp_path, transport))
    assert calls == 1
    assert result["attempted"] == 1
    assert result["validated"] == 0
    assert result["errors"] == [
        {"id": result["errors"][0]["id"], "split": "development", "category": "model_mismatch"}
    ]
    assert json.loads((tmp_path / "attempt-counter.json").read_text())["attempted"] == 1


def test_provider_error_text_is_redacted(tmp_path):
    secret = "token-secret-raw-response-body"

    def transport(*args):
        raise RuntimeError(secret)

    result = dispatch.execute(**_kwargs(tmp_path, transport))
    assert result["attempted"] == 1
    assert result["errors"][0]["category"] == "provider_or_validation_error"
    assert secret not in json.dumps(result)


def test_redirect_handler_rejects_redirect_without_forwarding_request():
    from urllib.request import Request

    request = Request(dispatch.ENDPOINT, headers={"Authorization": "Bearer do-not-forward"})
    redirected = dispatch._NoRedirectHandler().redirect_request(
        request, None, 302, "Found", {}, "https://other.example/collect"
    )
    assert redirected is None


def test_source_or_model_preflight_failure_makes_no_call(tmp_path, monkeypatch):
    called = []
    original = dispatch.build_qualification_report

    def bad_report(*, include_request_payloads=False):
        report = original(include_request_payloads=include_request_payloads)
        report["model"] = "wrong-model"
        return report

    monkeypatch.setattr(dispatch, "build_qualification_report", bad_report)
    result = dispatch.execute(**_kwargs(tmp_path, lambda *args: called.append(args)))
    assert result["attempted"] == 0
    assert result["errors"] == [{"category": "roster_model_source_or_split_validation_failed"}]
    assert called == []


def test_late_roster_payload_mismatch_fails_before_first_call(tmp_path, monkeypatch):
    original = dispatch.build_qualification_report

    def tampered_report(*, include_request_payloads=False):
        report = original(include_request_payloads=include_request_payloads)
        report["_request_payloads"][1]["state"]["response"] += " altered after freeze"
        return report

    monkeypatch.setattr(dispatch, "build_qualification_report", tampered_report)
    called = []
    result = dispatch.execute(**_kwargs(tmp_path, lambda *args: called.append(args)))
    assert result["attempted"] == 0
    assert result["errors"] == [{"category": "request_payload_hash_mismatch"}]
    assert called == []


def test_unauthorized_execution_fails_closed_before_preflight(tmp_path):
    called = []
    result = dispatch.execute(
        **{**_kwargs(tmp_path, lambda *args: called.append(args)), "authorize": False}
    )
    assert result["errors"] == [{"category": "authorization_required"}]
    assert result["attempted"] == 0
    assert called == []
