---
name: data-architect
description: >-
  Use this skill to assess, design, and evolve data architectures, including
  data platforms, data products, data mesh adoption, event-driven data flows,
  governance, modeling, and migration decisions. Load it when teams need
  workload-grounded tradeoffs, ownership and quality agreements, or a
  current-to-target data architecture. Do not use it for pipeline or platform
  operations, implementation details, interface contract semantics, SQL tuning,
  or statistical modeling; route those to data-engineering,
  platform-engineering, api-design-and-evolution, postgres, or data-scientist.
compatibility: >-
  Designed for agentic AI assistants (Hermes Agent, Claude Code, similar
  coding agents). No special system requirements.
metadata:
  author: data-architect contributors
  version: "1.1.0"
  topics: data-architecture, data-modeling, data-warehouse, data-governance, data-platform, data-products, data-mesh, event-driven-data, etl, streaming, cloud-data
---

# Data Architect

## Start with the Decision

1. Identify the decision and use the supplied context and repository artifacts first. For a bounded store choice or review, do not begin with a persona introduction, organization-wide inventory, or maturity questionnaire. Ask only for missing constraints that could change the recommendation; label other assumptions and proceed.
2. Classify the workload: transactional system of record, analytical serving, event exchange, or a combination. Establish the consumers, correctness requirements, data size and growth, concurrency, latency, retention/deletion needs, and recovery objectives that matter to this decision.
3. Compare the current approach with the smallest viable alternative. Include ownership, on-call burden, maintainability, migration and exit cost, and the team's ability to operate it. State which requirement would justify a more complex platform.
4. Deliver a recommendation with reasons, accepted costs, uncertainties, and the evidence that would change it. When evidence is insufficient, propose a bounded trial with success criteria rather than presenting the platform choice as settled.

## Practical Decision Rules

- **Transactional store:** Start with transaction boundaries, consistency, constraints, access patterns, and concurrent updates. Do not prescribe a warehouse, mesh, lakehouse, or analytical modeling exercise unless an actual consumer requires it. Route database implementation and recovery operations to `postgres`, and service implementation to `backend-engineering`.
- **Operational complexity:** Every additional datastore, replication path, or streaming service needs an accountable owner and a concrete workload benefit. Retaining the current platform is a valid recommendation when it meets the requirements.
- **Recovery and deletion:** A backup or configured policy is not recovery evidence. Require a representative restore rehearsal and checks of required invariants. Where deletions must survive recovery, specify how deletion records outlive the restored snapshot, how they are reapplied before access resumes, and how absence is verified. Keep commands and runbooks in the owning tool skill.
- **Evidence:** Separate observed behavior, assumptions, and planned validation. A successful prototype supports only its tested conditions. Experiment approval does not imply production adoption; route durable decision records to `adr-authoring` and follow repository conventions before using `templates/adr-template.md` as a fallback.
- **Platform selection:** Evaluate workload fit and total operating cost before vendor features. If one missing fact changes the winner, name it and the smallest check that resolves it.

## Task-Specific Workflow

### Architecture Review

Trace the relevant data flow and failure modes using available evidence. Rank findings by impact, distinguish verified defects from hypotheses, retain working components, and give a concrete next action for each material finding. Do not infer missing retries, incremental processing, or observability solely from symptoms.

### Decision Comparison

Use a compact comparison of viable options against the constraints, then state the recommended option, accepted tradeoffs, owner, validation needed, and reconsideration trigger. Avoid generic platform surveys when the workload is already clear.

### Strategy and Roadmap

For multi-quarter evolution, assess current bottlenecks, sequence incremental investments, name organizational dependencies, and define an observable success criterion for each phase. Load broader discovery or governance material only when the scope warrants it.

### Data Mesh or Event-Driven Data Product Design

**Applicability:** Use when the request involves domain-owned data products, mesh adoption, event-sourced inputs, or operational and analytical consumers sharing data.

1. Establish the business domains, producers, consumers, decision rights, and current failure costs before naming a target pattern.
2. Test whether domain teams can own products end to end, whether a platform team can provide self-service capabilities, and whether shared governance can be automated or made enforceable.
3. Define each product's semantics, owner, intended consumers, access modes, quality and freshness objectives, discoverability, compatibility policy, retention, and deprecation path.
4. Separate operational exchange from analytical serving. Decide whether a product is an event stream, a queryable snapshot, a historical table, or more than one compatible view.
5. Design replay, ordering, late-arriving data, duplicate delivery, backfill, consumer recovery, and access failure before recommending a streaming or mesh pattern.
6. Sequence a bounded pilot with explicit exit criteria. A centralized or hybrid design is a valid result when ownership, platform, or governance prerequisites are missing.

Load `references/data-mesh-readiness-and-operating-model.md` for adoption assessment, `references/event-driven-data-products.md` for product and recovery decisions, and `templates/architecture-design-session.md` for a facilitated workshop artifact.

## Discovery When the Problem Is Unclear

Use `references/discovery-framework.md` when the user asks for discovery or the decision cannot yet be bounded. Start with the most costly symptom and its affected consumer. For a requested quick scan, cover reliability, cost, shared definitions, ownership, and traceability; mark unknowns and prioritize the first concrete investigation. Treat symptoms as hypotheses, not proof that a catalog, schema registry, or new platform is required. Do not score organizational maturity from a count of yes/no answers.

## Core Expertise Areas

Load only the references needed for the current decision:

- **Data modeling** — Kimball, Inmon, Data Vault, lakehouse, star vs snowflake. → `references/architecture-patterns.md`
- **Data warehousing & lakehouse** — Medallion architecture, cloud warehouse design, cost optimization. → `references/architecture-patterns.md`
- **Cloud data platforms** — Snowflake, BigQuery, Redshift, Databricks. → `references/cloud-platform-comparison.md`
- **Data governance** — Frameworks, maturity model, quality dimensions, metadata management. → `references/governance-maturity.md`
- **Compliance & regulated environments** — GDPR, HIPAA, CCPA, SOX, PCI DSS, BCBS 239. → `references/compliance-by-framework.md`
- **Vendor evaluation** — Data catalogs, ETL/ELT tools, orchestration platforms. → `references/vendor-evaluation.md`
- **Data integration & ETL/ELT** — Batch vs streaming, CDC, dbt patterns, data contracts
- **Streaming & real-time** — Kafka architecture, Kappa vs Lambda, when streaming is worth it
- **AI/ML data infrastructure** — Feature stores, RAG architecture, training data pipelines
- **Tools ecosystem** — Modeling, warehouse, integration, governance, storage, observability tools
- **Real-world case studies** — Lakehouse migrations, Data Vault implementations, hybrid architectures. → `references/case-studies.md`
- **Data mesh adoption** — Readiness, domain ownership, platform boundary, federated governance, and transition choices. → `references/data-mesh-readiness-and-operating-model.md`
- **Event-driven data products** — Product contracts, access modes, replay, compatibility, and consumer recovery. → `references/event-driven-data-products.md`

## Reference Files

Load these on demand when the topic comes up:

- `references/architecture-patterns.md` — Decision framework for Kimball, Inmon, Data Vault, lakehouse, data fabric capabilities, data mesh, and hybrid shapes. Also covers streaming vs batch, star vs snowflake, and Medallion architecture.
- `references/anti-patterns.md` — 13 named anti-patterns with symptoms, root causes, and remediations. Load when doing design review or incident post-mortem.
- `references/discovery-framework.md` — Structured discovery questions and consulting session flow. Load when discovery is requested or the decision cannot yet be bounded.
- `references/cloud-platform-comparison.md` — Snowflake vs BigQuery vs Redshift vs Databricks: architecture, pricing, scaling, lock-in vectors, and decision framework. Load when doing platform selection or migration planning.
- `references/governance-maturity.md` — Staged data governance maturity model (Level 0-5) with DAMA-DMBOK framework, what each stage looks like in practice, and progression paths. Load when designing or assessing a governance program.
- `references/vendor-evaluation.md` — Structured evaluation criteria for data catalogs (Atlan, Alation, Collibra, DataHub, etc.), ETL/ELT tools (Fivetran, Airbyte, dbt), and orchestration (Airflow, Dagster, Prefect). Load during vendor selection.
- `references/compliance-by-framework.md` — What GDPR, HIPAA, CCPA, SOX, PCI DSS, and BCBS 239 require from a data architecture perspective. Design patterns for each. Load when designing for regulated environments.
- `references/case-studies.md` — Real-world architecture transformations: Data Vault at a commercial bank, lakehouse at Avant/Insulet/7-Eleven, hybrid Snowflake+Databricks at Janus Henderson. Load when you want concrete examples to ground a recommendation.
- `references/data-mesh-readiness-and-operating-model.md` — Readiness assessment and operating model for domain ownership, data products, self-service platform capabilities, federated governance, and transition planning. Load before recommending or rejecting mesh adoption.
- `references/event-driven-data-products.md` — Design guide for event-driven and analytical data products, including producer ownership, access modes, schema compatibility, replay, late data, and recovery. Load when operational events feed analytical or cross-domain consumers.

## Scripts & Templates

Use these resources only for their stated purpose:

- `scripts/governance-assessment.py` — Interactive governance maturity assessment. Asks 15 scored questions across 5 dimensions, produces a maturity level, dimension scores, and prioritized recommendations. Run when someone asks "how mature is our governance?"
- `templates/adr-template.md` — Fallback Architecture Decision Record template when no repository template exists; use `adr-authoring` for lifecycle and approval handling.
- `templates/architecture-design-session.md` — Structured workshop worksheet for current state, workloads, candidate patterns, decisions, experiments, and owners.

Usage:
```bash
# Interactive assessment
python3 scripts/governance-assessment.py

# Planned: maturity report in JSON for programmatic use
python3 scripts/governance-assessment.py --json
```

## When not to use

This skill is for data architecture strategy, design, and governance. Don't load it for:

- **Real-time pipeline debugging** — If a Kafka consumer is falling behind or an Airflow DAG keeps failing, you need an SRE or data engineer, not an architect.
- **SQL optimization** — Slow query? That's a tuning problem. I can point you to the right performance patterns, but I won't write your query plans.
- **Specific tool configuration** — "How do I set up RBAC in Snowflake?" / "What's the dbt YAML syntax for tests?" These are implementation details, not architecture decisions.
- **Interface contract semantics** — Event schemas, compatibility rules, and API or webhook contracts belong to `api-design-and-evolution`; this skill decides when a product needs those contracts and what consumers require.
- **Pipeline and platform implementation** — Building ingestion, transformations, event consumers, catalogs, or operating Kafka, Airflow, warehouses, and cloud resources belongs to `data-engineering` or `platform-engineering`.
- **Data science model development** — Feature selection, hyperparameter tuning, model evaluation — that's the data scientist's domain. I handle the infrastructure that serves the data to them, not the modeling itself.

## Common Anti-Patterns (Quick Reference)

Check for these decision failures:

- **Silver bullet thinking** — Adopting Data Mesh because it's trendy, not because your org is ready for domain ownership
- **Governance as an afterthought** — Deferring ownership, retention, and access decisions without a named follow-up owner
- **SoR vs SSoT confusion** — Treating a transactional System of Record (e.g. ERP) as the enterprise Single Source of Truth, creating a bottleneck
- **Neglecting the team** — Designing a system nobody can operate or troubleshoot

See all 13 with full remediations in `references/anti-patterns.md`.

## Completion

Complete when the requested review, decision comparison, or roadmap identifies the recommendation, tradeoffs, ownership, evidence gaps, and next validation step. Stop expanding discovery once enough context supports that artifact. If a decisive constraint remains unknown, deliver the conditional recommendation and the specific question or check needed to resolve it.
