# LangChain Agent Patterns

## create_agent (v1.0+)

The recommended way to create agents in LangChain v1.0+. Generates a LangGraph state machine underneath.

```python
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langchain_core.tools import tool

@tool
def search_web(query: str) -> str:
    """Search the web for current information."""
    return f"Results for: {query}"

model = ChatOpenAI(model="gpt-4o")
tools = [search_web]

agent = create_agent(model, tools, prompt="You are a helpful assistant.")
result = agent.invoke({"messages": [("user", "Search for LangChain v1.0")]})
```

## Tool Definition

```python
from langchain_core.tools import tool

@tool
def get_weather(city: str) -> str:
    """Get current weather for a city."""
    return f"The weather in {city} is sunny, 22C"

# Tools can access the LangGraph Runtime Context
@tool
def get_user_preferences(ctx: RuntimeContext) -> str:
    """Get the current user's preferences from state."""
    return ctx.configurable.get("preferences", "none")
```

## Multi-Agent with Supervisor Pattern

For multiple coordinated agents, use LangGraph directly:

```python
from langgraph.graph import StateGraph, END
from typing import TypedDict, Literal

class AgentState(TypedDict):
    messages: list
    next: str

def supervisor(state: AgentState) -> AgentState:
    # Decide which agent to call next
    return {"next": "researcher"}

graph = StateGraph(AgentState)
graph.add_node("supervisor", supervisor)
graph.add_node("researcher", research_agent)
graph.add_node("writer", writer_agent)
graph.add_conditional_edges("supervisor", lambda s: s["next"])
graph.add_edge("researcher", "supervisor")
graph.add_edge("writer", END)
```

## Key v1.0 Migration Notes

| Old pattern | New pattern (v1.0+) |
|-------------|---------------------|
| `AgentExecutor` | `create_agent` (uses LangGraph) |
| `initialize_agent` | `create_agent` |
| `LLMChain` | LCEL: `prompt | model | parser` |
| `ConversationBufferMemory` | LangGraph checkpointer |
| `agent.run()` | `agent.invoke()` |
