---
name: llamaindex
description: >-
  Expert skill for building LLM applications with the LlamaIndex framework —
  RAG pipelines, multi-agent orchestration, event-driven workflows, knowledge
  graph construction, production deployment, and evaluation. Use when working
  with LlamaIndex or comparing RAG and agent orchestration frameworks.
license: MIT
metadata:
  author: Magnus Hedemark
  version: 1.0.0
  source: https://github.com/run-llama/llama_index
---

# LlamaIndex Expert Skill

LlamaIndex is an MIT-licensed Python framework for building LLM applications over your data. In 2026, it has evolved from a RAG indexing library into an event-driven workflow framework with integrated production runtime (llama-deploy), agent orchestration (AgentWorkflow), knowledge graph construction (PropertyGraphIndex), and OpenTelemetry-native observability.

The framework is organized around seven core primitives: **Reader** (data loaders), **Document/Node** (chunked content model), **Index** (data structures over Nodes), **Retriever** (relevant Node selection), **Query Engine** (retriever + synthesis), **Agent** (LLM with tools), and **Workflow** (event-driven orchestration).

## Quick Reference

| Task | Approach | Reference |
|------|----------|-----------|
| Load data | `SimpleDirectoryReader("./data").load_data()` | `references/architecture.md` |
| Build vector index | `VectorStoreIndex.from_documents(docs)` | `references/rag-strategies.md` |
| Multi-agent orchestration | `AgentWorkflow(agents=[...])` | `references/agent-patterns.md` |
| Event-driven pipeline | `class MyFlow(Workflow): @step` | `references/workflows.md` |
| Production deployment | `deploy_workflow(workflow=MyFlow())` | `references/production-deployment.md` |
| Knowledge graph | `PropertyGraphIndex.from_documents(docs)` | `references/property-graph-index.md` |
| Evaluation | `FaithfulnessEvaluator().evaluate_response(...)` | `references/evaluation-observability.md` |
| Vector store setup | See integration docs | `references/integration-ecosystem.md` |

## When to Use This Skill

Load this skill any time you are:
- Building a RAG pipeline over enterprise or personal data
- Comparing LlamaIndex with LangChain, Haystack, or DSPy
- Designing multi-agent systems with handoff between specialist agents
- Deploying an LLM application to production with observability
- Constructing knowledge graphs from unstructured documents
- Debugging common LlamaIndex failures (retrieval miss, handoff bug, async issues)

## Reference Files

| Reference | Load when | File |
|-----------|-----------|------|
| Core Architecture | Understanding the 7 primitives, Settings, data flow | `references/architecture.md` |
| RAG Strategies | Building RAG pipelines from basic to advanced | `references/rag-strategies.md` |
| Agent Patterns | Multi-agent orchestration with AgentWorkflow | `references/agent-patterns.md` |
| Workflows | Event-driven step composition and durable execution | `references/workflows.md` |
| Production & Deployment | llama-deploy, debugging, failure modes | `references/production-deployment.md` |
| Property Graph Index | Knowledge graph construction and hybrid retrieval | `references/property-graph-index.md` |
| Evaluation & Observability | Metrics, tracing, span-attached scoring | `references/evaluation-observability.md` |
| Integration Ecosystem | Vector stores, LlamaHub, LlamaParse, ecosystem | `references/integration-ecosystem.md` |
| FAQ & Troubleshooting | Common errors and their fixes | `references/faq-and-troubleshooting.md` |

## Template Files

| Template | Purpose | File |
|----------|---------|------|
| Basic RAG | Minimal RAG pipeline in 10 lines | `templates/basic-rag.py` |
| Agentic RAG | Multi-source RAG with agent orchestration | `templates/agentic-rag.py` |
| Custom Workflow | Event-driven workflow with typed events | `templates/custom-workflow.py` |
| Production Deploy | llama-deploy wrapper for Workflow services | `templates/production-deploy.py` |

## Scripts

| Script | Purpose | File |
|--------|---------|------|
| check-setup | Verify LlamaIndex installation and configuration | `scripts/check-setup.py` |

## Common Gotchas

- **Async coroutines:** All Workflow step methods are async. Calling them synchronously silently returns a coroutine object without raising an error — you must `await` every step.
- **AgentWorkflow handoff bug:** After an agent hands off to another, the receiving agent may lose the user's request. Extend `FunctionAgent.take_step` to re-locate the last user message in chat history after handoff (see `references/agent-patterns.md` for the fix).
- **SimpleVectorStore is not for production:** It is in-memory only. Use Pinecone, Qdrant, Weaviate, or pgvector.
- **Missing reranker on hybrid retrieval:** Hybrid retrievers return more candidates than the synthesizer needs. Always apply a reranker (Cohere, Jina, ColBERT) as a node postprocessor.
- **Metadata filters prevent data leaks:** Without tenant-level metadata filters on the retriever, multi-tenant RAG systems leak data between tenants.
- **Instrument before instantiation:** Call `LlamaIndexInstrumentor().instrument()` before instantiating any workflow or the span tree will be incomplete.
- **llama-deploy needs Redis:** The control plane requires a running Redis instance. Without it, deployment succeeds silently but requests never route.
- **Workflow state is ephemeral by default:** Crash recovery requires explicit checkpoint snapshots via `Context.to_dict()`.

## Key Principles

1. **Decouple retrieval chunks from synthesis chunks.** The embedding representation that retrieves well differs from the context representation that generates well. Use `SentenceWindowNodeParser` + `MetadataReplacementNodePostProcessor` for this pattern.
2. **Rerank before you generate.** Hybrid retrieval + reranker is the minimum viable production RAG configuration.
3. **Agents are Workflows.** FunctionAgent and AgentWorkflow are pre-configured Workflows. You can always drop down to raw Workflow for custom control flow.
4. **Graphs are not just vector stores.** PropertyGraphIndex adds structural path traversal that vector similarity cannot provide — combine both for maximum retrieval quality.
5. **Evaluate in the same process.** Span-attached evaluation preserves the connection between the output and the retrieval context that produced it.

## When NOT to Use LlamaIndex

- Single-source, single-vector-store RAG with simple queries — the abstraction may not earn its weight
- Pure multi-agent state machines with frequent human-in-the-loop pauses — LangGraph is a better fit
- Production NLP search pipelines — Haystack's pipeline model is more mature for this use case
