# Lidarr Music Library Management

Manage your Lidarr music library from the terminal — search and browse artists and albums, add new artists, check calendars, view queue and download history.

## Why Install This Skill

When your agent loads this skill, it can **manage your entire music library** through Lidarr. That means:

- **List artists and albums** — browse your curated music collection
- **Add new artists** — search and add with MusicBrainz IDs
- **Track upcoming albums** — calendar for scheduled releases
- **Monitor downloads** — queue, history, wanted/ missing albums
- **Check profiles** — quality and metadata profiles

## What You Get

| Directory | Purpose |
|-----------|---------|
| `SKILL.md` | Complete command reference with trigger table |
| `scripts/lidarr-cli` | CLI tool for Lidarr API |

## Quick Start

```bash
export ARR_SERVER_LIDARR="http://localhost:8686"
export ARR_KEY_LIDARR="your-lidarr-api-key"
```

## Triggers

Load this when working with Lidarr, music library management, adding artists, or checking upcoming album releases.

## Requirements

Python 3.8+ with `requests` library. API key from Lidarr → Settings → General.
