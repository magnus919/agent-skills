# Performance Budget

Fill this budget when defining or reviewing frontend performance targets.
Budgets are committed config, measured on every change, and enforced in CI so
a regression fails the build instead of shipping silently.

## Budget Dimensions

| Dimension | Metric | Budget | Measured by | Enforcement point |
|---|---|---|---|---|
| Bundle size | Initial JS (gzipped) | `[fill: e.g. 250 KB per route]` | Bundle report from the build | Build / CI script |
| Bundle size | Initial CSS (gzipped) | `[fill: e.g. 50 KB]` | Build output | Build / CI script |
| Bundle size | Largest single chunk | `[fill: e.g. 120 KB]` | Bundle report | `bundle-budget-checker` |
| Loading | LCP | `[fill: e.g. 2.5 s]` | Lighthouse (lab + field) | CI Lighthouse job |
| Stability | CLS | `[fill: e.g. 0.1]` | Lighthouse | CI Lighthouse job |
| Responsiveness | INP | `[fill: e.g. 200 ms]` | Field data / lab | CI Lighthouse job |
| Third-party | Script count / weight | `[fill: e.g. max 2 scripts, 50 KB]` | Request audit | CI check |

## Bundle Budget

Fill in the enforced numbers for the `bundle-budget-checker` invocation:

- Total budget for all route chunks: `[fill: bytes or human size, e.g. 512000 or 500KB]`
- Per-chunk budget: `[fill: e.g. 120KB]`
- Chunks exempt from the per-chunk budget (lazy-loaded vendors, web workers): `[fill: names and reason]`
- Command used in CI:
  ```
  [fill: e.g. python3 frontend-engineering/scripts/bundle-budget-checker.py dist/bundle-report.json --total 500KB --chunk 120KB]
  ```

## Measurement Setup

- Lab tooling: `[fill: Lighthouse CI config, mobile + desktop profiles, throttling]`
- Field data source: `[fill: CrUX / RUM provider and the percentiles tracked, e.g. p75]`
- Baseline commit and scores: `[fill: the recorded baseline so regressions are measured against it]`
- How often measurements run: `[fill: every PR, nightly, on release]`

## Enforcement Workflow

- Where budgets live: `[fill: committed file path]`
- What happens when a PR exceeds a budget: `[fill: CI fails, alert channel, owner follows up]`
- Escalation path for deliberate regressions: `[fill: who can approve an exception and how it is tracked]`

## Known Current Violations

| Metric | Current value | Budget | Owner | Follow-up |
|---|---|---|---|---|
| `[fill: metric]` | `[fill: value]` | `[fill: budget]` | `[fill: owner]` | `[fill: linked issue]` |

## Review Checklist

- [fill: check that] Initial render contains no unused heavy dependencies
- [fill: check that] Images are sized, compressed, and dimensioned
- [fill: check that] Fonts load with font-display swap and no layout shift
- [fill: check that] Route-level code splitting is in place for every page
- [fill: check that] Third-party scripts are deferred and counted in the budget
- [fill: check that] Measurements are rerun after each change
