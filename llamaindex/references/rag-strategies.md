# LlamaIndex RAG Strategies

## Basic RAG

```python
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader

documents = SimpleDirectoryReader("./data").load_data()
index = VectorStoreIndex.from_documents(documents)
query_engine = index.as_query_engine()
response = query_engine.query("Your question here")
```

## Chunking Strategies

| Parser | Best For | Configuration |
|--------|----------|---------------|
| `SentenceSplitter` | General prose | `chunk_size=1024, chunk_overlap=20` |
| `SemanticSplitterNodeParser` | Coherent semantic units | `breakpoint_percentile_threshold=95` |
| `HierarchicalNodeParser` | Large documents | `chunk_sizes=[2048, 512, 128]` |
| `SentenceWindowNodeParser` | Embedding precision + synthesis context | `window_size=3` |

## Decoupling Retrieval from Synthesis

```python
from llama_index.core.node_parser import SentenceWindowNodeParser
from llama_index.core.postprocessor import MetadataReplacementNodePostProcessor

node_parser = SentenceWindowNodeParser.from_defaults(
    window_size=3,
    window_metadata_key="window",
    original_text_metadata_key="original_sentence",
)

postprocessor = MetadataReplacementNodePostProcessor(
    target_metadata_key="window"
)
```

## Hybrid Retrieval

```python
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.core import QueryBundle

# Hybrid via supported vector stores (Weaviate, Qdrant, Pinecone)
vector_retriever = index.as_retriever(similarity_top_k=10)

# Add BM25 retriever for keyword matching
from llama_index.core.retrievers import BM25Retriever
bm25_retriever = BM25Retriever.from_defaults(
    index=index, similarity_top_k=10
)
```

## Reranking

Always apply a reranker on hybrid retrieval output:

```python
from llama_index.core.postprocessor.cohere_rerank import CohereRerank

rerank = CohereRerank(top_n=5)
query_engine = index.as_query_engine(
    similarity_top_k=10,
    node_postprocessors=[rerank],
)
```

## Metadata Filters

```python
from llama_index.core.vector_stores import MetadataFilters, ExactMatchFilter

filters = MetadataFilters(
    filters=[ExactMatchFilter(key="tenant_id", value="acme_corp")]
)
query_engine = index.as_query_engine(filters=filters)
```

## Recursive Retrieval for Large Corpora

Two-level retrieval: document summaries -> chunks.

```python
from llama_index.core.retrievers import RecursiveRetriever

retriever_chunk = RecursiveRetriever(
    "vector",
    retriever_dict={"vector": vector_retriever_chunk},
    node_dict=all_nodes_dict,
)
```

## RouterQueryEngine

Route queries to different strategies based on intent:

```python
from llama_index.core.query_engine import RouterQueryEngine
from llama_index.core.selectors import PydanticSingleSelector

query_engine = RouterQueryEngine(
    selector=PydanticSingleSelector.from_defaults(),
    query_engine_tools=[summary_tool, vector_tool],
)
```

## Chunk Size Optimization with ParamTuner

```python
from llama_index.core.param_tuner.base import ParamTuner

param_tuner = ParamTuner(
    param_fn=objective_function,
    param_dict={"chunk_size": [256, 512, 1024]},
    fixed_param_dict={"top_k": 2},
)
results = param_tuner.tune()
best_chunk_size = results.best_run_result.params["chunk_size"]
```
