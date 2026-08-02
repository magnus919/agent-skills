---
name: privacy-engineering
description: >-
  Translate privacy principles and legal requirements into data-flow, lifecycle,
  acceptance, and verification artifacts. Map data classification, purpose,
  processing, access, retention, deletion, residency, and consent; define
  verifiable privacy acceptance criteria; and produce data-lifecycle records,
  retention/deletion verification plans, and privacy change reviews. Use when
  engineering privacy into a system, feature, or data flow — not for legal
  advice, jurisdiction-specific regulatory interpretation, or replacing security
  engineering or incident response.
license: MIT
compatibility: No runtime dependency. Host-, platform-, and regulation-neutral methodology.
metadata:
  tags: privacy-engineering, data-lifecycle, retention, deletion, residency, consent,
    data-classification, privacy-acceptance-criteria, privacy-change-review,
    minimization, tenant-isolation
---

# Privacy Engineering

Translate privacy principles into engineering artifacts that are observable,
testable, and verifiable. This skill does not provide legal advice and does not
substitute for jurisdiction-specific regulatory interpretation; those belong to
qualified legal counsel and to [legal-strategy](../legal-strategy/SKILL.md).

## Disclaimer

**This skill does not provide legal advice.** It provides an engineering method
for translating privacy requirements (whether derived from GDPR, CCPA, HIPAA,
internal policy, or contractual obligations) into verifiable technical artifacts.
Jurisdiction-specific regulatory interpretation must be escalated to qualified
legal counsel. Do not use this skill to determine whether a specific regulatory
regime applies or to interpret the legal scope of a privacy obligation.

## When to use

Load this skill when the task involves engineering privacy into a system,
feature, or data flow:

- Map data classification, purpose, processing activities, access patterns,
  retention periods, deletion workflows, residency constraints, and consent
  flows.
- Define privacy acceptance criteria that are testable and verifiable — not
  policy prose alone.
- Produce a data-lifecycle record that traces data from collection through
  deletion across all stores and backups.
- Design a retention/deletion verification plan with measurable success
  conditions (e.g., "data for user X deleted from all primary stores within
  Y hours of verified account closure").
- Map data flows across service boundaries, tenant boundaries, and geographic
  regions, identifying where PII transits or resides.
- Review a change (feature, schema, integration, AI pipeline) for privacy impact
  and produce a privacy change review.
- Address privacy implications of agent traces (LLM conversation logs, tool-call
  history) and product analytics telemetry.
- Integrate consent and revocation signals into system behavior.
- Apply data minimization and purpose limitation at the engineering level.
- Define tenant-boundary isolation requirements for multi-tenant data.

## When not to use

- **Legal advice or regulatory interpretation**: route to
  [legal-strategy](../legal-strategy/SKILL.md). Privacy engineering translates
  legal requirements into engineering artifacts; it does not interpret the law.
- **Security implementation** (authN/Z, encryption at rest/transit, threat
  modeling, vulnerability management): route to
  [secure-software-engineering](../secure-software-engineering/SKILL.md).
  Privacy engineering defines *what* data protections are required; security
  engineering implements *how* those protections are enforced.
- **Security auditing and vulnerability assessment**: route to
  [security-audit-methodology](../security-audit-methodology/SKILL.md).
- **Data architecture, schema design, storage selection, pipeline
  implementation**: route to
  [data-engineering](../data-engineering/SKILL.md). Privacy engineering defines
  retention and deletion requirements; data engineering implements the storage
  and pipeline mechanics.
- **Incident response and live-service reliability**: the skill names
  privacy-incident triggers and evidence requirements, but live incident
  command belongs to
  [site-reliability-engineering](../site-reliability-engineering/SKILL.md)
  and post-incident learning to incident-learning (same-wave skill; prose
  reference only).
- **Production readiness evidence assembly and launch decisions**: route to
  [production-readiness](../production-readiness/SKILL.md). Privacy engineering
  produces the privacy-dimension evidence that feeds the readiness packet.
- **Product analytics measurement design**: route to
  [product-analytics-and-measurement](../product-analytics-and-measurement/SKILL.md).
  Privacy engineering defines the privacy constraints on measurement; product
  analytics designs the measurement strategy within those constraints.
- **Agent evaluation design and observability instrumentation**: route to
  [agent-evals-and-observability](../agent-evals-and-observability/SKILL.md).
  Privacy engineering defines privacy requirements for agent traces and
  telemetry; agent-evals-and-observability implements the minimized,
  redacted collection.

## Privacy dimensions (structured concerns)

Every privacy engineering engagement must address these seven dimensions.
At least six must appear as structured fields (checklist items, table rows,
or labeled fields) in any artifact produced; all seven must be present
somewhere in the body of work.

| # | Dimension | Engineering concern |
|---|---|---|
| 1 | **Purpose** | What is the declared purpose for collecting/processing this data? Is each processing activity tied to a specific, explicit purpose? |
| 2 | **Lifecycle (retention)** | What is the retention period for each data category? What triggers the retention clock? Where is the retention policy enforced? |
| 3 | **Access** | Who or what can access this data? Under what conditions? Is access logged and reviewed? Are access patterns consistent with the declared purpose? |
| 4 | **Deletion** | How is data deleted when retention expires or a deletion request is received? Is deletion verified across all stores, backups, caches, and derived datasets? |
| 5 | **Tenant / isolation** | How is data isolated between tenants? Are tenant-boundary violations detectable? Are cross-tenant queries prevented by default? |
| 6 | **Residency** | Where does data reside at rest and in transit? Are there geographic or jurisdictional constraints on data location? Are residency constraints enforced at the infrastructure level? |
| 7 | **Consent** | Is consent obtained before data collection? Can consent be withdrawn? Is the system behavior different pre-consent, post-consent, and post-revocation? |

## Working method

1. **Start from purpose, not technology.** For every data element, ask: why is
   this collected? What outcome does it serve? If the purpose cannot be stated
   in one sentence, the data element is suspect.

2. **Classify before you collect.** Assign a data classification (public,
   internal, confidential, restricted/PII) and a purpose label before
   instrumentation or storage is designed.

3. **Map the full data lifecycle.** Trace each data category from collection
   through processing, storage, access, archival, and deletion. Include caches,
   replicas, backups, logs, and derived datasets. A lifecycle that ends at
   "primary database" is incomplete.

4. **Define verifiable acceptance criteria.** Every privacy requirement must
   produce at least one acceptance criterion that is testable — a specific,
   measurable condition with a verification method and a pass/fail condition.
   "Data is handled securely" is not verifiable. "PII does not appear in
   analytics export" is.

5. **Verify deletion, not just policy.** A retention policy that is not
   verified through a deletion test is a policy document, not an engineering
   artifact. Produce a retention/deletion verification plan and exercise it.

6. **Route legal interpretation to legal counsel.** When a question requires
   interpreting the scope of a regulation, determining applicability, or
   resolving a legal ambiguity, escalate — do not interpret.

7. **Address agent traces and product telemetry explicitly.** Any system that
   logs LLM conversations, tool-call history, user interactions, or product
   analytics must have privacy controls designed before collection begins.

## Agent traces and product analytics telemetry

### Agent traces

Agent traces include LLM conversation logs, tool-call arguments and responses,
intermediate reasoning, and agent state transitions. These traces often contain
sensitive data: user prompts, system context, tool outputs, and PII that the
agent accessed during a task.

Privacy engineering for agent traces requires:

- **Minimization**: capture only what is necessary for the declared purpose
  (debugging, evaluation, audit). Strip prompt content, tool arguments, and
  intermediate reasoning before storage unless each field is justified.
- **Redaction**: apply redaction before traces leave the execution boundary.
  Redact PII, credentials, and sensitive context. Redaction is not a
  post-storage filter — it must happen at collection time.
- **Retention**: define a trace retention period tied to a specific purpose.
  Debugging traces may need hours; evaluation datasets may need longer but
  require consent and provenance.
- **Deletion**: traces must be deletable. A deletion request must remove traces
  from all stores (primary, archive, backup) and the deletion must be
  verifiable.
- **Consent**: where traces contain user content, consent must be obtained
  before collection. Consent revocation must stop future collection and trigger
  deletion of existing traces where legally required.

### Product analytics telemetry

Product analytics telemetry includes event streams, user-behavior tracking,
feature-usage metrics, and session recordings. Privacy engineering defines the
constraints; [product-analytics-and-measurement](../product-analytics-and-measurement/SKILL.md)
designs the measurement strategy within those constraints.

Privacy engineering for analytics telemetry requires:

- **Consent boundary**: define what is measured before consent, after consent,
  and what is never measured. The pre-consent set must be minimal — strictly
  necessary for system operation.
- **Minimization**: collect only properties that serve a declared measurement
  purpose. Speculative properties ("we might need this later") are rejected.
- **Aggregation threshold**: metrics must not be reported when the contributing
  cohort falls below a minimum size that risks re-identification.
- **Retention and deletion**: raw event retention period must be defined.
  Deletion requests must cascade to derived datasets and aggregated metrics
  where the individual contribution is identifiable.
- **Jurisdictional awareness**: note when telemetry crosses regulatory
  boundaries. The engineering artifacts record the constraint; legal
  interpretation of applicability is escalated.

## File map

| Path | Loaded when |
|---|---|
| [references/discovery-brief.md](references/discovery-brief.md) | Understanding ownership boundaries between legal, privacy, security, and data engineering |
| [templates/data-lifecycle-record.md](templates/data-lifecycle-record.md) | Producing a full data-lifecycle record from collection through deletion |
| [templates/privacy-acceptance-criteria.md](templates/privacy-acceptance-criteria.md) | Defining verifiable, testable privacy acceptance criteria with verification methods and pass/fail conditions |
| [templates/data-flow-and-access-map.md](templates/data-flow-and-access-map.md) | Mapping data flows across services, tenants, and regions with access patterns |
| [templates/retention-deletion-verification-plan.md](templates/retention-deletion-verification-plan.md) | Designing a retention/deletion verification plan with measurable success conditions |
| [templates/privacy-change-review.md](templates/privacy-change-review.md) | Reviewing a change for privacy impact and producing a privacy change review |
| [evals/evals.json](evals/evals.json) | Evaluating the skill's output quality across representative scenarios |

## Routing and ownership boundaries

### What this skill owns

- Privacy requirements translation into engineering artifacts.
- Data lifecycle tracing (collection → processing → storage → access → deletion).
- Privacy acceptance criteria (verifiable, testable, measurable).
- Retention and deletion verification planning.
- Consent and revocation engineering.
- Tenant-boundary isolation requirements.
- Residency constraint engineering.
- Privacy change review.
- Privacy dimension of agent traces and product analytics.

### What this skill does NOT own

- **Legal interpretation**: owned by [legal-strategy](../legal-strategy/SKILL.md).
  Privacy engineering consumes legal requirements as input; it does not produce
  them or interpret regulatory scope.
- **Security implementation**: owned by
  [secure-software-engineering](../secure-software-engineering/SKILL.md).
  Privacy engineering says "PII must be encrypted at rest"; security engineering
  selects the encryption scheme, manages keys, and verifies implementation.
- **Security auditing**: owned by
  [security-audit-methodology](../security-audit-methodology/SKILL.md).
- **Data architecture and pipeline implementation**: owned by
  [data-engineering](../data-engineering/SKILL.md). Privacy engineering
  defines retention periods and deletion requirements; data engineering
  implements the storage, backup, and pipeline mechanics that satisfy them.
- **Incident response**: owned by
  [site-reliability-engineering](../site-reliability-engineering/SKILL.md)
  for live command; incident-learning (same-wave, prose only) for post-incident
  learning. Privacy engineering defines what constitutes a privacy incident and
  what evidence is required; it does not run incident command.
- **Production readiness**: owned by
  [production-readiness](../production-readiness/SKILL.md).
  Privacy engineering feeds the privacy-dimension evidence into the readiness
  packet.
- **Product analytics measurement**: owned by
  [product-analytics-and-measurement](../product-analytics-and-measurement/SKILL.md).
  Privacy engineering defines the privacy constraints; product analytics
  designs measurement within them.
- **Agent evaluation and telemetry**: owned by
  [agent-evals-and-observability](../agent-evals-and-observability/SKILL.md).
  Privacy engineering defines the privacy requirements for telemetry.

### Feeds (prose references to skills not yet landed)

Privacy engineering produces artifacts that feed:
- **agent-production-operations** (M3 bundle) — privacy acceptance criteria
  and data-lifecycle records as production evidence.
- **incident-learning** (same-wave skill) — privacy incident evidence and
  change-review findings for post-incident learning pipeline.

## Core principles

- **Purpose before collection**: no data element is collected without a
  declared, specific purpose. "It might be useful later" is not a purpose.
- **Minimization by default**: collect the minimum set of data properties
  needed to satisfy the declared purpose. Reject speculative collection.
- **Deletion is a feature**: every data element has a defined end of life.
  Deletion must be verifiable — a policy that says "data is deleted after 90
  days" without a verification plan is not an engineering artifact.
- **Verifiable, not aspirational**: every privacy requirement produces
  acceptance criteria with a verification method and pass/fail condition.
  "Data is handled securely" fails this standard.
- **Consent is a state machine**: consent is obtained, recorded, honored, and
  revocable. System behavior must differ measurably across pre-consent,
  post-consent, and post-revocation states.
- **Tenant isolation is a hard boundary**: in multi-tenant systems, data from
  one tenant must never be accessible to another. Cross-tenant queries must
  be prevented by default, not filtered after the fact.
- **Escalate jurisdictional questions**: when a requirement depends on
  whether a specific regulation applies or how a jurisdiction interprets a
  privacy obligation, escalate to legal counsel. This skill does not answer
  those questions.
