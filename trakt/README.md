# Trakt — Media Discovery from the Terminal

Discover trending, anticipated, and popular movies and TV shows via the Trakt.tv API. Read-only discovery with no user authentication needed.

## Why Install This Skill

When your agent loads this skill, it can **surface what's worth watching** without a browser. That means:

- **Trending movies and TV** — what everyone's watching right now
- **Most anticipated** — upcoming releases with buzz
- **Popular content** — what's been hot recently
- **No authentication** — just a Client ID, no OAuth flow

## What You Get

| Directory | Purpose |
|-----------|---------|
| `SKILL.md` | Complete command reference with examples |
| `scripts/trakt-cli` | CLI tool for Trakt.tv API v2 |

## Quick Start

```bash
export TRAKT_CLIENT_ID="your-trakt-client-id"
trakt-cli movie trending
trakt-cli tv trending
```

Client ID from trakt.tv/oauth/applications (free, no OAuth needed).

## Triggers

Load this for what to watch, trending movies, popular shows, or media discovery.

## Requirements

Python 3.8+ with `requests` library. Free Client ID from trakt.tv.
