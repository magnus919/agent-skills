# CrewAI Callbacks

## Step Callback

Called after each agent step:

```python
def on_step(agent, task, step_output):
    print(f"[{agent.role}] Step completed: {step_output[:100]}...")

agent = Agent(
    role="Researcher",
    goal="Find information",
    backstory="Expert researcher",
    step_callback=on_step,
)
```

## Task Callback

Called after task completion:

```python
def on_task_complete(task, output):
    print(f"[{task.agent.role}] Task '{task.description[:50]}...' complete")

task = Task(
    description="Research the topic",
    expected_output="Research brief",
    agent=researcher,
    callback=on_task_complete,
)
```

## Use Cases

- Logging agent decisions for debugging
- Monitoring token usage per agent
- Sending progress updates to a dashboard
- Early stopping if output quality drops
