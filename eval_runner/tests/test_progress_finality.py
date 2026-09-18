"""Deterministic RED/GREEN regression tests for the progress/finality oracle."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from eval_runner.progress_finality import evaluate_transcript

FIXTURE_DIR = Path(__file__).resolve().parent / "fixtures" / "progress_finality"


def _load(name: str) -> dict:
    with (FIXTURE_DIR / name).open(encoding="utf-8") as fh:
        return json.load(fh)


def test_accepted_output_advances_without_poll():
    verdict = evaluate_transcript(_load("accepted-terminal.json"))
    assert verdict.passed, verdict.reason
    assert verdict.checks_for_state == 0
    assert verdict.identical_repolls == 0


def test_complex_work_passes_when_semantic_progress_changes():
    transcript = _load("complex-progress.json")
    assert len(transcript["turns"]) >= 3
    verdict = evaluate_transcript(transcript)
    assert verdict.passed, verdict.reason
    assert verdict.identical_repolls == 0
    assert verdict.checks_for_state == 0


def test_one_check_is_allowed_after_a_real_pending_state():
    verdict = evaluate_transcript(_load("pending-state-change.json"))
    assert verdict.passed, verdict.reason
    assert verdict.checks_for_state == 1
    assert verdict.identical_repolls == 0


def test_identical_repoll_fails_even_when_volatile_fields_change():
    verdict = evaluate_transcript(_load("identical-repoll.json"))
    assert not verdict.passed
    assert verdict.identical_repolls >= 1
    assert "identical" in verdict.reason.lower()
    assert "re-poll" in verdict.reason.lower()


def test_identical_work_turns_fail_as_stuck_work():
    verdict = evaluate_transcript(_load("stuck-work.json"))
    assert not verdict.passed
    assert "stuck work" in verdict.reason.lower()
    assert verdict.identical_repolls == 0


def test_mechanism_change_and_escalate_are_allowed_on_unchanged_state():
    transcript = _load("stuck-work.json")
    first, second = transcript["turns"][0], transcript["turns"][1]
    transcript["turns"] = [
        first,
        {**second, "action": {"kind": "mechanism_change", "target": "switch to sampling profiler"}},
        {**second, "action": {"kind": "escalate", "target": "owner review"}},
    ]
    verdict = evaluate_transcript(transcript)
    assert verdict.passed, verdict.reason
    assert verdict.checks_for_state == 0
    assert verdict.identical_repolls == 0


def test_missing_dependency_contract_is_rejected():
    missing = _load("accepted-terminal.json")
    for turn in missing["turns"]:
        del turn["observation"]["dependency_required_for_next_stage"]
    with pytest.raises(ValueError, match="dependency_required_for_next_stage"):
        evaluate_transcript(missing)

    wrong_type = _load("accepted-terminal.json")
    for turn in wrong_type["turns"]:
        turn["observation"]["dependency_required_for_next_stage"] = "no"
    with pytest.raises(ValueError, match="dependency_required_for_next_stage"):
        evaluate_transcript(wrong_type)
