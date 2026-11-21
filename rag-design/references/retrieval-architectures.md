# Retrieval architectures

Choose by observable information need. [Research log](research-log.md) gives
the source boundaries for the named methods and projects.

| Workload | Representation and retrieval | Failure to test |
|---|---|---|
| Error code, clause number, name, or literal quote | Exact lookup, normalized aliases, or a lexical index such as BM25 | Tokenization of identifiers and language-specific stemming |
| Paraphrase or conceptual match | Embed passages and queries, retrieve nearest neighbors, hydrate source spans | Weak handling of identifiers, fine distinctions, and missing relevant chunks |
| Mixed lookup and paraphrase | Run lexical and dense branches in the same authorized scope, fuse by rank or calibrated scores | One branch floods the pool or fusion buries unique evidence |
| Relationship or multi-hop question | Resolve a seed entity, traverse typed and scoped edges, recover supporting spans | Entity collisions, missing or spurious edges, and paths that cross permissions |
| Corpus-wide themes | Produce evidence-linked summaries by authorized collection or community, aggregate with coverage checks | Old reports, hidden source contributions, uneven coverage and high query cost |
| State at a historical date | Query fact validity and, if relevant, when it was recorded | Superseded facts treated as current, or current ACLs confused with historical state |
| Chart, drawing, scanned page, or demonstration | Retrieve relevant pages, regions, or time slices with text and/or visual representations | Correct document with wrong figure, axis, unit, region, or timestamp |

## Vector and hybrid

Preserve headings and source offsets during chunking. Split at semantic or
document structure boundaries where practical. Compare passage sizes and
overlap on real evidence locators. Retrieve small fragments and expand
to authorized parent context only when needed. Deduplicate adjacent chunks
and repeated versions before spending the context budget.

Run an exact similarity baseline on an authorized sample to measure loss
from approximate nearest-neighbor search (ANN). Report candidate recall
before reranking and after context packing. Selective ACLs can reduce ANN
candidate yield even when all returned results are correctly authorized.
Compare iterative scans, scoped indexes, partitions, and exact search on
selective subsets. Fuse rank lists with reciprocal rank fusion when branch
scores are incomparable, or learn and verify a score calibration. A
cross-encoder can improve ordering of candidates it receives. It cannot
recover evidence absent from the pool and adds cost and data exposure.

## Graph and temporal

A graph can be curated, imported from authoritative systems, or extracted
from documents. Prefer typed edges, canonical entity IDs, a resolution
strategy, and source-backed claims. Graph retrieval includes distinct paths:

- **Local traversal** seeds from entity lookup, text, or vectors, then expands
  bounded typed edges. Track each hop and hydrate supporting spans.
- **Global synthesis** can use Microsoft GraphRAG-style community reports with
  aggregation. Compare to collection-wide lexical or hierarchical summaries
  before paying for entity extraction and community rebuilding.
- **Hybrid graph retrieval** can combine local entity evidence, broader
  relationship evidence and ordinary passage retrieval, as in LightRAG.
  Evaluate scopes, update behavior, and deletion for the actual build.
- **Temporal state** associates assertions with a valid interval and a
  recorded interval when historical reconstruction matters. Graphiti
  illustrates temporal edge invalidation. A relational event or fact table
  may suffice for the same query contract. Distinguish current best knowledge,
  historical state, and the state known at a past decision time.

Cap path depth, branching, and subgraph size. Entity summaries, property
values, node existence, edge existence, and counts can each disclose data.
An extracted edge is a candidate assertion with provenance and possible
contradictions. If graph enrichment fails, keep authorized source retrieval
available and represent the lost capability in the response.

For measurement streams, date-aligned evidence, and forecasting, see
[Temporal RAG](temporal-rag.md).

## Multimodal

Model the query, index, evidence, and generator modalities separately. OCR,
layout parsing, captions, and transcripts supply searchable text. Preserve
reading order, cells, page coordinates, original assets, and timecodes.
For layout-dependent inputs compare that baseline with native page or image
retrieval. ColPali encodes page images into multiple vectors and scores
matches through late interaction. This is a page retrieval pattern.
MuRAG is an example of retrieval plus generation over image and text.

Use native evidence where the answer depends on a figure or scene. Send a
vision-capable model the narrowly authorized crop or page and relevant text.
For audio/video, time-align transcripts and sampled frames, then verify the
answer against the original segment. Avoid citing a caption as proof of a
number or spatial relationship it never contained. Track rendition,
resolution, region, time range, and provenance, and measure storage and
inference cost independently. Route tabular computations to an authorized,
typed query when exact aggregation is required.

## Orchestration

A fixed pipeline is a useful control for most comparisons. Route by workload
when queries actually require different evidence. Agent-directed retrieval can
decompose a multi-hop question or refine a weak evidence set. Give every
subquery the same authenticated scope, maximum hop/call and spend budgets, and
an evidence sufficiency or abstention rule. The model may propose retrieval
but policy controls the eligible data and all write actions. Record which
branch contributed each citation and compare to the fixed baseline by category.
