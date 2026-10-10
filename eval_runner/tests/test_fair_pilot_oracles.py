"""Deterministic positive controls and mutations for pilot oracle rules."""

from eval_runner.fair_pilot_oracles import (
    business_transition_oracle,
    judge_qualification_oracle,
    policy_translation_oracle,
    proposal_authority_oracle,
    stakeholder_map_oracle,
)


def test_business_transition_oracle_catches_stale_approval_and_partial_failure():
    trace = {
        "editable_proposal": True,
        "approved_revision": 4,
        "draft_revision_at_execution": 4,
        "permission_at_execution": False,
        "execution_authorized": False,
        "command_timed_out": True,
        "command_status_queried": True,
        "reservation_status": "confirmed",
        "notification_status": "failed",
        "blind_reservation_retry": False,
        "usability_evidence": "synthetic_fixture_only",
    }
    assert all(business_transition_oracle(trace).values())
    trace["approved_revision"] = 3
    trace["blind_reservation_retry"] = True
    trace["notification_status"] = "unknown"
    checks = business_transition_oracle(trace)
    assert checks["approval_matches_current_draft"] is False
    assert checks["no_blind_reservation_retry"] is False
    assert checks["reservation_and_notification_separate"] is False


def test_proposal_oracle_keeps_application_authority_outside_model_data():
    proposal = {"item_id": "camera-1", "quantity": 1, "record_revision": "r12"}
    kwargs = {
        "allowed_item_ids": {"camera-1"},
        "current_record_revision": "r13",
        "permission_current": False,
        "app_approval_identity": "user-7",
        "app_approved_revision": "r12",
        "execution_authorized": False,
    }
    checks = proposal_authority_oracle(proposal, **kwargs)
    assert all(checks.values())
    mutated = {**proposal, "approval_identity": "model-claimed-user"}
    checks = proposal_authority_oracle(mutated, **kwargs)
    assert checks["model_output_contains_no_authority"] is False
    bad_authority = {**kwargs, "execution_authorized": True}
    assert (
        proposal_authority_oracle(proposal, **bad_authority)[
            "execution_authority_matches_application_state"
        ]
        is False
    )
    out_of_scope = {**proposal, "item_id": "other-tenant-item"}
    assert (
        proposal_authority_oracle(out_of_scope, **kwargs)["candidate_within_application_scope"]
        is False
    )


def test_policy_oracle_covers_boundaries_precedence_and_ambiguous_dates():
    decide = policy_translation_oracle
    assert (
        decide(
            effective_date="2026-06-30",
            requested_days=7,
            item_available=True,
            exception_requested=False,
        )
        == "allow"
    )
    assert (
        decide(
            effective_date="2026-06-30",
            requested_days=8,
            item_available=True,
            exception_requested=False,
        )
        == "deny"
    )
    assert (
        decide(
            effective_date="2026-07-01",
            requested_days=5,
            item_available=True,
            exception_requested=False,
        )
        == "allow"
    )
    assert (
        decide(
            effective_date="2026-07-01",
            requested_days=6,
            item_available=True,
            exception_requested=False,
        )
        == "deny"
    )
    assert (
        decide(
            effective_date="2026-07-01",
            requested_days=6,
            item_available=True,
            exception_requested=True,
        )
        == "review"
    )
    assert (
        decide(
            effective_date="2026-07-01",
            requested_days=6,
            item_available=False,
            exception_requested=True,
        )
        == "deny"
    )
    assert (
        decide(
            effective_date=None, requested_days=2, item_available=True, exception_requested=False
        )
        == "review"
    )
    overlap = (
        {"version": "v1", "starts": "2026-01-01", "ends": "2026-08-01", "max_days": 7},
        {"version": "v2", "starts": "2026-07-01", "ends": None, "max_days": 5},
    )
    assert (
        decide(
            effective_date="2026-07-15",
            requested_days=2,
            item_available=True,
            exception_requested=False,
            versions=overlap,
        )
        == "review"
    )
    gap = (
        {"version": "v1", "starts": None, "ends": "2026-06-01", "max_days": 7},
        {"version": "v2", "starts": "2026-07-01", "ends": None, "max_days": 5},
    )
    assert (
        decide(
            effective_date="2026-06-15",
            requested_days=2,
            item_available=True,
            exception_requested=False,
            versions=gap,
        )
        == "review"
    )


def test_stakeholder_oracle_checks_all_categories_and_map_fields():
    categories = (
        "decision_maker",
        "end_user",
        "operator_support",
        "downstream_consumer",
        "adjacent_system_owner",
    )
    stakeholders = [
        {
            "category": category,
            "role": category,
            "needs": "reliable billing",
            "constraints": "existing system boundary",
            "conflicts": "timing versus accuracy",
            "inclusion_reason": "could block adoption",
        }
        for category in categories
    ]
    assert all(stakeholder_map_oracle(stakeholders).values())
    missing_category = stakeholders[:-1]
    assert stakeholder_map_oracle(missing_category)["all_required_categories_present"] is False
    missing_evidence = [*stakeholders[:-1], {**stakeholders[-1], "conflicts": ""}]
    assert (
        stakeholder_map_oracle(missing_evidence)[
            "every_record_explains_needs_constraints_and_conflicts"
        ]
        is False
    )


def test_judge_qualification_oracle_rejects_confidence_gate_and_unqualified_voting():
    evidence = {
        "accuracy": 0.525,
        "mean_max_probability": 0.90,
        "error_detection_auroc": 0.518,
        "acceptance_threshold": None,
        "independent_labels": True,
        "risk_coverage_evaluated": True,
        "unsupported_cases_route_to_review": True,
        "repeated_vote_separately_evaluated": True,
        "correlated_errors_evaluated": True,
        "full_cost_evaluated": True,
    }
    assert all(judge_qualification_oracle(**evidence).values())
    confidence_gate = {**evidence, "acceptance_threshold": 0.9}
    assert (
        judge_qualification_oracle(**confidence_gate)["high_mean_confidence_not_used_as_gate"]
        is False
    )
    unqualified_vote = {**evidence, "correlated_errors_evaluated": False}
    assert (
        judge_qualification_oracle(**unqualified_vote)["repeat_vote_separately_qualified"] is False
    )
