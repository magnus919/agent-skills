# Change Governance Record — [CHANGE ID]

> One record per production change. This is the artifact an auditor samples (SOC 2 CC8.1: request → review → test → approve → deploy → verify). Every field must be populated for the change to be audit-ready; leave nothing implied. Retention: at least 12 months (SOC 2 / PCI DSS); 7 years if this touches a financial-reporting system (SOX).

## 1. Change Identification

| Field | Value |
|-------|-------|
| Change ID | [e.g., CHG-2026-0417 — unique, sequential] |
| Change title | [short description] |
| Ticket link | [ticketing link — contains business justification, risk assessment, test plan] |
| Risk tier | Low / Medium / High / Emergency (see section 6) |
| Type | Feature / Fix / Security / Configuration / Infrastructure / Migration |
| Requester | [name] |
| Date requested | [YYYY-MM-DD] |

## 2. Description and Justification

### Description

[What changed and why. Enough context that a reviewer with no memory of this change can evaluate it.]

### Business justification

[Problem being solved, expected outcome, success criteria.]

## 3. Design and Review

| Field | Value |
|-------|-------|
| Design / RFC link | [link for significant changes — ADR, design doc] |
| PR / MR link(s) | [link to the pull request containing the diff] |
| Author | [name] |
| Reviewer(s) | [name(s) — at least one engineer other than the author] |
| Review approval time (UTC) | [YYYY-MM-DD HH:MM UTC] |
| Branch protection enforced | Yes / No |

> Branch protection (required peer review, status checks) is the control that makes the review record trustworthy. Never disable it "temporarily" — use the emergency path in section 6 instead.

## 4. Testing and CI

| Field | Value |
|-------|-------|
| CI pipeline run ID(s) | [e.g., Actions run #12345 / GitLab pipeline 67890] |
| Commit SHA tested | [full SHA] |
| Unit / integration results | [pass link] |
| Security scans (SAST / dependency / secret) | [report links + pass/fail] |
| Test environment(s) | [staging, perf, ...] |
| Test data used | [synthetic / masked subset — no production PII in test environments] |

## 5. Approval (Deployment Gate)

| Field | Value |
|-------|-------|
| Approver | [name — MUST NOT be the code author] |
| Approval decision | Approved / Rejected |
| Approval time (UTC) | [YYYY-MM-DD HH:MM UTC] |
| Approval mechanism | [e.g., GitHub Environments required reviewer, CAB record] |
| Deployer | [name or pipeline identity — separate from the author where required] |

## 6. Emergency Change (Break-Glass) — only if applicable

| Field | Value |
|-------|-------|
| Emergency flag | Yes / No |
| Emergency justification | [why the normal path was bypassed — security exploit / production outage] |
| Authorized approver | [senior manager / on-call lead] |
| Retroactive approval due | [within 24–72 h per org policy] |
| Retroactive approval date | [YYYY-MM-DD] |
| Post-implementation review due | [YYYY-MM-DD — within X days] |

> Emergency ≠ uncontrolled. The break-glass path is an alternate, audited path: it still requires approval, testing (as far as possible), and full documentation in the same tracking system as normal changes.

## 7. Deployment

| Field | Value |
|-------|-------|
| Environment(s) | [staging → production (list all)] |
| Deploy timestamp (UTC) | [YYYY-MM-DD HH:MM UTC per environment] |
| Artifact (name + version) | [e.g., api:2.4.0] |
| Artifact digest | [sha256:...] |
| SBOM / provenance | [link — SLSA attestation] |
| Deployment mechanism | [pipeline deploy / Argo CD sync / manual] |
| Pipeline run ID (deploy) | [run ID] |
| Rollout strategy | [canary / blue-green / rolling / feature-flag — see deployment-strategy-matrix.md] |

## 8. Post-Deployment Verification

| Field | Value |
|-------|-------|
| Smoke / synthetic checks | [results link] |
| Health / SLI confirmation | [dashboard snapshot or link, e.g., error rate below threshold] |
| Rollback status | [not needed / available / triggered — see rollback-runbook.md if triggered] |
| Verification time (UTC) | [YYYY-MM-DD HH:MM UTC] |
| Ticket closed | [date, by whom] |

## 9. Evidence Traceability (audit summary)

| Chain step | Artifact | Location / link |
|------------|----------|-----------------|
| Request & authorization | Ticket | [link] |
| Design & review | PR with approvals | [link] |
| Testing | CI runs + scan reports | [link] |
| Final approval | Approval record (approver ≠ author) | [link] |
| Implementation | Deploy log + artifact digest | [link] |
| Post-implementation review | Verification + ticket closure | [link] |

> Timestamps must be UTC everywhere, and tools must be NTP-synchronized so the chain correlates. Keep the evidence chain intact after merge — never delete merged PRs, release branches, or deploy logs.
