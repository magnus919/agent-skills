---
name: api-design-and-evolution
description: >-
  Design, document, review, and evolve consumer-facing APIs and event interfaces.
  Use when choosing REST/HTTP, GraphQL, RPC, events, webhooks, or streaming; writing
  OpenAPI or AsyncAPI contracts; defining schemas, pagination, mutations, errors,
  idempotency, or API compatibility; or planning API versioning, deprecation, and
  migration. Use secure-software-engineering for a full security lifecycle, ADR
  authoring for durable architecture decisions, and spec-driven-development for a
  delivery specification and implementation gates.
license: MIT
compatibility: No runtime dependency. References version- and status-aware public standards indexed in references/source-index.md.
---

# API Design And Evolution

Design an interface as a durable agreement with its consumers, not a route list.
Start with the consumer job, domain meaning, authority boundary, and failure modes;
then choose the interface style and contract format. Keep facts, assumptions, and
policy decisions distinguishable.

## When To Use

Use for a new or changed REST/HTTP API, GraphQL schema, RPC operation, event or
message contract, webhook, or streaming interface. Use it before implementation and
again whenever consumer-visible behavior changes.

Do not use this as an ADR template, a complete product-discovery method, a security
assessment, or an implementation test plan. Hand those concerns to
[adr-authoring](../adr-authoring/SKILL.md),
[product-discovery](../product-discovery/SKILL.md),
[secure-software-engineering](../secure-software-engineering/SKILL.md), and
[verification-methodology](../verification-methodology/SKILL.md), respectively.

## Workflow

1. **Discover the agreement.** State consumer jobs, domain terms and invariants,
   authoritative data and schema owners, actors, object/action authority boundaries,
   data sensitivity, and failure modes. Record unanswered questions rather than
   inventing policy. Start [templates/api-design-brief.md](templates/api-design-brief.md).
2. **Choose the interface shape.** Compare interaction direction, coupling,
   delivery needs, query flexibility, mutation semantics, caching, observability,
   and evolution surface. Read [references/interface-selection.md](references/interface-selection.md).
   Record the choice and rejected options in the brief; use an ADR only when the
   choice is consequential beyond this interface.
3. **Make the contract explicit.** Define representations and their semantics,
   including null versus absent, defaults, enums/unions, identifiers, timestamps,
   units, ordering, filtering, and pagination. Use
   [templates/endpoint-contract.md](templates/endpoint-contract.md) with
   [references/contract-semantics.md](references/contract-semantics.md).
4. **Design mutation and failure behavior.** Define authority checks, preconditions,
   idempotency scope and equivalence, retries, concurrency, partial outcomes,
   long-running operation state, errors, and resource limits. Read
   [references/operations-and-failures.md](references/operations-and-failures.md)
   and create [templates/error-taxonomy.md](templates/error-taxonomy.md) when
   errors are shared across operations.
5. **Describe asynchronous delivery where relevant.** For messages, webhooks, or
   streams, state the publisher/subscriber perspective, envelope, delivery contract,
   duplicate/gap/reordering behavior, ordering scope, and security boundary. Read
   [references/events-webhooks-streaming.md](references/events-webhooks-streaming.md).
6. **Assess change from each consumer's perspective.** Inventory consumers,
   generated clients, strict decoders, signatures, caches, quotas, and operational
   dependencies. Complete [templates/compatibility-change-assessment.md](templates/compatibility-change-assessment.md).
   Do not call a change safe solely because it is additive.
7. **Plan and verify rollout.** For a deprecation or migration, use
   [templates/deprecation-migration-plan.md](templates/deprecation-migration-plan.md)
   and [references/evolution-and-deprecation.md](references/evolution-and-deprecation.md).
   Review the contract using [templates/contract-review.md](templates/contract-review.md).
   Test provider conformance, consumer expectations, compatibility diffs, examples,
   negative cases, and the deployed boundary.

## Reference Guide

| Load when | File |
|---|---|
| Selecting REST/HTTP, GraphQL, RPC, event/message, webhook, or streaming | [references/interface-selection.md](references/interface-selection.md) |
| Modeling data, collection reads, schemas, or OpenAPI | [references/contract-semantics.md](references/contract-semantics.md) |
| Designing writes, errors, retry behavior, limits, or authorization handoff | [references/operations-and-failures.md](references/operations-and-failures.md) |
| Designing event contracts, webhook delivery, or streams | [references/events-webhooks-streaming.md](references/events-webhooks-streaming.md) |
| Reviewing compatibility, versions, deprecation, migration, or rollback | [references/evolution-and-deprecation.md](references/evolution-and-deprecation.md) |
| Preparing contract/provider/consumer/deployment verification | [references/contract-verification.md](references/contract-verification.md) |
| Checking exact sources, versions, status, and intended use | [references/source-index.md](references/source-index.md) |
| Exercising required edge cases before claiming readiness | [references/scenario-probes.md](references/scenario-probes.md) |

## Security Boundary

Document authentication requirements and server-side object/action authorization in
the interface contract. For the threat model, credential handling, tenant isolation,
untrusted URLs or files, webhook signature design, output minimization, redaction,
or abuse resistance, load
[secure-software-engineering](../secure-software-engineering/SKILL.md). An API
contract cannot prove that an authorization boundary is enforced.

## Completion

Stop when the selected interface has an owner, an authoritative contract, explicit
consumer and failure assumptions, a compatibility assessment for each change, and
evidence or an explicit gap for each required review item. Escalate unresolved domain
semantics, authority, delivery, or consumer-impact questions to their accountable
owner.
