# Accessibility and Debugging

> **Last Updated:** 2026-08-03

Two workflows that share one tool feature set: asserting accessibility via the
accessibility tree, and debugging tests with the inspector, codegen, and
traces.

## Accessibility snapshot checks

### Full scans with axe-core

`@axe-core/playwright` runs the axe engine against the rendered page:

```ts
import AxeBuilder from '@axe-core/playwright';

const results = await new AxeBuilder({ page }).analyze();
// results.violations: [{ id, impact, nodes, ... }]
expect(results.violations.filter((v) => v.impact === 'critical' || v.impact === 'serious'))
  .toEqual([]);
```

- Scan every route that matters, ideally in CI; scan the full page or use
  `.include()` / `.exclude()` to scope.
- Triage by `impact`: fix critical/serious; track moderate/minor in a backlog.
- False positives happen (e.g., contrast rules on known-brand colors) — scope
  them out deliberately, never with a blanket `disableRules(['color-contrast'])`.

### Aria snapshots (snapshot-based accessibility assertions)

`expect(page).toMatchAriaSnapshot()` asserts against the **accessibility tree**,
not the DOM:

```ts
await expect(page).toMatchAriaSnapshot(`
  - heading "Store front" [level=1]
  - button "Add to cart"
`);
```

- These read like spec assertions ("the heading is X, the button is Y") and
  catch regressions in structure, labels, and semantics — not just contrast.
- They are stable: inline text changes show up as a reviewable diff.
- **Update deliberately.** Run `npx playwright test --update-snapshots` only
  after inspecting what changed; never blind-update to make CI green (hard
  boundary in `SKILL.md`).
- Requires Playwright 1.49+ (see `00-source-index.md` for version notes).

## Headed debugging

When a test fails or a locator matches nothing:

1. **Read the failure first** — `scripts/pwrun report --report <json> --json`
   gives the failing spec and the error message from the last retry.
2. **Run headed with slow-mo** to watch the actual page:

   ```bash
   npx playwright test <spec> --headed --slow-mo 300
   ```
3. **The inspector** (`--debug` or `PWDEBUG=1`) pauses before each action and
   shows the current locator; `page.pause()` drops a breakpoint mid-test.
4. **Codegen** to prototype a flow quickly:

   ```bash
   npx playwright codegen https://example.com
   ```
   Generate starter tests, then harden the emitted selectors into user-facing
   locators (`02-selectors.md`).
5. **Traces** are the evidence record: with `trace: 'on-first-retry'` (or
   `--trace on`), every failed run produces a trace you can open in the Trace
   Viewer — network, DOM snapshots, console, and the failing action, frame by
   frame. This is the primary artifact to attach to a bug report.

## Debugging checklist

| Symptom | First move |
|---|---|
| Locator resolves to 0 elements | `--debug`; check async render — assert on a container first |
| Locator matches 2+ elements | Narrow with `filter({ hasText })` or scope to a container |
| Timeout on `click()` | Trace: is something covering the element (overlay)? is it disabled? |
| Passes locally, fails CI | Compare env: browser deps (`install --with-deps`), `baseURL`, shard isolation |
| Flaky across retries | `--repeat-each=5 --workers=1` to measure; then fix the selector |
| Console errors before failure | Trace console tab; check for unhandled rejections the test should assert |

## Related

- Authoring and assertions: `01-e2e-authoring.md`.
- Selector repair loop: `02-selectors.md`.
- CI trace/artifact wiring: `05-ci-integration.md`.
