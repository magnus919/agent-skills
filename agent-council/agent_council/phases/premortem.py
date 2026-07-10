"""Premortem phase — each agent envisions how the decision already failed."""

import asyncio
from pydantic_ai import Agent
from agent_council.state import AgentPersona, Premortem
from agent_council.config import load_config
from agent_council.guardrails import FACTUAL_CLAIM_GUARDRAIL


async def run_premortems(
    question: str,
    personas: list[AgentPersona],
) -> dict[str, Premortem]:
    """Each agent independently writes a failure scenario.

    Agents do NOT see each other's premortems — this runs before any
    positions are formed, bypassing positional commitment bias.
    """
    cfg = load_config()

    async def _premortem(persona: AgentPersona) -> tuple[str, Premortem]:
        agent = Agent(
            cfg["model"],
            output_type=Premortem,
            system_prompt=(
                f"You are {persona.name}.\n"
                f"Background: {persona.background}\n"
                f"Expertise: {persona.expertise}\n"
                f"Approach: {persona.approach}\n"
                f"Bias: {persona.bias}\n\n"
                "You are in a structured debate. Your first task: write a "
                "pre-mortem — imagine it is 6 months in the future and the "
                "decision about to be discussed has ALREADY FAILED. Write "
                "the history of how it failed. What went wrong? What were the "
                "early warning signals nobody heeded? Be specific and draw on "
                "your expertise."
                f"{FACTUAL_CLAIM_GUARDRAIL}"
            ),
        )
        result = await agent.run(question)
        return persona.name, result.output

    tasks = [_premortem(p) for p in personas]
    results = await asyncio.gather(*tasks)
    return dict(results)
