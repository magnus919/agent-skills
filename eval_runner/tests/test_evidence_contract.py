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
        (ROOT / "eval_runner/fair-pilot-evidence-contracts-v2.json").read_text()
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
        assert contract["review_criteria"]
        assert set(contract["arm_sources"]) == {"candidate", "baseline"}
        assert contract["arm_sources"]["candidate"]["revision"] == item["candidate_revision"]
        assert contract["arm_sources"]["baseline"]["revision"] == item["baseline_revision"]
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
    (tmp_path / "eval_runner/fair-pilot-evidence-contracts-v2.json").write_text(
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
    (tmp_path / "eval_runner/fair-pilot-evidence-contracts-v2.json").write_text(
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


@pytest.mark.parametrize(
    "contract_path",
    sorted(
        list(ROOT.glob("*/evals/evidence-contract-v1.json"))
        + list(ROOT.glob("*/skills/*/evals/evidence-contract-v1.json"))
    ),
)
def test_checked_in_skill_evidence_contract(contract_path):
    skill = contract_path.parent.parent
    cases = load_cases(skill / "evals/evals.json")
    assert load_evidence_contracts(skill, cases)


@pytest.mark.parametrize(
    ("skill", "case_id", "observations"),
    [
        (
            "resilience-and-recovery",
            "restore-timing-with-content-mismatch",
            {
                "cutover": "hold",
                "recovery_time": "met",
                "content_integrity": "failed",
                "data_loss": "unverified",
            },
        ),
        (
            "migration-engineering",
            "cutover-blocked-by-content-parity",
            {
                "cutover": "hold",
                "active_writer": "source",
                "content_parity": "failed",
                "retry_safety": "unverified",
            },
        ),
        (
            "incident-learning",
            "followup-requires-observable-freeze-control",
            {
                "observed_entry_point": "retry",
                "other_entry_points": "unverified",
                "validation_owner": "release engineering",
            },
        ),
    ],
)
def test_lifecycle_decisions_resolve_without_passing_the_rationale(skill, case_id, observations):
    from eval_runner.grader import grade_output
    from eval_runner.models import AdapterOutput, ExitStatus

    case = next(
        case for case in load_cases(ROOT / skill / "evals/evals.json") if case.id == case_id
    )
    good = grade_output(
        case.id,
        case.assertions,
        AdapterOutput(ExitStatus.COMPLETED, response=json.dumps(observations)),
    )
    assert good.pass_count == len(observations)
    assert good.manual_count > 0
    assert not good.passed

    for field in observations:
        for bad in (
            {**observations, field: "contradiction"},
            {k: v for k, v in observations.items() if k != field},
        ):
            result = grade_output(
                case.id,
                case.assertions,
                AdapterOutput(ExitStatus.COMPLETED, response=json.dumps(bad)),
            )
            assert result.fail_count == 1


@pytest.mark.parametrize(
    ("assertion", "response", "verdict"),
    [
        ("response_json_equals:decision=true", '{"decision":true}', "pass"),
        ("response_json_equals:decision=true", '{"decision":true,"decision":true}', "fail"),
        ("response_json_equals:decision=true", '{"decision":1}', "fail"),
        ("response_json_equals:decision=true", "decision: true", "fail"),
        ("response_json_equals:decision=null", "{}", "fail"),
        ("response_json_equals:decision=null", '{"decision":null}', "pass"),
        ("response_json_equals:decision=unquoted", '{"decision":true}', "manual_review"),
    ],
)
def test_exact_json_decision_requires_a_valid_typed_field(assertion, response, verdict):
    from eval_runner.grader import grade_output
    from eval_runner.models import AdapterOutput, ExitStatus

    result = grade_output(
        "strict-json", [assertion], AdapterOutput(ExitStatus.COMPLETED, response=response)
    )
    assert result.results[0].verdict.value == verdict


@pytest.mark.parametrize(
    ("response_change", "expected_failures"),
    [
        ({}, 0),
        ({"complete": "hold"}, 1),
        ({"changed_manifest": "eligible"}, 1),
        ({"omitted_case": "eligible"}, 1),
        ({"advisory_only": "eligible"}, 1),
        ({"changed_manifest": None, "omitted_case": None}, 2),
    ],
)
def test_release_evidence_case_catches_missing_or_incorrect_decisions(
    response_change, expected_failures
):
    from eval_runner.grader import grade_output
    from eval_runner.models import AdapterOutput, ExitStatus

    cases = load_cases(ROOT / "agent-skills/evals/evals.json")
    case = next(case for case in cases if case.id == "release-evidence-pin-and-roster")
    response = {
        "complete": "eligible",
        "changed_manifest": "hold",
        "omitted_case": "hold",
        "advisory_only": "hold",
    }
    response.update(response_change)
    content = json.dumps({key: value for key, value in response.items() if value is not None})
    result = grade_output(
        case.id, case.assertions, AdapterOutput(ExitStatus.COMPLETED, response=content)
    )
    assert result.fail_count == expected_failures
    assert result.pass_count == 4 - expected_failures
    assert result.manual_count == 3
    assert not result.passed
