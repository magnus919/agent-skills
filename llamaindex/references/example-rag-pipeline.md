# End-to-End RAG Pipeline — Worked Example

This example shows a complete LlamaIndex RAG pipeline from data loading through production evaluation. It demonstrates the expected output depth for the Full pipeline mode.

## Scenario

A directory of technical PDF documentation about a REST API. We need to build a production RAG pipeline that answers developer questions with citations.

## Pipeline

### 1. Ingest — Load Documents

```python
from llama_index.core import SimpleDirectoryReader, Settings
from llama_index.llms.openai import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding

Settings.llm = OpenAI(model="gpt-4o-mini")
Settings.embed_model = OpenAIEmbedding(model="text-embedding-3-small")

documents = SimpleDirectoryReader("./api-docs/").load_data()
print(f"Loaded {len(documents)} documents")
# Output: Loaded 12 documents
```

### 2. Chunk — Semantic Splitting

```python
from llama_index.core.node_parser import SemanticSplitterNodeParser

splitter = SemanticSplitterNodeParser(
    embed_model=Settings.embed_model,
    breakpoint_percentile_threshold=95,
    buffer_size=1,
)
nodes = splitter.get_nodes_from_documents(documents)
print(f"Created {len(nodes)} chunks")
# Output: Created 347 chunks
```

### 3. Index — Vector + Hybrid

```python
from llama_index.core import VectorStoreIndex
from llama_index.core.retrievers import BM25Retriever

# Build vector index
index = VectorStoreIndex(nodes=nodes)

# Create retrievers for hybrid search
vector_retriever = index.as_retriever(similarity_top_k=10)
bm25_retriever = BM25Retriever.from_defaults(index=index, similarity_top_k=10)
```

### 4. Retrieve — Hybrid + Rerank

```python
from llama_index.core.retrievers import QueryFusionRetriever
from llama_index.core.postprocessor.cohere_rerank import CohereRerank
from llama_index.core.query_engine import RetrieverQueryEngine

# Fusion retriever with reciprocal rank fusion
hybrid_retriever = QueryFusionRetriever(
    retrievers=[vector_retriever, bm25_retriever],
    similarity_top_k=5,
    num_queries=1,  # Use original query only
    mode="reciprocal_rerank",
)

# Reranker
reranker = CohereRerank(top_n=5)

# Query engine
query_engine = RetrieverQueryEngine.from_args(
    retriever=hybrid_retriever,
    node_postprocessors=[reranker],
)
```

### 5. Agent — Query with Multi-Source Routing (Optional)

```python
from llama_index.core.agent.workflow import FunctionAgent
from llama_index.core.tools import QueryEngineTool

rag_tool = QueryEngineTool.from_defaults(
    query_engine=query_engine,
    name="api_docs_search",
    description="Search API documentation for endpoints, parameters, and examples",
)

agent = FunctionAgent(
    name="APIAgent",
    system_prompt="Answer developer questions about the REST API using documentation.",
    tools=[rag_tool],
)

response = await agent.run(user_msg="How do I authenticate API requests?")
# Response includes: authentication methods, required headers, token expiry
```

### 6. Evaluate — Measure Quality

```python
from llama_index.core.evaluation import FaithfulnessEvaluator, RelevancyEvaluator

faith = FaithfulnessEvaluator()
rel = RelevancyEvaluator()

test_queries = [
    "What is the rate limiting policy?",
    "How do I paginate through results?",
    "What error codes does the API return?",
]

for q in test_queries:
    resp = query_engine.query(q)
    faith_result = faith.evaluate_response(response=resp)
    rel_result = rel.evaluate_response(response=resp, question=q)
    print(f"Q: {q}")
    print(f"  Faithfulness: {faith_result.passing}")
    print(f"  Relevancy: {rel_result.passing}")
    print(f"  Sources: {len(resp.source_nodes)} chunks")
```

### 7. Deploy — Production

```python
from llama_deploy import deploy_workflow, WorkflowServiceConfig, ControlPlaneConfig
from llama_index.core.workflow import Workflow, StartEvent, StopEvent, step

class RAGWorkflow(Workflow):
    @step
    async def answer(self, ev: StartEvent) -> StopEvent:
        result = query_engine.query(ev.query)
        return StopEvent(result=str(result))

await deploy_workflow(
    workflow=RAGWorkflow(timeout=60),
    workflow_config=WorkflowServiceConfig(service_name="api-rag"),
    control_plane_config=ControlPlaneConfig(),
)
```

## Expected Output Depth

- **Quick mode:** 2-3 source chunks, no reranker, single evaluator metric
- **Full mode (shown above):** 5 source chunks, hybrid retrieval + reranker, multi-metric evaluation, deploy-ready
- **Evaluate mode:** ParamTuner over chunk_size=[256,512,1024] with top_k=[2,5,10], reporting best configuration

## Common Pitfalls in This Pipeline

- Skipping the reranker produces answers that appear correct but miss nuance
- Using SimpleVectorStore instead of a persistent vector store loses all indexed data on restart
- Forgetting `await` on the agent call produces no error — just a silent coroutine object
- The hybrid retriever returns more candidates than the synthesizer needs without the reranker
