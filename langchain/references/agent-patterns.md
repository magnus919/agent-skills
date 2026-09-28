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


## Keep typed decisions outside the chat model

For a bounded System One judgment, call an injected typed decision service from application orchestration or a suitable LangChain middleware hook, then route on its validated result. LangChain owns middleware and agent-flow wiring; the System One skill owns question design, provider/model validation, calibration, abstention, and substitution. The harness owns authorized state, action/recovery boundaries, and end-to-end evidence. Do not present the typed decision service as a normal chat-model implementation or let a middleware hook grant authority by itself.

**Implementation sketch — uses documented middleware hooks as a seam; not executed against LangChain or a provider:**

```python
from langchain.agents.middleware import AgentMiddleware, AgentState
from langgraph.runtime import Runtime

class DecisionState(AgentState, total=False):
    ticket: dict
    typed_decision: dict

class DecisionMiddleware(AgentMiddleware):
    state_schema = DecisionState

    def __init__(self, decision_service):
        super().__init__()
        self.decision_service = decision_service  # injected typed adapter

    async def abefore_agent(self, state: DecisionState, runtime: Runtime):
        try:
            result = await self.decision_service.classify(state["ticket"])
        except DecisionUnavailable:  # application-defined adapter exception
            return {"typed_decision": {"status": "unavailable"}}
        # The adapter validates answer IDs/types/options/probabilities.
        return {"typed_decision": result}

# Application-owned deterministic orchestration consumes `typed_decision`:
# billing -> billing workflow; technical -> technical workflow;
# unknown/unavailable -> review. Tool authorization remains a separate check.
```

For a workflow requiring an explicit graph route, keep the branch in outer orchestration or use LangGraph conditional edges rather than assuming `create_agent`'s generative loop owns the decision policy. The official [middleware guide](https://docs.langchain.com/oss/python/langchain/middleware) documents custom state and hooks, and the current [AgentMiddleware API](https://reference.langchain.com/python/langchain/agents/middleware/types/AgentMiddleware) exposes `abefore_agent` for asynchronous work; see [System One](../../system-one/SKILL.md) for the typed contract and [harness-engineering](../../harness-engineering/SKILL.md) plus its [placement guide](../../harness-engineering/references/system-one-decisions.md) for workflow ownership. The snippet is a design sketch; it has not been SDK-tested.


### Handoff contract

Application orchestration gives middleware or a pre-agent step authorized, versioned state and the finite set of allowed routes. The injected System One adapter consumes its pinned question/rubric/model revision and returns validated typed answers, model identity, and explicit unknown/error status. Middleware may carry this result in state; deterministic application policy consumes it to choose a route. Return adapter/model failures to System One, while LangChain wiring defects and harness action, recovery, and accepted-task outcomes go to their respective owners.
