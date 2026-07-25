"""Tests for release-grade evaluation: trials, rubric, pairwise, release matrix."""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from eval_runner.release import (
    CalibrationRecord,
    CaseAggregation,
    FreezeSnapshot,
    RubricGrader,
    TrialRecord,
    aggregate_trials,
    apply_rubric,
    build_release_report,
    compute_release_decision,
    dataset_hash,
    evaluate_pairwise,
    plan_pairwise,
    write_release_report,
)


def _trial(case_id: str, status: str = "completed", passed: bool = True, missing: list[str] | None = None) -> dict:
    return {
        "trial_id": f"t-{case_id}-{status}",
        "case": {"case_id": case_id, "prompt_hash": "abc", "fixture_hashes": {}},
        "status": status,
        "failures": [] if passed and status == "completed" else [{"type": "assertion", "message": "fail"}],
        "missing_evidence": missing or [],
    }


def test_aggregate_trials_groups_by_case():
    manifests = [
        _trial("case-a", passed=True),
        _trial("case-a", passed=False),
        _trial("case-b", passed=True),
    ]
    results = aggregate_trials(manifests)
    assert len(results) == 2
    case_a = next(r for r in results if r.case_id == "case-a")
    assert case_a.trial_count == 2
    assert case_a.success_count == 1
    assert case_a.failure_count == 1
    assert case_a.success_frequency == 0.5
    assert not case_a.consistent


def test_aggregate_trials_consistency():
    manifests = [_trial("c1", passed=True), _trial("c1", passed=True), _trial("c1", passed=True)]
    results = aggregate_trials(manifests)
    assert results[0].consistent
    assert results[0].success_frequency == 1.0


def test_aggregate_trials_counts_errors_and_timeouts():
    manifests = [
        _trial("c1", status="completed", passed=True),
        _trial("c1", status="error", passed=False),
        _trial("c1", status="timeout", passed=False),
    ]
    results = aggregate_trials(manifests)
    agg = results[0]
    assert agg.success_count == 1
    assert agg.error_count == 1
    assert agg.timeout_count == 1
    assert agg.trial_count == 3


def test_aggregate_trials_preserves_all_failures():
    manifests = [
        _trial("c1", passed=False),
        _trial("c1", passed=False),
        _trial("c1", status="error", passed=False),
    ]
    results = aggregate_trials(manifests)
    agg = results[0]
    assert agg.failure_count == 2
    assert agg.error_count == 1
    assert agg.success_count == 0


def test_aggregate_trials_missing_evidence():
    manifests = [
        _trial("c1", passed=True, missing=["response"]),
        _trial("c1", passed=True, missing=["token_usage"]),
    ]
    results = aggregate_trials(manifests)
    assert set(results[0].all_missing_evidence) == {"response", "token_usage"}


def test_aggregate_trials_case_sets():
    manifests = [_trial("c1"), _trial("c2")]
    results = aggregate_trials(manifests, case_sets={"c1": "release", "c2": "regression"})
    assert results[0].case_set == "release"
    assert results[1].case_set == "regression"


def test_case_aggregation_to_dict():
    agg = CaseAggregation(
        case_id="c1",
        case_set="release",
        trials=[
            TrialRecord("t1", "c1", "completed", True),
            TrialRecord("t2", "c1", "completed", True),
        ],
    )
    d = agg.to_dict(paired_delta="both_pass")
    assert d["case_id"] == "c1"
    assert d["case_set"] == "release"
    assert d["trial_count"] == 2
    assert d["success_frequency"] == 1.0
    assert d["consistent"] is True
    assert d["paired_delta"] == "both_pass"


def test_rubric_grader_pass():
    grader = RubricGrader("test-grader", "1.0", ("relevance", "completeness"))
    result = grader.grade("the expected output is here and complete", "expected output is here and complete")
    assert result["verdict"] == "pass"
    assert result["grader_id"] == "test-grader"
    assert result["grader_version"] == "1.0"
    assert result["blinded"] is True


def test_rubric_grader_abstain_on_empty():
    grader = RubricGrader("test-grader", "1.0", ("relevance",))
    result = grader.grade("   ", "expected")
    assert result["verdict"] == "abstain"


def test_rubric_grader_insufficient_evidence_on_none():
    grader = RubricGrader("test-grader", "1.0", ("relevance",))
    result = grader.grade(None, "expected")
    assert result["verdict"] == "insufficient_evidence"


def test_rubric_grader_versioned():
    g1 = RubricGrader("g", "1.0", ("relevance",))
    g2 = RubricGrader("g", "2.0", ("relevance",))
    r1 = g1.grade("hello world", "hello world")
    r2 = g2.grade("hello world", "hello world")
    assert r1["grader_version"] == "1.0"
    assert r2["grader_version"] == "2.0"


def test_apply_rubric_adds_case_id():
    grader = RubricGrader("g", "1", ("relevance",))
    result = apply_rubric(grader, "case-42", "response text", "expected text")
    assert result["case_id"] == "case-42"


def test_plan_pairwise_deterministic():
    plans1 = plan_pairwise(["c1", "c2", "c3"], seed=42)
    plans2 = plan_pairwise(["c1", "c2", "c3"], seed=42)
    assert [(p.case_id, p.position_a) for p in plans1] == [(p.case_id, p.position_a) for p in plans2]


def test_plan_pairwise_blinded_positions():
    plans = plan_pairwise(["c1", "c2", "c3", "c4", "c5", "c6", "c7", "c8"], seed=99)
    positions = [p.position_a for p in plans]
    assert "candidate" in positions
    assert "baseline" in positions


def test_plan_pairwise_reversal():
    plan = plan_pairwise(["c1"], seed=1)[0]
    rev = plan.reversed
    assert rev.position_a == plan.position_b
    assert rev.position_b == plan.position_a


def test_evaluate_pairwise_order_reversal():
    plan = plan_pairwise(["c1"], seed=7)[0]
    result = evaluate_pairwise(
        plan,
        response_a="the complete expected answer with all details",
        response_b="partial answer",
        expected="the complete expected answer with all details",
    )
    assert result["order_reversal_tested"] is True
    assert result["order_reversal_consistent"] is not None
    assert result["case_id"] == "c1"


def test_evaluate_pairwise_abstain_on_none():
    plan = plan_pairwise(["c1"], seed=1)[0]
    result = evaluate_pairwise(plan, response_a=None, response_b="something", expected="something")
    assert result["winner"] == "abstain"


def test_calibration_not_calibrated():
    cal = CalibrationRecord()
    assert not cal.calibrated
    d = cal.to_dict()
    assert d["calibrated"] is False


def test_calibration_calibrated():
    cal = CalibrationRecord(human_sample_count=50, judge_agreement_rate=0.85)
    assert cal.calibrated
    d = cal.to_dict()
    assert d["calibrated"] is True
    assert d["judge_agreement_rate"] == 0.85


def test_calibration_low_agreement_not_calibrated():
    cal = CalibrationRecord(human_sample_count=50, judge_agreement_rate=0.5)
    assert not cal.calibrated


def test_release_decision_pass():
    cases = [
        {"case_id": "c1", "case_set": "release", "success_frequency": 1.0, "consistent": True, "missing_evidence": [], "paired_delta": "both_pass"},
    ]
    cal = CalibrationRecord(human_sample_count=20, judge_agreement_rate=0.9)
    decision = compute_release_decision(cases, [], cal)
    assert decision["outcome"] == "PASS"


def test_release_decision_block_on_hard_gate():
    decision = compute_release_decision([], [], CalibrationRecord(), hard_gate_violations=["privacy violation"])
    assert decision["outcome"] == "BLOCK"
    assert "privacy violation" in decision["reasons"][0]


def test_release_decision_hold_on_missing_evidence():
    cases = [
        {"case_id": "c1", "case_set": "release", "success_frequency": 1.0, "consistent": True, "missing_evidence": ["response"], "paired_delta": "both_pass"},
    ]
    decision = compute_release_decision(cases, [], CalibrationRecord())
    assert decision["outcome"] == "HOLD"


def test_release_decision_block_on_low_frequency():
    cases = [
        {"case_id": "c1", "case_set": "release", "success_frequency": 0.5, "consistent": False, "missing_evidence": [], "paired_delta": "both_pass"},
    ]
    cal = CalibrationRecord(human_sample_count=20, judge_agreement_rate=0.9)
    decision = compute_release_decision(cases, [], cal)
    assert decision["outcome"] == "BLOCK"


def test_release_decision_block_on_regression():
    cases = [
        {"case_id": "c1", "case_set": "regression", "success_frequency": 1.0, "consistent": True, "missing_evidence": [], "paired_delta": "candidate_regression"},
    ]
    cal = CalibrationRecord(human_sample_count=20, judge_agreement_rate=0.9)
    decision = compute_release_decision(cases, [], cal)
    assert decision["outcome"] == "BLOCK"


def test_release_decision_conditional_on_inconsistency():
    cases = [
        {"case_id": "c1", "case_set": "release", "success_frequency": 0.9, "consistent": False, "missing_evidence": [], "paired_delta": "both_pass"},
    ]
    cal = CalibrationRecord(human_sample_count=20, judge_agreement_rate=0.9)
    decision = compute_release_decision(cases, [], cal)
    assert decision["outcome"] == "CONDITIONAL"


def test_release_decision_conditional_on_uncalibrated_judge():
    cases = [
        {"case_id": "c1", "case_set": "release", "success_frequency": 1.0, "consistent": True, "missing_evidence": [], "paired_delta": "both_pass"},
    ]
    rubric = [{"case_id": "c1", "verdict": "pass"}]
    cal = CalibrationRecord()
    decision = compute_release_decision(cases, rubric, cal)
    assert decision["outcome"] == "CONDITIONAL"
    assert any("advisory" in r for r in decision["reasons"])


def test_release_decision_conditional_on_rubric_abstain():
    cases = [
        {"case_id": "c1", "case_set": "release", "success_frequency": 1.0, "consistent": True, "missing_evidence": [], "paired_delta": "both_pass"},
    ]
    rubric = [{"case_id": "c1", "verdict": "abstain"}]
    cal = CalibrationRecord(human_sample_count=20, judge_agreement_rate=0.9)
    decision = compute_release_decision(cases, rubric, cal)
    assert decision["outcome"] == "CONDITIONAL"


def test_freeze_snapshot_completeness():
    freeze = FreezeSnapshot(
        candidate_tree_hash="abc123",
        baseline_tree_hash="def456",
        dataset_hash="ghi789",
        grader_versions={"default": "1.0"},
        randomization_seed=42,
    )
    assert freeze.complete
    d = freeze.to_dict()
    assert d["candidate_tree_hash"] == "abc123"
    assert d["randomization_seed"] == 42


def test_freeze_snapshot_incomplete():
    freeze = FreezeSnapshot(
        candidate_tree_hash="",
        baseline_tree_hash="def456",
        dataset_hash="ghi789",
        grader_versions={},
        randomization_seed=42,
    )
    assert not freeze.complete


def test_build_release_report_structure():
    freeze = FreezeSnapshot("a", "b", "c", {"g": "1"}, 42)
    cal = CalibrationRecord(human_sample_count=10, judge_agreement_rate=0.8)
    report = build_release_report(
        skill_name="test-skill",
        freeze=freeze,
        case_results=[],
        rubric_results=[],
        pairwise_results=[],
        calibration=cal,
    )
    assert report["schema_version"] == 1
    assert report["skill_name"] == "test-skill"
    assert "report_id" in report
    assert "generated_at" in report
    assert report["release_decision"]["outcome"] in ("PASS", "CONDITIONAL", "HOLD", "BLOCK")


def test_build_release_report_validates_against_schema():
    try:
        from jsonschema import Draft202012Validator
    except ImportError:
        print("SKIP: jsonschema not installed")
        return

    schema_path = (
        Path(__file__).resolve().parent.parent.parent
        / "schemas"
        / "release-eval-v1.schema.json"
    )
    schema = json.loads(schema_path.read_text())
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema)

    freeze = FreezeSnapshot("abc", "def", "ghi", {"default-pairwise": "1"}, 42)
    cal = CalibrationRecord(human_sample_count=10, judge_agreement_rate=0.8)
    case_results = [
        {
            "case_id": "c1",
            "case_set": "release",
            "trial_count": 3,
            "success_count": 3,
            "failure_count": 0,
            "error_count": 0,
            "timeout_count": 0,
            "success_frequency": 1.0,
            "consistent": True,
            "missing_evidence": [],
            "paired_delta": "both_pass",
        }
    ]
    rubric_results = [
        {
            "case_id": "c1",
            "grader_id": "default-pairwise",
            "grader_version": "1",
            "blinded": True,
            "verdict": "pass",
            "scores": {"relevance": 0.9},
            "rationale": "good",
        }
    ]
    pairwise_results = [
        {
            "case_id": "c1",
            "position_a": "candidate",
            "position_b": "baseline",
            "winner": "a",
            "order_reversal_tested": True,
            "order_reversal_consistent": True,
        }
    ]

    report = build_release_report(
        skill_name="test-skill",
        freeze=freeze,
        case_results=case_results,
        rubric_results=rubric_results,
        pairwise_results=pairwise_results,
        calibration=cal,
    )

    errors = list(validator.iter_errors(report))
    assert not errors, f"Schema validation failed: {[e.message for e in errors]}"


def test_release_schema_matches_runtime_case_ids():
    try:
        from jsonschema import Draft202012Validator
    except ImportError:
        print("SKIP: jsonschema not installed")
        return

    schema_path = (
        Path(__file__).resolve().parent.parent.parent
        / "schemas"
        / "release-eval-v1.schema.json"
    )
    schema = json.loads(schema_path.read_text())
    for definition in ["case_result", "rubric_result", "pairwise_result"]:
        case_id_schema = schema["$defs"][definition]["properties"]["case_id"]
        validator = Draft202012Validator(case_id_schema)
        assert not list(validator.iter_errors("valid-case-1")), definition
        for unsafe_case_id in ["../case", "Uppercase", "case_id", "case\n"]:
            assert list(validator.iter_errors(unsafe_case_id)), (
                definition,
                unsafe_case_id,
            )


def test_write_release_report():
    import tempfile

    freeze = FreezeSnapshot("a", "b", "c", {"g": "1"}, 42)
    cal = CalibrationRecord()
    report = build_release_report(
        skill_name="my-skill",
        freeze=freeze,
        case_results=[],
        rubric_results=[],
        pairwise_results=[],
        calibration=cal,
    )
    with tempfile.TemporaryDirectory() as tmp:
        path = write_release_report(report, Path(tmp))
        assert path.is_file()
        assert "my-skill" in path.name
        loaded = json.loads(path.read_text())
        assert loaded["schema_version"] == 1


def test_dataset_hash_deterministic():
    import tempfile

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        f.write('{"evals": []}')
        f.flush()
        h1 = dataset_hash(Path(f.name))
        h2 = dataset_hash(Path(f.name))
        assert h1 == h2
        assert len(h1) == 16
    Path(f.name).unlink()


if __name__ == "__main__":
    test_aggregate_trials_groups_by_case()
    test_aggregate_trials_consistency()
    test_aggregate_trials_counts_errors_and_timeouts()
    test_aggregate_trials_preserves_all_failures()
    test_aggregate_trials_missing_evidence()
    test_aggregate_trials_case_sets()
    test_case_aggregation_to_dict()
    test_rubric_grader_pass()
    test_rubric_grader_abstain_on_empty()
    test_rubric_grader_insufficient_evidence_on_none()
    test_rubric_grader_versioned()
    test_apply_rubric_adds_case_id()
    test_plan_pairwise_deterministic()
    test_plan_pairwise_blinded_positions()
    test_plan_pairwise_reversal()
    test_evaluate_pairwise_order_reversal()
    test_evaluate_pairwise_abstain_on_none()
    test_calibration_not_calibrated()
    test_calibration_calibrated()
    test_calibration_low_agreement_not_calibrated()
    test_release_decision_pass()
    test_release_decision_block_on_hard_gate()
    test_release_decision_hold_on_missing_evidence()
    test_release_decision_block_on_low_frequency()
    test_release_decision_block_on_regression()
    test_release_decision_conditional_on_inconsistency()
    test_release_decision_conditional_on_uncalibrated_judge()
    test_release_decision_conditional_on_rubric_abstain()
    test_freeze_snapshot_completeness()
    test_freeze_snapshot_incomplete()
    test_build_release_report_structure()
    test_build_release_report_validates_against_schema()
    test_release_schema_matches_runtime_case_ids()
    test_write_release_report()
    test_dataset_hash_deterministic()
    print("All release evaluation tests passed.")
