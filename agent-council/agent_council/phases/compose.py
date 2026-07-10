"""Compose phase — generates agent personas from the question."""

from pydantic_ai import Agent
from agent_council.state import AgentPersona
from agent_council.config import load_config


async def compose_personas(question: str, num_agents: int = 5) -> list[AgentPersona]:
    """Generate debate agent personas tailored to the question.

    Uses an LLM to compose personas with diverse backgrounds, analytical
    approaches, and biases. The compose agent is a single LLM call that
    outputs a structured list of AgentPersona definitions.
    """
    cfg = load_config()

    compose_agent = Agent(
        cfg["model"],
        output_type=list[AgentPersona],
        system_prompt=(
            "You are a council composition specialist. Your job is to design "
            "expert debating agents for a structured multi-perspective debate.\n\n"
            "Critical directive: Prioritize DIVERSITY OF INITIAL POSITION over "
            "diversity of expertise. Research shows that a group with four distinct "
            "approaches to a problem — none individually correct — outperforms a "
            "group with more expertise but shared framing.\n\n"
            "For each agent provide: name, one-paragraph career background, specific "
            "expertise, analytical approach, and what bias or experience they bring "
            f"to THIS question. Design exactly {num_agents} agents.\n\n"
            "At least one agent should be structurally skeptical (a light red-team "
            "role). At least one agent should approach the problem from a fundamentally "
            "different cognitive frame than the others. Design them to create productive "
            "friction — real disagreement grounded in real experience, not caricatures."
        ),
    )

    result = await compose_agent.run(
        f"Design {num_agents} expert debating agents for the question: {question}"
    )

    return result.output
