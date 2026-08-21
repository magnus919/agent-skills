---
name: api-design-and-evolution
description: >-
  Design, govern, document, review, and evolve consumer-facing APIs and event
  interfaces. Use when choosing REST/HTTP, GraphQL, RPC, events, webhooks, or
  streaming; writing OpenAPI or AsyncAPI contracts; assessing an API landscape,
  ownership, duplication, lifecycle, discoverability, retirement, gateways, service
  meshes, north-south or east-west traffic, routing, policy, observability, or failure
  boundaries; defining schemas, pagination, mutations, errors, idempotency, or
  compatibility; or planning versioning, deprecation, and migration. Do not use for
  product discovery, platform operations, full security assessment, ADR authoring,
  or delivery gates; route those to the neighboring specialist skills.
license: MIT
compatibility: No runtime dependency. References version- and status-aware public standards indexed in references/source-index.md.
---

# API Design And Evolution

Design an interface as a durable agreement with its consumers, not a route list.
Start with the consumer job, domain meaning, authority boundary, and failure modes;
then choose the interface style and contract format. Keep facts, assumptions, and
policy decisions distinguishable.

## When to use

Use for a new or changed REST/HTTP API, GraphQL schema, RPC operation, event or
message contract, webhook, or streaming interface. Use it before implementation and
again whenever consumer-visible behavior changes.

## When not to use

Do not use this as an ADR template, a complete product-discovery method, a security
assessment, or an implementation test plan. Hand those concerns to
[adr-authoring](../adr-authoring/SKILL.md),
[product-discovery](../product-discovery/SKILL.md),
[secure-software-engineering](../secure-software-engineering/SKILL.md), and
[verification-methodology](../verification-methodology/SKILL.md), respectively.

## Workflow

1. **Classify the scope.** If the request spans more than one interface, start
   [templates/api-landscape-assessment.md](templates/api-landscape-assessment.md) and
   read [references/api-landscape-and-governance.md](references/api-landscape-and-governance.md).
   If it changes where traffic is admitted, routed, observed, or isolated, read
   [references/api-infrastructure-topologies.md](references/api-infrastructure-topologies.md).
   Keep portfolio findings separate from any individual contract decision.
2. **Discover the agreement.** State consumer jobs, domain terms and invariants,
   authoritative data and schema owners, actors, object/action authority boundaries,
   data sensitivity, and failure modes. Record unanswered questions rather than
   inventing policy. Start [templates/api-design-brief.md](templates/api-design-brief.md).
3. **Choose the interface shape.** Compare interaction direction, coupling,
   delivery needs, query flexibility, mutation semantics, caching, observability,
   and evolution surface. Read [references/interface-selection.md](references/interface-selection.md).
   Record the choice and rejected options in the brief; use an ADR only when the
   choice is consequential beyond this interface.
4. **Make the contract explicit.** Define representations and their semantics,
   including null versus absent, defaults, enums/unions, identifiers, timestamps,
   units, ordering, filtering, and pagination. Use
   [templates/endpoint-contract.md](templates/endpoint-contract.md) with
   [references/contract-semantics.md](references/contract-semantics.md).
5. **Design mutation and failure behavior.** Define authority checks, preconditions,
   idempotency scope and equivalence, retries, concurrency, partial outcomes,
   long-running operation state, errors, and resource limits. Read
   [references/operations-and-failures.md](references/operations-and-failures.md)
   and create [templates/error-taxonomy.md](templates/error-taxonomy.md) when
   errors are shared across operations.
6. **Describe asynchronous delivery where relevant.** For messages, webhooks, or
   streams, state the publisher/subscriber perspective, envelope, delivery contract,
   duplicate/gap/reordering behavior, ordering scope, and security boundary. Read
   [references/events-webhooks-streaming.md](references/events-webhooks-streaming.md).
7. **Assess change from each consumer's perspective.** Inventory consumers,
   generated clients, strict decoders, signatures, caches, quotas, and operational
   dependencies. Complete [templates/compatibility-change-assessment.md](templates/compatibility-change-assessment.md).
   Do not call a change safe solely because it is additive.
8. **Plan and verify rollout.** For a deprecation or migration, use
   [templates/deprecation-migration-plan.md](templates/deprecation-migration-plan.md)
   and [references/evolution-and-deprecation.md](references/evolution-and-deprecation.md).
   Review the contract using [templates/contract-review.md](templates/contract-review.md).
   Test provider conformance, consumer expectations, compatibility diffs, examples,
   negative cases, and the deployed boundary. Load
   [release-engineering](../release-engineering/SKILL.md) for release sequencing,
   artifact promotion, progressive exposure, and coordinated rollback after the
   compatibility policy is defined.

## Reference Guide

| Load when | File |
|---|---|
| Assessing an API portfolio, ownership, duplication, discoverability, lifecycle, standards, or retirement | [references/api-landscape-and-governance.md](references/api-landscape-and-governance.md) and [templates/api-landscape-assessment.md](templates/api-landscape-assessment.md) |
| Comparing gateways, ingress proxies, service meshes, traffic direction, routing, policy, telemetry, or failure boundaries | [references/api-infrastructure-topologies.md](references/api-infrastructure-topologies.md) |
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

## Ownership Boundaries

- **Product owners** decide consumer outcomes, audience, value, and lifecycle intent;
  this skill turns those decisions into interface agreements and evidence.
- **Platform owners** decide gateway, ingress, mesh, networking, deployment, and
  runtime operations. This skill identifies topology responsibilities and contract
  consequences but does not operate the substrate.
- **Security owners** decide threat models, credential and secret controls, abuse
  resistance, and tenant isolation. This skill records the contract handoff and
  required authorization behavior without substituting for the assessment.
- **Architecture owners** decide cross-system principles, significant boundaries,
  and durable architecture decisions. Use [adr-authoring](../adr-authoring/SKILL.md)
  when a landscape or topology decision has consequences beyond the API portfolio.

An API landscape assessment is not a product roadmap, platform runbook, security
review, or enterprise architecture repository. Escalate unresolved ownership,
authority, or retirement decisions instead of assigning them implicitly.

## Completion

Stop when the selected interface has an owner, an authoritative contract, explicit
consumer and failure assumptions, a compatibility assessment for each change, and
evidence or an explicit gap for each required review item. Escalate unresolved domain
semantics, authority, delivery, or consumer-impact questions to their accountable
owner.
