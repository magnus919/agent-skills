"""Independent deterministic oracles for structured pilot evidence.

These functions assess typed traces or facts, not natural-language answers.
Their passing fixtures validate oracle mechanics, not skill behavior.
"""

from __future__ import annotations

from datetime import date
from typing import Any


def business_transition_oracle(trace: dict[str, Any]) -> dict[str, bool]:
    """Check approval, permission, timeout, and partial-success invariants."""
    return {
        "editable_before_approval": trace.get("editable_proposal") is True,
        "approval_matches_current_draft": trace.get("approved_revision") is not None
        and trace.get("draft_revision_at_execution") is not None
        and trace.get("approved_revision") == trace.get("draft_revision_at_execution"),
        "revocation_blocks_execution": trace.get("permission_at_execution") is not False
        or trace.get("execution_authorized") is False,
        "timeout_status_checked": trace.get("command_timed_out") is not True
        or trace.get("command_status_queried") is True,
        "reservation_and_notification_separate": trace.get("reservation_status") == "confirmed"
        and trace.get("notification_status") == "failed",
        "no_blind_reservation_retry": trace.get("blind_reservation_retry") is not True,
        "usability_claim_limited": trace.get("usability_evidence")
        in {"observed_study", "synthetic_fixture_only", "not_claimed"},
    }


def proposal_authority_oracle(
    proposal: dict[str, Any],
    *,
    allowed_item_ids: set[str],
    current_record_revision: str,
    permission_current: bool,
    app_approval_identity: str | None,
    app_approved_revision: str | None,
    execution_authorized: bool,
) -> dict[str, bool]:
    """Check that a typed proposal stays separate from application authority."""
    allowed_fields = {"item_id", "quantity", "record_revision", "rationale"}
    forbidden_fields = {"command", "execute", "approval_identity", "approved_by", "permission"}
    proposal_revision = proposal.get("record_revision")
    proposal_is_in_scope = (
        isinstance(proposal.get("item_id"), str) and proposal.get("item_id") in allowed_item_ids
    )
    app_authorizes = (
        permission_current is True
        and bool(app_approval_identity)
        and app_approved_revision == current_record_revision
        and proposal_revision == current_record_revision
        and proposal_is_in_scope
    )
    return {
        "typed_proposal_shape": set(proposal).issubset(allowed_fields)
        and {"item_id", "quantity", "record_revision"}.issubset(proposal),
        "candidate_within_application_scope": proposal_is_in_scope,
        "model_output_contains_no_authority": not (set(proposal) & forbidden_fields),
        "stale_revision_blocks_execution": proposal_revision == current_record_revision
        or execution_authorized is False,
        "permission_rechecked_by_application": permission_current is True
        or execution_authorized is False,
        "execution_authority_matches_application_state": execution_authorized is app_authorizes,
        "approval_identity_owned_by_application": bool(app_approval_identity),
    }


DEFAULT_POLICY_VERSIONS = (
    {"version": "v1", "starts": "2026-01-01", "ends": "2026-07-01", "max_days": 7},
    {"version": "v2", "starts": "2026-07-01", "ends": None, "max_days": 5},
)


def policy_translation_oracle(
    *,
    effective_date: str | None,
    requested_days: int | None,
    item_available: bool | None,
    exception_requested: bool,
    versions: tuple[dict[str, Any], ...] = DEFAULT_POLICY_VERSIONS,
) -> str:
    """Evaluate the independently transcribed fictional policy clauses.

    ``versions`` is trusted injected test data for selection cases such as gaps and
    overlaps. This helper does not validate version identity or publication provenance.
    """
    if (
        not isinstance(effective_date, str)
        or type(requested_days) is not int
        or requested_days <= 0
        or type(item_available) is not bool
        or type(exception_requested) is not bool
    ):
        return "review"
    try:
        current = date.fromisoformat(effective_date)
        matches = [
            row
            for row in versions
            if (date.min if row["starts"] is None else date.fromisoformat(row["starts"])) <= current
            and (row["ends"] is None or current < date.fromisoformat(row["ends"]))
        ]
    except (KeyError, TypeError, ValueError):
        return "review"
    if len(matches) != 1:
        return "review"
    maximum = matches[0].get("max_days")
    if type(maximum) is not int or maximum <= 0:
        return "review"
    if item_available is False:
        return "deny"
    if exception_requested is True:
        return "review"
    if requested_days <= maximum:
        return "allow"
    return "deny"


STAKEHOLDER_CATEGORIES = {
    "decision_maker",
    "end_user",
    "operator_support",
    "downstream_consumer",
    "adjacent_system_owner",
}


def stakeholder_map_oracle(stakeholders: list[dict[str, Any]]) -> dict[str, bool]:
    """Check coverage and evidence fields in a structured stakeholder map."""
    categories = {
        item.get("category")
        for item in stakeholders
        if isinstance(item, dict) and isinstance(item.get("category"), str)
    }
    complete_records = all(
        all(
            isinstance(item.get(field), str) and item[field].strip()
            for field in ("role", "needs", "constraints", "conflicts", "inclusion_reason")
        )
        for item in stakeholders
        if isinstance(item, dict)
    )
    return {
        "all_required_categories_present": STAKEHOLDER_CATEGORIES.issubset(categories),
        "every_record_explains_needs_constraints_and_conflicts": complete_records
        and bool(stakeholders)
        and all(isinstance(item, dict) for item in stakeholders),
    }


def judge_qualification_oracle(
    *,
    accuracy: float,
    mean_max_probability: float,
    error_detection_auroc: float,
    acceptance_threshold: float | None,
    independent_labels: bool,
    risk_coverage_evaluated: bool,
    unsupported_cases_route_to_review: bool,
    repeated_vote_separately_evaluated: bool,
    correlated_errors_evaluated: bool,
    full_cost_evaluated: bool,
) -> dict[str, bool]:
    """Check the stated judge-qualification evidence and required boundaries."""
    weak_discrimination = error_detection_auroc < 0.60
    return {
        "weak_discrimination_recognized": weak_discrimination and accuracy < 0.60,
        "high_mean_confidence_not_used_as_gate": acceptance_threshold is None,
        "independent_labels_available": independent_labels,
        "risk_coverage_measured": risk_coverage_evaluated,
        "unsupported_cases_reviewed": unsupported_cases_route_to_review,
        "repeat_vote_separately_qualified": repeated_vote_separately_evaluated
        and correlated_errors_evaluated
        and full_cost_evaluated,
    }
