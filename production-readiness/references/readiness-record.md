# Production Readiness Record

Fill one record per launch candidate. Replace every `_[fill: ...]_` marker.

## Risk classification

- **Risk class:** _[fill: Low / Standard / High]_
- **Rationale:** _[fill: which trigger condition applies, e.g. "customer-facing service launch with SLO-bearing change"]_

## Evidence checklist

For each category: provide a named source artifact OR an explicit gap annotation
with owner and due date. No blank entries.

| # | Category | Source / evidence | Gap / missing |
|---|---|---|---|
| 1 | Ownership | _[fill: team name, on-call rotation, escalation path]_ | _[fill or "none"]_ |
| 2 | User/business outcome | _[fill: success metric, OKR link, product brief]_ | _[fill or "none"]_ |
| 3 | Dependencies | _[fill: dependency map, health-check results]_ | _[fill or "none"]_ |
| 4 | SLOs | _[fill: SLO declaration, error-budget policy]_ | _[fill or "none"]_ |
| 5 | Observability | _[fill: dashboard link, alert rules, monitoring coverage]_ | _[fill or "none"]_ |
| 6 | Support | _[fill: runbook, support playbook, escalation matrix]_ | _[fill or "none"]_ |
| 7 | Security | _[fill: security review record, threat-model summary]_ | _[fill or "none"]_ |
| 8 | Data | _[fill: data classification, retention/deletion policy, migration test]_ | _[fill or "none"]_ |
| 9 | Rollback | _[fill: rollback runbook, rehearsal log, recovery-time estimate]_ | _[fill or "none"]_ |
| 10 | Capacity | _[fill: capacity model, load-test report, quota review]_ | _[fill or "none"]_ |
| 11 | Cost | _[fill: cost estimate, budget approval]_ | _[fill or "none"]_ |

## Structured field confirmation

- [ ] Ownership — named owner or team recorded above
- [ ] Rollback — rollback plan or recovery path recorded above
- [ ] Support — runbook or support handoff recorded above
- [ ] Observability — dashboards and alert rules recorded above

## Launch decision

- **Decision:** _[fill: Go / No-go / Defer / Exception]_
- **Accountable owner:** _[fill: name and role]_
- **Date:** _[fill: YYYY-MM-DD]_

### If Exception

- **Gap being waived:** _[fill: which evidence category and why it cannot be filled]_
- **Human approver (required — must be distinct from submitter):** _[fill: name and role]_
- **Approval date:** _[fill: YYYY-MM-DD]_
- **Review cadence:** _[fill: when the waived gap will be re-assessed]_

### If No-go

- **Blocking gap(s):** _[fill: which categories are blocking and why]_
- **Resolution path:** _[fill: what must happen to unblock]_

### If Defer

- **Deferred conditions:** _[fill: specific conditions that must be met]_
- **Re-review date:** _[fill: YYYY-MM-DD]_
- **Gap owners:** _[fill: names and due dates]_
