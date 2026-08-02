# Discovery Brief: Privacy Engineering

## Survey scope

This brief surveys adjacent skills in the agent-skills catalog to define the ownership boundaries of `privacy-engineering`. The goal is to own the translation of privacy principles into verifiable engineering artifacts — without duplicating legal interpretation, security implementation, security auditing, data architecture, incident response, production readiness, product analytics, or agent observability.

## Skills surveyed

### legal-strategy

**What legal-strategy owns:** Regulatory landscape analysis (GDPR, CCPA, AI Act, HIPAA, sector-specific), IP strategy, contract risk assessment (indemnification, liability caps, DPAs), data privacy frameworks (privacy-by-design, DPIAs, data mapping, breach response), corporate governance, and employment law. It is the authoritative source for legal interpretation and regulatory applicability.

**Boundary:** Legal-strategy interprets the law and determines which regulatory regimes apply. Privacy engineering consumes those interpretations as input and translates them into verifiable engineering artifacts. Legal-strategy says "Article 17 of GDPR establishes a right to erasure under specified conditions"; privacy engineering says "here is the deletion verification plan: data for user X must be removed from primary store within 72 hours, from backups within 30 days, from analytics exports within 7 days, verified by checksum comparison and row-count audit."

**Concrete example — data subject access request:** A user submits a DSAR under GDPR. Legal-strategy determines whether the request is valid, what data categories are in scope, and whether any exemptions apply. Privacy engineering designs and verifies the technical path: which stores contain the user's data, how it is retrieved, how the response is assembled, what redactions apply, and how the response is delivered within the statutory timeline. Legal-strategy owns the "whether and what"; privacy engineering owns the "how and verify."

**Routing decision:** Privacy engineering routes all regulatory interpretation questions to legal-strategy. It never determines whether GDPR, CCPA, or any other regulation applies. It never interprets the scope of a legal obligation. When a question starts with "does this regulation require..." or "are we subject to...", escalate to legal-strategy.

### secure-software-engineering

**What secure-software-engineering owns:** Security requirements, threat modeling, secure design, authentication and authorization, input validation, secrets lifecycle, dependency supply chain, secure code review, multi-tenant isolation (security dimension), and release evidence. It builds security into decisions before defects reach production.

**Boundary:** Secure-software-engineering owns the security implementation — the controls that enforce privacy requirements. Privacy engineering defines *what* protections are needed; security engineering implements *how* those protections work. Privacy engineering says "PII at rest must be encrypted and access must be logged with an immutable audit trail"; security engineering selects the encryption scheme (AES-256-GCM), manages the key hierarchy, configures the KMS, implements the audit-log pipeline, and verifies the implementation through security review.

**Concrete example — encryption of PII at rest:** Privacy engineering defines the requirement: "All PII fields (name, email, phone, address) must be encrypted at rest with access logging. Access logs must be immutable and retained for 1 year." Security engineering implements: TDE on the database, application-level field encryption with envelope encryption, KMS key policy, CloudTrail/Database audit logging, log immutability via WORM storage or append-only ledger. Privacy engineering verifies: does the encryption actually cover all PII fields? Can we prove no PII field is stored in plaintext? Security engineering owns the implementation and the security review; privacy engineering owns the requirement and the privacy-dimension verification.

**Routing decision:** Privacy engineering routes security implementation to secure-software-engineering. It does not select encryption algorithms, design authentication protocols, manage secrets, or threat-model the system. It does consume security evidence as input to privacy verification (e.g., encryption-at-rest evidence satisfies the "PII must be encrypted" acceptance criterion).

### security-audit-methodology

**What security-audit-methodology owns:** Authorized security assessments — threat modeling (STRIDE, attack trees), vulnerability assessment (CVSS, CWE), security architecture review (authN/Z, data flow, secrets), dependency analysis (SBOM, CVE), and security testing guidance. It is the authoritative source for finding and classifying security weaknesses.

**Boundary:** Security-audit-methodology assesses whether security controls are correctly implemented and whether vulnerabilities exist. Privacy engineering assesses whether privacy requirements are satisfied by the implemented controls and whether privacy-specific gaps exist (e.g., data retained beyond its purpose, PII in an unanticipated store, deletion not verified). A security audit might find that a database is properly encrypted and access-controlled (security pass); a privacy review might find that the same database retains user data 18 months beyond the declared retention period (privacy gap).

**Concrete example — audit of a user-data store:** Security audit finds: TLS 1.3 configured, AES-256 encryption at rest, IAM roles correctly scoped, no CVEs in database version, access logging enabled. Security verdict: controls are adequate. Privacy engineering finds: the store contains email addresses that were collected for "account recovery" but are also used for "marketing personalization" (purpose mismatch); the retention policy says 90 days but data from 2019 is still present (retention violation); the deletion procedure does not cover the read-replica (incomplete deletion). Privacy verdict: three gaps, each requiring a verifiable fix.

**Routing decision:** Privacy engineering routes vulnerability assessment and security-control verification to security-audit-methodology. Security audit findings are evidence for privacy verification (e.g., "encryption at rest confirmed by security audit" satisfies one privacy acceptance criterion), but security audit does not assess purpose limitation, retention compliance, or deletion completeness.

### data-engineering

**What data-engineering owns:** Database operations (schema management, indexing, backup/recovery, migration), ETL/ELT pipeline design (dbt patterns, incremental loading), SQL analytical patterns, data quality monitoring, storage infrastructure, and backup strategy implementation (WAL archiving, snapshots). It is the authoritative source for data infrastructure.

**Boundary:** Data-engineering owns the implementation of storage, pipelines, and backup mechanics. Privacy engineering owns the requirements that those implementations must satisfy: what retention periods apply, what deletion behavior is required, where data may reside, and how those behaviors are verified. Data engineering designs the partition scheme that enables deletion by user ID; privacy engineering defines the deletion SLA and verifies it.

**Concrete example — user-data deletion:** Privacy engineering defines: "Upon verified account closure, user PII must be deleted from all primary stores within 72 hours, from all backups within 30 days, and from all analytics-derived datasets within 7 days. Deletion must be verified by row-count audit and sampling." Data engineering implements: the deletion stored procedure with partition-aware execution, the backup rotation that ages out old snapshots, the dbt model that filters deleted users from derived tables, the monitoring that tracks deletion job completion. Privacy engineering verifies: after deletion, can we find any trace of the user's PII in any store? Is the 72-hour SLA met? Data engineering owns the implementation; privacy engineering owns the requirement and the verification.

**Routing decision:** Privacy engineering routes pipeline implementation, storage architecture, backup mechanics, and schema design to data-engineering. It does not write SQL, design partition schemes, configure backup schedules, or manage database infrastructure. It does define the data requirements that drive those decisions and verifies the outcomes.

### production-readiness

**What production-readiness owns:** Assembling cross-domain evidence into a launch decision — an 11-category evidence packet (ownership, user/business outcome, dependencies, SLOs, observability, support, security, data, rollback, capacity, cost) — and producing go/no-go/defer/exception outcomes with accountable owners.

**Boundary:** Production-readiness assembles evidence from all domains, including privacy. Privacy engineering produces the privacy-dimension evidence that feeds the readiness packet: data classification, retention/deletion verification, data-flow maps, privacy acceptance criteria. Production-readiness does not produce privacy evidence itself; it consumes it as one of the 11 categories (primarily under "data" and "security").

**Concrete example — launching a feature that processes user health data:** Privacy engineering produces: a data-lifecycle record tracing health-data flow, privacy acceptance criteria (e.g., "health data fields are encrypted at rest, verified by audit log review; health data is not transmitted to analytics pipeline, verified by schema inspection"), a retention/deletion verification plan, and a privacy change review. Production-readiness consumes these as evidence for the "data" and "security" categories in the readiness packet. If privacy engineering reports a gap (e.g., "deletion verification not yet exercised"), production-readiness records it as a missing-evidence entry and may produce a "no-go" or "exception" outcome.

**Routing decision:** Privacy engineering feeds production-readiness. Privacy artifacts are required inputs to the production-readiness evidence packet for any change that touches PII or crosses a trust boundary. Privacy engineering does not make the launch decision; production-readiness owns that outcome.

### product-analytics-and-measurement

**What product-analytics-and-measurement owns:** Metric trees, event/tracking plans, instrumentation QA, measurement governance, dashboard contracts, and privacy-aware measurement design. It is the authoritative source for turning product outcomes into observable, governed evidence.

**Boundary:** Product-analytics-and-measurement owns the measurement strategy — what to track, how to define events, and how to verify instrumentation quality. Privacy engineering owns the privacy constraints on measurement: the consent boundary, minimization rules, aggregation thresholds, retention periods, and deletion behavior. Product analytics designs the tracking plan within those constraints; privacy engineering verifies that the implementation satisfies the constraints.

**Concrete example — adding analytics to a health app:** Privacy engineering defines: pre-consent events limited to session-start and error-occurred (no user properties); post-consent events may include feature-usage with hashed user ID; no health-condition data in analytics under any consent state; raw events retained 90 days; aggregated metrics require minimum cohort of 100; deletion requests must cascade to raw events within 7 days. Product-analytics-and-measurement designs: the event taxonomy consistent with these constraints, the tracking plan with property schemas that exclude health-condition fields, the identity resolution that uses hashed IDs post-consent, and the instrumentation QA checklist that verifies no health-condition data appears in the analytics pipeline.

**Routing decision:** Privacy engineering defines the privacy constraints; product-analytics-and-measurement designs the measurement strategy within them. Privacy engineering does not design metric trees, event taxonomies, or tracking plans. Product-analytics-and-measurement does not define retention periods, consent boundaries, or deletion requirements.

### agent-evals-and-observability

**What agent-evals-and-observability owns:** Agent evaluation design, dataset management, grader calibration, trajectory review, regression analysis, release gates, and production observability (traces, logs, metrics, privacy controls). It is the authoritative source for agent evaluation methodology and telemetry instrumentation.

**Boundary:** Agent-evals-and-observability owns the evaluation and observability implementation — how traces are collected, how datasets are versioned, how graders are calibrated. Privacy engineering owns the privacy requirements for agent traces and telemetry: what must be minimized, redacted, retained, and deletable. Agent-evals-and-observability implements the collection pipeline within those constraints; privacy engineering verifies the constraints are satisfied.

**Concrete example — agent trace collection for debugging:** Privacy engineering defines: prompt content and tool arguments must be redacted before traces leave the execution environment; redaction must occur at collection time, not post-storage; trace retention is 72 hours for debugging; traces must be deletable by user ID; consent is required before trace collection in user-facing agents. Agent-evals-and-observability implements: the OpenTelemetry pipeline with a redaction processor, the trace store with TTL-based expiration, the deletion API, and the consent gate. Privacy engineering verifies: does the redaction actually strip PII from traces? Can we prove that redaction happened before the trace left the execution boundary?

**Routing decision:** Privacy engineering defines privacy requirements for agent telemetry; agent-evals-and-observability implements the collection and observability infrastructure. Privacy engineering does not design trace schemas, configure OpenTelemetry, or calibrate graders. Agent-evals-and-observability does not define retention periods, consent boundaries, or redaction rules.

### incident-learning (same-wave skill, prose only)

**What incident-learning will own:** Separation of observed facts from causal hypotheses and contributing conditions; mapping follow-up work across code, tests, skills, operations, product, and governance; closure defined as verification that the intended change occurred. It is the pipeline that converts incident findings into verified, owned follow-up work.

**Boundary:** Incident-learning will own the post-incident learning pipeline. Privacy engineering feeds privacy-incident findings (e.g., a deletion-verification failure, a consent-boundary violation) into that pipeline. Privacy engineering identifies the privacy gap and produces the initial evidence; incident-learning tracks the fix to verified closure.

**Routing decision:** Privacy engineering feeds incident-learning with privacy-incident evidence, but does not own the verified-closure pipeline. It defines what constitutes a privacy incident and what evidence is required; incident-learning owns the follow-up-work lifecycle.

### agent-production-operations (M3 bundle, prose only)

**What agent-production-operations will own:** Composing production-readiness, migration-engineering, resilience-and-recovery, capacity-and-cost-engineering, and incident-learning into a unified production evidence packet for agent workloads.

**Boundary:** Agent-production-operations will consume privacy evidence — data-lifecycle records, privacy acceptance criteria, retention/deletion verification plans — as input to production readiness decisions for agent systems. Privacy engineering produces the privacy dimension of that evidence packet.

**Routing decision:** Privacy engineering feeds the agent-production-operations bundle. Privacy artifacts are required inputs for agent systems that process user data, log conversations, or operate across jurisdictional boundaries.

## What privacy engineering does NOT own

- **Legal interpretation**: owned by legal-strategy. Privacy engineering does not determine regulatory applicability, interpret legal scope, or provide legal advice.
- **Security implementation**: owned by secure-software-engineering. Privacy engineering does not select encryption algorithms, design authN/Z, manage secrets, or implement security controls.
- **Security auditing**: owned by security-audit-methodology. Privacy engineering does not find CVEs, score vulnerabilities, or assess security-control correctness.
- **Data infrastructure**: owned by data-engineering. Privacy engineering does not design schemas, implement pipelines, configure backups, or manage storage.
- **Incident command**: owned by site-reliability-engineering. Privacy engineering does not run live incident response.
- **Post-incident learning pipeline**: owned by incident-learning (same-wave, prose). Privacy engineering feeds findings but does not own the closure pipeline.
- **Production readiness decisions**: owned by production-readiness. Privacy engineering feeds privacy evidence but does not make go/no-go calls.
- **Measurement strategy**: owned by product-analytics-and-measurement. Privacy engineering defines constraints; measurement design stays with product analytics.
- **Agent telemetry implementation**: owned by agent-evals-and-observability. Privacy engineering defines requirements; implementation stays with agent observability.

## Summary

Privacy engineering fills a gap between legal interpretation (which produces policy) and security/data implementation (which produces controls and infrastructure). It is the method for translating privacy requirements into verifiable engineering artifacts — data-lifecycle records, privacy acceptance criteria, retention/deletion verification plans, data-flow maps, and privacy change reviews. It routes legal questions to legal counsel, security implementation to security engineering, and data infrastructure to data engineering. It produces evidence that feeds production-readiness, incident-learning, and agent-production-operations.
