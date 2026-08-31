# TMDb Metadata Skill

## Why Install This Skill

Give your agent a dependable terminal workflow for exploring movie and television metadata without hand-building every HTTP request. It can start from a title, an IMDb ID, or a discovery filter, then enrich the result with credits, recommendations, images, and provider metadata.

The skill also makes TMDb's easy-to-miss rules visible: choose one authentication mode, respect the 500-page ceiling, use the correct nested `/find` response, and URL-encode compound provider paths.

## What You Get

| Path | Purpose |
| --- | --- |
| `SKILL.md` | Setup, commands, recipes, gotchas, and routing |
| `scripts/tmdb` | Executable JSON-capable CLI for search, detail, find, discovery, and trends |
| `scripts/test_tmdb.py` | Offline pytest/unittest coverage with mocked HTTP behavior |
| `references/auth-pagination-and-errors.md` | Authentication, pagination, errors, rate limits, and image construction |
| `references/find-and-details.md` | External IDs, IMDb entry points, details, credits, and compound responses |
| `references/search-discover-trending.md` | Search, discovery filters, trending, genres, and certifications |
| `evals/evals.json` | Runnable examples covering normal and negative routing |

## Quick Start

```bash
export TMDB_ACCESS_TOKEN="YOUR_ACCESS_TOKEN"
tmdb movie search --term "Dune" --limit 5 --json
tmdb find tt0111161 --source imdb_id --json
tmdb movie detail 550 --append credits,videos --json
```

## Triggers

Load this skill when the request involves movie or TV metadata, title search, IMDb/TVDB resolution, credits, release dates, certifications, recommendations, images, trending media, or provider metadata.

## Requirements

- Python 3.8 or newer
- `requests` Python package
- A TMDb API Read Access Token or v3 API key
- `jq` for the shell pipeline examples

This is a read-oriented metadata workflow. It does not play media, search torrents, or maintain personal watch history.
