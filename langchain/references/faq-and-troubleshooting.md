# LangChain FAQ and Troubleshooting

## Installation

**Q: Installation fails with dependency conflicts?**
A: Use a virtual environment. Install core: `pip install langchain langchain-core`, then add integrations as needed.

**Q: Python version requirements?**
A: LangChain v1.x requires Python 3.10+. Python 3.11+ recommended.

## Common Errors

**Q: "ModuleNotFoundError: No module named 'langchain_openai'"**
A: Install the integration package: `pip install langchain-openai`

**Q: Agent doesn't call tools**
A: Ensure tool functions have: (1) type hints on parameters, (2) descriptive docstrings, (3) `@tool` decorator.

**Q: LangSmith traces not appearing**
A: Set `LANGCHAIN_TRACING_V2=true` and `LANGCHAIN_API_KEY` before any chain execution. Must be done at module import time.

**Q: "Cannot use 'pipe' with non-Runnable"**
A: All components in an LCEL chain must implement the Runnable interface. Use `RunnableLambda` to wrap plain functions.

**Q: Chain returns no output**
A: Missing output parser. Add `StrOutputParser()` or another parser at the end of your chain.

## Migration

**Q: Should I migrate from AgentExecutor?**
A: Yes. AgentExecutor is in maintenance mode until Dec 2026. Use `create_agent` for new code. Existing AgentExecutor code continues to work until then.

**Q: How do I migrate from LLMChain?**
A: Replace `LLMChain(prompt=..., llm=...)` with LCEL: `prompt | model | parser`.

## Performance

**Q: Chain execution is slow**
A: Use streaming: `chain.stream()` returns tokens incrementally. Enable async: `await chain.ainvoke()`.

**Q: Memory usage grows unbounded**
A: Use LangGraph's checkpointer with bounded thread history instead of legacy in-memory buffers.
