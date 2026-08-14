# Operational Handoff Record

The operational handoff record is the durable artifact that transfers a production
change from the launch decision to the team that will own it in production. It is
the final output of the production-excellence gate model
([gates.md](gates.md)) and the production evidence packet
([evidence-packet.md](evidence-packet.md)).

## Handoff fields

### Service and change identification

| Field | Description |
|---|---|
| **Service name** | The service or system being launched or changed |
| **Change identifier** | Issue, ticket, or change-request ID |
| **Change description** | One-paragraph summary of what changed and why |
| **Risk class** | Low / Standard / High |
| **Service owner** | Named individual accountable for the service in production |
| **Launch coordinator** | Named individual who ran the readiness review and gate model |

### Gate outcome

| Field | Description |
|---|---|
| **Outcome** | Go / No-go / Defer / Exception / Escalation |
| **Outcome date** | Date the gate decision was reached |
| **Outcome authority** | Who approved the outcome (service owner, exception authority, escalation body) |
| **Conditions** | Any conditions attached to the outcome (deferral triggers, exception expiration, post-launch requirements) |

### Evidence summary

| Field | Description |
|---|---|
| **Readiness** | Risk class, accountable owner, decision summary — reference to readiness record |
| **Migration** | Migration type, recovery path, verification — reference to migration plan (or "none") |
| **Resilience** | Failure modes assessed, RTO/RPO, last exercise date — reference to recovery evidence |
| **Capacity/cost** | Demand model summary, budget constraint, SLO interaction — reference to capacity model |
| **Incident learning** | Relevant prior incidents, follow-up status — reference to incident records |
| **Security** | Review status, trust-boundary assessment — reference to security review (or "not applicable") |
| **Release** | Release plan summary — reference to release plan |
| **Platform** | Service-catalog entry, paved-road status — reference to platform entry |
| **Data** | Data-path assessment — reference to data-quality evidence |
| **QA** | Verification summary, boundary exercised — reference to QA evidence |

### Gap register (for any missing evidence)

| Field | Description |
|---|---|
| **Domain** | Which evidence domain has a gap |
| **Gap description** | What evidence is missing |
| **Owner** | Who is accountable for closing the gap |
| **Due date** | When the gap must be closed |
| **Risk of non-closure** | What happens if the gap is not closed by the due date |

### Post-launch learning path

| Field | Description |
|---|---|
| **Incident-learning route** | Whether launch outcomes and any post-launch incidents should feed [incident-learning](../../incident-learning/SKILL.md) |
| **Lifecycle-learning route** | Whether launch outcomes should feed [product-lifecycle-learning](../../product-lifecycle-learning/SKILL.md) for expected-vs-observed comparison |
| **Review cadence** | When the service owner should revisit the handoff record (e.g., 7 days post-launch, 30 days post-launch) |
| **Escalation path** | Who to contact if post-launch issues exceed the service owner's authority |

### Sign-off

| Field | Description |
|---|---|
| **Service owner signature** | Name and date |
| **Launch coordinator signature** | Name and date |
| **Exception authority signature** | Name and date (only for Exception outcomes) |
| **Escalation body acknowledgement** | Name and date (only for Escalation outcomes) |

## Post-launch learning: routing launch outcomes

After launch, the handoff record feeds two learning paths:

### Incident-learning route

Post-launch incidents (degraded SLOs, unexpected failures, dependency outages,
capacity breaches) are routed to [incident-learning](../../incident-learning/SKILL.md)
with a reference to this handoff record. The incident-learning skill's verified-closure
requirement ensures that follow-up items traced to launch decisions are tracked to
completion.

For a **Go** outcome: incidents are unexpected and trigger the standard
incident-learning flow.

For an **Exception** outcome: incidents related to the waived domain are
expected to be elevated; the exception's post-launch condition defines the
threshold for re-escalation.

### Lifecycle-learning route

The expected outcomes recorded in the handoff (SLO targets, capacity assumptions,
cost projections, migration-success criteria) are routed to
[product-lifecycle-learning](../../product-lifecycle-learning/SKILL.md) for
expected-vs-observed comparison at the review cadence. The lifecycle-learning
skill's continue/improve/harvest/pivot/pause/retire decisions are informed by
the gap between what the handoff predicted and what production observed.

## Handoff for non-Go outcomes

The handoff record is populated even when the outcome is not Go:

- **No-go**: the handoff records the blocking gap and routes it to the gap owner.
  The record is retained as evidence of the decision and its rationale.
- **Defer**: the handoff records the deferral condition and the re-evaluation
  trigger. At the trigger date, the service owner re-opens the gate model with
  updated evidence.
- **Exception**: the handoff records the waiver and its post-launch condition.
  The exception authority is named; the condition is tracked.
- **Escalation**: the handoff records the escalation target and the specific
  conflict. The escalation body's decision (when reached) is recorded in a
  follow-up handoff.
