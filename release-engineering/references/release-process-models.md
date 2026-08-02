# Release Process Models

How a team branches, integrates, and cuts releases is the first structural decision in release engineering. The model you choose determines merge complexity, how defects flow toward production, whether a bad change can be isolated, and — per DORA's research — how fast and how stable your delivery actually is. The models below are not a menu of equal options: the evidence and the practitioner consensus point hard at trunk-based development for anything cloud-hosted, with the others surviving where constraints (packaged software, regulation, hardware) genuinely demand them.

## Trunk-Based Development — the Modern Default

**Trunk-based development (TBD)** means all developers collaborate on one long-lived branch (`main`/`trunk`). Feature branches are short-lived — ideally less than a day and holding a single developer's work — and exist only to carry a code review through CI before merging back. No long-lived feature or release branches are used for artifact creation. Incomplete work is hidden behind **feature flags** or **branch-by-abstraction**, never parked on a branch.

Why this matters (and why DORA evidence favors it):

| Effect | Mechanism |
|--------|-----------|
| Small batches | Merging to trunk daily forces small, reviewable increments; DORA correlates small batches with higher performance and lower failure impact |
| No merge hell | Conflicts are resolved continuously instead of accumulated for a big merge |
| One source of truth | Every deploy candidate comes from the same integrated line; no "is this fix on the branch?" archaeology |
| Fast feedback | Every change is integration-tested the moment it lands, not weeks later |

TBD is the default recommendation for cloud/SaaS teams that can automate build, test, and deploy, and that can use flags or branch-by-abstraction to decouple deploy from release. If you cannot merge to trunk at least daily, you are not really doing TBD — you are doing batched integration with a trunk-shaped label.

### Merge Queues

Under high PR volume, keeping `main` green is itself a bottleneck. **Merge queues** (GitHub merge queue, Graphite, Trunk.io) dynamically group ready PRs, run CI against the combined set, and only merge when the group passes — replacing fragile "rebase-and-retest" manual rituals. GitHub's own data is the reference point: its merge queue ships **2,500+ PRs/month into its monorepo from 500+ engineers**, and reduced average wait time by ~33% after launch. A merge queue is an enabler of TBD, not a substitute for it: it keeps the trunk green while preserving small, frequent merges.

### Branch Protection and Review Workflow

The branching model is only as good as its enforcement layer — the branch-protection rules that make the model structural rather than aspirational:

| Rule | Protects against | Applies to |
|------|------------------|-----------|
| Required status checks (CI must pass) | Merging broken code | All merges to `main`/trunk |
| Required PR review (peer review) | Untested, unreviewed changes | All merges to `main`/trunk |
| No direct pushes to protected branches | Bypassing the model | `main`/trunk, release branches |
| Restrict pushes to release branches | Unauthorized hotfixes | `release/*` during stabilization |
| Merge queue on protected branches | CI races and red `main` | High-volume repos |

Branch protection is policy-as-code applied to the repository: it encodes "small, reviewed, CI-passing changes only" so the process does not depend on memory or goodwill. It pairs with the pipeline's own gates (see [cd-and-pipeline-stages.md](./cd-and-pipeline-stages.md)) — the repo protects the merge, the pipeline protects the deploy.

### Named example — Google

Roughly **35,000 developers** collaborate in a single monorepo on a shared trunk. Most major projects branch from mainline *at a revision* for a release and **never merge back**; fixes are cherry-picked forward into the release branch and periodically returned to mainline. This works because builds are hermetic, tests are fast, and feature flags cover in-flight work. Google's scale is the stress test for TBD: if it breaks down anywhere, it is at merge-request review and CI capacity, not at the branching model itself.

## GitHub Flow — Lightweight Middle Ground

**GitHub Flow** is `main` plus short-lived feature branches merged via pull request, with deployment happening from `main`. The trunkbaseddevelopment.com reference notes it is "quite similar" to TBD; the difference is mostly *where you release from* — GitHub Flow keeps the option of releasing straight off `main` with no release-branch ceremony.

| Aspect | GitHub Flow | Trunk-based |
|--------|-------------|-------------|
| Long-lived branch | `main` only | `main`/trunk only |
| Feature branches | Short-lived, PR-merged | Short-lived, PR-merged |
| Release point | Tag or deploy from `main` | Tag from trunk, or cut a short-lived release branch |
| Best fit | Small-to-mid teams, SaaS, low ceremony | Teams needing strict mainline discipline at scale |

GitHub Flow is the right default when a team wants most of TBD's benefits but has not yet built the flag/testing machinery to keep incomplete work safely on trunk. The migration path is usually GitHub Flow → TBD as flags and pipeline maturity arrive, not the reverse.

## GitFlow — the Legacy Model (When It Still Fits)

**GitFlow** adds long-lived `develop` and `release` branches alongside `main`, with `hotfix` branches for urgent patches. It was designed for versioned, packaged software with scheduled releases and parallel maintenance of multiple released versions. That is also its cost: every change travels `feature → develop → release → main`, and fixes must be merged in multiple directions, which accumulates merge overhead and slows lead time. Practitioner consensus is to prefer TBD or GitHub Flow unless you genuinely ship boxed/versioned software that customers run without your control.

When GitFlow still fits:

- **On-premise or customer-managed software** where several released major versions are supported in parallel and each must receive security patches.
- **Regulated environments** that mandate a formal release branch as the artifact source for audit.
- **Hardware-coupled or firmware products** where field units cannot be upgraded arbitrarily.

> **Gotcha — GitFlow as cargo cult:** Teams adopt GitFlow "because the enterprise template says so," then pay merge-tax on every release while gaining nothing. If you cannot name the customer constraint that requires parallel version maintenance, use trunk-based or GitHub Flow instead.

## Release Branches Cut Just-in-Time

Release branches remain a valid tool when they are **cut just-in-time from trunk**, hardened, and **deleted after release** — or omitted entirely when you release from trunk with a fix-forward strategy. The just-in-time pattern gives you a stable stabilization surface without the long-lived-branch overhead of GitFlow:

1. **Branch cut** — at the release-candidate point, create `release/v<major>.<minor>.x` from a trunk revision you trust.
2. **Stabilization** — cherry-pick only critical fixes (P0/P1 defects, security, customer-blocking issues) from trunk into the branch.
3. **Release** — tag and build the artifact from the branch; re-run the full CI suite on the branch, because cherry-picks bypass the integration testing that happened on trunk.
4. **Patches** — hotfixes go through the same branch, tagged `v2.3.1`, `v2.3.2`, ...
5. **End of life** — archive or delete the branch once all consumers have migrated.

**Cherry-pick discipline:** every cherry-pick is code that skipped trunk's integration tests. Require a tracking issue, enforce the same code-review standard, re-run CI on the branch after each pick, and keep a log (SHA + description) attached to the release notes. Google rebuilds at the original release revision and pins the *build toolchain* to that revision, so a compiler change cannot silently alter a hotfixed in-production release.

**The merge-back decision:** at release time, choose explicitly among *merge the branch back, cherry-pick fixes forward, or archive it*. Google's model is branch-from-mainline-at-a-revision, never merge back, cherry-pick fixes forward and periodically return them to mainline. The unforgivable option is *no decision*: a branch that lingers indefinitely, silently accumulating divergence until "which branch has the fix?" becomes archaeology. If a branch will outlive one release, it must have a merge-back or archiving plan before it is cut.

## Release Trains and Calendar Releases

**Release trains** ship on a fixed cadence regardless of which features are ready — the train leaves the station on schedule. This converts coordination cost into a predictable date: teams know when the branch cuts, when stabilization starts, and when the release ships, and can plan cross-team dependencies against it. The tradeoff is that incomplete work must be explicitly deferred to the next train, which only works when features are flag-gated or genuinely shippable in pieces.

| Example | Cadence | Notes |
|---------|---------|-------|
| **Ubuntu** | 6-month cycle (`YY.MM` versions) | Feature freeze and release freeze ladder leading up to each release |
| **Chromium** | 4-week branch cadence | Branch point every 4 weeks, stabilization to stable, patches on the branch |
| **GitLab** | Monthly (`YY.MM`), self-managed release on the third Thursday of the month (one-week delay if needed) | Patch releases for regressions and security fixes between majors |
| **Firefox** | 2-week cycle (`main` → `beta` merge every 2 weeks) | Version-numbered trains with a single beta channel feeding stable; ~5 betas per cycle, RC QA-tagged, uplifts via tracking/approval flags |

The freeze ladder is the train's engine: each milestone (feature freeze → release candidate → final release) converts "should we include this?" from a debate into a date. What is not frozen by the freeze date rides the next train — and the only way that is acceptable is feature flags, which let a feature land on the train while *exposure* waits (see [progressive-delivery.md](./progressive-delivery.md)).

**SAFe Agile Release Trains (ARTs)** are the scaled-agile variant: 5–12+ teams align on a common **Program Increment** cadence (typically 8–12 weeks) with PI Planning and periodic sync events, coordinated by a Release Train Engineer. ARTs are an *organizational scaling construct* — they schedule and synchronize many teams — not a deployment technique. They fit large, multi-team, regulated, or hardware-coupled environments where independent per-team cadence would fragment the product. Treat the specific PI length and role names as SAFe-version-dependent rather than fixed doctrine.

> **Gotcha — the train metaphor taken literally:** A release train that ships regardless of readiness forces you to either ship broken features or hold finished ones. The escape valve is feature flags: ride the train, but expose features only when each is ready. Trains without flags are how "it's on the train, so we shipped it" accidents happen.

## Feature-Driven vs Time-Based Releases

| Model | Trigger | Pros | Cons | Fits |
|-------|---------|------|------|------|
| **Feature-driven** | Ship when a feature is done | User value arrives immediately; no artificial wait | No predictable dates; feature scope creep delays everything | SaaS with flag-based dark launches, small teams |
| **Time-based (train/calendar)** | Ship on schedule | Predictable dates; coordination cost falls; scope control via deferral | Ships whatever is ready; needs flags/deferral discipline | Multi-team products, regulated releases, hardware, enterprises |

The two are not mutually exclusive: mature teams use **calendar cadence for the container and feature-driven release inside it** — the train ships on schedule, but each feature is flag-gated and turned on when its own quality bar is met. This is precisely how "deploy on the train, release features on demand" reconciles the models. The container handles coordination; the flags handle readiness.

## Single-Repo vs Multi-Repo Cadence

The branching model interacts with repository topology:

- **Multi-repo (polyrepo):** each repo owns its pipeline and versioning; cross-repo dependencies are mediated by artifact registries and version ranges. Coordination cost moves into dependency upgrades — every breaking change triggers a cascade of downstream releases. Releases are per-service, which is good for independence and bad for atomic cross-cutting changes.
- **Monorepo:** one repository, one (or per-service) pipeline, atomic cross-cutting changes, synchronized builds. Releases may be **fixed/one-version** (everything ships together — Google's one-version rule) or **independently versioned** (changesets/release-please) with affected-build detection to avoid rebuilding everything (see [monorepo-polyrepo-release.md](./monorepo-polyrepo-release.md)).

The cadence question follows: polyrepo teams need explicit cross-repo release coordination (version ranges, deprecation windows); monorepo teams can release atomically and are the natural home for TBD and release trains.

## Deployment Risk Profiles

The process model also determines *how* a release reaches production, and Google's risk-profiled deployment is the reference pattern: most services roll out via **exponential cluster expansion** (small canary → doubling exposure on health), while **sensitive infrastructure** (billing, data, anything where a mistake is expensive) extends the rollout over several days, **interleaving across geographic regions** so a regional failure does not become a global one. The risk profile is a property of the release's blast radius, not of the team's mood: a config change to a payment path and a new README deploy do not deserve the same rollout shape. Choosing the profile is part of choosing the release model (see [progressive-delivery.md](./progressive-delivery.md) for the mechanisms).

## Ownership and Ceremony

Every process model implies an ownership and ceremony structure, and the two must match:

| Model | Ceremony | Owner |
|-------|----------|-------|
| Trunk-based | None per deploy — the pipeline is the gate | The deploying team; no release manager |
| GitHub Flow | PR review + CI; tag-and-deploy on demand | The deploying team |
| Release branches (JIT) | Branch cut, stabilization, patch flow | Release manager or designated DRI per release |
| Release train | Branch cut, freeze ladder, go/no-go, comms | Release manager DRI who owns the train's schedule |

The rule: **ceremony should scale with coordination need.** Per-deploy ceremony in a trunk-based team is waste; the absence of ceremony on a multi-team train is how trains derail. The train's DRI owns the calendar, the branch cut, and the go/no-go (see [readiness-and-quality-gates.md](./readiness-and-quality-gates.md)); the trunk-based team's "ceremony" is the pipeline itself. When in doubt, put the ceremony in the pipeline (automated gates) rather than in the calendar (meetings) — the pipeline enforces 24×7; the meeting enforces once a month. And whatever the model, name the DRI: an unnamed owner is an unowned process.

## Decision Guidance

| Situation | Model |
|-----------|-------|
| SaaS/high-throughput team with automated tests and flags | Trunk-based |
| Small team, low ceremony, deploy from `main` | GitHub Flow |
| Versioned, packaged software, parallel major-version support | GitFlow (or just-in-time release branches from trunk) |
| Regulated enterprise needing a formal artifact branch for audit | Trunk + just-in-time release branches |
| Multi-team product needing predictable dates | Release train / calendar (SAFe ART at scale) |
| Firmware/hardware with field units | Time-based trains + just-in-time release branches |
| High PR volume breaking `main` | TBD + merge queue (GitHub merge queue, Graphite, Trunk.io) |

A useful litmus test: *can the current `main` head ship to production right now?* If not, your process model is forcing batches larger than your quality gates can absorb — shrink the model, not the gates.

## Choosing: a Checklist

When selecting or auditing a process model, run the team through these questions:

1. Can the head of `main` ship to production today? (If not, batches are too large or gates too weak.)
2. Can incomplete work live safely on trunk (feature flags / branch-by-abstraction)? (If not, you will be tempted to park it on branches.)
3. How many released versions must be maintained in parallel, and by what obligation (customer contract, regulation, device fleet)?
4. Does any regulator or customer contract require a release-branch artifact as the audit source?
5. Do multiple teams need a common schedule (trains), or does per-team cadence fragment the product?
6. What is the actual merge cost today — conflict rate, PR wait time, stabilization length? (Measure it; do not argue about it.)
7. What ceremony does the model demand, and does the team have the ownership structure to sustain it?

The answers to 1–2 determine whether trunk-based is viable; 3–4 determine whether GitFlow-style parallel-version support is genuinely required; 5 determines whether trains are warranted; 6–7 tell you whether the team is actually operating the model it thinks it has.

## Signs the Model Is Wrong

Process-model problems announce themselves before they cause incidents. Watch for these symptoms:

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| Long-lived branches accumulate divergent fixes that never reach mainline | Branch lifecycle unenforced | Schedule branch deletion/merge-back; track every backport |
| `main` is frequently red | Batches too large; incomplete work not flag-gated | Shrink batches; hide in-flight work behind flags |
| PRs sit unmerged for days | No merge queue; PRs too big | Add a merge queue; split PRs |
| Every release needs weeks of stabilization | Cadence mismatch or oversize batches | Smaller trains; flag-gated deferral of unfinished work |
| Cherry-pick rate on release branches stays high for months | Fixes are not merging back to trunk | Enforce merge-back as a release criterion |
| Merges regularly conflict | Long-lived feature branches | Move to trunk-based / short-lived branches |

Any of these persisting is a process-model defect, not a personnel problem — the model is generating the friction.

## Gotchas

> **Gotcha — long-lived release branches:** A release branch kept alive past its release accumulates divergent fixes that never reach mainline. Either schedule the branch's deletion, or treat every backport as a first-class change with a tracking issue.

> **Gotcha — trunk-based without the prerequisites:** Merging to trunk daily without fast automated tests and feature flags just moves the pain: broken `main` becomes everyone's problem. TBD is a contract — merge small, keep tests green, hide incomplete work.

> **Gotcha — merge queues treated as a magic shield:** Merge queues keep `main` green under volume but do not reduce batch size. If PRs still sit unmerged for days, the queue is masking an integration bottleneck, not fixing one.

> **Gotcha — cherry-pick archaeology:** Release branches that are never merged back force engineers to re-apply fixes by hand. Track every cherry-pick with a ticket and a changelog entry so the "did this fix ship?" question has a machine-answerable record.

> **Gotcha — trains without a deferral mechanism:** A calendar release with no way to say "this feature is not ready" degrades into a quality lottery. The deferral mechanism (flag, exemption process, scope review) is part of the model, not an add-on.

## Sources and Further Reading

- [Trunk-Based Development (trunkbaseddevelopment.com)](https://trunkbaseddevelopment.com/)
- [Google SRE Book — Release Engineering (ch. 8)](https://sre.google/sre-book/release-engineering/)
- [DORA — Working in Small Batches capability](https://dora.dev/capabilities/working-in-small-batches/)
- [DORA — The DORA Metrics guide](https://dora.dev/guides/dora-metrics/)
- [GitHub Blog — How GitHub uses merge queue to ship hundreds of changes every day](https://github.blog/engineering/engineering-principles/how-github-uses-merge-queue-to-ship-hundreds-of-changes-every-day/)
- [Chromium — Release Process](https://www.chromium.org/developers/release-process/)
- [Ubuntu Project Docs — Release Team Freezes](https://documentation.ubuntu.com/project/release-team/freezes/)
- [SAFe — Agile Release Train](https://scaledagileframework.com/agile-release-train/)
