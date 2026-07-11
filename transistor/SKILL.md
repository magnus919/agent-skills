---
name: transistor
description: 'Manage Transistor.fm podcast hosting from the terminal: view shows,
  list episodes, check analytics, and get subscriber counts. Use when the user mentions
  Transistor, podcast hosting, podcast analytics, show management, or episode tracking.'
license: MIT
compatibility: Requires TRANSISTOR_API_KEY env var (from Settings → API Keys in the
  Transistor.fm dashboard), Python 3.8+, and the `requests` library. Uses the Transistor.fm
  v1 REST API with JSON:API format responses.
metadata:
  tags: transistor, podcast, podcast-hosting, analytics, api-client
  sources: https://transistor.fm/, https://developers.transistor.fm/
---

# transistor-cli — Transistor.fm Podcast Hosting

Manage your Transistor.fm podcast shows, episodes, subscribers, and analytics from the terminal. Uses the Transistor.fm v1 REST API.

## Setup

1. Get your API key from Transistor.fm: **Settings → API Keys** (bottom of the page)
2. Set the environment variable:

```bash
export TRANSISTOR_API_KEY="your-transistor-api-key"
```

`--help` and `--dry-run` work without credentials.

## Essential Commands

### user — Current user info

```bash
transistor-cli user                                # email and timezone
transistor-cli user --json                         # machine-readable
```

### shows — List all shows

```bash
transistor-cli shows                               # all shows with episode/subscriber counts
transistor-cli shows --json                        # machine-readable with IDs
```

Shows title, episode count, subscriber count, and ID.

### episodes — List episodes

```bash
transistor-cli episodes                            # last 20 episodes across all shows
transistor-cli episodes --show 12345               # filter by show ID
transistor-cli episodes --limit 50                 # more results
transistor-cli episodes --show 12345 --json        # machine-readable
```

Get show IDs from `transistor-cli shows --json`. Shows season/episode numbers, title, status, duration, and publish date.

### analytics — Download and play analytics

```bash
transistor-cli analytics                           # totals across all shows
transistor-cli analytics --show 12345              # filter by show ID
transistor-cli analytics --json                    # machine-readable with full totals
```

Shows total downloads and plays (when available).

## Global Flags

All flags work in any position:

```bash
transistor-cli --json shows                        # flag before subcommand
transistor-cli shows --json                        # flag after subcommand
transistor-cli --dry-run episodes                  # preview (no API call)
transistor-cli --force episodes --limit 100        # override safety checks
transistor-cli --quiet shows                       # suppress non-essential output
transistor-cli --verbose episodes                  # detailed logging
```

Extra flag vs other CLIs: `--force` overrides internal safety checks (e.g. large limits).

## Known Gotchas

- **API key from Settings → API Keys** — Not from the user profile or account page. Navigate to Settings → API Keys at the bottom of the Transistor.fm dashboard.
- **JSON:API format** — Transistor uses the JSON:API spec. All responses are nested under a `data` key, and attributes are under `data[].attributes`. The CLI unwraps these for display, but raw JSON output shows the full JSON:API structure.
- **Show IDs are required for filtered queries** — Use `transistor-cli shows --json` to get show IDs first, then pass them to `--show` for episodes and analytics.
- **Pagination uses cursor-based pagination** — The `--limit` flag controls the page size. Default is 20 for episodes. The API returns `meta` with pagination info.
- **Analytics are totals only** — The analytics endpoint returns aggregate totals (downloads, plays). Per-episode analytics are not available via this CLI.
- **Transistor API is append-only via this CLI** — The CLI implements GET endpoints for reading. Creating/updating shows or episodes is not covered here.
- **Rate limits** — Transistor.fm has rate limits. The CLI does not auto-retry on 429 responses.

## References

- [scripts/transistor-cli](scripts/transistor-cli) — The CLI binary. Built following the cli-builder patterns: `--json`, `--dry-run`, `--force`, `--quiet`, `--verbose`, dual-output via `emit()`, lazy auth.
- [Transistor API Docs](https://developers.transistor.fm/) — Official API reference.
- [Transistor.fm Dashboard](https://dashboard.transistor.fm/) — Settings → API Keys for your API key.
