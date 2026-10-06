# Agentic SRE action contract

A proposal/evidence record, never a permission grant. Confirm target, scope and rollback path before acting. Default: current independently attributable human approval for each production mutation; a governed exception requires proven external enforcement and compatible policies.

| Field | Required record |
|---|---|
| Identity and change | Incident/change ID; agent/model/prompt/tool versions; human owner |
| Effect | Diagnosis / mutation / rollback / paging / closure / expansion; exact command/API and expected effect |
| Scope | Environment, tenant, resource IDs, population, excluded targets, maximum blast radius |
| Authority | Human approval reference OR independent governance grant ID/revision, approver, allowed class and level; external verification receipt |
| Policy | Applicable host/organization/action ceilings and effective precedence; prohibited effects |
| Validity | Grant start/expiry, revocation source, check timestamp, recheck-before-effect mechanism |
| Preconditions | Expected resource version, capacity, dependencies, error budget, deployments and data/state conditions |
| Evidence | Timestamped sources, freshness limits, missing/stale/conflicting-data stop behavior |
| Concurrency | External lease/fencing token, competing operator coordination, resource and fleet action budgets |
| Execution | Dry-run result, operation/idempotency key, attempt/time/cost limits, journal/receipt source |
| Ambiguity | UNKNOWN-state reconciliation query, deduplication proof, retry conditions, partial-effect handoff |
| Abort/recovery | Success and abort criteria, stopping owner, separately authorized rollback target/procedure, durable-state compatibility or compensation |
| Revocation | How new/in-flight effects stop safely; when human handoff is required |
| Verification | Independent customer journey/SLO, dependency and durable-state checks; backlog/secondary effects; agent-free observation window |
| Closure | R-01 evidence references and independent human confirmation; missing evidence leaves MITIGATING/MONITORING |

After execution append actual effects, receipts, timestamps, deviations and uncertainties separately from the proposed plan. A completed template or planned check is not execution evidence.
