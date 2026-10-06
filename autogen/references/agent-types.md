# AutoGen Agent Types

These examples target the pinned AgentChat 0.7.5 packages in `../requirements.txt` and require Python 3.10 or later.

## AssistantAgent

The primary model-backed agent. Use `run()` for a bounded one-agent task and `run_stream()` when messages should be displayed as they arrive.

```python
from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient

model_client = OpenAIChatCompletionClient(model="gpt-4o-mini")
assistant = AssistantAgent(
    name="assistant",
    system_message="You are a helpful AI assistant.",
    model_client=model_client,
)
result = await assistant.run(task="Explain AutoGen in one sentence.")
print(result.messages[-1].content)
await model_client.close()
```

## UserProxyAgent

In AgentChat 0.7.5, `UserProxyAgent` represents a human participant. It requests input through `input_func`; it does not run generated code and does not accept legacy `human_input_mode` or `is_termination_msg` arguments.

```python
from autogen_agentchat.agents import AssistantAgent, UserProxyAgent
from autogen_agentchat.conditions import MaxMessageTermination
from autogen_agentchat.teams import RoundRobinGroupChat

assistant = AssistantAgent(name="assistant", model_client=model_client)
human = UserProxyAgent(
    name="human",
    description="A human participant",
    input_func=lambda prompt: input(prompt),
)
team = RoundRobinGroupChat(
    [assistant, human],
    termination_condition=MaxMessageTermination(max_messages=4),
)
result = await team.run(task="Explain AutoGen and ask me one question.")
for message in result.messages:
    print(message.source, message.content)
```

For UI integrations, provide an `input_func` that connects to the application's input channel and honors cancellation. A command-line `input()` function is only suitable for an interactive terminal.

## CodeExecutorAgent

`CodeExecutorAgent` handles code execution. Give it a `CodeExecutor` instance; use Docker for model-generated code in the shipped example. The agent and executor are separate from `UserProxyAgent`.

```python
from autogen_agentchat.agents import CodeExecutorAgent
from autogen_ext.code_executors.docker import DockerCommandLineCodeExecutor

async with DockerCommandLineCodeExecutor(work_dir="coding") as executor:
    code_agent = CodeExecutorAgent(name="code_executor", code_executor=executor)
    # Add code_agent to a team with an assistant that can produce code blocks.
```

## Conversation and termination

| Need | Use |
|------|-----|
| A model-backed assistant | `AssistantAgent(model_client=...)` |
| A human participant | `UserProxyAgent(input_func=...)` |
| Code execution | `CodeExecutorAgent(code_executor=...)` |
| Fixed turn order | `RoundRobinGroupChat([...])` |
| Bounded conversation | A team `TerminationCondition`, such as `MaxMessageTermination` |

The `human_input_mode`, `is_termination_msg`, and `code_executor` constructor keywords belonged to the separate legacy `pyautogen` 0.2 API. See `v04-migration.md` when migrating that code.
