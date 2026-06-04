---
name: arr-cli/radarr-commands
description: "Full Radarr command reference for the arr-cli skill — all subcommands, flags, and extended examples."
---

# Radarr Commands — Full Reference

## System

```bash
radarr-cli status                    # version, OS, database
radarr-cli status --json             # machine-readable
```

## Movies

```bash
radarr-cli movies                    # all movies
radarr-cli movies --limit 10         # top 10
radarr-cli movies --status released  # filter: released, inCinemas, announced
radarr-cli movies --json             # machine-readable (includes tmdbId for cross-ref)
```

**Icons:** ✅ = has file, 👁️ = monitored but missing, 🚫 = unmonitored.

## Lookup (search to add)

```bash
radarr-cli lookup --term "Dune"            # search by title
radarr-cli lookup --term "Dune" --json     # includes TMDb ID and overview
```

**⚠️ Side effect:** `lookup` silently adds an unmonitored record to Radarr. For pure existence checks, use `radarr-cli --json movies` and filter by `tmdbId`.

## Add

```bash
# Basic: add monitored with auto-search
radarr-cli add --tmdb-id 550 --root /movies --quality-profile 4 --search

# High quality, upcoming release (don't search yet)
radarr-cli add --tmdb-id 99999 --root /movies --quality-profile 5 --availability announced

# Add unmonitored (manual decision later)
radarr-cli add --tmdb-id 12345 --root /movies --unmonitored

# Preview without adding (no side effects)
radarr-cli --dry-run add --tmdb-id 550 --root /movies --quality-profile 4
```

| Flag | Default | Description |
|------|---------|-------------|
| `--tmdb-id` | required | TMDb movie ID (canonical key) |
| `--root` | required | Root folder path (discover with `root-folder`) |
| `--quality-profile` | 4 (HD-1080p) | Quality profile ID |
| `--unmonitored` | off | Add without monitoring (default: monitored) |
| `--search` | off | Trigger automatic search after adding |
| `--availability` | released | `announced`, `inCinemas`, or `released` |

## Quality Profiles

```bash
radarr-cli quality-profile           # list all profiles with IDs
radarr-cli quality-profile 4         # inspect specific profile (cutoff, tier checkmarks)
radarr-cli --json quality-profile    # machine-readable for scripting
```

Use `--json` output to find profile IDs programmatically.

## Calendar

```bash
radarr-cli calendar                  # next 14 days
radarr-cli calendar --json           # machine-readable
```

## Queue

```bash
radarr-cli queue                     # current download queue (default: 20)
radarr-cli queue --limit 50          # more results
radarr-cli queue --json              # machine-readable
```

## History

```bash
radarr-cli history                   # recent activity (default: 20)
radarr-cli history --limit 50        # more results
radarr-cli history --event-type grabbed   # filter by event type
radarr-cli history --json            # machine-readable
```

## Search (trigger on existing items)

```bash
radarr-cli search --movie-id 5       # trigger automatic search for movie (Radarr internal ID)
```

Returns a command object immediately — search runs async in the background.

## Root Folders

```bash
radarr-cli root-folder               # list all root folders with free space
radarr-cli root-folder --json        # machine-readable
```

## Collections

```bash
radarr-cli collections               # list movie collections
radarr-cli collections --json        # machine-readable with movie counts
```

## JSON Output

All commands accept `--json`. Pipe to `jq` for scripting:

```bash
radarr-cli --json movies | jq '.movies[] | {title, tmdbId, hasFile, monitored}'
radarr-cli --json queue | jq '.queue[] | {title, status, progress}'
radarr-cli --json history | jq '.history[] | {date, title, eventType}'
```
