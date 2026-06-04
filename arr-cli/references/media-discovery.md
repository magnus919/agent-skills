---
name: arr-cli/media-discovery
description: "Workflow for discovering new media via TMDb/Trakt APIs and cross-referencing against your Radarr/Sonarr library."
---

# Media Discovery & Cross-Reference

Use this reference when the user asks about upcoming movies, new releases, trending content, or finding something to watch. It covers discovering content through external APIs and checking whether it's already in your library.

## Prerequisites

- **TMDb API key** — Get one free at themoviedb.org → Settings → API
- **Trakt API key** (optional) — Get one at trakt.tv → Settings → Your API Apps

## Cross-Reference by ID

**Always use TMDb ID (movies) or TVDb ID (series), never title matching.** Title matching produces false negatives — titles in Radarr/Sonarr may differ slightly from TMDb/Trakt (punctuation, subtitle format, etc.).

### Check if a movie is already in Radarr

```bash
# Pure existence check — no side effects
radarr-cli --json movies | jq '.[] | select(.tmdbId == 1003596)'

# Returns the movie record if it exists, empty if not
# Fields: title, tmdbId, hasFile, monitored, status, year
```

**Do NOT use `radarr-cli lookup --tmdb-id N` for existence checks** — it silently adds an unmonitored record.

### Check if a series is already in Sonarr

```bash
sonarr-cli --json series | jq '.[] | select(.tvdbId == 77526)'
```

### Add a discovered movie

```bash
# Not in library → add
radarr-cli add --tmdb-id 1003596 --root /movies --quality-profile 4 --search

# Already exists but unmonitored → get Radarr internal ID, then PUT
# (See troubleshooting.md for the unmonitor-to-monitored recipe)
```

## TMDb Discovery Examples

```bash
# R-rated horror coming soon (genre 27 = Horror)
curl -s "https://api.themoviedb.org/3/discover/movie?with_genres=27&certification=R&sort_by=popularity.desc" \
  -H "Authorization: Bearer $TMDB_ACCESS_TOKEN" | \
  python3 -c "
import json,sys
data = json.load(sys.stdin)
for m in data.get('results',[]):
    print(f\"  {m['id']:8} {m['title']:45} ({m.get('release_date','?')[:4]})\")
"
```

## Trakt Discovery Examples

```bash
# Anticipated movies
curl -s "https://api.trakt.tv/movies/anticipated?limit=10" \
  -H "Content-Type: application/json" \
  -H "trakt-api-key: $TRAKT_CLIENT_ID" \
  -H "trakt-api-version: 2" | \
  python3 -c "
import json,sys
data = json.load(sys.stdin)
for m in data:
    movie = m.get('movie',{})
    print(f\"  {movie.get('ids',{}).get('tmdb','?'):8} {movie.get('title','?'):45}\")
"
```

## Full Cross-Reference Workflow

1. **Discover** — Use TMDb or Trakt to find content (upcoming horror, anticipated movies, trending series)
2. **Extract IDs** — Each result includes TMDb ID (movies) or TVDb ID (series)
3. **Check library** — Filter `radarr-cli --json movies` or `sonarr-cli --json series` by that ID
4. **Add if missing** — Use `radarr-cli add --tmdb-id N` or `sonarr-cli add --tvdb-id N`
5. **Report** — Present results split into "already in library" and "added"
