# PeerTube — Federated Video from the Terminal

Browse videos, channels, and server info on any PeerTube instance. Search across the fediverse, list channels, check your account stats, and manage authentication.

## Why Install This Skill

When your agent loads this skill, it can **navigate the federated video universe** without a browser. That means:

- **Browse videos** — recent uploads from any instance
- **Search across instances** — find content in the fediverse
- **Explore channels** — list channels and their videos
- **Check server info** — instance name, description, user/video/view stats
- **Authenticate** — OAuth2 login with token persistence

## What You Get

| Directory | Purpose |
|-----------|---------|
| `SKILL.md` | Complete command reference with auth setup |
| `scripts/peertube-cli` | CLI tool for PeerTube API |

## Quick Start

```bash
export PEERTUBE_SERVER="https://your-instance.example.com"
peertube-cli auth login --username "myuser" --password "mypassword"
```

## Triggers

Load this for PeerTube, federated video, decentralized video platforms, or browsing PeerTube content.

## Requirements

Python 3.8+ with `requests` library.
