"""Position phase — each agent forms an independent initial position."""

import asyncio
from pydantic_ai import Agent
from agent_council.state import AgentPersona, Position, Premortem
from agent_council.config import load_config
from agent_council.guardrails import FACTUAL_CLAIM_GUARDRAIL


async def run_positions(
    question: str,
    personas: list[AgentPersona],
    premortems: dict[str, Premortem],
) -> dict[str, Position]:
    """Each agent forms an independent initial position.

    Agents see their own premortem (to maintain continuity) but NOT other
    agents' positions or premortems. This ensures independent thought.
    """
    cfg = load_config()

    async def _position(persona: AgentPersona) -> tuple[str, Position]:
        my_premortem = premortems.get(persona.name)

        system = (
            f"You are {persona.name}.\n"
            f"Background: {persona.background}\n"
            f"Expertise: {persona.expertise}\n"
            f"Approach: {persona.approach}\n"
            f"Bias: {persona.bias}\n\n"
            "You are in a structured debate. Your task: form your initial "
            "position on the question. Be specific about your stance, your "
            "reasoning, and what assumptions you're making.\n"
            f"Your pre-mortem identified these failure modes:"
        )
        if my_premortem:
            system += (
                f"\n  - Failure scenario: {my_premortem.failure_scenario}\n"
                f"  - Root causes: {'; '.join(my_premortem.root_causes)}\n"
                f"  - Warning signals: {'; '.join(my_premortem.early_warning_signals)}\n\n"
                "Your position should account for these risks."
            )
        else:
            system += "\n  (none recorded)\n"

        system += (
            "\n\nReturn your position with a confidence score (0-1) and "
            "the key assumptions that must hold for your position to be correct."
            f"{FACTUAL_CLAIM_GUARDRAIL}"
        )

        agent = Agent(cfg["model"], output_type=Position, system_prompt=system)
        result = await agent.run(question)
        output = result.output
        output.agent_name = persona.name
        return persona.name, output

    tasks = [_position(p) for p in personas]
    results = await asyncio.gather(*tasks)
    return dict(results)
