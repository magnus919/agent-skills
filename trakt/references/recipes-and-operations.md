# Trakt recipes and operations

## Trending to a handoff

1. Run `trakt movie trending --limit 20 --json`.
2. For each object, read `.movie` and retain `.watchers` as the current-watch signal.
3. Pass `.movie.ids.tmdb` or `.movie.ids.imdb` to the next tool only when present; do not mistake a Trakt response for TMDb metadata.

```sh
trakt --json movie trending --limit 20 |
  jq '.movies[] | {title: (.movie.title // .title), year: (.movie.year // null), watchers: (.watchers // null), ids: (.movie.ids // .ids)}'
```

## Compare discovery signals

Fetch the same page of `movie trending`, `movie popular`, and `movie anticipated`. Trending answers "watched recently"; popular answers "high broad popularity"; anticipated answers "appears on many upcoming-interest lists." Keep these datasets labeled when combining them.

## Paginate anticipated releases

The CLI fetches exactly one page per invocation; loop it. Drive the bound from the normalized pagination metadata: `--json` output carries `.pagination.page_count` (empty `{}` if a response lacked the headers, so fall back with jq's `// 1`).

```sh
pages=$(trakt --json movie anticipated --page 1 --limit 100 | jq -r '.pagination.page_count // 1')
for p in $(seq 1 "$pages"); do
  trakt --json movie anticipated --page "$p" --limit 100 > "anticipated-$p.json"
done
```

If you call the API directly instead of through the script, inspect the raw `X-Pagination-Page-Count` header and stop at that count; do not stop merely because a page returned fewer items than `--limit`. If the response is 429, wait at least the numeric `Retry-After` value and cap retries before continuing the loop.

## JSON processing

`--json` emits an object with `movies` or `shows` plus a `pagination` object (`page`, `limit`, `page_count`, `item_count`); trending elements retain their wrapper shape, and human output adds a `Page N of M` footer only when the headers were present. Use `jq` for selection and `@csv` only after explicitly handling null IDs. Human output is for inspection, JSON output is for pipelines.

## Sources

- https://docs.trakt.tv/docs/required-headers
- https://docs.trakt.tv/reference/getmoviestrending
- https://docs.trakt.tv/reference/getmoviesanticipated
- https://trakt.docs.apiary.io/reference/movies/anticipated/get-most-anticipated-movies
