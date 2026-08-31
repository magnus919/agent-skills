# Jellyfin user scoping — the userId matrix

The single most common Jellyfin integration failure after authentication: a request that
authenticates fine but 404s or 400s because **which user** the query is about was never
stated. Jellyfin's data model is per-user at the library level; most read endpoints need
you to say whose library you are looking at.

## Why user id is everywhere

A Jellyfin library is not one global catalog. Views, playstate, favorites, resume points,
and parental-control visibility all attach to a user. The authentication layer may or may
not imply a user:

- **User access token** (from `AuthenticateByName`): implies one user. Recent servers fall
  back to that user when `userId` is omitted on some endpoints.
- **API key** (from Dashboard → API Keys): implies NO user. `AuthorizationInfo.User` stays
  null and the request gets administrator role. Every user-scoped concept must be named
  explicitly with a `userId` parameter — including `/UserViews`, which is meaningless
  without one.

The bundled CLI always sends `userId` explicitly on user-scoped commands regardless of
which credential type it holds. That is the cross-version-safe baseline.

## The userId requirement matrix

| Endpoint | User token, userId omitted | API key |
| --- | --- | --- |
| `GET /Items` | **400** — body `userId is required` (servers enforce `if (!isApiKey && user is null) return BadRequest("userId is required")`) | Optional — omitted means an unrestricted, userless view; pass it anyway for `UserData` in DTOs |
| `GET /Items/{itemId}` | Defaults to the token's user; `userId` supplies whose `UserData` embeds | Pass explicitly for user data |
| `GET /UserViews` | Parameter accepted; pass it | REQUIRED to be meaningful |
| `GET /Shows/{seriesId}/Seasons` / `Episodes` | ≥10.9 falls back to token user; ≤10.8 crashes on omission — always pass | REQUIRED |
| `GET /Shows/NextUp` | Same version split as above — always pass | REQUIRED |
| `GET /Items/Latest` | `userId` scopes "recently added for whom"; always pass | REQUIRED for meaningful results |
| `GET /Search/Hints` | Optional — "omit to search all" | Optional |
| `GET /Users/Me` | Works (returns token's user) | **400** `Token is not owned by a user.` |
| `GET /System/Info`, `/System/Info/Public`, `/Users` | No user concept | Fine |

Note the deliberate trap in `/Users/Me`: it is the natural "who am I" endpoint for a user
token and returns exactly the id you need — but with an API key it is a 400, by design,
because an API key is nobody.

## 400 vs 404: absent vs invalid userId on /Items

Two distinct failure signatures, enforced in this order by the items controller
(verified at master and v10.10.7):

1. The user lookup runs first: a supplied-but-nonexistent `userId` throws
   `ResourceNotFoundException` → mapped to **404** (`Error processing request.` body).
2. Then the guard: an ABSENT `userId` on non-API-key auth returns **400** with the literal
   string body `userId is required` (not the middleware's generic text).

So: `400 userId is required` = you forgot the parameter; `404` = the parameter names a user
that does not exist. Mock both distinctly.

## Finding a user id without logging in as one

1. **`GET /Users`** (any valid token): array of `UserDto` with `Name` and `Id`. The
   administrator-flavored listing — API keys see everyone.
2. **`GET /Users/Public`** (no auth): only users flagged visible on login screens.
3. **After `AuthenticateByName`**: the response's `User.Id` is the documented primary.
4. **With a user token**: `GET /Users/Me`.

```bash
# Discover user ids with an API key
curl -s -H 'Authorization: MediaBrowser Token="YOUR_API_KEY"' \
  "http://localhost:8096/Users" | jq -r '.[] | [.Name, .Id] | @tsv'
# → alice    6eec632a-ff0d-4d09-aad0-bf9e90b14bc6
```

## Scoping errors look like 404s

The confusion this reference exists for: `GET /Items` (or `/Shows/NextUp`) called without a
`userId` under a context where one is required does not answer "you forgot the user" on
every endpoint and version — older servers crash (NextUp ≤10.8: 500 from an empty-Guid
`ArgumentException`), and user-token fallbacks silently change results. Symptoms cluster as
"endpoint exists but returns 400/404/empty" even though the token is perfectly valid. The
fix is uniform: resolve the user id once, pass it explicitly on every user-scoped call.

The bundled CLI mirrors that baseline: `recent`, `next-up`, and `item` require
`JELLYFIN_USER_ID` or `--user-id` before any network call, refuse to guess an
administrator, and dry-run previews show the `userId` that would have been sent.

## Sources

- https://api.jellyfin.org/ — official Jellyfin API reference (ReDoc), version 12.0.0 stable
- https://api.jellyfin.org/openapi/jellyfin-openapi-stable.json — canonical OpenAPI spec (`/Users/Me` 400 "Token is not owned by a user.", `userId` parameter descriptions across /Items, /Items/Latest, /Shows/*, /Search/Hints)
- https://github.com/jellyfin/jellyfin — server source: `ItemsController.cs` (userId-required guard and 400/404 ordering), `RequestHelpers.cs` (GetUserId token fallback), `TvShowsController.cs` (NextUp userId version history), `AuthorizationContext.cs` (API key ⇒ User null + admin role)
- https://mintlify.wiki/jellyfin/jellyfin/api/authentication/overview — official server docs (API key vs user token semantics)
- https://gist.github.com/nielsvanvelzen/ea047d9028f676185832e51ffaf12a6f — core-developer authorization guide (API-key identity behavior)
