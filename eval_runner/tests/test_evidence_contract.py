"""The optional pilot oracle contracts stay pinned and separate from tasks."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from eval_runner.evidence_contract import load_evidence_contracts
from eval_runner.runner import load_cases

ROOT = Path(__file__).resolve().parents[2]


def test_six_skill_plan_has_inventory_and_hidden_oracle_contracts():
    plan = json.loads((ROOT / "docs/fair-skill-evaluation-pilot-v1.json").read_text())
    pilot_contracts = json.loads(
        (ROOT / "eval_runner/fair-pilot-evidence-contracts-v1.json").read_text()
    )
    assert plan["status"] == "plan_only"
    assert plan["live_calls"]["shared_budget"] == "0/100"
    assert plan["live_calls"]["generation"] == "not_run"
    assert plan["live_calls"]["jev"] == "not_run"
    assert len(plan["pilot"]) == 6
    for item in plan["pilot"]:
        assert item["inventory_present"] is True
        assert item["behavior_verified"] is False
        assert item["mutation_targets"]
        assert item["oracle"]["independent_facts"]
        manifest_path = ROOT / item["skill"] / "evals/evals.json"
        cases = load_cases(manifest_path)
        assert item["case_id"] in {case.id for case in cases}
        contracts = load_evidence_contracts(manifest_path.parent.parent, cases)
        contract = contracts[item["case_id"]]
        assert contract["task_inputs"]["prompt_sha256"]
        assert contract["expected_observable_outcomes"]
        assert contract["prohibited_behavior"]
        assert contract["required_evidence"]
        assert contract["oracle_type"] == item["oracle"]["type"] or (
            item["skill"]
            in {
                "product-design-and-ux",
                "pydanticai",
                "spec-driven-development",
                "product-discovery",
                "system-one",
            }
            and contract["oracle_type"] == "human_review"
        )
        assert f"{item['skill']}/{item['case_id']}" in pilot_contracts["cases"]


def test_global_contract_ignores_other_skills_and_case_unknowns(tmp_path):
    (tmp_path / "eval_runner").mkdir()
    skill = tmp_path / "example-skill"
    (skill / "evals").mkdir(parents=True)
    (skill / "SKILL.md").write_text("skill", encoding="utf-8")
    (skill / "evals/evals.json").write_text(
        json.dumps(
            {
                "evals": [
                    {
                        "id": "case-one",
                        "prompt": "task",
                        "expected_output": "hidden",
                        "assertions": ["hidden assertion"],
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    contract = {
        "schema_version": 1,
        "cases": {
            "example-skill/case-one": {
                "task_inputs": {"prompt_sha256": ""},
                "authoritative_sources": [],
                "expected_observable_outcomes": ["outcome"],
                "prohibited_behavior": ["prohibited"],
                "required_evidence": ["evidence"],
                "oracle_type": "human_review",
            },
            "other-skill/unrelated-case": {"invalid": "ignored outside this scope"},
        },
    }
    (tmp_path / "eval_runner/fair-pilot-evidence-contracts-v1.json").write_text(
        json.dumps(contract), encoding="utf-8"
    )
    from eval_runner.models import EvalCase

    case = EvalCase("case-one", "task", "hidden", ["hidden assertion"])
    # The scoped contract is validated against the exact task prompt; replace
    # the empty pin with its correct full digest.
    import hashlib

    contract["cases"]["example-skill/case-one"]["task_inputs"] = {
        "prompt_sha256": hashlib.sha256(b"task").hexdigest(),
        "fixture_sha256": {},
    }
    (tmp_path / "eval_runner/fair-pilot-evidence-contracts-v1.json").write_text(
        json.dumps(contract), encoding="utf-8"
    )
    loaded = load_evidence_contracts(skill, [case])
    assert list(loaded) == ["case-one"]


def test_task_and_source_hash_drift_fail_closed(tmp_path):
    import hashlib

    from eval_runner.models import EvalCase

    (tmp_path / "evals").mkdir()
    (tmp_path / "references").mkdir()
    (tmp_path / "references/source.md").write_text("source v1", encoding="utf-8")
    case = EvalCase("case-one", "task", "hidden", ["hidden assertion"])
    contract = {
        "schema_version": 1,
        "cases": {
            "case-one": {
                "task_inputs": {
                    "prompt_sha256": hashlib.sha256(b"task").hexdigest(),
                    "fixture_sha256": {},
                },
                "authoritative_sources": [{"path": "references/source.md", "sha256": "0" * 64}],
                "expected_observable_outcomes": ["outcome"],
                "prohibited_behavior": ["prohibited"],
                "required_evidence": ["evidence"],
                "oracle_type": "human_review",
            }
        },
    }
    (tmp_path / "evals/evidence-contract-v1.json").write_text(
        json.dumps(contract), encoding="utf-8"
    )
    with pytest.raises(ValueError, match="source hash mismatch"):
        load_evidence_contracts(tmp_path, [case])
    contract["cases"]["case-one"]["authoritative_sources"] = []
    contract["cases"]["case-one"]["task_inputs"]["prompt_sha256"] = "0" * 64
    (tmp_path / "evals/evidence-contract-v1.json").write_text(
        json.dumps(contract), encoding="utf-8"
    )
    with pytest.raises(ValueError, match="prompt hash mismatch"):
        load_evidence_contracts(tmp_path, [case])
