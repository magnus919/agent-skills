# Release Readiness and Quality Gates

A release is not "done" when the code is written; it is done when it is **deployed to production and validated there**. Release readiness is the disciplined answer to "what has to be true before we ship?" — organized so that every requirement has a named owner, an evidence trail, and a gate that actually blocks. The point of a readiness model is not bureaucracy; it is making the implicit explicit before a launch, when a problem costs 100× what it would cost to fix in design.

## Release Readiness as Four Dimensions

Readiness decomposes into four dimensions. Every item in every dimension needs a **named owner** — a person, never a team — plus an evidence link that an auditor (or a skeptical engineer) can check.

| Dimension | Typical items | Named owner example |
|-----------|---------------|---------------------|
| **Functional** | Acceptance tests pass on the *exact* release build; business owner UAT accepted; known defects risk-rated and explicitly accepted | Business/Product owner |
| **Non-functional** | Performance at peak + margin; security review (SAST, DAST, dependency scan); accessibility; resilience/graceful degradation | Engineering lead |
| **Operational** | Monitoring and alerting live *before* go-live; runbooks written and read by on-call; deployment rehearsed; rollback path tested (not assumed); on-call coverage window (24–72h) | Operations/SRE lead |
| **Governance** | Approval recorded (if required); audit artifacts linked (ticket → PR → CI → approval → deploy log → verification); segregation of duties; end-to-end traceability | Release/governance owner |

### A concrete checklist item looks like this

| Item | Owner | Evidence | Gate |
|------|-------|----------|------|
| Acceptance tests pass on exact RC | Product owner | CI run ID + artifact digest | Blocking |
| Performance at peak + margin | Engineering lead | Benchmark report on the RC | Blocking |
| Monitoring/alerting live before go-live | Ops lead | Alert dashboard URL + test page fired | Blocking |
| Rollback path tested (not assumed) | Ops lead | Rehearsal log / game-day record | Blocking |
| Approval recorded + traceability chain | Release owner | Change record with links | Blocking |
| Known defect #42 accepted | Product owner | Risk note + sign-off | Non-blocking |

The format matters as much as the content: each row names a person, points at evidence, and states whether it blocks. Rows without an owner or evidence are how "the checklist passed but the release failed" happens.

> **Gotcha — checklist without owners:** A readiness checklist with checkboxes but no names is theater: "done" means "somebody, somewhere, at some point." Every line item should name the individual who attests to it and link the evidence that backs the attestation.

### The Google Launch Coordination ancestry

The four dimensions map to the launch-coordination structure Google SRE formalizes (SRE Book ch. 27 and the Launch Checklist), which is worth keeping in mind for large launches:

| Launch Checklist area | Maps to dimension |
|-----------------------|-------------------|
| Architecture; failure modes; client behavior | Functional |
| Volume/capacity/performance; security; growth | Non-functional |
| Monitoring; automation & manual tasks; system reliability & failover; rollout plan | Operational |
| External dependencies; schedule; launch processes; sign-offs | Governance |

Google's model adds the launch-coordination view: a named Launch Coordinator, a pre-mortem-style risk review, and kill switches designed in from the start (see [progressive-delivery.md](./progressive-delivery.md)). You can keep the SRE framing for big launches and the four-dimension model for routine releases; the owner-and-evidence discipline is what survives both.

## Release Candidates

A **release candidate (RC)** is a promoted build explicitly labeled as a candidate for release. The label is not cosmetic: it marks the exact artifact whose tests, review, and verification evidence apply, and it is the thing a rollback returns to.

Google's model is instructive: packages are labeled `dev`, `canary`, and `production`, with movable labels pointing at immutable, content-hashed, signed versions. Google also **re-runs unit tests on the release branch** to create an audit trail, because a cherry-picked release branch may contain commits that never existed on mainline — testing only `main` would leave the shipped artifact's exact content unverified. For any release cut from a branch (see [release-process-models.md](./release-process-models.md)), re-verify the branch content itself.

> **Gotcha — testing the wrong build:** Readiness evidence that does not reference the exact artifact digest (SHA, version) being released is worthless. A release plan that says "tests pass" without pinning the build has no way to prove the tested build is the shipped build.

## Staging Parity and Smoke Tests

**Staging parity** is the pursuit of making staging and pre-prod mirror production as closely as feasible — same artifact, same config schema, same deploy mechanism, realistic data and scale. Parity is never perfect (the SRE Workbook states plainly that test environments are not 100% identical to production — which is *why* canarying in real traffic exists, see [progressive-delivery.md](./progressive-delivery.md)). The discipline is to name and manage the gaps: document the capacity delta, refresh data from production with compliance guards, and record dependency versions per environment. Unnamed parity gaps are a recurring source of prod-only defects; named gaps can be weighed, tested around, and closed.

**Smoke tests** are lightweight post-deploy verification that critical paths work — black-box probes (e.g., "the service answers at this URL," "the checkout flow completes") that complement canary metrics. Their value is isolating the canary signal from odd user behavior: a black-box probe exercises a known path deterministically, so a smoke-test failure is a deployment failure, not an artifact of user mix. Smoke tests should be fast, fail loudly, and run in every environment the artifact promotes through — including production immediately after deploy.

## Observability and Error-Budget Gates

The strongest release gate is the production system's own health. Gate promotion on **SLIs** (error rate, latency) and on **error-budget health** — not on test-passing alone, because tests encode your assumptions and production encodes reality.

Google's example **error-budget policy** (SRE Workbook Appendix B) is the template:

- If a service exceeds its **4-week error budget**, **halt all non-P0/security releases** for that service until it is back within SLO.
- A single incident that consumes **>20% of the budget** triggers a postmortem with a P0 action item.
- The policy is justified partly because **~70% of outages are change-induced** — the thing most likely to break a service is a release, so gating releases on reliability health is gating on the actual risk.

Error-budget gates integrate naturally with progressive delivery: the canary's allowed impact is sized by the budget (a 5% canary at 20% error costs ~1% overall), and exceeding the budget halts further promotion. The gate is only as good as the SLI selection behind it — stack-rank a small set of user-perceivable SLIs and feed them into both the canary analysis and the release gate (see [progressive-delivery.md](./progressive-delivery.md)). The error budget is also the objective arbiter between "we need to ship" and "the service is fragile": shipping during a budget burn is spending money you do not have.

## Go/No-Go

A **go/no-go** is a decision point: is this release, at this moment, cleared to proceed? Historically a meeting; in mature CD organizations it is increasingly automated or asynchronous.

**Structure when it is a meeting:**

1. Each dimension owner confirms their section — 30–60 seconds per owner, named individuals, not "the team."
2. The decision is recorded as **GO / NO-GO / GO-WITH-CONDITIONS**, with a timestamp.
3. Conditions have owners and deadlines; a GO-WITH-CONDITIONS is not a free pass — it is a tracked obligation.

**What survives in modern practice:** The ritual shrinks to an exception path. Routine deployments are covered by automated gates — dashboards, policy-as-code, error-budget checks, canary metrics — so the meeting becomes a review of *exceptions*, not a per-deploy ceremony. Asynchronous sign-off (recorded in the change record with evidence links) replaces the room for most releases. The questions that survive are the ones automation cannot answer: *Is the business risk of this launch acceptable? What known defects are we explicitly accepting? What is the customer-communication plan if it fails?*

**When a go/no-go meeting is still warranted:**

- **Compliance-driven releases** where auditors expect a documented approval decision per release (SOC 2, SOX, PCI; see [change-governance-and-compliance.md](./change-governance-and-compliance.md)).
- **Release trains** where a cross-team launch (or rollback) is coordinated on a calendar, and one team's no-go affects the train (see [release-process-models.md](./release-process-models.md)).
- **High-risk, high-blast-radius launches** (billing changes, data migrations, security boundaries) where the cost of being wrong justifies a human checkpoint.

> **Gotcha — go/no-go as rubber stamp:** A meeting that meets, approves, and records nothing is worse than no meeting: it manufactures the appearance of control while adding latency. If the meeting's decisions are never revisited and its conditions are never tracked, automate it away.

## Post-Release Monitoring Window

Readiness does not end at the deploy; it extends through a **post-release monitoring window** (commonly 24–72 hours) during which the release is treated as unproven:

- On-call is explicitly aware a release just shipped and knows which SLIs to watch.
- The rollback runbook is open and rehearsed, not rediscovered (see [rollback-and-recovery.md](./rollback-and-recovery.md)).
- Monitoring compares post-release SLIs and business metrics against the pre-release baseline — the same metrics the canary covered, now at full exposure.
- A known-issue list tracks anything observed in the window, with owners and follow-up.

The window closes when the release has demonstrably held: no SLO violation, no metric regression, no incident. Until then, the release is still *in flight*, and anything discovered in the window is handled by the release's own gates — escalate, roll back, or hotfix — rather than as an unrelated incident. This is the operational completion of "definition of done": a release is done when the window closes, not when the deploy button was pressed.

## Readiness Evidence as Data

The readiness checklist earns its keep when it is **data, not prose**: a structured record (e.g., JSON) where every item carries an ID, dimension, named owner, evidence link, status, and whether it blocks. Machine-readable readiness buys three things:

- **Completeness is checkable.** CI can fail a promotion when a blocking item has no owner or no evidence — the checklist enforces itself instead of relying on a human to read it.
- **Evidence is attached, not remembered.** Each item links its proof (CI run ID, scan report, rehearsal log), which is exactly what an auditor or a skeptical reviewer wants (see [change-governance-and-compliance.md](./change-governance-and-compliance.md)).
- **Automation can consume it.** A data-driven checklist feeds the automated go/no-go (policy-as-code gates, error-budget checks) described below — the same criteria, evaluated by machine for routine releases and by humans for exceptions.

The template lives in the skill's `templates/` directory; the discipline is that the *record* — not the meeting — is the source of truth for "is this release ready?"

An example record for one item:

```json
{
  "id": "READ-004",
  "dimension": "operational",
  "item": "Rollback path tested on exact RC",
  "owner": "ops-lead@example.com",
  "evidence": "rehearsal://2026-08-01/payments-rc3",
  "status": "pass",
  "blocks": true
}
```

The gate consumes `status` and `blocks`: a blocking item without `pass` fails the promotion, regardless of how the meeting went.

## Automating the Go/No-Go

In mature CD organizations the go/no-go becomes **policy-as-code**: the criteria that humans used to recite are encoded as automated checks. Dashboards aggregate readiness evidence; pipeline gates evaluate it (see [cd-and-pipeline-stages.md](./cd-and-pipeline-stages.md)); error-budget checks produce an automatic no-go when the budget is burned (see [progressive-delivery.md](./progressive-delivery.md)). The human decision is then limited to what automation cannot answer — business risk acceptance, known-defect sign-off, customer communication — and is recorded asynchronously in the change record with evidence links.

The migration path is deliberate: start with the meeting, then *automate one criterion at a time*, and retire the meeting's agenda items as the checks absorb them. A go/no-go meeting whose entire agenda has been automated is a meeting in search of a purpose — dissolve it and keep the exception path (compliance, trains, high-risk launches) where a human decision genuinely adds value.

## Definition of Done

A release's **definition of done** should be stated explicitly and end in production:

| Stage | Done means |
|-------|-----------|
| Code complete | Merged to trunk, reviewed |
| Build verified | Hermetic build of the exact RC passes unit/integration/security gates |
| Pre-production | Staging deploy green; smoke tests pass; performance evidence recorded |
| Production deployed | Artifact promoted and running in prod |
| Production validated | Canary/metric gates pass; SLIs healthy for the observation window; on-call aware |

Anything less than "production validated" leaves the release in a liminal state — deployed but unverified — which is where post-release incidents start. Note that this definition of done deliberately does not say "QA complete" or "approval granted"; those are inputs, not outcomes. The outcome is a validated, observable production state.

## Readiness Scale: Routine vs Coordinated

Apply readiness in two regimes, and do not confuse them:

| Regime | Applies to | Shape |
|--------|-----------|-------|
| **Routine** | Every deploy in a CD org | Lightweight: automated gates (tests, security, smoke, canary SLIs) + evidence links; no meeting |
| **Coordinated** | Launches, release trains, compliance-gated releases, high-risk changes | Full: four-dimension checklist with named owners, pre-mortem, go/no-go, communication plan, post-release monitoring window |

The failure modes are symmetric: applying *coordinated* ceremony to every routine deploy regresses a CD org to monthly releases; applying *routine* lightness to a coordinated launch (a billing change, a data migration, a regulated release) ships without the checks that justify the risk. The disciplined practice is to define, per release type, which regime applies — and to let risk (blast radius, regulatory exposure, cross-team coordination) drive the classification, not habit.

## Risk-Rated Defect Acceptance

A mature readiness process does not require zero defects — it requires that **known defects be explicit, risk-rated, and accepted by a named owner**. The distinction is between two very different states:

- **Known and accepted:** defect #42 (an obscure settings-page edge case) is logged, risk-rated (probability × impact), assigned an owner, and explicitly signed off as acceptable for this release — visible to everyone.
- **Known and unexamined:** the same defect exists but was never rated or signed off — it ships silently and is discovered by a customer, an auditor, or an incident.

Risk-rated acceptance also covers the *deferral* case: a feature that is ready for deployment but not ready for release can ride the train dormant behind a flag (see [progressive-delivery.md](./progressive-delivery.md)) — that is a different decision from shipping a known defect to everyone. The readiness record should state which defects are accepted, which are deferred behind flags, and which blocked the release.

## The Pre-Mortem

For significant launches, add a **pre-mortem**: before the release, imagine it has failed in six months, and work backward to the plausible causes. Google's launch coordination institutionalized this kind of adversarial review; it complements the checklist by surfacing risks the checklist does not list — the failure mode nobody wrote down. The output is a short list of named risks with mitigations (and often a kill switch, see [progressive-delivery.md](./progressive-delivery.md)). A pre-mortem is cheap, runs in an hour, and consistently finds at least one risk the team had not articulated — which is precisely its point.

## Evidence Retention and the Audit Chain

Governance readiness is only as durable as its evidence chain. The chain is: **ticket → PR review → CI runs → approval → deploy log → verification** — each link timestamped and linked, so an auditor (or a postmortem) can walk a change end to end. SOC 2 Type II auditors sample roughly 25–50 changes and expect exactly this traceability; retention runs 1–7 years depending on regime (see [change-governance-and-compliance.md](./change-governance-and-compliance.md)).

The chain breaks in predictable ways — deleted branches, missing CI logs, manual deploys that leave no record, approvals recorded without evidence. Each break is a readiness defect: a release whose chain cannot be walked is a release whose governance was never demonstrated. Make the pipeline emit the links (see [cd-and-pipeline-stages.md](./cd-and-pipeline-stages.md)) and treat a broken chain as a blocking readiness item, not a bookkeeping annoyance.

**The go/no-go decision record** is itself evidence: decision (GO / NO-GO / GO-WITH-CONDITIONS), timestamp, attendees/approvers, each condition with owner and deadline, and a review date. A decision record that cannot be produced after the fact is a decision that never happened in audit terms.

## Gotchas

> **Gotcha — readiness as a point-in-time artifact:** Readiness rots. Evidence gathered two weeks before launch (performance runs, security scans) describes a build that may no longer be the candidate. Re-run evidence on the exact RC, and re-verify after any branch change.

> **Gotcha — unowned governance evidence:** In regulated environments, "the approval happened" without a timestamped, linked record is not evidence. The change record must chain ticket → PR review → CI runs → approval → deploy log → verification (see [change-governance-and-compliance.md](./change-governance-and-compliance.md)).

> **Gotcha — error-budget gates without teeth:** An error-budget policy that nobody enforces (halts ignored, overrides routine) teaches the org that gates are optional. If you cannot afford to halt releases during an error-budget burn, do not claim you have a policy — you have a wish.

> **Gotcha — smoke tests that only check "site is up":** A probe asserting HTTP 200 on the homepage protects nothing. Smoke the critical user journeys (login, search, checkout, payment), and fail the deploy on probe failure, not just alert.

> **Gotcha — readiness as a single release milestone:** In continuous delivery the "release" is a stream, not an event. Run lightweight readiness checks per deploy and heavyweight checks only for coordinated or compliance-driven launches; a heavyweight ritual on every deploy is how CD orgs regress to monthly releases.

## Sources and Further Reading

- [Google SRE Book — Reliable Product Launches (ch. 27)](https://sre.google/sre-book/reliable-product-launches/)
- [Google SRE Book — Launch Coordination Checklist (Appendix E)](https://sre.google/sre-book/launch-checklist/)
- [Google SRE Workbook — Error Budget Policy (Appendix B)](https://sre.google/workbook/error-budget-policy/)
- [Google SRE Workbook — Canarying Releases (ch. 16)](https://sre.google/workbook/canarying-releases/)
- [RNVATE — Release Readiness Checklist (four-dimension model)](https://rnvate.com/insights/release-readiness-checklist.html)
- [DORA — The DORA Metrics guide](https://dora.dev/guides/dora-metrics/)
