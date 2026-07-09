# CrewAI Memory System

CrewAI v1.15+ uses a unified `Memory` class that replaces separate short-term, long-term, entity, and external memory types with a single intelligent API.

## Enabling Memory

```python
from crewai import Crew

crew = Crew(
    agents=[agent1, agent2],
    tasks=[task1, task2],
    memory=True,  # Enables unified memory for all agents
)
```

## How Memory Works

When `memory=True` is set at the Crew level:
- **Memory is shared** — all agents in the crew can access context from prior tasks
- **Short-term persistence** — within a single crew execution, agents remember context across tasks
- **Entity tracking** — the system tracks entities (people, places, concepts) mentioned across agent conversations
- **Long-term patterns** — across multiple crew runs, the system learns from successful patterns

## Memory Configuration

```python
from crewai import Crew, MemoryConfig

crew = Crew(
    agents=[agent1, agent2],
    tasks=[task1, task2],
    memory=True,
    memory_config=MemoryConfig(
        embedder="openai",  # Embedding provider for memory storage
        dimensions=1536,    # Embedding dimensions
    ),
)
```

## Memory Reset

```python
crew.reset_memories()  # Clear all stored memory
```

## Practical Patterns

- **Within a single crew run:** Memory is automatic. Agents reference prior task outputs through `context`.
- **Across crew runs:** Memory enables the system to learn from past execution patterns.
- **For state-dependent tools:** Set `cache=False` on tools that shouldn't return cached results.
- **For long-running systems:** Periodically call `reset_memories()` to prevent memory bloat.
