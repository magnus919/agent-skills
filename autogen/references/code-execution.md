# AutoGen Code Execution

In AgentChat 0.7.5, `CodeExecutorAgent` handles code blocks and receives a `CodeExecutor` through its `code_executor` argument. `UserProxyAgent` represents a human and is not an executor. Install the pinned packages from `../requirements.txt`.

## Docker (recommended for model-generated code)

```python
from autogen_agentchat.agents import AssistantAgent, CodeExecutorAgent
from autogen_agentchat.conditions import MaxMessageTermination
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_ext.code_executors.docker import DockerCommandLineCodeExecutor

async with DockerCommandLineCodeExecutor(work_dir="coding") as executor:
    assistant = AssistantAgent(
        name="assistant",
        model_client=model_client,
        system_message="Use a Python code block when calculation is useful.",
    )
    code_agent = CodeExecutorAgent(name="code_executor", code_executor=executor)
    team = RoundRobinGroupChat(
        [assistant, code_agent],
        termination_condition=MaxMessageTermination(max_messages=4),
    )
    result = await team.run(task="Calculate 1 + 1 using Python.")
    print(result.messages[-1].content)
```

Docker isolates the execution environment from the host, but code execution still has side effects inside the container. Bound team turns, restrict mounted files and network access as appropriate, and add `approval_func` when code should require review before execution.

## Local executor (trusted code only)

`LocalCommandLineCodeExecutor` executes on the host. Use it only for trusted code in a controlled development environment.

```python
from autogen_ext.code_executors.local import LocalCommandLineCodeExecutor

executor = LocalCommandLineCodeExecutor(work_dir="coding")
code_agent = CodeExecutorAgent(name="code_executor", code_executor=executor)
```

## Direct executor calls and cancellation

When calling the executor directly, pass `CodeBlock` objects and a `CancellationToken`.

```python
from autogen_core import CancellationToken
from autogen_core.code_executor import CodeBlock

result = await executor.execute_code_blocks(
    [CodeBlock(language="python", code="print(1 + 1)")],
    cancellation_token=CancellationToken(),
)
print(result.output)
```

`DockerCommandLineCodeExecutor` supports async context management, which starts and stops its container around the examples. For Docker setup and image behavior, see Microsoft's [command-line code executor guide](https://microsoft.github.io/autogen/stable/user-guide/core-user-guide/components/command-line-code-executors.html).
