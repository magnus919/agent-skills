# Research log and source ledger

Accessed 2026-11-21. The question and synthesis are in the
[research brief](research-brief.md). Evidence here records what the source
can support, applicable limitations, and where the finding was preserved.
Design recommendations are in the linked guides.

## Searches and decisions

| Pass | Discovery | Selection decision |
|---|---|---|
| Design orientation | Identify recurring design questions about memory substrates, retrieval, time, background enrichment, and governance. | Investigate shared entity IDs, multiple time axes, rebuildable projections, background workers, and permissions through public primary sources. |
| Retrieval | Search by foundational RAG, rank fusion, named graph techniques, native page retrieval, and adaptive retrieval. Follow original papers to official project docs. | Include different mechanisms and evaluation settings. Exclude secondary comparisons and universal performance rankings. |
| Tenancy | Search per-document ACLs, source sync, PostgreSQL row policy, pgvector filtering, graph namespace isolation, tenant sharding, and relationship authorization consistency. | Include first-party project docs with operational limits. Exclude unmatched forum claims and the historical RAGFlow issue as evidence of current capabilities. |
| Temporal | Follow temporal graph and narrative papers from notes. Check metrics query APIs, time buckets, probabilistic time-series models, and rolling-origin validation. | Distinguish temporal retrieval from observed analysis and forecasting. Retain original work and implementation references. |
| Workers and harness | Search reflection, tiered memory, sleep-time compute, asynchronous writes, managed extraction, and workflow checkpointing. Follow Letta to its paper and AWS to strategy docs. | Keep research benchmarks separate from product contracts and preview status. The historical Letta architecture link redirected to a generic landing page, so current availability of the 2025 interface is unverified. |

## Retrieval and representation

| Primary source | Retained claim and limits | Preserved in |
|---|---|---|
| [Lewis et al., RAG v4](https://arxiv.org/abs/2005.11401v4) | Combines dense passage retrieval and generation with sequence- and token-level formulations. The trained architecture is historical grounding for dense RAG. | [Architectures](retrieval-architectures.md) |
| [Cormack et al., reciprocal rank fusion](https://cormack.uwaterloo.ca/cormacksigir09-rrf.pdf) | Combines rank positions across lists without comparing raw scores. Reported IR benchmarks cannot select branches or tune fusion for a new corpus. | [Architectures](retrieval-architectures.md) |
| [Edge et al., GraphRAG v2](https://arxiv.org/abs/2404.16130v2) and [Microsoft query modes](https://microsoft.github.io/graphrag/query/overview/) | Entity extraction plus community reports supports global sensemaking. Local combines graph and chunks, DRIFT uses community context to expand local search, and global map/reduce over reports is resource intensive. Gains were reported for evaluated global questions. Require independent tests for freshness, ACLs and other workloads. | [Architectures](retrieval-architectures.md) |
| [Guo et al., LightRAG v3](https://arxiv.org/abs/2410.05779v3) and [project README](https://github.com/HKUDS/LightRAG) | Dual-level graph and vector retrieval with incremental updates. The project documents query keyword extraction as a provider-dependent stage and handling of JSON-mode rejection. Test real provider and storage adapters and access across modes. The presence of a query-only UI establishes a UI surface. | [Architectures](retrieval-architectures.md) |
| [Faysse et al., ColPali v6](https://arxiv.org/abs/2407.01449v6) | Retrieves visually rich pages using page image multi-vectors and late interaction. ViDoRe evaluates retrieval. Page retrieval results leave answer accuracy and deployment cost open. | [Architectures](retrieval-architectures.md) |
| [Chen et al., MuRAG v2](https://arxiv.org/abs/2210.02928v2) | Joint multimodal retrieval and generation for image-text QA. Task results cover the paper's datasets. | [Architectures](retrieval-architectures.md) |
| [Asai et al., Self-RAG](https://arxiv.org/abs/2310.11511) | Trained retrieval-on-demand and self-critique demonstrate adaptive retrieval. Learned decisions differ from a server-enforced policy or runtime cap. | [Architectures](retrieval-architectures.md) |

## Tenancy and authorization

| Primary source | Retained claim and limits | Preserved in |
|---|---|---|
| [pgvector filtering and multitenancy](https://github.com/pgvector/pgvector#filtering) | ANN index scanning can precede filtering and yield fewer authorized neighbors. Iterative scans have limits. Shared indexes can affect speed and recall across tenants. Exact search and partitioning are useful comparisons. | [Architectures](retrieval-architectures.md) |
| [PostgreSQL 19 row security](https://www.postgresql.org/docs/19/ddl-rowsecurity.html) | Policies can constrain read and write. Table owners normally bypass RLS and superusers and BYPASSRLS roles do. Verify policy combinations and actual runtime role. | [Authorization](authorization-and-tenancy.md) |
| [Qdrant multitenancy](https://qdrant.tech/documentation/manage-data/multitenancy/) | Payload filtering, custom sharding, and tiered tenancy have different isolation and resource tradeoffs. Shard routing and scoring statistics have their own scope. Bind identity and require filtering in the service. | [Authorization](authorization-and-tenancy.md) |
| [Graphiti reference servers](https://github.com/getzep/graphiti#reference-mcp-and-rest-servers) and [namespaces](https://help.getzep.com/graphiti/core-concepts/graph-namespacing) | Project expressly leaves authentication and authorization out of reference servers. Application must authorize group IDs. Reusing a namespace as the policy is unsafe. | [Authorization](authorization-and-tenancy.md) |
| [Onyx access controls](https://github.com/onyx-dot-app/documentation/blob/main/security/architecture/access_controls.mdx) | Applies indexed ACL filters and documents scheduled or manual connector-driven sync. Scope depends on connector, configuration, and edition. Evaluate stale permissions after changes. | [Authorization](authorization-and-tenancy.md) |
| [Azure AI Search document access](https://learn.microsoft.com/azure/search/search-document-level-access-overview) and [ADLS sync](https://learn.microsoft.com/en-us/azure/search/search-indexer-access-control-lists-and-role-based-access) | Application security filters and identity-based enforcement have different contracts. Documented preview paths depend on connector and synchronized permissions. ACL refresh differs from deletion, chunk remapping, and role propagation. | [Authorization](authorization-and-tenancy.md) |
| [Pang et al., Zanzibar](https://research.google/pubs/zanzibar-googles-consistent-global-authorization-system/) and [OpenFGA consistency](https://openfga.dev/docs/interacting/consistency) | Relationship authorization and ordering changes relative to content have an operational precedent. OpenFGA documents a cache-vs-database choice. A fresh check cannot repair an unsynchronized source or index on its own. | [Authorization](authorization-and-tenancy.md) |

## Time and forecasts

| Primary or author-maintained source | Retained claim and limits | Preserved in |
|---|---|---|
| [Rasmussen et al., Zep](https://arxiv.org/abs/2501.13956v1) | Graphiti tracks evolving assertions and invalidates superseded edges. Reported retrieval experiments are limited to their setups. | [Architectures](retrieval-architectures.md) |
| [Han et al., TG-RAG](https://arxiv.org/abs/2510.13590v1) | Dated relationship edges plus a hierarchical time graph and temporal summaries support evolving corpus queries and incremental updates. The reported method addresses temporal knowledge, not measured-series forecasts. | [Temporal RAG](temporal-rag.md) |
| [Kim et al., ChronoRAG](https://arxiv.org/abs/2508.18748v2) | Chronological passage assembly addresses ordering in narrative QA. Validity reconstruction and measurement alignment require additional contracts. | [Temporal RAG](temporal-rag.md) |
| [Prometheus HTTP API](https://prometheus.io/docs/prometheus/latest/querying/api/) and [Tiger Data time buckets](https://www.tigerdata.com/docs/learn/data-lifecycle/time-buckets/about-time-buckets) | Range evaluation and time bucketing illustrate typed numeric evidence operations. Choose and document grain, window, origin and authorization at the service boundary. | [Temporal RAG](temporal-rag.md) |
| [Ansari et al., Chronos v3](https://arxiv.org/abs/2403.07815v3) and [Hyndman and Athanasopoulos, forecasting toolbox](https://otexts.com/fpp3/toolbox.html) | Probabilistic forecasting is a distinct model task. Compare distribution and point forecasts to simple benchmarks on rolling historical origins. Chronos reported different performance on seen and unseen data. Require horizon-appropriate local evaluation. | [Temporal RAG](temporal-rag.md) |

## Agent memory and harnesses

| Primary source | Retained claim and limits | Preserved in |
|---|---|---|
| [Park et al., Generative Agents v2](https://arxiv.org/abs/2304.03442v2) | Memory stream, reflection, and retrieval support planning in a simulated town. The ablation concerns believable interaction in that simulation. | [Memory workers](memory-workers.md) |
| [Packer et al., MemGPT v2](https://arxiv.org/abs/2310.08560v2) | Tiered virtual context and controlled movement across memory tiers. Distinct from offline consolidation or a commercial access model. | [Memory workers](memory-workers.md) |
| [Lin et al., Sleep-time Compute](https://arxiv.org/abs/2504.13171v1) and [Letta example](https://www.letta.com/blog/sleep-time-compute/) | Precomputation moves certain work off the request path. Letta documented a secondary memory-editing agent. Paper results on modified reasoning tasks leave whole-system amortization and downstream data quality open. | [Memory workers](memory-workers.md) |
| [AWS AgentCore strategies](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/memory-strategies.html) and [memory types](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/memory-types.html) | Configured strategies produce long-term memory from raw events, with built-in, override, and self-managed choices. Validate readiness, tenant policy and deletion independently. | [Memory workers](memory-workers.md) |
| [Claude Managed Agents Dreams](https://platform.claude.com/docs/en/managed-agents/dreams) | Documented research preview reads earlier sessions and an input store, produces a separate output store, and leaves the source available for review and rollback. Archiving the job and handling the output store differ. No inference of general availability. | [Memory workers](memory-workers.md) |
| [LangChain memory](https://docs.langchain.com/oss/python/concepts/memory), [retrieval](https://docs.langchain.com/oss/python/deepagents/retrieval), and [LangGraph persistence](https://docs.langchain.com/oss/python/langgraph/persistence) | Documents hot-path vs background writes, retrieval patterns and connectors, and the distinction between thread checkpoints and cross-thread stores. Application code must enforce evidence and access contracts around replay. | [Harness](rag-harness.md) |

The retained sources above are preserved at the claim level. Paper findings are
author-reported within their study setting, and project docs describe
capabilities and limitations as accessed. Illustrative workflows and controls
in the skill are design proposals. No comparative deployment or behavioral
performance measurements were made.
