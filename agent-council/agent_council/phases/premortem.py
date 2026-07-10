"""Premortem phase — each agent envisions how the decision already failed."""

import asyncio
from pydantic_ai import Agent
from agent_council.state import CouncilState, Premortem
from agent_council.config import load_config
from agent_council.guardrails import FACTUAL_CLAIM_GUARDRAIL


async def run_premortems(
    question: str,
    state: CouncilState,
    verbose: bool = False,
) -> dict[str, Premortem]:
    """Each agent independently writes a failure scenario.

    Agents do NOT see each other's premortems — this runs before any
    positions are formed, bypassing positional commitment bias.
    Uses real profiles if available, falls back to fabricated personas.
    """
    cfg = load_config()

    async def _premortem(agent_id: str, identity_block: str) -> tuple[str, Premortem]:
        agent = Agent(
            cfg["model"],
            output_type=Premortem,
            retries=3,
            system_prompt=(
                f"{identity_block}\n\n"
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
        return agent_id, result.output

    # Build agent identities
    tasks = []
    if state.profiles:
        for p in state.profiles:
            identity = (
                f"You are {p.name}.\n\n"
                f"Your identity and operating principles:\n"
                f"{p.soul_content}\n\n"
                f"Description: {p.description}"
            )
            tasks.append(_premortem(p.name, identity))
    else:
        for p in state.personas:
            identity = (
                f"You are {p.name}.\n"
                f"Background: {p.background}\n"
                f"Expertise: {p.expertise}\n"
                f"Approach: {p.approach}\n"
                f"Bias: {p.bias}"
            )
            tasks.append(_premortem(p.name, identity))

    results = await asyncio.gather(*tasks)
    return dict(results)
