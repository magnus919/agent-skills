# RAG design record

## Workload and decision

- Decision owner, scope, alternatives, and reason to revisit
- Representative questions, expected evidence locators, and unanswerable cases
- Chosen baseline, measured gaps, and upgrade thresholds
- Latency, cost, freshness, revocation, and retention objectives

## Evidence and flows

- Authoritative sources, versions, retrievers, evidence forms, citation locators
- Ingest, project, publish, retrieve, authorize, synthesize, and resolve citations
- Valid time and recorded time where applicable
- Series scope, grain, units, analysis cutoff, forecast horizon and calibration where applicable
- Harness intake/output schemas, runtime transitions, checkpoint policy and acceptance
- Background workers, input/output scopes, retries, publication, and rollback

## Authority and lifecycle

| Principal and tenant | Operation | Resource and version | Authority and conditions | Enforcement and stale behavior |
|---|---|---|---|---|
| | | | | |

- Policy inheritance, derived evidence, approved sharing, and external processing
- Cache keys and reauthorization, revocation, deletion, and restore
- Tenant partitioning, quotas, audit paths, and resource owners

## Acceptance

| Case, corpus/policy version, principal | Expected evidence and operation result | Metric and threshold | Owner |
|---|---|---|---|
| | | | |

- Rollout, monitoring, fallback, rollback, and unresolved decisions
