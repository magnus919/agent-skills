# Haystack — Production Search & NLP Pipelines (deepset)

An expert-level skill for building **production search and NLP pipelines** with Haystack. Pipelines are validated DAGs with typed components and explicit connections.

## Why Install This Skill

When your agent loads this skill, it becomes a Haystack expert who can:

- **Design pipeline DAGs** — add_component + connect with typed input/output slots
- **Build RAG pipelines** — document indexing + query pipelines with embedding retrieval
- **Create agentic systems** — tool-using agents with ReAct pattern
- **Integrate generative AI** — PromptBuilder (Jinja2) + LLM generators
- **Evaluate pipeline quality** — faithfulness, relevancy, and custom metrics
- **Deploy with Hayhooks** — REST API deployment for production

## What You Get

| Directory | Purpose |
|-----------|---------|
| `SKILL.md` | Core paradigm, where-to-start table, framework comparison |
| `references/` | Deep dives into pipeline design, RAG, agents, evaluation, Hayhooks, and framework comparisons |

## Framework Comparison

Haystack uses explicit Pipeline DAGs (add_component + connect) — different from LangChain's LCEL pipe operator and LlamaIndex's query engines. Pipelines are validated at declaration time.

## Requirements

Python 3.8+ with `haystack-ai` package.
