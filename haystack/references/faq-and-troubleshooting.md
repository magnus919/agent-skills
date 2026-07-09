# Haystack FAQ and Troubleshooting

## Installation

**Q: Installation fails?**
A: `pip install haystack-ai` (not `haystack` — that's an older, deprecated package).

**Q: Module not found for integration?**
A: Install integration packages separately: `pip install elasticsearch-haystack pinecone-haystack weaviate-haystack chroma-haystack`.

## Common Errors

**Q: Pipeline.run() returns empty results?**
A: Check that your indexing pipeline actually ran and wrote documents. Verify with `document_store.count_documents()`.

**Q: "Component X has no output slot Y"?**
A: Connection mismatch. Each component has typed input/output slots. Check the component's documentation for slot names.

**Q: Prompt rendering issues?**
A: PromptBuilder uses Jinja2. Variable names must match what you pass in `pipeline.run()`. `{{documents}}` vs `{{docs}}` is a common error.

**Q: Embedding mismatch between indexing and query?**
A: Use the same model in both `SentenceTransformersDocumentEmbedder` and `SentenceTransformersTextEmbedder`. Different models produce incompatible embeddings.

## Performance

**Q: Retrieval too slow?**
A: For production, use a vector database with ANN indexing (Elasticsearch, Pinecone, Weaviate). InMemory scales poorly beyond ~100K documents.

**Q: Pipeline warm-up too slow?**
A: Model loading happens on `warm_up()`. For production, warm up once and reuse the pipeline instance.

## Deployment

**Q: How to deploy Haystack?**
A: Use Hayhooks. Serialize your pipeline to YAML, deploy via Hayhooks REST API.

**Q: Can I use multiple pipelines?**
A: Yes — run separate Hayhooks instances or use a proxy to route requests.
