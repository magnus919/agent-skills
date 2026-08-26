---
name: tmdb
description: Search and discover movies, TV shows, and trending content via The Movie
  Database (TMDb) API v3. Use when the user asks about movies, TV, film, cinema, genres,
  certifications, ratings, cast, upcoming releases, or trending media.
license: MIT
compatibility: Requires TMDB_ACCESS_TOKEN or TMDB_API_KEY env var (free at themoviedb.org/settings/api),
  Python 3.8+, and the `requests` library.
metadata:
  tags: tmdb, movies, tv, film, cinema, entertainment, media-discovery, api-client
  sources: https://developer.themoviedb.org/reference, https://www.themoviedb.org/settings/api
---

# tmdb — Movie & TV Discovery from the Terminal

Search movies and TV shows by keyword, discover by genre/certification/rating/date, check trending and upcoming releases, browse genre lists, and view US certification ratings — all from TMDb's v3 API.

## Setup

1. Get a free API key or access token at [themoviedb.org/settings/api](https://www.themoviedb.org/settings/api)
2. Set one of these environment variables:

```bash
export TMDB_ACCESS_TOKEN="your-tmdb-access-token"   # preferred
# OR
export TMDB_API_KEY="your-tmdb-api-key"
```

`--help` and `--dry-run` work without credentials (lazy auth).

## Essential Commands

### movie search — Search movies by keyword

```bash
tmdb movie search --term "dune"                  # basic search
tmdb movie search --term "inception" --limit 5   # top 5 results
tmdb movie search --term "arrival" --json         # machine-readable
```

Shows: title, release year, vote average.

### movie discover — Discover movies by genre, certification, rating, and date

```bash
tmdb movie discover --genre horror                           # horror movies
tmdb movie discover --genre horror --certification R         # horror, R-rated
tmdb movie discover --genre comedy --rating 7 --limit 15     # highly-rated comedy
tmdb movie discover --from 2024-01-01 --to 2024-12-31        # released in 2024
tmdb movie discover --genre scifi --from 2026-05-01          # recent sci-fi
tmdb movie discover --genre thriller --certification R \
  --rating 6 --from 2025-01-01 --limit 20                        # compound filter
```

### movie upcoming — Upcoming movie releases

```bash
tmdb movie upcoming                         # next 10 upcoming
tmdb movie upcoming --limit 20              # more results
tmdb movie upcoming --json                  # machine-readable
```

### tv search — Search TV shows by keyword

```bash
tmdb tv search --term "severance"           # basic TV search
tmdb tv search --term "the expanse" --limit 5
tmdb tv search --term "silo" --json
```

Shows: name, first air year, vote average.

### tv discover — Discover TV shows by genre, rating, and air date

```bash
tmdb tv discover --genre sci-fi                    # sci-fi shows
tmdb tv discover --genre drama --rating 7          # critically-acclaimed drama
tmdb tv discover --genre comedy --from 2025-01-01  # recent comedy
```

### trending — Trending content across day or week

```bash
tmdb trending                              # trending movies this week
tmdb trending --type tv                    # trending TV this week
tmdb trending --type all --window day      # all media trending today
tmdb trending --limit 20 --json            # top 20 as JSON
```

### genre list — Browse available genres

```bash
tmdb genre list --type movie               # all movie genres
tmdb genre list --type tv                  # all TV genres
tmdb genre list --type movie --json
```

### certification — View US movie certification ratings

```bash
tmdb certification                          # US certification list
tmdb certification --json                   # machine-readable
```

## Global Flags

These flags work in any position before, between, or after subcommands:

```bash
tmdb --json movie search --term "dune"             # JSON output
tmdb movie search --term "dune" --json             # json after subcommand
tmdb --dry-run movie discover --genre horror       # preview without API call
tmdb --quiet trending                              # suppress diagnostic output
tmdb --verbose movie search --term "alien"         # verbose logging
```

## Known Gotchas

- **Genre name matching is case-insensitive** — `--genre Horror`, `--genre horror`, and `--genre HORROR` all work. Names are matched via substring, so `--genre sci` matches "Sci-Fi" and "Science Fiction".
- **Certifications are US-only** — The `--certification` flag and the `certification` subcommand only return/accept US ratings (G, PG, PG-13, R, NC-17). International certifications are not available.
- **API version** — This CLI wraps TMDb API v3. Endpoints and response shapes follow the v3 spec.
- **Pagination defaults** — Every command defaults to 10 results. Use `--limit` to get more. The CLI does not auto-paginate beyond the first page.
- **Now-playing is defined** — The `movie now-playing` subcommand is registered in argparse and maps to the TMDb `/movie/now_playing` endpoint.

## References

- [scripts/tmdb](scripts/tmdb) — The CLI binary. Built following the cli-builder patterns: non-interactive, `--json`, `--dry-run`, `--quiet`, `--verbose`, dual-output via `emit()`, lazy auth, structured logging.
- [TMDb API v3 Reference](https://developer.themoviedb.org/reference) — Official API documentation.
- [TMDb API Settings (get a key)](https://www.themoviedb.org/settings/api) — Free API key registration.
