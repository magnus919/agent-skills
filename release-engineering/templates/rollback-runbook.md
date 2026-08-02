# Rollback Runbook — [SERVICE / SYSTEM] v[VERSION]

> One runbook per service or release. Fill in the placeholders, then rehearse it — an unrehearsed runbook is fiction. Keep this next to the deploy runbook. Last reviewed: [YYYY-MM-DD] by [name].

## 1. When This Runbook Applies

| Field | Value |
|-------|-------|
| Service / system | [name] |
| Release(s) covered | [e.g., v2.4.0 and any patch on top of it] |
| Known-good artifact | [image:tag + sha256 digest] |
| Deploy mechanism | [Argo CD sync / pipeline deploy / manual steps] |
| Rollback decision authority | [name — on-call lead; decision time-boxed to X minutes] |

## 2. Trigger and Detection Thresholds

Initiate rollback (or flag-off) when any of these holds for the stated window. Base thresholds on pre-release baselines, not guesses.

| Signal | Threshold | Window | Tool / Alert |
|--------|-----------|--------|--------------|
| Error rate (HTTP 5xx) | [e.g., > 1.0%, or > 2× baseline] | [10 min] | [Datadog alert] |
| Latency p95 | [e.g., > 300 ms, or > 1.5× baseline] | [15 min] | [Grafana] |
| Error budget burn | [e.g., > 2% of monthly budget consumed in 1 h] | [1 h] | [burn-rate alert] |
| Saturation / capacity | [e.g., CPU/memory > 85% on > 50% of instances] | [15 min] | [infra alert] |
| Data integrity | [e.g., migration verification query fails] | [immediately] | [migration log] |
| Business signal | [e.g., support-ticket spike about the new feature] | [1 h] | [ticketing] |

> **Gotcha —** compare canary vs. control populations, never "before vs. after" (time is a confound). If the defect is gated behind a feature flag, flip the flag off first — it is the fastest and least risky lever.

## 3. Impact Assessment

| Question | Answer |
|----------|--------|
| Who is affected? | [users / segments / internal teams] |
| What is the blast radius? | [service, downstream dependencies, data, clients] |
| Severity | [SEV-1 / SEV-2 / SEV-3] |
| Is data at risk? | [yes/no — if yes, stop and involve the DB owner before acting] |
| Was a schema migration deployed with this release? | [yes/no — if yes, see section 5.3; rollback may be unsafe after finalization] |
| Is the change client-side (mobile/desktop/IoT)? | [yes/no — if yes, rollback is forward-only; use a kill switch / phased release] |

## 4. Decision Matrix — Rollback vs. Roll-Forward vs. Flag-Off

| Situation | Recommended action | Why |
|-----------|--------------------|-----|
| Defect is behind a feature flag | **Flag off** | Seconds, no redeploy, fully reversible, auditable |
| User-visible or severe defect, flag not involved | **Artifact rollback** | Returns to a known-good state that has run in production |
| Minor defect with a trivial, low-risk fix | **Roll-forward (hotfix)** | Faster than rollback if the fix is certain; still build + test + stage it |
| Destructive schema change already finalized | **Roll-forward with a new migration** | Code rollback is broken after finalization — never combine old code with a finalized schema |
| Data corruption / loss, no forward path | **Backup / point-in-time restore (last resort)** | Slow and lossy; governed by RPO/RTO — escalate first |

> **Gotcha —** `git revert` is not a rollback. It produces new code that must be rebuilt, retested, and redeployed, and it does not undo migrations, data changes, or flag state that shipped with the reverted commit.

## 5. Step-by-Step Rollback

### 5.1 Ordering (microservices)

- Roll **consumers back before producers**: undo the caller's use of the new behavior before removing the provider's capability.
- Assume any service may roll back one version (N-1 compatibility): never depend on a service that could roll back under you.
- With N-1 contracts in place, services roll back independently — no orchestration needed. Coordinated rollback across services is a design smell.

### 5.2 Stateless services / artifacts

1. [Announce in #incident / #releases: "Rolling back <service> to <known-good version> — reason: <observed signal>".]
2. [Re-point the deploy to the known-good artifact — e.g., `kubectl set image deployment/<svc> <svc>=<registry>/<svc>:<good-tag>`, or Argo CD sync to the previous tag, or pipeline "redeploy release <previous>".]
3. [Enable connection draining / graceful termination so in-flight requests finish.]
4. [Warm caches before restoring full traffic to avoid a latency spike.]
5. [Confirm new pods healthy and traffic shifted.]
6. [Blue/green: rollback is a router change — cut traffic back to the blue environment, verify, then keep the bad green environment for inspection.]

### 5.3 Stateful services / databases

1. [Identify the migration phase: initial / transition / finalization. Never roll code back past a finalized schema.]
2. [If code rollback is safe (schema still supports the previous release): redeploy the previous binary; the database stays in the transition phase until a patch is released.]
3. [For feature removal: prefer a new forward migration (append-only, idempotent) over "un-applying" the old one.]
4. [If data is corrupted: escalate to the DB owner; plan backup / point-in-time restore with RPO [X min] and RTO [Y min]; get approval before restoring.]
5. [Manual checkpoint before any destructive step — pause and confirm with the on-call lead.]

### 5.4 Clients / devices (mobile, desktop, IoT)

1. [Rollback is not possible for shipped binaries — use a kill switch / remote config / feature flag to disable the broken behavior.]
2. [Mobile: pause a phased release, then publish the last stable build as a new version with a higher build number, re-signed and re-submitted.]
3. [IoT: rely on A/B (dual-bank) partitions + watchdog auto-revert; validate post-install before switching the active bank.]
4. [Document the version long-tail: some users will keep the bad version for days or indefinitely.]

## 6. Verification (Rollback Is Complete When ...)

| SLI | Target after rollback | Check |
|-----|----------------------|-------|
| Error rate | [back to baseline, e.g., < 0.5%] | [dashboard link] |
| Latency p95 | [back to baseline, e.g., < 250 ms] | [dashboard link] |
| Error budget | [no longer burning] | [budget dashboard] |
| Version breakdown | [100% of traffic on the known-good version] | [version-labeled metrics] |
| Data integrity | [migration / consistency checks green] | [check output] |

> **Gotcha —** verify per-version metrics, not aggregate: subtle failures (e.g., errors only for a subset of users) surface only when most instances run the bad version.

## 7. Communication Plan

| Audience | Channel | Message | When |
|----------|---------|---------|------|
| Internal (eng + on-call) | #incident | Decision + observed signal | Immediately |
| Support | #support | User-facing impact + ETA | Within [15] min |
| Customers / status page | status page | Outage / degradation notice | Within [30] min |
| Post-incident | #postmortems | Rollback changelist + timeline | After resolution |

## 8. Post-Rollback Activities

- [ ] **Quarantine the bad artifact**: label/deny it so it cannot be re-promoted (e.g., remove the tag, blocklist the digest).
- [ ] **Record the rollback changelist** describing the observed problem (see [change-governance-record.md](change-governance-record.md)).
- [ ] **Open a blameless postmortem** within [2] business days; rollbacks are normal, not a failure of the team.
- [ ] Fix the pipeline / thresholds that let the defect through (CI gap, missing canary stage, wrong threshold).
- [ ] Update this runbook and the readiness checklist with lessons learned.

## 9. Rehearsal Log

> Rehearse "just because" every few weeks — find traps (incompatible versions, broken automation) while the release is healthy. If rehearsal breaks, roll forward and fix the cause.

| Date | Rehearsed by | Scenario | Result | Traps found | Follow-up |
|------|--------------|----------|--------|-------------|-----------|
| [YYYY-MM-DD] | [name] | [e.g., canary error-rate spike] | Pass / Fail | [none / description] | [ticket] |
| [YYYY-MM-DD] | [name] | [e.g., migration rollback window] | Pass / Fail | [none / description] | [ticket] |
