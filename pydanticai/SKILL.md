---
name: pydanticai
description: >-
  Build type-safe AI agents and graph-based workflows with PydanticAI and
  PydanticGraph. Agent creation, function tools, capabilities, dependency
  injection, structured output, streaming, multi-agent patterns, testing,
  evals, and graph state machines. Use whenever you are building agents,
  tool-using LLM workflows, or graph-based state machines in Python.
license: MIT
metadata:
  source: https://pydantic.dev/docs/ai/overview/
  version: "1.0.3"
compatibility: Python 3.10+; requires pydantic-ai or pydantic-ai-slim package
---

# PydanticAI & PydanticGraph Expert Skill

PydanticAI is a Python agent framework for building production-grade GenAI applications, built by the team behind Pydantic. PydanticGraph is its companion graph/state-machine library.

**Install:**
```bash
pip install pydantic-ai               # Full install (all providers)
pip install "pydantic-ai-slim[openai]" # Minimal install + your provider
```

## Quick Reference

```python
from pydantic_ai import Agent

# Basic agent — one line
agent = Agent('openai:gpt-5.2', instructions='Be concise.')

# Run it
result = agent.run_sync('What is the capital of France?')
print(result.output)
```

## When to Load Which Reference

| Topic | Load When | File |
|---|---|---|
| **Agent creation & lifecycle** | You need to create, configure, or run an agent — define tools, deps, output types, run methods, streaming | `references/core-agents.md` |
| **Capabilities & hooks** | You need built-in capabilities (Thinking, WebSearch, MCP, etc.), on-demand loading, lifecycle hooks, or custom capabilities | `references/capabilities-hooks.md` |
| **PydanticGraph** | You need a state machine, graph-based control flow, parallel execution, BaseNode subclasses, or GraphBuilder with joins/decisions | `references/graph.md` |
| **Models, output & streaming** | You need multi-model setups, FallbackModel, streaming output, output functions, or structured output with validation | `references/models-output.md` |
| **Multi-agent patterns & integrations** | You need agent delegation, programmatic hand-off, MCP servers, durable execution, or UI adapters | `references/patterns.md` |
| **Testing & evaluation** | You need TestModel, FunctionModel, pytest patterns, overrides, or Pydantic Evals for systematic eval | `references/testing-evals.md` |
| **Full worked examples** | You want complete runnable examples — bank support agent, email feedback graph, multi-agent flight booking | `references/examples.md` |
| **API surface reference** | You need to find the right import path, class name, or method signature quickly | `references/api-reference.md` |

## Common Patterns at a Glance

### Agent with tools and structured output
```python
from pydantic import BaseModel
from pydantic_ai import Agent, RunContext

class WeatherResult(BaseModel):
    temperature: float
    conditions: str

agent = Agent('openai:gpt-5.2', output_type=WeatherResult)

@agent.tool
async def get_weather(ctx: RunContext, city: str) -> str:
    """Get current weather for a city."""
    return f"24°C and sunny in {city}"

result = agent.run_sync('Weather in London?')
print(result.output.temperature)
```
→ See `references/core-agents.md` for full agent lifecycle, run methods, and tool patterns.

### Agent with dependency injection
```python
from dataclasses import dataclass
from pydantic_ai import Agent, RunContext

@dataclass
class MyDeps:
    api_key: str
    db_conn: str

agent = Agent('openai:gpt-5.2', deps_type=MyDeps)

@agent.tool
async def query_db(ctx: RunContext[MyDeps], sql: str) -> str:
    return f"Query results using {ctx.deps.db_conn}"
```
→ See `references/core-agents.md` for dependency injection patterns and testing overrides.

### Graph with multiple nodes
```python
from dataclasses import dataclass
from pydantic_graph import BaseNode, End, GraphRunContext, GraphBuilder

@dataclass
class MyState:
    value: int = 0

@dataclass
class ProcessNode(BaseNode[MyState]):
    async def run(self, ctx: GraphRunContext[MyState]) -> End | NextNode:
        ctx.state.value += 1
        if ctx.state.value >= 5:
            return End(ctx.state.value)
        return NextNode()
```
→ See `references/graph.md` for both BaseNode and GraphBuilder APIs, parallel execution, and join/reducer patterns.

### When to use which run method

| When you need… | Use | Key behavior |
|---|---|---|
| A single answer, sync code | `run_sync()` | Blocks until complete, returns `RunResult` |
| A single answer, async code | `run()` | Async, returns `RunResult` |
| Stream text as it's generated | `run_stream()` | Async context manager, yields `stream_text()` / `stream_output()` |
| See granular events (tool calls, part starts, deltas) | `run_stream_events()` | Yields `AgentStreamEvent` types — `FunctionToolCallEvent`, `PartStartEvent`, `FinalResultEvent` |
| Manual control over each graph step | `iter()` | Iterate over agent's internal graph nodes (`UserPromptNode` → `ModelRequestNode` → `CallToolsNode`) |
| Tool calls to execute during streaming | `run_stream_events()` or `run(event_stream_handler=...)` | `run_stream()` stops at the first output that matches `output_type` and does NOT execute subsequent tool calls |

*Details for each run method in `references/core-agents.md`.*

### Graph API: BaseNode vs GraphBuilder

| Factor | BaseNode (class-based) | GraphBuilder (function-based) |
|---|---|---|
| Style | Subclass `BaseNode[StateT]`, implement `async run()` | Decorate async functions with `@g.step` |
| State mutation | Via `ctx.state` inside `run()` method | Via `ctx.state` inside step function |
| Parallelism | Manual fork/join logic | Built-in `.map()` per-element fan-out and `.broadcast()` same-input-to-multiple |
| Joins / aggregation | Manual aggregation in return types | Built-in reducers: `reduce_list_append`, `reduce_sum`, `reduce_dict_update`, etc. |
| Edge declaration | Inferred from `run()` return type annotation | Explicit via `g.edge_from(source).to(target)` |
| When to use | Complex node logic, OO patterns, conditional edge logic | Simple linear flows, parallel data processing, concise syntax |

*Both APIs in `references/graph.md`.*

### Error handling quick-pick

```python
from pydantic_ai import UnexpectedModelBehavior, capture_run_messages

with capture_run_messages() as messages:
    try:
        result = agent.run_sync('Query')
    except UnexpectedModelBehavior as e:
        cause = e.__cause__  # Often ModelRetry('reason')
        print(f"Root cause: {cause}")
        print("Full conversation:", messages)  # Inspect every message
        # Common recovery: raise ModelRetry from tools with clear instructions
```

| Exception | Meaning | Recovery |
|---|---|---|
| `UnexpectedModelBehavior` | Retry limit exceeded or model gave unexpected response | Inspect `e.__cause__`, check messages, adjust instructions or tool retries |
| `ModelRetry` (raised from tools) | Tool wants model to retry with different args | Let it propagate — PydanticAI handles it automatically up to `retries` limit |
| `ModelAPIError` | Provider returned 4xx/5xx | Check API key, rate limits, model availability |
| `UsageLimitExceeded` | Token/request budget exhausted | Increase `UsageLimits` or optimize prompt |
| `HookTimeoutError` | A lifecycle hook timed out | Increase hook timeout or optimize hook logic |

## Key CLI Commands

```bash
pip install pydantic-ai                    # Everything
pip install "pydantic-ai-slim[openai]"      # Minimal
pip install "pydantic-ai-slim[openai,google,anthropic]"  # Multi-provider
```

## Directory Structure

```
pydanticai/
├── SKILL.md
├── references/
│   ├── core-agents.md         # Agent lifecycle, tools, deps, output
│   ├── capabilities-hooks.md  # Capabilities system & lifecycle hooks
│   ├── graph.md               # PydanticGraph (BaseNode + GraphBuilder)
│   ├── models-output.md       # Models, streaming, structured output
│   ├── patterns.md            # Multi-agent patterns & integrations
│   ├── testing-evals.md       # Testing & evaluation framework
│   ├── examples.md            # Complete worked examples
│   └── api-reference.md       # Quick API surface reference
```

## Gotchas

- **Output type = final only:** The `output_type` constrains the *final* response. The model can still call tools (function tools) mid-run. Output functions are different — they're forced to be called and end the run.
- **pydantic-graph has zero dependency on pydantic-ai:** It's a standalone library. You can use it for non-GenAI state machines. Install with `pip install pydantic-graph`.
- **`pydantic-ai-slim` vs `pydantic-ai`:** The slim package ships only core deps + OpenTelemetry. The full `pydantic-ai` is a meta-package that adds openai, anthropic, google, cli, mcp, evals, web, retries, and logfire extras.
- **Tool calls during streaming by default DON'T execute:** `run_stream()` stops at the first output that matches the output type. Use `run_stream_events()` or `run()` with `event_stream_handler` to keep tool calls executing.
- **System prompt ≠ instructions:** System prompts are part of message history and round-trip. Instructions are server-side and don't appear in messages sent to clients. When reusing `message_history`, the agent's new system prompt won't automatically be sent unless you add `ReinjectSystemPrompt`.
- **`conversation_id` is manual for forking:** Pass `conversation_id='new'` to start a fresh conversation chain from existing history. It's not automatic.
- **Models named `provider:model_name`** — PydanticAI auto-resolves the model class from the string prefix. For custom endpoints, use `OpenAIChatModel(model_name, provider=OpenAIProvider(base_url=...))`.
- **`TestModel` can't emulate native tools:** Override with `agent.override(model=TestModel(), native_tools=[])` in tests if your agent uses WebSearch, etc.
- **`defer_model_check=True` for testable module-level agents:** When declaring an `Agent` at module level (outside a function) and using `TestModel` in tests with `agent.override(model=TestModel())`, set `defer_model_check=True` on the constructor. Without it, the agent tries to resolve the model string at import time — which fails without API credentials, even though the real model is overridden before any test runs.
- **Message history requires pairing:** When slicing history, tool calls and their returns must stay paired or the LLM will error.
- **`stream_text()` fails with BaseModel output types:** When `output_type` is a BaseModel (structured output), calling `result.stream_text()` raises `UserError('stream_text() can only be used with text responses')`. Use `result.stream_output()` instead to get partial validated objects as they stream in. If you need text-level streaming with structured output, use `run_stream_events()` and inspect `PartDeltaEvent` with `TextPartDelta` deltas. The two methods serve different output modes — text output → `stream_text()`, structured output → `stream_output()`.
- **`graph.run()` returns OutputT, NOT the state object:** Despite passing `state=MyState()` to `graph.run()`, the return value is the graph's `output_type` (e.g. `list[int]`), not the state. The `state` object IS mutated in-place during execution (since it's a mutable dataclass), so keep a separate reference:

  ```python
  state = MyState(items_processed=0)
  result = await graph.run(state=state, inputs=[1, 2, 3])
  # result -> [2, 4, 6]       (OutputT = list[int])
  # state.items_processed -> 3 (state mutated in-place)
  ```

  This trap is most common with parallel `.map()` patterns where the reader assumes `result.items_processed` will work. It won't. The `items_processed` count lives on the state object you passed in, not on the return value.
