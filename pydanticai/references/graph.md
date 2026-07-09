# PydanticGraph — Graph & State Machine Engine

PydanticGraph is a type-hint-driven async graph and state machine library for Python. It has zero dependency on pydantic-ai — use it standalone for any workflow.

**Install:** `pip install pydantic-graph` (or included with `pydantic-ai`)

## Two APIs: BaseNode (class-based) and GraphBuilder (function-based)

Both are fully supported and interoperable.

---

## API 1: BaseNode (Class-based)

Nodes are dataclasses subclassing `BaseNode[StateT, DepsT, RunEndT]`.

### Core Types

| Type | Purpose |
|---|---|
| `BaseNode[StateT, DepsT, RunEndT]` | Abstract node class. Subclass and implement `run()`. |
| `End[RunEndT]` | Return from `run()` to signal graph completion. |
| `GraphRunContext[StateT, DepsT]` | Holds `ctx.state` and `ctx.deps` during execution. |
| `GraphBuilder[StateT, DepsT, InputT, OutputT]` | Builder for constructing executable graphs. |
| `Graph[StateT, DepsT, InputT, OutputT]` | Ready-to-run graph. |

### Simple Node

```python
from dataclasses import dataclass
from pydantic_graph import BaseNode, GraphRunContext

@dataclass
class MyNode(BaseNode[MyState]):          # State generic parameter
    foo: int                               # Node parameters (dataclass fields)

    async def run(self, ctx: GraphRunContext[MyState]) -> AnotherNode:
        # Business logic
        ctx.state.counter += 1
        return AnotherNode()               # Return type = next node
```

### Node That Can End the Graph

```python
@dataclass
class MaybeEndNode(BaseNode[MyState, None, int]):  # RunEndT = int
    foo: int

    async def run(self, ctx: GraphRunContext[MyState]) -> AnotherNode | End[int]:
        if self.foo % 5 == 0:
            return End(self.foo)           # End with value int
        return AnotherNode(self.foo + 1)
```

### Full Graph Example

```python
from __future__ import annotations
from dataclasses import dataclass
from pydantic_graph import BaseNode, End, GraphBuilder, GraphRunContext, StepContext

@dataclass
class DivisibleBy5(BaseNode[None, None, int]):
    foo: int
    async def run(self, ctx: GraphRunContext) -> Increment | End[int]:
        if self.foo % 5 == 0:
            return End(self.foo)
        return Increment(self.foo)

@dataclass
class Increment(BaseNode):
    foo: int
    async def run(self, ctx: GraphRunContext) -> DivisibleBy5:
        return DivisibleBy5(self.foo + 1)

g = GraphBuilder(input_type=int, output_type=int)

@g.step
async def start(ctx: StepContext[None, None, int]) -> DivisibleBy5:
    return DivisibleBy5(ctx.inputs)

g.add(
    g.node(DivisibleBy5),
    g.node(Increment),
    g.edge_from(g.start_node).to(start),
)

graph = g.build()
result = await graph.run(inputs=4)
print(result)  # 5
```

### Stateful Graph Example

```python
from dataclasses import dataclass
from pydantic_graph import BaseNode, End, GraphBuilder, GraphRunContext, StepContext

@dataclass
class VendingState:
    user_balance: float = 0.0
    product: str | None = None

@dataclass
class InsertCoin(BaseNode[VendingState]):
    async def run(self, ctx: GraphRunContext[VendingState]) -> CoinsInserted:
        return CoinsInserted(float(input('Insert coins: ')))

@dataclass
class CoinsInserted(BaseNode[VendingState]):
    amount: float
    async def run(self, ctx: GraphRunContext[VendingState]) -> SelectProduct | Purchase:
        ctx.state.user_balance += self.amount
        if ctx.state.product:
            return Purchase(ctx.state.product)
        return SelectProduct()

g = GraphBuilder(state_type=VendingState)
@g.step
async def start(ctx: StepContext[VendingState, None, None]) -> InsertCoin:
    return InsertCoin()
g.add(
    g.node(InsertCoin), g.node(CoinsInserted),
    g.edge_from(g.start_node).to(start),
)
graph = g.build()
result = await graph.run(state=VendingState())
```

### Dependency Injection

```python
from dataclasses import dataclass
from pydantic_graph import BaseNode, End, GraphBuilder, GraphRunContext, StepContext

@dataclass
class GraphDeps:
    db_url: str

@dataclass
class QueryNode(BaseNode[None, GraphDeps, str]):
    async def run(self, ctx: GraphRunContext[None, GraphDeps]) -> End[str]:
        return End(f"Connected to {ctx.deps.db_url}")

g = GraphBuilder(deps_type=GraphDeps, output_type=str)
@g.step
async def start(ctx: StepContext[None, GraphDeps, None]) -> QueryNode:
    return QueryNode()
g.add(g.node(QueryNode), g.edge_from(g.start_node).to(start))
graph = g.build()
result = await graph.run(deps=GraphDeps(db_url='postgres://...'))
```

### GenAI Example (Agent Inside Graph)

```python
from dataclasses import dataclass
from pydantic_ai import Agent
from pydantic_graph import BaseNode, End, GraphBuilder, GraphRunContext, StepContext

@dataclass
class State:
    messages: list = None

email_writer = Agent('openai:gpt-5.2', output_type=str,
    instructions='Write a welcome email.')
feedback_agent = Agent('openai:gpt-5.2', output_type=str,
    instructions='Review the email and provide feedback.')

@dataclass
class WriteEmail(BaseNode[State]):
    feedback: str | None = None
    async def run(self, ctx: GraphRunContext[State]) -> Feedback:
        prompt = f"Write email. Feedback: {self.feedback}" if self.feedback else "Write welcome email."
        result = await email_writer.run(prompt)
        return Feedback(result.output)

@dataclass
class Feedback(BaseNode[State, None, str]):
    email: str
    async def run(self, ctx: GraphRunContext[State]) -> WriteEmail | End[str]:
        result = await feedback_agent.run(f"Review: {self.email}")
        if 'approve' in result.output.lower():
            return End(self.email)
        return WriteEmail(feedback=result.output)

g = GraphBuilder(state_type=State, output_type=str)
@g.step
async def start(ctx: StepContext[State, None, None]) -> WriteEmail:
    return WriteEmail()
g.add(g.node(WriteEmail), g.node(Feedback), g.edge_from(g.start_node).to(start))
graph = g.build()
```

### Mermaid Diagrams

```python
print(graph)
# or
mermaid = graph.render(title='My Graph', direction='LR')  # TB, LR, RL, BT
```

### Step-by-step execution with iter()

```python
async with graph.iter(state=state) as run:
    async for event in run:
        print(f"Node: {event}")
        if run.output is not None:
            break
```

---

## API 2: GraphBuilder (Function-based)

The builder API provides concise syntax with parallel execution primitives.

### Simple Chain

```python
from dataclasses import dataclass
from pydantic_graph import GraphBuilder, StepContext

@dataclass
class CounterState:
    value: int = 0

g = GraphBuilder(state_type=CounterState, output_type=int)

@g.step
async def increment(ctx: StepContext[CounterState, None, None]) -> int:
    ctx.state.value += 1
    return ctx.state.value

@g.step
async def double_it(ctx: StepContext[CounterState, None, int]) -> int:
    return ctx.inputs * 2

g.add(
    g.edge_from(g.start_node).to(increment),
    g.edge_from(increment).to(double_it),
    g.edge_from(double_it).to(g.end_node),
)

graph = g.build()
result = await graph.run(state=CounterState())
```

### Parallel Processing with Map

```python
from pydantic_graph import GraphBuilder, StepContext, reduce_list_append

g = GraphBuilder(state_type=CounterState, input_type=list[int], output_type=list[int])

@g.step
async def square(ctx: StepContext[CounterState, None, int]) -> int:
    ctx.state.items_processed += 1
    return ctx.inputs * ctx.inputs

collect = g.join(reduce_list_append, initial_factory=list[int])

g.add(
    g.edge_from(g.start_node).map().to(square),        # Fan-out: one per input item
    g.edge_from(square).to(collect),                    # Collect results
    g.edge_from(collect).to(g.end_node),
)

graph = g.build()
result = await graph.run(state=CounterState(), inputs=[1, 2, 3])
```

### Parallel with Broadcast

```python
# Same input goes to multiple parallel paths
g.edge_from(g.start_node).broadcast().to(square, cube, sqrt)
```

### Decisions (Conditional Branching)

```python
# Use a decision node to route based on a condition
g.edge_from(check_node).to(
    on_true=process_positive,
    on_false=process_negative,
)
```

### Joins and Reducers

| Reducer | Behavior |
|---|---|
| `reduce_list_append` | Collect items into list |
| `reduce_list_extend` | Extend list with items |
| `reduce_sum` | Sum numeric values |
| `reduce_dict_update` | Merge dicts |
| `reduce_first_value` | Take first value |
| `reduce_null` | Discard values |

```python
my_join = g.join(reduce_sum, initial_factory=lambda: 0)
```

## StepContext Fields

| Field | Type | Description |
|---|---|---|
| `ctx.state` | `StateT` | Mutable shared state |
| `ctx.deps` | `DepsT` | Injected dependencies |
| `ctx.inputs` | `InputT` | Input data for this step |

## Graph generics

`GraphBuilder` is generic over `[StateT, DepsT, InputT, OutputT]`:
- Omit `state_type` for stateless graphs (defaults to `None`)
- Omit `deps_type` for dependency-free graphs
- Omit `input_type`/`output_type` for simple graphs

## Comparison: BaseNode vs GraphBuilder

| Aspect | BaseNode API | GraphBuilder API |
|---|---|---|
| Style | Class-based (OO) | Function-based (builder pattern) |
| State mutation | Via dataclass fields + `ctx.state` | Via `ctx.state` |
| Parallelism | Manual fork/join | Built-in `.map()`, `.broadcast()`, joins |
| Complexity | Better for complex node logic | Better for simple linear flows |
| Graph structure | Inferred from `run()` return types | Explicit via `g.edge_from()` |
