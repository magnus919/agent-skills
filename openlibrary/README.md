# Open Library — Book Metadata from the Terminal

Search books and authors, resolve ISBNs, walk the edition/work/author graph,
enumerate editions, and read community ratings from the public Open Library
API. No API key exists — every read is keyless.

## Why Install This Skill

When your agent loads this skill, it gets **structured access to 50M+ book records**
without any signup or credentials:

- **Search anything** — keyword queries with sort by edition count, date, or title; field-scoped lookups by title, author, subject, publisher, or ISBN
- **Resolve any identifier** — turn an ISBN/LCCN/OCLC into a canonical edition record and follow it up to the abstract work and its author
- **Enumerate editions** — every published version of a work with dates, publishers, and ISBNs
- **Read community signals** — star ratings and want-to-read counts per work
- **Get cover images correctly** — proper URLs on Open Library's dedicated image host, with existence checks that actually return 404 instead of blank placeholders

The skill also encodes where agents typically trip: ISBN endpoints that answer
302 redirects, merged-record keys that hide redirect stubs inside HTTP 200
responses, the OL…M/W/A key-suffix system, `{type,value}`-wrapped text fields,
and rate-limit etiquette that keeps you unblocked.

## What You Get

| Path | Purpose |
|------|---------|
| `SKILL.md` | Command reference: setup, intent-grouped commands, pipeline recipes, jq guidance, known gotchas |
| `scripts/openlibrary` | CLI tool for the Open Library API (`--json`, `--dry-run`, automatic redirect resolution) |
| `scripts/test_openlibrary.py` | Offline test suite for the CLI (help/errors/dry-run/mocked logic; live probes env-guarded) |
| `references/api-overview-and-key-graph.md` | Access model, rate etiquette, OLID key graph, merge-stub behavior |
| `references/search-api-guide.md` | Search parameters, sort keys, query syntax, sibling search endpoints, error model |
| `references/books-isbn-and-covers.md` | ISBN/identifier resolution, view models, editions, ratings, covers-host rules |
| `references/recipes-and-gotchas.md` | Worked curl/jq pipelines and a symptom-indexed gotcha table |
| `evals/evals.json` | Behavioral eval cases covering searches, pipelines, gotchas |

## Quick Start

```bash
openlibrary search --query "dune"                 # find works
openlibrary isbn 9780451524935                    # resolve an ISBN to its edition
openlibrary editions OL81699W                     # list every edition of a work
openlibrary ratings OL45804W                      # community signals
```

Optional politeness knob:

```bash
export OL_EMAIL="you@example.com"   # adds contact to User-Agent; ~3x rate budget
```

## Triggers

Load this for book research, ISBN or OLID lookups, author biographies, edition
enumeration, reading-level community stats, cover-image URL assembly, or any
question about the Open Library catalog itself.

## Requirements

- Python 3.8+ with the `requests` library
- No API key, no account — reads are fully public
- `jq` recommended for processing `--json` output
