#!/usr/bin/env python3
"""Offline teaching examples for evidence-grounded System One decisions.

All model answers below are synthetic fixtures. This module makes no network
calls and performs no live actions; action outcomes are injected observations.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from typing import Any


class ContractError(ValueError):
    """A fixture or decision violates the bounded example contract."""


def _probability(value: Any, field: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ContractError(f"{field} must be a finite number from 0 to 1")
    value = float(value)
    if not math.isfinite(value) or not 0 <= value <= 1:
        raise ContractError(f"{field} must be a finite number from 0 to 1")
    return value


def select_candidate(candidates: list[dict[str, str]], answer: dict[str, Any], cutoff: float) -> dict[str, Any]:
    """Validate one bounded candidate proposal; cutoff is fixture policy only."""
    cutoff = _probability(cutoff, "cutoff")
    if not isinstance(candidates, list) or not candidates:
        raise ContractError("candidates must be a non-empty list")
    ids: list[str] = []
    for candidate in candidates:
        if not isinstance(candidate, dict) or not isinstance(candidate.get("id"), str) or not candidate["id"]:
            raise ContractError("each candidate needs a non-empty string id")
        ids.append(candidate["id"])
    if len(ids) != len(set(ids)):
        raise ContractError("candidate ids must be unique")
    if not isinstance(answer, dict):
        raise ContractError("answer must be an object")

    outcome = answer.get("outcome")
    if outcome == "unavailable":
        if answer.get("candidate_id") is not None:
            raise ContractError("unavailable answer cannot name a candidate")
        return {"route": "escalate", "reason": "decision_unavailable", "permission": "not_granted"}
    if outcome == "no_match":
        if answer.get("candidate_id") is not None:
            raise ContractError("no-match answer cannot name a candidate")
        return {"route": "no_match", "reason": "no_candidate_applicable", "permission": "not_granted"}
    if outcome != "candidate":
        raise ContractError("outcome must be candidate, no_match, or unavailable")
    candidate_id = answer.get("candidate_id")
    if candidate_id not in ids:
        raise ContractError("candidate_id must identify a supplied candidate")
    p_applicable = _probability(answer.get("p_applicable"), "p_applicable")
    if p_applicable < cutoff:
        return {"route": "no_match", "reason": "below_example_cutoff", "permission": "not_granted"}
    return {"route": "select", "candidate_id": candidate_id, "p_applicable": p_applicable, "permission": "not_granted"}


def select_and_check_action(proposal: dict[str, Any], allowed_actions: list[dict[str, str]], evidence: dict[str, Any], current_revision: str, observed: dict[str, Any]) -> dict[str, Any]:
    """Check a proposed action against current evidence and a simulated result."""
    if not isinstance(proposal, dict):
        raise ContractError("proposal must be an object")
    ids = [x.get("id") for x in allowed_actions if isinstance(x, dict)]
    if (
        len(ids) != len(allowed_actions)
        or not ids
        or any(not isinstance(item, str) or not item for item in ids)
        or len(ids) != len(set(ids))
    ):
        raise ContractError("allowed action ids must be present and unique")
    action_id = proposal.get("action_id")
    if not isinstance(action_id, str) or not action_id or action_id not in ids:
        raise ContractError("action_id must identify a supplied allowed action")
    if not isinstance(evidence, dict) or not isinstance(current_revision, str) or not current_revision:
        raise ContractError("current evidence and revision are required")
    expected_effect = proposal.get("expected_effect")
    if not isinstance(expected_effect, str) or not expected_effect:
        raise ContractError("expected_effect must be a non-empty string")
    if evidence.get("revision") != current_revision or proposal.get("evidence_revision") != current_revision:
        return {"status": "rejected", "reason": "stale_evidence", "simulated_executor_fixture_used": False, "permission": "not_granted"}
    if not isinstance(observed, dict):
        raise ContractError("observed result must be an object")
    if observed.get("error"):
        return {"status": "unknown", "reason": "execution_error", "simulated_executor_fixture_used": True, "error": str(observed["error"]), "permission": "not_granted"}
    if not isinstance(observed.get("effect"), str) or observed.get("effect") != expected_effect:
        return {"status": "failed", "reason": "effect_not_observed", "simulated_executor_fixture_used": True, "observed_effect": observed.get("effect"), "permission": "not_granted"}
    if observed.get("outcome") != "pass":
        return {"status": "incomplete", "reason": "outcome_not_verified", "simulated_executor_fixture_used": True, "permission": "not_granted"}
    return {"status": "verified", "reason": "effect_and_outcome_observed", "simulated_executor_fixture_used": True, "permission": "not_granted"}


def review_proposal(review: dict[str, Any], evidence: dict[str, str], current_revision: str) -> dict[str, Any]:
    """Validate semantic-review evidence; output is an input to policy, not a grant."""
    if not isinstance(review, dict) or not isinstance(evidence, dict):
        raise ContractError("review and evidence must be objects")
    if review.get("revision") != current_revision:
        return {"status": "rejected", "reason": "stale_review", "permission": "not_granted", "findings": []}
    refs = review.get("evidence_ids")
    if not isinstance(refs, list) or any(not isinstance(ref, str) for ref in refs):
        raise ContractError("evidence_ids must be a list of strings")
    if not refs:
        raise ContractError("review must cite at least one evidence item")
    if any(ref not in evidence for ref in refs):
        raise ContractError("review cites evidence outside the supplied evidence set")
    disposition = review.get("disposition")
    if disposition not in {"supported", "unsupported", "uncertain"}:
        raise ContractError("disposition must be supported, unsupported, or uncertain")
    findings = review.get("findings", [])
    if not isinstance(findings, list) or any(not isinstance(item, str) for item in findings):
        raise ContractError("findings must be a list of strings")
    return {"status": "reviewed", "disposition": disposition, "findings": findings, "evidence_ids": refs, "revision": current_revision, "permission": "not_granted"}


def deterministic_policy(review_result: dict[str, Any], host_authorized: bool) -> dict[str, str]:
    """Consume semantic evidence and independently apply host authorization."""
    if not isinstance(review_result, dict):
        raise ContractError("review_result must be an object")
    if not isinstance(host_authorized, bool):
        raise ContractError("host_authorized must be a boolean from the host policy boundary")
    if review_result.get("status") != "reviewed" or review_result.get("disposition") != "supported":
        return {"decision": "hold", "authorization": "not_granted"}
    if not host_authorized:
        return {"decision": "deny", "authorization": "denied_by_host"}
    return {"decision": "eligible_for_executor", "authorization": "granted_by_host"}


def examples() -> dict[str, Any]:
    """Return three reproducible fixtures with explicit synthetic provenance."""
    provenance = "SYNTHETIC OFFLINE FIXTURE; not inference, calibration, or measured performance"
    candidates = [{"id": "browser", "label": "Browser workflow"}, {"id": "filesystem", "label": "Local file workflow"}]
    selection = {
        "provenance": provenance,
        "cases": {
            "satisfying": select_candidate(candidates, {"outcome": "candidate", "candidate_id": "browser", "p_applicable": 0.91}, 0.70),
            "near_miss_no_match": select_candidate(candidates, {"outcome": "no_match", "candidate_id": None}, 0.70),
            "unavailable": select_candidate(candidates, {"outcome": "unavailable", "candidate_id": None}, 0.70),
        },
        "cutoff_note": "0.70 is only a declared fixture policy value; it is not a recommended or calibrated threshold.",
    }
    allowed = [{"id": "refresh-index"}]
    proposal = {"action_id": "refresh-index", "evidence_revision": "rev-12", "expected_effect": "index_revision=rev-12"}
    action = {
        "provenance": provenance,
        "cases": {
            "satisfying": select_and_check_action(proposal, allowed, {"revision": "rev-12"}, "rev-12", {"effect": "index_revision=rev-12", "outcome": "pass"}),
            "stale_evidence": select_and_check_action({**proposal, "evidence_revision": "rev-11"}, allowed, {"revision": "rev-11"}, "rev-12", {"effect": "index_revision=rev-12", "outcome": "pass"}),
            "no_effect": select_and_check_action(proposal, allowed, {"revision": "rev-12"}, "rev-12", {"effect": None, "outcome": "fail"}),
            "execution_error": select_and_check_action(proposal, allowed, {"revision": "rev-12"}, "rev-12", {"error": "simulated timeout"}),
        },
        "note": "The executor result is injected fixture data; this command performs no action.",
    }
    evidence = {"doc-7": "Approved maintenance window is 02:00-03:00 UTC."}
    review = review_proposal({"revision": "rev-12", "disposition": "supported", "evidence_ids": ["doc-7"], "findings": ["Proposed window is within the approved window."]}, evidence, "rev-12")
    review_example = {
        "provenance": provenance,
        "semantic_review": review,
        "host_policy_allowed": deterministic_policy(review, True),
        "host_policy_denied": deterministic_policy(review, False),
        "note": "Semantic support supplies evidence to policy; only the host policy grants or denies authorization.",
    }
    return {"selection": selection, "action": action, "review": review_example}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("scenario", nargs="?", choices=("selection", "action", "review", "all"), default="all")
    parser.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    args = parser.parse_args(argv)
    output = examples()
    selected = output if args.scenario == "all" else {args.scenario: output[args.scenario]}
    if args.json:
        print(json.dumps(selected, indent=2, sort_keys=True))
    else:
        for name, result in selected.items():
            print(f"[{name}] {result['provenance']}")
            for case, value in result.get("cases", {}).items():
                print(f"  {case}: {json.dumps(value, sort_keys=True)}")
            if name == "review":
                print(f"  semantic_review: {json.dumps(result['semantic_review'], sort_keys=True)}")
                print(f"  host_policy_allowed: {json.dumps(result['host_policy_allowed'], sort_keys=True)}")
                print(f"  host_policy_denied: {json.dumps(result['host_policy_denied'], sort_keys=True)}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ContractError as exc:
        print(f"invalid example contract: {exc}", file=sys.stderr)
        raise SystemExit(2) from exc
