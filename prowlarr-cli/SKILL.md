---
name: prowlarr-cli
description: >-
  Manage your Prowlarr indexer hub from the terminal. List and inspect indexers,
  view query/grab statistics, check health, manage connected *arr applications
  and download clients, browse search history, and test indexer connectivity.
  Use when the user mentions Prowlarr, indexers, indexer management, testing
  indexers, search history, or the indexer hub.
license: MIT
compatibility: >-
  Python 3.8+ with `requests` library. Requires ARR_SERVER_PROWLARR and
  ARR_KEY_PROWLARR (from Prowlarr → Settings → General → API Key).
metadata:
  tags: [prowlarr, indexer, arr-stack, media-server, api-client]
  sources:
    - https://prowlarr.com/
---

# prowlarr-cli — Prowlarr Indexer Management

CLI for Prowlarr, the indexer manager for the *arr stack. Unlike radarr-cli
and sonarr-cli, this manages indexer infrastructure rather than media.

## Quick Setup

```bash
export ARR_SERVER_PROWLARR="http://localhost:9696"
export ARR_KEY_PROWLARR="your-prowlarr-api-key"
```

`--help` and `--dry-run` work without credentials.

## When to Use Which

| User says... | Load... |
|---|---|
| "list my indexers", "what indexers do I have" | `prowlarr-cli indexers` |
| "show me indexer 5", "details on this indexer" | `prowlarr-cli indexer 5` |
| "how are my indexers doing", "query stats" | `prowlarr-cli indexer-stats` |
| "are any indexers down" | `prowlarr-cli indexer-status` |
| "what apps are connected" | `prowlarr-cli applications` |
| "what download clients are configured" | `prowlarr-cli download-clients` |
| "show me search history" | `prowlarr-cli history` |
| "test all my indexers" | `prowlarr-cli test-all` |
| "prowlarr health" | `prowlarr-cli health` |
| "list tags" | `prowlarr-cli tags` |

## Quick Reference

**Global flags:** `--json`, `--dry-run`, `--force`, `--quiet`, `--verbose`

```bash
# System info
prowlarr-cli status

# Indexer management
prowlarr-cli indexers                                # all indexers
prowlarr-cli indexers --limit 10                     # top 10
prowlarr-cli indexer 5                               # single indexer details
prowlarr-cli indexer-stats                           # query/grab stats
prowlarr-cli indexer-status                          # health per indexer

# Infrastructure
prowlarr-cli applications                            # connected *arr apps
prowlarr-cli download-clients                        # configured download clients
prowlarr-cli tags                                    # list tags
prowlarr-cli health                                  # health warnings

# Search and testing
prowlarr-cli history --limit 20                      # search history
prowlarr-cli test-all                                # test all indexers

# JSON output for scripting
prowlarr-cli --json indexers | jq '.indexers[] | {name, protocol, enable, status}'
prowlarr-cli --json health | jq '.[].message'
```

## Reference Files

| File | Contents |
|------|----------|
| `references/prowlarr-commands.md` | Full command reference |
| `references/troubleshooting.md` | Pitfalls and FAQs |

## When NOT to Use

- **Media search** — Prowlarr indexes content but doesn't download it. Use Radarr/Sonarr/Lidarr.
- **First-time Prowlarr setup** — assumes Prowlarr is already installed and configured.
