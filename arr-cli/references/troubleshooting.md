---
name: arr-cli/troubleshooting
description: "Common pitfalls, FAQs, and guidance on when not to use the arr-cli skill."
---

# Troubleshooting & FAQs

## Common Pitfalls

### Looking up adds an unmonitored record

`radarr-cli lookup --tmdb-id N` silently creates an unmonitored record. This is a Radarr API design — there's no pure "lookup without adding." For existence checks, filter the movie list instead:

```bash
# ✅ Correct — no side effects
radarr-cli --json movies | jq '.[] | select(.tmdbId == 12345)'

# ❌ Wrong — creates phantom unmonitored record
radarr-cli lookup --tmdb-id 12345
```

### Adding requires a root folder path

`radarr-cli add --root /movies` — the root folder must be an exact path known to Radarr. Discover available paths:

```bash
radarr-cli root-folder
```

### Commands appear to hang on large libraries

The `movie` and `series` endpoints return the full collection — no server-side pagination. On libraries with 2500+ movies, this can take a few seconds. Use `--limit N` for faster results:

```bash
radarr-cli movies --limit 10
```

### JSON output mixed with warning lines

Occasionally Python deprecation warnings can bleed into `--json` output. If `json.loads()` fails, filter lines that start with `[` or `{` before parsing.

### Sonarr wanted endpoint is paginated

The `wanted` endpoint returns a `totalRecords` field. Use `--limit` to control page size. Results are capped at the server's max page size.

## When Not to Use

- **Media playback** — this CLI manages the library, not plays content. Use Jellyfin.
- **First-time *arr setup** — assumes Radarr/Sonarr are already installed and configured. See `radarr.video` or `sonarr.tv`.
- **Bulk library migration** — for large-scale imports, use Radarr/Sonarr's built-in tools.
- **Streaming service status** — this won't tell you if a streaming service is down.

## FAQ

**Q: Why use --tmdb-id instead of a title search?**
A: Titles can differ between TMDb and Radarr (special characters, subtitle formatting, year disambiguation). The TMDb ID is the canonical key shared by both systems.

**Q: Can I add a movie that's not released yet?**
A: Yes. Use `--availability announced` for unreleased films, `--availability inCinemas` for current theatrical releases. Don't use `--search` for unreleased content — there's nothing to search for.

**Q: How do I find a movie's TMDb ID?**
A: Use `radarr-cli lookup --term "title" --json` — the results include `tmdbId`. Or search themoviedb.org directly — the ID is in the URL.

**Q: How do I find a series' TVDb ID?**
A: Use `sonarr-cli lookup --term "title" --json` — results include `tvdbId`. Or search thetvdb.com.

**Q: What does quality profile 4 vs 5 mean?**
A: Profile IDs vary by setup. Use `radarr-cli quality-profile` to list all profiles with their names:
- 4 is typically HD-1080p
- 5 is typically Ultra-HD (4K)
- Run the command to see your actual configuration
