# AutoGen Agent Types

## AssistantAgent

The primary AI agent. Uses an LLM to generate responses.

```python
from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient

model_client = OpenAIChatCompletionClient(model="gpt-4o-mini")

assistant = AssistantAgent(
    name="assistant",
    system_message="You are a helpful AI assistant.",
    model_client=model_client,
)
```

## UserProxyAgent

Automated proxy that can execute code. Despite the name, NOT a human user by default.

```python
from autogen_agentchat.agents import UserProxyAgent

proxy = UserProxyAgent(
    name="proxy",
    human_input_mode="NEVER",  # "ALWAYS" for human-in-the-loop, "TERMINATE" to stop
    is_termination_msg=lambda msg: "TERMINATE" in (msg.get("content", "") or ""),
    code_executor=code_executor,
)
```

## Key Parameters

| Parameter | Description |
|-----------|-------------|
| `name` | Unique agent name |
| `system_message` | System prompt defining agent behavior |
| `human_input_mode` | "NEVER", "ALWAYS", or "TERMINATE" |
| `is_termination_msg` | Function to detect termination messages |
| `code_executor` | CodeExecutor for running generated code |
| `model_client` | LLM client (AssistantAgent only) |
| `tools` | Tools the agent can call |
