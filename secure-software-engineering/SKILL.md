---
name: secure-software-engineering
description: >-
  Use when designing or implementing software securely: define security requirements,
  threat-model a feature, choose secure defaults, design authentication and authorization,
  handle untrusted data and secrets, evaluate dependencies, or review security-sensitive
  changes. Use for prevention during requirements, design, implementation, and review;
  not for post-build security assessments or scanning an existing codebase.
license: MIT
compatibility: No runtime dependency. Host-neutral guidance for authorized software engineering work.
---

# Secure Software Engineering

Build security into decisions before defects reach production. This is a prevention-oriented workflow, not a claim that a design or release is secure. Record assumptions, the evidence collected, residual risks, and the owner of any accepted exception.

## When To Use

Use this skill to answer "How do we build this securely?" for a new feature, integration, service, API, tenant boundary, AI capability, or release. Start early and revisit affected decisions when architecture, data flows, dependencies, or threats change.

Do not use it for an authorized post-build assessment: use [security-audit-methodology](../security-audit-methodology/SKILL.md). Do not use it as a vulnerability scanner for an existing codebase; use an authorized scanning tool or specialist security assessment. Use [spec-driven-development](../spec-driven-development/SKILL.md) when the task is to formalize the resulting requirements and phase gates, and [verification-methodology](../verification-methodology/SKILL.md) to make evidence-backed completion claims.

## Workflow

1. **Requirements**: identify assets, actors, harm, data classifications, regulatory or contractual constraints, and security outcomes. Write testable acceptance criteria before selecting controls.
2. **Threat model**: map data flows and trust boundaries; state assumptions, abuse cases, mitigations, and residual risk. STRIDE is optional vocabulary, not an exhaustive method.
3. **Design**: choose controls that fit the trust model, including server-side authorization, data isolation, safe failure behavior, and AI capability boundaries. Explain rejected alternatives.
4. **Implement**: make each boundary enforceable in code and configuration; protect input, output, credentials, dependencies, logs, and operational paths.
5. **Review and release**: verify controls with direct evidence, review changes for bypasses, preserve release evidence, and feed incidents or near misses into requirements and tests.

Loop to the affected phase when evidence contradicts an assumption or a design changes. Stop when each material decision has an accountable owner, direct evidence or an explicit gap, and a disposition for residual risk.

## Reference Files

| Load when | File |
|---|---|
| You need a version-pinned source and its decision use | [references/source-index.md](references/source-index.md) |
| Defining assets, boundaries, abuse cases, or security criteria | [references/security-requirements-threat-modeling.md](references/security-requirements-threat-modeling.md) |
| Choosing identity, sessions, permissions, or service access | [references/authentication-authorization.md](references/authentication-authorization.md) |
| Handling requests, files, URLs, serialized data, output, or AI content | [references/input-validation-data-handling.md](references/input-validation-data-handling.md) |
| Adding a key, token, credential, or signing material | [references/secrets-lifecycle.md](references/secrets-lifecycle.md) |
| Adding, updating, building, or publishing dependencies | [references/dependency-supply-chain.md](references/dependency-supply-chain.md) |
| Designing logs, audit events, monitoring, or forensic evidence | [references/secure-logging-audit.md](references/secure-logging-audit.md) |
| Sharing infrastructure or data across tenants | [references/multi-tenant-isolation.md](references/multi-tenant-isolation.md) |
| Reviewing a change or defining a security review gate | [references/secure-code-review.md](references/secure-code-review.md) |
| Preparing artifacts, exceptions, rollback, or response for release | [references/release-evidence.md](references/release-evidence.md) |
| Learning from an incident, near miss, or escaped defect | [references/incident-learning.md](references/incident-learning.md) |
| Designing an LLM, RAG pipeline, model integration, or agent tool | [references/ai-llm-security.md](references/ai-llm-security.md) |

## Templates

| Use when | File |
|---|---|
| Starting a feature or system threat model | [templates/lightweight-threat-model.md](templates/lightweight-threat-model.md) |
| Writing security acceptance criteria for a specification or change | [templates/security-acceptance-criteria.md](templates/security-acceptance-criteria.md) |
| Reviewing a security-relevant code change | [templates/secure-code-review-checklist.md](templates/secure-code-review-checklist.md) |

## Guardrails

- Treat prompts, retrieved content, tool output, webhooks, files, and client-provided identity or tenant fields as untrusted until a boundary validates them.
- A framework, scan, SBOM, signature, provenance attestation, or checklist is evidence about a limited claim, not proof that software is safe.
- Do not make a control universal: authentication protocols depend on the trust model; row-level security is one isolation mechanism; secret rotation follows events and risk; controls need verification in their actual deployment.
- Keep completed threat models and security acceptance criteria confidential when they expose system boundaries or weaknesses. Use placeholders, never real credentials or private deployment details.

## Portability

Use the host environment's normal mechanisms to create artifacts, run tests, and obtain approvals. Do not assume a vendor, cloud, identity provider, database, CI system, or deployment topology.
