# Multi-Tenant Isolation

Security owns the threat model and enforceable controls for tenant boundaries. The
end-to-end SaaS architecture, commercial tiers, placement strategy, and lifecycle
authority belong to [multi-tenant-saas-architecture](../../multi-tenant-saas-architecture/SKILL.md).

## Make The Decision Now

State the isolation promise per tenant tier and resource. For compute, storage,
keys, queues, caches, search, logs, backups, exports, support paths, and recovery,
record whether tenants share a pooled boundary, use a bridge boundary with a
dedicated sensitive component, or receive a silo boundary. A tier name is not a
control: identify the mechanism, the failure it prevents, and the evidence that
supports the promise. Route demand distributions, quota sizing, fairness targets,
and unit-cost evidence to
[capacity-and-cost-engineering](../../capacity-and-cost-engineering/SKILL.md).

## Model The Two Planes

Treat the control plane and application plane as distinct trust boundaries even if
they run in one deployment. The control plane may decide tenant identity,
placement, entitlements, support grants, provisioning, suspension, export, and
deletion; it must not become an unrestricted reader of application data by default.
The application plane serves tenant work and must consume authenticated,
versioned policy state without treating a client claim as authority.

For every crossing, document the actor and authority, credential audience, tenant
and user context, policy version, freshness rule, failure behavior, idempotency
key, and audit event. A stale or unavailable control-plane decision must fail in a
defined safe mode, not silently widen access. Provisioning and deprovisioning
commands need authenticated origin, replay protection, duplicate handling, and
reconciliation evidence. Platform implementation of network, workload, secret,
logging, and backup substrate belongs to
[platform-engineering](../../platform-engineering/SKILL.md).

## Propagate Identity Without Trusting Labels

Derive tenant context from a verified user or workload identity and an authoritative
membership/placement lookup. Bind it to the request, transaction, job, trace,
export, and downstream call using a server-controlled context. Reject missing,
stale, mismatched, or audience-confused context. A tenant ID in a header, URL,
queue payload, callback, cache key, or JWT custom claim is an input to validate,
not proof of authority.

At each hop preserve the subject, tenant, actor type, delegated purpose, resource
scope, and correlation identifier. Downstream services and workers must authorize
again within their own authority; gateway authentication or an upstream predicate
is not sufficient. API and event contract details belong to
[api-design-and-evolution](../../api-design-and-evolution/SKILL.md), while service
middleware, data access, jobs, and integration tests belong to
[backend-engineering](../../backend-engineering/SKILL.md).

## Protect Privileged Support Paths

Support access and impersonation are separate administrative capabilities, not a
special case that bypasses tenant authorization. Require a named operator, an
approved purpose, target tenant and resource scope, time limit, ticket or case
reference where policy requires it, and a visible session indicator. Prefer
read-only or customer-approved actions; require step-up approval for writes,
exports, key access, deletion, or cross-tenant investigation. Prevent chaining
impersonation into broader operator privileges, and make break-glass access
expire automatically.

Record who initiated, who was impersonated, why, what policy allowed it, which
objects were touched, what changed, and when the grant expired. Test direct API,
bulk, background, and support-tool paths with expired, revoked, wrong-tenant, and
cross-tenant grants. Audit-event design and sensitive-field minimization belong
to the logging owner; the security requirement is that the action be attributable
and reviewable.

## Apply Controls To Every Tenant-Bearing Resource

- **Data and keys:** Scope queries and object stores by server-derived tenant
  context. Use separate accounts, databases, schemas, namespaces, predicates,
  RLS, workload boundaries, or key hierarchies as the promise requires. Per-tenant
  keys can reduce blast radius but do not replace authorization; define key access,
  rotation, disablement, recovery, and destruction evidence.
- **Caches, search, and queues:** Include an authoritative tenant and resource
  scope in cache identity and invalidation. Filter search at query authorization
  and index/write boundaries. Bind queue messages, worker credentials, callbacks,
  retries, dead letters, and replay tools to tenant scope. Never let a shared
  worker select a tenant solely from message data.
- **Logs and traces:** Keep tenant context for investigation without copying
  customer payloads into shared telemetry. Separate audit access from ordinary
  operators, restrict query scope, redact secrets and sensitive content, and
  define retention and deletion behavior. A trace ID is correlation, not an
  authorization token.
- **Backups, restore, export, and deletion:** Define whether backup snapshots
  are pooled, bridge, or siloed and who may restore them. Restore into a bounded
  quarantine before serving data; verify tenant identity, key availability,
  authorization, and integrity. Exports must be tenant-scoped, purpose-bound,
  time-limited, encrypted, and independently authorized. Deletion must cover
  primaries, replicas, indexes, caches, queues, logs, derived data, exports, and
  backups according to the adopted retention policy, with completion and gap
  evidence. Route lifecycle and privacy acceptance artifacts to
  [privacy-engineering](../../privacy-engineering/SKILL.md).
- **Resource controls:** Give each tenant and tier explicit concurrency, storage,
  request, queue, search, export, and job limits where exhaustion can cross a
  boundary. Protect shared pools with admission control, bounded work, fair
  scheduling, backpressure, and reserved capacity where justified. A quota is
  not a capacity model; route sizing, load/soak evidence, hot-tenant analysis,
  and cost tradeoffs to [capacity-and-cost-engineering](../../capacity-and-cost-engineering/SKILL.md).

## Threat Cases

Threat-model at least these abuse paths and add design-specific variants:

| Case | Security question | Evidence to seek |
|---|---|---|
| Control-plane compromise or confused deputy | Can a provisioning, support, entitlement, or restore capability read or alter application data beyond its purpose? | Separate credentials and policy tests for each plane and privileged command. |
| Context substitution | Can a caller replace tenant context between authentication, lookup, queueing, storage, or downstream calls? | Direct, asynchronous, retry, and callback tests with mismatched context. |
| Support impersonation abuse | Can an operator hide, prolong, chain, or broaden an impersonation session? | Approval, expiry, scope, audit, revocation, and break-glass tests. |
| Shared-resource bleed | Can cache reuse, search ranking, logs, backups, exports, or dead letters reveal another tenant? | Distinct sentinel data and negative tests at every resource boundary. |
| Noisy neighbor or exhaustion | Can one tenant consume shared workers, connections, memory, queue depth, search capacity, storage, or export bandwidth and deny another? | Tenant-distributed load/soak evidence, quotas, fairness observations, and safe degradation. |
| Lifecycle race | Can a suspended, deleted, or deprovisioned tenant continue receiving jobs, tokens, exports, or restored data? | Provision/deprovision state machine tests, tombstone handling, retries, and reconciliation records. |

## Evidence And Verification

Build an authorization matrix and a resource-boundary inventory. Prove, with
distinct tenants and tiers, allowed and denied reads/writes, direct and bulk API
paths, worker retries and replays, cache hits, search results, logs, keys, backup
restore, exports, deletion, support impersonation, and resource exhaustion. Verify
that a new tenant is born with restrictive permissions, scoped credentials,
tenant-aware observability, limits, and no unintended shared data.

For deprovisioning, show the initiating authority, state transition, revocation
of sessions and jobs, blocking of new work, completion across every store, and
reconciliation of failures. Record evidence location, test environment, policy
version, owner, and residual gap. A passing database test does not prove that
cache, search, logs, backups, queues, support tools, or capacity boundaries are
safe.

## Misuse To Avoid

- Treating a pooled, bridge, or silo label as proof without naming its actual
  isolation mechanism and failure blast radius.
- Filtering tenant IDs only in the UI or trusting client headers, URL segments,
  queue fields, trace fields, or support claims.
- Treating control-plane administrator access, database privilege, or restore
  access as permission to view every tenant's application data.
- Calling a database boundary complete while cache keys, logs, search indexes,
  asynchronous workers, exports, backups, or deletion jobs remain shared.
- Calling a rate limit or quota capacity evidence without representative load,
  distribution, fairness, and degradation measurements.
- Granting an AI agent tenant-wide capability when the user needs a
  document-scoped capability; prompts and retrieval content cannot grant access.
