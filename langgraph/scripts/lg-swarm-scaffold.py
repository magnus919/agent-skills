#!/usr/bin/env python3
"""
LangGraph Swarm Pattern Scaffold Generator.

Generates a complete swarm-based multi-agent project with:
- State definitions with handoff tracking
- Handoff tool factory (Command-based)
- Triage agent for initial routing
- Specialist agents with domain tools + handoff tools
- Conditional routing with recursion guard
- Node wrappers for each agent

Usage:
    python lg-swarm-scaffold.py --name support --agents billing,tech,account
    python lg-swarm-scaffold.py --name triage --agents search,summarize --triage-only
"""

import argparse
import os
from typing import List


def snake_case(name: str) -> str:
    return name.replace("-", "_").replace(" ", "_").lower()


def pascal_case(name: str) -> str:
    return "".join(word.capitalize() for word in name.replace("-", " ").replace("_", " ").split())


SWARM_HANDOFF_TOOLS = """\
from langgraph.types import Command
from langchain_core.tools import tool


def make_handoff_tool(target_agent: str, description: str):
    \"\"\"Factory that creates a handoff tool for transferring to another agent.

    The tool returns a Command that tells LangGraph to navigate to a different
    node in the parent graph, updating current_agent and the handoff counter.
    \"\"\"

    @tool(f"transfer_to_{target_agent}")
    def handoff(reason: str) -> Command:
        \"\"\"Transfer the conversation to another specialist agent.\"\"\"
        return Command(
            goto=target_agent,
            update={"current_agent": target_agent},
            graph=Command.PARENT,
        )

    handoff.__doc__ = description
    return handoff
"""


def generate_swarm_project(project_name: str, agents: List[str], output_dir: str, triage_only: bool = False):
    pname = snake_case(project_name)
    state_class = pascal_case(project_name) + "State"
    dir_path = os.path.join(output_dir, pname)
    os.makedirs(dir_path, exist_ok=True)

    agent_names = [snake_case(a) for a in agents]
    agent_labels = [a.replace("-", " ").title() for a in agents]

    # state.py
    state_code = f'''\
\"\"\"State definitions for {project_name} swarm multi-agent system.\"\"\"
from typing import Annotated, TypedDict
from langgraph.graph import MessagesState
import operator


class {state_class}(MessagesState):
    """Shared state across all agents in the {project_name} swarm."""

    current_agent: str = ""
    """Which specialist agent is currently active. Empty = triage phase."""

    resolution_notes: Annotated[list[str], operator.add]
    """Audit trail of what each agent resolved."""

    handoff_count: int = 0
    """Recursion guard — incremented on each handoff. Hard limit at 3."""
'''

    # handoff_tools.py
    handoff_tool_defs = ""
    handoff_tool_imports = "\n".join(
        f'transfer_to_{name} = make_handoff_tool(\n'
        f'    "{name}",\n'
        f'    "Transfer to the {label.lower()} specialist for {label.lower()} issues.",\n'
        f')'
        for name, label in zip(agent_names, agent_labels)
    )
    handoff_code = SWARM_HANDOFF_TOOLS + "\n\n" + handoff_tool_imports

    # agents.py
    if triage_only:
        agent_code = f'''\
\"\"\"Agent definitions for {project_name} swarm.

Triage-only mode: the triage agent routes to specialists who handle the request.
Specialists may or may not have handoff tools depending on the use case.
\"\"\"
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from .handoff_tools import (
    {", ".join(f"transfer_to_{n}" for n in agent_names)}
)

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# Triage agent — only routes, never answers
triage_agent = create_agent(
    llm,
    tools=[{", ".join(f"transfer_to_{n}" for n in agent_names)}],
    system_prompt=(
        "You are a triage agent. Analyze the request and transfer "
        "to the appropriate specialist using the transfer tools. "
        "Do NOT try to answer questions yourself — always transfer."
    ),
)
'''
    else:
        # Full swarm: each specialist gets handoff tools for all OTHER agents
        agent_handoff_imports = "\n".join(
            f'from .handoff_tools import transfer_to_{n}'
            for n in agent_names
        )
        agent_code = f'''\
\"\"\"Agent definitions for {project_name} swarm.\"\"\"
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
{agent_handoff_imports}

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# Triage agent — only routes, never answers
triage_agent = create_agent(
    llm,
    tools=[{", ".join(f"transfer_to_{n}" for n in agent_names)}],
    system_prompt=(
        "You are a triage agent. Analyze the request and transfer "
        "to the appropriate specialist. Do NOT answer questions "
        "yourself — always transfer. If multiple issues exist, "
        "transfer to the most urgent one first."
    ),
)
'''

        for name, label in zip(agent_names, agent_labels):
            other_handoffs = [f"transfer_to_{n}" for n in agent_names if n != name]
            handoff_str = ",\n    ".join(other_handoffs)

            agent_code += f'''

# {label} specialist
{name}_agent = create_agent(
    llm,
    tools=[
        # Add domain tools here
        # e.g., lookup_{name}_info, do_{name}_action,
        {handoff_str},
    ],
    system_prompt=(
        "You are a {label.lower()} specialist. "
        "Help with {label.lower()} issues. "
        "If the customer has issues outside your domain, "
        "transfer to the appropriate specialist."
    ),
)
'''

    # graph.py
    route_code = f'''\
\"\"\"Graph assembly for {project_name} swarm multi-agent system.\"\"\"
from typing import Literal

from langchain_core.messages import AIMessage
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

from .state import {state_class}
from .agents import triage_agent, {", ".join(f"{name}_agent" for name in agent_names)}
'''

    route_code += f"""

# Node wrappers
def triage_node(state: {state_class}) -> Command:
    result = triage_agent.invoke({{"messages": state["messages"]}})
    return result  # Command from handoff tool

"""

    for name, label in zip(agent_names, agent_labels):
        route_code += f"""
def {name}_node(state: {state_class}) -> dict:
    result = {name}_agent.invoke({{"messages": state["messages"]}})
    return {{
        "messages": result["messages"][-1:],
        "resolution_notes": [f"{label}: {{result['messages'][-1].content[:200]}}"],
    }}

"""

    route_code += f"""
def route_after_agent(
    state: {state_class},
) -> Literal[{', '.join(f'"{n}"' for n in agent_names)}, "__end__"]:
    \"\"\"Route to the next agent or end based on state and handoff count.\"\"\"

    # Recursion guard
    if state.get("handoff_count", 0) >= 3:
        return "__end__"

    messages = state.get("messages", [])
    if messages:
        last_msg = messages[-1]
        if isinstance(last_msg, AIMessage) and not last_msg.tool_calls:
            return "__end__"  # No tool calls = done

    current = state.get("current_agent", "")
    if current in ({', '.join(f'"{n}"' for n in agent_names)}):
        return current
    return "__end__"


def build_graph() -> StateGraph:
    \"\"\"Assemble and compile the swarm multi-agent graph.\"\"\"
    builder = StateGraph({state_class})

    # Add nodes
    builder.add_node("triage", triage_node)
    {chr(10) + '    '.join(f'builder.add_node("{n}", {n}_node)' for n in agent_names)}

    # Wire edges
    builder.add_edge(START, "triage")

    # Each specialist can route to any other specialist or end
    for node in [{', '.join(f'"{n}"' for n in agent_names)}]:
        builder.add_conditional_edges(
            node,
            route_after_agent,
            [{', '.join(f'"{n}"' for n in agent_names)}, END],
        )

    checkpointer = MemorySaver()
    return builder.compile(checkpointer=checkpointer)
"""

    # Write files
    with open(os.path.join(dir_path, "state.py"), "w") as f:
        f.write(state_code)
    with open(os.path.join(dir_path, "handoff_tools.py"), "w") as f:
        f.write(handoff_code)
    with open(os.path.join(dir_path, "agents.py"), "w") as f:
        f.write(agent_code)
    with open(os.path.join(dir_path, "graph.py"), "w") as f:
        f.write(route_code)

    # Add Command import to graph.py
    graph_path = os.path.join(dir_path, "graph.py")
    with open(graph_path) as f:
        content = f.read()
    content = content.replace(
        "from .agents import",
        "from langgraph.types import Command\n\nfrom .agents import"
    )
    with open(graph_path, "w") as f:
        f.write(content)

    print(f"Swarm project generated at: {dir_path}")
    print(f"Files: state.py, handoff_tools.py, agents.py, graph.py")
    print(f"Agents: {', '.join(agent_names)}")
    if triage_only:
        print("Mode: triage-only (specialists handle requests without further handoffs)")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate LangGraph swarm pattern scaffold")
    parser.add_argument("--name", required=True, help="Project name (e.g., support)")
    parser.add_argument("--agents", required=True, help="Comma-separated agent names (e.g., billing,tech,account)")
    parser.add_argument("--output", default=".", help="Output directory (default: current)")
    parser.add_argument("--triage-only", action="store_true",
                        help="Triage routes to specialists who handle without further handoffs")
    args = parser.parse_args()

    agents = [a.strip() for a in args.agents.split(",")]
    generate_swarm_project(args.name, agents, args.output, args.triage_only)
