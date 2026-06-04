---
name: lidarr-cli/commands
description: "Full lidarr-cli command reference — all subcommands, flags, and examples."
---

# lidarr-cli Commands — Full Reference

## System

```bash
lidarr-cli status                    # version, OS, database
lidarr-cli status --json             # machine-readable
```

## Artists

```bash
lidarr-cli artists                   # all artists
lidarr-cli artists --limit 10        # top 10
lidarr-cli artists --json            # machine-readable (includes foreignArtistId)
```

**Icons:** ✅ = has albums, 👁️ = monitored but empty, 🚫 = unmonitored.

## Lookup (search artists to add)

```bash
lidarr-cli lookup --term "Radiohead"       # search by name
lidarr-cli lookup --term "Radiohead" --json  # includes MusicBrainz ID
```

Results include `foreignArtistId` (MusicBrainz UUID) — this is the ID to use with `add`.

## Lookup Album

```bash
lidarr-cli lookup-album --term "OK Computer"
lidarr-cli lookup-album --term "OK Computer" --json
```

## Add

```bash
# Basic: add monitored with auto-search
lidarr-cli add --mb-id a74b1b7f-71a5-4011-9441-d0b5e4122711 --root /music --quality-profile 4 --search

# Add with specific metadata profile
lidarr-cli add --mb-id UUID --root /music --quality-profile 4 --metadata-profile 2 --search

# Add unmonitored
lidarr-cli add --mb-id UUID --root /music --unmonitored

# Preview
lidarr-cli --dry-run add --mb-id UUID --root /music
```

| Flag | Default | Description |
|------|---------|-------------|
| `--mb-id` | required | MusicBrainz ID (UUID format) |
| `--root` | required | Root folder path (discover with `root-folder`) |
| `--quality-profile` | 4 | Quality profile ID |
| `--metadata-profile` | 1 | Metadata profile ID |
| `--unmonitored` | off | Add without monitoring (default: monitored) |
| `--search` | off | Search for albums after adding |

## Albums

```bash
lidarr-cli albums --artist-id 1            # all albums for an artist
lidarr-cli albums --artist-id 1 --limit 5  # limit results
lidarr-cli albums --artist-id 1 --json     # machine-readable
```

Get the Lidarr artist ID from `lidarr-cli artists --json`.

## Tracks

```bash
lidarr-cli tracks --album-id 1             # all tracks for an album
lidarr-cli tracks --album-id 1 --limit 10  # limit results
lidarr-cli tracks --album-id 1 --json      # machine-readable
```

## Track Files

```bash
lidarr-cli track-files --album-id 1        # downloaded files with quality and size
lidarr-cli track-files --album-id 1 --json
```

## Quality Profiles

```bash
lidarr-cli quality-profile                # list all profiles
lidarr-cli quality-profile 4              # inspect specific (cutoff, tier checkmarks)
lidarr-cli --json quality-profile         # machine-readable
```

## Metadata Profiles

```bash
lidarr-cli metadata-profile               # list all metadata profiles
lidarr-cli metadata-profile --json
```

Metadata profiles control how Lidarr handles album metadata (tags, artwork, etc.).
Profile 1 is typically "Standard" — the default.

## Calendar

```bash
lidarr-cli calendar                       # upcoming album releases
lidarr-cli calendar --json
```

## Queue

```bash
lidarr-cli queue                          # current download queue
lidarr-cli queue --limit 50
lidarr-cli queue --json
```

## History

```bash
lidarr-cli history                        # recent activity
lidarr-cli history --limit 50
lidarr-cli history --event-type grabbed
lidarr-cli history --json
```

## Wanted (Missing Albums)

```bash
lidarr-cli wanted                         # missing albums
lidarr-cli wanted --limit 50
lidarr-cli wanted --json
```

## Search (trigger on existing artists)

```bash
lidarr-cli search --artist-id 5           # trigger automatic search (Lidarr artist ID)
```

Returns a command object immediately — search runs async in the background.

## Root Folders

```bash
lidarr-cli root-folder                    # list all root folders with free space
lidarr-cli root-folder --json
```

## Disk Space

```bash
lidarr-cli disk-space                     # storage usage per path
lidarr-cli disk-space --json
```

## Health

```bash
lidarr-cli health                         # health check warnings
lidarr-cli health --json
```

## JSON Output

All commands accept `--json`. Pipe to `jq` for scripting:

```bash
lidarr-cli --json artists | jq '.artists[] | {artistName, foreignArtistId, monitored}'
lidarr-cli --json wanted | jq '.wanted[] | {artist, title, releaseDate}'
lidarr-cli --json queue | jq '.queue[] | {title, status, progress}'
```
