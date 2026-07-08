"""
Subgraph Agent — Composition Template

Demonstrates two patterns for composing subgraphs within a parent graph:

Pattern A: Different state schemas (call inside a node)
  - Parent and subgraph have no shared keys
  - Use a wrapper function to transform state at the boundary

Pattern B: Shared state keys (add as node)
  - Parent and subgraph share state keys (e.g., messages)
  - Pass compiled subgraph directly to add_node — no wrapper needed

Requirements:
  pip install langgraph langchain langchain-openai
"""

from typing_extensions import TypedDict
from langgraph.graph.state import StateGraph, MessagesState, START, END
from langgraph.checkpoint.memory import MemorySaver

# ═══════════════════════════════════════════════════════════════════════════
# Pattern A: Different State Schemas
# ═══════════════════════════════════════════════════════════════════════════

# Subgraph state — entirely different keys from parent
class ResearchState(TypedDict):
    topic: str
    findings: list[str]

def search_node(state: ResearchState):
    """Simulate searching for information on the topic."""
    return {"findings": [f"Search results for: {state['topic']}"]}

def analyze_node(state: ResearchState):
    """Analyze the search findings."""
    return {"findings": state["findings"] + ["Analysis complete."]}

# Build and compile subgraph
research_builder = StateGraph(ResearchState)
research_builder.add_node("search", search_node)
research_builder.add_node("analyze", analyze_node)
research_builder.add_edge(START, "search")
research_builder.add_edge("search", "analyze")
research_builder.add_edge("analyze", END)
research_subgraph = research_builder.compile()

# Parent graph with different state
class QueryState(TypedDict):
    question: str
    answer: str

def call_research_team(state: QueryState):
    """Wrapper: transforms parent state to subgraph state and back."""
    # Transform parent → subgraph
    subgraph_input = {"topic": state["question"], "findings": []}
    subgraph_output = research_subgraph.invoke(subgraph_input)
    # Transform subgraph → parent
    return {"answer": subgraph_output["findings"][-1]}

parent_a = StateGraph(QueryState)
parent_a.add_node("research", call_research_team)
parent_a.add_edge(START, "research")
parent_a.add_edge("research", END)
pattern_a_graph = parent_a.compile()

# Test Pattern A
result_a = pattern_a_graph.invoke({"question": "LangGraph subgraphs", "answer": ""})
print(f"Pattern A result: {result_a['answer']}")

# ═══════════════════════════════════════════════════════════════════════════
# Pattern B: Shared State Keys (Add Subgraph as Node)
# ═══════════════════════════════════════════════════════════════════════════

# Subgraph that operates on shared MessagesState
def sub_agent_node(state: MessagesState):
    """A simple agent node that responds to user messages."""
    last_msg = state["messages"][-1].content if state["messages"] else ""
    return {
        "messages": [{"role": "assistant", "content": f"Subgraph processed: {last_msg[:50]}..."}]
    }

sub_builder = StateGraph(MessagesState)
sub_builder.add_node("sub_agent", sub_agent_node)
sub_builder.add_edge(START, "sub_agent")
sub_builder.add_edge("sub_agent", END)
subgraph_b = sub_builder.compile()

# Parent graph — add compiled subgraph as a node directly
parent_b = StateGraph(MessagesState)
parent_b.add_node("entry", lambda s: {"messages": s["messages"]})
parent_b.add_node("subgraph_node", subgraph_b)  # <-- compiled graph as node
parent_b.add_edge(START, "entry")
parent_b.add_edge("entry", "subgraph_node")
parent_b.add_edge("subgraph_node", END)
pattern_b_graph = parent_b.compile()

# Test Pattern B
result_b = pattern_b_graph.invoke(
    {"messages": [{"role": "user", "content": "Hello from the parent graph!"}]}
)
print(f"Pattern B result: {result_b['messages'][-1].content}")

# ═══════════════════════════════════════════════════════════════════════════
# Pattern C: Per-Thread Subgraph with Namespace Isolation
# ═══════════════════════════════════════════════════════════════════════════

from langchain.agents import create_agent
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

@tool
def fruit_info(fruit_name: str) -> str:
    """Look up fruit info."""
    return f"Info about {fruit_name}: fresh and delicious."

@tool
def veggie_info(veggie_name: str) -> str:
    """Look up veggie info."""
    return f"Info about {veggie_name}: healthy and green."

def create_sub_agent(model, *, name, **kwargs):
    """Wrap an agent with a unique node name for namespace isolation."""
    agent = create_agent(model=model, name=name, **kwargs)
    return (
        StateGraph(MessagesState)
        .add_node(name, agent)  # unique name → stable namespace
        .add_edge("__start__", name)
        .compile()
    )

fruit_agent = create_sub_agent(
    "gpt-4o-mini", name="fruit_agent",
    tools=[fruit_info],
    prompt="You are a fruit expert. Use the fruit_info tool.",
    checkpointer=True,
)

veggie_agent = create_sub_agent(
    "gpt-4o-mini", name="veggie_agent",
    tools=[veggie_info],
    prompt="You are a veggie expert. Use the veggie_info tool.",
    checkpointer=True,
)

@tool
def ask_fruit_expert(question: str) -> str:
    """Ask the fruit expert. Use for ALL fruit questions."""
    response = fruit_agent.invoke(
        {"messages": [{"role": "user", "content": question}]},
    )
    return response["messages"][-1].content

@tool
def ask_veggie_expert(question: str) -> str:
    """Ask the veggie expert. Use for ALL veggie questions."""
    response = veggie_agent.invoke(
        {"messages": [{"role": "user", "content": question}]},
    )
    return response["messages"][-1].content

# Outer agent with checkpointer
from langchain.agents.middleware import ToolCallLimitMiddleware

orchestrator = create_agent(
    llm,
    tools=[ask_fruit_expert, ask_veggie_expert],
    prompt=(
        "You have two experts: ask_fruit_expert and ask_veggie_expert. "
        "ALWAYS delegate questions to the appropriate expert."
    ),
    middleware=[
        ToolCallLimitMiddleware(tool_name="ask_fruit_expert", run_limit=1),
        ToolCallLimitMiddleware(tool_name="ask_veggie_expert", run_limit=1),
    ],
    checkpointer=MemorySaver(),
)

print("Pattern C: Namespace-isolated per-thread subagents ready.")

# ═══════════════════════════════════════════════════════════════════════════
# Usage Notes
# ═══════════════════════════════════════════════════════════════════════════
#
# - Use Pattern A when parent and subgraph have different data models
# - Use Pattern B when both operate on shared state (e.g., messages)
# - Use Pattern C when subagents need per-thread memory AND namespace isolation
# - Per-thread subgraphs (checkpointer=True) cannot run in parallel —
#   use ToolCallLimitMiddleware to prevent parallel tool calls
# - Per-invocation (default) is the right choice for most multi-agent systems
