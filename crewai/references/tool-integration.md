# CrewAI Tool Integration

## @tool Decorator

```python
from crewai.tools import tool

@tool("search_web")
def search_web(query: str) -> str:
    """Search the web for current information."""
    return f"Results for: {query}"

@tool("calculate")
def calculate(expression: str) -> str:
    """Evaluate a mathematical expression."""
    return str(eval(expression))
```

## Assigning Tools

Tools are assigned to agents:

```python
agent = Agent(
    role="Researcher",
    goal="Find information",
    backstory="Expert researcher",
    tools=[search_web, calculate],  # Agent-level tools
)

# Or task-level (overrides agent tools)
task = Task(
    description="Research and compute",
    agent=agent,
    tools=[search_web],  # Task-specific — only this tool is available
)
```

## Built-in Tools

CrewAI ships tool packages: `crewai-tools` with SerperDevTool, ScrapeWebsiteTool, etc. Install separately:

```bash
pip install crewai-tools
```

## Tool Design Guidelines

- **Docstring matters.** The docstring/description is what the LLM sees to decide when to use the tool.
- **Type hints required.** Tool parameters use type hints for schema generation.
- **Handle errors gracefully.** Tool failures mark tasks as failed but don't raise exceptions.
- **Return strings.** Keep return values as strings for consistent handling.
- **Cache results.** Same input → same cached output (controlled by `cache` parameter).
