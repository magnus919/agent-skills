# Complete Worked Examples

## Example 1: Bank Support Agent

Complete agent with dependencies, structured output, tools, and streaming.

```python
from dataclasses import dataclass
from pydantic import BaseModel, Field
from pydantic_ai import Agent, RunContext

# --- Dependencies ---
@dataclass
class SupportDeps:
    customer_id: int
    db: dict  # Mock database

# --- Output Type ---
class SupportResult(BaseModel):
    support_advice: str = Field(description='Advice for the customer')
    block_card: bool = Field(description='Whether to block card')
    risk: int = Field(description='Risk level 0-10', ge=0, le=10)

# --- Agent ---
support_agent = Agent(
    'openai:gpt-5.2',
    deps_type=SupportDeps,
    output_type=SupportResult,
    system_prompt='You are a bank support agent. Be helpful and assess risk.',
)

@support_agent.tool
async def get_balance(ctx: RunContext[SupportDeps]) -> float:
    """Get the customer's current account balance."""
    return ctx.deps.db.get('balance', 0.0)

@support_agent.tool
async def recent_transactions(ctx: RunContext[SupportDeps], limit: int = 5) -> list[str]:
    """Get recent transactions."""
    return ctx.deps.db.get('transactions', [])[:limit]

# --- Run ---
async def main():
    deps = SupportDeps(customer_id=123, db={
        'balance': 1500.00,
        'transactions': ['Amazon -$42.00', 'Paycheck +$2000.00'],
    })
    result = await support_agent.run('I lost my card!', deps=deps)
    print(result.output.support_advice)
    print(f"Block card: {result.output.block_card}, Risk: {result.output.risk}")
```

## Example 2: Weather Agent with Streaming Events

Full streaming visibility into tool calls and responses.

```python
from datetime import date
from pydantic_ai import (
    Agent, RunContext,
    PartStartEvent, PartDeltaEvent,
    FunctionToolCallEvent, FunctionToolResultEvent,
    FinalResultEvent, TextPartDelta, ToolCallPartDelta,
)

weather_agent = Agent(
    'openai:gpt-5.2',
    system_prompt='Providing weather forecasts.',
)

@weather_agent.tool
async def get_forecast(ctx: RunContext, location: str, forecast_date: date) -> str:
    """Get weather forecast for a location on a date."""
    return f'The forecast in {location} on {forecast_date} is 24°C and sunny.'

async def main():
    async with weather_agent.run_stream_events(
        'What is the weather in Paris on Tuesday?'
    ) as events:
        async for event in events:
            if isinstance(event, FunctionToolCallEvent):
                print(f"[Tool Call] {event.part.tool_name}({event.part.args})")
            elif isinstance(event, FunctionToolResultEvent):
                print(f"[Tool Result] {event.part.content}")
            elif isinstance(event, PartStartEvent):
                print(f"[Part Start] {type(event.part).__name__}")
            elif isinstance(event, PartDeltaEvent):
                if isinstance(event.delta, TextPartDelta):
                    print(f"[Text] {event.delta.content_delta}", end='')
            elif isinstance(event, FinalResultEvent):
                print(f"\n[Final Result Starting]")
```

## Example 3: Vending Machine (PydanticGraph Stateful)

Complete stateful graph with user interaction.

```python
from __future__ import annotations
from dataclasses import dataclass
from pydantic_graph import BaseNode, End, GraphBuilder, GraphRunContext, StepContext

PRODUCTS = {'water': 1.25, 'soda': 1.50, 'crisps': 1.75, 'chocolate': 2.00}

@dataclass
class VendingState:
    balance: float = 0.0
    product: str | None = None

@dataclass
class InsertCoin(BaseNode[VendingState]):
    async def run(self, ctx: GraphRunContext[VendingState]) -> CoinInserted:
        return CoinInserted(1.00)  # Simulated coin insert

@dataclass
class CoinInserted(BaseNode[VendingState]):
    amount: float
    async def run(self, ctx: GraphRunContext[VendingState]) -> SelectProduct | Purchase:
        ctx.state.balance += self.amount
        if ctx.state.product:
            return Purchase(ctx.state.product)
        return SelectProduct()

@dataclass
class SelectProduct(BaseNode[VendingState]):
    async def run(self, ctx: GraphRunContext[VendingState]) -> Purchase:
        return Purchase('soda')  # Simulated selection

@dataclass
class Purchase(BaseNode[VendingState, None, None]):
    product: str
    async def run(self, ctx: GraphRunContext[VendingState]) -> End | InsertCoin | SelectProduct:
        price = PRODUCTS.get(self.product)
        if not price:
            print(f"No such product: {self.product}")
            return SelectProduct()
        ctx.state.product = self.product
        if ctx.state.balance >= price:
            ctx.state.balance -= price
            print(f"Dispensing {self.product}. Change: ${ctx.state.balance:.2f}")
            return End(None)
        else:
            short = price - ctx.state.balance
            print(f"Need ${short:.2f} more for {self.product}")
            return InsertCoin()

g = GraphBuilder(state_type=VendingState)
@g.step
async def start(ctx: StepContext[VendingState, None, None]) -> InsertCoin:
    return InsertCoin()
g.add(g.node(InsertCoin), g.node(CoinInserted),
      g.node(SelectProduct), g.node(Purchase),
      g.edge_from(g.start_node).to(start))

async def main():
    result = await g.build().run(state=VendingState())
```

## Example 4: Parallel Processing Graph

Using GraphBuilder's map operation for parallel execution.

```python
from dataclasses import dataclass
from pydantic_graph import GraphBuilder, StepContext, reduce_list_append

@dataclass
class State:
    processed: int = 0

g = GraphBuilder(state_type=State, input_type=list[int], output_type=list[int])

@g.step
async def double(ctx: StepContext[State, None, int]) -> int:
    ctx.state.processed += 1
    return ctx.inputs * 2

collect = g.join(reduce_list_append, initial_factory=list[int])

g.add(
    g.edge_from(g.start_node).map().to(double),   # Parallel fan-out
    g.edge_from(double).to(collect),               # Gather results
    g.edge_from(collect).to(g.end_node),
)

async def main():
    state = State()
    result = await g.build().run(state=state, inputs=[1, 2, 3, 4, 5])
    print(result)        # [2, 4, 6, 8, 10]
    print(state.processed)  # 5
```

## Example 5: Multi-Agent Flight Booking

Programmatic hand-off between two agents with shared usage tracking.

```python
from pydantic import BaseModel
from pydantic_ai import Agent, RunUsage

class Flight(BaseModel):
    airline: str
    flight_number: str
    price: float

class Booking(BaseModel):
    flight: Flight
    seat: str
    confirmed: bool

search_agent = Agent('openai:gpt-5.2', output_type=Flight,
    instructions='Search for the best flight matching criteria.')
book_agent = Agent('openai:gpt-5.2', output_type=Booking,
    instructions='Book the specified flight with the given seat preference.')

async def book_flight(origin: str, dest: str, date: str, seat: str) -> Booking:
    usage = RunUsage()
    flight_result = await search_agent.run(
        f'Find a flight from {origin} to {dest} on {date}',
        usage=usage,
    )
    booking_result = await book_agent.run(
        f'Book flight {flight_result.output.flight_number}, seat {seat}',
        usage=usage,
        message_history=flight_result.new_messages(),
    )
    return booking_result.output
```

## Example 6: RAG with Embeddings

```python
from pydantic_ai import Agent, Embedder, RunContext

embedder = Embedder('openai:text-embedding-3-small')
rag_agent = Agent('openai:gpt-5.2')

@rag_agent.tool
async def search_docs(ctx: RunContext, query: str) -> str:
    """Search documentation for relevant context."""
    query_vec = await embedder.embed_query(query)
    results = vector_db.search(query_vec.embeddings[0], top_k=3)
    return '\n'.join(results)

result = rag_agent.run_sync('How do I configure authentication?')
```
