# Jellyfin Media Server from the Terminal

Query your Jellyfin media library — recently added movies and episodes, search and inspect
items, walk series, seasons, and episodes, browse library contents, see next-up episodes,
log in as a user, and check server stats.

## Why Install This Skill

When your agent loads this skill, it can **navigate your home media server** without
opening a browser. That means:

- **See what's new** — recently added movies and TV episodes, filtered server-side
- **Search your library** — find any movie, show, or episode by keyword
- **Navigate series** — walk a show's seasons and episodes, and see what's next unwatched
- **Browse collections** — list your libraries and page through everything in them
- **Authenticate properly** — log in as a user (or use Quick Connect) without fumbling
  Jellyfin's unusual `MediaBrowser` authorization header, which trips up most scripts
- **Check server details** — server name, version, operating system, user count, counts

Every command is read-only (plus a `login` helper), and `--dry-run` previews any request
without touching the network.

## What You Get

| Path | Purpose |
|------|---------|
| `SKILL.md` | Complete command reference with setup, gotchas, and recipes |
| `scripts/jellyfin` | CLI for Jellyfin API operations (`--json`, `--dry-run`) |
| `scripts/test_jellyfin_cli.py` | Offline test suite (all HTTP mocked) |
| `references/auth-and-sessions.md` | The MediaBrowser header scheme, login flow, token channels, deprecation timeline |
| `references/endpoint-catalog.md` | Endpoint-by-endpoint parameter and response-shape catalog |
| `references/user-scoping-and-errors.md` | Which calls need a user id, and why queries 400/404 without one |
| `references/gotchas-field-guide.md` | Wire-level failure signatures and version differences |
| `references/worked-recipes.md` | Multi-step curl/jq and CLI workflows |
| `references/quick-connect.md` | Passwordless Quick Connect login |
| `evals/evals.json` | Behavioral eval cases including negative triggers |

## Quick Start

```bash
scripts/jellyfin --help
export JELLYFIN_URL="http://your-server:8096"
export JELLYFIN_API_KEY="your-api-key"           # Dashboard → API Keys
export JELLYFIN_USER_ID="your-jellyfin-user-id"  # required by user-scoped commands
```

```bash
scripts/jellyfin search --query "dune" --type Movie --json
scripts/jellyfin recent --movies --limit 5
```

No API key yet? Log in as a user instead — the script sends the pre-token
`Authorization: MediaBrowser Client=..., Device=..., DeviceId=..., Version=...` header
that `POST /Users/AuthenticateByName` requires and prints the values to export:

```bash
scripts/jellyfin login --username alice --prompt
```

## Triggers

Load this when asking about Jellyfin, media server content, recently added movies or TV,
next-up episodes, browsing your home media library, or Jellyfin API authentication.

## Requirements

Python 3.8+ with `requests`. A running Jellyfin server (10.8+ behaviors assumed).
Authentication: an API key (Dashboard → API Keys), a user access token via `login`, or
Quick Connect. User-scoped commands also need a Jellyfin user id.
