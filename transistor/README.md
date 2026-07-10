# Transistor.fm — Podcast Hosting from the Terminal

Manage your Transistor.fm podcast shows, episodes, subscribers, and analytics — all from the terminal.

## Why Install This Skill

When your agent loads this skill, it can **manage your podcast hosting** without the web dashboard. That means:

- **List shows** — all your podcasts with episode and subscriber counts
- **Browse episodes** — recent episodes with publish dates
- **Check analytics** — subscriber counts and trends
- **Filter by show** — drill into a specific podcast's episodes

## What You Get

| Directory | Purpose |
|-----------|---------|
| `SKILL.md` | Complete command reference with examples |
| `scripts/transistor-cli` | CLI tool for Transistor.fm v1 REST API |

## Quick Start

```bash
export TRANSISTOR_API_KEY="your-transistor-api-key"
transistor-cli shows
transistor-cli episodes
```

API key from Settings → API Keys in the Transistor.fm dashboard.

## Triggers

Load this for Transistor.fm, podcast hosting, podcast analytics, show management, or episode tracking.

## Requirements

Python 3.8+ with `requests` library.
