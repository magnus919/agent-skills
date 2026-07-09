# LlamaIndex Integration Ecosystem

## Vector Stores

| Store | Production | Best For |
|-------|-----------|----------|
| Pinecone | Yes | Managed, high-scale |
| Qdrant | Yes | Self-hosted or managed |
| Weaviate | Yes | Hybrid search + graph |
| Chroma | Yes | Embeddings + metadata |
| pgvector | Yes | PostgreSQL native |
| Milvus | Yes | Billion-scale |
| SimpleVectorStore | No | Dev/test only |

```python
from llama_index.vector_stores.qdrant import QdrantVectorStore
from qdrant_client import QdrantClient

vector_store = QdrantVectorStore(
    client=QdrantClient(url="http://localhost:6333"),
    collection_name="my_docs",
)

index = VectorStoreIndex.from_documents(documents, vector_store=vector_store)
```

## LlamaHub Data Connectors

200+ data loaders available:

```python
pip install llama-index-readers-notion
from llama_index.readers.notion import NotionPageReader
documents = NotionPageReader(integration_token="...").load_data()
```

Available connectors include: PDFs, Notion, Confluence, Slack, GitHub, S3, JIRA, SAP, Salesforce, Google Drive, SQL databases, web pages, Discord, YouTube.

## LlamaParse Document Parsing

```python
pip install llama-parse
from llama_parse import LlamaParse

parser = LlamaParse(result_type="markdown",
    parsing_instruction="Extract tables and preserve layout.")
documents = parser.load_data("./complex_document.pdf")
```

Key capabilities: LLM-powered parsing, JSON output mode, multi-model support (GPT-4.1, Gemini 2.5 Pro), auto skew correction, MCP integration.

## LangChain Interoperability

```python
from llama_index.core.langchain_helpers.agents import (
    IndexToolConfig, LlamaIndexTool
)

tool_config = IndexToolConfig(
    query_engine=query_engine,
    name="vector_index",
    description="Useful for answering queries about documents",
)
rag_tool = LlamaIndexTool.from_tool_config(tool_config)
# Use rag_tool with any LangChain agent
```

## Framework Comparison

| Framework | Lead With | Best For | License |
|-----------|----------|----------|---------|
| **LlamaIndex** | Data ingestion + retrieval | RAG-heavy apps, heterogeneous sources | MIT |
| **LangChain + LangGraph** | Chain/graph abstractions | Multi-agent state machines, checkpoints | MIT |
| **Haystack** | Pipeline composition | Production NLP search pipelines | Apache 2.0 |
| **DSPy** | Compiled prompt programs | Optimization-driven prompt programming | MIT |

LlamaIndex excels when you have multiple data sources, multiple indexes, hybrid retrieval, and metadata filtering. For single-source, single-strategy RAG, the abstraction may not earn its weight.
