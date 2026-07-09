# LlamaIndex Production Deployment

## llama-deploy: Distributed Runtime

```python
import asyncio
from llama_deploy import deploy_workflow, WorkflowServiceConfig, ControlPlaneConfig

async def main():
    await deploy_workflow(
        workflow=SimpleRAG(timeout=60),
        workflow_config=WorkflowServiceConfig(service_name="simple_rag"),
        control_plane_config=ControlPlaneConfig(),
    )
```

Requirements:
- Redis (or compatible message queue) for the control plane
- Worker processes registering with the control plane
- API gateway for HTTP routing

## Debugging

### Debug Logging

```python
import logging, sys
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
```

### Callback Handler

```python
from llama_index.core import set_global_handler
set_global_handler("simple")  # Prints event trace
```

### OpenTelemetry Tracing

```python
pip install traceai-llamaindex
```

```python
from fi_instrumentation import register
from traceai_llamaindex import LlamaIndexInstrumentor

trace_provider = register(project_name="rag_app")
LlamaIndexInstrumentor().instrument(tracer_provider=trace_provider)
```

## Common Production Failures

| Failure | Symptom | Root Cause | Fix |
|---------|---------|------------|-----|
| Retrieval miss | Poor answer quality | No reranker on hybrid retrieval | Add Cohere/ColBERT reranker |
| Cross-tenant leak | Wrong data returned | Missing metadata filters | Wire filters at retriever level |
| Async coroutine bug | Workflow doesn't run | Forgot `await` | Ensure all steps are awaited |
| llama-deploy silent failure | No response | No Redis running | Start redis-server first |
| Incomplete traces | Missing spans | Instrumentation called too late | Call instrument() before instantiation |
| Handoff failure | Agent doesn't respond | ChatMemory overflow | Extend FunctionAgent.take_step() |

## Production Configuration Checklist

- [ ] Use a managed vector store (Pinecone, Qdrant, pgvector) — not SimpleVectorStore
- [ ] Apply SemanticSplitterNodeParser for adaptive chunking
- [ ] Add reranker (Cohere, Jina, ColBERT) on all hybrid retrieval
- [ ] Wire metadata filters at retriever level for multi-tenant isolation
- [ ] Enable async mode for concurrent operations
- [ ] Instrument observability before workflow instantiation
- [ ] Configure Redis for llama-deploy
- [ ] Set up span-attached evaluation for continuous quality monitoring
