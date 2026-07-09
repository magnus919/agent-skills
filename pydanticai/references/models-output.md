# Models, Output, & Streaming

## Models — Provider System

PydanticAI supports a three-layer model architecture: **Model** (LLM API wrapper), **Provider** (auth/endpoint), **Profile** (per-model schema rules).

### Model String Syntax

```python
agent = Agent('openai:gpt-5.2')                    # provider:model_name
agent = Agent('anthropic:claude-sonnet-4-6')
agent = Agent('google:gemini-3-flash-preview')
agent = Agent('openrouter:google/gemini-3-pro-preview')
```

### Using a Model Instance Directly

```python
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.models.anthropic import AnthropicModel
from pydantic_ai.providers.openai import OpenAIProvider

model = OpenAIChatModel(
    'gpt-5.2',
    provider=OpenAIProvider(
        base_url='https://api.openai.com/v1',
        api_key='sk-...',
    ),
)
agent = Agent(model)
```

### Built-in Model Backends

| Backend | File | Provider prefix |
|---|---|---|
| OpenAI Chat | `models/openai.py` | `openai:` |
| OpenAI Responses | `models/openai.py` | `openai-responses:` |
| Anthropic | `models/anthropic.py` | `anthropic:` |
| Google Gemini | `models/google.py` | `google:` |
| Google Cloud (Vertex) | `models/google.py` | `google-cloud:` |
| Groq | `models/groq.py` | `groq:` |
| Mistral | `models/mistral.py` | `mistral:` |
| Cohere | `models/cohere.py` | `cohere:` |
| AWS Bedrock | `models/bedrock.py` | `bedrock:` |
| Ollama | `models/ollama.py` | `ollama:` |
| OpenRouter | `models/openrouter.py` | `openrouter:` |
| HuggingFace | `models/huggingface.py` | `huggingface:` |
| Cerebras | `models/cerebras.py` | `cerebras:` |
| xAI (Grok) | `models/xai.py` | `xai:` |
| Z.AI | `models/zai.py` | `zai:` |

### OpenAI-Compatible Providers

Many providers speak the OpenAI API. Use them with `OpenAIChatModel`:
`alibaba`, `azure`, `cerebras`, `deepseek`, `fireworks`, `github`, `heroku`, `litellm`, `moonshotai`, `nebius`, `ollama`, `openrouter`, `ovhcloud`, `sambanova`, `together`, `vercel`, `zai`.

### Async Context Manager for Cleanup

```python
async with agent:                                 # Cleans up HTTP client
    result = await agent.run('Query')
```

### FallbackModel — Multi-Model Fallback

```python
from pydantic_ai import Agent, ModelSettings
from pydantic_ai.models.fallback import FallbackModel
from pydantic_ai.models.anthropic import AnthropicModel
from pydantic_ai.models.openai import OpenAIChatModel

fallback = FallbackModel(
    OpenAIChatModel('gpt-5.2', settings=ModelSettings(temperature=0.7)),
    AnthropicModel('claude-sonnet-4-5', settings=ModelSettings(temperature=0.2)),
)
agent = Agent(fallback)
```

`fallback_on` parameter controls what triggers fallback — exceptions, exception handlers, and response handlers all supported.

### ConcurrencyLimitedModel — Rate Limiting

```python
from pydantic_ai import Agent, ConcurrencyLimitedModel

model = ConcurrencyLimitedModel('openai:gpt-4o', limiter=5)  # 5 concurrent
agent = Agent(model)

# Shared limiter across models
from pydantic_ai import ConcurrencyLimiter
shared = ConcurrencyLimiter(max_running=10, name='openai-pool')
model1 = ConcurrencyLimitedModel('openai:gpt-4o', limiter=shared)
model2 = ConcurrencyLimitedModel('openai:gpt-4o-mini', limiter=shared)
```

### Custom Model

```python
from pydantic_ai.models import Model
from pydantic_ai.models.base import StreamedResponse

class MyCustomModel(Model):
    async def request(self, messages, model_settings, model_request_parameters):
        ...
    async def request_stream(self, messages, model_settings, model_request_parameters, run_context):
        ...
```

---

## Output Types

### Structured Output with Pydantic Models

```python
from pydantic import BaseModel, Field
from pydantic_ai import Agent

class CityLocation(BaseModel):
    city: str
    country: str

agent = Agent('openai:gpt-5.2', output_type=CityLocation)
result = agent.run_sync('Where were the olympics held in 2012?')
print(result.output)       # CityLocation(city='London', country='United Kingdom')
print(result.output.city)  # Typed access
```

### Multiple Output Types (Union / List)

```python
class Box(BaseModel):
    width: int; height: int; depth: int; units: str

agent = Agent('openai:gpt-5-mini',
    output_type=[Box, str],   # Registered as separate output tools
    instructions="Extract box dimensions or ask user to try again.",
)
result = agent.run_sync('The box is 10x20x30 cm')
print(result.output)  # Box(width=10, height=20, depth=30, units='cm')
```

For union types with type checking:
```python
agent: Agent[object, list[str] | list[int]] = Agent(
    'openai:gpt-5-mini',
    output_type=list[str] | list[int],  # type: ignore
)
```

### Output Functions

Functions called by the model as its final action — result is NOT sent back to the model.

```python
from pydantic_ai import Agent, ModelRetry

def run_sql_query(query: str) -> list[dict]:
    """Run a SQL query on the database."""
    if 'DROP' in query.upper():
        raise ModelRetry("Destructive queries not allowed.")
    return db.execute(query)

agent = Agent('openai:gpt-5.2',
    output_type=[run_sql_query],
    instructions='You are a SQL agent.',
)
```

Output functions can take `RunContext`, return `ModelRetry`, and be combined with other output types in a list.

### TextOutput marker

Force text output to a specific function:
```python
from pydantic_ai import Agent, TextOutput

def split_words(text: str) -> list[str]:
    return text.split()

agent = Agent('openai:gpt-5.2', output_type=TextOutput(split_words))
```

### Output modes

```python
from pydantic_ai import ToolOutput  # Marks a type as tool-call output
```

### StructuredDict (for spec files)

```yaml
output_schema:
  type: object
  properties:
    answer: {type: string}
    confidence: {type: number}
  required: [answer, confidence]
```

This creates a `StructuredDict` output type that returns `dict[str, Any]`.

### Output Validation

```python
@agent.output_validator
async def validate_output(ctx: RunContext[MyDeps], output: str) -> str:
    response = await ctx.deps.client.post('https://validate.example.com', json={'text': output})
    if response.status_code == 400:
        raise ModelRetry(f'Invalid output: {response.text}')
    return output
```

---

## Streaming

### Stream Text

```python
async with agent.run_stream('Tell me a story') as result:
    async for chunk in result.stream_text():
        print(chunk, end='')

    # Deltas mode (each chunk is just the new characters)
    async for delta in result.stream_text(delta=True):
        print(delta, end='')
```

### Stream Structured Output

```python
async with agent.run_stream('Extract data') as result:
    async for partial in result.stream_output():
        print(partial)  # Partial validated output
```

### Stream All Events (for UIs)

```python
from pydantic_ai import PartStartEvent, PartDeltaEvent, FunctionToolCallEvent, FinalResultEvent

async with agent.run_stream_events('Query') as events:
    async for event in events:
        if isinstance(event, PartStartEvent):
            # TextPart, ToolCallPart, etc starting
        elif isinstance(event, PartDeltaEvent):
            # Streaming delta for a part
        elif isinstance(event, FunctionToolCallEvent):
            print(f"Tool called: {event.part.tool_name}")
        elif isinstance(event, FinalResultEvent):
            print("Final result starting")
```

### Stream with Event Stream Handler

Pass a callback to `run()` or `run_stream()` for mid-run visibility:

```python
async def event_handler(ctx, event_stream):
    async for event in event_stream:
        if isinstance(event, FunctionToolCallEvent):
            log_tool_call(event)

async with agent.run_stream('Query', event_stream_handler=event_handler) as result:
    async for text in result.stream_text():
        print(text)
```

### Cancellation

```python
async with agent.run_stream('Long story') as result:
    async for chunk in result.stream_text(delta=True):
        if len(chunk) > 100:
            await result.cancel()     # Stop generation
            break
    print(result.cancelled)           # True
    print(result.response.state)      # 'interrupted'
```

### Memory Tools & File Attachments

PydanticAI supports file/audio/video/image attachments via `FilePart`, `ImageUrl`, `AudioUrl`, `VideoUrl` in messages. Use `BinaryContent` for inline binary data.
