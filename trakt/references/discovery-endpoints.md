# Trakt discovery endpoints

All endpoints below are GET requests at `https://api.trakt.tv` and use the request contract in `auth-and-request-contract.md`.

| Endpoint | Meaning | Response shape |
|---|---|---|
| `/movies/trending` | Most watched movies in the last 24 hours, ordered by watchers | wrapper objects with `watchers` and nested `movie` |
| `/movies/popular` | Popularity based on rating percentage and number of ratings | movie objects |
| `/movies/anticipated` | Upcoming interest based on list appearances | movie objects |
| `/shows/trending` | Most watched shows in the last 24 hours, ordered by watchers | wrapper objects with `watchers` and nested `show` |
| `/shows/popular` | Popularity based on rating percentage and number of ratings | show objects |
| `/shows/anticipated` | Upcoming interest based on list appearances | show objects |

Trending is a short, current watch signal. Popular is a broad popularity ranking, while anticipated is an upcoming-interest signal. Do not treat a trending rank as a release calendar or a popularity score as a personalized recommendation.

## Paging and filters

These feeds accept `page` and `limit`; compatibility defaults are page 1 and limit 10. Set both explicitly for reproducible automation. Responses provide `X-Pagination-Page`, `X-Pagination-Limit`, `X-Pagination-Page-Count`, and `X-Pagination-Item-Count`. Stop at the reported page count instead of assuming a short page means completion.

The bundled CLI forwards `--page` and `--limit` to the query string and normalizes those four headers into a JSON `pagination` object with the keys `page`, `limit`, `page_count`, and `item_count`. Keys are integers when the headers were present; the object is `{}` when the headers are missing, so downstream jq can fall back with `.pagination.page_count // 1`.

Endpoint pages also document filters such as `extended`, `watchnow`, `genres`, `years`, `ratings`, date ranges, countries, and `ignore_watched`, `ignore_collected`, and `ignore_watchlisted` where supported. Encode comma-separated values as query parameters. `watchnow=any` means any service, while `any_all` and the `free_all`/`subscriptions_all` forms have stricter all-country semantics.

## Result normalization

For trending responses, unwrap `movie` or `show` before reading title, year, and IDs, but preserve `watchers` if ranking matters. Popular and anticipated responses are already direct media objects. Trakt IDs are not TMDb metadata: use the returned `ids` object to hand an identifier to another tool, and use TMDb when the task is catalog metadata, credits, images, or provider details.

## Sources

- https://docs.trakt.tv/reference/getmoviestrending
- https://docs.trakt.tv/reference/getmoviespopular
- https://docs.trakt.tv/reference/getmoviesanticipated
- https://docs.trakt.tv/reference/getshowstrending
- https://docs.trakt.tv/reference/getshowspopular
- https://docs.trakt.tv/reference/getshowsanticipated
- https://trakt.docs.apiary.io/reference/movies/trending/get-trending-movies
