# Haystack File Converters and Multi-Format Indexing

Haystack provides type-specific converters for different file formats. Use `FileTypeRouter` to handle mixed-format directories.

```python
from haystack import Pipeline
from haystack.components.routers import FileTypeRouter
from haystack.components.converters import (
    TextFileToDocument,
    MarkdownToDocument,
    PyPDFToDocument,
)
from haystack.components.preprocessors import DocumentSplitter, DocumentCleaner
from haystack.components.joiners import DocumentJoiner
from haystack.components.writers import DocumentWriter
```

## Multi-Format Indexing Pipeline

```python
p = Pipeline()
p.add_component("router", FileTypeRouter(mime_types=["text/plain", "application/pdf", "text/markdown"]))
p.add_component("text_converter", TextFileToDocument())
p.add_component("pdf_converter", PyPDFToDocument())
p.add_component("markdown_converter", MarkdownToDocument())
p.add_component("joiner", DocumentJoiner())
p.add_component("cleaner", DocumentCleaner())
p.add_component("splitter", DocumentSplitter(split_by="word", split_length=500))
p.add_component("embedder", SentenceTransformersDocumentEmbedder())
p.add_component("writer", DocumentWriter(document_store=document_store))

# Route each file type to its converter
p.connect("router.text/plain", "text_converter.sources")
p.connect("router.application/pdf", "pdf_converter.sources")
p.connect("router.text/markdown", "markdown_converter.sources")
p.connect("text_converter.documents", "joiner.documents")
p.connect("pdf_converter.documents", "joiner.documents")
p.connect("markdown_converter.documents", "joiner.documents")
p.connect("joiner.documents", "cleaner.documents")
p.connect("cleaner.documents", "splitter.documents")
p.connect("splitter.documents", "embedder.documents")
p.connect("embedder.documents", "writer.documents")
```

## Available Converters

| Converter | Format | Dependency |
|-----------|--------|------------|
| `TextFileToDocument` | .txt | none |
| `PyPDFToDocument` | .pdf | pypdf |
| `MarkdownToDocument` | .md | markdown-it-py |
| `HTMLToDocument` | .html | trafilatura |
| `PPTXToDocument` | .pptx | python-pptx |
| `DocxToDocument` | .docx | python-docx |
| `CSVToDocument` | .csv | pandas |
| `JSONToDocument` | .json | none |
| `MultiFileConverter` | auto-detect | all above |

## Pipeline YAML Serialization

Haystack pipelines can be serialized to/from YAML — a key differentiator from other frameworks.

```python
# Export pipeline as YAML
yaml_str = pipeline.dumps()
with open("indexing_pipeline.yaml", "w") as f:
    f.write(yaml_str)

# Rebuild from YAML
from haystack import Pipeline
restored = Pipeline.loads(open("indexing_pipeline.yaml").read())

# Deploy with Hayhooks
# hayhooks deploy --file indexing_pipeline.yaml
```

## Component Type System

Each component declares typed input and output slots:

```python
from haystack import component

@component
class MyProcessor:
    @component.output_types(processed=str)
    def run(self, text: str) -> dict:
        return {"processed": text.upper()}

# Connections must match types
# text: str -> output must have 'processed: str'
pipeline.connect("processor.processed", "next_component.input_field")
```

Type mismatches are caught by pipeline validation at build time, not runtime.
