# CrewAI Agent Design

## Agent Parameters

| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| `role` | Yes | — | Agent's role in the crew |
| `goal` | Yes | — | What the agent aims to accomplish |
| `backstory` | Yes | — | Agent's background and expertise |
| `llm` | No | gpt-4 | LLM to power the agent |
| `tools` | No | [] | Tools the agent can use |
| `verbose` | No | False | Print detailed execution logs |
| `allow_delegation` | No | True | Allow agent to delegate tasks to others |
| `max_iter` | No | 15 | Max reasoning iterations before forced output |
| `memory` | No | False | Enable cross-task memory |
| `cache` | No | True | Enable tool result caching |
| `max_rpm` | No | None | Max requests per minute rate limit |
| `function_calling_llm` | No | None | Separate LLM for function/tool calling |
| `step_callback` | No | None | Callback after each agent step |
| `use_system_prompt` | No | True | Use system prompt vs human message |

## Agent Definition Example

```python
from crewai import Agent
from crewai.tools import tool

@tool("search")
def search_web(query: str) -> str:
    """Search the web."""
    return f"Results for: {query}"

researcher = Agent(
    role="Senior Research Analyst",
    goal="Find comprehensive, accurate information",
    backstory="""You are a senior research analyst with 15 years of experience
    in market research and competitive analysis. You excel at finding
    insights from complex data sets.""",
    tools=[search_web],
    verbose=True,
    allow_delegation=False,  # Prevent delegation loops
    max_iter=10,  # Limit reasoning iterations
)
```

## Key Gotchas

- `allow_delegation=True` (default) can cause agents to hand off endlessly. Set to `False` for single-responsibility agents.
- `max_iter=15` default. Complex tasks may need more. Simple tasks should set lower.
- Tool docstring becomes the tool description the LLM sees. Make it descriptive.
- `verbose=True` prints all LLM calls and tool invocations — good for debugging, noisy for production.
