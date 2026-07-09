#!/usr/bin/env python3
"""Haystack indexing pipeline — load, split, embed, write."""

from haystack import Pipeline
from haystack.components.converters import TextFileToDocument
from haystack.components.preprocessors import DocumentSplitter
from haystack.components.embedders import SentenceTransformersDocumentEmbedder
from haystack.components.writers import DocumentWriter
from haystack.document_stores.in_memory import InMemoryDocumentStore

document_store = InMemoryDocumentStore()

pipeline = Pipeline()
pipeline.add_component("converter", TextFileToDocument())
pipeline.add_component("splitter", DocumentSplitter(split_by="word", split_length=500, split_overlap=50))
pipeline.add_component("embedder", SentenceTransformersDocumentEmbedder())
pipeline.add_component("writer", DocumentWriter(document_store=document_store))

pipeline.connect("converter.documents", "splitter.documents")
pipeline.connect("splitter.documents", "embedder.documents")
pipeline.connect("embedder.documents", "writer.documents")

result = pipeline.run({"converter": {"sources": ["docs.txt"]}})
print(f"Indexed {document_store.count_documents()} documents")
