# TMDb Authentication, Pagination, and Errors

## Choose one application credential

TMDb v3 accepts either `api_key` as a query parameter or an API Read Access Token in `Authorization: Bearer <token>`. Both methods provide the same access level across v3; the read token also works across v4. Obtain both from the account API settings page. Send one method, not both, so an accidental stale query key cannot obscure a rejected bearer token.

```bash
curl -H 'accept: application/json' \
  -H "Authorization: Bearer $TMDB_ACCESS_TOKEN" \
  'https://api.themoviedb.org/3/movie/550'
# Alternative: .../movie/550?api_key=$TMDB_API_KEY
```

A bad credential commonly returns HTTP 401 with `status_code: 7` and `Invalid API key: You must be granted a valid key.` Permission failures use code 3 and `Authentication failed: You do not have permissions to access the service.` Do not confuse code 33, which is an invalid request token. The CLI reports the 401 response rather than retrying with a second credential.

## Pages and rate limits

Search and discover responses contain `page`, `results`, `total_pages`, and `total_results`; pages contain up to 20 results. Page numbers start at 1 and max out at 500. Requests beyond that limit return a validation error, rather than being silently clamped. Search/discover access is effectively capped at 10,000 items even when totals advertise more. Trending has a larger documented sample ceiling.

TMDb's current guidance describes a soft limit around 40 requests per second, subject to change. On HTTP 429, respect `Retry-After`; the service may also expose `X-RateLimit-Limit`, `X-RateLimit-Remaining`, and `X-RateLimit-Reset`. Exponential backoff is safer than tight retry loops.

## Parameters and images

Use `language=en-US` (an ISO 639-1 language plus ISO 3166-1 region) for deterministic localized fields. `region=US` selects or filters release dates for that market. Image URLs combine the secure base URL from `/3/configuration`, a valid size, and the returned path: `https://image.tmdb.org/t/p/w500/<POSTER_PATH>`. Common poster sizes include `w92`, `w185`, `w342`, `w500`, `w780`, and `original`; backdrop sizes differ.

## Sources

- https://developer.themoviedb.org/docs/authentication-application
- https://developer.themoviedb.org/reference/authentication
- https://www.themoviedb.org/documentation/api/status-codes
- https://developer.themoviedb.org/docs/rate-limiting
- https://developer.themoviedb.org/reference/search-movie
- https://developer.themoviedb.org/docs/languages
- https://developer.themoviedb.org/docs/region-support
- https://developer.themoviedb.org/docs/image-basics
- https://developer.themoviedb.org/reference/configuration-details
