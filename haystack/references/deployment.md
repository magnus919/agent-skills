# Haystack Deployment

## Hayhooks

Hayhooks turns Haystack pipelines into REST APIs:

```bash
pip install hayhooks
hayhooks run  # Starts server on port 1416
```

Deploy a pipeline:
```python
# deploy.py
from hayhooks import deploy
deploy("my_pipeline.yaml")  # Serialized pipeline YAML

# Then use curl:
# curl -X POST http://localhost:1416/my_pipeline \
#   -H "Content-Type: application/json" \
#   -d '{"text_embedder": {"text": "query"}}'
```

## MCP Server

Hayhooks also exposes pipelines as MCP servers, enabling any MCP client to use your Haystack pipeline as a tool.

## Containerization

```dockerfile
FROM python:3.11-slim
RUN pip install haystack hayhooks
COPY pipelines/ /app/pipelines/
CMD ["hayhooks", "run", "--host", "0.0.0.0"]
```

## Production Checklist

- [ ] Use a production document store (not InMemory)
- [ ] Separate indexing and query pipelines
- [ ] Set up Hayhooks for REST API access
- [ ] Add evaluation pipeline for monitoring
- [ ] Containerize with Docker
- [ ] Configure logging and error tracking
- [ ] Set up model caching to avoid reloading on every request
