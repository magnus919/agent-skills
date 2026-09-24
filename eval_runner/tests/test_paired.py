"""Tests for the paired evaluation path: sandbox, grader, comparison, orchestrator."""

from __future__ import annotations

import io
import json
import os
import re
import subprocess
import sys
import tempfile
import urllib.error
from datetime import datetime, timedelta, timezone
from email.utils import format_datetime
from pathlib import Path
from unittest.mock import MagicMock, patch

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from eval_runner.comparison import (
    build_comparison_report,
    format_comparison_summary,
    write_comparison_report,
)
from eval_runner.fake_adapter import FakeAdapter
from eval_runner.grader import AssertionVerdict, grade_output
from eval_runner.manifest import build_manifest
from eval_runner.models import AdapterInput, AdapterOutput, EvalCase, ExitStatus, ToolEvent
from eval_runner.openai_adapter import OpenAICompatAdapter, _retry_after_seconds
from eval_runner.paired import (
    infrastructure_error_count,
    run_paired_evaluation,
    run_paired_trial,
)
from eval_runner.sandbox import cleanup_sandbox, stage_paired_sandboxes, stage_skill_sandbox


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
        assertions=assertions
        or [
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
    result = grade_output(
        "c1", ["response_contains:paired-test-01", "exit_status:completed"], output
    )
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


def test_paired_runner_counts_generation_errors_as_nonzero_outcome():
    reports = [
        {"candidate": {"infra_error": True}, "baseline": {"infra_error": True}},
        {"candidate": {"infra_error": False}, "baseline": {"infra_error": False}},
    ]
    assert infrastructure_error_count(reports) == 2


def test_paired_runner_stops_after_first_infrastructure_failure():
    class ErrorAdapter:
        name = "fixture-error-adapter"
        version = "1"

        def __init__(self):
            self.calls = 0

        def execute(self, _input):
            self.calls += 1
            return AdapterOutput(exit_status=ExitStatus.ERROR, error="fixture failure")

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        skill = _make_skill_dir(tmp_path)
        cases = [
            _make_case(),
            EvalCase(
                id="paired-test-02",
                prompt="Again",
                expected_output="",
                assertions=["response_contains:x"],
            ),
        ]
        adapter = ErrorAdapter()
        reports = run_paired_evaluation(
            adapter, cases, skill, tmp_path / "output", model="fixture/model"
        )
        assert len(reports) == 1
        assert adapter.calls == 2
        assert infrastructure_error_count(reports) == 2


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

    assert report["schema_version"] == 2
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
        / "comparison-report-v2.schema.json"
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
    b_grade = grade_output(
        "c1", assertions, AdapterOutput(exit_status=ExitStatus.ERROR, error="fixture error")
    )

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
    assert report["paired_delta"] == "insufficient_data"


def test_comparison_schema_matches_runtime_case_ids():
    try:
        from jsonschema import Draft202012Validator
    except ImportError:
        print("SKIP: jsonschema not installed")
        return

    schema_path = (
        Path(__file__).resolve().parent.parent.parent
        / "schemas"
        / "comparison-report-v2.schema.json"
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

        assert report["schema_version"] == 2
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
        Path(__file__).resolve().parent.parent.parent / ".github" / "workflows" / "skill-eval.yml"
    ).read_text()
    assert "vars.EVAL_BASE_URL ||" not in workflow
    assert "vars.EVAL_MODEL ||" not in workflow
    assert "http://" not in workflow
    assert ".gguf" not in workflow
    assert "--model-label configured-model" not in workflow
    action_refs = re.findall(r"uses: actions/[^@]+@([^ #\n]+)", workflow)
    assert action_refs
    assert all(re.fullmatch(r"[0-9a-f]{40}", ref) for ref in action_refs)


def test_nous_key_is_scoped_to_trusted_model_job():
    workflow = yaml.safe_load(
        (
            Path(__file__).resolve().parent.parent.parent
            / ".github"
            / "workflows"
            / "skill-eval.yml"
        ).read_text()
    )
    jobs = workflow["jobs"]
    model_job = jobs["paired-eval-model"]

    assert "github.event_name == 'push'" in model_job["if"]
    assert "github.event_name == 'workflow_dispatch'" in model_job["if"]
    assert "github.ref == 'refs/heads/main'" in model_job["if"]
    assert "inputs.run_model_smoke" in model_job["if"]
    assert workflow["jobs"]["paired-eval-smoke"]["if"] == "github.event_name != 'workflow_dispatch'"
    audit_job = workflow["jobs"]["jev-eval-audit"]
    assert "github.event_name == 'push'" in audit_job["if"]
    assert "github.event_name == 'workflow_dispatch'" in audit_job["if"]
    assert "github.ref == 'refs/heads/main'" in audit_job["if"]
    assert "inputs.run_model_smoke" in audit_job["if"]
    endpoint_step = next(
        step for step in model_job["steps"] if step["name"] == "Check model endpoint"
    )
    inference_step = next(
        step for step in model_job["steps"] if step["name"] == "Run paired evaluation (real model)"
    )
    assert endpoint_step["env"]["NOUS_API_KEY"] == "${{ secrets.NOUS_API_KEY }}"
    assert inference_step["env"]["EVAL_API_KEY"] == "${{ secrets.NOUS_API_KEY }}"
    assert "--api-key" not in inference_step["run"]
    assert "--no-thinking" not in inference_step["run"]

    for job_name, job in jobs.items():
        if job_name != "paired-eval-model":
            assert "secrets.NOUS_API_KEY" not in json.dumps(job)


def test_manual_model_smoke_is_main_only_and_selects_fixed_manifest():
    workflow = yaml.load(
        (
            Path(__file__).resolve().parent.parent.parent
            / ".github"
            / "workflows"
            / "skill-eval.yml"
        ).read_text(),
        Loader=yaml.BaseLoader,
    )
    assert "workflow_dispatch" in workflow["on"]
    assert workflow["on"]["workflow_dispatch"]["inputs"]["run_model_smoke"]["type"] == "boolean"
    assert workflow["on"]["workflow_dispatch"]["inputs"]["model_id"]["type"] == "string"
    assert workflow["on"]["workflow_dispatch"]["inputs"]["model_id"]["default"] == (
        "poolside/laguna-s-2.1:free"
    )
    assert workflow["on"]["workflow_dispatch"]["inputs"]["max_output_tokens"]["type"] == "choice"
    assert workflow["on"]["workflow_dispatch"]["inputs"]["max_output_tokens"]["options"] == [
        "4096",
        "8192",
        "12288",
    ]
    assert workflow["on"]["workflow_dispatch"]["inputs"]["max_output_tokens"]["default"] == "4096"
    model_job = workflow["jobs"]["paired-eval-model"]
    assert "github.event_name == 'workflow_dispatch'" in model_job["if"]
    assert "github.ref == 'refs/heads/main'" in model_job["if"]
    assert "inputs.run_model_smoke" in model_job["if"]

    selection_step = next(
        step for step in model_job["steps"] if step["name"] == "Detect changed skills with evals"
    )
    endpoint_step = next(
        step for step in model_job["steps"] if step["name"] == "Check model endpoint"
    )
    inference_step = next(
        step for step in model_job["steps"] if step["name"] == "Run paired evaluation (real model)"
    )
    assert endpoint_step["env"]["EVAL_MODEL"] == "${{ inputs.model_id || vars.EVAL_MODEL }}"
    assert inference_step["env"]["EVAL_MODEL"] == "${{ inputs.model_id || vars.EVAL_MODEL }}"
    assert inference_step["env"]["MAX_OUTPUT_TOKENS"] == "${{ inputs.max_output_tokens || '4096' }}"
    assert '--max-tokens "$MAX_OUTPUT_TOKENS"' in inference_step["run"]
    assert "Manual model smoke evaluation." in selection_step["run"]
    assert "4096|8192|12288" in selection_step["run"]
    repo_root = Path(__file__).resolve().parent.parent.parent
    manifest_source = repo_root / "agent-skills" / "evals" / "evals.json"
    manifest_data = json.loads(manifest_source.read_text())
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        manifest_path = tmp_path / "agent-skills" / "evals" / "evals.json"
        manifest_path.parent.mkdir(parents=True)
        manifest_path.write_text(manifest_source.read_text())
        output_path = tmp_path / "github-output"
        summary_path = tmp_path / "github-summary"
        environment = {
            **os.environ,
            "PYTHONPATH": str(repo_root),
            "GITHUB_EVENT_NAME": "workflow_dispatch",
            "RUN_MODEL_SMOKE": "true",
            "BASE_SHA": "",
            "EVAL_MODEL": "poolside/laguna-s-2.1:free",
            "MAX_OUTPUT_TOKENS": "4096",
            "GITHUB_OUTPUT": str(output_path),
            "GITHUB_STEP_SUMMARY": str(summary_path),
        }
        result = subprocess.run(
            ["bash", "--noprofile", "--norc", "-e", "-o", "pipefail", "-c", selection_step["run"]],
            env=environment,
            cwd=tmp_path,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, result.stderr
        assert "manifests=agent-skills/evals/evals.json\n" in output_path.read_text()
        assert "eligible_count=1\n" in output_path.read_text()
        assert "selected_count=1\n" in output_path.read_text()
        assert "agent-skills/evals/evals.json" in summary_path.read_text()
        assert "poolside/laguna-s-2.1:free" in summary_path.read_text()
        assert "4096" in summary_path.read_text()
        selection = json.loads((tmp_path / "eval-output-model" / "selection.json").read_text())
        assert selection["status"] == "selected"
        assert selection["selected_count"] == 1
        assert selection["expected_cases"]["agent-skills"] == [
            case["id"] for case in manifest_data["evals"]
        ]

        environment["MAX_OUTPUT_TOKENS"] = "1024"
        output_path.write_text("")
        invalid_budget = subprocess.run(
            ["bash", "--noprofile", "--norc", "-e", "-o", "pipefail", "-c", selection_step["run"]],
            env=environment,
            cwd=tmp_path,
            capture_output=True,
            text=True,
        )
        assert invalid_budget.returncode != 0
        assert "Unsupported output-token ceiling" in invalid_budget.stderr
        assert output_path.read_text() == ""


def test_teacher_calibration_accepts_verified_manual_smokes_after_artifact_validation():
    workflow = yaml.load(
        (
            Path(__file__).resolve().parent.parent.parent
            / ".github"
            / "workflows"
            / "jev-teacher-calibration.yml"
        ).read_text(),
        Loader=yaml.BaseLoader,
    )
    job = workflow["jobs"]["teacher-label"]
    assert job["if"] == "github.ref == 'refs/heads/main'"
    steps = job["steps"]
    names = [step["name"] for step in steps]
    source_check = steps[names.index("Verify source is a completed main-branch paired evaluation")]
    assert "python3 system-one/scripts/jev_teacher_source.py" in source_check["run"]
    assert "gh api" in source_check["run"]
    prepare_index = names.index("Prepare prediction-blind packet")
    probe_index = names.index("Probe inference route with synthetic text only")
    teacher_index = names.index("Obtain two blind inference-model passes")
    assert prepare_index < probe_index < teacher_index
    assert "NOUS_API_KEY" in steps[probe_index]["env"]
    assert "NOUS_API_KEY" in steps[teacher_index]["env"]
    assert "NOUS_API_KEY" not in source_check.get("env", {})


def test_openai_adapter_uses_scoped_eval_api_key_from_environment():
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        adapter_input = AdapterInput(
            skill_path=tmp_path / "empty-skill",
            case=_make_case(),
            work_dir=tmp_path / "work",
            output_dir=tmp_path / "output",
            model="stepfun/step-3.7-flash",
        )
        response_body = {
            "choices": [{"message": {"content": "ok"}, "finish_reason": "stop"}],
            "usage": {"prompt_tokens": 1, "completion_tokens": 1},
        }
        response = MagicMock()
        response.__enter__.return_value.read.return_value = json.dumps(response_body).encode()

        with (
            patch.dict(os.environ, {"EVAL_API_KEY": "fixture-auth-42"}),
            patch(
                "eval_runner.openai_adapter.urllib.request.urlopen", return_value=response
            ) as urlopen,
        ):
            result = OpenAICompatAdapter(
                base_url="https://inference-api.nousresearch.com",
                model="stepfun/step-3.7-flash",
            ).execute(adapter_input)

        assert result.exit_status == ExitStatus.COMPLETED
        assert result.finish_reason == "stop"
        assert result.rate_limit_retries == 0
        assert result.environment_state["rate_limit_retries"] == 0
        request = urlopen.call_args.args[0]
        assert request.get_header("Authorization") == "Bearer fixture-auth-42"
        assert json.loads(request.data)["model"] == "stepfun/step-3.7-flash"


def test_openai_adapter_rejects_empty_and_incomplete_completions():
    cases = [
        ("", "stop", "stop", "empty assistant content (finish_reason=stop)"),
        ("  \n", "stop", "stop", "empty assistant content (finish_reason=stop)"),
        (
            "partial answer",
            "length",
            "length",
            "assistant completion did not end normally (finish_reason=length)",
        ),
        (
            "partial answer",
            "content_filter",
            "content_filter",
            "assistant completion did not end normally (finish_reason=content_filter)",
        ),
        (
            "",
            "private\ncontent",
            None,
            "empty assistant content",
        ),
    ]
    for index, (content, raw_finish_reason, expected_finish_reason, expected_error) in enumerate(
        cases
    ):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            adapter_input = AdapterInput(
                skill_path=tmp_path / "empty-skill",
                case=_make_case(),
                work_dir=tmp_path / "work",
                output_dir=tmp_path / "output",
                model="fixture/model",
            )
            body = {
                "choices": [
                    {
                        "message": {"content": content},
                        "finish_reason": raw_finish_reason,
                    }
                ],
                "usage": {"prompt_tokens": 11, "completion_tokens": 4096},
            }
            response = MagicMock()
            response.__enter__.return_value.read.return_value = json.dumps(body).encode()
            with patch("eval_runner.openai_adapter.urllib.request.urlopen", return_value=response):
                result = OpenAICompatAdapter(
                    base_url="https://example.invalid", model="fixture/model"
                ).execute(adapter_input)

            assert result.exit_status == ExitStatus.ERROR, index
            assert result.response is None, index
            assert result.finish_reason == expected_finish_reason, index
            assert result.error == f"model completion unusable: {expected_error}", index
            assert result.token_usage == {"input_tokens": 11, "output_tokens": 4096}, index
            assert result.duration_ms >= 0, index
            assert "private" not in (result.error or ""), index


def test_truncated_openai_completion_is_infra_error_in_paired_report():
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        skill = _make_skill_dir(tmp_path)
        body = {
            "choices": [
                {
                    "message": {"content": "partial answer must not be retained"},
                    "finish_reason": "length",
                }
            ],
            "usage": {"prompt_tokens": 11, "completion_tokens": 4096},
        }
        response = MagicMock()
        response.__enter__.return_value.read.return_value = json.dumps(body).encode()
        adapter = OpenAICompatAdapter(base_url="https://example.invalid", model="fixture/model")

        with patch("eval_runner.openai_adapter.urllib.request.urlopen", return_value=response):
            report = run_paired_trial(
                adapter, _make_case(), skill, tmp_path / "paired-output", "fixture/model"
            )

        for side in ("candidate", "baseline"):
            trial = report[side]
            assert trial["infra_error"]
            assert trial["manifest"]["status"] == "error"
            assert trial["manifest"]["outputs"]["response"] is None
            assert trial["manifest"]["outputs"]["finish_reason"] == "length"
            assert trial["assertions"]
            assert all(item["verdict"] == "infra_error" for item in trial["assertions"])
        assert "partial answer" not in json.dumps(report)
        assert report["paired_delta"] == "insufficient_data"
        assert "not assessed" in format_comparison_summary(report)


def test_openai_adapter_keeps_only_safe_http_error_fields():
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        adapter_input = AdapterInput(
            skill_path=tmp_path / "empty-skill",
            case=_make_case(),
            work_dir=tmp_path / "work",
            output_dir=tmp_path / "output",
            model="fixture/model",
        )
        body = json.dumps(
            {
                "error": {
                    "type": "invalid_request_error",
                    "code": "unsupported_parameter",
                    "param": "chat_template_kwargs",
                    "message": "private generated response must not be retained",
                }
            }
        ).encode()
        error = urllib.error.HTTPError(
            "https://example.invalid/v1/chat/completions",
            400,
            "Bad Request",
            {},
            io.BytesIO(body),
        )
        with patch("eval_runner.openai_adapter.urllib.request.urlopen", side_effect=error):
            result = OpenAICompatAdapter(
                base_url="https://example.invalid", model="fixture/model"
            ).execute(adapter_input)

        assert result.exit_status == ExitStatus.ERROR
        assert result.error == (
            "HTTP 400: Bad Request (type=invalid_request_error, "
            "code=unsupported_parameter, param=chat_template_kwargs)"
        )
        assert "private generated response" not in result.error


def test_openai_adapter_retries_rate_limit_once_using_retry_after():
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        skill_path = _make_skill_dir(tmp_path)
        adapter_input = AdapterInput(
            skill_path=skill_path,
            case=_make_case(),
            work_dir=tmp_path / "work",
            output_dir=tmp_path / "output",
            model="fixture/model",
        )
        rate_limited = urllib.error.HTTPError(
            "https://example.invalid/v1/chat/completions",
            429,
            "Too Many Requests",
            {"Retry-After": "2"},
            io.BytesIO(b"{}"),
        )
        response = MagicMock()
        response.__enter__.return_value.read.return_value = json.dumps(
            {"choices": [{"message": {"content": "ok"}, "finish_reason": "stop"}]}
        ).encode()

        with (
            patch(
                "eval_runner.openai_adapter.urllib.request.urlopen",
                side_effect=[rate_limited, response],
            ) as urlopen,
            patch("eval_runner.openai_adapter.time.sleep") as sleep,
        ):
            result = OpenAICompatAdapter(
                base_url="https://example.invalid", model="fixture/model"
            ).execute(adapter_input)

        assert result.exit_status == ExitStatus.COMPLETED
        assert result.response == "ok"
        assert result.rate_limit_retries == 1
        assert result.environment_state["rate_limit_retries"] == 1
        assert urlopen.call_count == 2
        sleep.assert_called_once_with(2.0)

        now = datetime.now(timezone.utc)
        manifest = build_manifest(
            adapter_name="openai-compat",
            adapter_version="0.1.0",
            harness_name="openai-compat",
            harness_version="0.1.0",
            model_provider="fixture",
            model_id="fixture/model",
            adapter_input=adapter_input,
            adapter_output=result,
            started_at=now,
            finished_at=now,
        )
        assert manifest["outputs"]["rate_limit_retries"] == 1


def test_openai_adapter_records_retry_when_retry_is_also_rate_limited():
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        adapter_input = AdapterInput(
            skill_path=tmp_path / "empty-skill",
            case=_make_case(),
            work_dir=tmp_path / "work",
            output_dir=tmp_path / "output",
            model="fixture/model",
        )
        first_429 = urllib.error.HTTPError(
            "https://example.invalid/v1/chat/completions",
            429,
            "Too Many Requests",
            {"Retry-After": "0"},
            io.BytesIO(b"{}"),
        )
        second_429 = urllib.error.HTTPError(
            "https://example.invalid/v1/chat/completions",
            429,
            "Too Many Requests",
            {"Retry-After": "10"},
            io.BytesIO(b'{"error":{"message":"private provider detail"}}'),
        )

        with (
            patch(
                "eval_runner.openai_adapter.urllib.request.urlopen",
                side_effect=[first_429, second_429],
            ) as urlopen,
            patch("eval_runner.openai_adapter.time.sleep") as sleep,
        ):
            result = OpenAICompatAdapter(
                base_url="https://example.invalid", model="fixture/model"
            ).execute(adapter_input)

        assert result.exit_status == ExitStatus.ERROR
        assert result.rate_limit_retries == 1
        assert result.error == ("HTTP 429: Too Many Requests (retry_after_seconds=10)")
        assert "private provider detail" not in result.error
        assert urlopen.call_count == 2
        sleep.assert_called_once_with(0.0)


def test_openai_adapter_defers_rate_limit_retry_beyond_bounded_wait():
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        adapter_input = AdapterInput(
            skill_path=tmp_path / "empty-skill",
            case=_make_case(),
            work_dir=tmp_path / "work",
            output_dir=tmp_path / "output",
            model="fixture/model",
        )
        rate_limited = urllib.error.HTTPError(
            "https://example.invalid/v1/chat/completions",
            429,
            "Too Many Requests",
            {"Retry-After": "61"},
            io.BytesIO(b"{}"),
        )

        with (
            patch(
                "eval_runner.openai_adapter.urllib.request.urlopen",
                side_effect=rate_limited,
            ) as urlopen,
            patch("eval_runner.openai_adapter.time.sleep") as sleep,
        ):
            result = OpenAICompatAdapter(
                base_url="https://example.invalid", model="fixture/model"
            ).execute(adapter_input)

        assert result.exit_status == ExitStatus.ERROR
        assert result.error == (
            "HTTP 429: Too Many Requests (retry_after_seconds=61, retry_deferred=true)"
        )
        assert result.rate_limit_retries == 0
        urlopen.assert_called_once()
        sleep.assert_not_called()


def test_retry_after_http_date_is_parsed_as_utc():
    now = datetime(2026, 9, 24, 12, 0, 0, tzinfo=timezone.utc)
    retry_at = now + timedelta(seconds=17)
    header = format_datetime(retry_at, usegmt=True)

    assert _retry_after_seconds({"Retry-After": header}, now=now) == 17


def test_nous_endpoint_preflight_requires_key_and_sends_bearer_header():
    workflow = yaml.safe_load(
        (
            Path(__file__).resolve().parent.parent.parent
            / ".github"
            / "workflows"
            / "skill-eval.yml"
        ).read_text()
    )
    step = next(
        item
        for item in workflow["jobs"]["paired-eval-model"]["steps"]
        if item["name"] == "Check model endpoint"
    )
    script = step["run"]

    with tempfile.TemporaryDirectory() as tmp:
        temp_path = Path(tmp)
        bin_dir = temp_path / "bin"
        bin_dir.mkdir()
        curl_stub = bin_dir / "curl"
        curl_stub.write_text(
            '#!/bin/sh\nprintf \'%s\\n\' "$@" > "$CURL_ARGS_FILE"\n'
            'cat > "$CURL_HEADERS_FILE"\n'
            'if [ "${CURL_EXIT_CODE:-0}" != "0" ]; then exit "$CURL_EXIT_CODE"; fi\n'
            'printf \'{"data":[{"id":"%s"}]}\\n\' "${CURL_MODEL_ID:-stepfun/step-3.7-flash}"\n'
        )
        curl_stub.chmod(0o755)
        output_path = temp_path / "github-output"
        args_path = temp_path / "curl-args"
        headers_path = temp_path / "curl-headers"
        environment = {
            **os.environ,
            "PATH": f"{bin_dir}:{os.environ['PATH']}",
            "EVAL_BASE_URL": "https://inference-api.nousresearch.com",
            "EVAL_MODEL": "stepfun/step-3.7-flash:free",
            "GITHUB_OUTPUT": str(output_path),
            "CURL_ARGS_FILE": str(args_path),
            "CURL_HEADERS_FILE": str(headers_path),
            "CURL_EXIT_CODE": "0",
            "GITHUB_EVENT_NAME": "push",
            "RUN_MODEL_SMOKE": "false",
        }
        shell = ["bash", "--noprofile", "--norc", "-e", "-o", "pipefail", "-c", script]

        environment["NOUS_API_KEY"] = ""
        missing_key = subprocess.run(shell, env=environment, capture_output=True, text=True)
        assert missing_key.returncode == 0
        assert output_path.read_text() == "available=false\n"
        assert not args_path.exists()
        assert not headers_path.exists()

        environment["GITHUB_EVENT_NAME"] = "workflow_dispatch"
        environment["RUN_MODEL_SMOKE"] = "true"
        output_path.write_text("")
        manual_missing_key = subprocess.run(shell, env=environment, capture_output=True, text=True)
        assert manual_missing_key.returncode != 0
        assert output_path.read_text() == "available=false\n"
        assert not args_path.exists()
        assert not headers_path.exists()

        environment["NOUS_API_KEY"] = "fixture-bearer-42"
        environment["EVAL_BASE_URL"] = "https://untrusted.example"
        output_path.write_text("")
        manual_untrusted_base = subprocess.run(
            shell, env=environment, capture_output=True, text=True
        )
        assert manual_untrusted_base.returncode != 0
        assert output_path.read_text() == "available=false\n"
        assert not args_path.exists()
        assert not headers_path.exists()

        environment["GITHUB_EVENT_NAME"] = "push"
        environment["RUN_MODEL_SMOKE"] = "false"
        environment["NOUS_API_KEY"] = "fixture-bearer-42"
        environment["EVAL_BASE_URL"] = "https://untrusted.example"
        output_path.write_text("")
        untrusted_base = subprocess.run(shell, env=environment, capture_output=True, text=True)
        assert untrusted_base.returncode == 0
        assert output_path.read_text() == "available=false\n"
        assert not args_path.exists()
        assert not headers_path.exists()

        environment["EVAL_BASE_URL"] = "https://inference-api.nousresearch.com"
        environment["CURL_MODEL_ID"] = "stepfun/step-3.7-flash"
        output_path.write_text("")
        untrusted_model = subprocess.run(shell, env=environment, capture_output=True, text=True)
        assert untrusted_model.returncode != 0
        assert output_path.read_text() == "available=false\n"
        assert "not listed" in untrusted_model.stderr
        assert "fixture-bearer-42" not in untrusted_model.stdout
        assert "fixture-bearer-42" not in untrusted_model.stderr

        environment["EVAL_MODEL"] = "stepfun/step-3.7-flash"
        output_path.write_text("")
        authenticated = subprocess.run(shell, env=environment, capture_output=True, text=True)
        assert authenticated.returncode == 0
        assert output_path.read_text() == "available=true\n"
        curl_args = args_path.read_text().splitlines()
        assert "-H" in curl_args
        assert "@-" in curl_args
        assert "fixture-bearer-42" not in curl_args
        assert "https://inference-api.nousresearch.com/v1/models" in curl_args
        assert headers_path.read_text() == "Authorization: Bearer fixture-bearer-42\n"
        assert "fixture-bearer-42" not in authenticated.stdout
        assert "fixture-bearer-42" not in authenticated.stderr
        assert "fixture-bearer-42" not in output_path.read_text()

        output_path.write_text("")
        environment["CURL_EXIT_CODE"] = "22"
        unavailable = subprocess.run(shell, env=environment, capture_output=True, text=True)
        assert unavailable.returncode == 0
        assert output_path.read_text() == "available=false\n"

        environment["GITHUB_EVENT_NAME"] = "workflow_dispatch"
        environment["RUN_MODEL_SMOKE"] = "true"
        output_path.write_text("")
        manual_unavailable = subprocess.run(shell, env=environment, capture_output=True, text=True)
        assert manual_unavailable.returncode != 0
        assert output_path.read_text() == "available=false\n"
        assert "fixture-bearer-42" not in manual_unavailable.stdout
        assert "fixture-bearer-42" not in manual_unavailable.stderr


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
    test_nous_key_is_scoped_to_trusted_model_job()
    test_manual_model_smoke_is_main_only_and_selects_fixed_manifest()
    test_teacher_calibration_accepts_verified_manual_smokes_after_artifact_validation()
    test_openai_adapter_uses_scoped_eval_api_key_from_environment()
    test_openai_adapter_rejects_empty_and_incomplete_completions()
    test_truncated_openai_completion_is_infra_error_in_paired_report()
    test_openai_adapter_retries_rate_limit_once_using_retry_after()
    test_openai_adapter_records_retry_when_retry_is_also_rate_limited()
    test_openai_adapter_defers_rate_limit_retry_beyond_bounded_wait()
    test_retry_after_http_date_is_parsed_as_utc()
    test_nous_endpoint_preflight_requires_key_and_sends_bearer_header()
    print("All paired evaluation tests passed.")
