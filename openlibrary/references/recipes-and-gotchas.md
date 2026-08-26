# Worked Recipes and Gotcha Compendium

Multi-step pipelines against the Open Library API using `curl`/`jq` (or the bundled
CLI), followed by a symptom-indexed gotcha table. Fundamentals:
[api-overview-and-key-graph.md](api-overview-and-key-graph.md) (key graph, merges),
[search-api-guide.md](search-api-guide.md) (search params/errors),
[books-isbn-and-covers.md](books-isbn-and-covers.md) (ISBN redirects, covers).

## Recipe 1: ISBN → edition → work → full author bio

The canonical resolution chain. Each hop uses a different key type — this is where
OL…M/W/A confusion bites:

```bash
ISBN=9780451524935

# 1. ISBN resolves via 302 to an OL…M edition record (requests follows by default)
curl -sL "https://openlibrary.org/isbn/$ISBN.json" > edition.json

# 2. Pull the work key out of the edition (path form /works/OL…W)
WORK=$(jq -r '.works[0].key' edition.json)          # e.g. /works/OL166894W

# 3. Fetch the work for description + subjects; note double-nested author refs
curl -s "https://openlibrary.org${WORK}.json" > work.json
AUTHOR=$(jq -r '.authors[0].author.key' work.json)  # /authors/OL23919A

# 4. Author record; bio may be {type,value}-wrapped or a plain string
curl -s "https://openlibrary.org${AUTHOR}.json" | jq -r '
  if (.bio | type) == "object" then .bio.value else .bio end'
```

Failure modes at each hop: step 1 needs `-L` in curl or you parse an HTML 302 page;
step 3's `.authors[0].author.key` is wrong on *edition* records (flat `.authors[0].key`
there); step 4 crashes naive parsers when `bio` is an object.

## Recipe 2: search → filter to readable ebooks → fetch editions of the top hit

```bash
# availability requires ia in fields= (silently absent otherwise!)
curl -s 'https://openlibrary.org/search.json' \
  --data-urlencode 'q=title:"moby dick"' \
  --data-urlencode 'fields=key,title,author_name,first_publish_year,ia,ebook_access,availability' \
  --data-urlencode 'sort=editions' --data-urlencode 'limit=5' > hits.json

jq -r '.docs[] | select(.ebook_access == "public") | .key' hits.json | head -1 > workkey
WORK=$(cat workkey)

# enumerate all editions with pagination links
NEXT="/works/${WORK##*/}/editions.json?limit=50"
while [ "$NEXT" != "null" ] && [ -n "$NEXT" ]; do
  curl -s "https://openlibrary.org$NEXT" | jq '.entries[] | {key, isbn_13, publish_date}'
  NEXT=$(curl -s "https://openlibrary.org$NEXT" | jq -r '.links.next // empty')
done
```

## Recipe 3: cover-image URL assembly without blank-image surprises

Cover IDs come from records (`covers:[12054527]`) or search results
(`cover_edition_key`, `cover_i`). Build URLs on the covers host and demand real 404s:

```bash
COVER_ID=$(jq -r '.covers[0] | select(. >= 0)' edition.json | head -1)
for size in S M L; do
  url="https://covers.openlibrary.org/b/id/${COVER_ID}-${size}.jpg?default=false"
  code=$(curl -s -o /dev/null -w '%{http_code}' -L "$url")
  echo "$size $code"   # 200 = exists; 404 = no cover at this size
done
```

Without `?default=false` every probe returns 200 (blank placeholder), so existence
checks silently lie. For batch image pulls, resolve to numeric cover IDs first —
ISBN-based lookups are rate-limited at 100 req/IP per 5 min, ID-based are exempt.

## Recipe 4: author disambiguation via search-authors, then their top works

```bash
curl -s 'https://openlibrary.org/search/authors.json?q=herbert&limit=5' \
  | jq '.docs[] | {name, key, birth_date, death_date, top_work, work_count}'
# pick the right bare OL…A key, then:
curl -s 'https://openlibrary.org/authors/OL3874685A/works.json?limit=10' \
  | jq '{size, works: [.entries[].title]}'
```

Author-search keys arrive **bare** (`OL…A`); book-search keys arrive as paths
(`/works/OL…W`). When assembling URLs from either, strip everything up to the final
slash first.

## Recipe 5: community-signal ranking of a series' entries

```bash
for W in $(curl -s 'https://openlibrary.org/search.json?q=series:dune&limit=8' \
      | jq -r '.docs[].key'); do
  WID=${W##*/}
  ratings=$(curl -s "https://openlibrary.org/works/$WID/ratings.json")
  shelves=$(curl -s "https://openlibrary.org/works/$WID/bookshelves.json")
  jq -n --arg w "$WID" --argjson r "$ratings" --argjson s "$shelves" \
    '{work: $w, avg: $r.summary.average, rated: $r.summary.count,
      want_to_read: $s.counts.want_to_read}'
  sleep 1   # anonymous budget is ~1 req/s; be polite
done
```

## Gotchas indexed by symptom

| Symptom | Cause | Fix |
|---------|-------|-----|
| JSON parse error / HTML instead of data after an ISBN lookup | `/isbn/<isbn>.json` answers **302** to `/books/OL…M.json`; client didn't follow | Follow redirects (`requests` default, `curl -L`) |
| `KeyError: 'author'` reading work authors | Work records double-nest: `authors[].author.key`; editions nest flat | Branch on collection or use a tolerant accessor |
| Bio/description arrives as dict, not string | Legacy `{type: "/type/text", value}` wrapper on older records | `v["value"] if isinstance(v, dict) else v` |
| Requested `availability` missing from search docs | `availability` requires `ia` in the same `fields=` list | `fields=key,title,ia,availability` |
| Search returned 0 results but no error | Malformed q parses loosely and returns HTTP 200 empty; empty/missing q too | Treat empties as results-not-errors; validate input client-side |
| `Internal Server Error` plain text from search | Invalid `sort=` enum (e.g. `bogus`) → HTTP 500 non-JSON | Validate sort choices before sending |
| 422 validation JSON from search | Non-integer `limit`, negative `offset` (FastAPI validation) | Clamp inputs client-side |
| Merged work key returns odd body with HTTP 200 | Wiki merges leave `{type:{key:"/type/redirect"}, location}` stubs, not 3xx | Detect redirect-type bodies and re-fetch `location` |
| Author OLID under `/books/` "fails" | Wrong collection for suffix letter → 301 reroute to correct one | Follow redirects, or normalize keys by suffix before fetching |
| Slug-URL `.json` gives HTML not JSON | `.json` must attach to the bare key (e.g. `/authors/<AUTHOR_KEY>.json`), never after a slug path (`/authors/<AUTHOR_KEY>/Slug.json`) | Append `.json` directly to the key |
| Cover check says exists but image is blank | Missing covers return blank placeholder **with HTTP 200** | Add `?default=false` to get true 404s |
| Covers start returning 403 | Non-ID/non-OLID cover lookups cap at 100 req/IP per 5 min | Resolve to cover IDs (`/b/id/...`), which are exempt |
| Cover/image download stalls mid-pipeline | Cover URLs often 302 into archive.org zip shards | Follow redirects there too |
| Old cached OLID now serves a different book | Deleted keys get reassigned; OLIDs aren't long-term identity | Pair OLID with title/ISBN in caches |
| Rate-limited or blocked entirely | Anonymous budget ~1 req/s (3 identified); no Retry-After header exists | Send `User-Agent: AppName (email)`, cache, sleep ≥1s, batch via search.json |

## Design rules for robust clients

1. Always follow redirects everywhere; both metadata and images redirect routinely.
2. Normalize every key by its suffix letter (M/W/A) and rebuild canonical URLs;
   accept both bare and path forms on input.
3. Handle `{type,value}` text wrapping centrally, once.
4. Never branch on HTTP status alone: merged-stub 200s, silent-empty 200s, and
   non-JSON 500s all exist. Inspect bodies.
5. Identify your client via User-Agent email; sleep between bursts; prefer one
   `/search.json` over hundreds of single-record GETs.
6. Cache by (OLID + title), not OLID alone.

## Sources

- https://openlibrary.org/dev/docs/api/books — identifier endpoints, view models, redirect semantics
- https://openlibrary.org/dev/docs/api/covers — cover URL patterns, default=false, rate limits
- https://openlibrary.org/dev/docs/api/search — fields=/sort/error semantics exercised in recipes
- https://openlibrary.org/dev/docs/api/authors — slug rule, works.json paging, batch-by-key trick
- https://openlibrary.org/developers/api — rate-limit etiquette encoded in recipe sleeps
- https://openlibrary.org/search/howto — field scopes and filters used in queries
- Live read-only probes (2026-08-26) validating each recipe's chain end-to-end
