# Production — Deployment, Observability, and Common Failures

Deploying LangGraph workflows to production requires careful infrastructure planning. This reference covers deployment via LangSmith Agent Server, observability with LangSmith, and the most common production failure modes with fixes.

## Deployment

LangGraph apps are deployed via **LangSmith Agent Server** — a purpose-built platform for long-running, stateful workflows.

### Key Capabilities

| Feature | Details |
|---------|---------|
| Persistence | Handled automatically by Agent Server — no manual checkpointer config needed |
| Scaling | Horizontal scaling with stateful persistence |
| Monitoring | Built-in LangSmith tracing and evaluation |
| CLI | `langgraph deploy` for deployment management |
| Docker | Custom Dockerfiles supported via `langgraph.json` configuration |

### Deployment Architecture

```
Local Dev → langgraph deploy → Agent Server → Production
                                    │
                                    ▼
                            LangSmith Tracing
                                    │
                                    ▼
                        Observability + Evaluation
```

## Observability with LangSmith

### Per-Node Tracing

Decorate every node with `@traceable` for isolated spans:

```python
from langsmith import traceable

@traceable(name="billing_node", run_type="chain")
def billing_node(state: MultiAgentState) -> dict:
    # ... node implementation
    return result
```

### Tag Traces for Comparison

```python
with tracing_context(
    metadata={"pattern": "supervisor", "agents_available": 3},
    tags=["production", "multi-agent-v1"],
):
    result = graph.invoke(inputs)
```

### Key Metrics to Watch

1. **Routing accuracy** — Open the supervisor span, check if the chosen agent matches the actual domain. Log misroutes as negative feedback.
2. **Handoff chains** (swarm) — Trace the full `triage → tech → billing` path. Longer than 3 hops = routing problem.
3. **Token waste on re-routing** — The supervisor pattern doubles token spend on routing calls. Track total tokens per pattern and compare.

## Common Production Failure Modes

### 1. Routing Loops (Supervisor)

Supervisor routes to billing → billing responds → supervisor routes to billing again → repeats.

**Diagnosis:** LangSmith traces show the same `supervisor → billing → supervisor → billing` pattern repeating.

**Fix:** Include resolution notes in the supervisor's context so it can see what's already been addressed. Add a `handoff_count` to state and check it in the routing function.

```python
class MultiAgentState(MessagesState):
    current_agent: str
    resolution_notes: Annotated[list[str], operator.add]
    handoff_count: int

def route_to_agent(state: MultiAgentState) -> str:
    if state["handoff_count"] >= 5:
        return "end"  # force escalation
    agent = state.get("current_agent", "DONE")
    if agent == "DONE":
        return "end"
    return agent
```

### 2. Context Loss on Handoff (Swarm)

Agent A resolves part of the issue and hands off to Agent B. Agent B sees the original message but has no context about what Agent A already did.

**Fix:** Propagate resolution context through `Command.update`. The `resolution_notes` accumulator ensures each specialist's work is visible to the next.

### 3. Supervisor Bottleneck

Every interaction requires a routing LLM call — even for obvious intents.

**Fix:** Add a fast-path classifier (keyword matching or small model) for unambiguous intents before the supervisor LLM call.

### 4. Swarm Ping-Pong

Agent A doesn't know the answer → hands off to Agent B → Agent B doesn't know → hands off back. Repeats until recursion limit.

**Fix:** Track `handoff_count` in state. After 3, force escalation to a human or fallback agent.

### 5. Lost Messages During Handoff

Handoff tool returns `Command(graph=Command.PARENT)` but the specialist's tool-calling loop messages don't propagate to the parent.

**Fix:** Ensure `Command.update` includes the relevant messages. LLMs expect `ToolCall` ↔ `ToolMessage` pairing. Breaking this pairing causes malformed history errors.

### 6. Per-Thread Subgraph Parallel Calls

An LLM calls a per-thread subgraph tool multiple times in parallel. Both writes hit the same checkpoint namespace → conflict.

**Fix:** Use `ToolCallLimitMiddleware` or configure the model to prevent parallel tool calls for per-thread subgraph tools.

### 7. Checkpoint Bloat

Long conversations accumulate thousands of checkpoints, increasing latency and storage costs.

**Fix:** Prune old checkpoints periodically. With PostgresSaver, set up a cron job to delete checkpoints older than N days.

### 8. MemorySaver Not Persisting Restarts

Local development with `MemorySaver` loses all state when the process restarts.

**Fix:** Use a persistent backend (`PostgresSaver` / `SqliteSaver`) for anything that needs to survive restarts.

## Production Readiness Checklist

- [ ] Checkpointer uses a persistent backend (not `MemorySaver`)
- [ ] All nodes have `@traceable` decorators for observability
- [ ] Routing has a recursion guard (`handoff_count` limit)
- [ ] Supervisor includes resolution notes in context (prevents loops)
- [ ] Fast-path classifier exists for unambiguous intents
- [ ] Evals pipeline runs on every PR (routing accuracy + resolution coverage)
- [ ] Checkpoint pruning cron job configured
- [ ] Per-thread subgraph tools have parallel call limits
- [ ] Error handling for tool failures (graceful degradation, not crash)
- [ ] Streaming implemented for real-time UX
