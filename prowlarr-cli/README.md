# Prowlarr — Indexer Hub Management

Manage your Prowlarr indexer hub from the terminal — list and inspect indexers, view query/grab statistics, check health, manage connected *arr applications, and test indexer connectivity.

## Why Install This Skill

When your agent loads this skill, it can **manage your entire indexer infrastructure**. That means:

- **List and inspect indexers** — see what indexers are configured
- **Monitor performance** — query and grab statistics per indexer
- **Test connectivity** — verify indexers are responding
- **Check health** — overall system health and per-indexer status
- **View connected apps** — which *arr applications are linked
- **Browse search history** — see what's been searched and found

## What You Get

| Directory | Purpose |
|-----------|---------|
| `SKILL.md` | Complete command reference with trigger table |
| `scripts/prowlarr-cli` | CLI tool for Prowlarr API |

## Quick Start

```bash
export ARR_SERVER_PROWLARR="http://localhost:9696"
export ARR_KEY_PROWLARR="your-prowlarr-api-key"
```

## Triggers

Load this when working with Prowlarr, indexers, or the *arr stack's indexer hub.

## Requirements

Python 3.8+ with `requests` library. API key from Prowlarr → Settings → General.
