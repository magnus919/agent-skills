# Continuous Delivery and Pipeline Stages

The pipeline is where release engineering becomes machinery: it decides what can ship, how fast it can ship, and — if designed badly — how slowly and how riskily. The canonical pattern is deceptively simple: build an artifact **once**, then **promote** that same immutable artifact through progressively more production-like environments. Most pipeline failures come from violating one of the words in that sentence: the artifact gets rebuilt, or the environments diverge, or the gates stop meaning anything.

## Continuous Delivery vs Continuous Deployment

The two terms are routinely conflated; the distinction is one human decision.

- **Continuous Delivery (CD):** software is *always releasable*. The current version of every service could be deployed to production at a moment's notice, but a human or business process chooses when and how often to actually release. The Thoughtworks CD working group's indicators: the software is deployable throughout its lifecycle; keeping it deployable is prioritized over new features; fast, automated feedback on production-readiness is available; and any version can be pushed to any environment at the push of a button.
- **Continuous Deployment:** every change that survives the pipeline is *automatically* put into production, often many times per day. Continuous deployment is CD plus the removal of the human release decision.

| | Continuous Delivery | Continuous Deployment |
|---|---|---|
| Deployable at any time | Yes | Yes |
| Who triggers production deploy | Human/business decision (push-button) | The pipeline, automatically |
| Prerequisite | Automated gates + release candidate discipline | CD + high-confidence automated gates + fast rollback |
| Typical cadence | On-demand, business-chosen | Many per day |

> **Gotcha — "we do CD" meaning "we have CI":** Continuous integration (frequent merges to trunk with automated builds) is a prerequisite, not the deliverable. If a human still edits environment config by hand or rebuilds per environment, you have CI, not CD.

## The Canonical Pipeline: Build Once, Promote Many

The deployment pipeline (Humble & Farley's *Continuous Delivery* is the canonical source) has a fixed spine:

```
Commit → Build → Unit tests → Integration/system tests → Package/artifact
  → Promote dev → Promote staging/pre-prod → Deploy production → Verify
```

The two load-bearing rules:

1. **Build once.** The exact artifact that ran tests is the exact artifact that reaches production. Rebuilding per environment means production runs code that was never tested — the pipeline's core guarantee is void. "Only build binaries once" is the founding rule of the field, and it is still violated more often than it should be.
2. **Promote, don't re-package.** Promotion moves an immutable artifact between environments, ideally by moving a pointer or label rather than copying bits. Google's MPM packages are content-hashed, versioned, and signed, with movable labels (`dev`, `canary`, `production`) pointing at immutable versions. Content-addressed storage and digest-pinned references make promotion verifiable: the promoted digest equals the tested digest.

### Stage Inventory

| Stage | Responsibility | Typical gates | Promotion evidence |
|-------|----------------|---------------|--------------------|
| Source | Trigger on commit/PR; capture commit metadata | Branch protection, review | Commit SHA, author, PR number |
| Build | Produce the artifact hermetically | Hermetic/reproducible build succeeds | Artifact digest (SHA-256) |
| Unit + static analysis | Fast correctness and lint | Test suite, SAST, dependency scan | Test reports, scan results |
| Integration/system | Cross-component behavior | Contract tests, E2E, integration suite | Test reports pinned to digest |
| Package/publish | Store immutable artifact + metadata | Signing, SBOM generation, provenance attestation | Signed digest, SBOM, attestation |
| Promotion (dev → staging) | Move artifact through pre-prod | Deploy + smoke tests + config validation | Deploy log per environment |
| Promotion (staging → prod) | Deploy to production | Canary/metric gates, error-budget check, approval if any | Deploy log, verification window |

Each stage gates the next; the artifact only promotes when the previous stage passes. The evidence each stage emits is what makes the pipeline auditable (see [change-governance-and-compliance.md](./change-governance-and-compliance.md)) — a pipeline that emits no structured records produces no audit trail even though it "does CI."

### Push-on-Green vs Select-a-Build

**Push-on-green** is the Google-flavored extreme: deploy every build that passes all tests, automatically. Google describes it as one end of a spectrum — some Google teams deploy every green build; others **build hourly and select** a build to promote based on test results and feature content. Both are legitimate; the selection model adds human judgment about *what* to ship, while push-on-green optimizes for velocity. Start with selection, graduate to push-on-green as metrics and rollback mature. Push-on-green without fast automated rollback (see [rollback-and-recovery.md](./rollback-and-recovery.md)) is a gamble, not a practice.

## Stage Gates and Their Failure Modes

| Gate type | Example | Failure mode |
|-----------|---------|--------------|
| Compile/build | Hermetic build succeeds | Build machine state leaks in (non-hermetic) |
| Unit/integration tests | Suites run on the artifact | Flaky tests → gate ignored or rerun into green |
| Security scans | SAST, dependency/CVE scan, SBOM check | Scans run on a *different* artifact than the one shipped |
| Performance check | Peak-load + margin benchmark on staging | Staging capacity ≠ production capacity → false pass |
| Approval | Human sign-off to promote | Approval without evidence; CAB delay (see below) |
| Post-deploy verification | Canary metrics, smoke tests | Verification watches the wrong SLIs or no SLIs |

The meta-failure mode is **gate erosion**: when a gate blocks frequently for reasons engineers believe are spurious, teams start bypassing it (hotfix overrides, force-promote), and the gate becomes theater. Fix the gate's false positives rather than adding more gates on top. A gate you cannot trust should be deleted; an untrusted gate that stays is worse than none, because it trains the org to ignore gates.

## The Evidence on Approval Gates (CABs)

The empirical case against heavyweight human approval is one of the strongest findings in the delivery literature (Accelerate / 2019 State of DevOps, via Forsgren et al.):

- External approval (Change Advisory Board or manager sign-off) is **negatively correlated** with lead time, deployment frequency, and restore time.
- It has **no correlation** with change-failure rate — approval does not make releases safer.
- The research describes heavyweight approval as "worse than no approval process": it slows delivery without improving stability.

The recommended replacement is **lightweight peer review** (pair programming or intra-team code review) **combined with a deployment pipeline that detects and rejects bad changes**. The pipeline is the enforcement mechanism; the review is the quality input. For teams under audit pressure, the pipeline *also* produces better evidence than a CAB minute ever did — immutable, timestamped, and linked (see [change-governance-and-compliance.md](./change-governance-and-compliance.md)).

> **Gotcha — "one more sign-off" as a risk control:** Adding an approver does not reduce change-failure rate — the Accelerate data says so directly. If a release keeps failing, add automated gates and smaller batches, not another approval step.

## Pipeline-as-Code

The pipeline definition itself must be versioned, reviewed, and tested like production code:

- **Versioned:** pipeline YAML/Starlark lives in the source repo, so a release's pipeline is reproducible from history — and a changed pipeline is diffable in review.
- **Reviewed:** pipeline changes go through the same PR review as application code — a pipeline edit is a production change, because the pipeline is what reaches production.
- **Tested:** exercise the pipeline on a branch/PR environment before it runs on `main`; validate inputs (secrets, parameters) rather than assuming them.
- **Auditable:** pipeline runs emit structured events (start/end timestamps per stage, commit SHA, artifact digest, stage result) that feed dashboards and postmortems. Without these events, "what did we deploy when and why" is tribal knowledge.

## Hermetic Builds

A **hermetic build** produces a byte-for-byte reproducible artifact whose output depends only on declared inputs — not on the build machine, the time of day, or what happens to be in a package registry. Hermeticity is what makes build-once meaningful:

- **Determinism:** the same commit always yields the same artifact; no "works on my machine" drift.
- **Trust:** no surprise dependency fetched at build time (see [supply-chain-security.md](./supply-chain-security.md)).
- **Rollback safety:** a prior artifact can be reproduced exactly if needed (see [rollback-and-recovery.md](./rollback-and-recovery.md)).
- **Auditability:** you know exactly what went into an artifact because the build environment is pinned.

Practical steps: pin toolchains and base images (digest references, not tags); vendor or mirror dependencies behind an internal registry with lockfiles and hashes; disable network access during builds (sandbox or `--network none`); use content-addressable build tools (Bazel, Nix) where feasible. The tradeoff is real — dependency mirroring and build infrastructure are overhead — but it buys determinism, cacheability, and supply-chain guarantees that no test suite can provide.

## The Self-Service Model

Google's release-engineering philosophy (SRE Book ch. 8) names four principles that the pipeline should embody:

1. **Self-service** — teams control their own release cadence through the pipeline; no ticket to a central release team.
2. **High velocity** — frequent releases with fewer changes per version (small batches).
3. **Hermetic builds** — reproducible artifacts isolated from host environment.
4. **Enforcement of policies** — the platform gates operations (approve code, create release, deploy) so safety does not depend on human memory.

The pipeline is the enforcement point: roles and policies live in the platform (who can trigger, promote, approve, override), not in a checklist. If an engineer must ask "how do I release this service?", the self-service model has failed — the answer should be a documented command or CI trigger (see [role-and-career.md](./role-and-career.md) for how this shapes the RE role).

## The Hotfix and Emergency Path

Emergencies should not invent a parallel process; they should use a **faster version of the same pipeline**. The recommended model (GoCD, and consistent with Google's release engineering) is a hotfix path that is structurally identical to the production pipeline but *fetches the artifact earlier* — skipping the full promotion ladder — and is kept paused behind strict trigger controls, so it cannot be used casually:

1. Severity justifies an emergency change (SEV-1, active security vulnerability).
2. Emergency change ticket created — abbreviated but auditable.
3. Required approvals obtained via a break-glass path (senior approval, documented; see [change-governance-and-compliance.md](./change-governance-and-compliance.md)).
4. Hotfix branch cut from the production tag; minimal cherry-picked fix.
5. Automated smoke tests + targeted regression on the exact candidate.
6. Deploy to a canary subset, monitor, then full rollout — same gates as any release.
7. Post-implementation review within a bounded window; retroactive full documentation.

The key discipline: **if the pipeline is fast enough, prefer committing the fix through the whole pipeline** so it is fully tested, and spend the postmortem on *how a bad build reached production* rather than on the hotfix mechanics. A hotfix path that is faster but less tested is a standing invitation to skip quality exactly when the stakes are highest.

## Config Strategy in the Pipeline

Configuration is the most common source of production incidents after the code itself, and its treatment in the pipeline is a design decision:

| Strategy | Description | Strengths | Weaknesses | Best for |
|----------|-------------|-----------|------------|----------|
| **Mainline** | Config lives in the app repo and ships inside the artifact | Atomic deploys; version correlation is trivial | Any config change requires a rebuild; cannot toggle independently | Small services |
| **Bundled defaults + runtime overrides** | Artifact carries safe defaults; per-env overrides applied at deploy | Safe-start; env differences explicit | Merge logic for defaults + overrides | Most services |
| **Config-only packages** | Config is its own versioned, promoted artifact | Config promotes/rolls back without redeploying code | Config/code version skew needs management | Large services with frequent config changes |
| **External stores** | Config served at runtime (Consul, etcd, parameter store) | Real-time changes; fine-grained access control; audit logging | Runtime dependency; startup latency; misconfiguration cascades | Multi-service systems, global flags |

The layered recommendation: **bundled defaults inside the artifact, environment overrides in a versioned config artifact or external store, runtime toggles in a feature-flag system.** Whichever strategy you choose, version and review config like code, and snapshot config alongside binaries by build ID so the running binary and its config are always a matched pair — the direct defense against config drift.

## Environment Parity and Config Drift

Staging and pre-prod should mirror production as closely as feasible — same artifact, same config schema, same deployment mechanism. The SRE Workbook is blunt that test environments are **never 100% identical to production**, which is exactly why canarying in real traffic is needed (see [progressive-delivery.md](./progressive-delivery.md)). But parity gaps are also a recurring source of prod-only defects, so name and manage them deliberately:

| Parity dimension | Typical gap | Mitigation |
|------------------|-------------|------------|
| Data | Staging has fake/masked/anonymized data | Refresh from production snapshots (with compliance guards); seed realistic volumes |
| Capacity | Staging runs a fraction of prod capacity | Load-test at prod scale or document the scaling delta |
| Config | Staging config hand-edited, prod config differs | Config as versioned artifacts promoted alongside binaries; drift detection (GitOps reconcile) |
| Dependencies | Staging talks to different upstreams | Same registry/versions; record dependency versions per environment |

**Config drift** — config and binary falling out of sync — is a classic incident cause. Google versions config in VCS with code review and snapshots config *alongside* binaries by build ID, so the running binary and its config are always a matched pair. Treat config as an artifact with the same promotion rules as code: versioned, reviewed, promoted, and rollback-able.

## The Pipeline and Delivery Metrics

The pipeline is also the **measurement instrument** for delivery performance. The five DORA metrics (see [metrics-and-dora.md](./metrics-and-dora.md)) are all derivable from pipeline telemetry — if the pipeline emits it:

- **Deployment frequency** — successful production deploys per time period, from deploy events.
- **Change lead time** — commit timestamp to production deploy, from commit + deploy events.
- **Change-failure rate** — deploys needing immediate remediation, from failed/rolled-back deploy events.
- **Failed deployment recovery time** — failed deploy to next successful deploy, from deploy events.
- **Deployment rework rate** — unplanned deploys caused by a production incident, from incident-linked deploy events.

Design implication: every stage should emit structured events (start/end timestamps, commit SHA, artifact digest, stage result, environment) so the pipeline is not just a delivery mechanism but a source of evidence — for DORA, for audits, and for postmortems. A pipeline that produces no records produces no metrics and no audit trail, no matter how green it looks.

## Secrets and Credentials in the Pipeline

The pipeline holds the keys to production; treat its credentials as a first-class risk surface:

- **Never bake secrets into artifacts.** Secrets are injected at deploy time from a secrets manager (Vault, cloud parameter store), scoped to the environment.
- **Short-lived, least-privilege credentials.** Pipeline credentials with 15-minute expirations and the minimum scope for their stage; a leaked long-lived deploy token is a standing compromise.
- **Separation of duties at the stage level.** Build, promote, and deploy should have distinct authorization — the identity that builds is not the identity that deploys, and neither is the identity that approves (see [change-governance-and-compliance.md](./change-governance-and-compliance.md)).
- **Audit secret access.** Who read which secret, when, from what context — because a pipeline that touches secrets without logging them is a pipeline whose compromise you will never detect.

Supply-chain hygiene (artifact signing, SBOM, provenance) is the other half of this surface; see [supply-chain-security.md](./supply-chain-security.md).

## Limits of the Pipeline

A green pipeline is necessary, not sufficient — it enforces *process*, not *product quality*:

- Tests that assert nothing, or assert the wrong thing, pass green while shipping broken features.
- Requirements errors sail through every gate; the pipeline cannot detect that you built the wrong thing.
- A pipeline cannot fix missing ownership (no on-call, no accountable team) or architectural problems (a service that cannot be deployed independently).

The corollary is positive: because the pipeline *can* enforce process reliably, reserve human attention for what it cannot — verification methodology, code review quality, pre-mortems, and the readiness judgments described in [readiness-and-quality-gates.md](./readiness-and-quality-gates.md). Treat "the pipeline is green" as the floor, not the ceiling.

## Gotchas

> **Gotcha — rebuilding per environment:** The most common pipeline sin. "Production build differs because we set flags at build time" means production runs untested bits. Environment differences belong in *config*, injected at deploy time, never compiled in.

> **Gotcha — green-check theater:** A stage that passes but asserts nothing (a test suite with no assertions, a smoke check that only verifies HTTP 200) looks safe and protects nothing. Validate gates by deliberately breaking them in a rehearsal.

> **Gotcha — flaky-test erosion:** When a suite reruns "until green," the gate is lying. Track rerun rate; a gate that needs retries is a queue of future prod incidents.

> **Gotcha — CI vs CD confusion in metrics:** Pipeline run counts are not deployment frequency; PR merges are not deploys. Measure the metric you actually care about (deployments to production), or your DORA dashboard will flatter you (see [metrics-and-dora.md](./metrics-and-dora.md)).

> **Gotcha — pipeline-as-code not reviewed:** The most privileged code in your system is the pipeline that deploys to production. A compromised or sloppy pipeline definition is worse than a bad app commit. Review it, sign it, audit it.

> **Gotcha — one pipeline, no selection:** If every green build auto-deploys but the org cannot actually absorb that cadence (support, on-call, capacity), push-on-green produces chaos, not velocity. The cadence must match the org's ability to verify and recover.

## Sources and Further Reading

- [Martin Fowler — Continuous Delivery (bliki)](https://martinfowler.com/bliki/ContinuousDelivery.html)
- [Google SRE Book — Release Engineering (ch. 8)](https://sre.google/sre-book/release-engineering/)
- [Google SRE Workbook — Canarying Releases (ch. 16)](https://sre.google/workbook/canarying-releases/)
- [Software Engineering at Google — Continuous Delivery (ch. 24)](https://abseil.io/resources/swe-book/html/ch24.html)
- [Harness — Is a Change Advisory Board Really Needed? (Accelerate evidence)](https://www.harness.io/blog/change-advisory-board-really-needed)
- [DORA — The DORA Metrics guide](https://dora.dev/guides/dora-metrics/)
- [Continuous Delivery: Reliable Software Releases through Build, Test, and Deployment Automation (Humble & Farley)](https://www.oreilly.com/library/view/continuous-delivery-reliable/9780321670250/)
