# API Landscape And Governance

Use this reference when a team needs to understand or steer a collection of APIs,
not only design one contract. The output is a decision-ready landscape record with
evidence, owners, exceptions, and follow-up work. It is not a universal maturity
ladder: capability and risk vary by audience, domain, and change pressure.

## Build The Inventory

Start from published contracts, runtime routes, repositories, gateways, event
catalogs, client registries, and deployment records. Reconcile them rather than
treating any one source as complete. For each surface capture:

- business capability and domain authority;
- interface style, audience, exposure, contract location, and lifecycle state;
- owning team, accountable product owner, technical contact, and support path;
- consumers, critical workflows, data classification, and dependency direction;
- deployment and topology references, traffic evidence, quotas, and incident history;
- last meaningful change, successor or replacement, and confidence in each fact.

Mark unknowns and stale records explicitly. An inventory that hides uncertainty gives
false confidence and makes retirement unsafe.

## Find Ownership And Duplication

Map each domain concept to its authoritative owner, then compare interfaces by
consumer job and semantic responsibility, not by similar URL names. Investigate
duplicates, wrappers, forks, shadow APIs, version drift, and multiple schemas for the
same fact. A surface may be intentionally distinct when its audience, authority,
latency, sensitivity, or failure contract differs. Record the reason; do not merge
interfaces merely to reduce a count.

Assign one accountable owner for contract meaning and lifecycle. Supporting teams may
own implementation, gateway configuration, SDKs, or documentation, but those roles
must not silently replace the authority owner.

## Improve Discoverability

Make the path from a consumer job to a trustworthy interface short. Publish the
contract, audience, owner, domain vocabulary, examples, authentication handoff,
limits, support path, lifecycle state, and known compatibility posture in a searchable
catalog. Link generated artifacts to their source contract and distinguish experimental,
internal, partner, and public surfaces. Measure failed searches, stale entries,
unowned surfaces, and support questions as feedback, not as a reason to mandate one
catalog product.

## Govern The Lifecycle

Treat an API as a product-shaped capability with an accountable problem and consumer
feedback loop:

1. **Propose:** identify the consumer job, domain owner, audience, alternatives, and
   expected operational consequences.
2. **Shape:** define the contract and topology handoffs; check for duplication and
   reuse without forcing incompatible consumers onto one surface.
3. **Operate:** collect consumer, reliability, latency, error, adoption, and support
   evidence with signal definitions appropriate to the interface.
4. **Improve:** prioritize changes by consumer harm, domain value, and reversibility.
5. **Deprecate:** name a successor, affected consumers, migration support, telemetry,
   communication, pause conditions, and evidence-based sunset criteria.
6. **Retire:** remove only after the owner verifies criteria, residual routes and
   consumers are understood, and an operational recovery or communication path exists.

Retirement is a decision, not a deletion task. Keep a record of why the surface was
retired, what replaced it, and what evidence would reveal an overlooked dependency.
Reuse the contract-level [deprecation and migration plan](../templates/deprecation-migration-plan.md)
for consumer-specific execution.

## Make Standards Proportional

Set a small baseline for every surface, then add controls where exposure, blast radius,
data sensitivity, consumer diversity, irreversibility, or regulatory obligations justify
them. A proportional policy can vary review depth, contract verification, observability,
support, rollout evidence, and retirement controls by risk class. Keep exceptions
visible with an owner, rationale, expiry or review condition, and compensating evidence.

Avoid universal thresholds for adoption, latency, review time, version count, or
retirement windows. Standards are useful when they reduce recurring ambiguity; they are
harmful when compliance artifacts replace consumer outcomes and operational evidence.

## Ownership Handoffs

- Product owns the consumer problem, audience, value, and lifecycle intent.
- API owners own domain meaning, contract authority, consumer compatibility, and
  interface lifecycle evidence.
- Platform owns the gateway, ingress, mesh, networking, deployment, and runtime
  controls described in the topology handoff.
- Security owns threat modeling, credential lifecycle, abuse controls, and isolation.
- Architecture owners arbitrate cross-domain principles and durable decisions when the
  blast radius exceeds the API portfolio.

## Landscape Exit Check

Stop when every material surface has an owner and lifecycle state, duplicate or
intentional overlap has a recorded rationale, discovery gaps are visible, standards
are tied to risk, retirement candidates have evidence and a recovery/communication
path, and unresolved decisions are assigned to the accountable owner.
