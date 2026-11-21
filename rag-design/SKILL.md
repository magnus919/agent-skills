---
name: rag-design
description: >-
  Design retrieval-augmented generation (RAG) for personal, enterprise, and
  multi-tenant systems. Choose lexical, vector, hybrid, graph, temporal, or
  multimodal retrieval and define evidence, ingestion, memory writes, citations,
  document and fragment authorization, and evaluation. Do not use for operating
  one framework or datastore, general SaaS architecture, or model training.
license: MIT
compatibility: No runtime dependencies. Validate implementation choices against the selected stack and workload.
---

# RAG Design

RAG selects evidence from external sources and gives it to a generator. Choose
the retrieval strategy, evidence representation, storage, orchestration, and
access policy independently. A graph can seed from vectors, image pages can
have text and visual indexes, and a temporal query can run over relational rows.

## Design workflow

1. **Write the workload.** Collect real questions and evidence locators. Label
   exact lookups, semantic matches, relationship paths, corpus-wide synthesis,
   historical queries, layout-dependent questions, and unanswerable requests.
   Name corpus owners, source types, freshness and revocation budgets, answer
   latency and cost, provider boundaries, and sensitive metadata.
2. **Choose the baseline and an upgrade hypothesis.** Start with exact,
   structured, lexical, or dense retrieval as the queries warrant. Compare
   candidate designs on the same authorized evidence. Add fusion, reranking,
   graph expansion, community reports, vision, or a bounded agent loop for a
   measured miss. Define what result would justify the additional cost.
3. **Specify the evidence contract.** Store stable source and fragment IDs,
   content versions, original locators, provenance, validity, and policy
   references. Track derivations through chunks, embeddings, graph attributes,
   summaries, caches, and media. Resolve citations to the original span, page,
   region, row, or time range and authorize each resolution.
4. **Design the write path.** Name who can propose, ingest, edit, publish, share,
   revoke, and delete. Version source events and make projection workers
   idempotent. Define authority and visibility during partial indexing,
   deletion, rollback, and restore. Treat retrieved instructions and extracted
   facts as untrusted input. Give agent memory proposals a destination, scope,
   provenance, validation rule, and review or promotion policy.
5. **Design the read path.** Bind principal and tenant on the server and plan
   each retrieval branch within authorized scope. Recheck authoritative access
   and current version before hydration or external processing. Enforce the
   same policy on all reachable paths and derived evidence. Bound query
   expansion, time, tokens, and fan-out. Answer with evidence, ask for
   clarification, or abstain.
6. **Validate by layer.** Measure retrieval against authorized gold evidence,
   then grade answer grounding and citations independently. Test denied
   disclosure and denied writes separately from relevance. Test stale grants,
   selective filters, permission changes, and restore. Record latency,
   ingestion cost, storage, and freshness alongside quality.

## When not to use

- Use [LlamaIndex](../llamaindex/SKILL.md), [Haystack](../haystack/SKILL.md),
  or [LangChain](../langchain/SKILL.md) for framework-specific implementation.
- Use [harness engineering](../harness-engineering/SKILL.md) for runtime controls
  and [LangGraph](../langgraph/SKILL.md) for stateful workflow implementation.
- Use [multi-tenant SaaS architecture](../multi-tenant-saas-architecture/SKILL.md)
  for tenant provisioning, migration, and commercial lifecycle.
- Use [secure software engineering](../secure-software-engineering/SKILL.md)
  for the application threat model and authorization implementation, and
  [agent evals and observability](../agent-evals-and-observability/SKILL.md) for
  general eval and trace design.

## References

| Design task | Read |
|---|---|
| Select retrieval, graph, temporal, multimodal, or agentic patterns | [Retrieval architectures](references/retrieval-architectures.md) |
| Combine time-series evidence, events, and forecasts | [Temporal RAG](references/temporal-rag.md) |
| Build a predictable input/output workflow with replay and acceptance | [RAG harness](references/rag-harness.md) |
| Design asynchronous enrichment and memory consolidation | [Memory workers](references/memory-workers.md) |
| Design read/write roles, fragments, derivations, or tenant isolation | [Authorization and tenancy](references/authorization-and-tenancy.md) |
| Build a personal or enterprise design and acceptance plan | [Implementation and evaluation](references/implementation-and-evaluation.md) |
| Review the comparative findings and evidence limits | [Research brief](references/research-brief.md) |
| Inspect primary sources and implementation caveats | [Research log](references/research-log.md) |
| Record the proposed system and rollout criteria | [Design record](templates/rag-design-record.md) |

## Completion

Deliver a design record with query examples, baseline and upgrade criteria,
read/write flows, authorization decisions by evidence type, lifecycle failure
handling, and acceptance cases with accountable owners. Mark unverified
capabilities and unresolved authority decisions. Stop when these can be
reviewed or when a named policy or evidence gap blocks a material decision.
