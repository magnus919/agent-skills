# LangChain Callbacks

The callbacks system provides real-time hooks into every stage of chain and agent execution. Use it for custom logging, monitoring, token tracking, and debugging.

## BaseCallbackHandler

```python
from langchain_core.callbacks import BaseCallbackHandler

class MyHandler(BaseCallbackHandler):
    def on_llm_start(self, serialized: dict, prompts: list[str], **kwargs) -> None:
        print(f"LLM starting with {len(prompts)} prompts")

    def on_llm_end(self, response, **kwargs) -> None:
        text = response.generations[0][0].text[:50]
        print(f"LLM finished: {text}...")

    def on_tool_start(self, serialized: dict, input_str: str, **kwargs) -> None:
        print(f"Tool: {serialized.get('name')}")

    def on_tool_end(self, output: str, **kwargs) -> None:
        print(f"Tool output: {str(output)[:100]}")

    def on_retriever_start(self, query: str, **kwargs) -> None:
        print(f"Retrieving: {query}")

    def on_retriever_end(self, documents: list, **kwargs) -> None:
        print(f"Retrieved {len(documents)} documents")
```

## Event Reference

| Event | Arguments | When |
|-------|-----------|------|
| `on_llm_start` | serialized, prompts | Model called |
| `on_llm_end` | response | Model returns |
| `on_llm_error` | error, kwargs | Model exception |
| `on_chat_model_start` | serialized, messages | Chat model called |
| `on_chain_start` | serialized, inputs | Chain step begins |
| `on_chain_end` | outputs | Chain step completes |
| `on_tool_start` | serialized, input_str | Tool invoked |
| `on_tool_end` | output | Tool returns |
| `on_tool_error` | error, kwargs | Tool exception |
| `on_retriever_start` | query | Retrieval begins |
| `on_retriever_end` | documents | Retrieval completes |
| `on_text` | text | Custom log messages |

## Using Callbacks

### Per-Invocation

```python
handler = MyHandler()
chain.invoke({"q": "Hello"}, config={"callbacks": [handler]})
```

### Global Verbose Mode

```python
from langchain_core.globals import set_verbose
set_verbose(True)  # Print all callbacks to stdout
```

## Practical: Audit Agent Tool Calls

```python
from langchain_core.callbacks import BaseCallbackHandler

class AgentAuditHandler(BaseCallbackHandler):
    def on_tool_start(self, serialized: dict, input_str: str, **kwargs) -> None:
        print(f"  calling tool: {serialized.get('name')}")
        print(f"  with input: {input_str[:120]}")
    def on_tool_end(self, output: str, **kwargs) -> None:
        print(f"  tool returned: {str(output)[:120]}")
    def on_retriever_end(self, documents: list, **kwargs) -> None:
        print(f"  retrieved {len(documents)} docs")

agent = create_agent(model, tools)
result = agent.invoke(
    {"messages": [("user", "Research LangChain")]},
    config={"callbacks": [AgentAuditHandler()]}
)
```

## Async Callbacks

```python
from langchain_core.callbacks import AsyncCallbackHandler

class AsyncAuditHandler(AsyncCallbackHandler):
    async def on_llm_start(self, serialized, prompts, **kwargs):
        print("LLM starting...")
    async def on_tool_end(self, output, **kwargs):
        print(f"Tool done: {str(output)[:80]}")
```

## LangSmith Integration

When LangSmith tracing is enabled (`LANGCHAIN_TRACING_V2=true`), all callback events are automatically captured as trace spans. Custom callbacks add additional instrumentation on top — e.g., sending metrics to a custom dashboard while LangSmith handles the canonical trace.
