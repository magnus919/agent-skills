---
title: "Reliability Design Review: [System or Change]"
doc_id: RDR-[SERVICE]-[VERSION]
status: draft | reviewed | approved | rejected
created: [YYYY-MM-DD]
owner: "[Name / Team]"
reviewers: "[Names / Teams]"
---

# Reliability Design Review — [System or Change]

## Decision

- **Decision:** [approve / approve with conditions / defer / reject]
- **Decision owner:** [Name / role]
- **Review date:** [YYYY-MM-DD]
- **Next review trigger:** [date, SLO breach, traffic threshold, architecture change]

## 1. User and business context

- **Critical user journeys:** [What users need to accomplish]
- **User impact if this fails:** [availability, latency, correctness, freshness, privacy, data loss]
- **Existing or proposed SLOs:** [Link or concise statement]
- **Error-budget trade-off:** [What budget is consumed or protected?]

## 2. System and dependency boundaries

- **Request path:** [Describe or link diagram]
- **Async/data paths:** [Queues, pipelines, batch jobs, replay]
- **Dependencies:** [Service, owner, failure mode, fallback]
- **Shared resources:** [Databases, quotas, clusters, control planes]
- **Failure domains:** [What can fail together?]

## 3. Concrete assumptions

| Dimension | Normal | Expected peak | Worst credible case | Evidence / owner |
|---|---:|---:|---:|---|
| Requests or events per second | [ ] | [ ] | [ ] | [ ] |
| Payload or storage growth | [ ] | [ ] | [ ] | [ ] |
| Latency budget | [ ] | [ ] | [ ] | [ ] |
| Concurrent work / queue depth | [ ] | [ ] | [ ] | [ ] |
| Recovery point / recovery time | [ ] | [ ] | [ ] | [ ] |

## 4. Failure and degraded modes

| Failure or saturation condition | User-visible effect | Detection | Mitigation / shed / defer | Recovery verification | Owner |
|---|---|---|---|---|---|
| [ ] | [ ] | [ ] | [ ] | [ ] | [ ] |

Include retry amplification, timeout behavior, dependency failure, quota exhaustion, bad configuration, partial rollout, data corruption, and loss of observability where relevant.

## 5. Change and rollout safety

- **Change units:** [small, reversible steps]
- **Canary population and control:** [ ]
- **Observation window and sample size:** [ ]
- **Success metrics:** [SLO, user journey, saturation, dependency]
- **Abort thresholds and authority:** [ ]
- **Rollback or roll-forward:** [ ]
- **Configuration validation and audit path:** [ ]

## 6. Data, privacy, and security reliability

- **Correctness and completeness checks:** [ ]
- **Durability, backup, restore, and replay evidence:** [ ]
- **Privacy or security failure modes:** [ ]
- **Access and break-glass controls:** [ ]

## 7. Operations and human work

- **Dashboards and alerts:** [Links; each page has an action]
- **Runbook:** [Link]
- **On-call readiness:** [Access, training, escalation, handoff]
- **Expected toil:** [Estimate and reduction plan]
- **Cognitive-load risks:** [Ambiguous signals, hidden state, complex procedures]

## 8. Verification plan

- [ ] Unit and integration behavior verified
- [ ] Load or capacity assumptions tested
- [ ] Failure and degraded modes exercised
- [ ] Canary and rollback exercised
- [ ] Restore or replay verified where applicable
- [ ] User-visible SLO and telemetry verified in the live boundary

## 9. Open risks and conditions

| Risk / unknown | Evidence needed | Owner | Due / trigger | Decision if unresolved |
|---|---|---|---|---|
| [ ] | [ ] | [ ] | [ ] | [ ] |

## 10. Approval record

- **Service owner:** [Name / date]
- **Reliability reviewer:** [Name / date]
- **Security / privacy reviewer (if applicable):** [Name / date]
- **Product or business owner:** [Name / date]
