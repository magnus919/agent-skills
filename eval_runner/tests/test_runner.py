"""Tests for the eval runner using the fake adapter."""

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from eval_runner import models as models
from eval_runner import fake_adapter as fake_adapter_mod
from eval_runner import manifest as manifest_mod

EvalCase = models.EvalCase
AdapterInput = models.AdapterInput
AdapterOutput = models.AdapterOutput
ExitStatus = models.ExitStatus
FakeAdapter = fake_adapter_mod.FakeAdapter
build_manifest = manifest_mod.build_manifest
write_manifest = manifest_mod.write_manifest

from datetime import datetime, timezone


def _make_case() -> EvalCase:
    return EvalCase(
        id="test-case-01",
        prompt="Do the thing",
        expected_output="The thing is done",
        assertions=["assertion one", "assertion two"],
        files=[],
    )


def _make_skill_dir(tmp: Path) -> Path:
    skill = tmp / "test-skill"
    skill.mkdir()
    (skill / "SKILL.md").write_text("---\nname: test-skill\n---\n# Test\n")
    evals_dir = skill / "evals"
    evals_dir.mkdir()
    manifest = {
        "schema_version": 1,
        "skill_name": "test-skill",
        "evals": [
            {
                "id": "test-case-01",
                "prompt": "Do the thing",
                "expected_output": "The thing is done",
                "assertions": ["assertion one", "assertion two"],
            }
        ],
    }
    (evals_dir / "evals.json").write_text(json.dumps(manifest, indent=2))
    return skill


def test_fake_adapter_returns_completed():
    adapter = FakeAdapter()
    assert adapter.name == "fake"
    assert adapter.version == "0.1.0"

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        skill = _make_skill_dir(tmp_path)
        case = _make_case()

        adapter_input = AdapterInput(
            skill_path=skill,
            case=case,
            work_dir=tmp_path / "work",
            output_dir=tmp_path / "output",
        )

        result = adapter.execute(adapter_input)
        assert result.exit_status == ExitStatus.COMPLETED
        assert result.response is not None
        assert "test-case-01" in result.response
        assert result.activation_evidence is not None
        assert len(result.tool_events) == 3  # 1 read + 2 assertions
        assert result.error is None
        assert result.duration_ms >= 0


def test_fake_adapter_missing_evidence():
    result = AdapterOutput(exit_status=ExitStatus.COMPLETED)
    missing = result.missing_evidence()
    assert "response" in missing
    assert "activation_evidence" in missing
    assert "token_usage" in missing
    assert "tool_events" in missing


def test_manifest_serialization():
    adapter = FakeAdapter()

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        skill = _make_skill_dir(tmp_path)
        case = _make_case()

        adapter_input = AdapterInput(
            skill_path=skill,
            case=case,
            work_dir=tmp_path / "work",
            output_dir=tmp_path / "output",
        )

        result = adapter.execute(adapter_input)
        now = datetime.now(timezone.utc)

        manifest = build_manifest(
            adapter_name=adapter.name,
            adapter_version=adapter.version,
            harness_name=adapter.name,
            harness_version=adapter.version,
            model_provider="fake",
            model_id="fake-model",
            adapter_input=adapter_input,
            adapter_output=result,
            started_at=now,
            finished_at=now,
        )

        assert manifest["schema_version"] == 1
        assert manifest["candidate"]["skill_name"] == "test-skill"
        assert manifest["case"]["case_id"] == "test-case-01"
        assert manifest["status"] == "completed"
        assert manifest["adapter"]["name"] == "fake"
        assert isinstance(manifest["missing_evidence"], list)

        manifest_path = write_manifest(manifest, tmp_path / "manifests")
        assert manifest_path.is_file()

        loaded = json.loads(manifest_path.read_text())
        assert loaded["trial_id"] == manifest["trial_id"]


def test_manifest_validates_against_schema():
    try:
        from jsonschema import Draft202012Validator
    except ImportError:
        print("SKIP: jsonschema not installed")
        return

    schema_path = (
        Path(__file__).resolve().parent.parent.parent
        / "schemas"
        / "run-manifest-v1.schema.json"
    )
    schema = json.loads(schema_path.read_text())
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema)

    adapter = FakeAdapter()

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        skill = _make_skill_dir(tmp_path)
        case = _make_case()

        adapter_input = AdapterInput(
            skill_path=skill,
            case=case,
            work_dir=tmp_path / "work",
            output_dir=tmp_path / "output",
        )

        result = adapter.execute(adapter_input)
        now = datetime.now(timezone.utc)

        manifest = build_manifest(
            adapter_name=adapter.name,
            adapter_version=adapter.version,
            harness_name=adapter.name,
            harness_version=adapter.version,
            model_provider="fake",
            model_id="fake-model",
            adapter_input=adapter_input,
            adapter_output=result,
            started_at=now,
            finished_at=now,
        )

        errors = list(validator.iter_errors(manifest))
        assert not errors, f"Schema validation failed: {[e.message for e in errors]}"


def test_eval_case_prompt_hash_deterministic():
    case = _make_case()
    assert case.prompt_hash == case.prompt_hash
    assert len(case.prompt_hash) == 16


if __name__ == "__main__":
    test_fake_adapter_returns_completed()
    test_fake_adapter_missing_evidence()
    test_manifest_serialization()
    test_manifest_validates_against_schema()
    test_eval_case_prompt_hash_deterministic()
    print("All tests passed.")
