# Playwright — E2E Testing, Scraping, and Headless Browsing

Drive a real browser with Playwright: author and debug E2E test suites, mock network traffic, run tests in parallel and in CI, and scrape JavaScript-rendered pages — all with a bundled smoke harness that works without a browser installed.

## Why Install This Skill

Your agent can operate a Playwright test suite end to end: read the config and understand what runs, write stable specs with user-facing locators, intercept and mock third-party APIs so tests stop being flaky, tune workers and sharding, and wire the suite into CI with traces and reports you can actually triage. It also covers the scraping side — loading JavaScript-rendered pages and extracting structured data with an explicit extract → validate → save loop that respects robots.txt and rate limits.

The bundled `pwrun` script makes the toolchain legible without any Node setup: it checks the environment, inventories the suite, and summarizes a Playwright JSON test report into a bounded failure list — so an agent can triage a red CI run from the report artifact alone, no browser needed.

## What You Get

| Directory | Purpose |
|---|---|
| `SKILL.md` | Agent-facing operating loop: authoring, selectors, network mocking, parallel workers, CI, scraping, accessibility snapshots, headed debugging |
| `references/` | Eight dated references: e2e authoring, selectors, network interception/mocking, parallel/sharding, CI, scraping/headless, accessibility + debugging, source index |
| `scripts/pwrun` | Smoke harness with `--json`: `doctor` (toolchain), `inventory` (suite shape), `report` (JSON-report triage), `smoke` (delegated run) |
| `tests/` | Deterministic tests plus a sample Playwright JSON report fixture |
| `templates/` | Copy-in test-suite scaffold: `playwright.config.ts`, `example.spec.ts`, `accessibility.spec.ts` |
| `evals/evals.json` | Output-quality evals (schema v1, 6 cases) spanning authoring, scraping, debugging, and frontend test implementation |

## Quick Start

```bash
# Inspect a Playwright suite and triage its runs — no node required
bash scripts/pwrun doctor --json
bash scripts/pwrun inventory --json
bash scripts/pwrun report --report test-results/test-results.json --json

# Scaffold a new suite (copy the templates into your project)
cp templates/playwright.config.ts templates/example.spec.ts templates/accessibility.spec.ts .
npm i -D @playwright/test
npx playwright install
npx playwright test
```

The `--help` output documents every flag and works without Node. Set `BASE_URL` to override the smoke target; `scripts/pwrun smoke --url http://localhost:3000 --json` runs a delegated pass through `npx playwright test`.

## Triggers

Load this skill for Playwright, `playwright test`, E2E test authoring and debugging, flaky selectors/locators, network interception and mocking (`page.route`), test parallelism and sharding, running E2E tests in CI, accessibility snapshot checks (`toMatchAriaSnapshot`, axe scans), or scraping/headless browsing of JavaScript-rendered pages. Do not load it for QA strategy or framework selection (that's `qa-methodology`), frontend component design (that's `frontend-engineering`), or Cloudflare challenge bypass (that's `flaresolverr`).

## Requirements

- Playwright 1.40+ for the documented patterns (aria snapshots need 1.49+).
- Node.js + `@playwright/test` to run tests or the `smoke` command.
- The `pwrun` script runs on Python 3.8+ (stdlib only) — `doctor`, `inventory`, and `report` need no Node or browser.
- A display server (or headless mode) when running browsers on a CI runner.
