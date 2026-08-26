# Open Library API Overview and the OLID Key Graph

Open Library (an Internet Archive project) exposes its catalog of 50M+ records through
public, keyless HTTP APIs. This file covers the access model, etiquette, and the
record-key graph that everything else builds on. Companion files: the Search API
([search-api-guide.md](search-api-guide.md)), ISBN/Books/Covers endpoints
([books-isbn-and-covers.md](books-isbn-and-covers.md)), and worked recipes
([recipes-and-gotchas.md](recipes-and-gotchas.md)).

## Access model: no key, three hosts, open CORS

Reads require **no API key and no registration**. Three hostnames matter:

| Host | Serves |
|------|--------|
| `openlibrary.org` | Metadata JSON: search, works, editions, authors, ratings |
| `covers.openlibrary.org` | Cover images and author photos (separate service) |
| `archive.org` | Ebook/scan content and bulk dumps (redirect targets) |

Metadata endpoints answer `application/json`, support `GET` + `OPTIONS`, and send
`access-control-allow-origin: *`, so browser-side fetches work directly.

Optional identification: put your app name and contact email in the User-Agent,
e.g. `User-Agent: MyLibraryApp (contact@example.org)`. Identified traffic gets a 3x
rate allowance (see below) and gives staff someone to contact before blocking you.
There is no token, secret, or account step anywhere in the read surface.

## Rate limits and etiquette (official guidance)

From the official APIs index page ([developers/api](https://openlibrary.org/developers/api)):

- Anonymous clients: **1 request/second**. Identified clients (User-Agent carrying app
  name + contact email/phone): **3 requests/second** ("identified requests will enjoy a
  3x request limit").
- No `X-Rate-Limit-*` or `Retry-After` headers are sent today; the limit is advisory
  policy, not header-signaled. Exceeding it politely means sleeping, because there is
  nothing to read out of the response.
- Explicitly discouraged: HTML scraping (use the API endpoints), spreading traffic
  across 5+ IPs, bulk harvesting, hundreds of single-book GETs where one
  `/search.json` batch would do, or using Open Library as a backend for a
  high-traffic service. Violations bring "aggressive rate limiting or blocking".
- For bulk data use the monthly dumps instead
  ([developers/dumps](https://openlibrary.org/developers/dumps)): editions ~9.2G,
  works ~2.9G, authors ~0.5G, ratings/reading-log much smaller. Dump lines are
  `type, key, revision, last_modified, JSON`.

The covers service has its own harder limit: non-ID/non-OLID cover lookups are capped
at **100 requests/IP per 5 minutes**, then **403 Forbidden**
([dev/docs/api/covers](https://openlibrary.org/dev/docs/api/covers)).

## The key graph: OLIDs and the letter-suffix type system

Every catalog entity has a stable-shaped identifier called an OLID whose **final
letter encodes the type**:

| Suffix | Type | Canonical JSON path | Example |
|--------|------|--------------------|---------|
| `M` | Edition (a physical/digital publication) | `/books/OL34854896M.json` | `OL34854896M` |
| `W` | Work (the abstract creative work) | `/works/OL45804W.json` | `OL45804W` |
| `A` | Author | `/authors/OL23919A.json` | `OL23919A` |

Two surface forms appear in payloads and docs alike: bare OLIDs (`OL45804W`) and
path keys (`/works/OL45804W`). Search results return path keys for works
(`/works/OL…W`) but bare keys in author search (`OL…A`). Parse defensively: strip or
add the collection prefix by inspecting the suffix letter rather than assuming one form.

Graph wiring, verified against live records:

- **Edition → work**: `edition.works` is a list of key refs:
  `"works": [{"key": "<RECORD_KEY>"}]`.
- **Work → authors**: double-nested, with a role node:
  `"authors": [{"author": {"key": "<RECORD_KEY>"}, "type": {"key": "<RECORD_KEY>"}}]`.
  Read `work.authors[].author.key`, never `work.authors[].key`.
- **Edition → authors**: flat single nesting instead:
  `"authors": [{"key": "<RECORD_KEY>"}]`. The two collections disagree — handle both.
- **Work → editions**: not embedded; enumerate via `/works/OL…W/editions.json`
  (see [books-isbn-and-covers.md](books-isbn-and-covers.md)).
- Common record furniture: `type.key` (`/type/edition`, `/type/work`,
  `/type/author`), integer-array `covers` / `photos`, `created`/`last_modified`
  timestamps, `revision`/`latest_revision` integers.

## Wrong key type: cross-collection 301 reroutes

Requesting a key under the wrong collection is forgiven with a redirect to the right
one (live-verified):

```
GET https://openlibrary.org/books/OL23919A.json   # author OLID under /books
HTTP/2 301
location: https://openlibrary.org/authors/OL23919A.json

GET https://openlibrary.org/works/OL123M.json     # edition OLID under /works
HTTP/2 301
location: https://openlibrary.org/books/OL123M.json
```

So a client that follows redirects survives suffix/collection mismatches automatically
(`requests` follows by default; `curl` needs `-L`). The practical symptom of *not*
following: your parser sees an HTML 301 page instead of JSON.

## Missing keys and the merge problem: redirect stubs inside HTTP 200

Truly nonexistent keys 404 with a JSON body:

```
GET https://openlibrary.org/books/OL999999999M.json
HTTP/2 404
{"error": "notfound", "key": "<RECORD_KEY>"}
```

But Open Library is a wiki: duplicates are merged and spam is deleted, and **merged
keys do not 3xx**. A merged-away key keeps serving `HTTP 200` with a stub record
(live-verified on a real merge found via `/recentchanges/merge-works.json`):

```json
{"location": "<RECORD_KEY>",
 "type": {"key": "<RECORD_KEY>"},
 "latest_revision": 4, "revision": 4, ...}
```

The old key `/works/OL24776360W` had just been merged into `/works/OL14868272W`, yet
the JSON endpoint returned **200**, not 302. Clients must detect
`payload["type"]["key"] == "/type/redirect"` in successful responses and re-fetch
`payload["location"]` themselves. (The HTML page for the same key does 302; only JSON
gives you the stub.) The bundled CLI performs this follow-up automatically.

Related identity hazards:

- **Deleted-and-reassigned keys**: an OLID freed by deletion can be reissued for an
  unrelated book (observed live). Never treat an OLID as long-term identity for
  caching; pair it with title or ISBN.
- Recent merges are observable at `/recentchanges/merge-works.json?limit=N`
  (`data.master`, `data.duplicates[]`) if you need to audit drift.

## Text-valued fields nest `{type, value}` objects

Free-text fields (`bio` on authors; `description`, `notes`, `first_sentence` on
editions/works) arrive in **two shapes** depending on record age:

```json
"bio": {"type": "/type/text", "value": "Joanne \"Jo\" Murray, OBE ..."}
```

Older records carry a plain string instead. Always branch: if dict, take `["value"]`;
if str, use as-is. The bundled CLI unwraps these automatically.

Photo/cover ID arrays mix in `-1` placeholders meaning "no image"
(e.g. `"photos": [5543033, -1]`): filter out negatives before building image URLs.

## Author URL quirk: `.json` placement matters

Bare author URLs HTML-redirect to slugged pages
(`/authors/OL23919A` → `/authors/OL23919A/J._K._Rowling`). Appending `.json` after
the slug (`/authors/OL23919A/J._K._Rowling.json`) does **not** serve JSON — append
it to the bare key: `/authors/<AUTHOR_KEY>.json`
([dev/docs/api/authors](https://openlibrary.org/dev/docs/api/authors)).

## Writes exist but are outside the keyless surface

Authenticated writes exist (`POST /account/login.json` with Internet Archive S3 keys
returns a session cookie; `PUT` resource JSON updates records), but the RESTful doc
states this is effectively internal: PUT/POST without permission returns **403**, and
the docs warn the API "works only from the localhost"
([dev/docs/restful_api](https://openlibrary.org/dev/docs/restful_api)). Plan around
reads only; expect every write path to require credentials this skill deliberately
does not handle.

## Sources

- https://openlibrary.org/developers/api — API index; rate limits (1/s anonymous, 3/s identified), User-Agent identification format, bulk-access policy
- https://openlibrary.org/dev/docs/api/authors — Authors API; slug/`.json`-placement rule
- https://openlibrary.org/dev/docs/api/books — Books/Editions/Works API; record shapes
- https://openlibrary.org/dev/docs/restful_api — write/login mechanics, status codes, localhost-only caveat
- https://openlibrary.org/developers/dumps — monthly dump catalog and line format
- Live read-only probes against openlibrary.org (2026-08-26): 301 cross-collection reroutes, 404 body shape, merge-stub 200 responses, `{type,value}` text nesting
