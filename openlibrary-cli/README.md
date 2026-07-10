# Open Library — Book Metadata from the Terminal

Search books and authors, look up works and ISBNs, and fetch detailed metadata from the public Open Library API. No API key, no registration — just works.

## Why Install This Skill

When your agent loads this skill, it can **access 50M+ book records** without any setup. That means:

- **Search by keyword** — find books by title, author, or subject
- **Look up by ISBN** — get detailed metadata for any ISBN
- **Author details** — bio, birth/death dates, top works
- **Work and edition info** — publication dates, languages, formats
- **Filter and sort** — by language, year, rating, or new arrivals

## What You Get

| Directory | Purpose |
|-----------|---------|
| `SKILL.md` | Complete command reference with examples |
| `scripts/openlibrary-cli` | CLI tool for the Open Library API |

## Quick Start

```bash
openlibrary-cli search --query "dune"
openlibrary-cli search --isbn "9780439358064"
openlibrary-cli search-authors --query "asimov"
```

## Triggers

Load this for book research, ISBN lookups, author information, or cataloging projects.

## Requirements

Python 3.8+ with `requests` library. No API key needed — fully public API.
