# Release Readiness Checklist — [RELEASE NAME] v[VERSION]

> One row per item. Every item needs a **named owner** (a person, not a team) and **evidence** (a link, log, or artifact). Do not mark an item done without evidence — the go/no-go call is only as strong as the checklist behind it. Target date: [YYYY-MM-DD]. Release manager: [name].

## Functional

| # | Check | Owner | Evidence | Done |
|---|-------|-------|----------|------|
| F-1 | Acceptance tests pass on the exact release-candidate artifact (not on latest main) | [name] | [CI run URL] | ☐ |
| F-2 | End-to-end smoke test of critical user journeys passes against the RC | [name] | [test report link] | ☐ |
| F-3 | UAT accepted by the business owner | [name] | [UAT sign-off ticket] | ☐ |
| F-4 | Known defects triaged: risk-rated and explicitly accepted or deferred | [name] | [ticket list] | ☐ |
| F-5 | Backward compatibility verified (API consumers, data contracts, N-1 services) | [name] | [contract test output] | ☐ |

## Non-Functional

| # | Check | Owner | Evidence | Done |
|---|-------|-------|----------|------|
| N-1 | Performance verified at peak load + margin (p95/p99 targets met) | [name] | [load test report] | ☐ |
| N-2 | Security scans clean or exceptions approved: SAST, dependency/CVE, secret scan | [name] | [scan reports] | ☐ |
| N-3 | Accessibility checks pass for UI changes | [name] | [a11y report] | ☐ |
| N-4 | Resilience validated: failover, circuit breakers, graceful degradation | [name] | [chaos / game-day record] | ☐ |
| N-5 | Capacity verified: no new scaling limits hit at projected traffic | [name] | [capacity plan / load test] | ☐ |

## Operational

| # | Check | Owner | Evidence | Done |
|---|-------|-------|----------|------|
| O-1 | Monitoring + alerting live for new metrics before go-live | [name] | [dashboard link] | ☐ |
| O-2 | Runbooks exist and were read by on-call (deploy, rollback, incident) | [name] | [runbook links, read receipts] | ☐ |
| O-3 | Deployment rehearsed in staging; exact steps executed once | [name] | [staging deploy log] | ☐ |
| O-4 | Rollback path tested, not assumed (time-boxed rehearsal) | [name] | [rollback-runbook.md](rollback-runbook.md) rehearsal log | ☐ |
| O-5 | On-call coverage confirmed for the post-release window (48–72 h) | [name] | [roster] | ☐ |
| O-6 | Data safety checkpoints set for any migration or destructive step | [name] | [migration plan + RPO/RTO values] | ☐ |

## Governance

| # | Check | Owner | Evidence | Done |
|---|-------|-------|----------|------|
| G-1 | Change record created and linked to this release ([change-governance-record.md](change-governance-record.md)) | [name] | [change ID / ticket] | ☐ |
| G-2 | Approval recorded by a person who is not the author | [name] | [approval record] | ☐ |
| G-3 | Separation of duties enforced: deployer ≠ author ≠ approver | [name] | [deploy log] | ☐ |
| G-4 | Artifact digest + SBOM/provenance recorded for the promoted artifact | [name] | [digest + SBOM link] | ☐ |
| G-5 | Audit artifacts linked end-to-end: ticket → PR → CI → approval → deploy → verify | [name] | [traceability export] | ☐ |

## Go / No-Go Decision

### Conditions for GO

All of the following must hold; record evidence next to each:

- [ ] All Functional items F-1..F-5 complete with evidence
- [ ] All Non-Functional items N-1..N-5 complete with evidence
- [ ] All Operational items O-1..O-6 complete with evidence
- [ ] All Governance items G-1..G-5 complete with evidence
- [ ] No open Critical or High severity defects; accepted risks documented in [release-plan.md](release-plan.md) section 5
- [ ] Rollback rehearsal completed within the last [30] days
- [ ] On-call coverage confirmed for the monitoring window

### Decision

| Field | Value |
|-------|-------|
| Decision | GO / NO-GO / GO WITH CONDITIONS |
| Meeting time (UTC) | [YYYY-MM-DD HH:MM UTC] |
| Conditions (if GO WITH CONDITIONS) | [condition — owner — deadline] |
| Decision record link | [link to meeting notes / recorded decision] |

### Signatories

| Role | Name | Signature / Date |
|------|------|------------------|
| Engineering lead | | |
| SRE / operations lead | | |
| Product owner | | |
| Release manager | | |

> The go/no-go decision is a time-stamped, recorded call by named individuals — not a round of applause. If conditions are attached, the release does not proceed past the next stage until they are closed.

## Checklist Hygiene

- Keep every item's evidence URL live until the release ticket closes; stale links break the audit chain.
- Re-run the checklist as a whole after any change to the release candidate — partial re-runs miss interactions.
- Record the checklist result (with the go/no-go decision) in the release ticket so the call is traceable.
- Evidence types to prefer: CI run URLs, scan reports, dashboard snapshots, deploy logs, and sign-off tickets — each maps to a row above.
