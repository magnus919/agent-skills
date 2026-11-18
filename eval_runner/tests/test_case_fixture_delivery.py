"""Verify fixtures are delivered byte-for-byte and kept separate from the rubric."""

import hashlib
import sys

import pytest

from eval_runner.cli_adapter import CliSubprocessAdapter
from eval_runner.fixtures import capture_fixtures
from eval_runner.models import AdapterInput, EvalCase, ExitStatus
from eval_runner.openai_adapter import OpenAICompatAdapter
from eval_runner.paired import run_paired_trial


def test_paired_subprocess_receives_equal_fixture_copies(tmp_path):
    skill = tmp_path / "skill"
    evals = skill / "evals"
    fixtures = evals / "fixtures"
    fixtures.mkdir(parents=True)
    (skill / "SKILL.md").write_text("# Trial Skill")
    (evals / "rubric.md").write_text("harness-only")
    payload = b"\x00\xfffixture\r\n"
    (fixtures / "input.bin").write_bytes(payload)
    case = EvalCase(
        "input-delivery",
        "Read the task fixture",
        "Recognizes the provided bytes",
        ["response_contains:fixture delivered"],
        ["evals/fixtures/input.bin"],
    )
    script = """
import os
from pathlib import Path
inputs = Path(os.environ["EVAL_INPUT_DIR"])
fixture = inputs / "evals/fixtures/input.bin"
assert fixture.read_bytes() == b"\\x00\\xfffixture\\r\\n"
assert not (inputs / "evals/rubric.md").exists()
fixture.unlink()  # The other arm must receive the original bytes.
print("fixture delivered")
"""
    result = run_paired_trial(
        CliSubprocessAdapter([sys.executable, "-c", script]),
        case,
        skill,
        tmp_path / "output",
        "fixture-cli",
    )
    for arm in ("candidate", "baseline"):
        assert result[arm]["semantic_verdict"] == "pass"
        assert result[arm]["manifest"]["case"]["fixture_hashes"] == {
            "evals/fixtures/input.bin": hashlib.sha256(payload).hexdigest()[:16]
        }


def test_fixture_capture_rejects_symlinks(tmp_path):
    (tmp_path / "file").write_bytes(b"fixture")
    (tmp_path / "link").symlink_to(tmp_path / "file")
    with pytest.raises(OSError):
        capture_fixtures(tmp_path, ["link"])


def test_api_adapter_declines_binary_fixture_without_sending_a_request(tmp_path, monkeypatch):
    def unexpected_egress(*args, **kwargs):
        pytest.fail("unexpected API call")

    monkeypatch.setattr("urllib.request.urlopen", unexpected_egress)
    (tmp_path / "input.bin").write_bytes(b"\xff")
    case = EvalCase("fixture-case", "Use a fixture", "", [], ["input.bin"])
    output = OpenAICompatAdapter("https://example.test", "fixture-model").execute(
        AdapterInput(tmp_path, case, tmp_path / "work", tmp_path / "output", fixture_dir=tmp_path)
    )
    assert output.exit_status == ExitStatus.ERROR
    assert "bounded UTF-8 task fixtures" in (output.error or "")


def test_api_adapter_includes_only_declared_text_fixture_in_user_message(tmp_path):
    (tmp_path / "input.json").write_text('{"fixture": true}')
    (tmp_path / "rubric.md").write_text("not an input")
    case = EvalCase("fixture-case", "Use a fixture", "", [], ["input.json"])
    adapter = OpenAICompatAdapter("https://example.test", "fixture-model")
    messages, provenance = adapter._build_input(
        AdapterInput(tmp_path, case, tmp_path / "work", tmp_path / "output", fixture_dir=tmp_path)
    )
    assert messages[1]["role"] == "user"
    assert '{"fixture": true}' in messages[1]["content"]
    assert "not an input" not in messages[1]["content"]
    assert provenance["task_fixtures"] == [
        {
            "path": "input.json",
            "sha256": hashlib.sha256(b'{"fixture": true}').hexdigest(),
            "bytes": 17,
        }
    ]
