# Testing & Evaluation

## Testing with TestModel

`TestModel` calls all tools and returns structured data based on their schemas — no LLM required.

**Dependency:** Requires `pytest-asyncio` (or `pytest-anyio`) for async test patterns with `@pytest.mark.asyncio`.

### Basic Usage

```python
from pydantic_ai import Agent
from pydantic_ai.models.test import TestModel

agent = Agent('openai:gpt-5.2', output_type=bool)

with agent.override(model=TestModel()):
    result = agent.run_sync('Test this')
    print(result.output)  # True/False based on output_type
```

### Disable Real Model Requests (Safety)

```python
from pydantic_ai import models
models.ALLOW_MODEL_REQUESTS = False  # No real LLM calls allowed
```

### Testing with `capture_run_messages`

```python
from pydantic_ai import capture_run_messages

with capture_run_messages() as messages:
    result = agent.run_sync('Test query')

# messages contains all ModelRequest/ModelResponse pairs
# Inspect tool calls, responses, and ordering
```

### pytest Fixture Pattern

```python
import pytest
from pydantic_ai import models
from pydantic_ai.models.test import TestModel

models.ALLOW_MODEL_REQUESTS = False

@pytest.fixture
def override_agent():
    with weather_agent.override(model=TestModel()):
        yield

async def test_forecast(override_agent):
    result = await run_weather_forecast(...)
    assert result is not None
```

### Full Integration Test Example

```python
from pydantic_ai import Agent, capture_run_messages
from pydantic_ai.models.test import TestModel
from pydantic_ai import ModelResponse, TextPart, ToolCallPart

weather_agent = Agent('openai:gpt-5.2', deps_type=WeatherService)

async def test_weather_forecast():
    with weather_agent.override(model=TestModel()):
        with capture_run_messages() as messages:
            result = weather_agent.run_sync(
                'What is the weather in London?',
                deps=WeatherService(),
            )
    # Assert on result, inspect messages for tool calls
    assert len(messages) == 4  # UserPrompt → ToolCall → ToolReturn → TextResponse
```

## Testing with FunctionModel

Full control over model responses by providing a custom function.

```python
from pydantic_ai import ModelMessage, ModelResponse, TextPart, ToolCallPart
from pydantic_ai.models.function import AgentInfo, FunctionModel

def mock_model(messages: list[ModelMessage], info: AgentInfo) -> ModelResponse:
    if len(messages) == 1:
        return ModelResponse(parts=[
            ToolCallPart('get_weather', {'city': 'London'})
        ])
    else:
        return ModelResponse(parts=[
            TextPart('The weather is sunny.')
        ])

with agent.override(model=FunctionModel(mock_model)):
    result = agent.run_sync('What is the weather?')
```

### Testing Native Tools

```python
# TestModel can't emulate native tools — disable them in tests
with agent.override(model=TestModel(), native_tools=[]):
    result = agent.run_sync('Query')
```

### Override Multiple Things

```python
with agent.override(
    model=TestModel(),
    deps=test_deps,
    toolsets=[test_toolset],
):
    result = agent.run_sync('Query')
```

## Pydantic Evals

A separate framework (`pydantic-evals`) for systematic evaluation.

**Install:** `pip install pydantic-evals` (optional: `[logfire]`)

### Core Data Model

```
Dataset (1) ──── (Many) Case
│
└─── (Many) Experiment ──┴─ (Many) Case results
     │
     ├── (1) Task (function being evaluated)
     └── (Many) Evaluator (scoring functions)
```

### Basic Usage

```python
from pydantic_evals import Case, Dataset

case1 = Case(
    name='capital_question',
    inputs='What is the capital of France?',
    expected_output='Paris',
)

dataset = Dataset(
    name='capital_quiz',
    cases=[case1],
    evaluators=[IsInstance(type_name='str')],
)

def guess_city(question: str) -> str:
    return 'Paris'

report = dataset.evaluate_sync(guess_city)
report.print(include_input=True, include_output=True)
```

### Custom Evaluator

```python
from dataclasses import dataclass
from pydantic_evals.evaluators import Evaluator, EvaluatorContext

@dataclass
class MyEvaluator(Evaluator[str, str]):
    def evaluate(self, ctx: EvaluatorContext[str, str]) -> float:
        if ctx.output == ctx.expected_output:
            return 1.0
        elif ctx.expected_output.lower() in ctx.output.lower():
            return 0.8
        return 0.0

dataset.add_evaluator(MyEvaluator())
```

### Built-in Evaluators
- `IsInstance` — Type checking
- `ExactMatch` — String comparison
- LLM-as-judge evaluators for subjective quality
- Span-based evaluation using OpenTelemetry traces

### Logfire Integration

```python
# Results auto-appear in Logfire web UI when logfire SDK is configured
report = dataset.evaluate_sync(my_function)
```
