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
from eval_runner import path_safety as path_safety_mod
from eval_runner.path_safety import contained_path
from eval_runner.runner import load_cases

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
        assert manifest["candidate"]["skill_path"] == "test-skill"
        assert not Path(manifest["candidate"]["skill_path"]).is_absolute()
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


def test_manifest_schema_enforces_public_identity_fields():
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
    candidate_properties = schema["properties"]["candidate"]["properties"]
    case_id_schema = schema["properties"]["case"]["properties"]["case_id"]

    skill_path_validator = Draft202012Validator(candidate_properties["skill_path"])
    assert not list(skill_path_validator.iter_errors("skill-name"))
    for unsafe_path in ["/private/skill", "../skill", "folder\\skill", "skill\n"]:
        assert list(skill_path_validator.iter_errors(unsafe_path)), unsafe_path

    case_id_validator = Draft202012Validator(case_id_schema)
    assert not list(case_id_validator.iter_errors("valid-case-1"))
    for unsafe_case_id in ["../case", "Uppercase", "case_id", "case\n"]:
        assert list(case_id_validator.iter_errors(unsafe_case_id)), unsafe_case_id


def test_eval_case_prompt_hash_deterministic():
    case = _make_case()
    assert case.prompt_hash == case.prompt_hash
    assert len(case.prompt_hash) == 16


def test_eval_case_rejects_unsafe_ids():
    invalid_ids = [
        "",
        "../escape",
        "/absolute",
        "folder/case",
        "folder\\case",
        ".leading",
        "Uppercase",
        "has_underscore",
        "has.dot",
        "leading-",
        "-trailing",
        "two--hyphens",
        "case\n",
        "x" * 65,
    ]
    for case_id in invalid_ids:
        try:
            EvalCase(
                id=case_id,
                prompt="prompt",
                expected_output="output",
                assertions=[],
            )
        except ValueError:
            pass
        else:
            raise AssertionError(f"unsafe case ID accepted: {case_id!r}")

    assert EvalCase(
        id="x" * 64,
        prompt="prompt",
        expected_output="output",
        assertions=[],
    ).id == "x" * 64


def test_eval_case_rejects_unsafe_fixture_paths():
    invalid_paths = [
        "../secret",
        "/absolute",
        "folder/../secret",
        "folder//file",
        "folder\\file",
        "folder/",
        "folder/file\n",
        "folder\nfile",
    ]
    for fixture_path in invalid_paths:
        try:
            EvalCase(
                id="fixture-case",
                prompt="prompt",
                expected_output="output",
                assertions=[],
                files=[fixture_path],
            )
        except ValueError:
            pass
        else:
            raise AssertionError(f"unsafe fixture path accepted: {fixture_path!r}")

    try:
        EvalCase(
            id="fixture-case",
            prompt="prompt",
            expected_output="output",
            assertions=[],
            files=["fixture.txt", "fixture.txt"],
        )
    except ValueError as exc:
        assert "must be unique" in str(exc)
    else:
        raise AssertionError("duplicate fixture paths were accepted")


def test_manifest_rejects_unsafe_artifact_paths():
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        skill = _make_skill_dir(tmp_path)
        output_dir = tmp_path / "output"
        output_dir.mkdir()
        adapter_input = AdapterInput(
            case=_make_case(),
            work_dir=tmp_path / "work",
            output_dir=output_dir,
            skill_path=skill,
        )
        adapter_output = AdapterOutput(
            exit_status=ExitStatus.COMPLETED,
            artifacts=["../secret"],
        )
        now = datetime.now(timezone.utc)
        try:
            build_manifest(
                adapter_name="fake",
                adapter_version="1",
                harness_name="fake",
                harness_version="1",
                adapter_input=adapter_input,
                adapter_output=adapter_output,
                model_provider="fake",
                model_id="fake",
                started_at=now,
                finished_at=now,
            )
        except ValueError:
            pass
        else:
            raise AssertionError("unsafe artifact path was hashed")


def test_hashing_rejects_symlink_escapes():
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        skill = _make_skill_dir(tmp_path)
        outside = tmp_path / "secret.txt"
        outside.write_text("secret")
        (skill / "fixture.txt").symlink_to(outside)

        case = EvalCase(
            id="fixture-case",
            prompt="prompt",
            expected_output="output",
            assertions=[],
            files=["fixture.txt"],
        )
        try:
            case.fixture_hashes(skill)
        except ValueError:
            pass
        else:
            raise AssertionError("fixture symlink escape was hashed")

        output_dir = tmp_path / "output"
        output_dir.mkdir()
        (output_dir / "artifact.txt").symlink_to(outside)
        adapter_input = AdapterInput(
            case=_make_case(),
            work_dir=tmp_path / "work",
            output_dir=output_dir,
            skill_path=skill,
        )
        adapter_output = AdapterOutput(
            exit_status=ExitStatus.COMPLETED,
            artifacts=["artifact.txt"],
        )
        now = datetime.now(timezone.utc)
        try:
            build_manifest(
                adapter_name="fake",
                adapter_version="1",
                harness_name="fake",
                harness_version="1",
                adapter_input=adapter_input,
                adapter_output=adapter_output,
                model_provider="fake",
                model_id="fake",
                started_at=now,
                finished_at=now,
            )
        except ValueError:
            pass
        else:
            raise AssertionError("artifact symlink escape was hashed")


def test_hashing_rejects_validation_to_open_symlink_swap():
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        skill = _make_skill_dir(tmp_path)
        fixture = skill / "fixture.txt"
        fixture.write_text("safe")
        outside = tmp_path / "secret.txt"
        outside.write_text("secret")
        case = EvalCase(
            id="fixture-case",
            prompt="prompt",
            expected_output="output",
            assertions=[],
            files=["fixture.txt"],
        )

        original_open = path_safety_mod.os.open
        swapped = False

        def swapping_open(path, flags, mode=0o777, *, dir_fd=None):
            nonlocal swapped
            if path == "fixture.txt" and dir_fd is not None and not swapped:
                fixture.unlink()
                fixture.symlink_to(outside)
                swapped = True
            return original_open(path, flags, mode, dir_fd=dir_fd)

        path_safety_mod.os.open = swapping_open
        try:
            try:
                case.fixture_hashes(skill)
            except ValueError:
                pass
            else:
                raise AssertionError("symlink swap escaped descriptor-relative hashing")
        finally:
            path_safety_mod.os.open = original_open
        assert swapped


def test_load_cases_rejects_unsafe_id():
    with tempfile.TemporaryDirectory() as tmp:
        manifest_path = Path(tmp) / "evals.json"
        manifest_path.write_text(
            json.dumps(
                {
                    "evals": [
                        {
                            "id": "../../escape",
                            "prompt": "prompt",
                            "expected_output": "output",
                        }
                    ]
                }
            )
        )
        try:
            load_cases(manifest_path)
        except ValueError as exc:
            assert "invalid eval case ID" in str(exc)
        else:
            raise AssertionError("unsafe manifest case ID was accepted")


def test_contained_path_rejects_escape():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp) / "output"
        for parts in [("..", "escape"), (str(Path(tmp).parent / "absolute"),)]:
            try:
                contained_path(root, *parts)
            except ValueError:
                pass
            else:
                raise AssertionError(f"escaping output path accepted: {parts!r}")


def test_manifest_writer_rejects_unsafe_case_id():
    with tempfile.TemporaryDirectory() as tmp:
        manifest = {"trial_id": "trial", "case": {"case_id": "../../escape"}}
        try:
            write_manifest(manifest, Path(tmp) / "manifests")
        except ValueError:
            pass
        else:
            raise AssertionError("manifest writer accepted an unsafe case ID")


if __name__ == "__main__":
    test_fake_adapter_returns_completed()
    test_fake_adapter_missing_evidence()
    test_manifest_serialization()
    test_manifest_validates_against_schema()
    test_manifest_schema_enforces_public_identity_fields()
    test_eval_case_prompt_hash_deterministic()
    test_eval_case_rejects_unsafe_ids()
    test_eval_case_rejects_unsafe_fixture_paths()
    test_manifest_rejects_unsafe_artifact_paths()
    test_hashing_rejects_symlink_escapes()
    test_hashing_rejects_validation_to_open_symlink_swap()
    test_load_cases_rejects_unsafe_id()
    test_contained_path_rejects_escape()
    test_manifest_writer_rejects_unsafe_case_id()
    print("All tests passed.")
