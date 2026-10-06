import { defineConfig, devices } from '@playwright/test';

// pwrun --url overrides inherited PW_SMOKE_URL. Direct Playwright runs can set
// PW_SMOKE_URL, then BASE_URL; the scaffold default is used otherwise.
const baseURL = process.env.PW_SMOKE_URL ?? process.env.BASE_URL ?? 'http://localhost:3000';
const parsedBaseURL = new URL(baseURL);
const host = parsedBaseURL.hostname;
const isLoopback = host === 'localhost' || host === '[::1]' || /^127(?:\.\d{1,3}){3}$/.test(host);

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
    baseURL, // --url via pwrun > PW_SMOKE_URL > BASE_URL > scaffold default
    trace: 'on-first-retry', // capture a trace when a test fails on retry
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
  },
  projects: [
    { name: 'chromium', use: { ...devices['Desktop Chrome'] } },
    { name: 'mobile-chromium', use: { ...devices['Pixel 7'] } }, // [fill: devices you support]
  ],
  // Start the scaffold app only for local targets. Remote targets are visited
  // directly and should not start an unrelated local dev server.
  webServer: isLoopback ? {
    command: 'npm run dev', // [fill: your app's dev/preview command]
    url: parsedBaseURL.origin, // [fill: local readiness origin]
    reuseExistingServer: !process.env.CI,
    timeout: 120_000,
  } : undefined,
});
