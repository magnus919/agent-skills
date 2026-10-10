"""Actual payload, source provenance, baseline parity, and fail-closed input tests."""

import hashlib
import json
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from eval_runner.models import AdapterInput, EvalCase
from eval_runner.openai_adapter import OpenAICompatAdapter
from eval_runner.reference_inputs import build_context, load_reference_inputs, read_source
from eval_runner.runner import load_cases
from eval_runner.sandbox import cleanup_sandbox, stage_paired_sandboxes

ROOT = Path(__file__).resolve().parents[2]
CASES = [
    ("product-design-and-ux", "embedded-loan-recovery", "embedded-business-agent.md"),
    ("pydanticai", "non-chat-proposal", "application-proposals.md"),
    ("spec-driven-development", "policy-translation-fidelity", "executable-business-policy.md"),
]


@pytest.mark.parametrize("skill,case_id,reference", CASES)
def test_actual_http_input_and_no_skill_baseline(tmp_path, skill, case_id, reference):
    source = ROOT / skill
    case = next(c for c in load_cases(source / "evals/evals.json") if c.id == case_id)
    candidate, baseline = stage_paired_sandboxes(source)
    adapter = OpenAICompatAdapter("https://example.invalid", "fixture/model")
    response = MagicMock()
    response.__enter__.return_value.read.return_value = json.dumps(
        {"choices": [{"message": {"content": "fixture"}, "finish_reason": "stop"}]}
    ).encode()
    try:
        with patch(
            "eval_runner.openai_adapter.urllib.request.urlopen", return_value=response
        ) as urlopen:
            result = adapter.execute(
                AdapterInput(candidate, case, tmp_path / "work", tmp_path / "output")
            )
        payload = json.loads(urlopen.call_args.args[0].data)
        messages = payload["messages"]
        supplied = messages[0]["content"]
        assert (source / "references" / reference).read_text() in supplied
        assert messages[-1] == {"role": "user", "content": case.prompt}
        assert case.expected_output not in supplied
        assert all(assertion not in supplied for assertion in case.assertions)
        provenance = result.input_provenance
        assert (
            provenance["messages_sha256"]
            == hashlib.sha256(
                json.dumps(
                    messages, sort_keys=True, ensure_ascii=False, separators=(",", ":")
                ).encode()
            ).hexdigest()
        )
        assert [s["path"] for s in provenance["sources"]] == ["SKILL.md", "references/" + reference]
        assert (
            provenance["sources"][1]["sha256"]
            == hashlib.sha256((source / "references" / reference).read_bytes()).hexdigest()
        )
        baseline_messages, baseline_provenance = adapter._build_input(
            AdapterInput(baseline, case, tmp_path / "bwork", tmp_path / "boutput")
        )
        assert [message["role"] for message in baseline_messages] == ["system", "user"]
        assert baseline_messages[-1] == {"role": "user", "content": case.prompt}
        assert "<skill_context>\n\n</skill_context>" in baseline_messages[0]["content"]
        assert (
            messages[0]["content"].split("<skill_context>", 1)[0]
            == baseline_messages[0]["content"].split("<skill_context>", 1)[0]
        )
        assert baseline_provenance["condition"] == "no_skill"
        assert baseline_provenance["sources"] == []
        assert provenance["comparison"] == "skill_vs_no_skill"
        assert baseline_provenance["comparison"] == "skill_vs_no_skill"
        assert provenance["wrapper_sha256"] == baseline_provenance["wrapper_sha256"]
        assert provenance["task_input_sha256"] == baseline_provenance["task_input_sha256"]
        assert provenance["model_settings_sha256"] == baseline_provenance["model_settings_sha256"]
    finally:
        cleanup_sandbox(candidate)
        cleanup_sandbox(baseline)


def make_source(tmp_path):
    (tmp_path / "SKILL.md").write_text("Entry point")
    (tmp_path / "references").mkdir()
    (tmp_path / "references/selected.md").write_text("Selected public reference")
    (tmp_path / "references/unrelated.md").write_text("UNRELATED PRIVATE SENTINEL")
    (tmp_path / ".env").write_text("SECRET SENTINEL")
    return {
        "references/selected.md": hashlib.sha256(
            (tmp_path / "references/selected.md").read_bytes()
        ).hexdigest()
    }


def test_only_explicit_sources_and_deterministic_order(tmp_path):
    refs = make_source(tmp_path)
    content, metadata = build_context(tmp_path, refs, None)
    assert "Selected public reference" in content
    assert "SENTINEL" not in content
    assert len(metadata["sources"]) == 2
    assert build_context(tmp_path, refs, None) == (content, metadata)


@pytest.mark.parametrize(
    "path",
    [
        "../private.md",
        "/private.md",
        "references/../private.md",
        "evals/rubric.md",
        ".env",
        "references/.secret.md",
        "references/nested/guide.md",
    ],
)
def test_forbidden_input_paths(tmp_path, path):
    make_source(tmp_path)
    with pytest.raises(ValueError):
        build_context(tmp_path, {path: "a" * 64}, None)


def test_missing_hash_drift_and_size_are_errors(tmp_path):
    refs = make_source(tmp_path)
    with pytest.raises(ValueError, match="hash mismatch"):
        build_context(tmp_path, {"references/selected.md": "a" * 64}, None)
    with pytest.raises(FileNotFoundError):
        build_context(tmp_path, {"references/missing.md": "a" * 64}, None)
    (tmp_path / "references/selected.md").write_bytes(b"x" * 60_001)
    with pytest.raises(ValueError, match="byte limit"):
        build_context(tmp_path, refs, None)


@pytest.mark.parametrize("kind", ["file", "directory", "entry"])
def test_symlinks_are_rejected(tmp_path, kind):
    source = tmp_path / "source"
    source.mkdir()
    refs = make_source(source)
    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / "selected.md").write_text("SECRET")
    target = (
        source / "references/selected.md"
        if kind == "file"
        else source / "references"
        if kind == "directory"
        else source / "SKILL.md"
    )
    if target.is_dir():
        for p in target.iterdir():
            p.unlink()
        target.rmdir()
    else:
        target.unlink()
    target.symlink_to(outside if kind == "directory" else outside / "selected.md")
    with pytest.raises((OSError, ValueError)):
        build_context(source, refs, None)


def test_contract_unknown_case_and_grader_path_rejected(tmp_path):
    make_source(tmp_path)
    (tmp_path / "evals").mkdir()
    config = tmp_path / "evals/openai-reference-inputs.json"
    config.write_text(json.dumps({"schema_version": 1, "cases": {"unknown": {}}}))
    with pytest.raises(ValueError, match="unknown case"):
        load_reference_inputs(tmp_path, {"known"})
    config.write_text(
        json.dumps({"schema_version": 1, "cases": {"known": {"evals/oracle.md": "a" * 64}}})
    )
    with pytest.raises(ValueError):
        load_reference_inputs(tmp_path, {"known"})


def test_aggregate_and_count_bounds(tmp_path):
    refs = make_source(tmp_path)
    (tmp_path / "references/selected.md").write_bytes(b"x" * 50_000)
    for name in ("second", "third", "fourth"):
        (tmp_path / f"references/{name}.md").write_bytes(b"x" * 50_000)
    refs = {
        f"references/{name}.md": hashlib.sha256(b"x" * 50_000).hexdigest()
        for name in ("selected", "second")
    }
    with pytest.raises(ValueError, match="aggregate"):
        build_context(tmp_path, refs, None)
    refs.update({f"references/{name}.md": "a" * 64 for name in ("third", "fourth")})
    with pytest.raises(ValueError, match="at most three"):
        build_context(tmp_path, refs, None)
    with pytest.raises(ValueError):
        read_source(tmp_path, ".env", 3)


def test_invalid_pin_prevents_any_http_request(tmp_path):
    make_source(tmp_path)
    case = EvalCase(
        "known",
        "prompt",
        "expected",
        ["assertion"],
        skill_references={"references/selected.md": "a" * 64},
    )
    adapter = OpenAICompatAdapter("https://example.invalid", "fixture/model")
    with patch("eval_runner.openai_adapter.urllib.request.urlopen") as urlopen:
        with pytest.raises(ValueError, match="hash mismatch"):
            adapter.execute(AdapterInput(tmp_path, case, tmp_path / "work", tmp_path / "out"))
        urlopen.assert_not_called()
