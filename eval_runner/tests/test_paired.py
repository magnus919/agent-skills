"""Tests for the paired evaluation path: sandbox, grader, comparison, orchestrator."""

from __future__ import annotations

import json
import re
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from eval_runner.models import AdapterOutput, EvalCase, ExitStatus, ToolEvent
from eval_runner.grader import AssertionVerdict, grade_output
from eval_runner.sandbox import cleanup_sandbox, stage_paired_sandboxes, stage_skill_sandbox
from eval_runner.comparison import (
    build_comparison_report,
    format_comparison_summary,
    write_comparison_report,
)
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


def test_comparison_schema_matches_runtime_case_ids():
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
    validator = Draft202012Validator(schema["properties"]["case_id"])
    assert not list(validator.iter_errors("valid-case-1"))
    for unsafe_case_id in ["../case", "Uppercase", "case_id", "case\n"]:
        assert list(validator.iter_errors(unsafe_case_id)), unsafe_case_id


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


def test_sandbox_rejects_top_level_symlink():
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        skill = _make_skill_dir(tmp_path)
        outside = tmp_path / "outside.md"
        outside.write_text("private")
        (skill / "linked.md").symlink_to(outside)

        try:
            stage_skill_sandbox(skill, readonly=False)
        except ValueError as exc:
            assert "symlink" in str(exc)
        else:
            raise AssertionError("top-level symlink was staged")


def test_sandbox_rejects_nested_symlink():
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        skill = _make_skill_dir(tmp_path)
        outside = tmp_path / "outside.md"
        outside.write_text("private")
        (skill / "references" / "linked.md").symlink_to(outside)

        try:
            stage_skill_sandbox(skill, readonly=False)
        except ValueError as exc:
            assert "symlink" in str(exc)
        else:
            raise AssertionError("nested symlink was staged")


def test_paired_trial_uses_generic_model_label_in_artifacts():
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        report = run_paired_trial(
            FakeAdapter(),
            _make_case(),
            _make_skill_dir(tmp_path),
            tmp_path / "output",
            "private-runtime-model",
            "configured-model",
        )
        assert report["candidate"]["manifest"]["model"]["model_id"] == "configured-model"
        assert report["baseline"]["manifest"]["model"]["model_id"] == "configured-model"


def test_comparison_writer_rejects_unsafe_case_id():
    with tempfile.TemporaryDirectory() as tmp:
        try:
            write_comparison_report(
                {"case_id": "../../escape", "report_id": "report"},
                Path(tmp) / "reports",
            )
        except ValueError:
            pass
        else:
            raise AssertionError("comparison writer accepted an unsafe case ID")


def test_paired_trial_rejects_symlinked_output_subdirectory():
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        output_dir = tmp_path / "output"
        output_dir.mkdir()
        outside = tmp_path / "outside"
        outside.mkdir()
        (output_dir / "candidate").symlink_to(outside, target_is_directory=True)

        try:
            run_paired_trial(
                FakeAdapter(),
                _make_case(),
                _make_skill_dir(tmp_path),
                output_dir,
                "fake-model",
            )
        except ValueError as exc:
            assert "escapes designated root" in str(exc)
        else:
            raise AssertionError("symlinked output subdirectory escaped containment")


def test_cleanup_does_not_follow_replaced_sandbox_symlink():
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        staged = stage_skill_sandbox(_make_skill_dir(tmp_path))
        staging_root = staged.parent
        moved = staged.with_name("moved-skill")
        staged.rename(moved)

        outside = tmp_path / "outside"
        outside.mkdir()
        victim = outside / "victim.txt"
        victim.write_text("do not touch")
        original_mode = victim.stat().st_mode
        staged.symlink_to(outside, target_is_directory=True)

        cleanup_sandbox(staged)

        assert victim.read_text() == "do not touch"
        assert victim.stat().st_mode == original_mode
        assert not staging_root.exists()


def test_cleanup_does_not_follow_replaced_nested_symlink():
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        skill = _make_skill_dir(tmp_path)
        references = skill / "references"
        (references / "cleanup-reference.md").write_text("reference")
        staged = stage_skill_sandbox(skill)
        staging_root = staged.parent

        staged_references = staged / "references"
        staged.chmod(0o700)
        staged_references.chmod(0o700)
        staged_references.rename(staged / "moved-references")
        outside = tmp_path / "outside"
        outside.mkdir()
        victim = outside / "victim.txt"
        victim.write_text("do not touch")
        original_mode = outside.stat().st_mode
        staged_references.symlink_to(outside, target_is_directory=True)

        cleanup_sandbox(staged)

        assert victim.read_text() == "do not touch"
        assert outside.stat().st_mode == original_mode
        assert not staging_root.exists()


def test_workflow_uses_variables_without_deployment_defaults_and_pins_actions():
    workflow = (
        Path(__file__).resolve().parent.parent.parent
        / ".github"
        / "workflows"
        / "skill-eval.yml"
    ).read_text()
    assert "vars.EVAL_BASE_URL ||" not in workflow
    assert "vars.EVAL_MODEL ||" not in workflow
    assert "http://" not in workflow
    assert ".gguf" not in workflow
    assert "--model-label configured-model" in workflow
    action_refs = re.findall(r"uses: actions/[^@]+@([^ #\n]+)", workflow)
    assert action_refs
    assert all(re.fullmatch(r"[0-9a-f]{40}", ref) for ref in action_refs)


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
    test_comparison_schema_matches_runtime_case_ids()
    test_paired_trial_end_to_end()
    test_paired_trial_candidate_cannot_read_evals()
    test_sandbox_rejects_top_level_symlink()
    test_sandbox_rejects_nested_symlink()
    test_paired_trial_uses_generic_model_label_in_artifacts()
    test_comparison_writer_rejects_unsafe_case_id()
    test_paired_trial_rejects_symlinked_output_subdirectory()
    test_cleanup_does_not_follow_replaced_sandbox_symlink()
    test_cleanup_does_not_follow_replaced_nested_symlink()
    test_workflow_uses_variables_without_deployment_defaults_and_pins_actions()
    print("All paired evaluation tests passed.")
