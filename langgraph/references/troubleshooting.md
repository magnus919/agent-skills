# Troubleshooting — Common Failures and Fixes

This reference catalogs the most common LangGraph failure modes, their symptoms, root causes, and fixes. Organized by pattern and symptom for quick lookup.

## Supervisor Pattern Failures

| Symptom | Likely Cause | Fix |
|---------|-------------|-----|
| Same agent called repeatedly in a loop | Routing loop — supervisor doesn't know the agent already handled it | Include `resolution_notes` in supervisor context |
| Slow response times under load | Supervisor bottleneck — even obvious intents get a routing LLM call | Add fast-path classifier for unambiguous intents |
| High token costs per request | Token waste on re-routing | Compare supervisor vs swarm token costs in LangSmith |
| Agent handles wrong domain | Routing accuracy regression | Check routing prompt, add negative feedback to eval dataset |

### Routing Loop — Full Diagnosis

1. Open LangSmith trace
2. Look for repeating `supervisor → billing → supervisor → billing` pattern
3. Check if `resolution_notes` is being passed to the supervisor node
4. If missing, the supervisor has no memory of what's been done
5. Fix: ensure supervisor prompt includes resolution notes:

```python
def supervisor(state: MultiAgentState) -> dict:
    notes = "\n".join(state.get("resolution_notes", []))
    history_context = f"\n\nAlready resolved:\n{notes}" if notes else ""
    # ... rest of supervisor
```

## Swarm Pattern Failures

| Symptom | Likely Cause | Fix |
|---------|-------------|-----|
| Infinite handoff loop | Swarm ping-pong — no recursion guard | Track `handoff_count`, hard limit at 3 |
| Customer asked the same question twice | Context loss on handoff — Agent B doesn't know what Agent A did | Propagate resolution context via `Command.update` |
| Next agent sees malformed history | Lost messages during handoff — ToolMessage pairing broken | Ensure `Command.update` includes paired messages |
| Agent routes to wrong specialist | Routing accuracy issue | Add more specific guidance in system prompt |

### Swarm Ping-Pong — Fix

```python
def route_after_agent(state: SwarmState) -> str:
    if state.get("handoff_count", 0) >= 3:
        return "human_escalation"  # or END with a fallback
    # ... rest of routing logic
```

### Context Loss — Fix

When a handoff tool returns `Command`, include what was done in the update:

```python
@tool
def transfer_to_billing(reason: str, context: dict = None) -> Command:
    update = {"current_agent": "billing", "handoff_count": context["count"] + 1}
    return Command(goto="billing", update=update, graph=Command.PARENT)
```

## Subgraph Failures

| Symptom | Likely Cause | Fix |
|---------|-------------|-----|
| Subgraph doesn't remember previous calls | Per-invocation default | Compile with `checkpointer=True` for per-thread memory |
| Tool calls fail with checkpoint conflict | Parallel calls to per-thread subgraph | Add `ToolCallLimitMiddleware` |
| Parallel subgraph calls overwrite each other | Same namespace conflict | Use `create_sub_agent` wrapper with unique names |
| Subgraph crashes without recovery | Stateless mode (`checkpointer=False`) | Use per-invocation (default) for durability |
| Parent can't see subgraph state | Different checkpoint namespaces | Use Store for cross-boundary data |

## Persistence Failures

| Symptom | Likely Cause | Fix |
|---------|-------------|-----|
| `thread_id` too long error | Postgres column length limit | Keep under 255 chars, use UUID |
| State lost on restart | Using in-memory `MemorySaver` | Switch to `PostgresSaver` or `SqliteSaver` |
| Checkpoints growing unbounded | No retention policy | Add cron job to prune old checkpoints |
| `interrupt()` has no effect | No checkpointer configured | Compile parent graph with checkpointer |

## Stream and Event Failures

| Symptom | Likely Cause | Fix |
|---------|-------------|-----|
| Subgraph events not visible in stream | Using wrong event protocol | Use `stream.subgraphs` projection or filter by namespace |
| Stream hangs | Graph in infinite loop | Add recursion guard or max iteration limit |
| Event namespace is empty string | Parent-level event, not subgraph | Filter by namespace: `[]` = parent, `[...]` = subgraph |

## Debugging Techniques

### 1. Check the Trace

LangSmith traces show every node execution, including:
- Input/output state per node
- Tool calls and their results
- Routing decisions (from structured output)
- Handoff chains (from Command objects)

### 2. Isolate the Subgraph

Test any subgraph independently before composing it:

```python
# Test subgraph in isolation
result = subgraph.invoke({"topic": "test"})
print(result)
```

### 3. Reduce Parallelism

When debugging, set `max_concurrency=1` to serialize execution:

```python
result = graph.invoke(inputs, {"max_concurrency": 1})
```

### 4. Add Logging to Nodes

Wrap nodes with print statements or pass through LangSmith:

```python
def debug_node(state: State) -> dict:
    print(f"enter {node_name}: keys={list(state.keys())}")
    result = actual_node(state)
    print(f"exit {node_name}: keys={list(result.keys())}")
    return result
```

### 5. Use `get_state` for Subgraph Inspection

```python
state = graph.get_state(config, subgraphs=True)
for task in state.tasks:
    if task.state:
        print(f"Subgraph state: {task.state}")
```

## Verification Checklist

When deploying a new multi-agent system, verify these in order:

- [ ] Single agent works independently (no routing dependencies)
- [ ] Supervisor/swarm routes correctly for single-domain requests
- [ ] Multi-domain requests are decomposed and handled completely
- [ ] Handoffs preserve context (no repeated questions)
- [ ] Recursion guard prevents infinite loops (supervisor and swarm)
- [ ] All errors are caught and produce graceful degradation
- [ ] Persistence works across thread resumptions
- [ ] Subgraphs are independently testable
- [ ] Eval dataset covers all routing paths
- [ ] LangSmith traces are readable and complete
