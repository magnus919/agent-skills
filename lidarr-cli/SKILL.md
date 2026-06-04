---
name: lidarr-cli
description: >-
  Manage your Lidarr music library from the terminal. Search and browse artists
  and albums, add new artists, check calendars, view queue and download history,
  inspect quality and metadata profiles, and trigger searches. Use when the user
  mentions Lidarr, music management, adding an artist, searching for music,
  checking the music library, upcoming album releases, or download queue.
license: MIT
compatibility: >-
  Python 3.8+ with `requests` library. Requires ARR_SERVER_LIDARR and
  ARR_KEY_LIDARR (from Lidarr → Settings → General → API Key).
metadata:
  tags: [lidarr, music, arr-stack, media-server, music-automation, api-client]
  sources:
    - https://lidarr.audio/
---

# lidarr-cli — Lidarr Music Library Management

CLI for Lidarr music management. Part of the *arr family — shares the same
API patterns as radarr-cli and sonarr-cli.

## Quick Setup

```bash
export ARR_SERVER_LIDARR="http://localhost:8686"
export ARR_KEY_LIDARR="your-lidarr-api-key"
```

`--help` and `--dry-run` work without credentials.

## When to Use Which

| User says... | Load... |
|---|---|
| "list my artists", "what's in Lidarr", "show my music library" | `lidarr-cli artists [--limit N]` |
| "add this artist", "find an artist" | `lidarr-cli lookup --term "name"` then `lidarr-cli add --mb-id UUID --root /music` |
| "what albums does this artist have" | `lidarr-cli albums --artist-id N` |
| "show me the tracks" | `lidarr-cli tracks --album-id N` |
| "what's coming up", "upcoming albums" | `lidarr-cli calendar` |
| "what's in the queue", "download progress" | `lidarr-cli queue` |
| "show me history", "what was downloaded" | `lidarr-cli history` |
| "what's missing", "wanted albums" | `lidarr-cli wanted` |
| "check quality profiles" | `lidarr-cli quality-profile` |
| "check metadata profiles" | `lidarr-cli metadata-profile` |
| "storage space", "disk usage" | `lidarr-cli disk-space` |
| "search for an artist" (already added) | `lidarr-cli search --artist-id N` |

## Quick Reference

**Global flags:** `--json`, `--dry-run`, `--force`, `--quiet`, `--verbose`

```bash
# System info
lidarr-cli status

# Discover and add an artist (use MusicBrainz ID, not title)
lidarr-cli lookup --term "Radiohead"
lidarr-cli add --mb-id a74b1b7f-71a5-4011-9441-d0b5e4122711 --root /music --quality-profile 4 --search

# Browse content
lidarr-cli albums --artist-id 1
lidarr-cli tracks --album-id 1
lidarr-cli track-files --album-id 1

# Preview before adding
lidarr-cli --dry-run add --mb-id a74b1b7f-71a5-4011-9441-d0b5e4122711 --root /music

# Queue, history, wanted
lidarr-cli queue --limit 10
lidarr-cli wanted --limit 10
lidarr-cli history --limit 5

# Profiles and storage
lidarr-cli quality-profile           # list all
lidarr-cli quality-profile 4         # inspect specific
lidarr-cli metadata-profile          # list metadata profiles
lidarr-cli disk-space                # storage usage
lidarr-cli health                    # health warnings
```

**Artist lookup by MusicBrainz ID (MBID):** Lidarr uses MusicBrainz IDs (UUID format,
e.g. `a74b1b7f-71a5-4011-9441-d0b5e4122711`) instead of TMDb/TVDb integer IDs.

**Default quality profile:** 4. **Default metadata profile:** 1.

## Reference Files

| File | Contents |
|------|----------|
| `references/lidarr-commands.md` | Full command reference with all flags and examples |
| `references/troubleshooting.md` | Pitfalls, FAQs, and when NOT to use |

## When NOT to Use

- **Music playback** — use Jellyfin for listening. This CLI only manages the library.
- **First-time Lidarr setup** — assumes Lidarr is already installed and configured.
- **Bulk imports** — use Lidarr's built-in import features for large migrations.
