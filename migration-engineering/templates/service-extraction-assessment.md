# Service Extraction Assessment Template

Use this assessment after a service-extraction target has been proposed and
before sequencing the migration. It records evidence and preserves a modular
monolith as an explicit outcome. It does not replace the architecture decision
that authorizes or rejects decomposition.

## Decision frame

| Field | Value |
|---|---|
| Assessment name | |
| Decision owner | |
| Current system and modules | |
| Proposed capability | |
| Proposed target boundary | |
| Business or operational problem to solve | |
| Evidence window and sources | |
| Decision status | Extract / Keep modular monolith / More evidence required |

## Boundary evidence

| Evidence area | Observed evidence | Confidence / gap | Owner |
|---|---|---|---|
| Capability purpose and language | | | |
| Invariants and transaction scope | | | |
| Data owned and authoritative writers | | | |
| Inbound callers and consumers | | | |
| Outbound dependencies | | | |
| Static and dynamic coupling | | | |
| Change and deployment coupling | | | |
| Failure and recovery boundary | | | |
| Customer journeys and impact | | | |
| Team and operational ownership | | | |

## Coupling and data ownership

| Question | Answer / evidence |
|---|---|
| Which records and fields would the target own? | |
| Which system is authoritative before, during, and after cutover? | |
| Which writes cross the proposed boundary? | |
| Which reads require joins or synchronous calls across it? | |
| Which invariants currently rely on a local transaction? | |
| Are deletes, retries, ordering, and replay defined? | |
| Is eventual consistency acceptable? For which user-visible actions? | |
| What happens when the target is unavailable? | |
| What hidden callers, jobs, reports, or caches may bypass the intended path? | |
| What evidence would disprove the proposed boundary? | |

## Pattern selection

| Candidate pattern | Role in this transition | Why it fits / does not fit | Evidence required |
|---|---|---|---|
| Strangler routing | | | |
| Branch by abstraction | | | |
| Anti-corruption boundary | | | |
| Change-data capture (CDC) | | | |
| Parallel run | | | |

**Selected primary pattern:**

**Supporting patterns:**

**Rejected pattern and reason:**

## Coexistence and migration sequence

| Phase | Old path live? | New path live? | Read authority | Write authority | Comparison / gate | Customer impact |
|---|---|---|---|---|---|---|
| Expand | | | | | | |
| Backfill / synchronization | | | | | | |
| Shadow or parallel run | | | | | | |
| Traffic or caller shift | | | | | | |
| Ownership transfer | | | | | | |
| Deprecation | | | | | | |
| Contract / cleanup | | | | | | |

## Data movement and correctness

| Field | Decision |
|---|---|
| Backfill mode | Full / Incremental / Streaming / Not applicable |
| CDC or event source | |
| Ordering and duplicate handling | |
| Delete propagation | |
| Replay and dead-letter recovery | |
| Reconciliation dimensions | Completeness / Accuracy / Timeliness / Consistency |
| Comparison method | Dual-read / Shadow execution / Consumer test / Synthetic validation |
| Pass threshold and observation period | |
| Hard stop condition | |
| Evidence artifact and owner | |

## Reversibility and operational risk

| Step or state | Recovery classification | Trigger to stop or abort | Tested procedure / gap | RTO / RPO |
|---|---|---|---|---|
| Routing or abstraction enabled | Rollback / Roll-forward / Restore / Irreversible | | | |
| Target deployed | Rollback / Roll-forward / Restore / Irreversible | | | |
| Data synchronized | Rollback / Roll-forward / Restore / Irreversible | | | |
| Read authority shifted | Rollback / Roll-forward / Restore / Irreversible | | | |
| Write authority transferred | Rollback / Roll-forward / Restore / Irreversible | | | |
| Old data or code removed | Rollback / Roll-forward / Restore / Irreversible | | | |

| Operational risk | Likelihood / impact | Mitigation and evidence | Accountable owner |
|---|---|---|---|
| Latency or throughput regression | | | |
| Partial failure or dependency outage | | | |
| Data divergence or lost change | | | |
| Duplicate or reordered side effect | | | |
| Security or authorization drift | | | |
| Observability and support gap | | | |
| On-call and ownership load | | | |
| Customer-visible semantic change | | | |

## Reasons to keep a modular monolith

Complete this section even when extraction is recommended. Mark each reason as
observed, plausible, or not applicable, and cite evidence.

| Retention reason | Status | Evidence / counter-evidence | Modular improvement or follow-up |
|---|---|---|---|
| Shared invariants require one local transaction | | | |
| Data ownership is unclear or remains shared | | | |
| Coupling would move rather than decrease | | | |
| Consumers or operational dependencies are not observable | | | |
| Distributed latency, failure, or consistency is unacceptable | | | |
| Scale, release cadence, isolation, or team ownership does not justify a service | | | |
| No tested recovery path fits the accepted impact | | | |
| Modules, dependency rules, or internal abstractions solve the stated problem | | | |

**Decision to retain the modular monolith, if applicable:**

**Condition that would reopen extraction:**

**Reassessment owner and date:**

## Handoff and approval

| Role | Name / team | Decision or implementation responsibility |
|---|---|---|
| Architecture decision owner | | Boundary and decomposition justification |
| Migration lead | | Current-to-target transition |
| API owner | | Contract and consumer compatibility |
| Data owner | | Backfill, CDC, and reconciliation implementation |
| Platform / release owner | | Runtime, routing, flags, and promotion |
| SRE / operations owner | | SLO gates, alerts, and response readiness |
| Security owner | | Trust boundary and authorization review |

**Approval or escalation record:**
