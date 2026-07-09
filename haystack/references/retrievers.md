# Haystack Retrievers

## Embedding Retrieval

```python
from haystack.components.embedders import SentenceTransformersTextEmbedder
from haystack.components.retrievers.in_memory import InMemoryEmbeddingRetriever

# Indexing pipeline uses SentenceTransformersDocumentEmbedder
# Query pipeline uses:
text_embedder = SentenceTransformersTextEmbedder(model="sentence-transformers/all-MiniLM-L6-v2")
retriever = InMemoryEmbeddingRetriever(document_store=document_store, top_k=5)
```

## BM25 Retrieval (Keyword)

```python
from haystack.components.retrievers.in_memory import InMemoryBM25Retriever

bm25_retriever = InMemoryBM25Retriever(document_store=document_store, top_k=5)
```

## Hybrid Retrieval

Run BM25 and embedding retrieval in parallel, merge results:

```python
from haystack.components.joiners import DocumentJoiner

pipeline.add_component("bm25_retriever", InMemoryBM25Retriever(document_store=doc_store))
pipeline.add_component("embedding_retriever", InMemoryEmbeddingRetriever(document_store=doc_store))
pipeline.add_component("joiner", DocumentJoiner(join_mode="concatenate"))  # or "merge"

pipeline.connect("text_embedder.embedding", "embedding_retriever.query_embedding")
pipeline.connect("bm25_retriever.documents", "joiner.documents")
pipeline.connect("embedding_retriever.documents", "joiner.documents")
```

## Reranking

Add a ranker after retrieval:

```python
from haystack_integrations.components.rankers.cohere import CohereRanker

pipeline.add_component("ranker", CohereRanker(model="rerank-english-v3.0", top_k=3))
pipeline.connect("joiner.documents", "ranker.documents")
pipeline.connect("ranker.documents", "prompt_builder.documents")
```

## Retriever Selection Guide

| Retriever | When to use |
|-----------|-------------|
| EmbeddingRetriever | Semantic search, conceptual queries |
| BM25Retriever | Keyword search, exact phrase matching |
| Hybrid (both + joiner) | Production RAG — best of both worlds |
| + Ranker after hybrid | Highest quality, adds latency |
