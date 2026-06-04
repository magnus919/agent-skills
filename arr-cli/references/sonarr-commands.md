---
name: arr-cli/sonarr-commands
description: "Full Sonarr command reference for the arr-cli skill — all subcommands, flags, and extended examples."
---

# Sonarr Commands — Full Reference

## System

```bash
sonarr-cli status                    # version, OS, database
sonarr-cli status --json             # machine-readable
```

## Series

```bash
sonarr-cli series                    # all series
sonarr-cli series --limit 10         # top 10
sonarr-cli series --status continuing  # filter: continuing, ended, upcoming
sonarr-cli series --json             # machine-readable (includes tvdbId for cross-ref)
```

**Icons:** ✅ = has episodes, 👁️ = monitored but empty, 🚫 = unmonitored.

## Lookup (search to add)

```bash
sonarr-cli lookup --term "Severance"        # search by title
sonarr-cli lookup --term "Severance" --json # includes TVDb ID and overview
```

## Add

```bash
# Standard weekly show with auto-search
sonarr-cli add --tvdb-id 77526 --root /tv --quality-profile 4 --series-type Standard --search

# Daily show (talk show, news)
sonarr-cli add --tvdb-id 12345 --root /tv --quality-profile 4 --series-type Daily --search

# Anime with absolute numbering, flat episode storage
sonarr-cli add --tvdb-id 12345 --root /tv --quality-profile 4 --series-type Anime --no-season-folder --search

# Preview without adding
sonarr-cli --dry-run add --tvdb-id 77526 --root /tv
```

| Flag | Default | Description |
|------|---------|-------------|
| `--tvdb-id` | required | TVDb series ID (canonical key) |
| `--root` | required | Root folder path (discover with `root-folder`) |
| `--quality-profile` | 4 (HD-1080p) | Quality profile ID |
| `--series-type` | Standard | `Standard`, `Daily`, or `Anime` |
| `--unmonitored` | off | Add without monitoring (default: monitored) |
| `--search` | off | Search for missing episodes after adding |
| `--no-season-folder` | off | Flat storage (all episodes in series root) |

## Quality Profiles

```bash
sonarr-cli quality-profile           # list all profiles with IDs
sonarr-cli quality-profile 4         # inspect specific profile (cutoff, tier checkmarks)
sonarr-cli --json quality-profile    # machine-readable for scripting
```

## Episodes

```bash
sonarr-cli episodes --series-id 1             # all episodes
sonarr-cli episodes --series-id 1 --limit 10  # recent episodes
sonarr-cli episodes --series-id 1 --json      # machine-readable
```

Get the Sonarr internal series ID from `sonarr-cli series --json`.

## Episode Files

```bash
sonarr-cli episode-file --series-id 1         # downloaded files with quality and size
sonarr-cli episode-file --series-id 1 --json   # machine-readable
```

## Calendar

```bash
sonarr-cli calendar                   # upcoming episodes (next 14 days)
sonarr-cli calendar --json            # machine-readable
```

## Wanted (Missing Episodes)

```bash
sonarr-cli wanted                     # missing episodes (default: 20)
sonarr-cli wanted --limit 50          # more results
sonarr-cli wanted --json              # machine-readable with totalRecords
```

## Queue

```bash
sonarr-cli queue                      # current download queue (default: 20)
sonarr-cli queue --limit 50           # more results
sonarr-cli queue --json               # machine-readable
```

## History

```bash
sonarr-cli history                    # recent activity (default: 20)
sonarr-cli history --limit 50         # more results
sonarr-cli history --event-type grabbed   # filter by event type
sonarr-cli history --json             # machine-readable
```

## Search (trigger on existing items)

```bash
sonarr-cli search --series-id 5       # trigger automatic search for series (Sonarr internal ID)
```

Returns a command object immediately — search runs async in the background.

## Root Folders

```bash
sonarr-cli root-folder                # list all root folders with free space
sonarr-cli root-folder --json         # machine-readable
```

## JSON Output

All commands accept `--json`. Pipe to `jq` for scripting:

```bash
sonarr-cli --json series | jq '.series[] | {title, tvdbId, monitored, seasons}'
sonarr-cli --json wanted | jq '.wanted[] | {seriesTitle, seasonNumber, episodeNumber}'
sonarr-cli --json queue | jq '.queue[] | {title, status, progress}'
```
