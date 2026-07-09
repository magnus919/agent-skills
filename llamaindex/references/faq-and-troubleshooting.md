# LlamaIndex FAQ and Troubleshooting

## Installation

**Q: Installation fails with dependency conflicts?**
A: Use a virtual environment. Install core first: `pip install llama-index-core`, then add integrations: `pip install llama-index-llms-openai llama-index-vector-stores-qdrant`.

**Q: Python version requirements?**
A: LlamaIndex 0.14+ requires Python 3.9+.

## Common Errors

**Q: "Coroutine object was never awaited"**
A: All Workflow step methods are async. You forgot `await` before the step call or `w.run()`. Add `await` to the call site.

**Q: Agent doesn't respond after handoff**
A: Known AgentWorkflow handoff bug. The user's request was pushed out of ChatMemory. Apply the take_step fix from the agent-patterns reference.

**Q: llama-deploy deployed but requests time out**
A: Redis isn't running or isn't reachable. Start `redis-server` and verify the control plane can connect. Check that the REDIS_URL env var matches the service configuration.

**Q: Retrieval quality is poor despite hybrid search**
A: Missing reranker. Hybrid retrieval returns more candidates than the synthesizer needs. Add CohereRerank or ColbertRerank as a node postprocessor.

**Q: Spans are missing or incomplete in observability UI**
A: Instrumentation was called after workflow instantiation. Move `LlamaIndexInstrumentor().instrument()` to before any Workflow subclass instantiation.

## Performance

**Q: Indexing is slow for large document sets**
A: Enable async mode, increase worker count in IngestionPipeline, and consider batched document loading. For very large sets, use the IngestionPipeline.run() with show_progress=True to monitor.

**Q: Memory usage grows unbounded**
A: The embedding cache accumulates. Monitor with `cache.get_size()` and clear periodically with `cache.clear()`. Consider a bounded cache implementation.

**Q: How many chunks should I use per document?**
A: Use the ParamTuner for systematic optimization: search across chunk sizes (256, 512, 1024) and evaluate against your query set. There is no one-size-fits-all answer.

## Design Decisions

**Q: Should I use Workflows or Query Pipelines?**
A: Workflows. Query Pipelines are deprecated in 0.14+. Use Workflows for any workload more complex than a single-shot query.

**Q: Should I use FunctionAgent or ReActAgent?**
A: FunctionAgent if your model supports native function calling (GPT-4, Claude 3, Gemini). ReActAgent if it doesn't (smaller open models).

**Q: Should I use PropertyGraphIndex or KnowledgeGraphIndex?**
A: PropertyGraphIndex. KnowledgeGraphIndex is deprecated. PGI supports labeled nodes, relationship properties, embeddings, Cypher queries, and combined concurrent retrieval strategies.

**Q: Should I use Settings or ServiceContext?**
A: Settings. ServiceContext is deprecated. Settings provides a single import with global configuration.
