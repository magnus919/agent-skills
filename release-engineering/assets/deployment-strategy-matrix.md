# Deployment Strategy Matrix

> Choose a strategy per release based on risk, reversibility, and audience. Strategies combine: feature flags gate a feature's visibility while a canary gates the binary. Rollback time assumes an immutable, previously healthy artifact is available.

## Comparison

| Strategy | Speed to full rollout | Safety (defect exposure) | Rollback time | Complexity | When to use |
|----------|----------------------|--------------------------|---------------|------------|-------------|
| Rolling | Fast — minutes | Moderate — all instances briefly run the new version as it spreads | Minutes (redeploy previous artifact) | Low | Default for stateless services with good monitoring |
| Blue-green | Fast cutover; swap in seconds | High — the full old environment stays live | Seconds (router change) | Medium; 2× resources | Risky changes needing instant rollback; infrastructure you can afford to double |
| Canary | Medium — staged % over minutes–hours | High — defects hit a small slice first | Minutes (redeploy / auto-rollback of the canary) | Medium | Risky changes; comparing against a control population |
| Ring | Slow by design — hours–days across cohorts | Very high — exposure grows by ring | Slow (rings are users/devices, hard to recall) | High | Large user bases, clients/devices, compliance-driven exposure limits |
| Feature flag | Instant on/off — no redeploy | Depends on rollout %; off = zero exposure | Seconds (toggle off) | Medium (flag debt) | Decoupling deploy from release; dark launch; kill switch |
| Shadow | Immediate (traffic mirrored) | No user impact (nothing live is served) | N/A (nothing served) | High | Validating performance/behavior without exposing users |

## Decision Guidance

| Situation | Pick |
|-----------|------|
| Stateless service, good monitoring | Rolling or canary |
| Change can break irreversibly (schema, data) | Canary + expand/contract migration; never rely on rollback past finalization |
| Instant rollback is a hard requirement | Blue-green (or canary with auto-rollback) |
| Mobile / desktop / IoT users | Ring (phased release) + feature flags / kill switch — true rollback is impossible |
| Defect can be gated behind a flag | Flag off is the fastest lever — reach for it before any redeploy |
| Need to compare behavior vs. control | Canary with canary-vs-control metrics |
| Regulatory exposure limits | Ring with approved exposure caps per cohort |

## Gotchas

- **Teeing / shadowing limits:** synthetic or mirrored traffic does not validate stateful systems (e.g., billing) — a shadow run can look perfect and still fail on real writes.
- **Before/after comparisons lie:** compare canary vs. control populations, not the same metric over time.
- **Flags are not free:** every flag left behind is rollback speed today and operational debt tomorrow — plan removal in the flag's lifecycle.
- **Canary size × error budget:** a 5% canary at 20% error costs ~1% of the overall budget — size the canary so a bad release stays inside the budget.

## Sources and Further Reading

- Google SRE Workbook ch. 16 — Canarying Releases: https://sre.google/workbook/canarying-releases/
- Google SRE Book ch. 8 — Release Engineering: https://sre.google/sre-book/release-engineering/
- Google Cloud — Reliable releases and rollbacks: https://cloud.google.com/blog/products/gcp/reliable-releases-and-rollbacks-cre-life-lessons
- Martin Fowler — Parallel Change: https://martinfowler.com/bliki/ParallelChange.html
- Runway — Rollbacks on mobile: https://www.runway.team/blog/rollbacks-on-mobile-yes-they-are-possible-and-this-is-why-you-need-them
