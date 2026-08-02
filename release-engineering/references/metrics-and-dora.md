# DORA Metrics: Exact Definitions, Benchmarks, and Pitfalls

DORA's software-delivery metrics are the shared scoreboard of release engineering. This file gives the **current five-metric model** with exact definitions, formulas, units, raw data sources, and aggregation rules; the last classic four-tier performance table (2024) with the mandatory 2025 caveat; known vendor-formula divergences; and the pitfalls that make most naive implementations wrong. One-page version: [../assets/dora-metrics-reference.md](../assets/dora-metrics-reference.md).

## The Five Metrics

DORA's metric set evolved over a decade: the original four keys (2014) were joined by a scoped recovery metric (2023), and a fifth delivery metric, **deployment rework rate**, was added in 2024. The current set splits into **throughput** and **instability**:

| Group | Metric | What it measures |
|-------|--------|------------------|
| Throughput | **Change lead time** | Commit → production |
| Throughput | **Deployment frequency** | How often changes ship |
| Throughput | **Failed deployment recovery time** | Time to recover from a failed deploy (formerly MTTR) |
| Instability | **Change failure rate** | Share of deploys needing immediate intervention |
| Instability | **Deployment rework rate** | Share of unplanned, bug-fix deployments |

The metric set's evolution matters when you read older material:

| Year | Change |
|------|--------|
| 2014 | Original four variables: deployment frequency, lead time for changes, MTTR, change fail rate |
| 2015 | Solidified the throughput-vs-stability framing; debunked the speed-vs-stability tradeoff myth |
| 2018 | Added "availability"; renamed the construct "Software Delivery and Operational (SDO) performance" |
| 2021 | Expanded availability → reliability (an *operational* measure, not a delivery metric) |
| 2023 | MTTR renamed and re-scoped to **Failed Deployment Recovery Time** (change-caused failures only) |
| 2024 | **Deployment Rework Rate** added as the fifth metric |
| 2025 | Report renamed "State of AI-assisted Software Development"; tiers replaced by archetypes; the five metrics remain |

## Operationalization: Data Sources and Canonical Scales

**Data-source → metric map** (for building the pipeline that produces these numbers):

| Metric | Primary source | Secondary |
|--------|---------------|-----------|
| Deployment frequency | CI/CD deploy events (env = production) | Git Deployments API / Releases-tags; CD tool records |
| Change lead time | VCS commit timestamps + deploy finish time + deployed SHA | PR merge time (for stage breakdowns) |
| Failed deployment recovery time | Incident management (change-caused incidents only) | Deploy records (failed deploy → restoring deploy) |
| Change failure rate | Deploy records + rollback/roll-forward detection | Incidents linked to deploys |
| Deployment rework rate | PR/branch/label heuristics + incidents | Issue-tracker bug labels |

**DORA's canonical categorical scales** (from the Quick Check — the bands DORA itself uses in surveys):

- **Change lead time:** >6 months | 1–6 months | 1 week–1 month | 1 day–1 week | <1 day | <1 hour
- **Deployment frequency:** <1/6 months | 1/month–1/6 months | 1/week–1/month | 1/day–1/week | 1/hour–1/day | on-demand (multiple/day)
- **Failed deployment recovery:** >6 months | 1–6 months | 1 week–1 month | 1 day–1 week | <1 day | <1 hour
- **Change failure rate:** 0–100% slider
- **Deployment rework rate:** 0–100% slider (last 6 months, unplanned bug-fix deploys)

### Worked Example (30-Day Window)

A service deploys 22 times in 30 days; 20 succeed; 3 of the successful deploys were unplanned hotfixes; 1 deploy fails in production and is rolled back 40 minutes later. A change commits on day 3 and reaches production on day 7.

| Metric | Computation | Result |
|--------|-------------|--------|
| Deployment frequency | 20 successful prod deploys / 30 days | 0.67 deploys/day |
| Change lead time (that change) | day 7 deploy finish − day 3 commit | 4 days (aggregate: median across all changes) |
| Change failure rate | 1 failed deploy / 21 total | 4.8% |
| Failed deployment recovery time | 40 min from failure start to rollback completion | 40 min (aggregate: median) |
| Deployment rework rate | 3 unplanned hotfix deploys / 20 successful | 15% |

Note the rework rate (15%) exceeding CFR (4.8%) — the typical pattern, because unplanned remediation deploys outnumber outright failed deploys.

## Exact Definitions, Formulas, and Data Sources

### Deployment Frequency (DF)

- **Definition:** How often application changes are deployed to production / released to end users.
- **Unit:** successful production deployments per day (a rate), or a categorical band.
- **Formula:** `DF = number of successful production deployments / number of days in window`.
- **Counting:** count *successful* deployments to **production only** (or "release to end users"); staging/test deploys never count. Count per **service**, not per repository — a monorepo deploying five services from one merge produces five deployment events.
- **Raw data sources:** CI/CD deployment events; CD tool records filtered to `environment = production`; Git host Deployments API (e.g., GitHub `/deployments?environment=production`, latest status `state == success`); cluster deploy logs. Proxy: Releases/tags — but this overcounts pre-releases and undercounts untagged hotfixes.

### Change Lead Time (CLT)

- **Definition:** Time from code **committed to version control** to that change **successfully running in production**.
- **Unit:** duration (hours/days).
- **Formula (per change):** `CLT = production_deployment_finish_time − commit_creation_time`.
- **Aggregation:** **median** across changes. Distributions are right-skewed — one long-lived refactor wrecks the mean. Datadog's approach: `git log <prev_deploy_sha>..<this_deploy_sha>` to find the commits in a deployment, drop merge commits (no new code), compute the per-commit duration, then aggregate (median across deployments).
- **Raw data sources:** version-control commit timestamps, deploy records (finish time + deployed SHA), PR merge data for stage breakdowns (time-to-PR-ready, review time, merge time, time-to-deploy, deploy time).
- **Correlation key:** the **commit SHA** (or the PR number stored in deploy metadata). Squash and rebase merges change SHAs and break naive matching — store the PR number in deployment metadata to correlate directly.

### Change Failure Rate (CFR)

- **Definition:** Ratio of deployments that cause a failure in production and **require immediate intervention** (rollback, roll-forward/hotfix, patch).
- **Unit:** percentage (0–100%).
- **Formula:** `CFR = (number of failed deployments / total deployments) × 100`.
- **Counting:** a change is a failure only if it needs *remediation in production*; a defect caught in staging is not CFR.
- **Raw data sources:** deploy records + rollback/roll-forward detection (via git metadata/version tags, or PR-title/branch heuristics like `^revert`, `^rollback`, `^hotfix`, `^emergency`); incidents linked to deployments.

### Failed Deployment Recovery Time (FDRT) — the 2023 MTTR rename

- **Definition:** Time to recover from a **deployment that fails and requires immediate intervention** — i.e., restoring service after a *change to production caused an impairment*.
- **Why the rename:** the old MTTR ("time to restore service") did not distinguish change-caused failures from external causes (data-center outage, network event). In 2023 DORA re-scoped the metric to **change-caused failures only**. Generic incident MTTR is *not* FDRT unless incidents are tagged change-caused.
- **Unit:** duration (minutes/hours).
- **Formula (per incident):** `FDRT = remediation_time − failure_start_time`, where remediation is the rollback or roll-forward deployment that restores service.
- **Aggregation:** **median**; use histograms/scatter, not mean-of-averages (non-normal distribution).
- **Raw data sources:** incident management (PagerDuty/OpsGenie/incident.io: created → resolved), filtered to change-caused incidents; deploy records (failed deploy → restoring deploy); monitoring/alerting (impairment detected → restored).

### Deployment Rework Rate (DRR) — added 2024

- **Definition:** Ratio of deployments that are **unplanned but performed to address a user-facing bug** — reactive remediation rather than planned value delivery. DORA's quickcheck phrasing: "percentage of deployments in the last 6 months that were not planned but were performed to address a user-facing bug."
- **Unit:** percentage (0–100%).
- **Formula:** `DRR = (unplanned/remediation deployments / total deployments) × 100`.
- **Counting:** classify deployments as unplanned via PR title/branch/label heuristics (revert/rollback/hotfix/fix-forward/emergency), linked incidents, or deploy-metadata flags. DORA's survey asks about the **last 6 months** specifically.
- **Distinction from CFR:** CFR counts *failed deployments*; DRR counts *unplanned deployments caused by production issues*. In practice you typically have more unplanned remediation deploys than outright failed deploys, so **DRR ≥ CFR**. DRR captures the "hidden tax" of reactive work that CFR understates.

## Performance Clusters: The 2024 Table (Last Classic Four-Tier Version)

DORA's tiers come from **cluster analysis** — a descriptive pattern-detection method over that year's survey respondents, not fixed prescriptive thresholds — and the values shift every year. **2024 is the last year with the classic Low/Medium/High/Elite table.**

| Level | Change lead time | Deployment frequency | Change failure rate | Failed deployment recovery time |
|-------|------------------|----------------------|---------------------|---------------------------------|
| **Low** | 1 to 6 months | Monthly to biannual | 40% | 1 week to 1 month |
| **Medium** | 1 week to 1 month | Weekly to monthly | 10% | Less than a day |
| **High** | 1 day to 1 week | Daily to weekly | 20% | Less than a day |
| **Elite** | Less than a day | On demand (multiple/day) | 5% | Less than an hour |

- The 2024 table has the famous **inversion**: High shows a *higher* CFR (20%) than Medium (10%) — clusters are descriptive groupings, not a monotonic scorecard.
- Elite vs. Low magnitudes (Octopus's reproduction): elite deploys ~182× more often, ~8× lower CFR, ~127× faster lead time, ~2,293× faster recovery. The Elite cluster has historically been under 20% of organizations.
- 2023 comparison: Elite stayed stable; High's CFR rose; Medium improved CFR and recovery; Low improved stability but worsened throughput.

> **Gotcha — DORA retired the tiers in 2025:** The 2025 report ("State of AI-assisted Software Development") **dropped the Elite/High/Medium/Low tiers entirely**, replacing them with seven qualitative archetypes built on eight measures (throughput, stability, team performance, product performance, individual effectiveness, time on valuable work, friction, burnout). 2025 publishes only metric *distributions*, not tiers. If you quote the four-tier table, **anchor it to 2024** and say the tiers were retired. The five delivery metrics themselves remain the metric set.

**2025 distribution highlights (for context, from the 2025 report):** only 16.2% of respondents deploy on-demand; 23.9% deploy less than once a month; 43.5% have lead times over a week; 39.5% exceed 16% CFR; 56.5% take between a day and a week to recover; only 7.3% have rework below 2%. A 2025 finding with direct release-engineering relevance: AI adoption correlates with higher throughput and individual effectiveness but **higher instability** — stability is the metric AI has not improved.

## Vendor-Formula Divergence

Your tool's numbers will not equal DORA's survey numbers, and different tools disagree with each other. Three known divergences to account for:

- **Datadog** computes CLT from `git log` between deployed SHAs, drops merge commits, and aggregates per-commit values (avg/max/min per deployment, median across deployments); detects CFR via rollback/roll-forward detection; correlates recovery time with incidents.
- **GitLab** measures CLT from **MR merge time** (button clicked) to production — *not* from commit creation as DORA canonically defines it — clamped with `GREATEST(0, deploy_finished − mr_merged)`; uses **mean** for deployment frequency (historical choice) and median for CLT; derives CFR as incidents/deployments with a known double-counting bug for duplicate incidents.
- **Azure DevOps / GitHub-native** tooling covers DF, CLT, and a CFR proxy from their own data but generally **cannot compute FDRT** without an incident-management source (PagerDuty/OpsGenie/incident.io).

> **Gotcha — "your tool's CFR may not equal DORA's CFR":** Vendors operationalize CFR via incident counts (GitLab) or rollback detection (Datadog) rather than the survey's "requires remediation" definition. Always read the vendor's formula before quoting numbers in a report, and note the definition next to the value.

## Pitfalls (Most Implementations Get These Wrong)

1. **Counting PR merges as deployments.** A merge to `main` is not a deployment. If you deploy once a day regardless of merges, DF is once a day.
2. **Mean instead of median** for lead time and recovery time — skewed distributions make the mean meaningless (one 2-week refactor destroys it).
3. **Repository frequency instead of service frequency.** Monorepos must count per service; otherwise one repo's five-service deploy reads as one.
4. **Ignoring rollbacks and roll-forwards.** Without detecting them you undercount CFR and cannot compute FDRT at all.
5. **Counting non-production environments.** Staging failures are not CFR; scope every metric to production/release-to-users.
6. **Generic MTTR vs. change-scoped FDRT.** Including infrastructure/network/hardware outages inflates recovery time and violates the 2023+ definition.
7. **Squash/rebase SHA mismatch** — breaks commit↔deploy correlation; store PR numbers in deploy metadata.
8. **Wrong sampling window and timezones.** Define a fixed window and normalize to the team's local timezone before day-of-week analysis (a Friday 5pm EST deploy looks like Saturday 00:00 UTC).
9. **"Average of averages."** Aggregating deployment-level averages obscures per-commit reality; prefer commit-level CLT then median across deployments.
10. **Disparate comparisons.** Metrics are application/service-level; don't compare a mobile app to a mainframe, and don't build league tables between teams (DORA explicitly cautions against team competition). Compare an application to *itself over time*.
11. **Double-counting duplicate incidents** (a known GitLab CFR bug).

## DORA Metrics Are System Outcomes, Not Individual Metrics

DORA metrics measure an application and its delivery **system**. Attributing them to individuals is a documented misuse: setting DF or CFR as a personal goal invites gaming (splitting deploys to inflate frequency, under-reporting failures) — Goodhart's law in action ("when a measure becomes a target, it ceases to be a good measure"). Share all five metrics across dev, ops, and release rather than assigning single metrics to single teams.

**How release engineers actually use them for process improvement:**

- **Diagnose the bottleneck, not the symptom.** High CLT with low DF → batch-size and trunk-based-development problems; high CFR with low FDRT → weak gates and missing rollback rehearsal; high DRR with normal CFR → reactive workload masking (the hidden tax). DORA's core validated finding: speed and stability are **correlated, not a tradeoff** — top performers do well on both.
- **Drive small batches.** Smaller changes move faster *and* fail/recover better; batch-size reduction is a primary lever.
- **Gate improvement work.** Pair DORA with pipeline health (success rate, mean-time-to-green, flaky-test rate) and supply-chain coverage (signing/SBOM) for a complete release-reliability picture.
- **Compare the application to itself over time.** The defensible improvement loop is: baseline the five metrics → pick one bottleneck (e.g., CLT driven by a slow review stage) → change the process → re-measure on the same definition → keep what moved the number. Never chase another team's number.
- **Bound the measurement cost.** Precise multi-system instrumentation may not pay for itself; start with the Quickcheck conversation or a platform-native dashboard, then invest where the signal is actionable.

## Sources and Further Reading

- [DORA — Software Delivery Performance Metrics (dora.dev guide)](https://dora.dev/guides/dora-metrics/)
- [DORA — A History of DORA's Software Delivery Metrics](https://dora.dev/insights/dora-metrics-history/)
- [DORA Quick Check](https://dora.dev/quickcheck/)
- [Octopus — The 2024 DevOps Performance Clusters](https://octopus.com/blog/2024-devops-performance-clusters)
- [RedMonk — DORA 2025: Measuring Software Delivery After AI](https://redmonk.com/rstephens/2025/12/18/dora2025/)
- [Datadog — DORA Metrics Calculation](https://docs.datadoghq.com/dora_metrics/calculation/)
- [GitLab — DORA Metrics](https://docs.gitlab.com/user/analytics/dora_metrics/)
- [Koalr — How to Calculate DORA Metrics from GitHub Data](https://koalr.com/blog/calculate-dora-from-github)
