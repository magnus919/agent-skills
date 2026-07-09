# Capabilities & Hooks System

Capabilities are the primary extension mechanism in PydanticAI. They bundle tools, lifecycle hooks, instructions, and model settings into reusable, composable units.

## Built-in Capabilities

| Capability | Purpose |
|---|---|
| `Thinking` | Enable extended reasoning/reasoning effort |
| `WebSearch` | Add web search tool (DuckDuckGo, Tavily, Exa, or provider-native) |
| `WebFetch` | Add web page fetch tool |
| `MCP` | Connect to MCP server tools |
| `Hooks` | Register lifecycle hooks (logging, metrics, validation) |
| `Instrumentation` | OpenTelemetry/Logfire instrumentation |
| `ToolSearch` | Enable tool search/progressive discovery |
| `ProcessHistory` | Hook into message history processing |
| `ReinjectSystemPrompt` | Re-inject system prompt on each request |
| `NativeTool` | Attach provider-native tools (code exec, image gen, etc.) |
| `HandleDeferredToolCalls` | Approve/deny deferred tool calls |
| `ImageGeneration` | Add image generation tool |
| `PrefixTools` | Prefix tool names (for multi-agent routing) |
| `PrepareTools` | Modify tool definitions per step |
| `PrepareOutputTools` | Modify output tool definitions per step |
| `SetToolMetadata` | Set metadata on tool definitions |
| `ThreadExecutor` | Use thread pool for tool execution |
| `ProcessEventStream` | Transform the event stream |
| `XSearch` | X/Twitter search tool |
| `WrapperCapability` | Wrap another capability |
| `CombinedCapability` | Compose multiple capabilities into one |
| `DynamicCapability` | Wrap a callable capability factory |
| `NativeOrLocalTool` | Try native tool, fall back to local function |

## Using Capabilities

```python
from pydantic_ai import Agent
from pydantic_ai.capabilities import Thinking, WebSearch

agent = Agent(
    'anthropic:claude-sonnet-4-6',
    capabilities=[
        Thinking(effort='high'),
        WebSearch(local='duckduckgo'),     # local = DuckDuckGo fallback
        # WebSearch(native=True),           # provider-native web search
    ],
)
```

## On-Demand (Deferred) Capabilities

Instead of sending every capability's tools and instructions on every turn, mark capabilities as `defer_loading=True`. They collapse to a one-line catalog entry the model loads on demand via the `load_capability` tool.

### Basic deferral
```python
from pydantic_ai import Agent
from pydantic_ai.capabilities import Capability

refunds = Capability(
    id='refunds',
    description='Use for refund eligibility, refund status, or processing a refund.',
    instructions='Always confirm the order ID before issuing a refund.',
    defer_loading=True,
)

@refunds.tool_plain
def refund_status(order_id: str) -> str:
    """Look up the refund status for an order."""
    return f'Order {order_id}: refund issued on 2025-05-01.'

agent = Agent(
    'openai-responses:gpt-5.4',
    instructions='You are a customer support assistant.',
    capabilities=[refunds],
)
```

The model sees in the catalog:
```
The following capabilities are deferred and can be loaded using the `load_capability` tool:
- refunds: Use for refund eligibility, refund status, or processing a refund.
```

### Deferring any capability
```python
from pydantic_ai.capabilities import MCP

agent = Agent(
    'openai-responses:gpt-5.4',
    capabilities=[
        MCP(
            url='https://mcp.example.com/analytics',
            native=True,
            id='analytics-mcp',
            description='Use for analytics queries.',
            defer_loading=True,
        ),
    ],
)
```

### What loads when

| Part | Before load | After load |
|---|---|---|
| Instructions (static/dynamic) | Not sent | Returned as tool result; included in subsequent requests |
| Function tools | Not exposed | Exposed on next request |
| Model settings | Not applied | Merged into run's settings |
| Lifecycle hooks | Do not fire | Fire after capability is loaded |
| Native tools | Not exposed | Exposed on next request |

### Resume across runs

Loaded-capability state lives in message history (the `load_capability` tool call/return pairs), not in the agent. When a conversation is resumed, previously loaded capabilities stay loaded — no re-discovery round-trip. Requires stable explicit `id` on each deferred capability.

### Runtime state in RunContext

```python
ctx.loaded_capability_ids      # Deferred IDs explicitly loaded
ctx.available_capability_ids   # Always-on + loaded IDs
ctx.capability_loaded          # True while running a capability-owned hook
```

## Building Custom Capabilities

### Simple: `Capability` convenience class
```python
from pydantic_ai import RunContext
from pydantic_ai.capabilities import Capability

my_cap = Capability(
    id='analytics',
    description='Database analytics queries.',
    instructions='Use the query tool for database lookups.',
)

@my_cap.tool
def query_db(ctx: RunContext[MyDeps], sql: str) -> list[dict]:
    """Run a SQL query."""
    return ctx.deps.db.execute(sql)

agent = Agent(model, capabilities=[my_cap])
```

`Capability` supports: `@cap.tool`, `@cap.tool_plain`, `@cap.instructions` (dynamic), `tools=`, `toolsets=`.

### Advanced: subclass `AbstractCapability`
```python
from dataclasses import dataclass
from typing import Any
from pydantic_ai import Agent, ModelSettings
from pydantic_ai.capabilities import AbstractCapability

@dataclass
class DeepReasoning(AbstractCapability[Any]):
    id: str = 'deep-reasoning'
    description: str = 'Use for multi-step planning or hard analytical problems.'
    defer_loading: bool = True

    def get_instructions(self) -> str:
        return 'Think step by step before answering.'

    def get_model_settings(self) -> ModelSettings:
        return ModelSettings(extra_body={'reasoning_effort': 'high'})

    async def before_tool_execute(self, ctx, *, call, tool_def, args):
        # Fires only after this capability is loaded
        return args
```

Overrideable methods: `get_instructions`, `get_model_settings`, `get_description`, `before_run`, `after_run`, `wrap_run`, `wrap_model_request`, `wrap_node_run`, `wrap_tool_validate`, `wrap_tool_execute`, `wrap_output_validate`, `wrap_output_process`, `prepare_tools`, `prepare_output_tools`, `handle_deferred_tool_calls`, `before_model_request`, `after_model_request`, etc.

### Custom capabilities in Agent Specs

```yaml
# agent.yaml
model: test
capabilities:
  - RateLimit:
      rpm: 30
```

```python
@dataclass
class RateLimit(AbstractCapability[Any]):
    rpm: int = 60
    # get_serialization_name() defaults to class name

agent = Agent.from_spec(
    AgentSpec(model='test', capabilities=[{'RateLimit': {'rpm': 30}}]),
    custom_capability_types=[RateLimit],
)
```

Override `from_spec` when constructor takes non-serializable types.

## Hooks System

The `Hooks` capability provides lightweight lifecycle hooks without subclassing.

### Creating hooks
```python
from pydantic_ai import Agent, RunContext
from pydantic_ai.capabilities import Hooks

hooks = Hooks()

@hooks.on.before_model_request
async def log_request(ctx, request_context):
    print(f"Sending {len(request_context.messages)} messages")
    return request_context

agent = Agent('test', capabilities=[hooks])
```

### All Hook Points

| Decorator | Fires |
|---|---|
| `@hooks.on.before_run` / `after_run` | Start/end of agent run |
| `@hooks.on.run` | Wrap entire run (supports error recovery) |
| `@hooks.on.run_error` | Run-level errors |
| `@hooks.on.before_node_run` / `after_node_run` | Each graph step |
| `@hooks.on.node_run` | Wrap node execution |
| `@hooks.on.node_run_error` | Node execution errors |
| `@hooks.on.before_model_request` | Before LLM call |
| `@hooks.on.after_model_request` | After LLM response |
| `@hooks.on.model_request` | Wrap LLM request |
| `@hooks.on.model_request_error` | LLM request errors |
| `@hooks.on.before_tool_validate` | Before tool arg validation |
| `@hooks.on.after_tool_validate` | After tool arg validation |
| `@hooks.on.tool_validate` | Wrap tool validation |
| `@hooks.on.tool_validate_error` | Tool validation errors |
| `@hooks.on.before_tool_execute` | Before tool execution |
| `@hooks.on.after_tool_execute` | After tool execution |
| `@hooks.on.tool_execute` | Wrap tool execution |
| `@hooks.on.tool_execute_error` | Tool execution errors |
| `@hooks.on.before_output_validate` | Before output validation |
| `@hooks.on.after_output_validate` | After output validation |
| `@hooks.on.output_validate` | Wrap output validation |
| `@hooks.on.output_validate_error` | Output validation errors |
| `@hooks.on.before_output_process` | Before output processing |
| `@hooks.on.after_output_process` | After output processing |
| `@hooks.on.output_process` | Wrap output processing |
| `@hooks.on.output_process_error` | Output processing errors |
| `@hooks.on.prepare_tools` | Filter/modify tool definitions |
| `@hooks.on.prepare_output_tools` | Filter/modify output tools |
| `@hooks.on.deferred_tool_calls` | Resolve deferred/approval calls |
| `@hooks.on.run_event_stream` | Wrap event stream |
| `@hooks.on.event` | Each individual stream event |

### Tool-targeted hooks
```python
@hooks.on.before_tool_execute(tools=['send_email'])
async def audit_dangerous(ctx, *, call, tool_def, args):
    call_log.append(f'audit: {call.tool_name}')
    return args
```

### Hook timeouts
```python
@hooks.on.before_model_request(timeout=5.0)
async def safe_hook(ctx, request_context):
    return request_context  # raises HookTimeoutError if >5s
```

### Skip model request entirely
```python
from pydantic_ai.exceptions import SkipModelRequest

@hooks.on.before_model_request
async def cache_hit(ctx, request_context):
    if cached := cache.get(request_context.messages):
        raise SkipModelRequest(cached)
    return request_context
```

### Hook ordering
- `before_*` hooks fire in registration order
- `after_*` hooks fire in reverse registration order
- `wrap_*` hooks nest as middleware (first registered = outermost)

## Third-Party Capabilities

Community capabilities available:
- `pydantic-ai-todo` — Task planning `TodoCapability` with subtasks, dependencies, PostgreSQL
- `subagents-pydantic-ai` — Multi-agent delegation (`SubAgentCapability`)
- `pydantic-ai-shields` — Guardrails: cost tracking, tool guard, input/output guard, PII detection
- `pydantic-ai-backend` — Filesystem/sandboxed code execution (`ConsoleCapability`)
- `pydantic-ai-skills` — Agent Skills support with progressive disclosure
- `summarization-pydantic-ai` — Long conversation management capabilities

## Publishing Capabilities

1. Implement `get_serialization_name()` — defaults to class name
2. Implement `from_spec()` — defaults to `cls(*args, **kwargs)`
3. Package naming: `pydantic-ai-*` prefix
4. Users register via `custom_capability_types=[MyCapability]` on `from_spec`/`from_file`
