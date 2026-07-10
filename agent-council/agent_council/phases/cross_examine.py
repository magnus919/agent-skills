"""Cross-examination phase — agents probe each other's positions."""

import asyncio
from pydantic_ai import Agent
from agent_council.state import (
    CouncilState,
    Position,
    CrossExamination,
)
from agent_council.config import load_config
from agent_council.guardrails import FACTUAL_CLAIM_GUARDRAIL


def _format_other_positions(
    my_name: str,
    positions: dict[str, Position],
) -> str:
    """Format other agents' positions for the prompt."""
    lines = []
    for name, pos in positions.items():
        if name == my_name:
            continue
        lines.append(f"--- {name} ---")
        lines.append(f"Stance: {pos.stance}")
        lines.append(f"Reasoning: {'; '.join(pos.reasoning)}")
        lines.append(f"Confidence: {pos.confidence}")
        lines.append(f"Assumptions: {'; '.join(pos.key_assumptions)}")
        lines.append("")
    return "\n".join(lines)


async def run_cross_examination(
    question: str,
    state: CouncilState,
    verbose: bool = False,
) -> dict[str, CrossExamination]:
    """Each agent reads all other positions and responds.

    Uses real profiles if available, falls back to fabricated personas.
    """
    cfg = load_config()

    async def _cross(
        agent_id: str,
        identity_block: str,
        other_positions: str,
        round_context: str,
    ) -> tuple[str, CrossExamination]:
        system = (
            f"{identity_block}\n\n"
            "You are in a structured debate. You have read every other agent's "
            "position on the question.\n\n"
            "Other agents' positions:\n"
            f"{other_positions}\n"
            f"{round_context}\n\n"
            "Respond to what you've read. For each point: concede where the "
            "other agent's reasoning is stronger, identify where you still "
            "disagree and why, and update your position if warranted. Be "
            "specific — do not hedge. If your confidence has changed, say so."
            f"{FACTUAL_CLAIM_GUARDRAIL}"
        )

        agent = Agent(cfg["model"], output_type=CrossExamination, system_prompt=system, retries=3)
        result = await agent.run(question)
        output = result.output
        output.agent_name = agent_id
        return agent_id, output

    # Build list of agent identities
    agents = []
    if state.profiles:
        for p in state.profiles:
            identity = (
                f"You are {p.name}.\n\n"
                f"Your identity and operating principles:\n"
                f"{p.soul_content}\n\n"
                f"Description: {p.description}"
            )
            agents.append((p.name, identity))
    else:
        for p in state.personas:
            identity = (
                f"You are {p.name}.\n"
                f"Background: {p.background}\n"
                f"Expertise: {p.expertise}\n"
                f"Approach: {p.approach}\n"
                f"Bias: {p.bias}"
            )
            agents.append((p.name, identity))

    prior_rounds = state.cross_examination_rounds

    tasks = []
    for agent_id, identity_block in agents:
        other_positions = _format_other_positions(agent_id, state.positions)

        round_context = ""
        if prior_rounds:
            round_context = "\n\nPrevious round context:\n"
            for i, rnd in enumerate(prior_rounds):
                if agent_id in rnd:
                    prev = rnd[agent_id]
                    round_context += f"Round {i + 1} — your reflection: {prev.reflection}\n"
                    if prev.concessions:
                        round_context += f"  You conceded: {'; '.join(prev.concessions)}\n"
                    if prev.remaining_disagreements:
                        round_context += (
                            f"  Still in dispute: "
                            f"{'; '.join(prev.remaining_disagreements)}\n"
                        )

        tasks.append(_cross(agent_id, identity_block, other_positions, round_context))

    results = await asyncio.gather(*tasks)
    return dict(results)
