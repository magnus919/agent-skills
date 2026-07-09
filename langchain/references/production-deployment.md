# LangChain Production Deployment

## LangSmith Observability

Enable tracing at startup — before any chain or agent execution:

```python
import os
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = "your-key"
os.environ["LANGCHAIN_PROJECT"] = "my-project"

# All chains and agents are now traced automatically
```

LangSmith provides:
- **Tracing:** Visualize every step in chain/agent execution
- **Debugging:** Inspect inputs, outputs, and intermediate state
- **Evaluation:** Systematic testing with datasets and annotators
- **Monitoring:** Production metrics, latency, error rates

## LangServe Deployment

Wrap an LCEL chain as a REST API:

```python
from langserve import add_routes
from fastapi import FastAPI

app = FastAPI()
add_routes(app, chain, path="/rag")

# Run: uvicorn main:app --port 8080
```

## LangSmith Deployment

Purpose-built infrastructure for running agents in production:

```python
# LangSmith Deployment handles:
# - Workflow orchestration with retry and back-pressure
# - Observability built in (auto-traced)
# - Horizontal scaling
# - Human-in-the-loop support
```

## Production Checklist

- [ ] Enable LangSmith tracing before any code execution
- [ ] Use `create_agent` — not deprecated AgentExecutor
- [ ] Set up error handling with `RunnableConfig(max_concurrency=...)`
- [ ] Implement caching for repeated queries
- [ ] Use smaller models (gpt-4o-mini) for simple tasks
- [ ] Configure metadata filters for multi-tenant isolation
- [ ] Set up production monitoring in LangSmith
- [ ] Use environment variables for all secrets

## Common Production Issues

| Issue | Cause | Fix |
|-------|-------|-----|
| High latency | No streaming | Use `chain.stream()` instead of `invoke()` |
| Rate limiting | Too many concurrent requests | Set `max_concurrency` in RunnableConfig |
| Cost spikes | Large model for simple tasks | Route simple queries to smaller model |
| Hallucination | No retrieval grounding | Add RAG chain with verified sources |
