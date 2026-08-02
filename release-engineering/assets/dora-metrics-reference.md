# DORA Metrics Quick Reference

> The five research-backed software delivery metrics, how to compute them, and the classic thresholds. Use for measuring, dashboarding, and reporting delivery performance. The metrics measure system outcomes, not individual performance — do not use them for personal evaluation.

## The Five Metrics

| Metric | What it measures | Formula / unit | Data source |
|--------|------------------|----------------|-------------|
| Deployment frequency (DF) | How often code reaches a production environment | Successful production deployments per day (or per week) | Deploy logs / CI-CD platform / GitOps sync records |
| Change lead time (CLT) | Time from commit to running in production | Median of (deploy finished_at − commit created_at) over deployed commits; unit: hours/days | Version-control commit timestamps + deploy records |
| Change failure rate (CFR) | Share of deployments that cause degraded service | Failed or remediated deploys ÷ total deploys × 100 (%) | Deploy ↔ incident correlation (rollbacks, hotfixes, incident tickets tied to a deploy) |
| Failed deployment recovery time | Time to restore service after a failed deploy | Median time from failed deploy start to next successful deploy; unit: minutes/hours | Incident + deploy timeline |
| Deployment rework rate | Share of deployments needing rework (rollback, hotfix, forward fix) | Unplanned rework deployments ÷ total deployments × 100 (%) | Deploy records flagged as unplanned |

## Classic 2024 Thresholds (the "four keys" at the time)

| Tier | Deployment frequency | Change lead time | Change failure rate | Failed deployment recovery time |
|------|----------------------|------------------|---------------------|-------------------------------|
| Elite | On-demand (multiple deploys/day) | Less than one hour | 0–5% | Less than one hour |
| High | Between once per day and once per week | Between one day and one week | 0–15% | Less than one day |
| Medium | Between once per week and once per month | Between one week and one month | 0–15% | Less than one week |
| Low | Between once per month and once every six months | Between one month and six months | 0–30% | Less than one month |

> **2025 change caveat —** the DORA team replaced the fixed tier labels with performance **clusters** (e.g., "high-performing", "low-performing") computed from the joint distribution of the four keys, and added **deployment rework rate** as a fifth metric. Do not hard-code 2024 threshold tables into dashboards; treat them as historical reference points and prefer the cluster model benchmarked against your own population.

## Top Pitfalls

- **PRs ≠ deploys.** Count deployments of code to production, not merged pull requests or commits.
- **Mean vs. median.** Use the median for lead time and recovery time — the mean is skewed by rare long outliers.
- **Repo vs. service.** Measure per deployable service, not per repository (a monorepo may contain many services).
- **Ignoring rollbacks.** A rolled-back deploy is a failure — excluding it inflates both DF and CFR.
- **Time-source mismatch.** Commit and deploy timestamps must be comparable (UTC, NTP-synced) or lead time is meaningless.
- **Manual counting.** Spreadsheets drift; derive the metrics from pipelines and GitOps records automatically.
- **Gaming the metric.** Raising DF without improving CFR or lead time just amplifies bad change.

## Sources and Further Reading

- DORA — research and metric definitions: https://dora.dev/
- Accelerate (Forsgren, Humble, Kim, 2018): https://itrevolution.com/product/accelerate/
- DORA metrics measurement guidance: https://dora.dev/research/measurement/
- Google Cloud DORA blog (2025 cluster change): https://cloud.google.com/blog/products/devops-sre
