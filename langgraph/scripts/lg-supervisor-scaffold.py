#!/usr/bin/env python3
"""
LangGraph Supervisor Pattern Scaffold Generator.

Generates a complete supervisor-based multi-agent project with:
- State definitions (MultiAgentState with routing fields)
- Routing decision schema (Pydantic)
- Supervisor node with structured output
- Specialist agent wrappers
- Graph assembly with conditional edges
- Main entry point and example invocation

Usage:
    python lg-supervisor-scaffold.py --name customer-service --agents billing,tech,account
    python lg-supervisor-scaffold.py --name research --agents search,summarize,fact-check --output ./my-project
"""

import argparse
import os
from typing import List


def snake_case(name: str) -> str:
    return name.replace("-", "_").replace(" ", "_").lower()


def pascal_case(name: str) -> str:
    return "".join(word.capitalize() for word in name.replace("-", " ").replace("_", " ").split())


AGENT_TEMPLATE = """\
from langchain.agents import create_agent

{tool_defs}

{agent_name}_agent = create_agent(
    llm,
    tools=[{tool_list}],
    system_prompt="{system_prompt}",
)
"""

NODE_TEMPLATE = """\
def {agent_name}_node(state: {state_class}) -> dict:
    \"\"\"{agent_name} specialist node.\"\"\"
    result = {agent_name}_agent.invoke({{"messages": state["messages"]}})
    return {{
        "messages": result["messages"][-1:],
        "resolution_notes": [
            f"{agent_name_display}: {{result['messages'][-1].content[:200]}}"
        ],
    }}
"""


def generate_project(project_name: str, agents: List[str], output_dir: str):
    pname = snake_case(project_name)
    state_class = pascal_case(project_name) + "State"
    dir_path = os.path.join(output_dir, pname)
    os.makedirs(dir_path, exist_ok=True)

    # Generate agent names with display labels
    agent_names = [snake_case(a) for a in agents]
    agent_labels = [a.replace("-", " ").title() for a in agents]

    # state.py
    state_code = f'''\
\"\"\"State definitions for {project_name} multi-agent system.\"\"\"
from typing import Annotated, TypedDict
from langgraph.graph import MessagesState
from pydantic import BaseModel, Field
import operator


class {state_class}(MessagesState):
    """Shared state across all agents in the {project_name} system."""

    current_agent: str
    """Which specialist agent is currently active."""

    resolution_notes: Annotated[list[str], operator.add]
    """Audit trail of what each agent resolved. Use operator.add for parallel-safety."""

    handoff_count: int = 0
    """Recursion guard — incremented on each routing decision."""


class RoutingDecision(BaseModel):
    """Structured output schema for the supervisor routing node."""

    next_agent: str = Field(
        description="The next agent to handle the request: "
        "{agent_choices} or 'DONE'"
    )
    reasoning: str = Field(description="Why this agent was chosen")
'''

    agent_choices = ", ".join(f"'{n}'" for n in agent_names)
    state_code = state_code.replace("{agent_choices}", agent_choices)

    utils_code = f'''\
\"\"\"Utility functions for {project_name}.\"\"\"
from langgraph.types import Command
from langchain_core.tools import tool


def make_handoff_tool(target_agent: str, description: str):
    \"\"\"Factory that creates a handoff tool for transferring to another agent.\"\"\"

    @tool(f"transfer_to_{{target_agent}}")
    def handoff(reason: str) -> Command:
        \"\"\"Transfer the conversation to another specialist agent.\"\"\"
        return Command(
            goto=target_agent,
            update={{"current_agent": target_agent}},
            graph=Command.PARENT,
        )

    handoff.__doc__ = description
    return handoff
'''

    # graph.py
    agent_uppers = [snake_case(a).upper() for a in agents]
    fast_path_entries = "\n    ".join(
        f'FAST_PATH[{a!r}] = "{n}"'
        for a, n in zip(agents, agent_names)
    )

    node_funcs = "\n\n\n".join(
        NODE_TEMPLATE.format(
            agent_name=name,
            agent_name_display=label,
            state_class=state_class,
        )
        for name, label in zip(agent_names, agent_labels)
    )

    graph_code = f'''\
\"\"\"Graph assembly for {project_name} multi-agent system (supervisor pattern).\"\"\"

from langchain_core.messages import SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

from .state import {state_class}, RoutingDecision

# Initialize LLM — swap provider as needed
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
routing_llm = llm.with_structured_output(RoutingDecision)

# Fast-path routing for unambiguous intents
FAST_PATH = {{}}
{fast_path_entries}


def supervisor(state: {state_class}) -> dict:
    \"\"\"Central routing node. Classifies intent and delegates to the appropriate specialist.\"\"\"

    # Try fast-path first
    if state["messages"]:
        last_msg = state["messages"][-1].content.lower()
        for keyword, agent in FAST_PATH.items():
            if keyword in last_msg:
                return {{"current_agent": agent}}

    # Full routing with context
    notes = "\\n".join(state.get("resolution_notes", []))
    history_context = f"\\n\\nAlready resolved:\\n{{notes}}" if notes else ""

    agent_descriptions = "\\n".join(
        f"- {{name}}: {{desc}}"
        for name, desc in [
            {agent_descriptions}
        ]
    )

    response = routing_llm.invoke([
        SystemMessage(
            content="You are a multi-agent supervisor. Analyze the conversation "
                    "and decide which specialist should handle the next step.\\n\\n"
                    f"Available agents:\\n{{agent_descriptions}}\\n"
                    "- DONE: the request has been fully addressed\\n\\n"
                    "Do NOT re-route to an agent that has already handled "
                    "its portion of the request." + history_context
        ),
        *state["messages"],
    ])
    return {{"current_agent": response.next_agent}}


# Specialist agents — import or define your agents here
# See templates in assets/templates/ for full agent definitions
{node_funcs}


def route_to_agent(state: {state_class}) -> str:
    \"\"\"Reads current_agent from state and returns the target node name.\"\"\"
    agent = state.get("current_agent", "DONE")
    if agent == "DONE" or state.get("handoff_count", 0) >= 5:
        return "end"
    return agent


def build_graph() -> StateGraph:
    \"\"\"Assemble and compile the supervisor multi-agent graph.\"\"\"
    builder = StateGraph({state_class})

    # Add nodes
    builder.add_node("supervisor", supervisor)
    {node_additions}

    # Wire edges
    builder.add_edge(START, "supervisor")

    builder.add_conditional_edges(
        "supervisor",
        route_to_agent,
        {{
            {route_map}
            "end": END,
        }},
    )

    # Each specialist returns to supervisor
    {return_edges}

    # Compile with checkpointer for persistence
    checkpointer = MemorySaver()
    return builder.compile(checkpointer=checkpointer)
'''

    node_additions = "\n    ".join(
        f'builder.add_node("{name}", {name}_node)'
        for name in agent_names
    )
    route_map = ",\n            ".join(
        f'            "{name}": "{name}"'
        for name in agent_names
    )
    return_edges = "\n    ".join(
        f'builder.add_edge("{name}", "supervisor")'
        for name in agent_names
    )
    agent_descriptions = ",\n        ".join(
        f'("{n}", "{l} specialist")'
        for n, l in zip(agent_names, agent_labels)
    )

    graph_code = graph_code.replace("{node_additions}", node_additions)
    graph_code = graph_code.replace("{route_map}", route_map)
    graph_code = graph_code.replace("{return_edges}", return_edges)
    graph_code = graph_code.replace("{agent_descriptions}", agent_descriptions)

    # main.py
    main_code = f'''\
\"\"\"{project_name} — Supervisor Multi-Agent System\"\"\"
from graph import build_graph


def main():
    graph = build_graph()

    config = {{"configurable": {{"thread_id": "example-1"}}}}

    user_query = input("What would you like help with? ")
    result = graph.invoke(
        {{
            "messages": [{{"role": "user", "content": user_query}}],
            "current_agent": "",
            "resolution_notes": [],
            "handoff_count": 0,
        }},
        config=config,
    )

    print("\\n=== Result ===")
    for msg in result["messages"]:
        if hasattr(msg, "content") and msg.content:
            print(f"{{msg.type}}: {{msg.content[:200]}}")

    if result.get("resolution_notes"):
        print("\\n=== Resolution Notes ===")
        for note in result["resolution_notes"]:
            print(f"  - {{note}}")


if __name__ == "__main__":
    main()
'''

    # Write files
    with open(os.path.join(dir_path, "state.py"), "w") as f:
        f.write(state_code)
    with open(os.path.join(dir_path, "utils.py"), "w") as f:
        f.write(utils_code)
    with open(os.path.join(dir_path, "graph.py"), "w") as f:
        f.write(graph_code)
    with open(os.path.join(dir_path, "main.py"), "w") as f:
        f.write(main_code)

    print(f"Project generated at: {dir_path}")
    print(f"Files: state.py, utils.py, graph.py, main.py")
    print(f"Agents: {', '.join(agent_names)}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate LangGraph supervisor pattern scaffold")
    parser.add_argument("--name", required=True, help="Project name (e.g., customer-service)")
    parser.add_argument("--agents", required=True, help="Comma-separated agent names (e.g., billing,tech,account)")
    parser.add_argument("--output", default=".", help="Output directory (default: current)")
    args = parser.parse_args()

    agents = [a.strip() for a in args.agents.split(",")]
    generate_project(args.name, agents, args.output)
