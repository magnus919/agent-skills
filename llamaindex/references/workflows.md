# LlamaIndex Workflows

## Core Model

Workflows are event-driven step-based orchestration. Steps consume typed events and emit typed events.

```python
from llama_index.core.workflow import Workflow, StartEvent, StopEvent, Event, step

class MyWorkflow(Workflow):
    @step
    async def step_one(self, ev: StartEvent) -> MyEvent:
        # Do work
        return MyEvent(result=processed_data)

    @step
    async def step_two(self, ev: MyEvent) -> StopEvent:
        # Final step
        return StopEvent(result=ev.result)
```

## Running a Workflow

```python
w = MyWorkflow(timeout=60, verbose=False)
result = await w.run(input_data="your data")
```

## Control Flow Patterns

| Pattern | Implementation |
|---------|---------------|
| **Sequential** | Step A >> Event >> Step B |
| **Branching** | `if condition: return EventX else: return EventY` |
| **Looping** | Step returns event handled by an earlier step |
| **Parallel fan-out** | `return list[Event]` |
| **Parallel fan-in** | Accept `list[Event]` |
| **Dynamic emission** | `ctx.send_event(ev)` |
| **Dynamic collection** | `ctx.collect_events(...)` |

## State Management

```python
async with ctx.store.edit_state() as state:
    state["counter"] = state.get("counter", 0) + 1
```

## Durable Workflows (Checkpoint/Resume)

```python
# Checkpoint on step completion
async for ev in handler.stream_events(expose_internal=True):
    if isinstance(ev, StepStateChanged) and ev.step_state == StepState.NOT_RUNNING:
        db.save("my-run", json.dumps(handler.ctx.to_dict()))

# Resume after crash
ctx = Context.from_dict(w, json.loads(db.load("my-run")))
result = await w.run(ctx=ctx)
```

Key properties:
- At-least-once semantics (in-flight steps may re-run)
- Step side effects must be idempotent
- Non-serializable objects (API clients, DB connections) go in `Resource` factories

## Resource Injection

```python
from typing import Annotated
from llama_index.core.workflow import Resource

def get_client() -> MyApiClient:
    return MyApiClient()

class MyWorkflow(Workflow):
    @step
    async def process(self, ev: StartEvent,
                      client: Annotated[MyApiClient, Resource(get_client)]) -> StopEvent:
        result = await client.do_work(ev.data)
        return StopEvent(result=result)
```

## Validation

```python
workflow.validate()  # Check event graph before running
workflow.validate(validate_resources=True)  # Also resolves Resource factories
```

For intentionally dynamic steps: `@step(skip_graph_checks=["reachability"])`

## Migrating from Query Pipelines

Query Pipelines are deprecated in 0.14+. Migrate patterns:
- **Loops** in a DAG = a step returning an event consumed by an earlier step
- **Branches** in a DAG = `if/else` returning different event types
- **Data passing** in a DAG = typed event fields
