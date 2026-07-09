# Hybrid PydanticAI + LangGraph Pattern

Use PydanticAI's type-safe agent framework inside a LangGraph `StateGraph` for orchestration. This gives you LangGraph's checkpointing, persistence, and complex control flow while keeping PydanticAI's declarative agent definitions and structured output validation.

## Architecture

```
LangGraph StateGraph (orchestration layer)
├── Checkpointer (SQLite/Postgres — persistence)
├── Human-in-the-loop (interrupt/resume)
│
├── Node: triage_agent
│   └── PydanticAI Agent (type-safe routing decision)
│
├── Node: specialist_agent
│   └── PydanticAI Agent (typed tools, structured output)
│       ├── @agent.tool — typed function tools
│       └── output_type=BaseModel — validated responses
│
└── Conditional edges (LangGraph routing)
```

## Complete Example

A research system: triage agent decides which specialist to call, each specialist is a PydanticAI agent with typed tools.

```python
from typing import Literal, NotRequired, TypedDict

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

from pydantic import BaseModel, Field
from pydantic_ai import Agent, RunContext


# ── LangGraph State ──────────────────────────────────────────────────────
class AgentState(TypedDict):
    """State passed between LangGraph nodes."""
    user_query: str
    specialist_type: NotRequired[str]        # 'weather' | 'news' | 'unknown'
    specialist_result: NotRequired[str]       # Raw output from PydanticAI agent
    final_answer: NotRequired[str]


# ── PydanticAI Agents ────────────────────────────────────────────────────
class WeatherOutput(BaseModel):
    summary: str = Field(description="Weather summary for the city")
    temperature: float = Field(description="Current temperature in Celsius")

weather_agent = Agent(
    'openai:gpt-5.2',
    output_type=WeatherOutput,
    instructions='Provide a weather summary for the given city.',
    defer_model_check=True,
)

@weather_agent.tool
async def get_temperature(ctx: RunContext, city: str, units: str = "celsius") -> float:
    """Get the current temperature for a city."""
    return 22.0 if units == "celsius" else 71.6

news_agent = Agent(
    'openai:gpt-5.2',
    output_type=str,
    instructions='Summarize the latest news for the given topic.',
    defer_model_check=True,
)


# ── LangGraph Nodes (wrapping PydanticAI agents) ────────────────────────

def triage_node(state: AgentState) -> dict:
    """Classify the query using simple keyword matching."""
    query = state["user_query"].lower()
    if any(w in query for w in ["weather", "temperature", "forecast"]):
        return {"specialist_type": "weather"}
    elif any(w in query for w in ["news", "headline", "latest"]):
        return {"specialist_type": "news"}
    return {"specialist_type": "unknown"}


def conditional_edge(state: AgentState) -> Literal["weather", "news", "unknown"]:
    """Route to the correct specialist node."""
    return state.get("specialist_type", "unknown")


async def weather_node(state: AgentState) -> dict:
    """Run the PydanticAI weather agent."""
    result = await weather_agent.run(state["user_query"])
    return {
        "specialist_result": result.output.model_dump_json(),
        "final_answer": f"Weather: {result.output.summary} ({result.output.temperature}°C)",
    }


async def news_node(state: AgentState) -> dict:
    """Run the PydanticAI news agent."""
    result = await news_agent.run(state["user_query"])
    return {"specialist_result": result.output, "final_answer": result.output}


def unknown_node(state: AgentState) -> dict:
    """Handle unrecognized queries."""
    return {"final_answer": "I can only answer weather and news queries."}


# ── Build the LangGraph ──────────────────────────────────────────────────

builder = StateGraph(AgentState)

builder.add_node("triage", triage_node)
builder.add_node("weather", weather_node)
builder.add_node("news", news_node)
builder.add_node("unknown", unknown_node)

builder.add_edge(START, "triage")
builder.add_conditional_edges("triage", conditional_edge, {
    "weather": "weather",
    "news": "news",
    "unknown": "unknown",
})
builder.add_edge("weather", END)
builder.add_edge("news", END)
builder.add_edge("unknown", END)

# Add checkpointing for persistence
checkpointer = MemorySaver()
graph = builder.compile(checkpointer=checkpointer)


# ── Run ──────────────────────────────────────────────────────────────────
async def main():
    # First conversation turn
    result1 = await graph.ainvoke(
        {"user_query": "What's the weather in London?"},
        {"configurable": {"thread_id": "thread-1"}},
    )
    print(result1["final_answer"])
    # > Weather: London is currently mild with light cloud cover (22.0°C)

    # Second turn — same thread, persisted history
    result2 = await graph.ainvoke(
        {"user_query": "Any tech news today?"},
        {"configurable": {"thread_id": "thread-1"}},
    )
    print(result2["final_answer"])
    # > Latest tech headlines...
```

## Key Integration Points

| PydanticAI feature | How it integrates into LangGraph | Benefit |
|---|---|---|
| `Agent(output_type=BaseModel)` | Agent runs inside an `async` LangGraph node | Validated structured output in graph state |
| `@agent.tool` with `RunContext` | Tools called automatically during agent run inside node | No manual tool wiring in LangGraph |
| `agent.run()` | Called inside the node function; result stored in graph state | Clean separation between agent logic and orchestration |
| `deps_type` with dependencies | Pass deps via closure or node-level initialization | LangGraph state stays clean |
| `defer_model_check=True` | Required for module-level agent declarations | Allows agents to import without API keys |

## When to Combine

| Advantage of PydanticAI | Advantage of LangGraph |
|---|---|
| Declarative agent setup with type safety | Built-in checkpointing and persistence |
| Auto-generated tool schemas from type hints | Human-in-the-loop via `interrupt()`/`Command(resume=...)` |
| Composable capabilities (WebSearch, MCP, etc.) | Subgraph composition with isolated state namespaces |
| Structured output with automatic validation | Conditional routing and dynamic fan-out (`Send()`) |
| Lower cognitive overhead for individual agents | Complex multi-agent patterns (supervisor, swarm, hierarchical) |

## When NOT to Combine

- **Simple single-agent workflows** — LangGraph adds unnecessary complexity
- **Pure data pipelines** — No LLM calls needed; use PydanticGraph directly
- **Teams committed to one framework** — The mental model overhead of maintaining both is real
