import { test, expect } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';

/**
 * Accessibility smoke scaffold.
 *
 * Requires: npm i -D @axe-core/playwright
 *
 * - The axe scan catches WCAG violations (contrast, landmarks, ARIA misuse).
 * - The aria snapshot is a stable, accessibility-aware assertion: it compares
 *   the accessibility tree, so it catches structure and label regressions.
 *
 * When the aria snapshot legitimately changes, run
 * `npx playwright test --update-snapshots` ONLY after reviewing the diff.
 */
test.describe('accessibility', () => {
  test('home page has no critical or serious axe violations', async ({ page }) => {
    await page.goto('/'); // [fill: route]
    const results = await new AxeBuilder({ page }).analyze();
    const blocking = results.violations.filter(
      (violation) => violation.impact === 'critical' || violation.impact === 'serious',
    );
    expect(blocking).toEqual([]);
  });

  test('home page matches the aria snapshot', async ({ page }) => {
    await page.goto('/');
    await expect(page).toMatchAriaSnapshot(`
      - heading "[fill: page heading]" [level=1]
      - button "[fill: primary action]"
    `);
  });
});
