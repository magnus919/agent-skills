#!/usr/bin/env python3
"""
Minimal RAG pipeline using LlamaIndex.
Loads documents from a directory, builds a vector index, and answers queries.
"""

from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.llms.openai import OpenAI
from llama_index.core import Settings

# --- Configuration ---
Settings.llm = OpenAI(model="gpt-4o-mini")
DATA_DIR = "./data"

# --- Load ---
documents = SimpleDirectoryReader(DATA_DIR).load_data()

# --- Index ---
index = VectorStoreIndex.from_documents(documents)

# --- Query ---
query_engine = index.as_query_engine(
    similarity_top_k=5,
)

response = query_engine.query("What does this data say about your question?")
print(f"Answer: {response}")

# Show sources
for source in response.source_nodes:
    print(f"  [{source.score:.3f}] {source.text[:100]}...")
