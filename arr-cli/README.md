# Radarr & Sonarr Media Library Management

A unified CLI skill for managing movies (Radarr) and TV series (Sonarr) from the terminal. Two CLIs, one skill wrapper.

## Why Install This Skill

When your agent loads this skill, it can **manage your entire *arr media library** without needing a web browser. That means:

- **Ask what's in your library** — list movies, TV series, recently added content
- **Add new media** — search for titles by name, then add them with the right quality profile
- **Track upcoming releases** — check calendars for scheduled releases
- **Monitor downloads** — view queue, download history, and wanted/missing episodes
- **Troubleshoot** — check quality profiles, root folders, and system status

## What You Get

| Directory | Purpose |
|-----------|---------|
| `SKILL.md` | Complete command reference with trigger table for every operation |
| `scripts/radarr-cli` | CLI tool for Radarr movie management |
| `scripts/sonarr-cli` | CLI tool for Sonarr TV series management |

## Quick Start

```bash
export ARR_SERVER_RADARR="http://localhost:7878"
export ARR_KEY_RADARR="your-radarr-api-key"
export ARR_SERVER_SONARR="http://localhost:8989"
export ARR_KEY_SONARR="your-sonarr-api-key"
```

## Triggers

Load this skill when you hear "Radarr," "Sonarr," "the *arr stack," "add a movie," "find a TV show," "what's in my library," "upcoming releases," "download queue," or anything about media library management.

## Requirements

Python 3.8+ with `requests` library. API keys from each app's Settings → General.
