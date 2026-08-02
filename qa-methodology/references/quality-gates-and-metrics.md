# Quality Gates and Metrics

## Gate Design: Blocking vs Advisory

A quality gate is an enforced checkpoint that must be satisfied before software proceeds. Classify every gate as one of three types:

| Type | Pipeline Behavior | Example |
|------|------------------|---------|
| **Blocking** | Pipeline stops; artifact not promoted | Unit test failure, critical CVE |
| **Advisory** | Pipeline continues; warning logged + team notified | Coverage drop, lint warnings |
| **Informational** | No pipeline impact; recorded for dashboard | Execution time trend, flake rate |

### Gate Placement by Stage

```
Commit → [Lint (advisory)] → [Unit tests (blocking)]
  → [Build (blocking)] → [Static analysis: 0 critical (blocking)]
    → [Integration tests (blocking)] → [E2E tests (blocking)]
      → [Performance regression (advisory)] → [Security scan (blocking)]
        → Release
```

### Gate Evolution

Tighten gates as the team matures. Review quarterly:

| Phase | Blocking | Advisory |
|-------|----------|----------|
| Starting | Tests compile + pass | Coverage > 50% |
| Growing | Unit pass, coverage > 70%, 0 critical static-analysis | Coverage > 80% |
| Maturing | All tests pass, coverage > 80%, 0 high CVEs | Flake rate < 2% |
| High-perf | All pass, coverage > 85%, mutation score > 70% on P0 | Perf regression < 5% |

> **Gotcha — Too many blocking gates:** When everything blocks, developers bypass or game the pipeline. Keep blocking gates to critical checks; use advisory for everything else. If a gate fires on > 50% of PRs, loosen it temporarily while the team improves.

### Anti-Patterns

| Anti-Pattern | Problem | Fix |
|-------------|---------|-----|
| Gates that never change | Thresholds become irrelevant | Quarterly review; tighten gradually |
| Coverage without quality | 90% coverage of weak assertions is misleading | Add mutation testing (see [test-automation.md](./test-automation.md)) |
| Single flaky test blocks pipeline | Loss of trust in CI | Quarantine flaky tests (see [test-automation.md](./test-automation.md)) |
| Manual gates for everything | Pipeline becomes the bottleneck | Automate everything scriptable; manual only for regulatory sign-off |

## DORA Four Keys + Reliability

The DORA metrics (from Google's DevOps Research and Assessment team) measure delivery performance. QA owns the quality-adjacent keys:

| DORA Key | Definition | QA Ownership | Elite Target |
|----------|-----------|-------------|-------------|
| **Deployment Frequency** | How often code ships to production | Enable via fast, reliable test feedback | Multiple per day |
| **Lead Time for Changes** | Commit → production elapsed time | Reduce test cycle time (parallelism, selection) | < 1 hour |
| **Change Failure Rate** | % of deploys causing incidents | Direct quality metric — escaped defects | < 5% |
| **Mean Time to Restore (MTTR)** | Time from incident → recovery | Detection speed (monitoring), rollback readiness | < 1 hour |

**Fifth metric — Reliability:** DORA's 2021 report added reliability as a complementary measure: meeting user-facing SLOs. QA contributes by validating SLO thresholds in pre-production and monitoring escape patterns post-deploy.

### Connecting DORA to QA Metrics

| DORA Key | QA Metric That Drives It |
|----------|------------------------|
| Deployment Frequency | Test suite duration, flake rate (fewer reruns = faster feedback) |
| Lead Time | Time-to-green on PR pipeline |
| Change Failure Rate | Defect escape rate, regression suite effectiveness |
| MTTR | MTTD (mean time to detect), rollback test coverage |

## Vanity vs Actionable Metrics

| Metric | Type | Why |
|--------|------|-----|
| Tests executed (count) | **Vanity** | Activity measure; says nothing about quality |
| Lines of test code | **Vanity** | More code ≠ more confidence |
| Coverage % alone | **Vanity** (without context) | Can be gamed; high coverage + low mutation score = weak suite |
| Defect escape rate | **Actionable** | Directly tells you where testing is failing |
| Flake rate | **Actionable** | Rising flake rate predicts loss of CI trust |
| MTTR by severity | **Actionable** | Drives investment in debugging/rollback tooling |
| Mutation score (P0 code) | **Actionable** | Tells you if tests actually catch faults |
| Change failure rate | **Actionable** | Direct DORA quality signal |
| Regression test ROI | **Actionable** | (Tests that caught a regression) / (total regression tests) — guides suite pruning |

**Rule:** If a metric changes and you don't know what action to take, it's vanity. Track 5–10 metrics maximum (the 5-10 rule); more than 10 causes analysis paralysis.

## Defect Severity and Priority Classification

### Severity Scale (Technical Impact)

| Level | Definition | Example |
|-------|-----------|---------|
| **S1 — Critical** | System down, data loss, security breach | Production database corrupted |
| **S2 — High** | Major feature broken, no workaround | Checkout flow returns 500 |
| **S3 — Medium** | Feature degraded, workaround exists | CSV export omits one column |
| **S4 — Low** | Cosmetic, minor inconvenience | Alignment off by 2px |

### Priority Scale (Business Urgency)

| Level | Definition | Response SLA |
|-------|-----------|-------------|
| **P1 — Immediate** | Blocks release or impacts revenue now | Acknowledge < 1h, fix < 4h |
| **P2 — Urgent** | High user impact, next-release blocker | Fix within current sprint |
| **P3 — Normal** | Moderate impact, schedule normally | Fix within 2 sprints |
| **P4 — Backlog** | Low impact, fix when convenient | No SLA; backlog grooming |

### Severity × Priority Interaction

Severity and priority are independent: a critical-severity bug in a deprecated feature may be P3 (fix next sprint), while a medium-severity bug affecting a key customer demo may be P1 (fix today). **Priority = f(severity, business context, user impact).**

### Escalation Rules

| Condition | Action |
|-----------|--------|
| Any S1/P1 defect | Blocks release; escalate to engineering leadership within 1 hour |
| S2/P1 unresolved > 24h | Escalate to VP Engineering |
| 3+ S2 defects in one release | Trigger release hold; root-cause review |
| S1 in production | Page on-call; post-incident review within 48h |

## Metric Visualization

Track 5–10 core metrics on a team-visible dashboard:

```
Quality Dashboard — Sprint 24
┌──────────────────────────────────────┐
│ Pass Rate: 98.5% │ Coverage: 83%     │
│ Escaped Defects: 3 (1 S2)           │
│ DDP: 94%         │ MTTR: 4.5h       │
│ Flake Rate: 1.2% │ Suite: 14min     │
│ Change Failure Rate: 3.2%           │
└──────────────────────────────────────┘
```

## Composition Links

- Test automation framework selection and mutation testing: [test-automation.md](./test-automation.md)
- Performance thresholds feeding gates: [performance-testing.md](./performance-testing.md)
- Flaky quarantine workflow: [test-automation.md](./test-automation.md)
- Agent evals and observability (eval-specific metrics, graders): [agent-evals-and-observability](../../agent-evals-and-observability/SKILL.md)

---

*Sources: DORA State of DevOps Report 2023 (Google Cloud), DORA Accelerate (Forsgren, Humble, Kim; 2018), SonarSource quality gate documentation, MinimumCD Practice Guide.*
