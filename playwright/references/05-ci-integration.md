# CI Integration

> **Last Updated:** 2026-08-03

Playwright in CI is: install browsers + OS deps, pin the version, run the
suite with retries and tracing, and surface a debuggable report. This
reference assumes GitHub Actions; the same shape applies to any runner.

## Minimal GitHub Actions workflow

```yaml
name: e2e
on: [push, pull_request]
jobs:
  e2e:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 20, cache: npm }
      - run: npm ci
      - run: npx playwright install --with-deps chromium
      - run: npx playwright test
      - if: failure()
        uses: actions/upload-artifact@v4
        with:
          name: playwright-report
          path: playwright-report/
          retention-days: 14
```

## Non-negotiables

1. **Install browsers with OS deps**: `npx playwright install --with-deps` (not
   bare `install`) on Linux runners; `--with-deps` installs the system
   libraries Chromium/Firefox/WebKit need.
2. **Pin and cache**:
   - `npm ci` with a committed `package-lock.json` (never `npm install`).
   - Cache the browser download: `~/.cache/ms-playwright` (Linux),
     `~/Library/Caches/ms-playwright` (macOS), `%USERPROFILE%\AppData\Local\ms-playwright` (Windows).
   - Cache `node_modules` via the setup-node `cache: npm` option.
3. **Retry flaky tests on CI only**, with traces on retry so failures are
   debuggable:

   ```ts
   retries: process.env.CI ? 2 : 0,
   use: { trace: 'on-first-retry' },
   ```
4. **Configure `webServer` in the config** so the runner starts and waits for
   the app; never assume a long-lived dev server on a runner.
5. **Upload artifacts on failure**: the HTML report, the JSON report, and the
   `test-results/` dir (traces). Retention bounded (7–14 days) — see hard
   boundaries in `SKILL.md` about keeping evidence bounded.

## Reporters

- `list`/`line` — human-readable run output.
- `html` — the browsable report (upload on failure).
- `json` — the machine-readable report for agent triage:

  ```bash
  scripts/pwrun report --report test-results/test-results.json --json
  ```

  It prints stats (expected/unexpected/flaky/skipped), the failing specs, and
  the error message from the last retry — enough to triage without opening a
  browser.
- `github` — inline annotations on GitHub Actions, keyed to the failing spec
  line.

## Sharding across jobs

For large suites, split the run:

```yaml
strategy:
  matrix:
    shard: [1/4, 2/4, 3/4, 4/4]
steps:
  - run: npx playwright test --shard=${{ matrix.shard }}
```

Merge reports from all shards with `playwright merge-reports` (see
`04-parallel-workers-and-sharding.md` for the math).

## Triage loop for a red CI run

1. `scripts/pwrun report --report <json> --json` — get the failing specs and
   messages.
2. Download the trace artifact (`trace.zip`) and open it in the Trace Viewer
   to see the failing action, network, and console.
3. Classify: environment (missing dep/browser), selector (see
   `02-selectors.md`), timing (webServer readiness, `webServer.timeout`),
   or app regression (real bug — the test did its job).
4. Fix, re-run, and confirm the shard matrix is green.

## Related

- Parallelism and sharding configuration: `04-parallel-workers-and-sharding.md`.
- Trace reading and headed debugging: `07-accessibility-and-debugging.md`.
