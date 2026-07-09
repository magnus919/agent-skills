# Haystack Document Stores

Document stores are the persistence layer. All share the same write/query interface.

## Available Stores

| Store | Production | Setup |
|-------|-----------|-------|
| `InMemoryDocumentStore` | Dev only | Built-in, no setup |
| `ElasticsearchDocumentStore` | Yes | `pip install elasticsearch-haystack`, running ES cluster |
| `PineconeDocumentStore` | Yes | `pip install pinecone-haystack`, API key |
| `WeaviateDocumentStore` | Yes | `pip install weaviate-haystack`, running Weaviate |
| `PGVectorStore` | Yes | `pip install pgvector-haystack`, PostgreSQL instance |
| `ChromaDocumentStore` | Dev | `pip install chroma-haystack` |

## Common Operations

```python
# Write documents
from haystack.document_stores.in_memory import InMemoryDocumentStore
from haystack import Document

doc_store = InMemoryDocumentStore()
doc_store.write_documents([
    Document(content="Haystack is a framework for building search systems."),
    Document(content="It uses pipeline-based architecture.")
])

# Query (BM25 by default)
results = doc_store.query("What is Haystack?", top_k=3)
```

## Metadata Filtering

```python
from haystack.document_stores.filters import document_store_filter

filtered = doc_store.filter_documents({
    "field": "meta.source",
    "operator": "==",
    "value": "internal"
})
```

## Store Selection Guide

- **InMemoryDocumentStore** — prototyping, testing, small datasets
- **ElasticsearchDocumentStore** — production search at scale, full-text + vector
- **PineconeDocumentStore** — serverless vector search, large-scale embedding retrieval
- **WeaviateDocumentStore** — hybrid search with built-in vectorization
- **PGVectorStore** — if you already use PostgreSQL, minimal infrastructure overhead
