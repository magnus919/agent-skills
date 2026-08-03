# E2E Test Authoring

> **Last Updated:** 2026-08-03

How to write Playwright E2E tests that are readable, stable, and fast to
maintain. Authoring decisions are execution-side; *what to test and at what
level* is QA strategy owned by `qa-methodology` (its
`qa-methodology/references/test-strategy.md`).

## Anatomy of a spec

One spec file per user journey, described in prose, located by behavior:

```ts
import { test, expect } from '@playwright/test';

test.describe('checkout', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/cart');
  });

  test('completes a purchase with a saved card', async ({ page }) => {
    await page.getByRole('button', { name: 'Checkout' }).click();
    await page.getByRole('button', { name: 'Place order' }).click();
    await expect(page.getByRole('heading', { level: 1 })).toHaveText('Order confirmed');
  });
});
```

Rules of thumb:

- **One journey per test.** A test that verifies two unrelated flows fails for
  two unrelated reasons and gets rewritten as two tests anyway.
- **Setup in `beforeEach` / fixtures, not in the test body.** Keep the test body
  readable as a spec of the behavior.
- **Describe what the user does**, not what the DOM does: "places an order",
  not "clicks the button with class `.btn-primary`".

## Web-first assertions (no sleeps)

Playwright assertions retry until a timeout:

```ts
await expect(page.getByText('Saved')).toBeVisible();
await expect(input).toHaveValue('50');
await expect(page).toHaveURL(/\/orders\/\d+/);
```

- Never `await page.waitForTimeout(2000)` to "fix" a race — it slows the suite
  and hides the real timing bug.
- For genuinely async conditions use `expect.poll()` or `expect(...).toPass()`
  instead of arbitrary sleeps.

## Fixtures

Shared setup lives in a fixture file and is composed per test:

```ts
import { test as base, expect } from '@playwright/test';

export const test = base.extend<{ signedInPage: Page }>({
  signedInPage: async ({ page }, use) => {
    await page.goto('/login');
    await page.getByLabel('Email').fill('qa@example.com');
    await page.getByLabel('Password').fill(process.env.TEST_PASSWORD!);
    await page.getByRole('button', { name: 'Sign in' }).click();
    await use(page);
  },
});
```

## Starting the app: webServer

Declare the app lifecycle in the config so Playwright starts, waits for, and
tears down the server per run (see `templates/playwright.config.ts`):

- `webServer.command` — the dev/preview command.
- `webServer.url` — a readiness URL; Playwright polls it before running tests.
- `reuseExistingServer: !process.env.CI` — reuse a dev server locally, always
  start fresh on CI.

Prefer `webServer` over asking the agent to start the app manually; the config
makes the run reproducible in CI too.

## The page-object model (at the size where it pays)

Group locators and actions for a screen into a class when a spec grows beyond
~15 lines or the same flow is asserted from several specs:

```ts
export class CartPage {
  constructor(private readonly page: Page) {}
  async open() { await this.page.goto('/cart'); }
  async applyPromo(code: string) { await this.page.getByLabel('Promo code').fill(code); }
  get checkoutButton() { return this.page.getByRole('button', { name: 'Checkout' }); }
}
```

Do not add a POM layer preemptively — one spec that reads as prose beats a
POM with one user.

## Related

- Locator choice and flaky-selector repair: `02-selectors.md`.
- Mocking external HTTP so tests stay hermetic: `03-network-interception-and-mocking.md`.
- Snapshot-style accessibility assertions: `07-accessibility-and-debugging.md`.
