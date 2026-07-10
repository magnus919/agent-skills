# TMDb — Movie & TV Discovery from the Terminal

Search movies and TV shows by keyword, discover by genre/certification/rating/date, check trending and upcoming releases, and browse genre lists.

## Why Install This Skill

When your agent loads this skill, it can **access the entire TMDb catalog** without a browser. That means:

- **Search movies and TV** — by keyword with release year and ratings
- **Discover by taste** — genre, certification, rating threshold, date range
- **Find trending content** — what's popular right now
- **Check upcoming releases** — what's coming to theaters
- **Browse certifications** — US ratings (G, PG, PG-13, R, NC-17)

## What You Get

| Directory | Purpose |
|-----------|---------|
| `SKILL.md` | Complete command reference with compound filter examples |
| `scripts/tmdb-cli` | CLI tool for TMDb v3 API |

## Quick Start

```bash
export TMDB_ACCESS_TOKEN="your-tmdb-access-token"
tmdb-cli movie search --term "dune"
tmdb-cli movie discover --genre horror --certification R
```

## Triggers

Load this for movies, TV shows, film discovery, genre browsing, or media recommendations.

## Requirements

Python 3.8+ with `requests` library. Free API key from themoviedb.org.
