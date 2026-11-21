# Research brief

Investigation date 2026-11-21. Question: which representation, retrieval,
and policy choices fit personal and shared RAG, and which documented
limitations affect adoption? The bounded technical investigation covers
primary papers and first-party descriptions of real implementations.
See the [search and extraction ledger](research-log.md) for source notes,
access dates, and exclusions.

| Finding | Confidence and evidence boundary |
|---|---|
| RAG spans independent choices about search, data representation, and generation. Dense, lexical, local graph, and global synthesis target different question types. | High for mechanism. Lewis, RRF, Microsoft GraphRAG, and LightRAG cover distinct mechanisms and workloads. Choosing a winner requires workload-level comparison. |
| Visual retrieval preserves evidence that text extraction may omit. Native page retrieval and multimodal generation solve different stages. | High for design distinction. ColPali studies page retrieval and MuRAG studies image-text QA. Neither establishes performance across operational media. |
| Time needs its own evidence contract. Narrative order, evolving facts, observed trends, and forecasts require different inputs. A metrics or time-series tool can supply measurements missing from documents and graph edges. | High for the interface distinction. TG-RAG, ChronoRAG, Graphiti, Prometheus, and Timescale supply parts of the design. The proposed cross-store composition and user benefit require validation. |
| Enterprise deployment must coordinate source and retrieval authority even if storage is siloed. More granular retrieval demands policy for derived evidence and lifecycle transitions. | High for design need. Azure and Onyx establish synchronization dependencies. PostgreSQL and Qdrant establish local enforcement or scoping primitives. Zanzibar offers a production authorization precedent. The full composed system needs tests. |
| Agent memory can benefit from scoped processing outside the request path. Reflection, tiered memory, precomputation, and consolidation occupy distinct roles. | High for existence, scoped to implementation. Research includes simulated agents and synthetic reasoning tasks. AWS documents a managed asynchronous extraction service. Claude Dreams is a research preview with separate output stores. Long-run quality gains and autonomous maintenance remain workload questions. |
| Typed orchestration can make a multimodal evidence path predictable at its interfaces and replay points. | High for the primitives. LangGraph documents state checkpoints and external stores. Correct evidence admission, replay authorization, and acceptance must be implemented and tested in the application. |

## Open questions for an implementation

- Which authorized query classes still fail after a basic retrieval baseline?
- How quickly can each source's deletion and policy changes take effect?
- What evidence may derived summaries, graph metadata, rollups, and models expose?
- Can a forecast beat the seasonal baseline and calibrate threshold-event
  probabilities for the requested horizon and traffic regime?
- What publication review and recovery cost is acceptable for agent-generated
  memory? Which useful enrichment can be deterministic?

## Durable inventory

The [research log](research-log.md) retains source-level claims and evidence
limits. The skill routes to [retrieval architectures](retrieval-architectures.md),
[temporal RAG](temporal-rag.md), [memory workers](memory-workers.md), [RAG harness](rag-harness.md),
[authorization and tenancy](authorization-and-tenancy.md), and
[implementation and evaluation](implementation-and-evaluation.md). The
[design record](../templates/rag-design-record.md) carries the findings into
new designs. Private research orientation informed the questions. Public
claims are mapped to public evidence in the ledger. No vendor service,
published benchmark, forecast, or tenant deployment was independently run.
