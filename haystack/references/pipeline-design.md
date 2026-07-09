# Haystack Pipeline Design

Haystack uses a **Pipeline** abstraction — a validated directed acyclic graph (DAG) of typed components.

## Basic Structure

```python
from haystack import Pipeline

pipeline = Pipeline()
pipeline.add_component("name", SomeComponent())
pipeline.connect("source_component.output_slot", "target_component.input_slot")
result = pipeline.run({"source_component": {"input_param": value}})
```

## Indexing Pipeline

```python
from haystack import Pipeline
from haystack.components.converters import TextFileToDocument
from haystack.components.preprocessors import DocumentSplitter
from haystack.components.embedders import SentenceTransformersDocumentEmbedder
from haystack.components.writers import DocumentWriter
from haystack.document_stores.in_memory import InMemoryDocumentStore

document_store = InMemoryDocumentStore()
indexing = Pipeline()
indexing.add_component("converter", TextFileToDocument())
indexing.add_component("splitter", DocumentSplitter(split_by="word", split_length=500))
indexing.add_component("embedder", SentenceTransformersDocumentEmbedder())
indexing.add_component("writer", DocumentWriter(document_store=document_store))

indexing.connect("converter.documents", "splitter.documents")
indexing.connect("splitter.documents", "embedder.documents")
indexing.connect("embedder.documents", "writer.documents")

indexing.run({"converter": {"sources": ["docs.txt"]}})
```

## Query Pipeline

```python
query = Pipeline()
query.add_component("text_embedder", SentenceTransformersTextEmbedder())
query.add_component("retriever", InMemoryEmbeddingRetriever(document_store=document_store))
query.add_component("prompt_builder", PromptBuilder(template="Context: {{documents}}\nQ: {{question}}\nA:"))
query.add_component("generator", OpenAIGenerator())

query.connect("text_embedder.embedding", "retriever.query_embedding")
query.connect("retriever.documents", "prompt_builder.documents")
query.connect("prompt_builder", "generator")

result = query.run({
    "text_embedder": {"text": "What is Haystack?"},
    "prompt_builder": {"question": "What is Haystack?"}
})
```

## Pipeline Validation

Haystack validates the pipeline at build time:

```python
pipeline.warm_up()  # Load models, validate connections
pipeline.run(...)   # Execute
```

Validation catches: missing connections, type mismatches, required inputs not provided.

## Custom Components

```python
from haystack import component

@component
class MyProcessor:
    @component.output_types(processed=str)
    def run(self, text: str):
        return {"processed": text.upper()}
```

## Pipeline YAML Serialization

Pipelines can be serialized to/from YAML:

```python
pipeline.dumps()  # to YAML string
Pipeline.loads(yaml_string)  # from YAML string
```
