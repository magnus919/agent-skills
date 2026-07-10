"""Convergence detection — evaluates debate state to decide when to stop."""

import math
from agent_council.state import CouncilState, RoundMetrics


def compute_round_metrics(state: CouncilState) -> RoundMetrics:
    """Compute convergence metrics from the current round's data."""
    if not state.cross_examination_rounds:
        return RoundMetrics(
            round=state.round_number,
            mean_confidence=0.0,
            dispersion=0.0,
            new_arguments=0,
            concessions_made=0,
        )

    current_round = state.cross_examination_rounds[-1]
    confidences = []
    concessions = 0
    total_arguments_before = set()

    # Count arguments from all prior rounds for novelty detection
    for r in state.cross_examination_rounds[:-1]:
        for ce in r.values():
            if ce.remaining_disagreements:
                total_arguments_before.update(ce.remaining_disagreements)
            if ce.new_evidence_needed:
                total_arguments_before.update(ce.new_evidence_needed)

    new_arguments = 0
    for ce in current_round.values():
        if ce.updated_confidence is not None:
            confidences.append(ce.updated_confidence)
        if ce.concessions:
            concessions += len(ce.concessions)
        if ce.remaining_disagreements:
            for arg in ce.remaining_disagreements:
                if arg not in total_arguments_before:
                    new_arguments += 1

    mean_conf = sum(confidences) / len(confidences) if confidences else 0.0
    dispersion = (
        math.sqrt(sum((c - mean_conf) ** 2 for c in confidences) / len(confidences))
        if confidences
        else 0.0
    )

    return RoundMetrics(
        round=state.round_number,
        mean_confidence=round(mean_conf, 3),
        dispersion=round(dispersion, 3),
        new_arguments=new_arguments,
        concessions_made=concessions,
    )


def should_stop(state: CouncilState, metrics: RoundMetrics) -> str:
    """Evaluate whether the debate should stop.

    Returns one of:
      - "converged" — dispersion below threshold, confidence stable
      - "diminishing_returns" — nothing new is surfacing
      - "genuine_disagreement" — dispersion widened, positions hardened
      - "continue" — run another round
    """
    # Hard cap
    if state.round_number >= state.max_rounds:
        return "max_rounds"

    # Need at least 2 rounds to compare
    if len(state.cross_examination_rounds) < 2:
        return "continue"

    prior = state.cross_examination_rounds[-2]
    prior_confs = [
        ce.updated_confidence
        for ce in prior.values()
        if ce.updated_confidence is not None
    ]
    current_confs = [
        ce.updated_confidence
        for ce in state.cross_examination_rounds[-1].values()
        if ce.updated_confidence is not None
    ]

    if not prior_confs or not current_confs:
        return "continue"

    prior_mean = sum(prior_confs) / len(prior_confs)
    current_mean = sum(current_confs) / len(current_confs)

    # Converged: dispersion below threshold
    if metrics.dispersion < state.convergence_threshold:
        # Still check if anything changed — settled means done
        if abs(current_mean - prior_mean) < 0.03:
            return "converged"
        return "continue"

    # Diminishing returns: no new arguments, no concessions
    if metrics.new_arguments == 0 and metrics.concessions_made == 0:
        return "diminishing_returns"

    # Genuine disagreement: dispersion widened and no one moved
    if (
        metrics.dispersion > state.convergence_threshold * 1.5
        and metrics.concessions_made == 0
        and metrics.new_arguments == 0
    ):
        return "genuine_disagreement"

    return "continue"
