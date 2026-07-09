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
  version: "1.0.0"
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
- **Message history requires pairing:** When slicing history, tool calls and their returns must stay paired or the LLM will error.
