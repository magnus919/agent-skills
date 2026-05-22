---
name: openlibrary-cli
description: >-
  Search books, authors, and works on Open Library from the terminal. Look up
  books by ISBN, search titles and authors, and fetch detailed work/author
  records via the public Open Library API. No API key required.
license: MIT
compatibility: Python 3.8+ and the `requests` library. No API key or registration
  required — the Open Library API is fully public. Optional OL_EMAIL env var
  sets a User-Agent contact for improved rate limiting.
metadata:
  tags: [open-library, books, authors, isbn, library, book-search, api-client, catalog]
  sources:
    - https://openlibrary.org/developers/api
    - https://openlibrary.org
---

# openlibrary-cli — Book Metadata from Open Library

Search books and authors, look up works and ISBNs, and fetch detailed metadata from the public [Open Library](https://openlibrary.org) API. No API key, no registration — just works.

## Setup

No authentication or API keys needed. The Open Library API is fully public.

```bash
# Optional: set your email to help with rate limiting (included in User-Agent):
export OL_EMAIL="you@example.com"
```

Only Python 3.8+ and the `requests` package are required. `--help` and `--dry-run` work without any setup.

## Essential Commands

### search — Search books by keyword

```bash
openlibrary-cli search --query "dune"                       # basic search (20 results)
openlibrary-cli search --query "dune" --limit 5             # just the top 5
openlibrary-cli search --query "dune" --sort new            # newest first
openlibrary-cli search --query "dune" --sort rating         # highest rated first
openlibrary-cli search --query "dune" --sort title          # alphabetical by title
openlibrary-cli search --query "foundation" --lang fr       # French editions
openlibrary-cli search --query "dune" --json                # machine-readable JSON
```

Shows: title, first publish year, authors, edition count. Supports `--sort` (editions, new, old, rating, title), `--lang`, `--offset`, and `--availability`.

### search-authors — Search authors by name

```bash
openlibrary-cli search-authors --query "asimov"             # search authors
openlibrary-cli search-authors --query "asimov" --limit 5   # top 5
openlibrary-cli search-authors --query "asimov" --json      # machine-readable
```

Shows: name, birth/death years, author key, top work.

### author — Get author details by key

```bash
openlibrary-cli author OL23919A                             # Isaac Asimov
openlibrary-cli author OL34184A                             # Ursula K. Le Guin
openlibrary-cli author OL23919A --json                      # full biography
```

Shows: name, birth/death dates, biography (up to 500 chars), Wikipedia link, personal name. Author keys are the `OL#####A` identifiers from search results.

### work — Get work details by key

```bash
openlibrary-cli work OL123W                                 # work by key
openlibrary-cli work OL81699W                               # "Foundation"
openlibrary-cli work OL81699W --json                        # full description
```

Shows: title, author keys, subjects, description (up to 500 chars). Work keys are the `OL#####W` identifiers found in search results.

### isbn — Lookup a book by ISBN

```bash
openlibrary-cli isbn 9780451524935                           # ISBN lookup
openlibrary-cli isbn 9780553382563                           # another book
openlibrary-cli isbn 9780451524935 --json                    # full edition metadata
```

Shows: title, author(s), page count, publish date, publisher, subjects (top 5). Accepts both ISBN-10 and ISBN-13.

## Global Flags

These flags work anywhere in the command — before or after the subcommand:

```bash
openlibrary-cli --json search --query "dune"                # JSON output
openlibrary-cli search --query "dune" --json                # same result, after subcommand
openlibrary-cli --dry-run search --query "dune"             # preview without API call
openlibrary-cli --quiet search --query "dune"               # suppress diagnostic output
openlibrary-cli --verbose author OL23919A                   # verbose logging
openlibrary-cli --dry-run isbn 9780451524935                # see what URL would be used
```

| Flag | Effect |
|------|--------|
| `--json` | Output machine-readable JSON instead of human-readable text |
| `--dry-run` | Show what API call would be made without executing it |
| `--quiet` | Suppress non-essential diagnostic output |
| `--verbose` | Enable verbose/debug logging |

## Known Gotchas

- **Public API, rate-limited** — No API key is needed, but Open Library enforces rate limits on unauthenticated requests. Set `OL_EMAIL` in your environment to include a contact email in the User-Agent header for better rate limit treatment.
- **ISBN lookup uses an edition endpoint** — The `isbn` command fetches `/isbn/{isbn}.json` which returns edition-level metadata (publisher, page count, publish date). For work-level metadata (description, subjects of the underlying work), use the `work` command with the work key from search results.
- **Search results are not stable** — Open Library's search index can return slightly different results for the same query over time. Use `--sort` and `--limit` for reproducible result sets.
- **Author keys from search are relative paths** — Search results return `key` as `/authors/OL23919A`. The CLI strips the prefix so you can use the bare key (e.g. `OL23919A`) directly with the `author` command.
- **Biographies and descriptions may be nested** — The Open Library API sometimes returns bio/description as a dict with a `value` key instead of a plain string (e.g. `{"type": "/type/text", "value": "..."}`). The CLI handles this automatically.
- **No lazy auth** — Unlike other CLI skills, no authentication setup is needed at all. The API is fully public, so `--help`, `--dry-run`, and all commands work without any env vars.
- **Pagination** — Use `--offset` to paginate through search results. The CLI defaults to 20 results and does not auto-paginate.
- **Work vs Edition** — A "work" is the abstract creative work (e.g. "Dune"). An "edition" is a specific published version (e.g. the 1965 hardcover). The `work` command returns work-level data; the `isbn` command returns edition-level data. The `search` command returns work-level results with edition counts.

## References

- [scripts/openlibrary-cli](scripts/openlibrary-cli) — The CLI binary. Built following the cli-builder patterns: non-interactive, `--json`, `--dry-run`, `--quiet`, `--verbose`, dual-output via `emit()`, structured logging.
- [Open Library API Docs](https://openlibrary.org/developers/api) — Official API documentation.
- [Open Library](https://openlibrary.org) — The open, editable library catalog.
