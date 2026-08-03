# Scraping and Headless Browsing

> **Last Updated:** 2026-08-03

Use Playwright as a headless browser for pages that need JavaScript to render:
load the page, extract structured records, validate them, and save — the
extract → validate → save loop. This is browser *automation*, not a generic
HTTP client; for static content prefer a plain HTTP request (see
`SKILL.md` → When not to use).

## The loop

```python
# Rough shape — the same pattern in JS: launch, context, page, extract, validate, save.
# (Playwright's Python package mirrors the Node API 1:1.)
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_context(
        user_agent="research-bot/1.0 (+contact@example.com)",
        viewport={"width": 1280, "height": 800},
    ).new_page()
    page.goto("https://docs.example.com/catalog", wait_until="networkidle")
    records = []
    for row in page.locator("table tbody tr").all():
        cells = row.locator("td").all_inner_texts()
        records.append(dict(zip(["name", "version", "license"], cells)))
    # validate: every record has the required fields
    valid = [r for r in records if r["name"] and r["version"]]
    # save: write one JSON/CSV artifact, bounded
    ...
```

## Extract → validate → save, explicitly

1. **Extract** — scope locators to the repeating container; use
   `.all_inner_texts()` / attribute reads to build plain records. Never return
   raw HTML blobs.
2. **Validate** — check required fields, types, and invariants *before* saving;
   drop or flag records that fail. A scrape that saves garbage is worse than
   one that reports failure.
3. **Save** — write one bounded artifact (JSON/CSV) per scrape with the
   timestamp and source URL in the artifact. Do not dump page HTML or screenshots
   of protected content into chat (hard boundaries in `SKILL.md`).

## Pagination and infinite scroll

- **Pagination**: follow the "next" button until it is disabled or the count
  target is reached:

  ```ts
  while (await nextButton.isEnabled() && records.length < MAX) {
    // extract current page...
    await nextButton.click();
    await expect(page.locator('tbody tr').first()).toBeVisible();
  }
  ```
- **Infinite scroll**: scroll to the bottom and wait for the container's
  height/record count to grow, with a max-iteration guard.
- Always cap: `MAX_RECORDS` and `MAX_PAGES` with a clear stop message when hit.

## Politeness and legality (hard constraints)

- Respect `robots.txt`, the site's terms of service, and rate limits. Playwright
  does not enforce them; the operator does.
- Add a delay between page loads (e.g., 1–3 s) and keep concurrency low; a burst
  of headless browsers is indistinguishable from an attack.
- Set an identifying `user_agent` with a contact address.
- **No credential harvesting, no personal data extraction, no auth-session
  persistence into committed files.** Storage state (`context.storage_state()`)
  must never be committed (see hard boundaries).
- **Challenge pages**: Cloudflare/DDoS-GUARD challenges are out of scope here —
  route to [flaresolverr](../flaresolverr/SKILL.md).

## Related

- Locating repeating elements robustly: `02-selectors.md`.
- Blocking analytics/trackers while scraping: `03-network-interception-and-mocking.md`.
- Debugging a scrape that misses content (headed, slow-mo, trace):
  `07-accessibility-and-debugging.md`.
