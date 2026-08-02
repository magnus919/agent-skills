# Hotfix / Emergency Release Plan — [HOTFIX VERSION]

> For SEV-1 incidents, security exploits, or critical data issues that cannot wait for the normal release train. Fill in the placeholders and obtain the required approvals BEFORE deploying. The normal governance chain is abbreviated — not skipped. See [change-governance-record.md](change-governance-record.md) section 6 for the emergency evidence requirements.

## 1. Emergency Details

| Field | Value |
|-------|-------|
| Severity | SEV-1 / SEV-2 / SEV-3 |
| Incident link | [incident ticket / war-room channel] |
| Hotfix version | [e.g., 2.4.1 — must be greater than the broken 2.4.0] |
| Broken version being fixed | [e.g., 2.4.0] |
| Incident commander | [name] |
| Release manager (hotfix DRI) | [name] |
| Target deploy time | [YYYY-MM-DD HH:MM UTC] |

## 2. Problem Statement

[What is broken, the observed impact (users/data/revenue), and the minimal fix that addresses it. One or two sentences plus the error/alert IDs.]

## 3. Hotfix Branch and Cherry-Picks

| Step | Detail |
|------|--------|
| Branch cut from | [production tag or last known-good release branch, e.g., release/2.4] |
| Hotfix branch | [e.g., hotfix/2.4.1-cve-auth-bypass] |
| Cherry-pick list | [commit SHAs, one per line, each with its original PR] |
| Excluded from hotfix | [anything in main that must NOT ride along — keep the diff minimal] |

> A hotfix must contain ONLY the fix. Do not pull in unrelated merges — every extra line is new risk under pressure.

## 4. Expedited Pipeline Path

| Stage | Expedited step | Who |
|-------|----------------|-----|
| Build | Hermetic build of the hotfix branch | [CI] |
| Tests | Targeted regression + smoke + tests covering the fixed path (full suite if time allows) | [eng lead] |
| Security | [scans if applicable — security fixes get SAST + dependency re-scan] | [sec eng] |
| Deploy | Canary subset → monitor [X min] → full rollout (never straight to 100% without a canary step) | [deployer] |

## 5. Required Approvals (Break-Glass)

> Same tracking system as normal changes — no shadow logs. Approvals may be post-hoc but are mandatory and time-stamped.

| Approval | Approver (≠ author) | Method | Deadline |
|----------|---------------------|--------|----------|
| Emergency change approval | [senior manager / on-call lead] | [chat + ticket, recorded] | Before deploy |
| Retroactive documentation | [release manager] | [change-governance-record.md](change-governance-record.md) section 6 | Within [24–72] h |
| Post-implementation review | [eng lead] | [postmortem] | Within [7] days |

## 6. Rollback Plan

- Known-good artifact (pre-incident): [e.g., api:2.3.1 + digest sha256:...]
- Rollback trigger: [e.g., hotfix error rate > 2× baseline for 10 min]
- Rollback mechanism: [re-deploy known-good artifact / flag off / forward migration — see rollback-runbook.md]
- Special caution: [e.g., "if the incident involved a data migration, verify the schema supports the rollback target before rolling code back"]

## 7. Communication Plan

| Audience | Channel | When |
|----------|---------|------|
| Incident team | #incident | Continuously |
| Engineering | #releases | On branch cut and deploy |
| Support | #support | Before user-facing impact is seen |
| Customers / status page | status page | Per severity SLA |

## 8. Post-Implementation Review

- [ ] Root cause documented in a blameless postmortem by [date — within 7 days]
- [ ] Permanent fix tracked for the next regular release
- [ ] Emergency procedure reviewed: was the break-glass path used correctly? Is the emergency ratio healthy (< [X]% of changes)?
- [ ] Monitoring/alerts added or tuned to catch this class of failure earlier
- [ ] Hotfix diff reviewed and merged back to main / release branches

## 9. Sign-Offs

| Role | Name | Date | Decision |
|------|------|------|----------|
| Incident commander | | | Deploy approved / Rejected |
| Release manager | | | Deploy approved / Rejected |
| Senior approver (emergency) | | | Retro-approval granted / Pending |
