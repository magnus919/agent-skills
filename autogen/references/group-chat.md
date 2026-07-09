# AutoGen Group Chat

## RoundRobinGroupChat

Fixed-order conversation. Each agent speaks in turn.

```python
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.ui import Console

agent1 = AssistantAgent(name="researcher", model_client=model_client)
agent2 = AssistantAgent(name="analyst", model_client=model_client)
agent3 = AssistantAgent(name="writer", model_client=model_client)

team = RoundRobinGroupChat([agent1, agent2, agent3])
result = await team.run(task="Research and write about AI trends")
```

## SelectorGroupChat

LLM-driven speaker selection. Uses a model to decide who speaks next.

```python
from autogen_agentchat.teams import SelectorGroupChat

team = SelectorGroupChat(
    [agent1, agent2, agent3],
    model_client=model_client,  # LLM used for speaker selection
)
```

## MagenticOneGroupChat

Magentic-One orchestrator pattern — a lead agent coordinates specialist agents.

## Key Parameters

| Parameter | Description |
|-----------|-------------|
| `participants` | List of agents in the group |
| `model_client` | LLM for speaker selection (SelectorGroupChat) |
| `max_turns` | Max conversation turns before termination |
