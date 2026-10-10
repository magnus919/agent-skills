"""Offline acceptance checks for the bounded fair-pilot increment."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

import eval_runner.fair_pilot_qualification as qualification
from eval_runner.fair_pilot_mutations import run_mutation_suite
from eval_runner.fair_pilot_qualification import build_qualification_report

ROOT = Path(__file__).resolve().parents[2]


def test_policy_mutation_report_separates_defects_equivalence_invalid_and_infra():
    report = run_mutation_suite()
    assert report["status"] == "pass"
    assert report["baseline"]["case_count"] == 8
    assert report["baseline"]["failures"] == []
    assert report["baseline"]["gap_and_overlap_controls_passed"] is True
    assert len(report["valid_defects"]["killed"]) == 4
    assert report["valid_defects"]["survived"] == []
    assert [item["id"] for item in report["equivalent_mutants"]["accepted"]] == [
        "commute-duration-comparison"
    ]
    assert report["equivalent_mutants"]["changed_behavior"] == []
    assert [item["id"] for item in report["invalid_mutants"]] == ["unmatched-source-anchor"]
    assert len(report["infrastructure_errors"]) == 1
    assert report["infrastructure_errors"][0]["expected_control"] is True
    assert report["uncovered_checks"]
    assert report["semantic_mutation_controls"]["request_count"] == 12
    assert report["semantic_mutation_controls"]["semantic_paraphrase_pairs"] == 1
    assert (
        report["semantic_mutation_controls"]["label_review_status"]
        == "pending_independent_agent_review"
    )
    assert report["semantic_mutation_controls"]["dispatch_authorized"] is False


def test_policy_oracle_cli_is_reproducible_and_source_pinned():
    command = ["python3", "-m", "eval_runner.fair_pilot_mutations", "--json"]
    first = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, check=True)
    second = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, check=True)
    assert json.loads(first.stdout) == json.loads(second.stdout)


def test_qualification_dossier_has_twelve_reviewable_requests_and_no_dispatch():
    first = build_qualification_report()
    second = build_qualification_report()
    assert first == second
    assert first["status"] == "ready_for_independent_agent_review_not_dispatch"
    assert first["dispatch_authorized"] is False
    assert first["live_attempts"] == 0
    assert first["question_variant"] == "deployed"
    assert first["assertions_per_request"] == 1
    assert first["model"]
    assert first["endpoint"]
    assert first["shared_cap"] == "100 total; usage 0"
    assert first["initial_request_cap"] == 12
    assert first["reserved_follow_up_attempts"] == 12
    assert first["request_count"] == 12
    assert first["split_counts"] == {"development": 6, "held_out": 6}
    assert first["proposed_label_counts"] == {"met": 5, "not_met": 5, "not_shown": 2}
    assert all(
        request["label_review_status"] == "pending_independent_agent_review"
        for request in first["requests"]
    )
    assert all(request["request_payload_bytes"] < 100_000 for request in first["requests"])
    assert all(len(request["request_payload_sha256"]) == 64 for request in first["requests"])
    assert all(request["source_pins"] for request in first["requests"])


def test_qualification_dossier_uses_authored_controls_and_real_artifact_excerpts_separately():
    dossier = json.loads(
        (ROOT / "docs/fair-skill-evaluation-qualification-v1.json").read_text(encoding="utf-8")
    )
    records = dossier["records"]
    historical = [
        item for item in records if item["origin"] == "historical_generated_output_excerpt"
    ]
    authored = [item for item in records if item["origin"] != "historical_generated_output_excerpt"]
    assert len(historical) == 3
    assert len(authored) == 9
    assert all(item["parent_artifact"].get("response_sha256") for item in historical)
    assert all(
        "not_model_output" in item["origin"] or item["origin"].startswith("authored_")
        for item in authored
    )
    assert {item["sample_kind"] for item in records} >= {
        "positive",
        "negative",
        "contradictory",
        "missing_evidence",
        "semantic_paraphrase",
    }
    pair = [item for item in records if item.get("semantic_equivalence_pair")]
    assert len(pair) == 2
    assert pair[0]["assertion"] == pair[1]["assertion"]
    assert pair[0]["expected_label"] == pair[1]["expected_label"]
    assert pair[0]["response_sha256"] != pair[1]["response_sha256"]


def test_stale_frozen_response_artifact_fails_preflight(tmp_path, monkeypatch):
    dossier = json.loads(qualification.DOSSIER.read_text(encoding="utf-8"))
    authored = next(item for item in dossier["records"] if item["origin"].startswith("authored_"))
    authored["response"] += " stale edit"
    path = tmp_path / "stale-dossier.json"
    path.write_text(json.dumps(dossier), encoding="utf-8")
    monkeypatch.setattr(qualification, "DOSSIER", path)
    with pytest.raises(ValueError, match="authored response hash mismatch"):
        build_qualification_report()
