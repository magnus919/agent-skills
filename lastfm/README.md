# Last.fm — Music Data API from the Terminal

Lookup user listening history, discover similar music, explore charts, manage tags, and scrobble listening events — all from your Last.fm account.

## Why Install This Skill

When your agent loads this skill, it can **work with your entire music listening history**. That means:

- **Music discovery** — find similar artists via collaborative filtering
- **Personal stats** — top artists, tracks, albums over any time period
- **Charts** — global and per-country trending music
- **Social graph** — friends' listening activity
- **Scrobbling & loving** — record what you're listening to in real time

## What You Get

| Directory | Purpose |
|-----------|---------|
| `SKILL.md` | Complete command reference with examples |
| `scripts/lastfm-cli` | CLI tool for the Last.fm API |

## Quick Start

```bash
export LASTFM_API_KEY="your_api_key_here"
```

Free API key from last.fm/api/account/create.

## Triggers

Load this for music data, listening statistics, music recommendations, similar artists, charts, or scrobbling.

## Requirements

Python 3.8+ with `requests` library. Free Last.fm API key.
