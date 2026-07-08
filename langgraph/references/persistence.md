# Persistence — Checkpointers and Stores

LangGraph provides two complementary persistence systems: **checkpointers** for short-term, thread-scoped memory and **stores** for long-term, cross-thread memory.

## Checkpointer vs Store

| Dimension | Checkpointer | Store |
|-----------|-------------|-------|
| Persists | Graph state snapshots | Application-defined key-value data |
| Scope | A single thread | Across threads |
| Memory type | Short-term, thread-scoped | Long-term, cross-thread |
| Use for | Conversation continuity, HITL, time travel, fault tolerance | User preferences, facts, shared knowledge |
| Access | Pass `thread_id` in graph config | Read/write from nodes or application code |

## Checkpointers (Short-Term Memory)

A checkpointer saves snapshots of graph state after each superstep (node execution). This enables:
- **Conversation continuity** — resume a thread where it left off
- **Human-in-the-loop** — pause for input, then resume
- **Time travel** — replay from any checkpoint
- **Fault tolerance** — recover from crashes

### Backends

```python
from langgraph.checkpoint.memory import MemorySaver   # in-memory (dev only)
from langgraph.checkpoint.sqlite import SqliteSaver   # file-based (dev)
from langgraph.checkpoint.postgres import PostgresSaver  # production
```

### Usage

```python
checkpointer = MemorySaver()  # or PostgresSaver.from_conn_string(...)
checkpointer.setup()          # creates tables for persistent backends

graph = builder.compile(checkpointer=checkpointer)

# Each thread gets a unique thread_id
config = {"configurable": {"thread_id": "thread-123"}}

result = graph.invoke(
    {"messages": [{"role": "user", "content": "Hi, my name is Bob."}]},
    config=config,
)

# Resume on the same thread — graph remembers previous messages
result2 = graph.invoke(
    {"messages": [{"role": "user", "content": "What's my name?"}]},
    config=config,
)
```

### Agent Server Handles Persistence Automatically

When deploying via LangSmith Agent Server, you do not need to implement or configure checkpointers manually. The server handles persistence infrastructure.

## Stores (Long-Term Memory)

A store persists key-value data outside graph state, accessible across threads and sessions.

### Usage

```python
from langgraph.store.memory import InMemoryStore

store = InMemoryStore()

# Write to store from a node
def remember_user(state: MessagesState, store: InMemoryStore):
    user_id = extract_user_id(state["messages"])
    store.put(
        ("users", user_id),
        "preferences",
        {"theme": "dark", "language": "en"},
    )
    return {"messages": [AIMessage(content="Saved your preferences!")]}

# Read from store
config = {"configurable": {"thread_id": "1"}}
result = graph.invoke(inputs, config=config, store=store)
```

### When to Use Store vs Checkpointer

| Need | Use |
|------|-----|
| Resume a conversation mid-stream | Checkpointer |
| Undo/redo across steps (time travel) | Checkpointer |
| Pause for human approval | Checkpointer |
| Remember user preferences across sessions | Store |
| Share data between unrelated threads | Store |
| Learn facts that persist beyond conversation | Store |

## Checkpointer Troubleshooting

### `thread_id` too long (PostgresSaver)

Keep `thread_id` under 255 characters. Use UUID or hash:

```python
import uuid
config = {"configurable": {"thread_id": str(uuid.uuid4())[:255]}}
```

### `MemorySaver` doesn't persist between restarts

In-memory checkpointers are lost on process restart. Use `PostgresSaver` or `SqliteSaver` for persistence.

### Checkpoints growing unboundedly

Long conversations accumulate checkpoints. Prune periodically or set retention:

```python
# PostgresSaver — add a cron job to delete old checkpoints:
# DELETE FROM langgraph_checkpoints WHERE created_at < NOW() - INTERVAL '7 days'
```

### State access from parent to subgraph

Subgraphs manage their own checkpoint namespace. Use **Store** for data that needs to cross graph boundaries, or configure the subgraph to write to the parent checkpoint.

## Advanced: Subgraph Persistence Modes

See `references/multi-agent-hierarchical.md` for the full subgraph persistence reference. Summary:

| Mode | `checkpointer=` | Behavior |
|------|----------------|----------|
| Per-invocation (default) | `None` | Fresh each call, inherits parent checkpointer for HITL |
| Per-thread | `True` | State accumulates across calls |
| Stateless | `False` | No checkpointing, runs like plain function |
