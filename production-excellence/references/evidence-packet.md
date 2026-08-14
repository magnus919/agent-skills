# Production Evidence Packet

The production evidence packet assembles cross-domain evidence into a single
decision-ready record. It is the shared input to the gate model
([gates.md](gates.md)) and feeds the operational handoff record
([handoff-record.md](handoff-record.md)).

## Applicability

This packet is used for **both**:

- **New services** — a service that has never been in production. Every evidence
  domain is assessed; domains that are not applicable are explicitly marked as such
  with a reason (not silently omitted).
- **Changes to existing systems** — a feature, migration, or configuration change
  to a service already in production. Only the domains affected by the change are
  assessed; unaffected domains are marked "no change" with a reference to the
  existing evidence.

## Evidence domains

### 1. Readiness

| Field | Requirement |
|---|---|
| **Risk class** | Low / Standard / High per [production-readiness](../../production-readiness/SKILL.md) |
| **Evidence source** | Readiness record or explicit gap statement |
| **Owner** | Named accountable owner for the readiness assessment |
| **Decision** | Go / No-go / Defer / Exception from the readiness review |

For a **change to an existing system**, cite the delta: what changed since the
last readiness review.

### 2. Migration

| Field | Requirement |
|---|---|
| **Migration type** | Schema / data / API / infrastructure / service (or "none") |
| **Evidence source** | Migration plan per [migration-engineering](../../migration-engineering/SKILL.md) |
| **Recovery path** | Rollback / roll-forward / restore / irreversible (explicit) |
| **Verification** | How migration correctness was verified (reconciliation, checksum, smoke) |

For a **new service**, migrations may not apply; state "no migration — new service."

### 3. Resilience and recovery

| Field | Requirement |
|---|---|
| **Failure modes assessed** | Dependency outage, data corruption, zone/region loss, overload |
| **Evidence source** | Recovery exercise results per [resilience-and-recovery](../../resilience-and-recovery/SKILL.md) |
| **RTO/RPO** | Stated targets (context-dependent, not universal) |
| **Degradation behavior** | What degrades and how (graceful degradation, not binary up/down) |
| **Recovery verified** | Date of last restore test, game-day, or failover exercise |

For a **change to an existing system**, state whether the change introduces new
failure modes or alters existing ones.

### 4. Capacity and cost

| Field | Requirement |
|---|---|
| **Demand model** | Expected load, peak, growth rate |
| **Capacity model** | Scaling limits, quotas, rate limits |
| **Cost model** | Unit cost, budget constraint, cost attribution |
| **SLO interaction** | Any cost/SLO tradeoff decisions per [capacity-and-cost-engineering](../../capacity-and-cost-engineering/SKILL.md) |
| **Assumptions** | Explicit: all demand/capacity/cost assumptions stated |

### 5. Incident learning

| Field | Requirement |
|---|---|
| **Pre-existing incidents** | Any incidents from this service or its dependencies relevant to this change |
| **Evidence source** | Incident records per [incident-learning](../../incident-learning/SKILL.md) |
| **Follow-up status** | Verified closure of prior incident follow-up items relevant to this change |
| **New risk register** | Risks identified during readiness that should feed incident-learning post-launch |

For a **new service**, pre-existing incidents may not apply; state "no prior
incidents — new service." The new-risk register is always populated.

## Cross-domain entry evidence

Before a production decision can be made, the following must exist as **entry
evidence** (the bundle does not gather it; it requires it):

| Evidence | Owned by | Required for |
|---|---|---|
| Readiness record with risk class and accountable owner | [production-readiness](../../production-readiness/SKILL.md) | All launches |
| Migration plan (when a migration is in scope) | [migration-engineering](../../migration-engineering/SKILL.md) | Migrations |
| Recovery exercise evidence (game-day, restore test) | [resilience-and-recovery](../../resilience-and-recovery/SKILL.md) | High-risk launches |
| Capacity and cost model with explicit assumptions | [capacity-and-cost-engineering](../../capacity-and-cost-engineering/SKILL.md) | SLO-bearing services |
| Incident-learning record for relevant prior incidents | [incident-learning](../../incident-learning/SKILL.md) | Changes to services with incident history |
| Security review evidence | [secure-software-engineering](../../secure-software-engineering/SKILL.md) | Trust-boundary changes |
| Release plan | [release-engineering](../../release-engineering/SKILL.md) | All launches |
| SLO / error-budget status | [site-reliability-engineering](../../site-reliability-engineering/SKILL.md) | SLO-bearing services |
| Platform/service-catalog entry | [platform-engineering](../../platform-engineering/SKILL.md) | New services |
| Data quality / pipeline evidence | [data-engineering](../../data-engineering/SKILL.md) | Data-path changes |
| QA verification evidence | [qa-methodology](../../qa-methodology/SKILL.md) | All launches |

## Missing-evidence handling

Any evidence domain without a named source is recorded as an **explicit gap**:

- The gap is named (e.g., "no restore test performed").
- An owner is assigned.
- A due date or condition is stated (e.g., "before next launch," "within 7 days post-launch").
- The gap feeds the gate model: missing evidence in a required domain may produce
  a no-go, defer, or exception outcome, depending on risk class and domain.

A gap is never silently omitted. Every domain in the packet is either sourced or
gapped.
