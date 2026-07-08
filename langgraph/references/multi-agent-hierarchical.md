# Hierarchical Multi-Agent — Subgraphs and Nested Teams

Hierarchical multi-agent systems use **subgraphs** — standalone LangGraph graphs composed as nodes within a parent graph. Each subgraph has its own state, its own nodes, and its own control flow, but communicates with the parent through defined state channels or function calls.

This pattern maps to organizational team structures: a parent supervisor delegates to team leads, who each manage their own specialist agents.

## Architecture

```
[Parent Supervisor]
       │
       ▼
┌──────────────┐     ┌──────────────┐
│  Research    │     │  Writing     │
│  Team        │     │  Team        │
│  (subgraph)  │     │  (subgraph)  │
│              │     │              │
│ Search →     │     │ Draft →      │
│ Analyze →    │     │ Review →     │
│ Synthesize   │     │ Polish       │
└──────────────┘     └──────────────┘
       │                      │
       └──────────┬───────────┘
                  ▼
         [Parent Supervisor]
                  │
                  ▼
            [Final Output]
```

## Two Subgraph Wiring Patterns

### Pattern A: Different State Schemas (Call Inside a Node)

Use when the parent and subgraph have **no shared state keys**. Write a wrapper function that transforms parent state to subgraph input and subgraph output back to parent state:

```python
from langgraph.graph.state import StateGraph, START

# Subgraph with its own state schema
class ResearchState(TypedDict):
    topic: str
    findings: list[str]

def search_node(state: ResearchState):
    results = search(state["topic"])
    return {"findings": [results]}

def analyze_node(state: ResearchState):
    analysis = analyze_findings(state["findings"])
    return {"findings": state["findings"] + [analysis]}

research_builder = StateGraph(ResearchState)
research_builder.add_node(search_node)
research_builder.add_node(analyze_node)
research_builder.add_edge(START, "search_node")
research_builder.add_edge("search_node", "analyze_node")
research_subgraph = research_builder.compile()

# Parent graph with different state
class ParentState(TypedDict):
    query: str
    answer: str

def call_research_team(state: ParentState):
    # Transform parent → subgraph state
    subgraph_input = {"topic": state["query"], "findings": []}
    subgraph_output = research_subgraph.invoke(subgraph_input)
    # Transform subgraph → parent state
    return {"answer": subgraph_output["findings"][-1]}

parent_builder = StateGraph(ParentState)
parent_builder.add_node("research", call_research_team)
parent_builder.add_edge(START, "research")
parent_graph = parent_builder.compile()
```

### Pattern B: Shared State Keys (Add Subgraph as Node)

Use when the parent and subgraph **share state keys** (e.g., both use `messages`). Pass the compiled subgraph directly to `add_node` — no wrapper needed:

```python
# Subgraph that reads/writes shared state
class SharedState(MessagesState):
    extra: str

def sub_agent_node(state: SharedState):
    result = some_agent.invoke({"messages": state["messages"]})
    return {"messages": result["messages"][-1:]}

sub_builder = StateGraph(SharedState)
sub_builder.add_node("sub_agent", sub_agent_node)
sub_builder.add_edge(START, "sub_agent")
subgraph = sub_builder.compile()

# Parent graph — add subgraph directly as a node
parent_builder = StateGraph(SharedState)
parent_builder.add_node("my_subgraph", subgraph)  # compiled graph as node
parent_builder.add_edge(START, "my_subgraph")
parent_graph = parent_builder.compile()
```

## Subgraph Persistence Modes

Subgraph persistence is controlled by the `checkpointer` parameter on `.compile()`.

| Mode | `checkpointer=` | Behavior | Use Case |
|------|----------------|----------|----------|
| **Per-invocation** (default) | `None` | Each call starts fresh, inherits parent's checkpointer for interrupts within a single call | Multi-agent systems where subagents handle independent one-off requests |
| **Per-thread** | `True` | State accumulates across calls on the same thread | Research assistant that builds context over several exchanges |
| **Stateless** | `False` | No checkpointing — runs like a plain function | Simple transformations, no durability needed |

### Per-Invocation (Default — Recommended)

```python
subgraph = builder.compile()  # checkpointer=None, inherits from parent
```

- Supports interrupts and durable execution within a single call
- Each call starts fresh — no memory across calls
- Supports parallel calls to the same subgraph without conflicts
- Right choice for most multi-agent systems

### Per-Thread

```python
subgraph = builder.compile(checkpointer=True)
```

- Subgraph remembers previous interactions on the same thread
- **Does NOT support parallel calls** — same-namespace checkpoint conflicts
- Use `ToolCallLimitMiddleware` when wrapping as tools to prevent parallel invocation
- Requires namespace isolation when multiple per-thread subgraphs exist

**Namespace isolation pattern:**

```python
def create_sub_agent(model, *, name, **kwargs):
    """Wrap an agent with a unique node name for namespace isolation."""
    agent = create_agent(model=model, name=name, **kwargs)
    return (
        StateGraph(MessagesState)
        .add_node(name, agent)   # unique name → stable namespace
        .add_edge("__start__", name)
        .compile()
    )

fruit_agent = create_sub_agent("gpt-4o-mini", name="fruit_agent",
    tools=[fruit_info], prompt="...", checkpointer=True)
veggie_agent = create_sub_agent("gpt-4o-mini", name="veggie_agent",
    tools=[veggie_info], prompt="...", checkpointer=True)
```

### Stateless

```python
subgraph = builder.compile(checkpointer=False)
```

- Runs like a plain function call
- No interrupts, no durable execution
- If the process crashes mid-run, the subgraph cannot recover

## Streaming from Subgraphs

```python
# Using the stream.subgraphs projection (recommended)
stream = graph.stream_events(inputs, version="v3")
for subgraph in stream.subgraphs:
    print(subgraph.graph_name, subgraph.path)
    for snapshot in subgraph.values:
        print(subgraph.path, snapshot)

# Using raw event protocol
for event in stream:
    if event["method"] == "updates":
        print(event["params"]["namespace"], event["params"]["data"])
```

## Inspecting Subgraph State

```python
# Requires parent graph compiled with checkpointer
config = {"configurable": {"thread_id": "1"}}
state = graph.get_state(config, subgraphs=True)

# Access subgraph state
subgraph_state = state.tasks[0].state  # first subgraph's current state
```

## Hierarchical Teams Pattern (Full)

This pattern combines a supervisor node with nested subgraph teams:

```python
from langgraph.graph import StateGraph, START, END

# 1. Create team subgraphs
research_team = create_research_subgraph(llm, tools)
writing_team = create_writing_subgraph(llm, tools)

# 2. Create parent state
class ManagerState(MessagesState):
    current_team: str
    final_output: str

# 3. Manager node decides which team to activate
def manager_node(state: ManagerState):
    decision = routing_llm.invoke([
        SystemMessage(content="Route to: research_team, writing_team, or DONE"),
        *state["messages"],
    ])
    return {"current_team": decision.next_agent}

# 4. Wire parent graph with subgraph nodes
builder = StateGraph(ManagerState)
builder.add_node("manager", manager_node)
builder.add_node("research_team", research_team)   # subgraph as node
builder.add_node("writing_team", writing_team)     # subgraph as node
builder.add_edge(START, "manager")
builder.add_conditional_edges(
    "manager",
    lambda s: s.get("current_team", "DONE"),
    {"research_team": "research_team", "writing_team": "writing_team", "DONE": END},
)
builder.add_edge("research_team", "manager")
builder.add_edge("writing_team", "manager")
graph = builder.compile()
```

## Design Principles

1. **Each subgraph is independently testable** — you can `.invoke()` any subgraph in isolation before composing it into the parent.
2. **State boundaries are interface contracts** — the state keys a subgraph reads and writes define its public API. Document them.
3. **Prefer shared state schemas (Pattern B)** when subgraphs operate on the same data types (messages, documents). The wrapper-less composition is simpler and faster.
4. **Use per-invocation persistence by default** — only opt into per-thread when a subagent genuinely needs cross-call memory.
5. **Name isolation for per-thread subgraphs** — two per-thread subgraphs need different namespace prefixes. The `create_sub_agent` wrapper pattern ensures this.
