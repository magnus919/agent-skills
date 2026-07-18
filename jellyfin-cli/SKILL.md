---
name: jellyfin-cli
description: Query your Jellyfin media server from the terminal — recently added movies
  and episodes, search across your library, browse libraries, and check server info
  and stats. Use when the user asks about Jellyfin, media server, movies, TV shows,
  recently added content, or their media library.
license: MIT
compatibility: Requires JELLYFIN_URL (default http://localhost:8096) and JELLYFIN_API_KEY
  env vars; `recent` also requires JELLYFIN_USER_ID or --user-id. Python 3.8+ and
  the `requests` library. Generate an API key at Dashboard → API Keys in the Jellyfin admin panel.
metadata:
  tags: jellyfin, media-server, movies, tv, episodes, recently-added, library, home-media,
    api-client
  sources: https://jellyfin.org/docs/general/clients/api, https://jellyfin.org/downloads
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
export JELLYFIN_USER_ID="your-jellyfin-user-id" # required by recent
```

Run the bundled CLI as `scripts/jellyfin-cli`. `--help` and `--dry-run` work without credentials.

## Essential Commands

### info — Server information

```bash
scripts/jellyfin-cli info                           # server name, version, OS, user count
scripts/jellyfin-cli info --json                    # machine-readable
scripts/jellyfin-cli --dry-run info                 # preview API requests
```

Shows: server name, version, operating system, number of users.

### recent — Recently added media

```bash
scripts/jellyfin-cli recent                         # last 10 items added
scripts/jellyfin-cli recent --limit 20              # more results
scripts/jellyfin-cli recent --movies                # only recently added movies
scripts/jellyfin-cli recent --episodes              # only recently added episodes
scripts/jellyfin-cli recent --user-id USER_ID       # override JELLYFIN_USER_ID
scripts/jellyfin-cli recent --movies --limit 5      # top 5 recently added movies
scripts/jellyfin-cli recent --json                  # machine-readable
```

Uses Jellyfin's current `/Items/Latest` endpoint. `--movies` and `--episodes` send `includeItemTypes` to the server, so the requested limit applies to the selected media type. Shows: name, type (Movie/Episode), production year, series name (for episodes), date added.

### search — Search your media library

```bash
scripts/jellyfin-cli search --query "dune"                # search everything
scripts/jellyfin-cli search --query "dune" --type Movie   # movies only
scripts/jellyfin-cli search --query "star trek" --type Series,Episode
scripts/jellyfin-cli search --query "inception" --limit 5 # top 5 results
scripts/jellyfin-cli search --query "dune" --json         # machine-readable
```

The `--type` flag accepts a comma-separated list of item types (e.g. `Movie,Series,Episode`).

### libraries — List media libraries

```bash
scripts/jellyfin-cli libraries                     # all configured libraries
scripts/jellyfin-cli libraries --json              # machine-readable
```

Shows: library name, collection type (movies, tvshows, music, etc.), library ID.

### stats — Library statistics

```bash
scripts/jellyfin-cli stats                         # movie, series, episode, song counts
scripts/jellyfin-cli stats --json                  # machine-readable
```

Shows: total count of movies, series, episodes, and songs in the library.

## Global Flags

These flags work anywhere in the command — before or after the subcommand:

```bash
scripts/jellyfin-cli --json recent --limit 5               # JSON output
scripts/jellyfin-cli recent --limit 5 --json               # same result, after subcommand
scripts/jellyfin-cli --dry-run search --query "dune"       # preview request without API call
```

| Flag | Effect |
|------|--------|
| `--json` | Output machine-readable JSON instead of human-readable text |
| `--dry-run` | Show each request path and parameters without executing it |

## Known Gotchas

- **JELLYFIN_URL must include protocol and port** — Both are required, e.g. `http://192.168.1.100:8096`. A bare hostname or IP without `http://` and `:8096` will fail. The default is `http://localhost:8096`.
- **Recent requires an explicit user** — Set `JELLYFIN_USER_ID` or pass `recent --user-id USER_ID`. The CLI never selects an administrator automatically. A real recent request without either value fails before network access; dry-run previews the request with a null user ID.
- **Recent type filtering is server-side** — `--movies` and `--episodes` become the `/Items/Latest` `includeItemTypes` parameter before `limit`; no local filtering is applied.
- **Search type values** — The `--type` flag for `search` uses Jellyfin item type names (e.g. `Movie`, `Series`, `Episode`, `MusicArtist`, `MusicAlbum`). Multiple types are comma-separated without spaces.
- **API key location** — Generate the key in the Jellyfin Dashboard under **Dashboard → API Keys**. The key is sent as the `X-Emby-Token` header.
- **Lazy auth** — `--help` and `--dry-run` work even when `JELLYFIN_URL` and `JELLYFIN_API_KEY` are not set. Dry-run reports request paths and parameters but never sends credentials or makes a network call.
- **No pagination** — Every command returns a single page of results. The CLI does not auto-paginate beyond the first response. Use `--limit` to control result size.

## References

- [scripts/jellyfin-cli](scripts/jellyfin-cli) — The bundled read-only CLI binary with `--json`, `--dry-run`, and lazy authentication.
- [Jellyfin API Docs](https://jellyfin.org/docs/general/clients/api) — Official API documentation.
- [Jellyfin Downloads](https://jellyfin.org/downloads) — Server download and setup guide.
