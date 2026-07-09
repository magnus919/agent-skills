# CrewAI Crew Patterns

## Sequential Process

Tasks run in order. Each task receives the output of the previous task as context.

```python
from crewai import Crew, Process

crew = Crew(
    agents=[researcher, writer, reviewer],
    tasks=[research_task, write_task, review_task],
    process=Process.sequential,
    verbose=True,
)
result = crew.kickoff()
```

## Hierarchical Process

A manager agent assigns tasks and validates results. Requires `manager_llm`.

```python
from crewai import Crew, Process
from langchain_openai import ChatOpenAI

crew = Crew(
    agents=[researcher, writer, reviewer],
    tasks=[research_task, write_task, review_task],
    process=Process.hierarchical,
    manager_llm=ChatOpenAI(model="gpt-4"),  # Required!
    verbose=True,
)
```

## Crew Parameters

| Parameter | Description |
|-----------|-------------|
| `agents` | List of agents in the crew |
| `tasks` | List of tasks to execute |
| `process` | `Process.sequential` or `Process.hierarchical` |
| `manager_llm` | Required for hierarchical. LLM for the manager agent |
| `verbose` | Print detailed execution logs |
| `memory` | Enable cross-agent memory |
| `cache` | Enable tool result caching |
| `planning` | Enable planning step before execution |
| `max_rpm` | Rate limit across the crew |

## Key Gotchas

- **Hierarchical without `manager_llm` fails silently.** The crew appears to run but produces no output.
- **Sequential with more than 4-5 agents** can produce very long completion times (each agent waits for the previous).
- **Crew-level `memory=True** enables agents to remember context across tasks.
- **Tool caching** (`cache=True`) prevents repeated API calls for the same input.
- **`crew.kickoff()` is synchronous** by default. For async, check the async API.
