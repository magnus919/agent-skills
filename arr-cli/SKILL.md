---
name: arr-cli
description: >-
  Manage your media library with Radarr (movies) and Sonarr (TV series)
  from the terminal. Search and list movies and series, check calendars,
  view wanted/missing episodes, and monitor library status. Use when the
  user mentions Radarr, Sonarr, the *arr stack, movie automation, TV
  series management, or media server setup.
license: MIT
compatibility: Requires ARR_SERVER_RADARR and ARR_KEY_RADARR (for Radarr)
  or ARR_SERVER_SONARR and ARR_KEY_SONARR (for Sonarr), Python 3.8+, and
  the `requests` library. API keys from each app's Settings → General.
metadata:
  tags: [radarr, sonarr, arr-stack, media-server, movie-automation, tv-series, api-client]
  sources:
    - https://radarr.video/
    - https://sonarr.tv/
---

# arr-cli — Radarr + Sonarr Media Library Management

Two CLIs, one skill wrapper. `radarr-cli` for movies, `sonarr-cli` for TV series. Radarr and Sonarr share the same API pattern but use separate server URLs and API keys.

## Setup

1. Get API keys from each app: Settings → General → API Key
2. Set environment variables:

```bash
# Radarr
export ARR_SERVER_RADARR="http://localhost:7878"
export ARR_KEY_RADARR="your-radarr-api-key"

# Sonarr
export ARR_SERVER_SONARR="http://localhost:8989"
export ARR_KEY_SONARR="your-sonarr-api-key"
```

`--help` and `--dry-run` work without credentials on both CLIs.

## Radarr Commands

### status — Server info

```bash
radarr-cli status                       # version, OS, database
radarr-cli status --json                # machine-readable
```

### movies — List your movie library

```bash
radarr-cli movies                       # all movies
radarr-cli movies --status released     # filter by status (released, inCinemas, announced)
radarr-cli movies --limit 10            # top 10
radarr-cli movies --json                # machine-readable
```

Icons: ✅ = has file, 👁️ = monitored but missing, 🚫 = unmonitored.

### lookup — Search for movies to add

```bash
radarr-cli lookup --term "Dune"                 # search by title
radarr-cli lookup --term "Dune" --json          # includes TMDb ID and overview
```

### add — Add movies to library

```bash
radarr-cli add --tmdb-id 12345 --quality-profile 4 --search    # add with auto-search
radarr-cli add --tmdb-id 12345 --quality-profile 5 --dry-run   # preview without adding
```

Use `--quality-profile 4` for HD-1080p, `5` for Ultra-HD. Omit `--search` to add unmonitored.

### quality-profile — View quality profiles

```bash
radarr-cli quality-profile                   # list all quality profiles
radarr-cli quality-profile 4                 # inspect HD-1080p specifics (cutoff, tiers)
radarr-cli quality-profile --json            # machine-readable
```

Each profile shows which quality tiers are allowed (✓) or blocked (✗), and the cutoff tier.

### calendar — Upcoming releases

```bash
radarr-cli calendar                             # upcoming releases
radarr-cli calendar --json                      # machine-readable
```

### collections — Movie collections

```bash
radarr-cli collections                          # list all collections
radarr-cli collections --json                   # with movie counts
```

## Sonarr Commands

### status — Server info

```bash
sonarr-cli status                        # version, OS, database
sonarr-cli status --json                 # machine-readable
```

### series — List your TV series

```bash
sonarr-cli series                        # all series
sonarr-cli series --status continuing    # filter (continuing, ended, upcoming)
sonarr-cli series --limit 10             # top 10
sonarr-cli series --json                 # machine-readable
```

### lookup — Search for series to add

```bash
sonarr-cli lookup --term "Severance"            # search by title
sonarr-cli lookup --term "Severance" --json     # with TVDB ID
```

### add — Add series to library

```bash
sonarr-cli add --tvdb-id 12345 --quality-profile 4 --series-type Standard --search   # standard weekly show
sonarr-cli add --tvdb-id 12345 --quality-profile 4 --series-type Daily --search       # daily show (talk show, news)
sonarr-cli add --tvdb-id 12345 --quality-profile 4 --series-type Anime --no-season-folder --search  # anime with absolute numbering
```

**Series types:** `Standard` (default, regular weekly episodes), `Daily` (airing daily, e.g. talk shows/news), `Anime` (absolute episode numbering, no season folders). Use `--no-season-folder` for flat episode storage.

### episodes — List episodes of a series

```bash
sonarr-cli episodes --series-id 1               # all episodes
sonarr-cli episodes --series-id 1 --limit 10    # recent episodes
sonarr-cli episode get 1                        # details for a specific episode
sonarr-cli episode-files --series-id 1          # downloaded episode files with quality info
```

Get the series ID from `sonarr-cli series --json`.

### calendar — Upcoming episodes

```bash
sonarr-cli calendar                              # upcoming episodes
sonarr-cli calendar --json                       # machine-readable
```

### wanted — Missing episodes

```bash
sonarr-cli wanted                                # missing episodes
sonarr-cli wanted --limit 50                     # more results
sonarr-cli wanted --json                         # machine-readable
```

### quality-profile — View quality profiles

```bash
sonarr-cli quality-profile                       # list all quality profiles
sonarr-cli quality-profile 4                     # inspect HD-1080p
```

## Global Flags

All flags work in any position on both CLIs:

```bash
radarr-cli --json movies                        # flag before subcommand
radarr-cli movies --json                        # flag after subcommand
radarr-cli --dry-run lookup --term "Dune"        # preview
sonarr-cli --quiet series                        # suppress non-essential output
```

## Known Gotchas

- **Separate credentials** — Radarr and Sonarr use different API keys and different ports (7878 vs 8989). Set both ARR_KEY_RADARR and ARR_KEY_SONARR.
- **API keys from Settings → General** — Not from the user profile page. Look under the General settings tab in each app.
- **Movie/series IDs are the *arr internal IDs**, not TMDb/TVDB IDs. Use `lookup` first to find the internal ID, or use `--json` to get both.
- **Quality profile IDs** default to 4 (HD-1080p). Override by setting the profile ID in your scripts if you use a different profile.
- **Calendar can be slow** on large libraries. Sonarr's calendar may take several seconds to respond.
- **Sonarr wanted endpoint is paginated** — it returns a `totalRecords` field. Use `--limit` to control page size.

## References

- [scripts/radarr-cli](scripts/radarr-cli) — Radarr CLI binary. cli-builder patterns: `--json`, `--dry-run`, `--quiet`, `--verbose`, dual-output via `emit()`, lazy auth.
- [scripts/sonarr-cli](scripts/sonarr-cli) — Sonarr CLI binary. Same patterns as radarr-cli.
- [Radarr API docs](https://radarr.video/docs/api/) — Official API reference.
- [Sonarr API docs](https://sonarr.tv/docs/api/) — Official API reference.
