# Architecture — LangGraph Core Concepts

This reference covers LangGraph's foundational architecture. Read this first if you're new to LangGraph or building a system from scratch.

## Overview

LangGraph is a low-level orchestration framework that models agent workflows as **directed graphs**. It is inspired by Google's [Pregel](https://research.google/pubs/pub37252/) and [Apache Beam](https://beam.apache.org/), with a public interface drawing from [NetworkX](https://networkx.org/). Unlike linear chain frameworks (LangChain Expression Language, traditional pipelines), LangGraph supports **cycles** — essential for agent tool-calling loops, iterative refinement, and multi-agent coordination.

```
User → [Agent Node] → {tool call?} → [Tool Node] → [Agent Node] → ... → Response
                    ↘ (no tool) → Response
```

## Core Abstractions

### State

The graph's shared, persistent data. All nodes read from and write to the same state object. Defined as a `TypedDict` or Pydantic schema.

**Key pattern — reducer annotations:** Fields that multiple nodes write to in parallel need a reducer. The `operator.add` reducer is the most common — it concatenates lists:

```python
from typing import Annotated, TypedDict
import operator

class AgentState(TypedDict):
    messages: Annotated[list, operator.add]  # parallel-safe append
    next_agent: str                          # single writer only
    resolution_notes: Annotated[list[str], operator.add]
```

**Rule of thumb:** If multiple nodes can write to the same key, it needs a reducer. If only one node ever writes (e.g., a shared `topic` field), no reducer needed.

### Nodes

Python functions (or runnable objects) that receive state and return state updates:

```python
def my_node(state: AgentState) -> dict:
    # Read from state, do work, return updates
    return {"messages": [AIMessage(content="hello")]}
```

Nodes can be:
- **LLM calls** — invoke a model, return output
- **Tool nodes** — execute tool calls from an LLM
- **Python functions** — deterministic logic, transformations, validation
- **Subgraphs** — nested LangGraph graphs (see multi-agent-hierarchical reference)
- **Agents** — LangChain agents wrapped as a single node

### Edges

Edges define how execution flows between nodes:

- **`add_edge(start, end)`** — unconditionally traverse from start to end
- **`add_conditional_edges(source, router, path_map)`** — dynamic routing based on state

```python
# Standard edge
builder.add_edge("node_a", "node_b")

# Conditional edge
builder.add_conditional_edges(
    "analyzer",
    route_based_on_state,       # function that returns a node name
    {"billing": "billing_node", "tech": "tech_node", END: END}
)
```

## Two APIs

### Graph API (`StateGraph`)

Full control. You explicitly add nodes and wire edges with method calls.

```python
from langgraph.graph import StateGraph, START, END, MessagesState

builder = StateGraph(MessagesState)
builder.add_node("agent", agent_node)
builder.add_node("tools", ToolNode([search, calculator]))
builder.add_edge(START, "agent")
builder.add_conditional_edges("agent", should_continue, {"tools": "tools", END: END})
builder.add_edge("tools", "agent")
graph = builder.compile()
```

### Functional API (`@task` + `@entrypoint`)

Simpler decorator-based approach for linear or tree-shaped workflows:

```python
from langgraph.func import entrypoint, task

@task
def research(topic: str) -> str:
    return llm.invoke(f"Research {topic}").content

@task
def write_report(research: str) -> str:
    return llm.invoke(f"Write report: {research}").content

@entrypoint()
def workflow(topic: str):
    r = research(topic).result()
    return write_report(r).result()
```

**When to use each:**
- **Graph API** — complex routing, cycles, multi-agent, subgraphs, conditional flows
- **Functional API** — sequential chains, parallel fan-out patterns, simpler orchestration

## The Agent Loop (Tool-Calling)

The most common LangGraph pattern is the agent tool-calling loop:

```
1. LLM node receives messages
2. LLM returns response (may contain tool_calls)
3. Conditional edge: if tool_calls → ToolNode; if no tool_calls → END
4. ToolNode executes tools, returns ToolMessages
5. Edge back to LLM node
6. Repeat from 1
```

```python
from langgraph.prebuilt import ToolNode, tools_condition

builder = StateGraph(MessagesState)
builder.add_node("llm", llm_call)
builder.add_node("tools", ToolNode([search, calculator]))
builder.add_conditional_edges("llm", tools_condition, {"tools": "tools", END: END})
builder.add_edge("tools", "llm")
```

`tools_condition` is a prebuilt router: returns "tools" if the last message has `tool_calls`, otherwise returns `END`.

## Streaming

LangGraph supports multiple streaming modes:

```python
# Stream all events (most detailed)
for event in graph.stream_events(inputs, version="v3"):
    if event["method"] == "updates":
        print(event["params"]["data"])

# Stream values only (final state per superstep)
for chunk in graph.stream(inputs):
    print(chunk)

# Stream individual tokens from LLM nodes
for chunk in graph.stream(inputs, stream_mode="messages"):
    print(chunk)
```

## Key Architecture Patterns from the Official Guide

| Pattern | Structure | Best For |
|---------|-----------|----------|
| **Prompt Chaining** | Sequential LLM calls | Translation, verification, step-by-step generation |
| **Parallelization** | Fan-out → aggregate | Multi-criteria scoring, parallel research tasks |
| **Routing** | Classify → dispatch | Customer support triage, content-type routing |
| **Orchestrator-Worker** | Plan → fan-out → synthesize | Report writing, code generation across files |
| **Evaluator-Optimizer** | Generate → evaluate → loop | Iterative refinement, quality gates |
| **Agent** | LLM ↔ tool calls | General autonomous agents |

## Design Principles

1. **State is the source of truth** — all inter-node communication happens through state, not through side channels or global variables.
2. **Nodes are pure-ish** — a node receives state, does work, returns updates. It should not depend on state that isn't passed to it.
3. **Reducers prevent conflicts** — any state key written by multiple nodes in parallel MUST have a reducer.
4. **Start simple, add complexity only when needed** — a single agent with good prompts beats a multi-agent system with bad routing. Add agents only when a single prompt or toolset becomes unwieldy.
5. **Use `Send()` for dynamic fan-out** — when you don't know how many workers you'll need at compile time, use `Send()` to spawn workers dynamically from the orchestrator node.
6. **Subgraph state isolation** — subgraphs with different state schemas need a wrapper function to transform state at the boundary. Shared-schema subgraphs can be added directly as nodes.
