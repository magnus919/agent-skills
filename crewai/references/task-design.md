# CrewAI Task Design

## Task Parameters

| Parameter | Required | Description |
|-----------|----------|-------------|
| `description` | Yes | Clear description of what to do |
| `expected_output` | Yes | Description of what success looks like |
| `agent` | Yes | The agent assigned to this task |
| `tools` | No | Task-specific tools (overrides agent defaults) |
| `context` | No | List of tasks whose outputs are passed as context |
| `callback` | No | Function called after task completion |
| `human_input` | No | Request human input before marking done |

## Task Examples

```python
from crewai import Task

research = Task(
    description="Research the topic thoroughly. Find at least 5 sources.",
    expected_output="A comprehensive research brief with key findings and source citations.",
    agent=researcher,
)

write_report = Task(
    description="Write a detailed report based on the research provided.",
    expected_output="A well-structured markdown report with executive summary.",
    agent=writer,
    context=[research],  # Pass research output as context
)
```

## Task Context Passing

Pass outputs from earlier tasks to later tasks using `context`:

```python
task1 = Task(description="Research", expected_output="Research brief", agent=researcher)
task2 = Task(description="Write", expected_output="Report", agent=writer, context=[task1])
# task2 receives task1's output automatically when the crew runs
```

## Human Input

```python
feedback_task = Task(
    description="Review the generated report",
    expected_output="Approved or revised report",
    agent=reviewer,
    human_input=True,  # Pause and ask for human input
)
```
