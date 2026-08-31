# ISBN Lookup, Editions, Ratings, and the Covers Host

This file covers everything keyed to a specific book: identifier-style endpoints
(ISBN/LCCN/OCLC/OLID), their 302-redirect resolution, the legacy Books API view
models, edition enumeration under a work, community aggregates, and image URLs on
the separate covers host. Key-graph fundamentals are in
[api-overview-and-key-graph.md](api-overview-and-key-graph.md).

## Identifier endpoints answer 302, not JSON

`/isbn/<isbn>.json`, `/lccn/<lccn>.json`, and `/oclc/<num>.json` do not serve the
record directly. They **redirect (HTTP 302) to the canonical edition JSON** at
`https://openlibrary.org/books/<EDITION_OLID>.json`. Live transcripts:

```
$ curl -is 'https://openlibrary.org/isbn/9780451524935.json'
HTTP/2 302
location: https://openlibrary.org/books/OL34854896M.json

$ curl -is 'https://openlibrary.org/lccn/93005405.json'
HTTP/2 302
location: https://openlibrary.org/books/OL1397864M.json

$ curl -is 'https://openlibrary.org/oclc/28419896.json'
HTTP/2 302
location: https://openlibrary.org/books/OL1397864M.json
```

Practical consequences:

- **Follow redirects or get nothing useful.** Python `requests.get()` follows by
  default; `curl` needs `-L`; a raw HTTP client that ignores Location sees only an
  HTML 302 page.
- After following, you land on `200 application/json`, the raw edition record —
  including its `key` (`/books/OL34854896M`), which is how you discover which edition
  an ISBN resolved to.
- The official Books API doc documents the HTML flavor of this redirect
  (`/isbn/9780140328721` → `/books/OL7353617M`) and notes `.json` may be appended to
  such page URLs; the 302-on-JSON behavior itself is established by live probes.
- An ISBN matching no record eventually 404s after redirects with body
  `{"error": "notfound", ...}`.

Direct edition keys skip the redirect entirely: `/books/OL7440033M.json` → `200`.

## Raw edition records vs the legacy Books API view models

**Two different representations exist for the same book.** Know which one you have:

1. **Raw record** (what identifier endpoints redirect to): flat bibliographic fields,
   string arrays for `publishers`, integer-array `covers`, path-shaped `key`,
   `type: {"key": "<RECORD_KEY>"}`, key-ref lists `works[]`/`authors[]`.
   Observed fields include: `title`, `subtitle`, `isbn_10`, `isbn_13`, `lccn`,
   `oclc_numbers`, `publishers`, `publish_date`, `publish_places`, `number_of_pages`,
   `pagination`, `languages` (`[{"key": "<RECORD_KEY>"}]`), `covers`, `works`,
   `authors`, `description`, `notes`, `first_sentence`, `table_of_contents`,
   `identifiers`, `lc_classifications`, `dewey_decimal_class`, `weight`,
   `physical_format`, `edition_name`, `copyright_date`, `ocaid` (the archive.org
   scan id), `source_records`.

2. **Legacy view models** via `GET /api/books?bibkeys=ISBN:<isbn>&format=json&jscmd=<mode>`:

   | jscmd | Shape |
   |-------|-------|
   | *(absent)* / `viewapi` | Tiny object: `bib_key`, `info_url`, `preview` (`noview`/`full`/`restricted`), `preview_url`, `thumbnail_url`. Use `preview` to test readability; `preview_url` is always present even when unreadable. |
   | `data` | Friendly model: `url`, `title`, `authors[{name,url}]`, `publishers[{name}]` (objects!), grouped `identifiers{isbn_10,isbn_13,lccn,oclc,goodreads,...}`, `classifications{lc_classifications,dewey_decimal_class}`, `subjects[]`, ready-made `cover{small,medium,large}` URLs, `ebooks[]`, `excerpts[]`, `links[]`. Docs recommend this as the stable format. |
   | `details` | viewapi fields plus a nested raw record under `details`; docs advise using `jscmd=data` instead. |

   `bibkeys` is comma-separated with prefixes `ISBN:`, `OCLC:`, `LCCN:`, `OLID:`;
   both ISBN-10 and ISBN-13 accepted. `format=json` required for machine use (default
   is JSONP-style JavaScript). The whole `/api/books` endpoint is flagged legacy
   ("may be phased out"); prefer search + direct record fetches for new work.

Live contrast for ISBN 9780451524935:

```json
// jscmd=data
{"ISBN:9780451524935": {
    "title": "Nineteen Eighty-Four",
    "url": "http://openlibrary.org/books/OL34854896M/Nineteen_Eighty-Four",
    "publishers": [{"name": "Signet Classics"}],
    "cover": {"small":  "https://covers.openlibrary.org/b/id/12054527-S.jpg",
              "medium": "https://covers.openlibrary.org/b/id/12054527-M.jpg",
              "large":  "https://covers.openlibrary.org/b/id/12054527-L.jpg"}, ...}}

// default viewapi
{"ISBN:9780451524935": {"bib_key": "ISBN:9780451524935",
    "info_url": "http://openlibrary.org/books/OL34854896M/Nineteen_Eighty-Four",
    "preview": "restricted", "preview_url": "https://archive.org/details/nineteeneightyfo0000orwe_g7l1",
    "thumbnail_url": "https://covers.openlibrary.org/b/id/12054527-S.jpg"}}
```

## Listing every edition of a work

```
GET https://openlibrary.org/works/<WORK_OLID>/editions.json[?limit=N&offset=M]
```

Response envelope:

```json
{"size": 6,
 "links": {"self": "/works/OL81699W/editions.json?limit=2",
           "work": "/works/OL81699W",
           "next": "/works/OL81699W/editions.json?limit=2&offset=2"},
 "entries": [ {full edition records}, ... ]}
```

- `entries[]` holds complete edition records (same shape as single-edition JSON).
- Pagination via `limit`/`offset` verified live; while more pages remain,
  `links.next` carries the prebuilt next URL — follow it rather than recomputing.
- The same `size`/`links.self`/`entries` structure serves author works at
  `/authors/OL…A/works.json` (default page size 50 there, `limit` up to 1000 per the
  Authors API doc).

## Community aggregates on works

Public, keyless GETs on any work key:

**Ratings** — `GET /works/<OLID>/ratings.json`

```json
{"summary": {"average": 3.966386554621849, "count": 119, "sortable": 3.7388955319679584},
 "counts": {"1": 10, "2": 6, "3": 18, "4": 29, "5": 56}}
```

Note the string keys `"1"`–`"5"` in `counts`, and that `summary.average` is absent
when nobody has rated.

**Bookshelves** — `GET /works/<OLID>/bookshelves.json`

```json
{"counts": {"want_to_read": 1191, "currently_reading": 97,
            "already_read": 189, "stopped_reading": 0}}
```

Shelf names are literal: `want_to_read`, `currently_reading`, `already_read`,
`stopped_reading`.

A per-work `/readinglog.json` route is **not part of the documented public API** (404
in testing); reading-log data flows through the My Books API
([dev/docs/api/mybooks](https://openlibrary.org/dev/docs/api/mybooks)) — e.g.
`/people/<username>/books/want-to-read.json` — or monthly dumps.

## Covers and author photos: a separate host with its own rules

All images live on `covers.openlibrary.org`, never on `openlibrary.org`:

```
Book covers:  https://covers.openlibrary.org/b/{id|olid|isbn|lccn|oclc}/<value>-{S|M|L}.jpg
Author photos: https://covers.openlibrary.org/a/{id|olid}/<value>-{S|M|L}.jpg
Cover metadata: append .json → https://covers.openlibrary.org/b/id/12547191.json
```

Sizes: S = thumbnail, M = details-page size, L = large. The same cover is reachable
by any of its keys (`/b/id/240727-S.jpg`, `/b/olid/OL7440033M-S.jpg`,
`/b/isbn/0385472579-S.jpg` all hit one image).

Behaviors verified live:

- Cover URLs commonly **302 into archive.org zip shards**
  (`location: https://archive.org/download/s_covers_0012/s_covers_0012_05.zip/0012054527-S.jpg`);
  some lookups answer 200 directly. Follow redirects regardless.
- A missing cover returns a **blank placeholder image with HTTP 200** unless you add
  `?default=false`, which yields a proper **404**:
  ```
  $ curl -sI '.../b/id/999999999999-M.jpg'            → HTTP 200 (blank)
  $ curl -sI '.../b/id/999999999999-M.jpg?default=false' → HTTP 404
  ```
  Always pass `default=false` when you need existence semantics.
- Rate limit: non-ID/non-OLID lookups (ISBN/LCCN/OCLC forms) are capped at
  **100 requests/IP per 5 minutes**, then **403 Forbidden**; ID- and OLID-based
  lookups are exempt ([dev/docs/api/covers](https://openlibrary.org/dev/docs/api/covers)).
  Resolve to cover IDs first if you will fetch many images.
- Cover metadata JSON includes `width`, `height`, `olid`, shard filenames — handy for
  checking existence before downloading.
- Author photo IDs come from the author record's `photos` array (filter out `-1`
  placeholders) and map to `/a/id/<photo_id>-<S|M|L>.jpg`.
- Etiquette: don't crawl covers; bulk archives live on archive.org items
  (`s_covers_*`, `m_covers_*`, `l_covers_*`). A courtesy link back to Open Library is
  appreciated when displaying covers.

## Sources

- https://openlibrary.org/dev/docs/api/books — identifier endpoints, redirect behavior, legacy /api/books and jscmd modes
- https://openlibrary.org/dev/docs/api/covers — URL patterns, sizes, default=false, rate limits
- https://openlibrary.org/dev/docs/api/authors — /authors/…/works.json pagination
- https://openlibrary.org/dev/docs/api/mybooks — documented reading-log surface
- https://openlibrary.org/developers/api — etiquette governing image/metadata fetching
- Live read-only probes against openlibrary.org and covers.openlibrary.org (2026-08-26): 302 Locations, editions.json envelope, ratings/bookshelves shapes, blank-vs-404 cover behavior, archive.org shard redirects
