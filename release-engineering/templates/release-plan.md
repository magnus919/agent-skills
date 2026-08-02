# Release Plan — [RELEASE NAME] v[VERSION]

> Fill in every `[PLACEHOLDER]` and delete the italic guidance notes before publishing. Keep this file in the release branch and link it from the release ticket so the audit chain ([change-governance-record.md](change-governance-record.md)) can reference it.

## Metadata

| Field | Value |
|-------|-------|
| Release name | [e.g., Aurora — a short, memorable label for the release train] |
| Version | [e.g., 2.4.0 — must match version-control tags and artifact names] |
| Target date (GA) | [YYYY-MM-DD] |
| Release manager (DRI) | [name — exactly one accountable owner] |
| Status | Draft / Frozen / In Flight / Shipped / Rolled Back |
| Changelog / commit source | [link to CHANGELOG.md or the commit range, e.g., main...release/2.4] |

## 1. Overview and Scope

### Objective

[One or two sentences: the user/business outcome this release delivers and how success is measured. Make it verifiable — "reduce checkout p95 latency by 20%", "GA the billing API v2", "remediate the CVE-2026-XXXX dependency".]

### In Scope

| ID | Item | Type (feat/fix/chore/security) | Source (PR/commit) |
|----|------|--------------------------------|--------------------|
| S-1 | [item] | feat | [#1234] |
| S-2 | [item] | fix | [abc1234] |

> Pull scope from the changelog or `git log --oneline <from>..<to>`; every item should trace to a merged PR or commit. The `release_plan_scaffold.py` script generates this table from a git range.

### Out of Scope

- [item — and why it is excluded: next release, blocked, product decision]
- [item]

## 2. Versioning and Artifacts

| Field | Value |
|-------|-------|
| Version scheme | SemVer / CalVer (see [versioning-decision-table.md](../assets/versioning-decision-table.md)) |
| Primary artifact(s) | [e.g., image registry.example.com/api:2.4.0, dist/api-2.4.0.tar.gz] |
| Artifact digest(s) | [sha256:... — of the exact artifact promoted to production] |
| SBOM / provenance | [link to SBOM (CycloneDX/SPDX) and SLSA provenance attestation] |
| Promotion policy | [build once, promote the same immutable artifact dev → staging → prod] |

## 3. Timeline and Milestones

| Milestone | Date | Owner | Exit Criteria |
|-----------|------|-------|---------------|
| Branch cut | [YYYY-MM-DD] | [name] | release/[version] branch created from main; CI green on branch |
| Code freeze | [YYYY-MM-DD] | [name] | only blockers merge; freeze announced in release channel |
| Release candidate build | [YYYY-MM-DD] | [name] | RC artifact built once, signed, digest recorded |
| Full test pass / UAT | [YYYY-MM-DD] | [name] | acceptance tests + UAT sign-off on the RC artifact |
| Staging deploy | [YYYY-MM-DD] | [name] | staging parity confirmed; readiness checklist run |
| GA / go-live | [YYYY-MM-DD] | [name] | go/no-go passed; rollout started |
| End of rollout | [YYYY-MM-DD] | [name] | 100% of target population on new version |
| Monitoring window closes | [YYYY-MM-DD + 48–72 h] | [name] | post-release monitoring done; release ticket closed |

> Freeze dates are a commitment: any change after branch cut needs the release manager's explicit sign-off and a re-run of the affected gates.

## 4. Owners and RACI

| Activity | R (Responsible) | A (Accountable) | C (Consulted) | I (Informed) |
|----------|-----------------|-----------------|---------------|--------------|
| Scope definition | [eng lead] | [PM] | [eng team] | [stakeholders] |
| Build & test | [CI owner] | [eng lead] | [QA] | [release manager] |
| Deploy | [deployer] | [release manager] | [SRE] | [eng team] |
| Rollback decision | [release manager] | [on-call lead] | [SRE, eng lead] | [all] |
| Comms | [comms owner] | [release manager] | [PM] | [customers] |
| Post-release monitoring | [SRE] | [SRE lead] | [eng lead] | [release manager] |

> Every row needs exactly one Accountable. The approver must never equal the deployer (separation of duties — see [change-governance-record.md](change-governance-record.md)).

## 5. Risks and Mitigations

| ID | Risk | Probability (H/M/L) | Impact (H/M/L) | Mitigation | Owner |
|----|------|---------------------|----------------|------------|-------|
| R-1 | [e.g., new dependency unavailable in prod registry] | M | H | [e.g., pre-push artifact to prod registry during staging] | [name] |
| R-2 | [e.g., schema migration locks the payments table] | M | H | [e.g., expand/contract migration; backfill in background; see rollback-runbook.md] | [name] |
| R-3 | [e.g., third-party API rate limit during launch] | L | M | [e.g., staged rollout + circuit breaker] | [name] |

## 6. Rollout Plan

| Strategy | [Canary / blue-green / rolling / ring / feature-flag — see deployment-strategy-matrix.md] |
|----------|--------------------------------------------------------------------------------------------|
| Staged progression | [e.g., canary 5% (4 h) → 25% (24 h) → 50% (24 h) → 100%; or ring: internal → beta → 10% → 100%] |
| Gate between stages | [SLI thresholds that must hold before the next stage, e.g., error rate < X%, p95 latency < Y ms] |
| Feature flags | [list flags toggled as part of this release and who flips them] |
| Auto-rollback trigger | [e.g., canary error rate > 2× baseline for 10 min → automatic rollback of canary] |
| Go/no-go authority | [who decides to pause or abort the rollout] |

## 7. Rollback Contingency

- Decision path, commands, and verification steps: see [rollback-runbook.md](rollback-runbook.md).
- Decision authority: [name] (on-call lead) — decision time-boxed to [X] minutes after a confirmed signal.
- Known-good artifact: [e.g., registry.example.com/api:2.3.1 with digest sha256:...]
- Special cases: [list anything unusual — irreversible migrations, client-side changes that cannot be recalled, data changes]

## 8. Communication Plan

| Audience | When | Channel | Message Owner |
|----------|------|---------|---------------|
| Internal engineering | [branch cut / RC / GA] | [#releases] | [release manager] |
| Support / on-call | [before GA] | [#support-handoff] | [comms owner] |
| Customers / status page | [GA + during rollout] | [status page, release notes] | [PM] |
| Executives | [GA] | [email / weekly] | [release manager] |

## 9. Post-Release Monitoring

| What | Where | Window | Alert Threshold |
|------|-------|--------|-----------------|
| [e.g., deployment frequency & change failure rate] | [DORA dashboard] | [48–72 h] | [n/a — trend] |
| [e.g., checkout p95 latency] | [Grafana] | [72 h] | [> 300 ms for 15 min] |
| [e.g., payment error rate] | [Sentry / Datadog] | [72 h] | [> 0.5% for 10 min] |
| [e.g., support tickets mentioning new feature] | [ticketing] | [1 week] | [n/a — triage] |

## 10. Sign-offs

| Role | Name | Date | Decision |
|------|------|------|----------|
| Engineering lead (quality) | | | Approved / Not approved |
| SRE / operations (rollback + monitoring ready) | | | Approved / Not approved |
| Product owner (scope + comms) | | | Approved / Not approved |
| Release manager (final) | | | GO / NO-GO / GO WITH CONDITIONS |

> GO WITH CONDITIONS requires named conditions, owners, and deadlines in the table below.

| Condition | Owner | Deadline | Status |
|-----------|-------|----------|--------|
| [condition] | [name] | [date] | Open / Done |
