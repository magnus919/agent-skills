import { test, expect } from '@playwright/test';

/**
 * Spec scaffold: one spec per user journey, described in prose, located by
 * user-facing roles/labels, asserted with web-first assertions. Copy into
 * e2e/ and adapt the [fill: ...] markers.
 */
test.describe('[fill: feature under test]', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/'); // [fill: app entry route, relative to baseURL]
  });

  test('[fill: the behavior in one sentence]', async ({ page }) => {
    // Prefer getByRole / getByLabel / getByText over CSS that encodes markup.
    await page.getByRole('button', { name: '[fill: button label]' }).click();

    // Web-first assertions auto-retry until the timeout; never use
    // page.waitForTimeout() to "fix" a race.
    await expect(
      page.getByRole('heading', { level: 1 }),
    ).toHaveText('[fill: expected heading]');

    await expect(page).toHaveURL(/\/[fill: path-pattern]/);
  });
});
