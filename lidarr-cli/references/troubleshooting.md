---
name: lidarr-cli/troubleshooting
description: "Common pitfalls, FAQs, and when NOT to use lidarr-cli."
---

# Troubleshooting & FAQs

## Common Pitfalls

### Artist lookup uses MusicBrainz ID, not a numeric ID

Lidarr uses MusicBrainz IDs (UUID format) as the canonical identifier. Always use
`--mb-id UUID` when adding an artist — not a numeric ID.

```bash
# ✅ Correct: MusicBrainz UUID
lidarr-cli add --mb-id a74b1b7f-71a5-4011-9441-d0b5e4122711 --root /music

# ❌ Wrong: numeric IDs won't work for artists
```

### Adding requires a root folder path

`lidarr-cli add --root /music` — the root folder must be an exact path known to Lidarr:

```bash
lidarr-cli root-folder
```

### Music is deeper than movies: artist → album → track

Lidarr has a three-level hierarchy:
- `lookup` → search artists
- `albums --artist-id N` → browse albums
- `tracks --album-id N` → browse tracks within an album
- `track-files --album-id N` → see downloaded files

### Metadata profiles are Lidarr-specific

Lidarr uses metadata profiles (album artwork, tag handling) that don't exist in
Radarr/Sonarr. Default is profile 1. List them with:

```bash
lidarr-cli metadata-profile
```

## When Not to Use

- **Music playback** — use Jellyfin for listening content
- **First-time Lidarr setup** — install and configure Lidarr first (lidarr.audio)
- **Bulk library migration** — use Lidarr's built-in import tools

## FAQ

**Q: Where do I find an artist's MusicBrainz ID?**
A: Use `lidarr-cli lookup --term "artist name" --json` — results include
`foreignArtistId`. Or search musicbrainz.org directly.

**Q: How do I find the Lidarr artist ID for a search?**
A: Run `lidarr-cli artists --json | jq '.artists[] | {artistName, id}'`

**Q: What's the difference between quality profile and metadata profile?**
A: Quality profile controls audio format (FLAC, MP3, etc.). Metadata profile
controls how album metadata (tags, artwork) is managed. Both are set at add time.

**Q: Can I trigger a search for an existing artist's albums?**
A: Yes. Find the Lidarr artist ID with `lidarr-cli artists --json`, then
`lidarr-cli search --artist-id N`. This searches for all missing albums.
