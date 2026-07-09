# Multi-Agent Patterns & Integrations

## Agent Delegation

One agent calls another agent through a tool. The delegate runs and returns control.

```python
from pydantic_ai import Agent, RunContext

joke_selector = Agent('openai:gpt-5.2', name='joke_selector',
    instructions='Use joke_factory to generate jokes, then pick the best.')
joke_generator = Agent('google:gemini-3-flash-preview', name='joke_generator',
    output_type=list[str],
    instructions='Generate funny jokes on the given topic.')

@joke_selector.tool
async def joke_factory(ctx: RunContext, count: int) -> list[str]:
    r = await joke_generator.run(
        f'Generate {count} jokes.',
        usage=ctx.usage,          # Pass usage for unified tracking
    )
    return r.output

result = joke_selector.run_sync('Tell me a joke.',
    usage_limits=UsageLimits(request_limit=5))
```

### Key points:
- Agents are stateless and designed to be global — pass to tools, not deps
- Pass `usage=ctx.usage` so delegate usage counts toward parent limits
- Delegates can use different models than the parent
- Passing `name=` is recommended for Logfire trace clarity

### Shared Dependencies Pattern

```python
@dataclass
class ClientAndKey:
    http_client: httpx.AsyncClient
    api_key: str

parent_agent = Agent('openai:gpt-5.2', deps_type=ClientAndKey)
child_agent = Agent('google:gemini-3-flash-preview', deps_type=ClientAndKey)

@parent_agent.tool
async def delegate_task(ctx: RunContext[ClientAndKey]) -> list[str]:
    r = await child_agent.run('Do something', deps=ctx.deps, usage=ctx.usage)
    return r.output
```

## Programmatic Agent Hand-Off

Multiple agents called in sequence by application code, with human-in-the-loop:

```python
from pydantic import BaseModel
from pydantic_ai import Agent, RunUsage

class FlightDetails(BaseModel):
    flight_number: str

flight_agent = Agent('openai:gpt-5.2', output_type=FlightDetails)

async def find_flight(usage: RunUsage) -> FlightDetails | None:
    prompt = input('Where to? ')
    result = await flight_agent.run(prompt, usage=usage)
    if isinstance(result.output, FlightDetails):
        return result.output
    return None

class SeatPref(BaseModel):
    row: int
    seat: str

seat_agent = Agent('openai:gpt-5.2', output_type=SeatPref)

async def find_seat(usage: RunUsage) -> SeatPref:
    answer = input('What seat? ')
    result = await seat_agent.run(answer, usage=usage)
    return result.output

async def main():
    usage = RunUsage()
    flight = await find_flight(usage)
    seat = await find_seat(usage)
    print(f'Booked {flight.flight_number}, seat {seat.seat}{seat.row}')
```

### Sharing Messages Between Agents

```python
result1 = flight_agent.run_sync('Find a flight to Paris')
result2 = seat_agent.run_sync(
    'Window seat please',
    message_history=result1.new_messages(),  # Pass conversation context
)
```

## Graph-Based Multi-Agent (PydanticGraph)

For complex workflows, use pydantic-graph to orchestrate agents:

```python
from dataclasses import dataclass
from pydantic_ai import Agent
from pydantic_graph import BaseNode, End, GraphBuilder, GraphRunContext, StepContext

writer = Agent('openai:gpt-5.2', output_type=str, instructions='Write a welcome email.')
reviewer = Agent('openai:gpt-5.2', output_type=str, instructions='Review the email.')

@dataclass
class State:
    user_name: str
    email_content: str = ''
    review_count: int = 0

@dataclass
class WriteEmail(BaseNode[State]):
    feedback: str | None = None
    async def run(self, ctx: GraphRunContext[State]) -> ReviewEmail:
        prompt = f"Write welcome email for {ctx.state.user_name}"
        if self.feedback:
            prompt += f"\nFeedback to address: {self.feedback}"
        result = await writer.run(prompt)
        ctx.state.email_content = result.output
        return ReviewEmail()

@dataclass
class ReviewEmail(BaseNode[State, None, str]):
    async def run(self, ctx: GraphRunContext[State]) -> WriteEmail | End[str]:
        result = await reviewer.run(f"Review this email:\n{ctx.state.email_content}")
        if ctx.state.review_count >= 3:
            return End(ctx.state.email_content)
        ctx.state.review_count += 1
        return WriteEmail(feedback=result.output)
```

## Deep Agent Patterns

Combine capabilities for autonomous agents:
- **Planning & progress tracking** — `pydantic-ai-todo` capability
- **File system operations** — `pydantic-ai-backend` ConsoleCapability
- **Task delegation** — `subagents-pydantic-ai` SubAgentCapability
- **Sandboxed code execution** — MCP server `mcp-run-python`
- **Context management** — `summarization-pydantic-ai` capabilities
- **Human-in-the-loop** — `HandleDeferredToolCalls` / deferred tools
- **Durable execution** — Temporal/Inngest/Prefect/DBOS integrations

## MCP (Model Context Protocol)

### MCP Capability (Recommended)

```python
from pydantic_ai import Agent
from pydantic_ai.capabilities import MCP

agent = Agent(
    'openai:gpt-5.2',
    capabilities=[
        MCP(url='https://mcp.example.com/api'),          # Local fallback
        MCP(url='https://mcp.example.com/native', native=True),  # Provider-native
    ],
)
```

`MCP` accepts: URL string, FastMCP transport, pre-built `fastmcp.Client`, in-process `FastMCP` server, or local script path.

### MCPToolset (Lower-Level)

```python
from pydantic_ai.mcp import MCPToolset

toolset = MCPToolset(url='https://mcp.example.com/api')
agent = Agent('openai:gpt-5.2', toolsets=[toolset])
```

### MCPServerTool (Native Only)

```python
from pydantic_ai.native_tools import MCPServerTool

agent = Agent('openai-responses:gpt-5.4', tools=[
    MCPServerTool(url='https://mcp.example.com/fs'),
])
```

### Building MCP Servers

See pydantic docs on [MCP server implementation](https://pydantic.dev/docs/ai/mcp/server).

## Durable Execution

PydanticAI supports four official durable execution solutions that preserve agent progress across failures and restarts:

- **Temporal** — `pydantic-ai-slim[temporal]`
- **Inngest** — `pydantic-ai-slim[inngest]`
- **Prefect** — `pydantic-ai-slim[prefect]`
- **DBOS** — `pydantic-ai-slim[dbos]`

These are co-maintained with the respective vendors and use PydanticAI's public interface.

## Web Chat UI

Two supported UI event stream protocols:

### Vercel AI SDK
```python
from fastapi import FastAPI
from starlette.requests import Request
from pydantic_ai import Agent
from pydantic_ai.ui.vercel_ai import VercelAIAdapter

agent = Agent('openai:gpt-5.2')
app = FastAPI()

@app.post('/chat')
async def chat(request: Request):
    return await VercelAIAdapter.dispatch_request(request, agent=agent)
```

### AG-UI (Microsoft)
```python
from pydantic_ai.ui.ag_ui import AGUIAdapter
return await AGUIAdapter.dispatch_request(request, agent=agent)
```

## Embeddings

```python
from pydantic_ai import Embedder

embedder = Embedder('openai:text-embedding-3-small')

result = await embedder.embed_query('What is machine learning?')
print(len(result.embeddings[0]))     # 1536 dimensions
print(result.usage.input_tokens)     # Token count

docs = ['Doc 1', 'Doc 2']
result = await embedder.embed_documents(docs)
print(result['Doc 1'])              # Access by text
```

Supported providers: OpenAI, Google, Cohere, VoyageAI, Bedrock, Sentence Transformers.
Dimension control: `EmbeddingSettings(dimensions=256)` (OpenAI & Google).
Two-stage retrieval: embedding model for broad recall, cross-encoder reranker for precision.
