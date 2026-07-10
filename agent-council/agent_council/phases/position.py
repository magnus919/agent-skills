"""Position phase — each agent forms an independent initial position."""

import asyncio
from pydantic_ai import Agent
from agent_council.state import CouncilState, Position, Premortem
from agent_council.config import load_config
from agent_council.guardrails import FACTUAL_CLAIM_GUARDRAIL


async def run_positions(
    question: str,
    state: CouncilState,
    verbose: bool = False,
) -> dict[str, Position]:
    """Each agent forms an independent initial position.

    Agents see their own premortem (to maintain continuity) but NOT other
    agents' positions or premortems. Ensures independent thought.
    Uses real profiles if available, falls back to fabricated personas.
    """
    cfg = load_config()

    async def _position(
        agent_id: str,
        identity_block: str,
        premortem: Premortem | None,
    ) -> tuple[str, Position]:
        system = (
            f"{identity_block}\n\n"
            "You are in a structured debate. Your task: form your initial "
            "position on the question. Be specific about your stance, your "
            "reasoning, and what assumptions you're making."
        )
        if premortem:
            system += (
                f"\n\nYour pre-mortem identified these failure modes:\n"
                f"  - Failure scenario: {premortem.failure_scenario}\n"
                f"  - Root causes: {'; '.join(premortem.root_causes)}\n"
                f"  - Warning signals: {'; '.join(premortem.early_warning_signals)}\n\n"
                "Your position should account for these risks."
            )

        system += (
            "\n\nReturn your position with a confidence score (0-1) and "
            "the key assumptions that must hold for your position to be correct."
            f"{FACTUAL_CLAIM_GUARDRAIL}"
        )

        agent = Agent(cfg["model"], output_type=Position, system_prompt=system)
        result = await agent.run(question)
        output = result.output
        output.agent_name = agent_id
        return agent_id, output

    tasks = []
    if state.profiles:
        for p in state.profiles:
            identity = (
                f"You are {p.name}.\n\n"
                f"Your identity and operating principles:\n"
                f"{p.soul_content}\n\n"
                f"Description: {p.description}"
            )
            pm = state.premortems.get(p.name)
            tasks.append(_position(p.name, identity, pm))
    else:
        for p in state.personas:
            identity = (
                f"You are {p.name}.\n"
                f"Background: {p.background}\n"
                f"Expertise: {p.expertise}\n"
                f"Approach: {p.approach}\n"
                f"Bias: {p.bias}"
            )
            pm = state.premortems.get(p.name)
            tasks.append(_position(p.name, identity, pm))

    results = await asyncio.gather(*tasks)
    return dict(results)
