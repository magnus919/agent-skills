"""Tests for the paired evaluation path: sandbox, grader, comparison, orchestrator."""

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from eval_runner.models import AdapterOutput, EvalCase, ExitStatus, ToolEvent
from eval_runner.grader import AssertionVerdict, grade_output
from eval_runner.sandbox import cleanup_sandbox, stage_paired_sandboxes, stage_skill_sandbox
from eval_runner.comparison import build_comparison_report, format_comparison_summary
from eval_runner.paired import run_paired_trial
from eval_runner.fake_adapter import FakeAdapter


def _make_skill_dir(tmp: Path) -> Path:
    skill = tmp / "test-skill"
    skill.mkdir()
    (skill / "SKILL.md").write_text("---\nname: test-skill\n---\n# Test\n")
    (skill / "README.md").write_text("# Test Skill\n")
    refs = skill / "references"
    refs.mkdir()
    (refs / "guide.md").write_text("# Guide\n")
    scripts = skill / "scripts"
    scripts.mkdir()
    (scripts / "run.py").write_text("print('hello')\n")
    evals = skill / "evals"
    evals.mkdir()
    (evals / "evals.json").write_text("{}")
    tests = skill / "tests"
    tests.mkdir()
    (tests / "test_thing.py").write_text("pass\n")
    return skill


def _make_case(assertions: list[str] | None = None) -> EvalCase:
    return EvalCase(
        id="paired-test-01",
        prompt="Do the thing",
        expected_output="The thing is done",
        assertions=assertions or [
            "response_contains:paired-test-01",
            "exit_status:completed",
            "activation_evidence_contains:test-skill",
        ],
        files=[],
    )


def test_sandbox_excludes_eval_and_tests():
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        skill = _make_skill_dir(tmp_path)
        staged = stage_skill_sandbox(skill, readonly=False)

        assert (staged / "SKILL.md").is_file()
        assert (staged / "README.md").is_file()
        assert (staged / "references" / "guide.md").is_file()
        assert (staged / "scripts" / "run.py").is_file()
        assert not (staged / "evals").exists()
        assert not (staged / "tests").exists()

        cleanup_sandbox(staged)


def test_sandbox_readonly():
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        skill = _make_skill_dir(tmp_path)
        staged = stage_skill_sandbox(skill, readonly=True)

        skill_md = staged / "SKILL.md"
        assert skill_md.is_file()
        import os
        import stat
        mode = skill_md.stat().st_mode
        assert not (mode & stat.S_IWUSR)

        cleanup_sandbox(staged)


def test_baseline_sandbox_is_empty():
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        skill = _make_skill_dir(tmp_path)
        _, baseline = stage_paired_sandboxes(skill)

        assert baseline.is_dir()
        assert not (baseline / "SKILL.md").exists()
        assert list(baseline.iterdir()) == []

        cleanup_sandbox(baseline)


def test_grader_pass():
    output = AdapterOutput(
        exit_status=ExitStatus.COMPLETED,
        response="Hello paired-test-01 world",
        activation_evidence="loaded test-skill/SKILL.md",
        tool_events=[ToolEvent(name="x")],
    )
    result = grade_output("c1", ["response_contains:paired-test-01", "exit_status:completed"], output)
    assert result.passed
    assert result.pass_count == 2
    assert result.fail_count == 0


def test_grader_fail():
    output = AdapterOutput(
        exit_status=ExitStatus.COMPLETED,
        response="nothing here",
        activation_evidence=None,
    )
    result = grade_output("c1", ["response_contains:expected-thing"], output)
    assert not result.passed
    assert result.fail_count == 1


def test_grader_infra_error():
    output = AdapterOutput(exit_status=ExitStatus.TIMEOUT, error="timed out")
    result = grade_output("c1", ["response_contains:x", "exit_status:completed"], output)
    assert not result.passed
    assert result.infra_error
    assert all(r.verdict == AssertionVerdict.INFRA_ERROR for r in result.results)


def test_grader_manual_review():
    output = AdapterOutput(exit_status=ExitStatus.COMPLETED, response="ok")
    result = grade_output("c1", ["some human-readable assertion"], output)
    assert result.passed
    assert result.manual_count == 1


def test_comparison_report_structure():
    output_pass = AdapterOutput(
        exit_status=ExitStatus.COMPLETED,
        response="paired-test-01 done",
        activation_evidence="test-skill loaded",
        tool_events=[ToolEvent(name="x")],
    )
    output_fail = AdapterOutput(
        exit_status=ExitStatus.COMPLETED,
        response="no match",
    )
    assertions = ["response_contains:paired-test-01"]
    c_grade = grade_output("c1", assertions, output_pass)
    b_grade = grade_output("c1", assertions, output_fail)

    report = build_comparison_report(
        skill_name="test-skill",
        case_id="c1",
        candidate_grade=c_grade,
        baseline_grade=b_grade,
        candidate_manifest={"trial_id": "aaa"},
        baseline_manifest={"trial_id": "bbb"},
    )

    assert report["schema_version"] == 1
    assert report["paired_delta"] == "candidate_improvement"
    assert report["candidate"]["passed"] is True
    assert report["baseline"]["passed"] is False

    summary = format_comparison_summary(report)
    assert "candidate_improvement" in summary


def test_comparison_report_validates_against_schema():
    try:
        from jsonschema import Draft202012Validator
    except ImportError:
        print("SKIP: jsonschema not installed")
        return

    schema_path = (
        Path(__file__).resolve().parent.parent.parent
        / "schemas"
        / "comparison-report-v1.schema.json"
    )
    schema = json.loads(schema_path.read_text())
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema)

    output = AdapterOutput(
        exit_status=ExitStatus.COMPLETED,
        response="paired-test-01",
        activation_evidence="test-skill",
        tool_events=[ToolEvent(name="x")],
    )
    assertions = ["response_contains:paired-test-01"]
    c_grade = grade_output("c1", assertions, output)
    b_grade = grade_output("c1", assertions, AdapterOutput(exit_status=ExitStatus.COMPLETED, response=""))

    report = build_comparison_report(
        skill_name="test-skill",
        case_id="c1",
        candidate_grade=c_grade,
        baseline_grade=b_grade,
        candidate_manifest={"trial_id": "aaa"},
        baseline_manifest={"trial_id": "bbb"},
    )

    errors = list(validator.iter_errors(report))
    assert not errors, f"Schema validation failed: {[e.message for e in errors]}"


def test_paired_trial_end_to_end():
    adapter = FakeAdapter()

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        skill = _make_skill_dir(tmp_path)
        case = _make_case()
        output_dir = tmp_path / "output"

        report = run_paired_trial(adapter, case, skill, output_dir, "fake-model")

        assert report["schema_version"] == 1
        assert report["case_id"] == "paired-test-01"
        assert report["candidate"]["passed"] is True
        assert (output_dir / "manifests").is_dir()
        assert (output_dir / "reports").is_dir()

        manifests = list((output_dir / "manifests").iterdir())
        assert len(manifests) == 2

        reports = list((output_dir / "reports").iterdir())
        assert len(reports) == 1


def test_paired_trial_candidate_cannot_read_evals():
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        skill = _make_skill_dir(tmp_path)
        staged = stage_skill_sandbox(skill, readonly=False)

        assert not (staged / "evals").exists()
        assert not (staged / "evals" / "evals.json").exists()

        cleanup_sandbox(staged)


if __name__ == "__main__":
    test_sandbox_excludes_eval_and_tests()
    test_sandbox_readonly()
    test_baseline_sandbox_is_empty()
    test_grader_pass()
    test_grader_fail()
    test_grader_infra_error()
    test_grader_manual_review()
    test_comparison_report_structure()
    test_comparison_report_validates_against_schema()
    test_paired_trial_end_to_end()
    test_paired_trial_candidate_cannot_read_evals()
    print("All paired evaluation tests passed.")
