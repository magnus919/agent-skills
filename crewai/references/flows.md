# CrewAI Flows — Event-Driven Orchestration

Flows connect multiple Crews into event-driven workflows with state management, resumption, and conditional branching.

## Basic Flow

```python
from crewai.flow.flow import Flow, listen, start

class MyFlow(Flow):
    @start()
    def begin(self):
        print("Flow started")
        return {"data": "initial"}

    @listen(begin)
    def process_data(self, state):
        print(f"Processing: {state['data']}")
        # Launch a crew here
        return {"result": "processed"}

flow = MyFlow()
result = flow.kickoff()
```

## State Management with @persist

```python
from crewai.flow.flow import Flow, listen, start, persist

@persist  # State persists across executions
class PersistentFlow(Flow):
    counter: int = 0  # Tracked state

    @start()
    def increment(self):
        self.counter += 1
        return {"counter": self.counter}
```

## Connecting Multiple Crews

```python
class ResearchFlow(Flow):
    @start()
    def research(self):
        crew = Crew(agents=[researcher], tasks=[research_task], process=Process.sequential)
        return crew.kickoff()

    @listen(research)
    def write_report(self, state):
        crew = Crew(agents=[writer], tasks=[write_task], process=Process.sequential)
        return crew.kickoff()
```

## Key Features

- **Event-driven:** `@listen` decorator triggers on completion of upstream steps
- **State management:** `@persist` enables state to survive across executions
- **Restoration:** `restore_from_state_id` to resume flows from checkpoints
- **Multiple crews:** Connect separate crews into a single orchestrated workflow
