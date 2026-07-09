# AutoGen v0.4 Migration and Advanced Patterns

AutoGen v0.4 introduced significant API changes from v0.2. This reference covers migration and patterns not found in the v0.2 API.

## v0.2 → v0.4 Migration

### v0.2 Pattern (Deprecated)

```python
# v0.2: UserProxyAgent bundled code execution + human input
from autogen import AssistantAgent, UserProxyAgent

assistant = AssistantAgent(name="assistant", llm_config=llm_config)
proxy = UserProxyAgent(name="proxy", human_input_mode="NEVER",
                       code_execution_config={"use_docker": True})
proxy.initiate_chat(assistant, message="Write Python code")
```

### v0.4 Pattern

```python
# v0.4: Code execution is a separate agent
from autogen_agentchat.agents import AssistantAgent, CodeExecutorAgent
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_ext.code_executors.local import LocalCommandLineCodeExecutor
from autogen_ext.models.openai import OpenAIChatCompletionClient

model_client = OpenAIChatCompletionClient(model="gpt-4o-mini")
assistant = AssistantAgent(name="assistant", model_client=model_client,
                           system_message="You are a helpful assistant.")
executor = CodeExecutorAgent(
    name="executor",
    code_executor=LocalCommandLineCodeExecutor(work_dir="coding"),
)

team = RoundRobinGroupChat([assistant, executor])
result = await team.run(task="Write Python code to calculate pi")
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

## Three human_input_mode Behaviors

| Mode | Behavior | Use case |
|------|----------|----------|
| `"NEVER"` | No human input requested. Agent runs fully autonomously. | Automated pipelines, batch processing |
| `"ALWAYS"` | Agent asks for human input before every reply. Blocks until input received. | Human-in-the-loop approval gates |
| `"TERMINATE"` | Agent asks for human input only when it's about to terminate (send TERMINATE). | Review final output before closing |

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
