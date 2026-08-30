# Open Library Search API Guide

`/search.json` is the primary read surface: a Solr-backed work index with offset
pagination, field-scoped queries, and server-side projection. This file documents the
full parameter surface, result schema, sibling search endpoints, and the error model
observed live. Key-graph basics (OL…M/W/A) live in
[api-overview-and-key-graph.md](api-overview-and-key-graph.md); ISBN/edition/covers
endpoints in [books-isbn-and-covers.md](books-isbn-and-covers.md).

## Endpoint and parameters

```
GET https://openlibrary.org/search.json?q=<query>&<params...>
```

| Parameter | Behavior |
|-----------|----------|
| `q` | Solr query string; supports field scopes and Lucene syntax (below). |
| `fields` | Comma-separated projection. `*` returns ~120 fields (docs warn it's "expensive, please use sparingly"). Special value `availability` adds an availability subdocument — **only if `ia` is also requested** (gotcha below). |
| `sort` | One of the sort keys below; default is relevance. Invalid values cause an HTTP 500 (error model below). |
| `limit` / `offset` | Offset pagination. `page`/`limit` also works (page starts at 1); if both `page` and `offset` are sent, **offset wins**. |
| `lang` | Two-letter ISO 639-1 preference — "influences but doesn't exclude" results. To *exclude*, use `language:<code>` inside `q`. |
| `title`, `author` | Top-level scoped params equivalent to prefixing inside q (e.g. `/search.json?title=the+lord+of+the+rings`). |

### Sort keys

All of these returned HTTP 200 in live probes (`q=harry potter&limit=1`);
the authoritative enumeration lives in Open Library source
(`openlibrary/plugins/worksearch/schemes/works.py`):

`new`, `old`, `rating asc`, `rating desc` (bare `rating` = desc), `editions`, `title`,
`scans`, `key` (sorts as a *string*, not numerically), `random`, `readinglog`,
`already_read`, `want_to_read`, `currently_reading`, `ebook_access`.

The existing CLI exposes `--sort {editions,new,old,rating,title}` plus empty for
relevance — a safe subset.

## Pagination model: offsets only, no tokens

There is no cursor or token concept anywhere on this API — clients compute the next
offset from `numFound` and `start`:

```json
{"numFound": 4045, "start": 0, "numFoundExact": true,
 "num_found": 4045, "documentation_url": "...", "q": "harry potter",
 "offset": null, "docs": [...]}
```

- `start` mirrors the effective zero-based offset of the first doc
  (`page=3&limit=10` → `start: 20`).
- `numFoundExact: false` signals the count is approximate.
- No documented cap on `limit` or `offset`: live probes honored `limit=2000` and
  `offset=11000`. The response simply clamps to the matched set. Stay modest anyway —
  the etiquette policy forbids using OL as a bulk backend.

## Result document schema

Common `docs[]` fields: `key` (path form `/works/OL…W`), `title`, `author_name[]`,
`author_key[]`, `first_publish_year`, `edition_count`, `cover_edition_key`,
`cover_i`, `ia[]` (Internet Archive scan ids), `has_fulltext`, `public_scan_b`,
`language[]`, `subject[]`, `publisher[]`, `publish_year[]`, `isbn[]`,
`number_of_pages_median`, `ebook_access`, `ratings_average`, `ratings_count`,
`readinglog_count`, `seed[]`.

The docs state the schema "is not guaranteed to be stable, but most common fields …
should be safe to depend on". Treat exotic fields as best-effort.

## Query syntax: field scopes and filters

Verified live prefixes:

| Prefix | Example | Notes |
|--------|---------|-------|
| `title:` | `q=title:flammable` | 551 hits |
| `author:` | `q=author:solnit` | 129 hits |
| `subject:` | `q=subject:"tennis rules"` | fuzzy containment (AND), not exact phrase |
| `publisher:` | `q=publisher:harper` | 77,889 hits |
| `isbn:` | `q=isbn:9780451524935` | ISBN-10 and ISBN-13 both resolve to the same single work |
| `language:` | `q=language:fre` | excludes works without matching-language editions |

Lucene extras from the official how-to ([search/howto](https://openlibrary.org/search/howto)):
ranges (`first_publish_year:[1200 TO 1400]`, `publish_year:[* TO 1800]`),
booleans `AND`/`OR`/`NOT`, negation `-subject_key:"apache_solr"`,
prefix wildcards `ddc:200*`, normalized exact keys (`subject_key:`, `person_key:`,
`place_key:`, `time_key:` — lowercase, spaces/slashes → underscores),
availability filter `ebook_access:` with values `no_ebook`, `printdisabled`,
`borrowable`, `public`, plus `has_fulltext:true`, `edition_count:N`,
`readinglog_count:[25 TO *]`.

## The `fields=` projection and its availability gotcha

Requesting fewer fields shrinks payloads dramatically. Live behavior:

- `fields=key,title` returns exactly those keys per doc.
- **`availability` is silently omitted unless `ia` is also requested** — verified live:
  - `fields=key,title,availability` → doc keys exactly `['key','title']`
  - `fields=key,title,ia,availability` → full availability subdocument present

With `ia` included, each doc gains:

```json
"availability": {
  "status": "borrow_available",
  "is_readable": false,
  "is_lendable": true,
  "is_printdisabled": true,
  "openlibrary_work": "OL82563W",
  "openlibrary_edition": "OL61057835M", ...
}
```

`status` values include `borrow_available`, `borrow_unavailable`, `printdisabled`,
`open` (readable), and absent/`error` when no scan exists.

Bonus expansion: `fields=key,title,editions` nests a mini-result-set under each work
(`numFound`/`start`/`docs[]` with edition fields); individual edition fields are
requested as `editions.key`, `editions.ebook_access`, `editions.language`;
`&editions.sort` overrides default boosting.

## Author search: `/search/authors.json`

Same envelope (`numFound`/`start`/`docs[]`); author docs carry bare-form keys
(`OL9937375A`) unlike book-search path keys:

```json
{"name": "Mark Twain", "key": "OL9937375A",
 "birth_date": "30 November 1835", "death_date": "21 April 1910",
 "top_work": "Roughing It", "work_count": 2157,
 "top_subjects": ["Twain, mark, 1835-1910", ...]}
```

Supports Solr syntax in `q` too (e.g. `birth_date:1973`) plus `limit`/`offset`.
Note `birth_date`/`death_date` may be null or free-text strings ("7 February 1812") —
they are display strings, not typed dates.

Batch-fetch trick documented on the Authors API page: partial author records via
book search with `q=key:(/authors/OL11111A OR /authors/OL22222A)`; there is no
batch endpoint for full author records.

## Subject browsing: `/subjects/<name>.json` (plural!)

The Subjects API ([dev/docs/api/subjects](https://openlibrary.org/dev/docs/api/subjects),
marked experimental) browses works grouped by normalized subject:

```
GET https://openlibrary.org/subjects/pizza.json?limit=1
→ {"key": "<RECORD_KEY>", "name": "pizza", "work_count": 519,
   "works": [{"key": "<RECORD_KEY>", "title": "Pete's a Pizza",
              "edition_count": 19, "authors": [{"name": "William Steig"}],
              "first_publish_year": 1998, "availability": {...}}, ...]}
```

- Path is **plural** `/subjects/<name>.json`; singular `/subject/pizza.json` 404s
  (live-verified).
- Names use underscores: `science_fiction`.
- Params: `details=true` (adds related `subjects[]`/`authors[]`/`publishers[]`
  with counts plus `publishing_history`), `ebooks=true`, `published_in=1500-1600`,
  `limit`, `offset`.
- Works here include `availability` by default, unlike `/search.json`.
- Sibling collections exist for persons/places/times (`/persons/<name>.json` etc.).

## Full-text inside-book search: `/search/inside.json`

Searches OCR text across millions of scanned books; Elasticsearch-shaped response:

```
GET https://openlibrary.org/search/inside.json?q=%22library science%22
→ hits.total, hits.hits[] with _id (ia identifier), _score,
  highlight.text[] ("{{{Library Science}}}" marks matches),
  fields.identifier (ia id), edition.key/title, availability
```

Default page size 20; `limit`/`offset` supported (live-verified). A separate,
documented-but-experimental *per-book* inside search actually runs on archive.org
data nodes (`https://ia800204.us.archive.org/fulltext/inside.php?item_id=...`)
— see [dev/docs/api/search_inside](https://openlibrary.org/dev/docs/api/search_inside)
if you need per-page match geometry; that host is outside this skill's CLI.

## Error model: silent empties vs hard failures

Live-probed status codes — counterintuitive but consistent:

| Request | Status | Body |
|---------|--------|------|
| missing or empty `q` | **200** | normal envelope, `numFound: 0`, `docs: []` |
| malformed query `q=title:"unclosed` | **200** | `numFound: 0` — no error surfaced |
| loosely-parseable garbage `q=(OR` | **200** | 568k loose matches |
| invalid enum `sort=bogus` | **500** | plain text `Internal Server Error` (not JSON!) |
| non-integer `limit=abc` | **422** | FastAPI validation JSON `{"detail":[{"type":"int_parsing",...}]}` |
| negative `offset=-5` | **422** | FastAPI validation JSON `greater_than_equal` |
| singular `/subject/pizza.json` | **404** | HTML error page |

Design consequence: user-facing "no results" is usually **not** an error — treat empty
`docs` as success. Conversely a bad `--sort` choice fails loudly as non-JSON 500, so
clients should validate sort choices before sending (as the bundled CLI does).

One environment caveat observed during research: responses can arrive with key fields
masked to asterisks by anti-bot middleware depending on client reputation. Production
responses carry real keys (the docs' own examples show them), but parsers should
tolerate both `OL…W` and `/works/OL…W` shapes and not assume key presence.

## Sources

- https://openlibrary.org/dev/docs/api/search — Search API parameters, fields= semantics, editions sub-query
- https://openlibrary.org/search/howto — query syntax, field scopes, filter examples
- https://openlibrary.org/developers/api — rate-limit etiquette applying to search traffic
- https://openlibrary.org/dev/docs/api/authors — author batch-fetch via key:(…) search
- https://openlibrary.org/dev/docs/api/subjects — Subjects API params (details/ebooks/published_in)
- https://openlibrary.org/dev/docs/api/search_inside — experimental per-book inside search (archive.org hosted)
- Live read-only probes against openlibrary.org (2026-08-26): sort keys, limit/offset ranges, fields=availability interaction, error status codes
