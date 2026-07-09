# Agents — Core API Reference

The `Agent` class is the primary interface for interacting with LLMs. It's a frozen dataclass generic over dependency type and output type: `Agent[AgentDepsT, OutputDataT]`.

## Constructor

```python
from pydantic_ai import Agent

agent = Agent(
    model=None,                        # str like 'openai:gpt-5.2' or Model instance
    *,
    output_type=str,                   # Output type: str, BaseModel, list, union, or output func
    instructions=None,                 # Static str, TemplateStr, callable, or list of same
    system_prompt=(),                  # Static string(s) for system prompt
    deps_type=object,                  # Type of dependency object
    name=None,                         # Agent name (shows in Logfire traces)
    description=None,                  # Description (supports TemplateStr for deps)
    model_settings=None,               # ModelSettings instance
    retries=None,                      # int or AgentRetries(tools=N, output=N)
    validation_context=None,           # Callable or value for output validation
    tools=(),                          # Function list or Tool instances
    toolsets=None,                     # Sequence of toolset instances
    defer_model_check=False,             # Skip model validation on construction. Set True for module-level agents tested with TestModel.
    end_strategy='graceful',           # 'early', 'graceful', 'exhaustive'
    metadata=None,                     # Dict or callable returning dict
    tool_timeout=None,                 # Default tool timeout in seconds
    max_concurrency=None,              # Concurrency limit for parallel runs
    capabilities=None,                 # Sequence of capability instances
)
```

> **`defer_model_check=True`** — use when declaring agents at module level for testing. Without it, the agent tries to resolve the model string at import time. If you're using `TestModel` with `agent.override(model=TestModel())` in tests, the module-level agent declaration will fail at import without API credentials unless this is set. Test-time scenario:
> ```python
> # agent_setup.py — module-level declaration
> agent = Agent('openai:gpt-5.2', deps_type=MyDeps, defer_model_check=True)
>
> # test_agent.py
> from pydantic_ai.models.test import TestModel
> with agent.override(model=TestModel()):
>     result = agent.run_sync('Test query', deps=test_deps)
> ```

## Run Methods — Five Ways to Execute

### 1. `agent.run()` — Async, returns completed result
```python
result = await agent.run('User prompt', deps=deps)
print(result.output)           # The final output (typed)
print(result.usage)            # RunUsage(input_tokens=..., output_tokens=...)
print(result.all_messages())   # Full message history
```

### 2. `agent.run_sync()` — Synchronous wrapper
```python
result = agent.run_sync('User prompt', deps=deps)
# Internally: loop.run_until_complete(self.run(...))
```

### 3. `agent.run_stream()` — Stream final output
```python
async with agent.run_stream('Tell me a story') as result:
    async for chunk in result.stream_text():
        print(chunk, end='')

    # Also available:
    async for text in result.stream_text(delta=True):  # emits deltas
        pass
```

### 4. `agent.run_stream_events()` — Stream all granular events
```python
async with agent.run_stream_events('What is the weather?') as events:
    async for event in events:
        if isinstance(event, PartStartEvent):
            print(f"Part started: {event.part}")
        elif isinstance(event, FunctionToolCallEvent):
            print(f"Tool call: {event.part.tool_name}")
        elif isinstance(event, AgentRunResultEvent):
            print(f"Final: {event.result.output}")
```

### 5. `agent.iter()` — Iterate over agent's internal graph nodes
```python
async with agent.iter('What is the capital of France?') as run:
    async for node in run:
        # node is a BaseNode subclass: UserPromptNode, ModelRequestNode, CallToolsNode, End
        if isinstance(node, End):
            print(f"Done: {node.data}")
```

### Common Run Parameters

All run methods accept:
- `message_history` — list of `ModelMessage` from previous runs
- `model` — override the agent's default model for this run
- `deps` — dependency instance (required if `deps_type` is set)
- `model_settings` — override model settings
- `usage_limits` — `UsageLimits` for capping requests/tokens
- `usage` — shared `RunUsage` for aggregating across runs
- `toolsets` — additional run-scoped toolsets
- `conversation_id` — str or 'new' to override/fork conversation

## Defining Tools

### `@agent.tool` — with RunContext access
```python
@agent.tool
async def my_tool(ctx: RunContext[MyDeps], param1: str, param2: int) -> str:
    """Tool description extracted as LLM schema."""
    # ctx.deps — access dependencies
    # ctx.model — current model
    # ctx.usage — token usage so far
    # ctx.run_step — current step number
    return result
```

### `@agent.tool_plain` — no RunContext
```python
@agent.tool_plain
def simple_tool(query: str) -> list[str]:
    """Search the database."""
    return db_search(query)
```

### `Tool` class — fine-grained control
```python
from pydantic_ai import Tool

Tool(
    my_func,
    prepare=my_prepare_fn,         # Dynamic tool definition modifier
    name="custom_name",            # Override auto-derived name
    description="Custom desc",     # Override auto-derived description
    retries=3,                     # Per-tool retry budget
    docstring_format='auto',       # 'google', 'numpy', 'sphinx', or 'auto'
    require_parameter_descriptions=False,
)
```

### Docstring Schema Extraction

PydanticAI extracts parameter schemas from docstrings using griffe:
```python
@agent.tool_plain(docstring_format='google', require_parameter_descriptions=True)
def search(db: str, query: str) -> list[str]:
    """Search the database.

    Args:
        db: The database to search (e.g. 'users', 'orders')
        query: The search query string
    """
    return results
```

Parameters are extracted from the function signature (all params except `RunContext`). Single object-typed parameters simplify the schema.

### Tool Retries & ModelRetry

Raise `ModelRetry` to ask the model to try again:
```python
from pydantic_ai import ModelRetry

@agent.tool
def lookup(id: str) -> dict:
    result = db.find(id)
    if not result:
        raise ModelRetry(f"ID {id} not found. Available IDs: ...")
    return result
```

## Dependency Injection

### Defining deps
```python
from dataclasses import dataclass
import httpx
from pydantic_ai import Agent, RunContext

@dataclass
class MyDeps:
    api_key: str
    client: httpx.AsyncClient

agent = Agent('openai:gpt-5.2', deps_type=MyDeps)

@agent.system_prompt
async def get_prompt(ctx: RunContext[MyDeps]) -> str:
    resp = await ctx.deps.client.get('https://example.com')
    return f"Context: {resp.text}"
```

### Passing deps at runtime
```python
async with httpx.AsyncClient() as client:
    deps = MyDeps('api-key-123', client)
    result = await agent.run('Query', deps=deps)
```

### Overriding deps for testing
```python
with agent.override(deps=test_deps):
    result = await agent.run('Test query')
```

### Sync vs Async deps
Both work — sync functions run in a thread pool via `run_in_executor`. Whether you use `run` or `run_sync` is independent of whether deps are sync or async.

### Agent Instructions

Three kinds of instructions, merged in order:

```python
# 1. Static — via constructor
agent = Agent(model, instructions='Be concise.')

# 2. Dynamic — via decorator (receives RunContext)
@agent.system_prompt
async def add_user_context(ctx: RunContext[MyDeps]) -> str:
    return f"The user is {ctx.deps.user_name}"

# 3. Per-run — via run() parameter
result = await agent.run('Query', instructions='Use metric units.')
```

Instructions appear in the `ModelRequest.instructions` field. System prompts appear in message history as `SystemPromptPart`.

### Additional Configuration

**Usage Limits:**
```python
from pydantic_ai import UsageLimits

result = agent.run_sync('Query', usage_limits=UsageLimits(
    request_limit=10,           # Max LLM requests
    total_tokens_limit=5000,    # Max total tokens
    tool_calls_limit=50,        # Max tool calls
))
```

**Model Settings:**
```python
from pydantic_ai import ModelSettings

agent = Agent(
    'openai:gpt-5.2',
    model_settings=ModelSettings(
        temperature=0.5,
        max_tokens=2000,
        top_p=0.9,
    )
)
```

**Run Metadata:**
```python
agent = Agent('openai:gpt-5.2', metadata={'environment': 'production'})
# Or callable:
agent = Agent('openai:gpt-5.2', metadata=lambda: {'user_id': get_current_user()})
```

### Static Type Checking

The `Agent` class is generic: `Agent[DepsT, OutputT]`. Your IDE infers types from `deps_type` and `output_type`:
```python
agent = Agent('openai:gpt-5.2', deps_type=int, output_type=bool)
# Revealed type: Agent[int, bool]

result = agent.run_sync('Test', deps=42)
reveal_type(result.output)  # bool
```

For union output types, explicitly annotate:
```python
agent: Agent[object, list[str] | list[int]] = Agent(
    'openai:gpt-5.2',
    output_type=list[str] | list[int],  # type: ignore
)
```

### System Prompts

Static system prompts (`system_prompt=`) and dynamic ones (`@agent.system_prompt`) are sent to the model at the start of each request. When `message_history` is provided, the receiving agent uses its own `system_prompt` — use `ReinjectSystemPrompt` capability if history from another agent lacks one.

### Reflection & Self-Correction

When structured output validation fails, PydanticAI automatically retries by sending the validation error back to the LLM. Control via:
```python
agent = Agent(model, retries=3)               # Same budget for tools & output
agent = Agent(model, retries=AgentRetries(tools=3, output=5))  # Separate budgets
agent = Agent(model, tools=[Tool(my_func, retries=5)])  # Per-tool override
```

### Error Handling

```python
from pydantic_ai import UnexpectedModelBehavior, capture_run_messages

with capture_run_messages() as messages:
    try:
        result = agent.run_sync('Query')
    except UnexpectedModelBehavior as e:
        print(f"Error: {e}")
        print(f"Cause: {e.__cause__}")
        print("Full message history:", messages)
```

Partial state on interruption — interrupted `ModelResponse` messages have `state='interrupted'`. Interrupted `ModelRequest` messages contain completed tool returns before the failure.

### Agent Specs (YAML/JSON configuration)

```yaml
# agent.yaml
model: anthropic:claude-opus-4-6
instructions: You are a helpful assistant.
capabilities:
  - WebSearch:
      local: duckduckgo
  - Thinking:
      effort: high
```

```python
from pydantic_ai import Agent

# From file
agent = Agent.from_file('agent.yaml')

# From dict
agent = Agent.from_spec({
    'model': 'openai:gpt-5.2',
    'instructions': 'You are helping {{user_name}}.',
}, deps_type=MyDeps)
```

Full `AgentSpec` fields: `model`, `name`, `description`, `instructions`, `model_settings`, `capabilities`, `deps_schema`, `output_schema`, `retries`, `end_strategy`, `tool_timeout`, `instrument`, `metadata`.

Template strings (`{{variable}}`) render against deps at runtime. When `deps_type` is provided, template variables are validated at construction time.
