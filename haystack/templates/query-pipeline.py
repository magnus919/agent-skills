#!/usr/bin/env python3
"""Haystack query pipeline — retrieve, prompt, generate."""

from haystack import Pipeline
from haystack.components.embedders import SentenceTransformersTextEmbedder
from haystack.components.retrievers.in_memory import InMemoryEmbeddingRetriever
from haystack.components.builders import PromptBuilder
from haystack.components.generators import OpenAIGenerator
from haystack.document_stores.in_memory import InMemoryDocumentStore

# Assume document_store already has documents
document_store = InMemoryDocumentStore()

pipeline = Pipeline()
pipeline.add_component("text_embedder", SentenceTransformersTextEmbedder())
pipeline.add_component("retriever", InMemoryEmbeddingRetriever(document_store=document_store, top_k=5))
pipeline.add_component("prompt_builder", PromptBuilder(
    template="Answer based on the context.\n\nContext: {{documents}}\n\nQuestion: {{question}}\nAnswer:"
))
pipeline.add_component("generator", OpenAIGenerator())

pipeline.connect("text_embedder.embedding", "retriever.query_embedding")
pipeline.connect("retriever.documents", "prompt_builder.documents")
pipeline.connect("prompt_builder", "generator")

result = pipeline.run({
    "text_embedder": {"text": "What is Haystack?"},
    "prompt_builder": {"question": "What is Haystack?"}
})
print(result["generator"]["replies"][0])
