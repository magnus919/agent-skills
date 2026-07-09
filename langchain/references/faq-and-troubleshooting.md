# LangChain FAQ and Troubleshooting

## Installation

**Q: Python version requirements?**
A: 3.10+. Python 3.11+ recommended.

**Q: Dependency conflicts?**
A: Use a virtual environment. Install core: `pip install langchain langchain-core`, then add integration packages as needed.

**Q: LangSmith API key setup?**
A: Set `LANGCHAIN_API_KEY`, `LANGCHAIN_TRACING_V2=true`, `LANGCHAIN_PROJECT=<name>`.

## Migration

**Q: Should I migrate from AgentExecutor?**
A: Yes, before Dec 2026. AgentExecutor is in maintenance mode. Use `create_agent` from `langchain.agents`.

**Q: create_agent vs create_react_agent?**
A: In LangChain v1.0+, use `create_agent` from `langchain.agents`. `create_react_agent` from `langgraph.prebuilt` is deprecated.

**Q: LLMChain migration?**
A: Replace `LLMChain(prompt=..., llm=...)` with LCEL: `prompt | model | parser`.

## Common Errors

**Q: Agent doesn't call tools**
A: Check: (1) type hints on parameters, (2) docstring descriptions, (3) `@tool` decorator, (4) `parse_docstring=True` if using Google-style docstrings.

**Q: Module not found for integration?**
A: Install each integration separately. Never `pip install langchain[all]` — it pulls 100+ unused deps.

**Q: Pydantic v1/v2 errors?**
A: LangChain v1.0 uses Pydantic v2. If integrations use v1 schemas, they may fail silently. Pin `pydantic>=2`.

**Q: Streaming agent hangs?**
A: Agents with tool calls cannot stream final output until all tools complete. Use `astream_events` filtering by event type.

**Q: Checkpoint serialization fails?**
A: Tools returning non-serializable objects (file handles, network connections) cannot be checkpointed. Ensure all tool outputs are JSON-serializable.

## Performance

| Issue | Fix |
|-------|-----|
| High latency | Use `chain.stream()` instead of `invoke()` |
| Rate limiting | Set `max_concurrency` in `RunnableConfig` |
| Cost spikes | Route simple queries to cheaper model (gpt-4o-mini) |
| Memory growth | Use LangGraph checkpointer with bounded thread history |
