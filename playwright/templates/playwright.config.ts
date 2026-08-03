import { defineConfig, devices } from '@playwright/test';

/**
 * Test-suite scaffold for Playwright.
 *
 * Copy this file (plus example.spec.ts and accessibility.spec.ts) into your
 * project root, adjust the [fill: ...] markers, and run:
 *
 *   npm i -D @playwright/test
 *   npx playwright install
 *   npx playwright test
 */
export default defineConfig({
  testDir: './e2e', // [fill: directory that holds your spec files]
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0, // retry flaky tests on CI only
  workers: process.env.CI ? 4 : undefined, // [fill: CI worker count for your runner]
  reporter: [
    ['list'],
    ['html', { open: 'never' }],
    ['json', { outputFile: 'test-results/test-results.json' }], // triage with scripts/pwrun report
  ],
  use: {
    baseURL: process.env.BASE_URL ?? 'http://localhost:3000', // [fill: app URL]
    trace: 'on-first-retry', // capture a trace when a test fails on retry
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
  },
  projects: [
    { name: 'chromium', use: { ...devices['Desktop Chrome'] } },
    { name: 'mobile-chromium', use: { ...devices['Pixel 7'] } }, // [fill: devices you support]
  ],
  webServer: {
    command: 'npm run dev', // [fill: your app's dev/preview command]
    url: 'http://localhost:3000', // [fill: readiness URL the server must answer]
    reuseExistingServer: !process.env.CI,
    timeout: 120_000,
  },
});
