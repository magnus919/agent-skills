# Jellyfin Media Server from the Terminal

Query your Jellyfin media library — recently added movies and episodes, search and inspect items, browse library contents, see next-up episodes, and check server stats.

## Why Install This Skill

When your agent loads this skill, it can **navigate your home media server** without opening a browser. That means:

- **See what's new** — recently added movies and TV episodes
- **Search your library** — find any movie, show, or episode by keyword
- **Navigate your library** — inspect search results, browse collections, and page through items
- **See what is next** — find the next unwatched episodes for a user
- **Check server details** — server name, version, operating system, user count

## What You Get

| Directory | Purpose |
|-----------|---------|
| `SKILL.md` | Complete command reference with setup and examples |
| `scripts/jellyfin-cli` | CLI tool for Jellyfin API operations |

## Quick Start

```bash
scripts/jellyfin-cli --help
export JELLYFIN_URL="http://your-server:8096"
export JELLYFIN_API_KEY="your-api-key"
export JELLYFIN_USER_ID="your-jellyfin-user-id" # required by recent, next-up, and item
```

API key from Dashboard → API Keys in the Jellyfin admin panel.

```bash
scripts/jellyfin-cli search --query "dune" --type Movie
scripts/jellyfin-cli next-up --limit 5
```

## Triggers

Load this when asking about Jellyfin, media server content, recently added movies or TV, or browsing your home media library.

## Requirements

Python 3.8+ with `requests` library. Jellyfin server with API key; `recent`, `next-up`, and `item` also require a Jellyfin user ID.
