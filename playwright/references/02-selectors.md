# Selector Robustness

> **Last Updated:** 2026-08-03

Selectors are the #1 source of E2E flakiness. The goal is locators that
describe what the element *is* (its role in the user experience), not where it
*happens to be* in the DOM.

## Locator priority

Use, in order of preference:

1. **Role** — `page.getByRole('button', { name: 'Save' })`. Mirrors how the
   page is presented to assistive tech and users; survives markup changes.
2. **Label / placeholder / text** — `getByLabel('Email')`,
   `getByPlaceholder('Search')`, `getByText('Saved', { exact: true })`.
3. **Test id** — `getByTestId('checkout-form')`. For elements whose role/label
   does not describe them (e.g., a decorative SVG, a canvas region). Test ids
   exist only for tests; agree on a naming convention.
4. **CSS / XPath** — last resort: layout-adjacent queries that role and label
   cannot express (e.g., "the third row of a table" is better done with
   `getByRole('row').nth(2)`).

## Composition over long strings

Chain and filter instead of concatenating brittle paths:

```ts
// Fragile: encodes nesting and order.
page.locator('div.product-card div.price span').click();

// Robust: describe the card by its visible content, then act within it.
const card = page.getByRole('article').filter({ hasText: 'Running shoes' });
await card.getByRole('button', { name: 'Add to cart' }).click();
```

- `filter({ hasText })` / `filter({ has: locator })` narrow a collection.
- `first()`, `last()`, `nth(n)` are code smells unless the ordering is the
  assertion (e.g., a sort test).

## The repair loop

A flaky test is a bug report about your selectors, not a request for more
`waitForTimeout`. When a test passes sometimes:

1. Run the spec alone (`npx playwright@1.62.1 test <spec> --workers=1 --repeat-each=5`)
   to measure flakiness deterministically.
2. Use `--debug` or the trace to see what the failing action actually resolved.
   Common causes:
   - **Zero matches** — the element appears late (async render): use a
     web-first assertion or wait for its container, not a sleep.
   - **Multiple matches** — your locator is too generic: narrow with
     `filter({ hasText })` or scope to a container.
   - **Stale node** — the element is re-rendered between lookup and action:
     re-query instead of storing a handle, or assert the new state after the
     re-render.
3. Fix the locator to describe the unique user-facing element, then re-run the
   repeat-each loop until it is green 5/5.

## Anti-patterns to avoid

- **`page.waitForTimeout()`** — masks races, slows the suite.
- **`page.waitForSelector()` + manual `click()`** — duplicates what
  `locator.click()` already does with retries.
- **Snapshots of CSS classes** (`expect(el).toHaveClass(...)`) for behavioral
  assertions — classes are implementation details.
- **Text that duplicates** across the page without disambiguation
  (`getByText('Submit')` matches 2 buttons) — add `{ exact: true }` or scope.
- **XPath with positional predicates** (`//div[2]/span[1]`) — order and
  structure change; roles do not.

## Related

- Authoring structure and fixtures: `01-e2e-authoring.md`.
- Emulating slow networks to surface timing bugs: `03-network-interception-and-mocking.md`.
