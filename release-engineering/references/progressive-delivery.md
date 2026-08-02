# Progressive Delivery

**Progressive delivery** — the term was coined by RedMonk's James Governor around 2018 — is the practice of **decoupling deploy from release**: putting a change into an environment is not the same event as exposing it to users. Deployment becomes a gradual, measured, automatically-evaluated process: you expose a change to a fraction of users or traffic, check that the world is still healthy, then expose more. It wraps canaries, blue/green, rings, feature flags, and A/B testing into one disciplined approach, and it is the primary way modern teams make high deployment frequency compatible with low change-failure rate.

## Decouple Deploy from Release

The single most useful mental model in release engineering:

| Event | Question it answers | Mechanism |
|-------|--------------------|-----------|
| **Deploy** | Is the new version running in the environment? | Pipeline, rollout tooling |
| **Release** | Do users see the new behavior? | Feature flags, traffic routing, store review approval |

Once these are separated, an incomplete or risky change can sit in production dormant (**dark launch**), be shown to a tiny cohort, or be turned off in seconds without any redeploy. This separation is the escape hatch that makes release trains, freezes, and calendar schedules compatible with continuous deployment (see [release-process-models.md](./release-process-models.md) and [feature-flag-lifecycle.md](./feature-flag-lifecycle.md)). It is also the answer to the oldest release dilemma — "the feature is on the train but not ready" — because readiness is now a property of *exposure*, not of *presence*.

## Canary Releases

A **canary release** deploys a new version to a small, time-limited subset of traffic ("canary") while a "control" population stays on the old version, evaluates the canary against the control, and only then proceeds to full rollout. The Google SRE Workbook (ch. 16) is the canonical treatment; its core principles:

- **Canarying conserves the error budget.** Impact scales with exposed traffic: a 5% canary running at a 20% error rate costs roughly 1% of overall error budget. The budget cost of a defective rollout is proportional to the fraction of traffic exposed to the defect — which is precisely why you expose a small fraction first, and why canary analysis can afford to be aggressive: rolling back a 5% canary costs the budget almost nothing.
- **Run one canary at a time.** Concurrent canaries confound attribution — you cannot tell which change caused which effect.
- **Size and duration must be representative.** The canary needs enough traffic volume for statistical significance, and it should span peak-load and time-of-day variation, not just a quiet hour. A canary that runs only off-peak is blind to the failures that matter.
- **Prefer SLI-derived metrics** (HTTP status codes, latency — user-perceivable signals) over noisy resource metrics (CPU, memory), which tend to be ignored or disabled by operators.
- **Compare canary vs. control, never before/after.** Time-based comparison is confounded — the deploy coincides with other events. Concurrent A/B comparison of the canary population against a control population isolates the change.
- **Metrics must be attributable** — isolatable from shared failure domains so a database outage elsewhere does not look like a canary failure.
- **Metric aggregation windows must be ≤ the canary duration**, or the canary ends before the signal resolves.

**Exponential ramp:** Google's production rollouts expand the canary in exponential steps (e.g., 1% → 10% → 50% → 100%, or cluster-by-cluster expansion) with verification between steps. The Rapid rollout system evaluates each step against the service's error budget before proceeding — a step that burns budget pauses the ramp and rolls back rather than continuing blind. This "measure, then expand" loop is the difference between progressive delivery and merely slow delivery.

### Canary analysis in practice

A workable canary procedure, synthesized from the SRE Workbook:

1. **Select SLIs** — a stack-ranked handful of user-perceivable signals (error rate, latency percentiles); no more than ~a dozen, and avoid noisy resource metrics.
2. **Size the canary** — enough traffic for the SLI delta you care about to be statistically detectable within the observation window; account for peak and off-peak variation.
3. **Guarantee attribution** — isolate shared failure domains; label metrics by release version so canary and control are separable.
4. **Run canary vs. control concurrently** — never before/after; ensure aggregation windows are ≤ the canary duration.
5. **Evaluate** — divergence beyond threshold → pause and roll back (or page); healthy → proceed.
6. **Ramp exponentially** — 1% → 10% → 50% → 100% (or cluster-by-cluster), re-evaluating after each step.
7. **Record the verdict** — the canary decision becomes part of the release's audit trail: which SLIs, what delta, what decision.

This is the loop that makes progressive delivery a *safety mechanism* rather than a scheduling preference. See [rollback-and-recovery.md](./rollback-and-recovery.md) for the automatic-rollback side of the loop.

## Blue/Green Deployments

**Blue/green** maintains two full environments — the current (blue) and the candidate (green). Deployment runs green in parallel; release is a router change that cuts traffic from blue to green; rollback is the trivial reversal of that router change. The cost is roughly **2× resources**, and unless both environments run concurrently with split traffic, blue/green is effectively a before/after canary — with the same time-confound risk.

| | Canary | Blue/green |
|---|--------|------------|
| Environments | One, mixed versions | Two full environments |
| Rollback speed | Traffic shift back | Router reversal (seconds) |
| Resource cost | ~1x + canary capacity | ~2× |
| Best for | Continuous delivery, most services | Big-bang migrations, stateful cutovers needing instant revert |

Blue/green shines where instant, whole-stack revert matters more than cost — e.g., a database cutover or a compliance-critical platform where the alternative (re-deploying the old stack) is slower than flipping the router back. Its weakness is the 2× resource bill and the temptation to treat it as a substitute for measurement: the switch is fast, but you still need the same SLI evaluation to know *whether* to switch.

## Ring and Cohort Rollouts

**Ring deployments** roll out to ordered, concentric populations: internal/dogfood first, then early adopters, then broad. **Microsoft's Insider model** is the canonical example — Windows Insider channels (Dev / Beta / Release Preview) and M365 Targeted Release let Microsoft expose builds to progressively larger, more tolerant cohorts before general availability, with enterprise "deployment rings" used for Windows updates. **iOS phased release** is effectively a two-ring model: a small percentage of users first, pausable before broad exposure.

| Ring | Population | Tolerance | Catches |
|------|-----------|-----------|---------|
| Internal/dogfood | Employees, insiders | High — they expect bugs | Integration, internal tooling, gross breakage |
| Early adopters | Beta/preview users | Medium | Real-world hardware/OS/browser diversity |
| Broad | General availability | Low | Long-tail compatibility, scale effects |

The **employee-first cohort** pattern — Meta/Facebook, Google, and LinkedIn have historically rolled changes to their own employees first — is a ring with the most forgiving population. It catches internal-tooling and culture problems early but cannot detect problems only external users hit (browser diversity, third-party integrations, hostile traffic), so employee rings are a complement to, not a substitute for, canary analysis. Rings organize *who* sees the change; canaries measure *how it behaves*.

### Rings vs canaries

| Aspect | Rings | Canaries |
|--------|-------|----------|
| Organizes | Populations, ordered by tolerance | Traffic samples vs. control |
| Cadence | Days–weeks per ring | Minutes–hours per step |
| Question | "Is this population ready for the next ring?" | "Is this version healthy?" |
| Best combined as | The rollout *shape* | The *gate* between steps |

The two compose: roll out in rings, and run a canary analysis inside each ring before expanding to the next. **Choosing ring membership** is itself a decision: order populations from most to least tolerant (internal → beta → new users → existing users → highest-value/least-tolerant last), define explicit exit criteria per ring, and treat "the ring passed" as a metric-backed claim, not a schedule event.

## Percentage Rollouts

A **percentage rollout** incrementally raises the exposed fraction (1% → 5% → 25% → 100%), typically gated on metric health between steps. It is the simplest progressive-delivery mechanism and pairs naturally with feature flags (percentage of users) or traffic routing (percentage of requests). The gate between steps is what makes it progressive rather than just "slow": each step waits for confirmation that the previous step is healthy before expanding. A percentage rollout with no metric gate and a fixed timer is neither fish nor fowl — it does not protect you, it just delays you.

**Sizing the steps:** steps should be small where risk is high and larger where confidence is high — the common shape is roughly logarithmic (1 → 5 → 25 → 100). The step increment is a bet: each step's blast radius should be smaller than the error budget it is allowed to consume, so even a bad step costs little (see [readiness-and-quality-gates.md](./readiness-and-quality-gates.md) for the budget connection).

## Traffic Shadowing

**Traffic shadowing (teeing)** copies live traffic to the candidate version while discarding its responses, so the candidate is exercised with real production load and inputs without any user impact. It is representative and safe for *stateless* systems, but the SRE Workbook warns it is **unreliable for stateful systems** — shared caches and databases can be skewed by the shadow copy, producing results that do not reflect real behavior. Synthetic load has the complementary problem: it "doesn't provide good state coverage" and can be outright dangerous on a billing system. Use shadowing as a rehearsal step, not as a final gate.

## Metric-Gated Progression and Automatic Rollback

Progressive delivery without automated evaluation is just slow delivery. The SRE Workbook's prescription: gate progression on a **stack-ranked set of a few SLIs (no more than ~a dozen)**, comparing canary and control populations; if the canary metric diverges too far from control, **pause and roll back the deployment, or page a human**. The canary analysis must:

- compare populations (canary vs. control), never before/after;
- use intervals ≤ canary duration;
- be attributable to the change under test;
- map to user-perceivable SLIs.

When the gate is wired to an automatic rollback, the pipeline itself becomes the safety net: a bad canary is detected and reverted in minutes without a human noticing first. This is the operational heart of "rollbacks are normal" (see [rollback-and-recovery.md](./rollback-and-recovery.md)). The automatic trigger is sized by the error budget — because a small canary costs little budget, aggressive auto-rollback at canary tier is nearly free insurance.

## Dark Launches and Feature Flags

A **dark launch** deploys code that is inert until toggled: the code path exists in production but is unreachable by users. Combined with **feature flags**, it gives you the full control surface for progressive delivery — percentage of users, targeted cohorts, gradual enablement, and a sub-second kill switch. The flag is what makes "deploy anytime, release when ready" actually true: the deploy and the release are separated by a remote-config decision, not by another release cycle.

Flags are foundational enough that most teams buy them (LaunchDarkly, Flagsmith, Split/Harness, Unleash) rather than build them, and the ecosystem is standardizing around OpenFeature. But flags are also an operational liability when unmanaged: every flag is a decision surface, and flags left in place become permanent ambient state (see [feature-flag-lifecycle.md](./feature-flag-lifecycle.md) for the full lifecycle — including the Knight Capital-style costs of unmanaged toggles). The discipline: name flags for their purpose, assign ownership and expiry, test both states, and remove flags once the rollout completes.

## A/B Testing in Production

**A/B testing** compares business-metric outcomes between exposed and unexposed cohorts — a statistically rigorous experiment layered on top of progressive delivery. The distinction from canarying matters:

| | Canary | A/B test |
|---|--------|----------|
| Question | Is the new version *reliable*? | Does the change *improve outcomes*? |
| Metrics | SLIs (error rate, latency) | Business metrics (conversion, engagement, revenue) |
| Decision | Roll out further or roll back | Keep, revert, or iterate the feature |
| Duration | Minutes-hours | Days-weeks (statistical power) |

Booking.com's experimentation platform automatically detects and reverts a bad change in **~1 second** (Lukas Vermeer) — the canonical example of automated, metric-driven rollback at scale. Walmart's **"Test to Launch"** makes progressive, experiment-gated release the default path to production. Netflix pairs automated canary analysis with experimentation across its fleet. The pattern: pre-register the metric and threshold, let the platform decide, and keep the human out of the per-step judgment call. A/B testing also requires the discipline that canarying does — attributable cohorts, adequate sample size, pre-registered metrics — plus patience: business metrics resolve more slowly than SLIs.

## Field Examples

| Company | Practice | Takeaway |
|---------|----------|----------|
| **Google** | Rapid/Sisyphus rollout system: exponential cluster expansion, canary vs. control evaluation, MPM package labels `dev`/`canary`/`production` | Canary analysis at platform scale, error-budget-conserving ramps |
| **Booking.com** | A/B/experimentation platform with automatic detect-and-revert of a bad change in ~1 second (Lukas Vermeer) | Automated experiment evaluation can revert faster than any human process |
| **Walmart** | "Test to Launch" — progressive exposure tied to automated verification | Retail-scale progressive rollout as the default release path |
| **Netflix** | Automated canary analysis (Kayenta), chaos engineering alongside progressive rollout | Machine-judged canary gates on large fleets |
| **Meta / LinkedIn** | Employee-first cohorts, flag-gated (Gatekeeper-style) rollout | Ring populations ordered by tolerance |

The pattern across all of them: **expose a little, measure against a control, expand on health, revert automatically on divergence.** The specific mechanism matters less than the loop.

## When Not to Use Progressive Delivery

Progressive delivery is not free, and it is not always applicable:

- **When you cannot measure.** A canary gate without SLIs is fiction. If the service has no observability worth the name, fix that first — progressive delivery *requires* a signal to gate on.
- **When cohort isolation is impossible.** If canary and control share state so tightly that attribution is meaningless (e.g., a single shared cache dominating behavior), canary analysis will produce noise. Flags may still work; canary analysis may not.
- **When regulation requires full validation before any exposure.** Certifiable systems (aviation, medical devices) may not legally expose unvalidated builds to any population, however small. There, "validation" happens before deployment, and the rollout shape is dictated by the regulator, not the SLI.
- **When user consent and ethics demand guardrails.** Experiments on users (A/B testing) carry consent and fairness obligations: pre-registered metrics, opt-outs, and limits on who can be assigned to a worse experience.
- **When the change cannot fail.** A documentation-only change or a no-op refactor with zero user-visible risk does not need a canary. Ceremony should track risk; adding ceremony where risk is absent just taxes velocity.

## Choosing a Strategy

The decision axes are **speed of rollout, safety (blast radius of a bad change), rollback time, and complexity/cost**:

| Strategy | Speed | Blast radius at step 1 | Rollback time | Complexity/cost | Default when ... |
|----------|-------|------------------------|---------------|-----------------|------------------|
| Canary (metric-gated) | Minutes-hours | Small fraction of traffic | Minutes | Medium | General-purpose stateless services |
| Blue/green | Seconds (switch) | Full stack at switch | Seconds | 2× resources | Instant whole-stack revert matters |
| Ring/cohort | Days-weeks | Bounded population | Medium | Medium | User-base segmentation (devices, regions, customers) |
| Feature flag | Real-time | Zero (dormant) | Sub-second | Low | Change can be toggled independently of deploy |
| Shadowing | Pre-release | Zero (discarded) | n/a | Medium | Rehearsal of stateless services |
| Percentage | Minutes-hours | Small % of users | Minutes | Low | Simplest option; pairs with flags or routing |

A canary with metric gates is the general-purpose default for stateless services; blue/green wins where instant revert matters more than cost; rings fit user-base segmentation; flags fit anything where the change can be switched on/off independently of deploy; shadowing fits pre-release rehearsal of stateless services. See the [deployment-strategy-matrix](../assets/deployment-strategy-matrix.md) for a side-by-side comparison across these axes.

## A Maturity Ladder

Progressive delivery is a capability you build incrementally, not a binary state. A useful ladder:

1. **Big-bang deploy, human verification** — full rollout; humans notice problems after.
2. **Controlled switch** — blue/green with a manual router flip; rollback is trivial but judgment is human.
3. **Progressive, gated** — canary/rings/percentages with metric gates between steps; humans review the gates.
4. **Automated** — automatic rollback wired to canary analysis; the pipeline enforces the loop without a human in the per-step path.
5. **Self-tuning** — experimentation platform (A/B, automated decisioning); the system decides both reliability and business outcomes.

Most teams should climb deliberately: each rung requires the instrumentation of the previous one (SLIs before gates, gates before automation). Jumping straight to automation without trustworthy SLIs just automates blindness.

## Gotchas

> **Gotcha — canary sized for convenience, not significance:** A 1% canary on a low-traffic service may need days to accumulate signal. Size the canary so the SLI delta you care about is statistically detectable within the observation window, or you will be making decisions on noise.

> **Gotcha — before/after comparisons:** Deploys never happen in a vacuum. Comparing the week before the deploy to the week after attributes unrelated events (marketing pushes, dependency outages) to your change. Always compare concurrent canary vs. control where possible.

> **Gotcha — metrics that cannot be attributed:** If the canary and control share a cache, a database, or a downstream dependency, a shared failure looks like a canary failure. Isolate failure domains before relying on the signal.

> **Gotcha — aggregation window longer than the canary:** The canary ends before the metric resolves, so decisions are made blind. Metric resolution must be faster than rollout steps.

> **Gotcha — shadowing stateful systems:** Teeing traffic into a candidate that writes to shared state corrupts the experiment and can corrupt production data. Restrict shadowing to stateless rehearsal.

> **Gotcha — percentage rollouts without gates:** Raising exposure on a timer rather than on metric health is slow rollout, not progressive delivery. It buys delay without safety.

> **Gotcha — flags as permanent crutches:** Feature flags are the fastest rollback lever, but flags that are never removed become an unmaintained decision surface with its own failure modes. Every flag needs an owner, an expiry, and a cleanup plan (see [feature-flag-lifecycle.md](./feature-flag-lifecycle.md)).

> **Gotcha — canary only at happy hour:** A canary that runs only during quiet hours will miss the load-dependent failures that matter. If you cannot canary across peak traffic, at least size the exposure so the off-peak canary is *statistically meaningful* — and say explicitly which failure modes you are not covering.

## Sources and Further Reading

- [Google SRE Workbook — Canarying Releases (ch. 16)](https://sre.google/workbook/canarying-releases/)
- [Google SRE Book — Release Engineering (ch. 8)](https://sre.google/sre-book/release-engineering/)
- [Google SRE Book — Reliable Product Launches (ch. 27)](https://sre.google/sre-book/reliable-product-launches/)
- [Microsoft Tech Community — Tactical Considerations for Creating Windows Deployment Rings](https://techcommunity.microsoft.com/blog/windows-itpro-blog/tactical-considerations-for-creating-windows-deployment-rings/)
- [Microsoft Windows Insider Blog — Introducing Windows Insider Channels](https://blogs.windows.com/windows-insider/2020/06/15/introducing-windows-insider-channels/)
- [Flagsmith — Progressive Delivery with Feature Flags](https://www.flagsmith.com/blog/progressive-delivery)
- [Martin Fowler — Parallel Change](https://martinfowler.com/bliki/ParallelChange.html)
