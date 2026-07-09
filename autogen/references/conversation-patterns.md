# AutoGen Conversation Patterns

## Two-Agent Chat

```python
from autogen_agentchat.agents import AssistantAgent, UserProxyAgent

assistant = AssistantAgent(name="assistant", model_client=model_client)
proxy = UserProxyAgent(name="proxy", human_input_mode="NEVER")

result = proxy.initiate_chat(assistant, message="What is AutoGen?", max_turns=2)
print(result.summary)
```

## Termination Conditions

Prevent infinite loops:

```python
proxy = UserProxyAgent(
    name="proxy",
    human_input_mode="NEVER",
    is_termination_msg=lambda msg: "TERMINATE" in (msg.get("content", "") or ""),
    max_consecutive_auto_reply=5,
)

# Or limit turns at chat level
result = proxy.initiate_chat(assistant, message="Hello", max_turns=10)
```

## Cancellation Tokens

```python
from autogen_core import CancellationToken

token = CancellationToken()
# Token can be used to cancel long-running operations
```

## Nested Chats

Agent delegates work to a sub-conversation:

```python
async def research_topic(query: str) -> str:
    researcher = AssistantAgent(name="researcher", model_client=model_client)
    fact_checker = AssistantAgent(name="fact_checker", model_client=model_client)
    proxy = UserProxyAgent(name="proxy", human_input_mode="NEVER")
    result = await proxy.initiate_chat(
        researcher, message=f"Research: {query}", max_turns=5
    )
    return result.summary

# Register as a function the main agent can call
assistant.register_function(function_map={"research": research_topic})
```
