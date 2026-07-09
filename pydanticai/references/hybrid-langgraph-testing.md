# Testing Hybrid PydanticAI + LangGraph Patterns with TestModel

Use `TestModel` to validate LangGraph wiring that wraps PydanticAI agents without needing real API keys or incurring LLM costs.

## Why This Matters

When wrapping a PydanticAI agent inside a LangGraph `StateGraph` node, you need to verify:

- The graph routes correctly (conditional edges reach the right node)
- State flows properly between nodes
- Checkpointing works across threads
- The agent's `@agent.tool` tools are registered and a callable path exists

`TestModel` lets you test all of this without calling a real LLM. It returns schema-conforming dummy values (e.g. `"a"` for `str` fields, `0.0` for `float` fields) instantly — no network, no API key, no cost.

## Key Ingredients

| Ingredient | Purpose |
|---|---|
| `TestModel()` | Fake model that returns valid-but-dummy structured output |
| `defer_model_check=True` | Required on module-level agents so they import without resolving the model |
| `Agent.override(model=TestModel())` | Context manager to swap in TestModel at test time |
| `MemorySaver()` | LangGraph checkpointer for thread-persistence testing |

## Complete Runnable Example

```python
"""
Hybrid PydanticAI + LangGraph demo — runs with TestModel, no API keys.
"""

from typing import Literal, NotRequired, TypedDict

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

from pydantic import BaseModel, Field
from pydantic_ai import Agent, RunContext
from pydantic_ai.models.test import TestModel


# ── LangGraph State ──────────────────────────────────────────────────────

class AgentState(TypedDict):
    user_query: str
    specialist_type: NotRequired[str]
    specialist_result: NotRequired[str]
    final_answer: NotRequired[str]


# ── PydanticAI Agent (output_type=BaseModel + @agent.tool) ───────────────

class WeatherOutput(BaseModel):
    summary: str = Field(description="Weather summary")
    temperature: float = Field(description="Temperature in Celsius")

TEST_MODEL = TestModel()                          # ← No API key needed

weather_agent = Agent(
    TEST_MODEL,                                   # ← Inject TestModel directly
    output_type=WeatherOutput,
    instructions='Provide a weather summary.',
    defer_model_check=True,                       # ← Required for module level
)


@weather_agent.tool
async def get_temperature(ctx: RunContext, city: str, units: str = "celsius") -> float:
    """Get the current temperature for a city."""
    return 22.0 if units == "celsius" else 71.6


# ── LangGraph Nodes ──────────────────────────────────────────────────────

def triage_node(state: AgentState) -> dict:
    query = state["user_query"].lower()
    if any(w in query for w in ["weather", "temperature", "forecast"]):
        return {"specialist_type": "weather"}
    return {"specialist_type": "unknown"}


def conditional_edge(state: AgentState) -> Literal["weather", "unknown"]:
    return state.get("specialist_type", "unknown")


async def weather_node(state: AgentState) -> dict:
    result = await weather_agent.run(state["user_query"])
    output: WeatherOutput = result.output
    return {
        "specialist_result": output.model_dump_json(),
        "final_answer": f"Weather: {output.summary} ({output.temperature}°C)",
    }


def unknown_node(state: AgentState) -> dict:
    return {"final_answer": "I can only answer weather-related queries."}


# ── Build Graph ──────────────────────────────────────────────────────────

builder = StateGraph(AgentState)
builder.add_node("triage", triage_node)
builder.add_node("weather", weather_node)
builder.add_node("unknown", unknown_node)

builder.add_edge(START, "triage")
builder.add_conditional_edges("triage", conditional_edge, {
    "weather": "weather",
    "unknown": "unknown",
})
builder.add_edge("weather", END)
builder.add_edge("unknown", END)

checkpointer = MemorySaver()
graph = builder.compile(checkpointer=checkpointer)


# ── Run ──────────────────────────────────────────────────────────────────

async def main():
    # Turn 1 — routes to weather node (PydanticAI agent runs under TestModel)
    r1 = await graph.ainvoke(
        {"user_query": "What's the weather in London?"},
        {"configurable": {"thread_id": "thread-1"}},
    )
    # r1["final_answer"] -> "Weather: a (0.0°C)"  (TestModel dummy values)
    # r1["specialist_type"] -> "weather"

    # Turn 2 — routes to unknown
    r2 = await graph.ainvoke(
        {"user_query": "Play some music"},
        {"configurable": {"thread_id": "thread-1"}},
    )
    # r2["final_answer"] -> "I can only answer weather-related queries."

    # Turn 3 — new thread, same agent type
    r3 = await graph.ainvoke(
        {"user_query": "Temperature in Tokyo"},
        {"configurable": {"thread_id": "thread-2"}},
    )
    # r3["final_answer"] -> "Weather: a (0.0°C)"
```

## What TestModel Returns for BaseModel output_type

| Field type | TestModel output |
|---|---|
| `str` | `"a"` (single character) |
| `float` | `0.0` |
| `int` | `0` |
| `bool` | `False` |
| `list` | `[]` |
| `dict` | `{}` |

These dummy values are **schema-conforming** — they pass Pydantic validation — but they're clearly artificial. Use them to verify graph **structure and routing**, not output quality.

## Alternative: Override at Test Time

If you want the agent declared with a real model name (e.g. `'openai:gpt-5.2'`) and swap in TestModel only during tests:

```python
# Module-level agent with real model name
weather_agent = Agent(
    'openai:gpt-5.2',
    output_type=WeatherOutput,
    defer_model_check=True,
)

# In your test
with weather_agent.override(model=TestModel()):
    result = await weather_agent.run("What's the weather?")
```

This is the standard pytest pattern — see `references/testing-evals.md` for the full fixture-based approach.

## Pitfalls

- **`graph.ainvoke()` needs `configurable["thread_id"]`** — LangGraph's MemorySaver requires a thread ID to persist state. Without it, checkpointing silently fails.
- **TestModel dummy values are obvious** — `summary="a"`, `temperature=0.0`. Don't mistake them for real LLM output.
- **`defer_model_check=True` is non-negotiable** at module level, even with TestModel injected directly. Without it, `Agent(...)` tries to resolve the model string at import time.
- **`graph.branches` does not exist on `CompiledStateGraph`** in latest langgraph — verify conditional edges by runtime behavior (different routing per query), not attribute access.
