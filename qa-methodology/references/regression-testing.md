# Regression Testing

## Core Principle

> **Every fixed bug becomes a regression test.** When a defect is fixed, the test that reproduces it (or should have caught it) is added to the suite permanently. This is the single highest-ROI regression practice: the suite's ability to catch known failure modes grows monotonically. Track "regression test added for fix" rate; target > 80% of bug fixes.

## What Belongs in a Regression Suite

| Include | Exclude |
|---------|---------|
| Every fixed bug (as a test) | Tests that haven't failed in 6+ months (review for archive) |
| Critical user paths (P0/P1) | Tests for deprecated features |
| Known failure patterns | Tests duplicating lower-level coverage |
| API contract checks | Visual regression on work-in-progress UI |
| Data integrity assertions | Performance tests (separate suite) |

## Test Impact Analysis (Shift-Left Selection)

Not every change needs the full suite. Impact analysis selects the subset of tests affected by a change.

| Approach | How It Works | Trade-off |
|----------|-------------|-----------|
| **Static call-graph** | Map changed code → functions → tests that call them | Fast, conservative (over-selects); misses dynamic dispatch |
| **Dynamic trace** | Record which tests execute which code (coverage instrumentation), then map changes → tests | Accurate; needs profiling infra; Ekstazi uses this |
| **ML prediction** | Train on historical (change, failing-test) pairs | Best precision; needs history; see [test-automation.md](./test-automation.md) |

**Tools:** Ekstazi (dynamic, JVM), Launchable (ML, language-agnostic), custom coverage-map scripts.

### Selection Math

Score each test for inclusion on a change:

```
selection_score(test) =
    w1 × changed_code_coverage(test)      # does it touch the diff? (0/1)
  + w2 × historical_failure_rate(test)    # how often has it failed recently?
  + w3 × business_risk(test)              # P0/P1 path? (see test-strategy.md)
```

Default weights: `w1=0.5, w2=0.3, w3=0.2`. Run all tests with score > threshold, plus always run the full P0 smoke set regardless of score.

| Change Type | Required Tests |
|-------------|---------------|
| Bug fix | Repro test + related unit tests |
| Feature addition | New feature tests + adjacent smoke |
| Refactoring | Full unit suite + integration smoke |
| Dependency update | Full regression suite |
| Infrastructure change | Integration + E2E suite |

## Suite Evolution (Tiering)

Tests move between tiers as the system and risk profile change:

| Tier | Cadence | Contents | Promotion / Retirement |
|------|---------|----------|----------------------|
| **Tier 0 — Smoke** | Every PR (< 5 min) | P0 paths, build sanity | Promote from Tier 1 if a path becomes critical |
| **Tier 1 — Core** | Every merge (< 30 min) | P0/P1 regression, contracts | Promote from Tier 2 on rising failure rate |
| **Tier 2 — Extended** | Nightly | P2, slower integration, E2E | Retire tests with 0 failures in 6 months + no risk coverage |
| **Tier 3 — Archive** | On demand | Retired, legacy | Restore if a related defect escapes |

**Evolution rule:** A test that fails in production-adjacent tiers gets promoted; a test with zero failures over 6 months and no P0/P1 risk coverage is a retirement candidate (review, don't auto-delete).

## Shift-Right Feedback Loops

Production signals drive regression suite composition — closing the loop between what escapes and what you test.

| Signal | Suite Action |
|--------|-------------|
| **Production error spike** (observability/APM) | Add a regression test reproducing the failing condition; promote related tests to Tier 1 |
| **Canary analysis failure** | The canary check becomes a permanent regression assertion; review why left-side testing missed it |
| **Escaped defect (customer report)** | Root-cause: add the missing test, then audit the tier that should have caught it |
| **Feature-flag rollout** | Flag-gated code gets targeted regression selection while flagged; full coverage before flag removal |

**Loop discipline:** Every escaped defect gets a post-mortem question — "which tier should have caught this, and why didn't it?" The answer drives suite evolution, not blame.

## Flaky Test Discipline: Rerun-Once, Never-Twice

> **Protocol:** In a blocking regression run, a failed test may be rerun **exactly once**. If it passes on the single rerun, record it as a **flake** (not a pass) and route to quarantine. If it fails the rerun, it is a **real failure** — block. **Never rerun a second time.**

Why never twice: a second rerun turns flake-masking into a habit. If a test needs two retries to pass, it is not reliable enough to gate on, and repeated retries hide a rising flake rate until CI trust collapses.

| Outcome | Classification | Action |
|---------|---------------|--------|
| Pass on first run | Pass | Record green |
| Fail, then pass on 1st rerun | **Flake** | Do NOT count as pass; open quarantine issue; see [test-automation.md](./test-automation.md) |
| Fail, fail on 1st rerun | **Real failure** | Block the pipeline |
| Needs 2nd rerun to pass | Unreliable | Treat as flake; quarantine immediately |

Track flake rate (flaky outcomes / total runs). Sustain at < 2%; above that, invest in stabilization before adding more tests.

> **Gotcha — Ignoring flakes:** A "pass on retry" is not a pass. Flakes are latent failures; a suite with 5% flakiness on 10,000 daily tests produces ~500 false signals/day and erodes trust until teams bypass automation entirely.

## Suite Hygiene

| Condition | Action |
|-----------|--------|
| Test hasn't failed in 6 months + no risk coverage | Review for archive |
| Test flakes > 2% over 50 runs | Quarantine and fix |
| Test takes > 5s (unit) / > 30s (integration) | Optimize or promote to slower tier |
| Test depends on another test's state | Fix isolation (tests must be independent) |
| Test runs against production data | Switch to synthetic fixtures (see [test-data-management.md](./test-data-management.md)) |

## Composition Links

- Impact-analysis tooling and ML selection: [test-automation.md](./test-automation.md)
- Risk-based tier prioritization (P0–P3): [test-strategy.md](./test-strategy.md) and [risk-based-testing.md](./risk-based-testing.md)
- Flaky quarantine workflow: [test-automation.md](./test-automation.md)
- Quality gates and metrics: [quality-gates-and-metrics.md](./quality-gates-and-metrics.md)

---

*Sources: Ekstazi (Gligoric et al.), Launchable (launchableinc.com), DORA State of DevOps Reports, Predić et al. arXiv:2106.13891 (2021).*
