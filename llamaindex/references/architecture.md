# LlamaIndex Core Architecture

## Seven Core Primitives

LlamaIndex organizes functionality around seven primitives that map to RAG pipeline stages:

| Primitive | Purpose | Example |
|-----------|---------|---------|
| Reader | Pull data from sources | `SimpleDirectoryReader("./data")` |
| Document | Source content with metadata | Returned by Reader |
| Node | Chunk of a Document | Created by Node Parsers |
| Index | Data structure over Nodes | `VectorStoreIndex`, `PropertyGraphIndex` |
| Retriever | Return relevant Nodes | `index.as_retriever(similarity_top_k=5)` |
| Query Engine | Retriever + response synthesis | `index.as_query_engine()` |
| Agent | LLM with tools | `FunctionAgent(tools=[...])` |
| Workflow | Event-driven orchestration | `class MyFlow(Workflow)` |

## Configuration

The `Settings` object provides global configuration, replacing the deprecated `ServiceContext`:

```python
from llama_index.core import Settings
from llama_index.llms.openai import OpenAI

Settings.llm = OpenAI(model="gpt-4o")
Settings.embed_model = "local:BAAI/bge-small-en-v1.5"
Settings.text_splitter = SentenceSplitter(chunk_size=1024, chunk_overlap=20)
```

## Data Flow

```
Source -> Reader -> Document -> Node Parser -> Nodes -> Index
                                                            |
                                           Retriever <- Query Engine <- Agent
                                                               |
                                                          Response
```

## Workflow Event Model

Workflows replace DAG-based composition with typed event passing:

```python
from llama_index.core.workflow import Workflow, StartEvent, StopEvent, Event, step

class RetrievedEvent(Event):
    query: str
    nodes: list

class SimpleRAG(Workflow):
    @step
    async def retrieve(self, ev: StartEvent) -> RetrievedEvent:
        # ... retrieval logic
        return RetrievedEvent(query=ev.query, nodes=nodes)

    @step
    async def generate(self, ev: RetrievedEvent) -> StopEvent:
        # ... generation logic
        return StopEvent(result=str(resp))
```

Steps infer input/output types from annotations. The framework validates the event graph before execution.
