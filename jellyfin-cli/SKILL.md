---
name: jellyfin-cli
description: >-
  Query your Jellyfin media server from the terminal — recently added movies
  and episodes, search across your library, browse libraries, and check server
  info and stats. Use when the user asks about Jellyfin, media server, movies,
  TV shows, recently added content, or their media library.
license: MIT
compatibility: Requires JELLYFIN_URL (default http://localhost:8096) and
  JELLYFIN_API_KEY env vars; Python 3.8+ and the `requests` library. Generate
  an API key at Dashboard → API Keys in the Jellyfin admin panel.
metadata:
  tags: [jellyfin, media-server, movies, tv, episodes, recently-added, library,
    home-media, api-client]
  sources:
    - https://jellyfin.org/docs/general/clients/api
    - https://jellyfin.org/downloads
---

# jellyfin-cli — Jellyfin Media Server from the Terminal

Query recently added movies and TV episodes, search your media library, list libraries, check server info, and view library statistics — all from your Jellyfin server's REST API.

## Setup

1. Make sure your Jellyfin server is running and accessible.
2. Generate an API key in the Jellyfin Dashboard → **API Keys** → `+` to create a new key.
3. Set these environment variables:

```bash
export JELLYFIN_URL="http://your-server:8096"   # include protocol and port
export JELLYFIN_API_KEY="your-api-key-here"
```

`--help` and `--dry-run` work without credentials (lazy auth).

## Essential Commands

### info — Server information

```bash
jellyfin-cli info                           # server name, version, OS, user count
jellyfin-cli info --json                    # machine-readable
jellyfin-cli --dry-run info                 # preview the API call
```

Shows: server name, version, operating system, number of users.

### recent — Recently added media

```bash
jellyfin-cli recent                         # last 10 items added
jellyfin-cli recent --limit 20              # more results
jellyfin-cli recent --movies                # only recently added movies
jellyfin-cli recent --episodes              # only recently added episodes
jellyfin-cli recent --movies --limit 5      # top 5 recently added movies
jellyfin-cli recent --json                  # machine-readable
```

Shows: name, type (Movie/Episode), production year, series name (for episodes), date added.

### search — Search your media library

```bash
jellyfin-cli search --query "dune"                # search everything
jellyfin-cli search --query "dune" --type Movie   # movies only
jellyfin-cli search --query "star trek" --type Series,Episode
jellyfin-cli search --query "inception" --limit 5 # top 5 results
jellyfin-cli search --query "dune" --json         # machine-readable
```

The `--type` flag accepts a comma-separated list of item types (e.g. `Movie,Series,Episode`).

### libraries — List media libraries

```bash
jellyfin-cli libraries                     # all configured libraries
jellyfin-cli libraries --json              # machine-readable
```

Shows: library name, collection type (movies, tvshows, music, etc.), library ID.

### stats — Library statistics

```bash
jellyfin-cli stats                         # movie, series, episode, song counts
jellyfin-cli stats --json                  # machine-readable
```

Shows: total count of movies, series, episodes, and songs in the library.

## Global Flags

These flags work anywhere in the command — before or after the subcommand:

```bash
jellyfin-cli --json recent --limit 5               # JSON output
jellyfin-cli recent --limit 5 --json               # same result, after subcommand
jellyfin-cli --dry-run search --query "dune"       # preview without API call
jellyfin-cli --quiet info                          # suppress diagnostic output
jellyfin-cli --verbose libraries                   # verbose logging
```

| Flag | Effect |
|------|--------|
| `--json` | Output machine-readable JSON instead of human-readable text |
| `--dry-run` | Show what API call would be made without executing it |
| `--quiet` | Suppress non-essential diagnostic output |
| `--verbose` | Enable verbose/debug logging |

## Known Gotchas

- **JELLYFIN_URL must include protocol and port** — Both are required, e.g. `http://192.168.1.100:8096`. A bare hostname or IP without `http://` and `:8096` will fail. The default is `http://localhost:8096`.
- **Admin user auto-discovery** — The `recent` command automatically discovers the first admin user on the server to fetch their recently added items. If no admin user exists (unusual), it returns "No admin user found."
- **Episode filtering is post-query** — The `--episodes` flag filters the "latest items" endpoint results by `Type == "Episode"` after fetching. This means the returned count may be smaller than `--limit` if there aren't enough episodes among the latest items. Similarly, `--movies` filters by `Type == "Movie"`.
- **Search type values** — The `--type` flag for `search` uses Jellyfin item type names (e.g. `Movie`, `Series`, `Episode`, `MusicArtist`, `MusicAlbum`). Multiple types are comma-separated without spaces.
- **API key location** — Generate the key in the Jellyfin Dashboard under **Dashboard → API Keys**. The key is sent as the `X-Emby-Token` header.
- **Lazy auth** — `--help` and `--dry-run` work even when `JELLYFIN_URL` and `JELLYFIN_API_KEY` are not set. All other commands will fail immediately if the env vars are missing or invalid.
- **No pagination** — Every command returns a single page of results. The CLI does not auto-paginate beyond the first response. Use `--limit` to control result size.

## References

- [scripts/jellyfin-cli](scripts/jellyfin-cli) — The CLI binary. Built following the cli-builder patterns: non-interactive, `--json`, `--dry-run`, `--quiet`, `--verbose`, dual-output via `emit()`, lazy auth, structured logging.
- [Jellyfin API Docs](https://jellyfin.org/docs/general/clients/api) — Official API documentation.
- [Jellyfin Downloads](https://jellyfin.org/downloads) — Server download and setup guide.
