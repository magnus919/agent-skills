"""Cross-examination phase — agents probe each other's positions."""

import asyncio
from pydantic_ai import Agent
from agent_council.state import (
    AgentPersona,
    Position,
    CrossExamination,
)
from agent_council.config import load_config


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
    personas: list[AgentPersona],
    positions: dict[str, Position],
    prior_rounds: list[dict[str, CrossExamination]] | None = None,
) -> dict[str, CrossExamination]:
    """Each agent reads all other positions and responds.

    This is the core convergence mechanism — agents confront alternative
    perspectives and either shift, dig in, or identify new evidence needs.
    """
    cfg = load_config()

    async def _cross(persona: AgentPersona) -> tuple[str, CrossExamination]:
        other_positions = _format_other_positions(persona.name, positions)
        round_context = ""
        if prior_rounds:
            round_context = "\n\nPrevious round context:\n"
            for i, rnd in enumerate(prior_rounds):
                if persona.name in rnd:
                    prev = rnd[persona.name]
                    round_context += f"Round {i + 1} — your reflection: {prev.reflection}\n"
                    if prev.concessions:
                        round_context += (
                            f"  You conceded: {'; '.join(prev.concessions)}\n"
                        )
                    if prev.remaining_disagreements:
                        round_context += (
                            f"  Still in dispute: "
                            f"{'; '.join(prev.remaining_disagreements)}\n"
                        )

        system = (
            f"You are {persona.name}.\n"
            f"Background: {persona.background}\n"
            f"Expertise: {persona.expertise}\n"
            f"Approach: {persona.approach}\n"
            f"Bias: {persona.bias}\n\n"
            "You are in a structured debate. You have read every other agent's "
            "position on the question.\n\n"
            "Other agents' positions:\n"
            f"{other_positions}\n"
            f"{round_context}\n\n"
            "Respond to what you've read. For each point: concede where the "
            "other agent's reasoning is stronger, identify where you still "
            "disagree and why, and update your position if warranted. Be "
            "specific — do not hedge. If your confidence has changed, say so."
        )

        agent = Agent(cfg["model"], output_type=CrossExamination, system_prompt=system)
        result = await agent.run(question)
        output = result.output
        output.agent_name = persona.name
        return persona.name, output

    tasks = [_cross(p) for p in personas]
    results = await asyncio.gather(*tasks)
    return dict(results)
