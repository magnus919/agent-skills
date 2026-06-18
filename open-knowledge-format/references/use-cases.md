# OKF — Real-World Use Cases and Adoption

## The Problem OKF Solves

Internal organizational knowledge is scattered across heterogeneous surfaces:

- Metadata catalogs with proprietary APIs
- Wikis, third-party systems, shared drives
- Code comments, docstrings, notebook cells
- The heads of a few senior engineers

When an AI agent needs to answer "How do I compute weekly active users from our event stream?" it has to assemble the answer from incompatible sources. Every agent builder reinvents context assembly; every catalog vendor reinvents data models.

OKF provides a **format-level** solution — not another service, not another SDK. Anyone can produce OKF, anyone can consume it, and it survives moving between systems.

## Google's Reference Implementation

Google published a proof-of-concept in the same repository as the spec:

- **Enrichment agent** — Built on the Google Agent Development Kit (ADK) with Gemini. Ingests BigQuery metadata and emits OKF bundles in two passes: a BQ pass (metadata extraction) and a web pass (LLM-driven crawling of documentation URLs for enrichment).
- **Interactive visualizer** — `viz.html`, a self-contained HTML file using Cytoscape.js that renders any OKF bundle as a force-directed graph with search, type filtering, and backlinks.

Three sample bundles are checked into the repo:

| Bundle | Source | Concepts |
|--------|--------|----------|
| `bundles/ga4/` | GA4 e-commerce dataset | BigQuery tables, metrics, dimensions |
| `bundles/stackoverflow/` | Stack Overflow public dataset | Schema references, cross-table joins |
| `bundles/crypto_bitcoin/` | Bitcoin blocks/transactions | Tables, foreign-key relationships |

## Third-Party Adoption

### Rust implementation (W4G1/okf)

A pure-Rust, zero-dependency implementation of OKF v0.1 — demonstrates the spec is implementable without any Google-specific tooling.

### Suganthan Mohanadasan

Published his entire blog as an OKF bundle at `suganthan.com/okf/`. Uses it to make his writing directly consumable by AI agents. Agents start at `suganthan.com/okf/index.md` and navigate through linked concept files.

### Marie Haynes

Created an OKF bundle from her traffic-drop assessment methodology using Antigravity. Produced a graph visualization showing how extracted concepts relate. Tested querying it with Gemini 3 Flash as the consumption agent.

## Predicted Use Cases

### Internal knowledge management

Organizations maintain OKF bundles alongside code repositories. Agents read the bundle to understand table schemas, metric definitions, and operational runbooks before performing tasks. Updates go through normal git workflows — PRs, reviews, merges.

### Agent-to-agent knowledge exchange

An agent working on a data pipeline produces an OKF bundle documenting the tables it creates and their semantics. A downstream agent consumes that bundle to understand how to query those tables. No API integration needed — just files in a shared repo.

### Selling expert knowledge as bundles

Professionals (lawyers, accountants, SEOs, consultants) package their proprietary processes as OKF bundles. Customers purchase and integrate them into their own agent systems. The format creates a marketplace for structured expert knowledge.

### Cross-organizational data sharing

Companies share OKF bundles with partners to document shared data schemas, business rules, and metrics. The format survives movement between organizations because it's just files.

## Related Patterns

OKF formalizes patterns already emerging in the ecosystem:

- **Obsidian vaults** wired to coding agents
- **AGENTS.md / CLAUDE.md** convention files in repositories
- **LLM wiki repos** (Karpathy's pattern) — directories of `index.md` and `log.md` artifacts
- **Metadata-as-code** within data platform teams

Each pattern independently solved the same problem; OKF standardizes the interoperability surface.

## When Not to Use OKF

- **Real-time query serving** — OKF is designed for curated knowledge, not sub-millisecond lookups. Use a vector DB or cache for serving.
- **High-volume transactional metadata** — OKF bundles are human-readable and git-friendly, but not designed for 100K+ concept updates per minute.
- **Replacing domain schemas** — Don't put Protobuf/ Avro/OpenAPI definitions in OKF. OKF *references* those schemas — it describes what they mean, not their binary wire format.
