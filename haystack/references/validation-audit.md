# Haystack Skill — Research Validation Audit

**Date:** 2026-07-09
**Sources:** docs.haystack.deepset.ai, docs.haystack.deepset.ai/reference

## Claims Verified Correct

| Claim | Source | Status |
|-------|--------|--------|
| Pipeline DAG via add_component() + connect() | haystack docs | ✓ |
| InMemory, Elasticsearch, Pinecone, Weaviate stores | haystack docs | ✓ |
| PromptBuilder uses Jinja2 templates | haystack docs | ✓ |
| DeepEvalEvaluator for LLM-based metrics | haystack docs | ✓ |
| SASEvaluator for semantic similarity | haystack docs | ✓ |
| Hayhooks for REST API deployment | haystack blog | ✓ |
| Evaluation as its own pipeline | haystack evaluation guide | ✓ |

## Missing from Skill (Addressed in This Enrichment)

- File converter components (TextFileToDocument, PyPDFToDocument, MarkdownToDocument, etc.)
- FileTypeRouter for multi-format indexing pipelines
- MultiFileConverter for automatic format detection
- Pipeline YAML serialization (dumps/loads)
- Component type system (input/output slot typing)
- Pipeline warm_up() for model loading
