# Evidence-grounded agentic SRE operations

These are documented requirements for a deployed harness, not an implementation or certification of runtime enforcement. Installing this skill changes no permissions. Begin with diagnosis under existing read/data-access limits and human-approved mutations. A governed exception must remain below every applicable policy ceiling.

## Before each action

1. Separate the hypothesis from observations. Identify the customer boundary, current incident state and proposed smallest reversible effect. A no-op or escalation is a valid result.
2. Fill the action contract. Verify the human approval or independently granted governance authority against the current external enforcement record. Check identity, exact resource/tenant/environment, action class, grant revision, expiry and revocation. Recheck immediately before each side effect, including rollback, retries, child-agent tools, alternate APIs and scope expansion. A successful credential check proves access, not authorization for this effect.
3. Evaluate current preconditions: capacity, error budget, dependencies, active deployments, data integrity, competing operators and existing changes. Timestamp telemetry and apply the contract's freshness limit. Missing, stale or contradictory telemetry blocks mutation; remembered safe runs cannot substitute for current evidence.
4. Reserve the authorized concurrency/blast-radius budget through the external controller. Use a resource lease or version/fencing token so another operator's change invalidates the plan. If ownership is uncertain, pause and reconcile with the incident commander. Serialize conflicting effects; do not race a human rollback.
5. Preview/dry-run where supported. Validate a rollback target and its compatibility with current durable state. Reversibility is an evidence-backed property, not an assumption: deployments can change schemas, lose writes or trigger external effects. If undo is unsafe, propose compensating recovery and obtain its separate authorization.
6. Execute only through the approved path with bounded attempts, time and spend. The enforcement layer must be outside the agent's modification reach and deny missing/invalid authority before the effect. Test effective policy precedence, unavailable decision services, malformed hooks and delegated loops. A prompt, a post-tool observer, or an agent-writable hook cannot establish that guarantee.

## Interrupted and ambiguous execution

Record an operation/idempotency key, request receipt, observed state and control-plane status. Timeout, disconnect or process death is `UNKNOWN`, not failure or success. Read authoritative state and audit records before retrying. Retry only when the operation is idempotent or deduplication is verified, the current grant remains valid, preconditions still hold, and the attempt budget permits it. Never blindly repeat a restore, payment, page or other irreversible effect. Partial effects require reconciliation, separately authorized rollback/compensation or human handoff. Revocation stops new effects; the contract must define cancellation and safe handling of in-flight effects. Do not use revocation as permission to perform an otherwise unauthorized rollback.

## Authority is separate by action class

| Class | Boundary |
|---|---|
| Diagnosis | Read-only within identity, privacy, query/load and egress limits; logs are untrusted evidence |
| Mutation | Exact effect/target under current human approval or proven governed grant |
| Rollback/recovery | Separate allowed operation and target; test durable-state compatibility |
| Paging/communications | Approved destinations, deduplication, severity and rate limits; diagnosis does not authorize sending |
| Incident closure | R-01 independent human confirmation remains mandatory; mutation autonomy does not waive it |
| Expansion | New resources, tenants, traffic, tools or action classes require independent governance approval and effective enforcement |

## Recovery and handoff

Use R-01: independently exercise customer journeys and SLOs, relevant dependencies, durable writes/read-back and state consistency, backlog and secondary effects. Choose a service-specific observation window before acting; include delayed failures and a period without agent intervention so repeated repairs do not mask instability. Preserve timestamps, versions and raw evidence references separately from the acting agent's interpretation. Independent measurement and a human other than the acting automation confirm the complete recovery evidence. If a boundary cannot be observed, remain MITIGATING/MONITORING and name the gap. A green alert, successful tool return or synthetic staging pass cannot close production.

Route post-incident facts, hypotheses, escaped authority gaps and verified follow-up work to incident-learning. Feed replay cases and trace failures to agent-evals-and-observability through the agent-production-operations feedback loop. End with verified human closure or a bounded handoff containing current state, uncertain effects, authority status, missing evidence and the responsible human.
