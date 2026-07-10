"""Synthesis phase — produces the final decision landscape."""

from typing import Literal

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
from agent_council.guardrails import verify_synthesis


def _collect_risks(
    premortems: dict[str, Premortem],
    positions: dict[str, Position],
    cross_rounds: list[dict[str, CrossExamination]],
) -> list[RiskVector]:
    """Collect all risks flagged across phases."""
    risks: list[RiskVector] = []

    # Heuristic severity: if 3+ agents flagged it independently, it's high.
    # Risks seen by 2 agents are medium, single-agent risks are low.
    def _severity(agent_count: int) -> Literal["low", "medium", "high"]:
        if agent_count >= 3:
            return "high"
        elif agent_count == 2:
            return "medium"
        return "low"

    # Track which risks were flagged by how many agents (dedup by description prefix)
    risk_counts: dict[str, set[str]] = {}

    def _record(description: str, agent: str, phase: str):
        key = description[:60]  # group similar descriptions
        if key not in risk_counts:
            risk_counts[key] = set()
        risk_counts[key].add(agent)

    # From premortems (pre-positional)
    for p in premortems.values():
        if p.root_causes:
            cause = "; ".join(p.root_causes[:3])
            _record(cause, p.agent_name, "premortem")

    # From cross-examinations (post-positional)
    for rnd in cross_rounds:
        for ce in rnd.values():
            if ce.remaining_disagreements:
                for d in ce.remaining_disagreements[:2]:
                    _record(d, ce.agent_name, "cross_examine")

    # Build final risk list with computed severity
    premortem_agents = {p.agent_name for p in premortems.values()}
    for key, agents in risk_counts.items():
        # Determine phase: if any premortem agent flagged it, origin is premortem
        phase = "premortem" if any(a in premortem_agents for a in agents) else "cross_examine"
        risks.append(
            RiskVector(
                description=key,
                agents_who_flagged=list(agents),
                severity=_severity(len(agents)),
                phase_discovered=phase,
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

    # Post-synthesis verification: scan for unsubstantiated factual claims
    verification = await verify_synthesis(narrative)
    verification_note = ""
    if verification.has_issues:
        items = "\n".join(
            f"  • \"{c.quote[:120]}\" — {c.claim_type}: {c.explanation[:150]}"
            for c in verification.claims[:5]
        )
        verification_note = (
            f"\n\n---\n"
            f"⚠️  Claims Not Verified\n"
            f"The following assertions in this synthesis could not be verified "
            f"by the council's own reasoning and should be checked before acting:\n"
            f"{items}\n"
        )
        if len(verification.claims) > 5:
            verification_note += (
                f"  ...and {len(verification.claims) - 5} more unsubstantiated "
                f"claim(s)."
            )
    narrative += verification_note

    stopped_reason = "max_rounds"  # will be overwritten by graph.py

    return Synthesis(
        question=state.question,
        mode=state.mode,
        num_agents=len(state.profiles) or len(state.personas),
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
        retries=3,
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
