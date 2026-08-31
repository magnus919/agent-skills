# Trakt authentication and request contract

## Public discovery

Trakt v2 identifies an application with its Client ID in the `trakt-api-key` header. Every request must also send the companion header `trakt-api-version: 2`; sending only one of the pair can produce an invalid request or authentication-style failure. Use `Content-Type: application/json` and an identifying `User-Agent` as well.

```sh
curl --fail-with-body 'https://api.trakt.tv/movies/trending?page=1&limit=20' \
  -H 'Content-Type: application/json' \
  -H 'User-Agent: MyAppName/1.0.0' \
  -H "trakt-api-key: ${TRAKT_CLIENT_ID}" \
  -H 'trakt-api-version: 2'
```

The bundled CLI uses this application-key mode. It does not put the Client ID in `Authorization: Bearer`; that header is reserved for an OAuth access token.

## OAuth boundary

Public trending, popular, and anticipated reads do not require a user login. OAuth is needed by endpoints marked as required and is appropriate for user-scoped list, history, collection, watchlist, or mutation operations. A bearer token does not replace the application key and version header when calling the API.

Trakt supports authorization-code and device-code flows. Access tokens last seven days. Refresh tokens are single-use: persist the replacement returned by a successful refresh and discard the old token. A 400/401 response containing `invalid_grant` means the session is no longer usable and requires reauthorization. Never log client secrets, access tokens, or refresh tokens.

## Failure handling

Treat 401 and 403 as credential or app-approval errors, 400/422 as request validation errors, and 429 as rate limiting. On 429, honor `Retry-After` and inspect `X-Ratelimit`; do not retry forever. Transient 502/503/504 responses can be retried with a bounded backoff. The CLI surfaces status and response details without attempting unsafe retries.

## Sources

- https://docs.trakt.tv/docs/required-headers
- https://docs.trakt.tv/docs/getting-started
- https://docs.trakt.tv/docs/authentication-oauth
- https://trakt.docs.apiary.io/api-description-document
