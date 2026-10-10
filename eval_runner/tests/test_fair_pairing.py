"""Matched pinned-snapshot inputs keep task and judgment evidence separated."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from eval_runner.models import EvalCase
from eval_runner.openai_adapter import NEUTRAL_SYSTEM_WRAPPER, OpenAICompatAdapter
from eval_runner.paired import run_paired_trial


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _snapshot(root: Path, *, skill: str, reference: str) -> None:
    (root / "references").mkdir(parents=True)
    (root / "evals").mkdir()
    (root / "SKILL.md").write_text(skill, encoding="utf-8")
    reference_bytes = reference.encode("utf-8")
    (root / "references/guide.md").write_bytes(reference_bytes)
    case = {
        "id": "pinned-case",
        "prompt": "Apply this task to the equipment-loan workflow.",
        "expected_output": "PRIVATE EXPECTED LABEL",
        "assertions": ["PRIVATE ASSERTION LABEL"],
    }
    (root / "evals/evals.json").write_text(json.dumps({"evals": [case]}), encoding="utf-8")
    (root / "evals/openai-reference-inputs.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "cases": {"pinned-case": {"references/guide.md": _sha256(reference_bytes)}},
            }
        ),
        encoding="utf-8",
    )


def test_pinned_pair_uses_each_snapshot_reference_and_neutral_shared_wrapper(tmp_path):
    candidate_root = tmp_path / "candidate"
    baseline_root = tmp_path / "baseline"
    _snapshot(candidate_root, skill="candidate guidance", reference="CANDIDATE SOURCE FACT")
    _snapshot(baseline_root, skill="old guidance", reference="BASELINE SOURCE FACT")
    source_bytes = (candidate_root / "references/guide.md").read_bytes()
    prompt = "Apply this task to the equipment-loan workflow."
    contract = {
        "schema_version": 1,
        "cases": {
            "pinned-case": {
                "task_inputs": {"prompt_sha256": _sha256(prompt.encode()), "fixture_sha256": {}},
                "authoritative_sources": [
                    {"path": "references/guide.md", "sha256": _sha256(source_bytes)}
                ],
                "expected_observable_outcomes": ["PRIVATE ORACLE LABEL"],
                "prohibited_behavior": ["PRIVATE PROHIBITED LABEL"],
                "required_evidence": ["PRIVATE REQUIRED EVIDENCE LABEL"],
                "oracle_type": "human_review",
            }
        },
    }
    contract_bytes = json.dumps(contract).encode("utf-8")
    (candidate_root / "evals/evidence-contract-v1.json").write_bytes(contract_bytes)

    response = MagicMock()
    response.__enter__.return_value.read.return_value = json.dumps(
        {"choices": [{"message": {"content": "fixture response"}, "finish_reason": "stop"}]}
    ).encode()
    adapter = OpenAICompatAdapter(
        "https://example.invalid", "fixture/model", max_tokens=512, temperature=0.2
    )

    with patch(
        "eval_runner.openai_adapter.urllib.request.urlopen", return_value=response
    ) as urlopen:
        report = run_paired_trial(
            adapter,
            EvalCase("pinned-case", prompt, "PRIVATE EXPECTED LABEL", ["PRIVATE ASSERTION LABEL"]),
            candidate_root,
            tmp_path / "output",
            "fixture/model",
            comparison_mode="pinned_skill_vs_skill",
            baseline_skill_path=baseline_root,
        )

    payloads = [json.loads(call.args[0].data) for call in urlopen.call_args_list]
    assert len(payloads) == 2
    candidate_messages, baseline_messages = (payload["messages"] for payload in payloads)
    candidate_context, baseline_context = (
        candidate_messages[0]["content"],
        baseline_messages[0]["content"],
    )
    assert candidate_context.startswith(NEUTRAL_SYSTEM_WRAPPER)
    assert baseline_context.startswith(NEUTRAL_SYSTEM_WRAPPER)
    assert (
        candidate_context.split("<skill_context>", 1)[0]
        == baseline_context.split("<skill_context>", 1)[0]
    )
    assert "CANDIDATE SOURCE FACT" in candidate_context
    assert "BASELINE SOURCE FACT" not in candidate_context
    assert "BASELINE SOURCE FACT" in baseline_context
    assert "CANDIDATE SOURCE FACT" not in baseline_context
    assert all(
        messages[-1] == {"role": "user", "content": prompt}
        for messages in (candidate_messages, baseline_messages)
    )
    all_payload_text = json.dumps(payloads)
    for hidden in (
        "PRIVATE EXPECTED LABEL",
        "PRIVATE ASSERTION LABEL",
        "PRIVATE ORACLE LABEL",
        "PRIVATE PROHIBITED LABEL",
        "PRIVATE REQUIRED EVIDENCE LABEL",
    ):
        assert hidden not in all_payload_text

    candidate_provenance = report["candidate"]["manifest"]["outputs"]["input_provenance"]
    baseline_provenance = report["baseline"]["manifest"]["outputs"]["input_provenance"]
    assert report["comparison_mode"] == "pinned_skill_vs_skill"
    assert candidate_provenance["comparison"] == baseline_provenance["comparison"]
    assert candidate_provenance["arm"] == "candidate"
    assert baseline_provenance["arm"] == "baseline"
    assert candidate_provenance["pair_id"] == baseline_provenance["pair_id"]
    for field in ("wrapper_sha256", "task_input_sha256", "model_settings_sha256"):
        assert candidate_provenance[field] == baseline_provenance[field]
        assert len(candidate_provenance[field]) == 64
    assert (
        candidate_provenance["model_settings_sha256"]
        == baseline_provenance["model_settings_sha256"]
    )
    assert candidate_provenance["sources"][-1]["sha256"] == _sha256(source_bytes)
    assert baseline_provenance["sources"][-1]["sha256"] == _sha256(b"BASELINE SOURCE FACT")
    assert candidate_provenance["evidence_contract_sha256"] == _sha256(contract_bytes)
    assert candidate_provenance["oracle_type"] == "human_review"


@pytest.mark.parametrize(
    "mode,baseline,match",
    [
        ("pinned_skill_vs_skill", None, "requires --baseline-skill-path"),
        ("skill_vs_no_skill", Path("somewhere"), "does not accept a baseline skill snapshot"),
    ],
)
def test_comparison_modes_fail_closed_on_missing_or_unexpected_snapshot(mode, baseline, match):
    from eval_runner.sandbox import stage_paired_sandboxes

    with pytest.raises(ValueError, match=match):
        stage_paired_sandboxes(
            Path("candidate"), comparison_mode=mode, baseline_skill_path=baseline
        )
