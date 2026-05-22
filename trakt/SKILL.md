---
name: trakt
description: >-
  Discover trending, anticipated, and popular movies and TV shows via the
  Trakt.tv API from the terminal. No authentication required for read-only
  discovery. Use when the user asks about what to watch, trending movies,
  popular shows, or media discovery.
license: MIT
compatibility: Requires TRAKT_CLIENT_ID env var (free from
  trakt.tv/oauth/applications), Python 3.8+, and the `requests` library.
  No OAuth or user login needed for discovery endpoints.
metadata:
  tags: [trakt, media-discovery, movies, tv-shows, trending, api-client]
  sources:
    - https://trakt.tv/
    - https://trakt.docs.apiary.io/
---

# trakt-cli — Trakt.tv Media Discovery

Discover trending, anticipated, and popular movies and TV shows from the terminal. Uses the Trakt.tv API v2 with a read-only Client ID — no user authentication required.

## Setup

1. Register an app at [trakt.tv/oauth/applications](https://trakt.tv/oauth/applications) to get a Client ID
2. Set the environment variable:

```bash
export TRAKT_CLIENT_ID="your-trakt-client-id"
```

No OAuth token, no user login needed for any of the commands below. `--help` and `--dry-run` work without credentials.

## Essential Commands

### movie trending — Trending movies

```bash
trakt-cli movie trending                          # top 10 trending movies
trakt-cli movie trending --limit 25               # more results
trakt-cli movie trending --json                   # machine-readable with TMDb IDs
```

### movie anticipated — Most anticipated movies

```bash
trakt-cli movie anticipated                       # top 10 anticipated
trakt-cli movie anticipated --limit 5             # top 5
trakt-cli movie anticipated --json                # machine-readable
```

### movie popular — Most popular movies

```bash
trakt-cli movie popular                           # top 10 popular movies
trakt-cli movie popular --limit 25                # more results
```

### tv trending — Trending TV shows

```bash
trakt-cli tv trending                             # top 10 trending shows
trakt-cli tv trending --limit 25                  # more results
trakt-cli tv trending --json                      # machine-readable with TVDB IDs
```

### tv anticipated — Most anticipated TV shows

```bash
trakt-cli tv anticipated                          # top 10 anticipated shows
trakt-cli tv anticipated --limit 5                # top 5
```

### tv popular — Most popular TV shows

```bash
trakt-cli tv popular                              # top 10 popular shows
trakt-cli tv popular --limit 25                   # more results
```

Each result shows: title, year, network (for TV), TMDb/TVDB ID, and tagline (for movies).

## Global Flags

All flags work in any position:

```bash
trakt-cli --json movie trending                   # flag before subcommand
trakt-cli movie trending --json                   # flag after subcommand
trakt-cli --dry-run movie trending                # preview (no API call)
trakt-cli --quiet movie trending                  # suppress non-essential output
trakt-cli --verbose movie trending                # detailed logging
```

## Known Gotchas

- **Read-only by design** — The CLI only uses the Client ID flow. No OAuth, no writing to your Trakt lists. All endpoints are public discovery endpoints.
- **No auth needed for these commands** — The trending, anticipated, and popular endpoints are public. Skip the setup if you only want to preview with `--dry-run`.
- **Rate limiting** — Trakt API v2 has rate limits (~1,000 calls per 5 minutes for free apps). The CLI does not auto-retry on 429 responses.
- **TRAKT_CLIENT_ID is required at runtime** — Unlike `--dry-run` which skips the API call, running live commands without the env var will fail with a clear error message.
- **Pagination defaults to page 1** — The CLI uses `--limit` for the results per page. Default is 10, max is typically 50.
- **TMDb/TVDB IDs** — Use `--json` to get the full IDs object (TMDb for movies, TVDB for shows) which is useful for lookups in other tools like Radarr/Sonarr.

## References

- [scripts/trakt-cli](scripts/trakt-cli) — The CLI binary. Built following the cli-builder patterns: `--json`, `--dry-run`, `--quiet`, `--verbose`, dual-output via `emit()`, lazy auth.
- [Trakt API Docs](https://trakt.docs.apiary.io/) — Official API reference.
- [Trakt OAuth Applications](https://trakt.tv/oauth/applications) — Register an app to get your Client ID.
