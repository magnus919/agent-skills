# Rollback and Recovery

Rollback is not one operation. The single most common release-engineering failure is treating "undo the deploy" as a single button when it is really a family of mechanisms with wildly different speeds, blast radii, and risks. The second most common failure is assuming rollback is possible at all. Google SRE's framing is the right starting point: **rollback capability is a precondition for rollout, not an afterthought** — "there's no good rollout unless you have a corresponding rollback ready to do" — and the hardest lesson is that *reverting code is not rolling back a deploy*.

## The Four Undo Operations (Never Conflate)

| Operation | What it does | Speed | Risk | Notes |
|-----------|--------------|-------|------|-------|
| **Artifact rollback** | Redeploy the previous immutable, known-good artifact | Minutes | Low — deterministic, previously healthy | Requires retained, immutable artifacts and hermetic builds |
| **Roll-forward (hotfix)** | Build new release = old release + minimal fix, deploy it | Hours (build + test + deploy) | Medium — the new artifact has never run in prod | Google: discourages as first response for user-visible bugs |
| **Git revert** | Source-control revert that produces *new code* | Slow — must rebuild, retest, redeploy | High — new artifact untested in prod; reverts code only, not schema/data/config/flags | Reverting a commit with a destructive migration leaves old code + new schema = broken |
| **Feature-flag rollback** | Toggle the offending behavior off via remote config | Seconds (sub-second) | Very low — reversible, auditable | Only works if the change is behind a flag |

**Decision criteria** (synthesized across Google, GoCD, and mobile practitioners):

1. Is the defect behind a **feature flag**? → flag off. Seconds, no redeploy.
2. Otherwise, is it **user-visible or severe**? → artifact rollback. Minutes, back to a known-good state.
3. Is it **minor with a trivial, low-risk fix**? → roll-forward. A quick roll-forward is often preferable when the fix is genuinely small and well-tested.
4. Never `git revert` and redeploy as a "rollback" — it produces a *new* artifact that has never run in production and does nothing about migrations, data, config, or flag state.

The decision axes are **change-failure expectations, time-to-fix, blast radius, and user impact**. The two extremes are the ones teams get wrong: reaching for `git revert` (slow, new untested artifact) when an artifact rollback exists, and reaching for roll-forward under incident pressure when the fix is non-trivial.

> **Gotcha — git revert ≠ rollback:** `git revert` only reverts code. It does nothing about schema migrations, data changes, config, or feature-flag state that shipped alongside the commit. If the commit contained a destructive migration, reverting the code leaves an incompatible schema in place — the worst of both worlds.

## Rollback by System Type

Rollback difficulty tracks **reversibility**: from nearly trivial (stateless services) through hard (shared databases) to impossible (shipped device binaries). Pick the mechanism by the layer you touched.

| Layer | Reversibility | Primary mechanism |
|-------|---------------|-------------------|
| Feature-flagged behavior | Near-total | Toggle off (seconds) |
| Stateless services | High | Redeploy prior artifact, re-point traffic |
| Microservices | High (with N-1 compatibility) | Independent rollback, consumers before producers |
| Stateful / databases | Bounded | Expand/contract; safe only before finalization |
| Mobile / desktop | Low–none | Forward-fix, flags, phased-release pause |
| IoT / firmware | None once flashed | A/B partitions, watchdog auto-revert |

### Stateless Services

For a service behind a load balancer, artifact rollback is: redeploy the prior artifact across instances and re-point traffic. It looks trivial and hides four operational steps that teams routinely omit:

1. **Detection by version** — keep error/latency summaries **broken down by binary release version**. Subtle failures (e.g., errors only for "users whose name contains an apostrophe") surface in aggregate monitoring only once the majority of instances are upgraded; per-version metrics are what distinguish a bad canary from the control.
2. **Connection draining / graceful stop** — stop accepting new connections, finish in-flight requests, then terminate, so rollback causes no mid-request failures.
3. **Cache warming** — after redeploying the prior artifact, warm caches before full traffic; the previous version's caches are cold or evicted, and a cold-cache thundering herd is a classic post-rollback incident.
4. **Verification** — confirm per-version error rates return to the healthy baseline using the same SLI set as canary gating (HTTP status + latency; CPU/memory are noisy and unreliable signals) before declaring the rollback complete.

**Blue/green** makes stateless rollback near-instant: rollback is a trivial reversal of the router change, at 2× resource cost (see [progressive-delivery.md](./progressive-delivery.md)).

### Stateful Services and Databases

This is the hard case. The core problem: a schema change and a binary change can desynchronize. Google's canonical trap — you release the new binary, upgrade the schema, then find a problem and roll back the binary — leaves you with "a binary that doesn't expect the new schema, and hasn't been tested with it." Destructive changes (drop column, rename, add non-null) are **irreversible at the data level**: you cannot `git revert` dropped rows.

The discipline is **expand/contract (parallel change)** — the backbone of safe schema evolution (Fowler; operationalized in production by Bitwarden):

| Phase | What happens | Releases |
|-------|--------------|----------|
| **Expand** | Add the new structure (column/table) alongside the old; **both old and new code work** | Release X |
| **Migrate/Transition** | Backfill data (batched, as a background task to avoid load); update clients/code incrementally; old and new coexist and stay in sync (e.g., dual-write) | Release X → X+1 |
| **Contract** | Only after nothing depends on the old, remove it (drop the column) — **in a later release, never the deploy that introduced the change** | Release X+2 |

Bitwarden's **release support matrix** shows the invariant — the schema must always support the previous release of the server, so code can be rolled back:

| Database phase | Release X | Release X+1 | Release X+2 |
|----------------|-----------|-------------|-------------|
| Start (initial migration adds new, keeps old) | ✅ supported | ❌ | ❌ |
| Transition (dual-write, backfill) | ✅ | ✅ | ❌ |
| End (finalization drops old) | ❌ | ✅ | ✅ |

Three migration types enforce this:

- **Initial migration** (before code deploy): adds support for the new release *without breaking the old*; must be fast/cheap for zero downtime.
- **Transition migration** (background task during dual-write): batched data backfill only — **no schema changes in this phase**.
- **Finalization migration** (runs as part of the next deploy): drops the old structure; the schema now supports only the new release.

**Rollback is safe only before finalization.** The state machine is explicit: old code + old schema → initial migration → old code + new schema (both supported) — roll code back or forward safely. Then new code + new schema (both supported) — roll back safely. Then finalization → new code + finalized schema — **old code + finalized schema = broken**: rollback is no longer an option; you must roll *forward* with a new migration. On a safe rollback, "it should be as simple as just re-deploying the previous version again," with the database staying in transition until a patch ships. Fully pulling a feature after finalization requires writing a *new forward* migration to undo the change — generally not recommended, since pending migrations and the rollout need revisiting.

Supporting rules:

- **Forward-only migrations:** migrations are append-only, sequenced, version-controlled with app code, tracked in a changelog table (Flyway/Liquibase). You never un-apply a migration in production; you add a new one. Migrations should be idempotent — safe to run multiple times.
- **Feature-free release for schema-coupled changes (Google):** ship release v+1 = v but *able to safely handle the new schema* (no new features); upgrade the schema; then release v+2 that *uses* the schema. Now either binary can be rolled back without rolling back the schema.
- **Backup/restore and point-in-time recovery (PITR) as last resort:** restore when data is corrupted or lost and no forward path exists. Governed by **RPO** (max tolerable data loss — PITR to 5 minutes ago loses ≤5 minutes of writes) and **RTO** (max tolerable downtime — how long the restore takes). Restore is slow (violates fast rollback), lossy (violates known-good), and can clobber good post-backup data — hence *last resort*.

> **Gotcha — destructive migration in the same deploy:** The single most common stateful-release disaster is dropping the old column in the same release that introduces the new one. Contract must always be a later release — and if you need to roll back after a finalization, you have already lost that option.

### Microservices

Rollback ordering follows **dependency direction**, under one ecosystem assumption (Google): *any service could be rolled back by one version.* Operationally this is **N-1 compatibility**: your service must tolerate its dependency being one version behind what you built against, because that dependency may roll back. If your launch waits for dependency S to move from r to r+1, be sure S will "stick" at r+1 — otherwise wait for r+2 before depending on r+1 features.

| Direction | Deploy order | Rollback order |
|-----------|--------------|----------------|
| **Producers (providers)** | Ship backward-compatibly *first*: expand the API, keep old behavior working | Remove the capability *last* |
| **Consumers (callers)** | Deploy *after* the producer's additive change exists | **Roll back first** — undo the caller's use of the new behavior before the provider loses it |

This mirrors expand/contract: contract (remove old) only after all consumers have migrated; un-migrate (roll back) consumers first. **Version-skew tolerance** makes this practical: Tolerant Reader and Postel's Law ("be conservative in what you send, liberal in what you accept") let consumers ignore unknown fields so a provider can expand without breaking them. If every service is N-1 compatible, services roll back **independently** — no orchestration needed; coordinated/sequenced rollback is only required when compatibility windows are violated, which is itself a design smell (if deploying one service requires deploying others, you have hidden coupling). Independent deployability is also what makes **partial rollback** possible: revert the single offending service while others stay forward.

### Mobile, Desktop, and IoT

**Mobile:** a true rollback is **impossible** — once a build is installed on a device, the only way to change it is to distribute a new one (per iOS-factor: the only way to change an installed build is a new version with an updated version/build number). The approximation: re-submit the last stable binary as a "new" version with a **higher build number**, re-signed (modifying a build invalidates its signature), re-submitted to **store review** (hours to days). Store constraints compound it:

- Build numbers must monotonically increase (Apple and Google both enforce this).
- Apple will not let you create a new version until the current one is live — a timing trap when you need to replace a bad release immediately.
- Google allows only one draft release on the Production track.

And there is a **version long-tail**: even after a hotfix ships, some users keep running the bad version indefinitely — you cannot uninstall a bad build from a device you do not own.

Levers that substitute for rollback on mobile:

- **Phased/staged rollout** — iOS phased release can be *paused* before reaching most users, then the binary replaced — the closest thing to a real rollback.
- **Feature flags / remote config / kill switches** — disable the broken feature on already-installed binaries without any store interaction. You cannot force users to update, so **build a kill switch in from day one**.
- **Forced update** — gate the app behind a minimum version; used sparingly, as it is hostile UX.

> **Gotcha — mobile rollback + irreversible client migration:** If the faulty release included a client-side database migration that cannot be reversed, deploying a rollback build can corrupt user data. Client rollback safety depends on server/schema backward compatibility — the same rule as servers, now enforced on software you cannot reach.

**Desktop:** auto-update channels (stable/beta/canary/dev rings) give staged exposure; rollback is publishing the prior version to the channel or promoting a fix forward. Easier than mobile — no store review, no marketplace-imposed build monotonicity — but still forward-push, not reach-back.

**IoT / embedded / firmware:** rollback is a *hardware-architecture* concern, not a deploy concern:

- **A/B (dual-bank) partitions:** new firmware installs to the inactive partition; the boot switch happens only after validation; if the update fails, the system automatically reverts to the previous partition — blue/green at the firmware level, and the mechanism that makes device rollback possible at all.
- **Watchdog timers:** if the device hangs during/after update, trigger recovery to the good partition.
- **Power-loss resumption:** resume an interrupted OTA rather than corrupting the active image (a bricked, offline device may be unrecoverable remotely).
- **Anti-downgrade checks:** signed firmware with version anti-rollback prevents installing a known-vulnerable older image — a security-vs-rollback-freedom tension to resolve explicitly.
- Automotive/standards context: UNECE R156 and ISO 24089 require robust update management including anti-bricking.

**When devices are offline or bricked, rollback is genuinely impossible** — design for forward-fix and fail-safe (safe-state) behavior. The mobile/IoT rule generalizes: the less reach you have over the artifact, the more your "rollback" strategy must be *forward* strategy — flags, staged rollout, and safe degradation.

## Preconditions: Artifact Retention and Immutability

Rollback is only as good as your ability to *re-deploy the exact previous artifact*. The preconditions are cheap and routinely neglected:

- **Immutability:** never mutate a published artifact. Content-addressed storage and signing make "the same version always means the same bytes" verifiable (see [cd-and-pipeline-stages.md](./cd-and-pipeline-stages.md)).
- **Retention:** keep the last N known-good artifacts for every environment, with retention tied to your recovery objectives and compliance obligations. An artifact you deleted cannot save a Monday-morning rollback.
- **Movable promotion labels:** promote by moving labels (`dev`, `canary`, `production`) that point at immutable versions, so "roll back to production" means "point the label at the previous version" — a deterministic, scriptable operation.
- **Reproducibility:** hermetic builds mean a lost artifact can be rebuilt byte-for-byte from its revision — the safety net under retention.

These preconditions are also the answer to the question "how fast can we roll back?" The answer is bounded by what you retained and what you tested — which is why retention, rehearsal, and rollback speed are the same conversation.

## Operationalizing Rollback

- **Rehearsed rollbacks:** Google's practice — roll back "just because" every few weeks, to find traps (incompatible versions, broken automation, broken tests) *while the new release is healthy*, which is "better by far" than discovering them while the service is on fire. If the rollback works, roll forward again; if it breaks, roll forward to remove the breakage and then diagnose. Rollback drills are fire drills; skipping them is a failure mode.
- **Runbooks:** every service needs a rollback runbook with: decision thresholds (which metric/canary signal triggers rollback), the exact commands/automation to redeploy the prior artifact, verification steps (per-version SLIs back to baseline), an escalation path, and **manual checkpoints for data-sensitive operations** before anything touching a destructive migration or backup/restore. The runbook is the tested artifact; a runbook that has not been executed is a hypothesis.
- **Time-boxed decisions:** decide rollback-vs-roll-forward within a bounded window (minutes), rather than debugging while users burn. This is the operational expression of "rollback first, investigate second."
- **Automatic triggers:** wire canary analysis to automatic action — if the canary metric diverges too far from control, pause and roll back the deployment or page a human. Gate on a stack-ranked top-few SLIs (≤ ~a dozen), compare canary vs. control populations (never before/after), and size the canary by error budget: a 5% canary at 20% error costs ~1% overall, so auto-rollback at that tier costs almost nothing (see [progressive-delivery.md](./progressive-delivery.md)).
- **Quarantine + postmortem:** after a rollback, quarantine the bad artifact (label/remove it so it cannot be re-promoted), open a blameless postmortem, and capture a rollback changelist describing the observed problem. The postmortem's real output is fixing the *pipeline* that let the bad build through — thresholds, tooling, runbooks — not assigning blame.

**Rollback communications:** the rollback itself needs a communication plan, not just commands. Announce the detection and decision on the status page and internal channels early (users prefer an honest "we rolled back a release" to silent breakage); keep the rollback changelist attached to the incident so anyone can see *what was observed*; and after verification, publish the all-clear with the postmortem link. The communication is part of the rollback because trust is part of recovery — and "rollbacks are normal" only holds if the org treats them as routine, which means announcing them as routine.

**Culture:** Google treats rollbacks as normal — "rollbacks are normal." When an error is found or suspected in a new release, the releasing team rolls back first and investigates second; a rollback request "is not interpreted as an attack on the releasing team." Rollback must be *easy to perform* and *trusted to be low-risk*; rehearsal is what keeps it trusted.

## Rollback Decision Authority

Pre-decide **who can call a rollback and at what threshold** — this is a release-time decision that should not require a meeting. Google's cultural norm is the useful default: rollback authority is broad and exercised without stigma — "a rollback request is not interpreted as an attack on the releasing team." The practical rule: any engineer with evidence (canary metric divergence, error spike tied to the release) can initiate a rollback of a stateless service; the rollback changelist records the observed problem.

Authority narrows where risk concentrates:

- **Data-touching operations** (destructive migrations, backup/restore, DB cutovers) need explicit authority and **manual checkpoints** before execution — the operator who touches data is not the operator who casually flips a load balancer.
- **Cross-service coordinated rollbacks** (when N-1 compatibility is violated and consumers must roll back before producers) need a coordinator, because ordering mistakes compound the incident.
- **Time-boxed decisions** bound the window: decide within X minutes, then execute — the decision authority is exercised within the box, not after it (see [progressive-delivery.md](./progressive-delivery.md) for the automatic-trigger version of this).

## Rollback vs Roll-Forward

The guidance converges on a layered answer rather than a universal rule:

| Situation | Choice | Why |
|-----------|--------|-----|
| Change behind a flag | Flag off | Seconds, no deploy risk |
| User-visible/severe defect, or any significant bug | **Artifact rollback first** | Known-good state; Google warns a hasty roll-forward under incident pressure either fails to fix the problem or makes it worse — "you're taking yourself further from a known-good state" |
| Minor issue with a trivial, low-risk fix | Roll-forward | Quick; GoCD: a quick roll-forward is generally preferable, and *frequent* rollbacks signal weak pipeline gates |
| After DB finalization / on shipped binaries | Roll-forward (or forward-migration / new build) only | Rollback is no longer available |

Reconciling the philosophies: for fast-reversible layers (stateless services, flagged features) rollback is cheap and should be a reflex; for slow or irreversible layers (finalized schemas, shipped binaries) you *cannot* rely on rollback, so invest in progressive delivery to avoid needing it. Both are true — at different layers. Progressive delivery shrinks the set of changes that require the expensive kinds of rollback (see [progressive-delivery.md](./progressive-delivery.md)), and rehearsed rollback capability covers the ones that still need it.

## Gotchas

> **Gotcha — rollback that was never rehearsed:** The rollback that has not been run in months will fail at the worst moment — wrong artifact retention, broken automation, incompatible versions. Rehearse on a schedule, not under fire.

> **Gotcha — rolling back code past a destructive migration:** Rolling the binary back after finalization of a schema change leaves old code on a new schema. Verify the migration phase before any rollback touches a stateful layer.

> **Gotcha — cold caches after stateless rollback:** Redeploying the prior artifact without warming its caches trades one incident for a thundering-herd latency spike. Warm, then release traffic.

> **Gotcha — consumers rolling forward past a reverted producer:** If a producer rolls back and a consumer keeps calling the new API, you get production errors from a service you did not change. Roll consumers back first; enforce N-1 compatibility.

> **Gotcha — no version-labeled metrics:** Without per-version error/latency breakdowns you cannot tell *which* release is misbehaving in aggregate monitoring. Version labels on metrics are the prerequisite for both canary analysis and rollback verification.

> **Gotcha — anti-downgrade vs rollback freedom:** Signed firmware with anti-rollback protection blocks installing known-vulnerable images — but also blocks your rollback. Resolve the tension explicitly in the update architecture, not during an incident.

> **Gotcha — rolling back the wrong release:** Without version-labeled metrics, an error spike can be attributed to the latest release when the culprit is two releases back. Verify attribution from per-version SLIs *before* rolling back; rolling back the wrong version while the real offender stays deployed doubles the incident.

## Sources and Further Reading

- [Google Cloud — Reliable Releases and Rollbacks (CRE Life Lessons)](https://cloud.google.com/blog/products/gcp/reliable-releases-and-rollbacks-cre-life-lessons)
- [Google SRE Workbook — Canarying Releases (ch. 16)](https://sre.google/workbook/canarying-releases/)
- [Google SRE Book — Release Engineering (ch. 8)](https://sre.google/sre-book/release-engineering/)
- [Martin Fowler — Parallel Change](https://martinfowler.com/bliki/ParallelChange.html)
- [Martin Fowler — Evolutionary Database Design](https://martinfowler.com/articles/evodb.html)
- [Bitwarden — Evolutionary Database Design (production engineering docs)](https://contributing.bitwarden.com/contributing/database-migrations/edd/)
- [iOS-Factor — Rollbacks](https://ios-factor.com/rollbacks)
- [Redstone OTA — Anti-Bricking OTA: Failure Recovery & Safe-Fail Design](https://www.redstoneota.com/anti-bricking-ota-failure-recovery-safe-fail-design/)
