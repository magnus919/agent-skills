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

## Mutation-Guided Test Hardening

Mutation-guided test hardening is targeted review evidence, not a mutation engine, portable report format, or score-optimization exercise. Coverage and mutation effectiveness answer different questions: line/branch coverage says whether execution reached code; mutation analysis asks whether tests detect plausible behavior-changing faults. Do not interpret a mutation score as a universal quality grade. It depends on operator quality, equivalent-mutant handling, scope, exclusions, timeouts, and denominator integrity.

### Tool Landscape

Use the project's established native tool and its raw report as authoritative. Confirm the installed version and supported configuration in the project's documentation; the table only identifies the official project documentation, not a promise of interchangeable features.

| Tool | Primary ecosystem | Official source |
|------|-------------------|-----------------|
| PIT | Java and JVM mutation testing | [PIT project README](https://github.com/hcoles/pitest) · [pitest.org](https://pitest.org) |
| StrykerJS | JavaScript and TypeScript mutation testing | [StrykerJS project README](https://github.com/stryker-mutator/stryker-js) · [stryker-mutator.io](https://stryker-mutator.io/) |
| mutmut | Python mutation testing | [mutmut documentation](https://mutmut.readthedocs.io/en/latest/) |

### Bounded Review Loop

Use this loop when a changed behavior, review concern, or weak assertion warrants stronger evidence:

1. Choose changed lines/files or an explicitly justified risk slice. Broaden the slice for dependency, configuration, harness, environment, shared-abstraction, or cross-cutting changes.
2. Run the project's established native mutation tool. PIT, StrykerJS, and mutmut are examples of the existing landscape; use the project's supported tool and raw report as authoritative, without assuming undocumented versions or features.
3. Record an explicit mutant budget, timeout, seed, exclusions, operator set, test command, tool/version, and environment.
4. Classify every result at minimum as `killed`, `survived`, `equivalent/likely equivalent`, `no coverage`, `timeout`, `flaky`, `invalid`, or `infrastructure/tooling failure`.
5. Treat survivors as triage inputs, not automatic defects. Propose a focused behavior-level test only where the surviving fault is meaningful.
6. Check the candidate for behavioral relevance, non-tautology, non-vacuity, non-redundancy, maintainability, flake risk, and implementation coupling. A generated test may be valuable even when it does not increase the score; a killed mutant does not prove the test is good.
7. Independently rerun the baseline, candidate test, and exact retained mutant. The implementer cannot self-certify the generated test; use a fresh verifier or human.
8. Record raw-report locations, commands, classifications, uncertainty, and reviewer decision in [templates/mutation-review.md](../templates/mutation-review.md).

Define the denominator explicitly, for example `classified mutants / in-scope mutants`, and state how equivalent, excluded, unknown, incomplete, and infrastructure-failed mutants are accounted for. They must not silently disappear or inflate a clean result. Keep mutation use advisory and risk-based rather than an unconditional repository-wide gate or universal score threshold. A project may independently validate a narrower policy, but that policy needs its own evidence and review.

### Reproduction Sequence

```text
record base/head and scope -> run native tool with bounded settings
-> preserve raw report -> classify every mutant and denominator
-> propose behavior-level test for meaningful survivor
-> fresh verifier reruns baseline, candidate, exact mutant
-> attach commands, outputs, uncertainty, and decision
```

For review artifacts use [mutation-review.md](../templates/mutation-review.md). For independent evidence and evaluation boundaries, see [ai-code-quality-gates.md](./ai-code-quality-gates.md), [verification-methodology](../../verification-methodology/SKILL.md), and [agent-evals-and-observability](../../agent-evals-and-observability/SKILL.md).

## Composition Links

- Test design techniques (EP, BVA, pairwise): [test-design-techniques.md](./test-design-techniques.md)
- Regression suite management and selection math: [regression-testing.md](./regression-testing.md)
- Quality gates and metrics: [quality-gates-and-metrics.md](./quality-gates-and-metrics.md)
- Systematic debugging of test failures: [systematic-debugging](../../systematic-debugging/SKILL.md)

---

*Sources: Playwright docs (2025), pytest-xdist docs, Launchable (launchableinc.com), Predić et al. arXiv:2106.13891 (2021), PIT project README (github.com/hcoles/pitest; pitest.org), StrykerJS project README (github.com/stryker-mutator/stryker-js; stryker-mutator.io), mutmut documentation (mutmut.readthedocs.io), and ACH (arXiv:2501.12862).*
