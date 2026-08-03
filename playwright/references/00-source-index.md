# Source Index — Playwright references

> **Last Updated:** 2026-08-03

## Scope

This skill's references are distilled from the official Playwright documentation
and the underlying standards the tool implements (WebDriver BiDi for CDP
migration, WAI-ARIA for the accessibility tree). They are patterns and
decision guidance, not a substitute for the primary sources below.

## Primary sources

| Topic | Source | Accessed |
|---|---|---|
| Test runner, assertions, fixtures, webServer | https://playwright.dev/docs/writing-tests | 2026-08-03 |
| Locators and selector philosophy | https://playwright.dev/docs/locators | 2026-08-03 |
| Network interception (`page.route`) | https://playwright.dev/docs/network | 2026-08-03 |
| Parallelism and sharding | https://playwright.dev/docs/test-parallel | 2026-08-03 |
| CI guides (GitHub Actions, Docker) | https://playwright.dev/docs/ci | 2026-08-03 |
| Traces, HTML/JSON reporters, debugging | https://playwright.dev/docs/trace-viewer | 2026-08-03 |
| Accessibility testing + aria snapshots | https://playwright.dev/docs/accessibility-testing | 2026-08-03 |
| Headless browsers and scraping contexts | https://playwright.dev/docs/api/class-browser | 2026-08-03 |
| Codegen, inspector, slow-mo | https://playwright.dev/docs/codegen | 2026-08-03 |
| `@axe-core/playwright` integration | https://github.com/dequelabs/axe-core-npm | 2026-08-03 |

## Version observations

- **1.40+** — `toMatchAriaSnapshot` is available from 1.49; earlier versions
  used the experimental `page.accessibility` API or `expect(...).toHaveAccessibleSnapshot()`.
  Pin the version that matches the features this skill references (see `SKILL.md`).
- The JSON reporter output shape changed over time (suite-level `tests` arrays
  became `specs[]` with nested `tests[]`). `scripts/pwrun report` parses both
  shapes; a fixture for the modern shape lives in `tests/fixtures/sample-report.json`.

## Refresh procedure

Re-verify statements in these references when a new Playwright major lands:
1. Re-read the primary source pages above.
2. Check the changelog for renamed APIs (e.g., `--update-snapshots` flags,
   reporter options, `webServer` fields).
3. Update the `Last Updated` line in the changed reference and the version
   observations above.
