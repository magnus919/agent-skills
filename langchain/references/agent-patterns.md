# LangChain Agent Patterns

## Agent Creation (v1.0+ — Recommended)

The recommended way to create agents in LangChain v1.0+. Generates a LangGraph state machine underneath — giving you streaming, checkpointing, and observability without writing graph code.

```python
from langchain.agents import create_agent
from langchain.tools import tool

@tool
def search_web(query: str) -> str:
    '''Search the web for current information.'''
    return f"Results for: {query}"

model = ChatOpenAI(model="gpt-4o")
agent = create_agent(model, tools=[search_web], prompt="You are a helpful assistant.")
result = agent.invoke({"messages": [("user", "Search for LangChain v1.0")]})
```

## create_react_agent (Deprecated — Legacy)

```python
from langgraph.prebuilt import create_react_agent
```

**Deprecated in v1.0** in favor of `create_agent` from `langchain.agents`. The full signature (18+ parameters) remains available for migration:

| Parameter | Type | Purpose |
|-----------|------|---------|
| `model` | str or LanguageModelLike | LLM to power the agent |
| `tools` | Sequence[BaseTool] | Tools the agent can call |
| `prompt` | str, SystemMessage, or Callable | System prompt added to messages |
| `response_format` | Pydantic / JSON Schema | Structured output schema |
| `pre_model_hook` | RunnableLike | Truncate/trim messages before LLM call |
| `post_model_hook` | RunnableLike | Guardrails/validation after LLM call |
| `checkpointer` | Checkpointer | Persist conversation state |
| `store` | BaseStore | Cross-thread persistent memory |
| `interrupt_before` | list[str] | Halt before specific nodes |
| `interrupt_after` | list[str] | Halt after specific nodes |
| `state_schema` | TypedDict | Custom graph state schema |
| `version` | 'v1' or 'v2' | Graph version (default: v2) |

## @tool Decorator — Full Reference

```python
from langchain.tools import tool
```

| Parameter | Default | Description |
|-----------|---------|-------------|
| `name_or_callable` | (first arg) | Tool name or decorated function |
| `return_direct` | `False` | Return tool output directly to user |
| `args_schema` | `None` | Pydantic model or JSON Schema for params |
| `infer_schema` | `True` | Auto-generate schema from type hints |
| `response_format` | `"content"` | `"content"` or `"content_and_artifact"` |
| `parse_docstring` | `False` | Parse Google-style docstrings into schema |

**Critical:** `parse_docstring=False` by default — parameter descriptions in docstrings are NOT included in the tool schema. Enable it:

```python
@tool(parse_docstring=True)
def search(query: str, limit: int = 10) -> str:
    """Search the database.

    Args:
        query: Search terms to look for
        limit: Max results to return
    """
    return f"{limit} results for '{query}'"
```

Type hints are **required** — they define the tool's input schema.

### args_schema with Pydantic

```python
from pydantic import BaseModel, Field

class WeatherInput(BaseModel):
    location: str = Field(description="City name or coordinates")
    units: str = Field(default="celsius", description="Temperature unit")

@tool(args_schema=WeatherInput)
def get_weather(location: str, units: str = "celsius") -> str:
    """Get current weather."""
    return f"{location}: 22{units[0].upper()}"
```

### Reserved Parameter Names

| Name | Purpose |
|------|---------|
| `config` | RunnableConfig for callbacks and tags |
| `runtime` | ToolRuntime for state, context, store access |

## Streaming with Agents

```python
from langchain.agents import create_agent

agent = create_agent(model, tools, prompt="You are helpful.")

async for event in agent.astream_events(
    {"messages": [("user", "Research LangChain RAG")]},
    version="v2"
):
    kind = event["event"]
    if kind == "on_chat_model_stream":
        print(event["data"]["chunk"].content, end="")
    elif kind == "on_tool_start":
        print(f"\n[Calling tool: {event['name']}]")
```

Streaming events include: `on_chat_model_start`, `on_chat_model_stream`, `on_tool_start`, `on_tool_end`, `on_retriever_start`, `on_retriever_end`.

## Multi-Agent with Supervisor

For multiple coordinated agents, use LangGraph's StateGraph directly:

```python
from langgraph.graph import StateGraph, END
from typing import TypedDict, Literal

class AgentState(TypedDict):
    messages: list
    next: str

graph = StateGraph(AgentState)
graph.add_node("supervisor", supervisor_agent)
graph.add_node("researcher", research_agent)
graph.add_node("writer", writer_agent)
graph.add_conditional_edges("supervisor", lambda s: s["next"])
graph.add_edge("researcher", "supervisor")
graph.add_edge("writer", END)
```

## Key v1.0 Migration

| Old pattern | New pattern (v1.0+) |
|-------------|---------------------|
| `AgentExecutor` | `create_agent` (uses LangGraph) |
| `initialize_agent` | `create_agent` |
| `LLMChain` | LCEL: `prompt | model | parser` |
| `ConversationBufferMemory` | LangGraph checkpointer |
| `agent.run()` | `agent.invoke()` |
