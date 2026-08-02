# Test Automation

## Framework Decision Matrix

| Criteria | pytest | Playwright | Vitest | Cypress |
|----------|--------|-----------|--------|---------|
| **Language** | Python | JS/TS, Python, .NET, Java | JS/TS (Vite-based) | JS/TS |
| **Primary Domain** | Unit, integration, API | E2E browser, mobile | Unit, component, E2E | E2E browser, component |
| **Browser Support** | N/A | Chromium, Firefox, WebKit | Via Playwright browser mode | Chromium, Firefox, Edge |
| **Parallelism** | pytest-xdist | Built-in workers + sharding | Built-in pool + sharding | Dashboard parallelization (paid) |
| **Auto-wait** | N/A | Yes (built-in) | N/A (VDOM assertions) | Yes (retry-ability) |
| **Network Mocking** | responses / pytest-httpx | route() API | vi.mock / msw | cy.intercept() |
| **Debugging** | pdb / --pdb | Trace viewer, video | Browser DevTools | Time-travel, snapshots |
| **CI-first?** | Yes | Yes (blob reports, sharding) | Yes (sharding, pool) | Dashboard-based |
| **Best For** | Python projects, data/API | Multi-browser E2E | Vite/React/Vue component + unit | Dev-integrated E2E |

### Selection Flow

```
Is the project Python?
  YES → pytest (with xdist for parallelism)
  NO  → Is it Vite-based?
          YES → Unit/component: Vitest | E2E: Playwright
          NO  → Playwright (E2E) + Jest or Vitest (unit)
```

> **Gotcha — "Automate everything":** Automating a bad test design just makes failures faster. Invest in test design (see [test-design-techniques.md](./test-design-techniques.md)) before scaling automation.

## Parallelism and Sharding

### Three Levels

| Level | What | Tooling |
|-------|------|---------|
| Within a job (multi-worker) | Multiple tests on one machine | `pytest -n auto`, Playwright workers, Vitest pool |
| Across jobs (sharding) | Suite split into N groups, each on a CI runner | `--shard=x/y`, matrix strategy |
| Across suites | Different test types in separate CI jobs | CI workflow orchestration |

### Configuration Example (GitHub Actions + Playwright)

```yaml
jobs:
  e2e:
    strategy:
      matrix:
        shard: [1, 2, 3, 4]
    steps:
      - uses: actions/checkout@v4
      - run: npx playwright test --shard=${{ matrix.shard }}/4
      - uses: actions/upload-artifact@v4
        if: always()
        with:
          name: blob-report-${{ matrix.shard }}
          path: blob-report

  merge-reports:
    if: always()
    needs: [e2e]
    steps:
      - run: npx playwright merge-reports --reporter html ./all-blob-reports
```

### pytest Splitting

```bash
# Within-node parallelism
pytest -n auto --dist worksteal   # dynamic rebalancing (xdist 3.x+)

# Across CI jobs (timing-balanced)
pytest --splits 4 --group ${{ matrix.group }} --store-durations
```

### Shard Balancing Tips

- Use `fullyParallel: true` (Playwright) for test-level distribution
- Log timing data (`--store-durations`) to balance groups by historical duration
- Set job-level timeouts to prevent hung workers from blocking the pipeline
- Cache dependencies between shards (node_modules, pip packages)

## ML / Predictive Test Selection

When suites exceed 10,000 tests, full-run-on-every-PR becomes impractical. Predictive selection uses historical data to run only tests likely to be affected by a change.

| Approach | How It Works | Tools / Research |
|----------|-------------|-----------------|
| **Static call-graph analysis** | Map changed code → tests that exercise it (conservative) | Ekstazi, custom dependency graphs |
| **ML-predicted relevance** | Train on historical (change, test-outcome) pairs; predict which tests to run | Launchable, Microsoft Research |
| **Failure-rate weighting** | Prioritize tests with high historical failure rate on similar changes | Custom scoring (see selection math in [regression-testing.md](./regression-testing.md)) |

**Key research:** Predić et al. (arXiv:2106.13891, 2021) demonstrated that ML-based test selection reduces CI runtime by 50–90% while catching >99% of failures that full-suite execution would catch. Launchable (commercial) and Microsoft's internal systems use similar approaches at scale.

**Adoption guidance:**
- < 1,000 tests: full suite on every PR (keep it simple)
- 1,000–10,000 tests: sharding + timing-based splitting
- > 10,000 tests: predictive selection (Launchable, custom ML) with full-suite nightly as safety net

> **Gotcha — Selection without safety net:** Never rely solely on predicted selection. Run the full suite on a schedule (nightly or on main-branch merge) to catch false negatives in the prediction model.

## Flaky Test Quarantine Workflow

### Detection → Quarantine → Fix → Reintegrate

```
1. DETECT: Test fails on retry but passes on re-run (flaky signal)
2. TAG:    Mark with @quarantine / skip annotation + tracking issue
3. ISOLATE: Move to separate CI job that runs but does NOT block the pipeline
4. TRACK:  Dashboard showing quarantine count, age, owner
5. FIX:    Owner has 5 business days to stabilize or delete
6. REINTEGRATE: Remove quarantine tag; burn-in 20+ green runs before re-blocking
```

### Quarantine Criteria

| Signal | Threshold | Action |
|--------|-----------|--------|
| Flake rate (failures / runs) | > 2% over 50 runs | Quarantine |
| Blocks PR pipeline | > 3 times in one week | Quarantine immediately |
| Age in quarantine | > 10 days unfixed | Escalate to team lead; consider deletion |

### Stabilization Patterns

| Root Cause | Fix |
|-----------|-----|
| Race condition / timing | Explicit waits on observable state, never `sleep()` |
| Shared mutable state | Isolated fixtures, rollback after each test |
| External dependency | Mock/stub at the boundary |
| Random data collision | Seeded randomness or UUID-based test data |
| Test interdependence | `pytest-randomly` to expose ordering issues |

## Mutation Testing as Test-Effectiveness Signal

Mutation testing measures whether your tests **actually detect injected faults**, not just whether they execute code (which is all coverage measures).

### How It Works

1. Tool introduces small code changes (mutants): `>` → `>=`, `+` → `-`, remove a statement
2. Run the test suite against each mutant
3. If tests fail → mutant killed (good). If tests pass → mutant survived (bad: tests don't catch this fault)
4. **Mutation score** = killed mutants / total mutants

### Tool Landscape

| Tool | Language | Notes |
|------|----------|-------|
| **PIT (pitest.org)** | Java/Kotlin | Industry standard for JVM; incremental mode |
| **Stryker** | JS/TS, C#, Scala | Supports Jest, Mocha, Vitest |
| **mutmut** | Python | Lightweight; integrates with pytest |

### Interpretation

| Mutation Score | Interpretation |
|---------------|---------------|
| > 80% | Strong test suite; tests assert behavior, not just execution |
| 60–80% | Adequate; focus on survived mutants in P0/P1 code |
| < 60% | Tests likely assert weakly (e.g., "no exception" without checking output) |

> **Gotcha — Coverage ≠ effectiveness:** A suite at 95% line coverage with a 40% mutation score has extensive dead assertions. Use mutation testing as the true quality signal for high-risk modules; coverage alone is necessary but not sufficient.

**Practical adoption:** Run mutation testing on P0/P1 modules weekly (not on every PR — it's expensive). Gate advisory: mutation score < 60% on payment/auth code triggers a review flag.

## Composition Links

- Test design techniques (EP, BVA, pairwise): [test-design-techniques.md](./test-design-techniques.md)
- Regression suite management and selection math: [regression-testing.md](./regression-testing.md)
- Quality gates and metrics: [quality-gates-and-metrics.md](./quality-gates-and-metrics.md)
- Systematic debugging of test failures: [systematic-debugging](../../systematic-debugging/SKILL.md)

---

*Sources: Playwright docs (2025), pytest-xdist docs, Launchable (launchableinc.com), Predić et al. arXiv:2106.13891 (2021), PIT (pitest.org), Stryker Mutator (stryker-mutator.io), mutmut (GitHub), DORA Accelerate (2018).*
