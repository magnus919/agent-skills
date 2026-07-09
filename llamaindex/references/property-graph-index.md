# LlamaIndex PropertyGraphIndex

## Overview

The `PropertyGraphIndex` replaces the deprecated `KnowledgeGraphIndex`. It uses labeled property graphs with typed nodes, relationship properties, embedding support, and Cypher query capability.

```python
from llama_index.core import PropertyGraphIndex

index = PropertyGraphIndex.from_documents(documents)
retriever = index.as_retriever()
query_engine = index.as_query_engine()
```

## Graph Construction Extractors

| Extractor | Approach | When to Use |
|-----------|----------|-------------|
| `SimpleLLMPathExtractor` | LLM extracts triples (entity, relation, entity) | Free-form exploration |
| `ImplicitPathExtractor` | Uses document structure metadata | No LLM needed |
| `DynamicLLMPathExtractor` | LLM with allowed type hints | Semi-guided extraction |
| `SchemaLLMPathExtractor` | Strict Pydantic schema validation | Production: guarantees type consistency |

### Schema-Guided Extraction

```python
from typing import Literal
from llama_index.core.indices.property_graph import SchemaLLMPathExtractor

entities = Literal["PERSON", "PLACE", "THING"]
relations = Literal["PART_OF", "HAS", "IS_A"]
schema = {
    "PERSON": ["PART_OF", "HAS", "IS_A"],
    "PLACE": ["PART_OF", "HAS"],
    "THING": ["IS_A"],
}

extractor = SchemaLLMPathExtractor(
    possible_entities=entities,
    possible_relations=relations,
    kg_validation_schema=schema,
    strict=True,
    max_triplets_per_chunk=10,
)

index = PropertyGraphIndex.from_documents(documents, kg_extractors=[extractor])
```

## Retrieval Strategies (Can Be Combined)

| Retriever | How It Works |
|-----------|-------------|
| `LLMSynonymRetriever` | LLM generates keywords/synonyms, finds matching nodes |
| `VectorContextRetriever` | Embedding similarity on graph nodes |
| `TextToCypherRetriever` | LLM generates Cypher from schema + query |
| `CypherTemplateRetriever` | Template with LLM-inferred params |
| `CustomPGRetriever` | Subclass for custom traversal |

### Combined Hybrid Retrieval

```python
from llama_index.core.indices.property_graph import (
    VectorContextRetriever, LLMSynonymRetriever, PGRetriever
)

retriever = PGRetriever(sub_retrievers=[
    VectorContextRetriever(index.property_graph_store),
    LLMSynonymRetriever(index.property_graph_store),
])
nodes = retriever.retrieve("query")
```

## Backing Stores

| Store | Embedding Support | Best For |
|-------|-----------------|----------|
| `SimplePropertyGraphStore` | No (use external) | Development |
| `Neo4jPropertyGraphStore` | Yes (native) | Production |
| `FalkorDBPropertyGraphStore` | Yes | High-performance graph |
| `TiDBPropertyGraphStore` | Yes | SQL + graph hybrid |

## Persistence

```python
index.storage_context.persist("./storage")

# Load
from llama_index.core import StorageContext, load_index_from_storage
index = load_index_from_storage(
    StorageContext.from_defaults(persist_dir="./storage")
)
```
