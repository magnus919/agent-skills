# Network Interception and Mocking

> **Last Updated:** 2026-08-03

Intercept browser traffic with `page.route()` to make E2E tests hermetic,
deterministic, and fast — and to assert on what the app actually sent.

## The route API

```ts
// Fulfill: answer an intercepted request with canned data.
await page.route('**/api/payments/tokenize', (route) =>
  route.fulfill({
    status: 200,
    contentType: 'application/json',
    body: JSON.stringify({ token: 'tok_test_123' }),
  }),
);

// Abort: block a request entirely (trackers, analytics, heavy media).
await page.route('**/analytics/*', (route) => route.abort());

// Continue: let the real request through (with optional overrides).
await page.route('**/api/feature-flags', (route) =>
  route.continue({ headers: { ...route.request().headers(), 'x-experiment': 'on' } }),
);
```

Guidance:

- **Mock at the boundary.** The app under test is real; the world outside it
  (payment providers, third-party APIs, message queues) is faked. Never patch
  in-page code (`window.fetch = ...`) — that tests a tampered app.
- **Realistic bodies win.** Mock payloads that match the real schema and
  content type; a mock that differs from production can pass a test the app
  would fail.
- **Glob `**` patterns, not exact URLs** — hosts, query strings, and CDN
  prefixes change; `**/api/orders` covers `https://api.example.com/api/orders`.
- **Register routes before navigation** — routes apply to requests made after
  registration, so set them up in `test.beforeEach` before `page.goto`.

## What NOT to mock

- The server under test: if the suite verifies the app + its backend
  integration, intercepting that API makes the test meaningless. Mock only
  *third-party* boundaries, or test the real API via a controlled
  environment.
- `page.goto()` navigation that the test depends on — routing over the app's
  own document requests breaks the flow the test is verifying.
- Responses whose timing you are testing (e.g., loading states): use
  `route.fulfill` with a small artificial delay or the API's
  `page.clock`/routing delay, never a fixed `waitForTimeout`.

## Asserting on traffic

Capture what the app sent, then assert on it:

```ts
let tokenizeBody: string | undefined;
page.on('request', (request) => {
  if (request.url().includes('/api/payments/tokenize')) tokenizeBody = request.postData();
});
// ... drive the flow ...
expect(JSON.parse(tokenizeBody!)).toMatchObject({ amount: 4990, currency: 'usd' });
```

Use `page.on('response')` to wait for a specific status instead of guessing
when the network settled:

```ts
await page.waitForResponse((response) => response.url().includes('/api/orders') && response.status() === 201);
```

## Emulating network conditions

```ts
await page.route('**/*', (route) =>
  route.continue().catch(() => {})
);
await page.context().setOffline(true); // test offline/error states
// or throttle via context options: offline, latency, downloadThroughput...
```

## Related

- Locators that survive the mocked world: `02-selectors.md`.
- Running these tests in parallel without interference: `04-parallel-workers-and-sharding.md`.
