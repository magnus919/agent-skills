# AutoGen Conversation Patterns

Examples target AgentChat 0.7.5 and Python 3.10+. They use asynchronous `run()` and `run_stream()`; old `initiate_chat()` and `summary` examples apply to `pyautogen` 0.2 only.

## Assistant and human participant

`UserProxyAgent` is the human side of a team. Its `input_func` receives the prompt and returns the user's reply.

```python
from autogen_agentchat.agents import AssistantAgent, UserProxyAgent
from autogen_agentchat.conditions import MaxMessageTermination
from autogen_agentchat.teams import RoundRobinGroupChat

assistant = AssistantAgent(name="assistant", model_client=model_client)
human = UserProxyAgent(name="human", input_func=lambda prompt: input(prompt))
team = RoundRobinGroupChat(
    [assistant, human],
    termination_condition=MaxMessageTermination(max_messages=4),
)
result = await team.run(task="Explain AutoGen and ask me a follow-up question.")
for message in result.messages:
    print(f"{message.source}: {message.content}")
```

## Termination conditions

Bound a team explicitly. `MaxMessageTermination` is useful when the exact final response is not known in advance; `TextMentionTermination` is useful when a model is instructed to emit a marker.

```python
from autogen_agentchat.conditions import MaxMessageTermination, TextMentionTermination

bounded = MaxMessageTermination(max_messages=10)
marked = TextMentionTermination("TERMINATE")
team = RoundRobinGroupChat([assistant, executor], termination_condition=bounded | marked)
result = await team.run(task="Perform the bounded task.")
print(result.messages[-1].content)
```

## Cancellation

Pass a `CancellationToken` to interrupt a long-running agent or team run.

```python
from autogen_core import CancellationToken

token = CancellationToken()
result = await assistant.run(task="Summarize the input.", cancellation_token=token)
# Call token.cancel() from the controlling task to stop a run.
```

## Agent as a tool

For a nested task that should remain inside a model-backed agent, wrap the specialist in `AgentTool` rather than calling the legacy `initiate_chat()` method.

```python
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.tools import AgentTool

researcher = AssistantAgent(name="researcher", model_client=model_client)
research_tool = AgentTool(agent=researcher, return_value_as_last_message=True)
coordinator = AssistantAgent(
    name="coordinator",
    model_client=model_client,
    tools=[research_tool],
)
result = await coordinator.run(task="Research the question and summarize the findings.")
```

Use `RoundRobinGroupChat` when agents should exchange visible messages in a fixed order. Use `SelectorGroupChat` when a model should choose the next speaker. See `group-chat.md` for team patterns.
