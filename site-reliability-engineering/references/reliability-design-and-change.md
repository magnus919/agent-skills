# Reliability Design, Change Safety, and Overload

Use this reference for design reviews, capacity and overload planning, production configuration, canary releases, data pipelines, and services whose reliability depends on more than availability alone.

## Source anchors

This reference synthesizes *The Site Reliability Workbook*, “Managing Load,” “Introducing Non-Abstract Large System Design,” “Data Processing Pipelines,” “Configuration Design and Best Practices,” “Configuration Specifics,” “Canarying Releases,” and “Identifying and Recovering from Overload,” plus *Seeking SRE*, “In the Beginning, There Was Chaos,” “Database Reliability Engineering,” “Engineering for Data Durability,” “Immutable Infrastructure and SRE,” “Scriptable Load Balancers,” and “The Service Mesh: Wrangler of Your Microservices?” The source books contain organization-specific examples; the procedures below generalize the engineering decisions without copying those examples.

## Design for the whole system

A reliability design review must include the user journey, not just the service under review. For each proposed system:

1. State the user-visible objectives and the SLOs they imply.
2. Draw the request and data paths, including asynchronous work and third parties.
3. Identify capacity limits, queues, retries, timeouts, rate limits, and shared resources.
4. Describe normal, degraded, overloaded, and recovery states.
5. Define what can be shed, delayed, cached, degraded, or served read-only.
6. Identify data-loss, corruption, privacy, and security consequences separately from downtime.
7. Specify observability, operator actions, rollback, restore, and verification.
8. Estimate operational work and cognitive load before approving the design.

A design that meets an availability target by silently corrupting data or violating privacy is not reliable.

## Non-Abstract Large System Design (NALSD-style review)

Use concrete boundaries and numbers rather than “high scale” or “resilient.” Record:

- expected request, event, and data rates, including peak and burst shape;
- storage growth, retention, replication, and recovery-point objectives;
- latency budgets across each dependency hop;
- failure domains and blast radius;
- consistency, ordering, idempotency, and replay behavior;
- quotas, backpressure, retry limits, and queue bounds;
- deployment and migration strategy;
- cost and operational ownership.

Iterate the design against the SLO and error budget. If a proposed feature consumes more reliability, capacity, or operator attention than the budget allows, record the trade-off and decision owner instead of hiding it in implementation detail.

## Load and overload management

Capacity planning is not only “add more machines.” Build a demand model from historical traffic, expected growth, scheduled events, and worst credible bursts. Test the model before the event and identify the manual fallback if automation fails.

When overload begins:

1. Confirm whether demand, capacity, dependency latency, or a control-plane failure is the limiting factor.
2. Stop amplification: bound retries, disable nonessential fan-out, and prevent queue growth from becoming unbounded.
3. Protect the critical user journey with admission control, prioritization, rate limits, caching, or graceful degradation.
4. Shed or defer work deliberately. Prefer a known reduced mode over random timeouts.
5. Watch saturation, queue depth, latency, errors, and dependency health for recovery evidence.
6. Restore normal traffic gradually and verify that backlog, data integrity, and downstream systems recover.
7. Record the capacity assumption that failed and create an owned repair.

A service that responds slowly under overload can consume more shared capacity through timeouts and retries, creating a cascade. Fast rejection with a clear degraded path can be more reliable than accepting work that cannot complete.

## Operational overload of the team

A team is operationally overloaded when urgent work continually preempts the engineering needed to reduce future load. Track operational work as a proportion of available engineering time, including pages, tickets, manual changes, support interruptions, and incident follow-up.

Recovery requires an explicit cutover:

- declare the team overloaded using a stated threshold or sustained trend;
- protect a fixed block of engineering time;
- reduce or renegotiate service scope and nonessential commitments;
- suppress, route, or retire non-actionable alerts;
- prioritize the smallest changes that remove recurring interruption;
- assign leadership support for deferred product work and staffing gaps;
- review the load trend weekly until the team returns below the threshold.

Do not respond to operational overload by asking the team to work longer hours. That hides the capacity failure and increases incident risk.

## Configuration safety

Treat configuration as production code with an explicit lifecycle:

- one authoritative source and a discoverable ownership path;
- schema, type, range, dependency, and compatibility validation;
- safe defaults and explicit units;
- version control, review, audit trail, and rollback;
- staged rollout or canary for high-impact changes;
- dry-run or preview where possible;
- clear distinction between static configuration and runtime state;
- emergency path that is fast but still logged and reconciled into source control.

Configuration should be easy to inspect during an incident. Avoid hidden inheritance, ambiguous names, duplicated values, unbounded lists, and emergency-only interfaces. A configuration change needs a stated expected effect and a way to observe whether that effect occurred.

## Canarying changes

A canary is a partial, time-limited deployment evaluated against a control. It is not merely “deploy to one host.” Define before rollout:

- canary population and selection method;
- control population and whether traffic is comparable;
- observation window and minimum sample size;
- success metrics tied to SLOs, user journeys, saturation, and dependency health;
- abort thresholds and who or what can stop the rollout;
- rollback or roll-forward action;
- criteria for expanding, pausing, or declaring success.

Compare canary and control, and account for traffic mix, time-of-day, cold starts, and unrelated changes. A canary with no control, no minimum sample, or no abort authority creates the appearance of safety without the decision evidence.

## Data processing and durability

For pipelines and data stores, define reliability beyond service uptime:

- freshness and completeness of output;
- correctness and reconciliation checks;
- ordering, duplication, replay, and late-arriving data behavior;
- checkpointing, retention, backfill, and recovery-point objectives;
- schema evolution and compatibility;
- access control and privacy boundaries;
- restore tests and corruption detection.

Availability and durability are different SLO dimensions. A pipeline can be “up” while producing stale, incomplete, duplicated, or wrong data. A database can answer requests while losing writes. Measure the property users and downstream decisions depend on.

## Third-party dependencies

Apply SRE discipline to vendors and managed services:

1. Classify the dependency by user impact, substitutability, and failure mode.
2. Record the dependency's SLO or service limits, support path, status signal, and contractual boundaries.
3. Measure the dependency from your service's perspective, not only from the vendor dashboard.
4. Design timeout, retry, fallback, queue, cache, and degraded-mode behavior.
5. Test provider failure and credential, quota, region, and API-version failure modes.
6. Track unresolved vendor repairs and review whether the dependency remains acceptable.

“External” is not the same as “unowned.” If a dependency failure is excluded from your SLO, document what users experience and what mitigation you actually provide.

## Complexity and service mesh caution

Prefer the simplest architecture that meets the objectives. Every proxy, control plane, configuration layer, retry policy, and telemetry path adds failure modes and cognitive load. Adopt a service mesh or similar platform only when the operational capability it provides outweighs its new blast radius and the team can observe and operate it.

## Agent procedure

Use this reference with `slo-sli-framework.md`, `monitoring-alerting.md`, `release-engineering.md`, and `troubleshooting.md`. Use the `templates/reliability-design-review.md` template. Reject vague claims such as “handles scale” or “has rollback” until the owner, evidence, thresholds, and verification path are explicit.
