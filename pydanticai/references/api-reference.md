# API Surface Quick Reference

## Common Imports

```python
from pydantic_ai import Agent, RunContext, Tool
from pydantic_ai import ModelRetry, UnexpectedModelBehavior, capture_run_messages
from pydantic_ai import ModelSettings, UsageLimits, RunUsage, RequestUsage
from pydantic_ai import AgentRetries, EndStrategy
from pydantic_ai import format_as_xml, TemplateStr
from pydantic_ai import AgentRunResult, StreamedRunResult
from pydantic_ai import AgentSpec, AgentStreamEvent
from pydantic_ai import (
    PartStartEvent, PartDeltaEvent,
    FunctionToolCallEvent, FunctionToolResultEvent,
    FinalResultEvent, AgentRunResultEvent,
    TextPartDelta, ToolCallPartDelta, ThinkingPartDelta,
)
from pydantic_ai.capabilities import (
    Thinking, WebSearch, MCP, Hooks, Capability,
    AbstractCapability, Instrumentation, ProcessHistory,
    ReinjectSystemPrompt, ToolSearch,
)
from pydantic_ai.messages import (
    ModelMessage, ModelRequest, ModelResponse,
    UserPromptPart, SystemPromptPart, TextPart,
    ToolCallPart, ToolReturnPart, RetryPromptPart,
    ThinkingPart, BinaryContent,
)
from pydantic_ai.models.test import TestModel
from pydantic_ai.models.function import FunctionModel, AgentInfo
from pydantic_ai.models.fallback import FallbackModel
from pydantic_ai.toolsets import (
    FunctionToolset, CombinedToolset, FilteredToolset,
    PrefixedToolset, RenamedToolset, PreparedToolset,
)
from pydantic_ai.mcp import MCPToolset
from pydantic_ai.embeddings import Embedder, EmbeddingSettings, EmbeddingResult
from pydantic_ai.exceptions import (
    ModelRetry, ModelAPIError, UserError,
    UsageLimitExceeded, UnexpectedModelBehavior,
)

# PydanticGraph
from pydantic_graph import (
    BaseNode, End, GraphRunContext, GraphBuilder,
    StepContext, Graph, GraphRun,
)
from pydantic_graph.join import (
    reduce_sum, reduce_list_append, reduce_list_extend,
    reduce_dict_update, reduce_first_value, reduce_null,
)
```

## Agent Constructor Parameters

| Parameter | Type | Default | Description |
|---|---|---|---|
| `model` | `str | Model | None` | `None` | Model ID or instance |
| `output_type` | type | `str` | Output type: BaseModel, union, list, or func |
| `instructions` | see below | `None` | Static/dynamic agent instructions |
| `system_prompt` | `str | Sequence[str]` | `()` | Static system prompt text |
| `deps_type` | type | `object` | Dependency type |
| `name` | `str | None` | `None` | Agent name |
| `description` | `str | TemplateStr | None` | `None` | Agent description |
| `model_settings` | `ModelSettings | None` | `None` | Temperature, max_tokens, etc. |
| `retries` | `int | AgentRetries | None` | `None` | Retry budgets |
| `tools` | `Sequence[Tool | ToolFunc]` | `()` | Function tools |
| `toolsets` | `Sequence[AgentToolset] | None` | `None` | Toolset instances |
| `end_strategy` | `EndStrategy` | `'graceful'` | `'early' | 'graceful' | 'exhaustive'` |
| `metadata` | `dict | Callable | None` | `None` | Run metadata |
| `capabilities` | `Sequence[AgentCapability] | None` | `None` | Capabilities |

`instructions` type: `str | TemplateStr | Callable[..., str] | list[str | TemplateStr | Callable[..., str]]`

## Run Methods

| Method | Returns | Description |
|---|---|---|
| `agent.run()` | `AgentRunResult` | Async |
| `agent.run_sync()` | `AgentRunResult` | Sync wrapper |
| `agent.run_stream()` | `StreamedRunResult` | Streaming text/structured |
| `agent.run_stream_events()` | `AsyncIterator[AgentStreamEvent]` | Granular events |
| `agent.iter()` | `AgentRun` | Graph node iteration |

## Key Model Settings

```python
ModelSettings(
    temperature=0.7,          # OpenAI/Anthropic/Google
    max_tokens=2000,          # Max output tokens
    top_p=0.9,                # Nucleus sampling
    presence_penalty=0.0,     # OpenAI
    frequency_penalty=0.0,    # OpenAI
    seed=42,                  # Deterministic output
    timeout=30.0,             # Request timeout
    extra_body={},            # Provider-specific params
)
```

## Usage Limits

```python
UsageLimits(
    request_limit=50,            # Max LLM requests per run
    total_tokens_limit=100000,   # Max total tokens
    duration_limit=300.0,        # Max seconds
    tool_calls_limit=100,        # Max tool calls
)
```

## Error Hierarchy

```
AgentRunError (base)
├── ModelRetry              → Ask model to try again (from tools/output validators)
├── ModelAPIError           → Provider API error (4xx/5xx)
├── ModelHTTPError          → HTTP-level error
├── UsageLimitExceeded      → Token/request limit hit
├── UserError               → Configuration error
├── CallDeferred            → Tool call needs external handling
├── ApprovalRequired        → Tool needs approval
├── UnexpectedModelBehavior → Retry limit exceeded or unexpected response
├── HookTimeoutError        → Hook exceeded timeout
└── FallbackExceptionGroup  → All fallback models failed (ExceptionGroup)
```

## Capability Hook Methods (AbstractCapability)

| Hook Method | Description |
|---|---|
| `before_run(ctx)` | Before agent run starts |
| `after_run(ctx, result)` | After agent run completes |
| `wrap_run(ctx, handler)` | Wrap entire run |
| `on_run_error(ctx, error)` | Handle run errors |
| `before_model_request(ctx, request_context)` | Before LLM call |
| `after_model_request(ctx, request_context, response)` | After LLM response |
| `wrap_model_request(ctx, request_context, handler)` | Wrap LLM request |
| `before_tool_execute(ctx, *, call, tool_def, args)` | Before tool runs |
| `after_tool_execute(ctx, *, call, tool_def, result)` | After tool runs |
| `prepare_tools(ctx, tool_defs)` | Modify tool definitions |
| `handle_deferred_tool_calls(ctx, *, requests)` | Resolve approval/async calls |
| `before_output_validate(ctx, output_context)` | Before output validation |
| `after_output_validate(ctx, output_context, result)` | After output validation |

## PydanticGraph Core API

```python
# GraphBuilder: main entry point
g = GraphBuilder(state_type=StateT, deps_type=DepsT,
                  input_type=InputT, output_type=OutputT)

# Building
g.step  # Decorator for step functions
g.node(BaseNodeSubclass)         # Register a BaseNode
g.edge_from(source).to(target)   # Simple edge
g.edge_from(source).map().to(target)     # Parallel fan-out
g.edge_from(source).broadcast().to(a, b) # Broadcast to multiple

# Joins
g.join(reducer, initial_factory=...)  # Create join node

# Running
graph = g.build()
graph.run(state=..., deps=..., inputs=...)    # → OutputT
graph.run_sync(...)                            # Sync wrapper
graph.iter(state=...)                          # Step-by-step
graph.render(title='...', direction='LR')      # → Mermaid string
```
