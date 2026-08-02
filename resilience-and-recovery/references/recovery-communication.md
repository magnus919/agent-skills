# Recovery Communication

## Purpose

Plan who to notify, when, and through what channels during recovery events. Communication failures during recovery compound technical failures — stakeholders make bad decisions when they lack accurate information.

## Communication plan template

### Stakeholder matrix

| Role | Who | Channel | When to notify | What to communicate |
|---|---|---|---|---|
| **Incident commander** | On-call IC or SRE lead | PagerDuty / Opsgenie / escalation policy | Immediately upon detection | Nature of failure, affected system, initial assessment |
| **System owner** | Named engineering lead for the affected system | Slack, phone | Within 5 minutes of confirmed failure | System status, expected impact, recovery in progress |
| **Engineering team** | On-call engineers for the affected system and dependencies | Slack channel, war room bridge | Within 10 minutes | Technical details, recovery procedure, assistance needed |
| **Product manager** | Named PM for the affected product | Slack, email | Within 15 minutes | User impact, expected duration, customer-facing communication plan |
| **Customer support** | Support team lead or on-call support | Slack, email | Within 15 minutes | What to tell customers, expected resolution time, escalation path |
| **Customers / users** | Status page, in-app notification, email | As defined by SLA | What is affected, what is being done, when to expect update, where to get more information |
| **Executives / leadership** | VP Engineering, CTO, or designated escalation contact | Phone, Slack | For P1/major incidents; within 30 minutes | Business impact, recovery status, estimated resolution, external communication risk |
| **Regulatory / compliance** | Compliance officer, legal | Email, phone | As required by regulation | Incident nature, data affected, containment status, notification timeline |

### Communication cadence

| Phase | Frequency | Content |
|---|---|---|
| **Detection to triage** | As information becomes available | What is known, what is unknown, what is being investigated |
| **Active recovery** | Every 15-30 minutes (or per SLA) | Recovery progress, updated ETA, any escalation or blocker |
| **Recovery verification** | At verification completion | Recovery confirmed, data integrity status, any residual impact |
| **Post-recovery** | Once, within 24 hours | Summary of incident, root cause (if known), follow-up actions, next exercise date |

### Communication templates

#### Initial notification
```
Incident: [System] is experiencing [failure type] as of [time].
Impact: [What users/customers are experiencing].
Status: Recovery procedure [name] has been initiated. ETA: [estimated recovery time].
Next update: [time of next scheduled update].
Contact: [incident commander or recovery lead name and contact].
```

#### Status update
```
Update: [System] recovery — [time elapsed since start].
Progress: [What has been done, what is in progress].
Current status: [System state — degraded, recovering, verifying].
Revised ETA: [updated estimate if changed].
Next update: [time].
```

#### Recovery confirmation
```
Resolved: [System] has been recovered as of [time].
Verification: [Data integrity confirmed / pending / with gaps].
Duration: [Total recovery time from detection to verification].
RTO comparison: [Measured RTO] vs [Target RTO] — [met / exceeded by X].
RPO comparison: [Measured RPO] vs [Target RPO] — [met / exceeded by X].
Follow-up: [Link to follow-up work ledger or incident-learning entry].
```

## Anti-patterns

- **Radio silence during recovery.** Stakeholders fill silence with assumptions. Communicate even when there is no update: "Still investigating; next update at X."
- **Over-communicating to the wrong audience.** Executives need business impact, not technical command output. Engineers need technical detail, not executive summary. Tailor content to audience.
- **No communication plan before the exercise.** If you are figuring out who to notify during a recovery event, the communication plan has already failed. Pre-plan channels and templates.
- **No post-recovery summary.** Stakeholders need closure. A recovery event without a post-recovery summary leaves uncertainty about whether the system is truly recovered.
