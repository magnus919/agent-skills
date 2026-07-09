#!/usr/bin/env python3
"""Hybrid RAG pipeline — BM25 + embedding in parallel."""

from haystack import Pipeline
from haystack.components.embedders import SentenceTransformersTextEmbedder
from haystack.components.retrievers.in_memory import InMemoryEmbeddingRetriever, InMemoryBM25Retriever
from haystack.components.joiners import DocumentJoiner
from haystack.components.builders import PromptBuilder
from haystack.components.generators import OpenAIGenerator
from haystack.document_stores.in_memory import InMemoryDocumentStore

document_store = InMemoryDocumentStore()

pipeline = Pipeline()
pipeline.add_component("text_embedder", SentenceTransformersTextEmbedder())
pipeline.add_component("bm25_retriever", InMemoryBM25Retriever(document_store=document_store, top_k=5))
pipeline.add_component("embedding_retriever", InMemoryEmbeddingRetriever(document_store=document_store, top_k=5))
pipeline.add_component("joiner", DocumentJoiner(join_mode="merge"))
pipeline.add_component("prompt_builder", PromptBuilder(
    template="Context:\n{{documents}}\n\nQuestion: {{question}}\nAnswer:"
))
pipeline.add_component("generator", OpenAIGenerator())

pipeline.connect("text_embedder.embedding", "embedding_retriever.query_embedding")
pipeline.connect("bm25_retriever.documents", "joiner.documents")
pipeline.connect("embedding_retriever.documents", "joiner.documents")
pipeline.connect("joiner.documents", "prompt_builder.documents")
pipeline.connect("prompt_builder", "generator")

result = pipeline.run({
    "text_embedder": {"text": "hybrid search query"},
    "bm25_retriever": {"query": "hybrid search query"},
    "prompt_builder": {"question": "hybrid search query"}
})
print(result["generator"]["replies"][0])
