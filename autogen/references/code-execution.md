# AutoGen Code Execution

## Docker (Recommended)

Safe execution of LLM-generated code in isolated containers:

```python
from autogen_ext.code_executors.docker import DockerCommandLineCodeExecutor

executor = DockerCommandLineCodeExecutor(work_dir="coding")
async with executor:
    # Use within GroupChat
    proxy = UserProxyAgent(
        name="proxy",
        code_executor=executor,
        human_input_mode="NEVER",
    )
```

## Local (Development Only)

Runs generated code on your machine — use only for trusted environments:

```python
from autogen_ext.code_executors.local import LocalCommandLineCodeExecutor

executor = LocalCommandLineCodeExecutor(work_dir="coding")
```

## Cancellation

```python
from autogen_core import CancellationToken

token = CancellationToken()
result = await executor.execute_code_blocks(code_blocks, cancellation_token=token)
# Cancel via: token.cancel()
```

## Best Practices

- Use Docker for any untrusted code execution
- Set a `work_dir` to isolate generated files
- Always pass a `CancellationToken` for long-running tasks
- Monitor `max_turns` to prevent runaway code generation
