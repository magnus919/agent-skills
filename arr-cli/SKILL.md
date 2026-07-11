---
name: arr-cli
description: Manage your Radarr (movies) and Sonarr (TV series) media library from
  the terminal. Search and browse movies/series, add new content, check calendars,
  view queue and download history, inspect quality profiles, and trigger searches.
  Use when the user mentions Radarr, Sonarr, the *arr stack, adding a movie or series,
  checking the library, finding something to watch, what's in the queue, download
  history, upcoming releases, media server setup, or movie/TV automation.
license: MIT
compatibility: Python 3.8+ with `requests` library. Requires ARR_SERVER_RADARR and
  ARR_KEY_RADARR (for Radarr) or ARR_SERVER_SONARR and ARR_KEY_SONARR (for Sonarr).
  API keys from each app's Settings → General.
metadata:
  tags: radarr, sonarr, arr-stack, media-server, movie-automation, tv-series, api-client
  sources: https://radarr.video/, https://sonarr.tv/
---

# arr-cli — Radarr + Sonarr Media Library Management

Two CLIs, one skill wrapper. `radarr-cli` for movies, `sonarr-cli` for TV series.

## Quick Setup

```bash
# Radarr
export ARR_SERVER_RADARR="http://localhost:7878"
export ARR_KEY_RADARR="your-radarr-api-key"

# Sonarr
export ARR_SERVER_SONARR="http://localhost:8989"
export ARR_KEY_SONARR="your-sonarr-api-key"
```

`--help` and `--dry-run` work without credentials.

## When to Use Which

| User says... | Load... |
|---|---|
| "list my movies", "what's in Radarr", "show me the library" | `radarr-cli movies [--limit N] [--status released\|inCinemas\|announced]` |
| "add this movie", "is this in Radarr", "search for a movie" | `radarr-cli lookup --term "title"` then `radarr-cli add --tmdb-id N --root /movies` |
| "what's coming up", "upcoming releases" | `radarr-cli calendar` or `sonarr-cli calendar` |
| "what's in the queue", "download progress" | `radarr-cli queue` or `sonarr-cli queue` |
| "show me history", "what was downloaded" | `radarr-cli history` or `sonarr-cli history` |
| "list my series", "what's on Sonarr" | `sonarr-cli series [--limit N] [--status continuing\|ended\|upcoming]` |
| "add this series", "find a TV show" | `sonarr-cli lookup --term "title"` then `sonarr-cli add --tvdb-id N --root /tv` |
| "what's missing", "wanted episodes" | `sonarr-cli wanted` |
| "check quality profiles", "what profiles exist" | `radarr-cli quality-profile` or `sonarr-cli quality-profile` |
| "search for a movie/series" (already added) | `radarr-cli search --movie-id N` or `sonarr-cli search --series-id N` |
| "where are my root folders", "storage paths" | `radarr-cli root-folder` or `sonarr-cli root-folder` |
| "what episodes are downloaded", "episode files" | `sonarr-cli episode-file --series-id N` |

## Quick Reference

**Global flags** (work anywhere in arg list): `--json`, `--dry-run`, `--force`, `--quiet`, `--verbose`

```bash
# System info
radarr-cli status
sonarr-cli status

# List with filters and JSON output (pipe to jq for scripting)
radarr-cli movies --limit 5 --status released --json | jq '.movies[].title'
sonarr-cli series --limit 5 --status continuing --json | jq '.series[].title'

# Discover and add a movie (always use TMDb ID, not title)
radarr-cli lookup --term "Dune"
radarr-cli add --tmdb-id 12345 --root /movies --quality-profile 4 --search

# Add with specific availability (for unreleased films)
radarr-cli add --tmdb-id 99999 --root /movies --quality-profile 5 --availability announced

# Discover and add a series (always use TVDb ID)
sonarr-cli lookup --term "Severance"
sonarr-cli add --tvdb-id 77526 --root /tv --quality-profile 4 --series-type Standard --search

# Add an anime series (flat episode storage, absolute numbering)
sonarr-cli add --tvdb-id 12345 --root /tv --quality-profile 4 --series-type Anime --no-season-folder --search

# Preview before adding (no side effects)
radarr-cli --dry-run add --tmdb-id 550 --root /movies --quality-profile 4

# Trigger a search for something already in your library
radarr-cli search --movie-id 5
sonarr-cli search --series-id 5

# Queue and history
radarr-cli queue --limit 10
radarr-cli history --limit 5 --event-type grabbed

# Discover root folder paths before adding
radarr-cli root-folder
sonarr-cli root-folder

# Quality profiles
radarr-cli quality-profile           # list all
radarr-cli quality-profile 4         # inspect HD-1080p details with tier checkmarks
```

**IMPORTANT — lookup side effect:** `radarr-cli lookup --tmdb-id N` silently adds an unmonitored record. For pure existence checks, use `radarr-cli --json movies | jq '.[] | select(.tmdbId == N)'` instead.

**Default quality profile:** HD-1080p (id: 4). Override with `--quality-profile N`.

## Reference Files

| File | Contents |
|------|----------|
| `references/radarr-commands.md` | Full Radarr command reference with all flags and examples |
| `references/sonarr-commands.md` | Full Sonarr command reference with all flags and examples |
| `references/media-discovery.md` | Cross-referencing TMDb/Trakt discovery results against your library |
| `references/troubleshooting.md` | Pitfalls, FAQs, and when NOT to use |

## When NOT to Use

- **Media playback** — use Jellyfin for watching content. This CLI only manages the library.
- **First-time *arr setup** — this skill assumes Radarr/Sonarr are already installed and configured. See `radarr.video` or `sonarr.tv` for installation guides.
- **Bulk imports** — for large-scale library migrations, prefer Radarr/Sonarr's built-in import features or manual disk operations.

## First-Time Loading

1. Set the env vars above (API keys from each app's Settings → General)
2. Test with `radarr-cli status` — you should see version and OS info
3. Browse your library: `radarr-cli movies --limit 5`
4. For cross-reference workflows (discovering new content via TMDb/Trakt), see `references/media-discovery.md`
