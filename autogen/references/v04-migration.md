# AutoGen v0.4 Migration and Advanced Patterns

AutoGen AgentChat 0.7.5 continues the API generation introduced in v0.4. This reference covers migration from the separate legacy `pyautogen` 0.2 package and current patterns. The runnable modern examples use Python 3.10+ and `../requirements.txt`.

## v0.2 → v0.4 Migration

### Legacy `pyautogen` 0.2 Pattern

```python
# v0.2: UserProxyAgent bundled code execution + human input
from autogen import AssistantAgent, UserProxyAgent

assistant = AssistantAgent(name="assistant", llm_config=llm_config)
proxy = UserProxyAgent(name="proxy", human_input_mode="NEVER",
                       code_execution_config={"use_docker": True})
proxy.initiate_chat(assistant, message="Write Python code")
```

### AgentChat 0.7.5 Pattern

```python
# v0.4: Code execution is a separate agent
from autogen_agentchat.agents import AssistantAgent, CodeExecutorAgent
from autogen_agentchat.conditions import MaxMessageTermination
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_ext.code_executors.docker import DockerCommandLineCodeExecutor
from autogen_ext.models.openai import OpenAIChatCompletionClient

model_client = OpenAIChatCompletionClient(model="gpt-4o-mini")
async with DockerCommandLineCodeExecutor(work_dir="coding") as executor:
    assistant = AssistantAgent(name="assistant", model_client=model_client,
                               system_message="Write a Python code block when calculation is useful.")
    code_agent = CodeExecutorAgent(name="executor", code_executor=executor)
    team = RoundRobinGroupChat(
        [assistant, code_agent],
        termination_condition=MaxMessageTermination(max_messages=4),
    )
    result = await team.run(task="Write Python code to calculate pi")
    print(result.messages[-1].content)
await model_client.close()
```

## AgentTool — Agent as Tool

```python
from autogen_agentchat.tools import AgentTool

writer = AssistantAgent(name="writer", model_client=model_client,
                        system_message="Write well.")
writer_tool = AgentTool(agent=writer)

assistant = AssistantAgent(
    name="assistant",
    model_client=model_client,
    tools=[writer_tool],
    system_message="You are a helpful assistant.",
)
```

## Streaming with run_stream()

```python
stream = assistant.run_stream(task="Tell me a story")
async for message in stream:
    print(message)  # Each message as it's generated
```

## Human input in AgentChat

AgentChat's `UserProxyAgent` represents a human and accepts `input_func`; it does not implement the legacy `human_input_mode` values. Code execution is a distinct `CodeExecutorAgent` role. See `agent-types.md` for the current constructors.

## Termination Conditions

```python
from autogen_agentchat.conditions import TextMentionTermination, MaxMessageTermination

# Stop when agent says TERMINATE
text_termination = TextMentionTermination("TERMINATE")

# Or stop after N messages
max_termination = MaxMessageTermination(max_messages=10)

# Combine conditions
# team.run(..., termination_condition=text_termination | max_termination)
```
