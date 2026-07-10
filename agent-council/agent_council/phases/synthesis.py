"""Synthesis phase — produces the final decision landscape."""

from pydantic_ai import Agent
from agent_council.state import (
    CouncilState,
    Position,
    Premortem,
    CrossExamination,
    Synthesis,
    RiskVector,
    Disagreement,
    RoundMetrics,
)
from agent_council.convergence import compute_round_metrics
from agent_council.config import load_config


def _collect_risks(
    premortems: dict[str, Premortem],
    positions: dict[str, Position],
    cross_rounds: list[dict[str, CrossExamination]],
) -> list[RiskVector]:
    """Collect all risks flagged across phases."""
    risks: list[RiskVector] = []

    # From premortems (pre-positional)
    for p in premortems.values():
        if p.root_causes:
            risks.append(
                RiskVector(
                    description="; ".join(p.root_causes[:3]),
                    agents_who_flagged=[p.agent_name],
                    severity="medium",
                    phase_discovered="premortem",
                )
            )

    # From cross-examinations (post-positional)
    for rnd in cross_rounds:
        for ce in rnd.values():
            if ce.remaining_disagreements:
                for d in ce.remaining_disagreements[:2]:
                    risks.append(
                        RiskVector(
                            description=d,
                            agents_who_flagged=[ce.agent_name],
                            severity="medium",
                            phase_discovered="cross_examine",
                        )
                    )

    return risks


async def synthesize(state: CouncilState) -> Synthesis:
    """Produce the final synthesis from all phase outputs.

    Combines algorithmic convergence metrics with an LLM-generated
    narrative synthesis of the decision landscape.
    """
    cfg = load_config()

    # Collect all risks
    risks = _collect_risks(
        state.premortems, state.positions, state.cross_examination_rounds
    )

    # Build convergence history
    history: list[RoundMetrics] = []
    for i in range(len(state.cross_examination_rounds)):
        # Temporarily set round_number to replay metrics
        state.round_number = i + 1
        metrics = compute_round_metrics(state)
        history.append(metrics)

    # Compute final metrics
    final_metrics = history[-1] if history else None
    first_metrics = history[0] if len(history) > 1 else final_metrics

    # Identify shared concerns from cross-examination
    shared_concerns = _extract_shared_concerns(state.cross_examination_rounds)

    # Identify disagreements
    disagreements = _extract_disagreements(state)

    # Build assumptions per position
    assumptions_per_position = {
        name: pos.key_assumptions for name, pos in state.positions.items()
    }

    # Generate narrative synthesis via LLM
    narrative = await _generate_synthesis_narrative(state, cfg)

    stopped_reason = state.synthesis.stopped_reason if state.synthesis else "max_rounds"

    return Synthesis(
        question=state.question,
        mode=state.mode,
        num_agents=len(state.personas),
        rounds_completed=len(state.cross_examination_rounds),
        stopped_reason=stopped_reason,  # type: ignore
        confidence_history=history,
        final_dispersion=final_metrics.dispersion if final_metrics else 0.0,
        mean_confidence_delta=(
            (final_metrics.mean_confidence - first_metrics.mean_confidence)
            if final_metrics and first_metrics
            else 0.0
        ),
        shared_risks=[r for r in risks if r.phase_discovered == "premortem"],
        shared_concerns=shared_concerns,
        disagreements=disagreements,
        assumptions_per_position=assumptions_per_position,
        risk_vectors=risks,
        principal_path=narrative,
    )


def _extract_shared_concerns(
    cross_rounds: list[dict[str, CrossExamination]],
) -> list[str]:
    """Find concerns raised by multiple agents across rounds."""
    concern_counts: dict[str, int] = {}
    for rnd in cross_rounds:
        for ce in rnd.values():
            for d in ce.remaining_disagreements:
                concern_counts[d] = concern_counts.get(d, 0) + 1
            for c in ce.concessions:
                concern_counts[c] = concern_counts.get(c, 0) + 1

    # Return concerns raised by more than one agent
    return [
        concern
        for concern, count in sorted(
            concern_counts.items(), key=lambda x: -x[1]
        )
        if count > 1
    ][:10]


def _extract_disagreements(state: CouncilState) -> list[Disagreement]:
    """Identify persistent disagreements from the last round."""
    if not state.cross_examination_rounds:
        return []

    last_round = state.cross_examination_rounds[-1]
    topic_positions: dict[str, dict[str, str]] = {}

    for ce in last_round.values():
        for d in ce.remaining_disagreements:
            if d not in topic_positions:
                topic_positions[d] = {}
            topic_positions[d][ce.agent_name] = ce.updated_position or "maintains position"

    return [
        Disagreement(topic=topic, positions=positions)
        for topic, positions in topic_positions.items()
    ][:8]


async def _generate_synthesis_narrative(
    state: CouncilState, cfg: dict
) -> str:
    """Generate a narrative principal's path via LLM."""
    # Build a summary of the debate for the LLM
    summary_parts = [f"# Debate: {state.question}\n"]
    summary_parts.append(f"Agents: {', '.join(p.name for p in state.personas)}\n")

    summary_parts.append("\n## Positions\n")
    for pos in state.positions.values():
        summary_parts.append(
            f"- **{pos.agent_name}** (confidence {pos.confidence}): {pos.stance}\n"
        )

    summary_parts.append("\n## Premortem Failure Scenarios\n")
    for pm in state.premortems.values():
        summary_parts.append(f"- **{pm.agent_name}**: {pm.failure_scenario[:200]}\n")

    summary_parts.append("\n## Cross-Examination Rounds\n")
    for i, rnd in enumerate(state.cross_examination_rounds):
        summary_parts.append(f"\n### Round {i + 1}\n")
        for ce in rnd.values():
            summary_parts.append(f"- **{ce.agent_name}**: {ce.reflection[:200]}\n")

    debate_summary = "".join(summary_parts)

    agent = Agent(
        cfg["model"],
        system_prompt=(
            "You are a senior decision analyst. You have overseen a structured "
            "multi-agent debate on an important question. Your job: synthesize "
            "the debate into a clear 'principal's path' — a narrative that "
            "presents the decision landscape to someone who must make a call.\n\n"
            "Do NOT describe the debate process (rounds, phases, agents). "
            "Write as a single analyst presenting their findings. Structure: "
            "what's at stake, where the evidence is strongest, where it's weakest, "
            "what assumptions each path depends on, and your recommended path "
            "forward with associated risks.\n\n"
            "Keep it under 500 words. Be direct. No hedging."
        ),
    )
    result = await agent.run(debate_summary)
    return result.output or ""
