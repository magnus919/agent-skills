# LangChain — LLM Application Framework

An expert-level skill for building LLM-powered applications with LangChain — the most widely adopted LLM orchestration framework. LCEL chains, RAG pipelines, agents, LangSmith observability, and LangServe deployment.

## Why Install This Skill

When your agent loads this skill, it becomes a **LangChain expert** who can:

- **Build chains with LCEL** — `prompt | model | parser` composition with the Runnable interface
- **Create agents** — `create_agent` with tools (not legacy AgentExecutor)
- **Implement RAG pipelines** — document loading, splitting, embedding, retrieval, generation
- **Add observability** — LangSmith tracing for production debugging
- **Deploy with LangServe** — REST API deployment for production

## What You Get

| Directory | Purpose |
|-----------|---------|
| `SKILL.md` | Core principles, pipeline modes, where-to-start table, quick reference |
| `references/` | LCEL reference, RAG strategies, agent patterns, LangSmith, LangServe, framework comparisons |

## Framework Comparison

LangChain is the broadest LLM framework with 1000+ integrations. Its agents now run on LangGraph underneath. Use LangChain for rapid prototyping and broad integration support; drop to LangGraph when you need full state-machine control.

## Requirements

Python 3.8+ with `langchain`, `langchain-community`, and provider-specific packages.
