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

Use `page` and `limit` in API clients, inspect `X-Pagination-Page-Count`, and stop at that count. If the response is 429, wait at least the numeric `Retry-After` value and cap retries. The CLI intentionally exposes one page per invocation; shell automation can iterate pages while retaining the response headers in a real HTTP client.

## JSON processing

`--json` emits an object with `movies` or `shows`; trending elements retain their wrapper shape. Use `jq` for selection and `@csv` only after explicitly handling null IDs. Human output is for inspection, JSON output is for pipelines.

## Sources

- https://docs.trakt.tv/docs/required-headers
- https://docs.trakt.tv/reference/getmoviestrending
- https://docs.trakt.tv/reference/getmoviesanticipated
- https://trakt.docs.apiary.io/reference/movies/anticipated/get-most-anticipated-movies
