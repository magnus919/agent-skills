---
name: prowlarr-cli/commands
description: "Full prowlarr-cli command reference — all subcommands, flags, and examples."
---

# prowlarr-cli Commands — Full Reference

## System

```bash
prowlarr-cli status                    # version, OS, database
prowlarr-cli status --json             # machine-readable
```

## Indexers

```bash
prowlarr-cli indexers                  # all indexers
prowlarr-cli indexers --limit 10       # top 10
prowlarr-cli indexers --json           # machine-readable
```

**Icons:** ✅ = enabled, 🚫 = disabled. Shows protocol (USENET/TORRENT), priority, and status.

## Indexer Details

```bash
prowlarr-cli indexer 5                 # full details for indexer ID 5
prowlarr-cli --json indexer 5          # machine-readable
```

Shows implementation name, protocol, enabled state, priority, and status.

## Indexer Statistics

```bash
prowlarr-cli indexer-stats             # query/grab counts per indexer
prowlarr-cli --json indexer-stats      # machine-readable
```

Shows total queries, grabs, and average response time per indexer.

## Indexer Status

```bash
prowlarr-cli indexer-status            # health/disabled status per indexer
prowlarr-cli --json indexer-status
```

Shows which indexers are disabled and their disabled-until information.

## Applications

```bash
prowlarr-cli applications              # connected *arr applications
prowlarr-cli applications --json
```

Lists Radarr, Sonarr, Lidarr instances connected to Prowlarr with sync level.

## Download Clients

```bash
prowlarr-cli download-clients          # configured download clients
prowlarr-cli download-clients --json
```

Shows all download clients configured in Prowlarr with protocol and enabled status.

## History

```bash
prowlarr-cli history                   # recent search history
prowlarr-cli history --limit 50        # more results
prowlarr-cli history --json            # machine-readable
```

Shows what was searched, which indexer handled it, and the event type.

## Health

```bash
prowlarr-cli health                    # health check warnings
prowlarr-cli health --json
```

## Tags

```bash
prowlarr-cli tags                      # list all tags
prowlarr-cli tags --json
```

## Test All

```bash
prowlarr-cli test-all                  # trigger a test of all indexers
prowlarr-cli --dry-run test-all        # preview
```

Triggers a `TestAllIndexers` command via the command API. Returns immediately — tests run async.

## JSON Output

All commands accept `--json`. Pipe to `jq` for scripting:

```bash
prowlarr-cli --json indexers | jq '.indexers[] | {name, protocol, enable, priority}'
prowlarr-cli --json history | jq '.history[] | {date, title, indexer, eventType}'
prowlarr-cli --json health | jq '.[] | {type, message}'
```
