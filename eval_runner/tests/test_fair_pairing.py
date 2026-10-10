"""Matched pinned-snapshot inputs keep task and judgment evidence separated."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from eval_runner.models import AdapterInput, EvalCase
from eval_runner.openai_adapter import NEUTRAL_SYSTEM_WRAPPER, OpenAICompatAdapter
from eval_runner.paired import (
    _load_baseline_reference_map,
    _load_candidate_reference_map,
    _validate_arm_source_contract,
    run_paired_trial,
)


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def test_all_pilot_arm_maps_are_pinned_to_their_historical_snapshots():
    root = Path(__file__).resolve().parents[2]
    plan = json.loads((root / "docs/fair-skill-evaluation-pilot-v1.json").read_text())
    baseline_path = root / "docs/fair-skill-evaluation-baseline-references-v1.json"
    candidate_path = root / "docs/fair-skill-evaluation-candidate-references-v1.json"
    baseline_map = _load_baseline_reference_map(baseline_path)
    candidate_map = _load_candidate_reference_map(candidate_path)
    assert set(baseline_map) == set(candidate_map) == {item["case_id"] for item in plan["pilot"]}
    for item in plan["pilot"]:
        case_id, skill = item["case_id"], item["skill"]
        for arm, reference_map, revision_key in (
            ("candidate", candidate_map, "candidate_revision"),
            ("baseline", baseline_map, "baseline_revision"),
        ):
            assert item["arm_sources"][arm]["revision"] == item[revision_key]
            assert item["arm_sources"][arm]["references"] == [
                {"path": path, "sha256": digest} for path, digest in reference_map[case_id].items()
            ]
            for relative_path, expected_hash in reference_map[case_id].items():
                source = subprocess.run(
                    ["git", "show", f"{item[revision_key]}:{skill}/{relative_path}"],
                    check=True,
                    capture_output=True,
                ).stdout
                assert _sha256(source) == expected_hash
        contract = json.loads(
            (root / "eval_runner/fair-pilot-evidence-contracts-v2.json").read_text()
        )["cases"][f"{skill}/{case_id}"]
        assert contract["arm_sources"] == item["arm_sources"]
        assert contract["review_criteria"]


def test_candidate_and_baseline_map_loaders_validate_case_hashes(tmp_path):
    path = tmp_path / "references.json"
    path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "cases": {"case-one": {"references/guide.md": "a" * 64}},
            }
        ),
        encoding="utf-8",
    )
    expected = {"case-one": {"references/guide.md": "a" * 64}}
    assert _load_candidate_reference_map(path) == expected
    assert _load_baseline_reference_map(path) == expected


def test_arm_source_contract_rejects_revision_and_reference_mismatch():
    contract = {
        "arm_sources": {
            "candidate": {
                "revision": "a" * 40,
                "references": [{"path": "references/current.md", "sha256": "1" * 64}],
            },
            "baseline": {
                "revision": "b" * 40,
                "references": [{"path": "references/old.md", "sha256": "2" * 64}],
            },
        }
    }
    _validate_arm_source_contract(
        contract,
        candidate_revision="a" * 40,
        baseline_revision="b" * 40,
        candidate_references={"references/current.md": "1" * 64},
        baseline_references={"references/old.md": "2" * 64},
    )
    with pytest.raises(ValueError, match="candidate revision"):
        _validate_arm_source_contract(
            contract,
            candidate_revision="c" * 40,
            baseline_revision="b" * 40,
            candidate_references={"references/current.md": "1" * 64},
            baseline_references={"references/old.md": "2" * 64},
        )
    with pytest.raises(ValueError, match="baseline reference map"):
        _validate_arm_source_contract(
            contract,
            candidate_revision="a" * 40,
            baseline_revision="b" * 40,
            candidate_references={"references/current.md": "1" * 64},
            baseline_references={"references/old.md": "0" * 64},
        )


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


def _commit_snapshot(root: Path) -> str:
    subprocess.run(["git", "-C", str(root), "init", "-q"], check=True)
    subprocess.run(["git", "-C", str(root), "config", "user.name", "Eval Fixture"], check=True)
    subprocess.run(
        ["git", "-C", str(root), "config", "user.email", "eval-fixture@example.invalid"],
        check=True,
    )
    subprocess.run(["git", "-C", str(root), "add", "."], check=True)
    subprocess.run(["git", "-C", str(root), "commit", "-qm", "fixture snapshot"], check=True)
    return subprocess.run(
        ["git", "-C", str(root), "rev-parse", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


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
    candidate_revision = _commit_snapshot(candidate_root)
    baseline_revision = _commit_snapshot(baseline_root)

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
            comparison_policy="complete_package",
            candidate_revision=candidate_revision,
            baseline_revision=baseline_revision,
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
    assert report["comparison_policy"] == "complete_package"
    assert report["snapshot_revisions"] == {
        "candidate": candidate_revision,
        "baseline": baseline_revision,
    }
    assert (
        report["snapshot_inputs"]["candidate"]["context_sha256"]
        == candidate_provenance["context_sha256"]
    )
    assert (
        report["snapshot_inputs"]["baseline"]["context_sha256"]
        == baseline_provenance["context_sha256"]
    )
    assert report["snapshot_inputs"]["candidate"]["sources"][-1]["sha256"] == _sha256(source_bytes)
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
    assert candidate_provenance["comparison_policy"] == "complete_package"
    assert candidate_provenance["snapshot_revision"] == candidate_revision


class _CountingAdapter:
    name = "counting-fixture"
    version = "1"

    def __init__(self):
        self.calls = 0
        self.inputs: list[AdapterInput] = []

    def execute(self, input: AdapterInput):
        from eval_runner.models import AdapterOutput, ExitStatus

        self.calls += 1
        self.inputs.append(input)
        return AdapterOutput(exit_status=ExitStatus.COMPLETED, response="fixture response")


def _pinned_fixtures(tmp_path: Path) -> tuple[Path, Path, str, str, EvalCase]:
    candidate_root = tmp_path / "candidate"
    baseline_root = tmp_path / "baseline"
    _snapshot(candidate_root, skill="candidate guidance", reference="CANDIDATE SOURCE FACT")
    _snapshot(baseline_root, skill="old guidance", reference="BASELINE SOURCE FACT")
    return (
        candidate_root,
        baseline_root,
        _commit_snapshot(candidate_root),
        _commit_snapshot(baseline_root),
        EvalCase("pinned-case", "Apply this task to the equipment-loan workflow.", "Expected", []),
    )


def test_baseline_reference_hash_is_preflighted_before_candidate_execution(tmp_path):
    candidate_root, baseline_root, candidate_revision, baseline_revision, case = _pinned_fixtures(
        tmp_path
    )
    adapter = _CountingAdapter()

    with pytest.raises(ValueError, match="reference source hash mismatch"):
        run_paired_trial(
            adapter,
            case,
            candidate_root,
            tmp_path / "output",
            "fixture/model",
            comparison_mode="pinned_skill_vs_skill",
            baseline_skill_path=baseline_root,
            comparison_policy="complete_package",
            candidate_revision=candidate_revision,
            baseline_revision=baseline_revision,
            baseline_reference_map={"pinned-case": {"references/guide.md": "0" * 64}},
        )

    assert adapter.calls == 0


def test_candidate_reference_hash_is_preflighted_before_any_execution(tmp_path):
    candidate_root, baseline_root, candidate_revision, baseline_revision, case = _pinned_fixtures(
        tmp_path
    )
    adapter = _CountingAdapter()
    with pytest.raises(ValueError, match="hash mismatch"):
        run_paired_trial(
            adapter,
            case,
            candidate_root,
            tmp_path / "output",
            "fixture/model",
            comparison_mode="pinned_skill_vs_skill",
            baseline_skill_path=baseline_root,
            comparison_policy="complete_package",
            candidate_revision=candidate_revision,
            baseline_revision=baseline_revision,
            candidate_reference_map={"pinned-case": {"references/guide.md": "0" * 64}},
        )
    assert adapter.calls == 0


@pytest.mark.parametrize("wrong_side", ["candidate", "baseline"])
def test_snapshot_revision_mismatch_is_preflighted_before_any_execution(tmp_path, wrong_side):
    candidate_root, baseline_root, candidate_revision, baseline_revision, case = _pinned_fixtures(
        tmp_path
    )
    adapter = _CountingAdapter()
    if wrong_side == "candidate":
        candidate_revision = "0" * 40
    else:
        baseline_revision = "0" * 40

    with pytest.raises(ValueError, match="revision mismatch"):
        run_paired_trial(
            adapter,
            case,
            candidate_root,
            tmp_path / "output",
            "fixture/model",
            comparison_mode="pinned_skill_vs_skill",
            baseline_skill_path=baseline_root,
            comparison_policy="complete_package",
            candidate_revision=candidate_revision,
            baseline_revision=baseline_revision,
        )

    assert adapter.calls == 0


def test_complete_package_fails_closed_without_baseline_case_or_reference_map(tmp_path):
    candidate_root, baseline_root, candidate_revision, baseline_revision, case = _pinned_fixtures(
        tmp_path
    )
    baseline_manifest = json.loads((baseline_root / "evals/evals.json").read_text(encoding="utf-8"))
    baseline_manifest["evals"][0]["id"] = "old-baseline-case"
    (baseline_root / "evals/evals.json").write_text(json.dumps(baseline_manifest), encoding="utf-8")
    reference_map = json.loads(
        (baseline_root / "evals/openai-reference-inputs.json").read_text(encoding="utf-8")
    )
    reference_map["cases"]["old-baseline-case"] = reference_map["cases"].pop("pinned-case")
    (baseline_root / "evals/openai-reference-inputs.json").write_text(
        json.dumps(reference_map), encoding="utf-8"
    )
    # This is a legitimate pre-release case ID mismatch, so pin that source change too.
    baseline_revision = _commit_snapshot(baseline_root)
    adapter = _CountingAdapter()

    with pytest.raises(
        ValueError, match="matching baseline eval case or an explicit baseline reference map"
    ):
        run_paired_trial(
            adapter,
            case,
            candidate_root,
            tmp_path / "output",
            "fixture/model",
            comparison_mode="pinned_skill_vs_skill",
            baseline_skill_path=baseline_root,
            comparison_policy="complete_package",
            candidate_revision=candidate_revision,
            baseline_revision=baseline_revision,
        )

    assert adapter.calls == 0


def test_explicit_baseline_map_supplies_old_snapshot_reference_for_new_case_id(tmp_path):
    candidate_root, baseline_root, candidate_revision, baseline_revision, case = _pinned_fixtures(
        tmp_path
    )
    baseline_manifest = json.loads((baseline_root / "evals/evals.json").read_text(encoding="utf-8"))
    baseline_manifest["evals"][0]["id"] = "old-baseline-case"
    (baseline_root / "evals/evals.json").write_text(json.dumps(baseline_manifest), encoding="utf-8")
    reference_map = json.loads(
        (baseline_root / "evals/openai-reference-inputs.json").read_text(encoding="utf-8")
    )
    reference_map["cases"]["old-baseline-case"] = reference_map["cases"].pop("pinned-case")
    (baseline_root / "evals/openai-reference-inputs.json").write_text(
        json.dumps(reference_map), encoding="utf-8"
    )
    baseline_revision = _commit_snapshot(baseline_root)
    baseline_hash = _sha256((baseline_root / "references/guide.md").read_bytes())
    adapter = _CountingAdapter()

    run_paired_trial(
        adapter,
        case,
        candidate_root,
        tmp_path / "output",
        "fixture/model",
        comparison_mode="pinned_skill_vs_skill",
        baseline_skill_path=baseline_root,
        comparison_policy="complete_package",
        candidate_revision=candidate_revision,
        baseline_revision=baseline_revision,
        baseline_reference_map={
            "pinned-case": {"references/guide.md": baseline_hash},
        },
    )

    assert adapter.calls == 2
    assert adapter.inputs[0].case.skill_references == {
        "references/guide.md": _sha256((candidate_root / "references/guide.md").read_bytes())
    }
    assert adapter.inputs[1].case.skill_references == {"references/guide.md": baseline_hash}


def test_explicit_candidate_map_overrides_manifest_references_from_candidate_snapshot(tmp_path):
    candidate_root, baseline_root, _, baseline_revision, case = _pinned_fixtures(tmp_path)
    explicit = b"candidate reference selected by a pinned pilot map"
    (candidate_root / "references/explicit.md").write_bytes(explicit)
    candidate_revision = _commit_snapshot(candidate_root)
    adapter = _CountingAdapter()

    run_paired_trial(
        adapter,
        case,
        candidate_root,
        tmp_path / "output",
        "fixture/model",
        comparison_mode="pinned_skill_vs_skill",
        baseline_skill_path=baseline_root,
        comparison_policy="complete_package",
        candidate_revision=candidate_revision,
        baseline_revision=baseline_revision,
        candidate_reference_map={"pinned-case": {"references/explicit.md": _sha256(explicit)}},
    )

    assert adapter.calls == 2
    assert adapter.inputs[0].case.skill_references == {"references/explicit.md": _sha256(explicit)}
    assert adapter.inputs[1].case.skill_references == {
        "references/guide.md": _sha256((baseline_root / "references/guide.md").read_bytes())
    }


def test_dirty_snapshot_fails_before_any_execution(tmp_path):
    candidate_root, baseline_root, candidate_revision, baseline_revision, case = _pinned_fixtures(
        tmp_path
    )
    (baseline_root / "references/guide.md").write_text("changed after pin", encoding="utf-8")
    adapter = _CountingAdapter()

    with pytest.raises(ValueError, match="changed or untracked files"):
        run_paired_trial(
            adapter,
            case,
            candidate_root,
            tmp_path / "output",
            "fixture/model",
            comparison_mode="pinned_skill_vs_skill",
            baseline_skill_path=baseline_root,
            comparison_policy="complete_package",
            candidate_revision=candidate_revision,
            baseline_revision=baseline_revision,
        )

    assert adapter.calls == 0


def test_instruction_only_policy_omits_references_from_both_arms_and_is_reported(tmp_path):
    candidate_root, baseline_root, candidate_revision, baseline_revision, case = _pinned_fixtures(
        tmp_path
    )
    adapter = _CountingAdapter()

    report = run_paired_trial(
        adapter,
        case,
        candidate_root,
        tmp_path / "output",
        "fixture/model",
        comparison_mode="pinned_skill_vs_skill",
        baseline_skill_path=baseline_root,
        comparison_policy="instruction_only",
        candidate_revision=candidate_revision,
        baseline_revision=baseline_revision,
    )

    assert adapter.calls == 2
    assert [item.case.skill_references for item in adapter.inputs] == [{}, {}]
    assert report["comparison_policy"] == "instruction_only"


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
