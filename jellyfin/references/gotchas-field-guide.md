# Jellyfin gotchas field guide

Version-sensitive, wire-level failure signatures observed in server source, the OpenAPI
spec, and tracked issues. Diagnostic order: auth posture → user scoping → response shape →
version drift.

## Response-shape asymmetry (the biggest interop trap)

Three families, three shapes — a generic client must branch:

| Endpoint | 200 shape |
| --- | --- |
| `GET /Items`, `/Shows/*`, `/Search/Hints`, `/UserViews` | Wrapper object: `{ Items: [...], TotalRecordCount, StartIndex }` (search: `SearchHints` key) |
| `GET /Items/Latest` | **Bare ARRAY** of `BaseItemDto` — no `Items` key, no `TotalRecordCount`, no `StartIndex` |
| `GET /Items/{itemId}`, `AuthenticateByName` | Single object |

`/Items/Latest` defaults: `limit` 20, `groupItems` true (episodes merge into series rows —
so it answers "what's new", not "how many").

## Property-casing minefield

Every JSON-producing operation documents three profiles: `application/json`,
`application/json; profile="CamelCase"`, `application/json; profile="PascalCase"`.
Observed defaults vary between server eras and clients; SDKs read PascalCase off raw
payloads while sample captures show camelCase. Normalize defensively: read both `Name`
and `name`, both `AccessToken` and `accessToken`, rather than trusting one casing. Query
PARAMETERS are always camelCase (`sortBy`, `startIndex`) regardless of profile.

## Error signatures on the wire

| Symptom | Actual cause |
| --- | --- |
| 400 text/plain `Error processing request.` on login | Missing/partial `Authorization: MediaBrowser Client=..., Device=..., DeviceId=..., Version=...` header — required BEFORE any token exists (ArgumentException mapping) |
| 401 on login | Wrong username/password ("Invalid username or password entered." in server logs) |
| 403 on login | Disabled user, device-access policy, or `MaxActiveSessions` cap |
| 401 + log `AuthenticationScheme: "CustomAuthentication" was challenged.` | Secured read with no/insufficient token |
| 403 with valid-format token | Token matches nothing (`Invalid token.` via SecurityException) or permission denied — note this is 403, not 401; some doc renders simplify it to 401 |
| 400 `Token is not owned by a user.` (JSON) | API key on `/Users/Me` — API keys are userless |
| 400 `userId is required` (plain string body) | `GET /Items` without `userId` on non-API-key auth |
| 404 on a user-scoped query | Supplied `userId` does not exist (user lookup precedes the missing-param guard) |
| 503 + `Retry-After` + `Message` headers | Server starting/restarting — can hit ANY endpoint; honor `Retry-After` |
| "Worked yesterday", now uniform 401s | Admin set `EnableLegacyAuthorization=false` (possible since 10.11): all `X-Emby-*`/`api_key` channels stopped resolving |

No rate limiting exists in the spec — Jellyfin is self-hosted. A 429 comes from a reverse
proxy, not Jellyfin.

## Auth-channel pitfalls

- `X-Emby-Token`, `X-MediaBrowser-Token`, `api_key` query param, and the
  `X-Emby-Authorization` header are deprecated legacy channels; maintainers target
  disabling them from 12.0. Prefer `Authorization: MediaBrowser ... Token="..."`.
- One access token per `(DeviceId, user)` pair: re-logging-in the same pair revokes the
  pair's previous token. Multi-profile CLIs must vary the DeviceId per profile or they will
  keep logging each other out.
- Never send two token channels in one request; which one wins is not contractual. The
  bundled CLI honors this literally: the token rides only the MediaBrowser `Token=`
  parameter and the legacy `X-Emby-Token` header is never attached (request-capture-tested
  in the offline suite).

## User-scoping pitfalls

- API key = administrator + no user. Everything per-user (views, latest, next-up, played
  state) needs an explicit `userId` parameter, and `UserData` fields stay empty otherwise.
- Recent servers fall back to the token's user when `userId` is omitted on some endpoints —
  which makes omissions work on your server and fail on someone else's API-key deployment.
  Always send it.

## TV navigation quirks

- **NextUp `userId` version split:** ≤10.8 crashes with `ArgumentException: Guid can't be
  empty` when omitted; ≥10.9 falls back to the session user. Pass `userId` unconditionally.
- **NextUp `limit` limits returned items, not series scanned.** The 2024 attempt to make
  `limit` prune the scan made items vanish from NextUp days later and was reverted — keep
  page sizes modest, expect long-tail behavior differences between 10.9.x and 10.10.x.
- `enableRewatching` defaults false: a fully-watched series never reappears in NextUp.
- Prefer `seasonId` (GUID) over numeric `season` on `/Shows/{seriesId}/Episodes` — season
  numbers shift when specials get inserted. Season `IndexNumber` 0 is the specials
  convention.
- `sortBy` on `/Shows/{seriesId}/Episodes` is SCALAR, unlike the comma-delimited array form
  `/Items` accepts.

## Field-selection and caching

- `BaseItemDto` declares ~155 properties but only requested `fields` populate extras;
  `Overview`, `Path`, `MediaSources`, `ProviderIds`, `ChildCount` are null unless asked for.
  `fields=DateCreated` is what makes "recently added" sorting meaningful client-side.
- `ImageTags` values are cache keys for image routes; passing `tag=` yields long-lived
  cacheable URLs. `Etag` changes on metadata edits — treat both as opaque.
- Image routes document **404 as the normal "no such image" response** — fall back to the
  next image type (Primary → Thumb → Parent* tags) instead of erroring.

## Version-drift ledger (what to gate on /System/Info/Public)

| Behavior | 10.7–10.8 | 10.9–10.10 | 10.11 / 12 |
| --- | --- | --- | --- |
| Legacy auth channels | on | on, default true | toggle exists (`EnableLegacyAuthorization`); removal targeted at 12.0 |
| NextUp userId omission | crash (500) | token-user fallback | same |
| `/Items` userId 400 vs 404 ordering | unverified | confirmed | confirmed |
| NextUp extras | `disableFirstEpisode`, `nextUpDateCutoff`, `enableRewatching` | adds `enableResumable` (default true) | same |
| `api.jellyfin.org` spec label | — | — | publishes "12.0.0" branding |

Pre-flight `GET /System/Info/Public` (no auth) gives the `Version` to branch on.

## Mock-test wire shapes (exact)

Success paths:
1. `POST /Users/AuthenticateByName` with complete MediaBrowser header + `{"Username","Pw"}`
   → 200 `AuthenticationResult` (`User.Id` hyphenated lowercase UUID; `AccessToken` string).
2. `GET /Items?userId=...&parentId=...&recursive=true&includeItemTypes=Movie&sortBy=SortName&sortOrder=Ascending&startIndex=0&limit=50`
   → 200 `{Items: [...], TotalRecordCount: N, StartIndex: 0}`.
3. `GET /Search/Hints?searchTerm=break&limit=20`
   → `{SearchHints: [{Id, ItemId (deprecated twin), Name, Type, MatchedTerm, ...}], TotalRecordCount}`.
4. `GET /Items/Latest?userId=...&limit=20&includeItemTypes=Movie,Series`
   → 200 bare `[{...BaseItemDto}]`.

Failure paths (assert status AND content-type):
5. Login without header → 400 text/plain `Error processing request.`
6. Login wrong password → 401 text/plain.
7. Reads: no token → 401 challenge; garbage token → 403.
8. API key on `/Users/Me` → 400 JSON containing `Token is not owned by a user.`
9. `/Items` absent userId (non-API-key) → 400 body literally `userId is required`.
10. `/Items` nonexistent userId → 404 `Error processing request.`
11. Any endpoint during startup → 503 with `Retry-After` and `Message` headers.

## Sources

- https://api.jellyfin.org/openapi/jellyfin-openapi-stable.json — canonical OpenAPI spec (response profiles, 503 blocks, defaults, schemas)
- https://github.com/jellyfin/jellyfin — server source: `ExceptionMiddleware.cs` (status mapping, body suppression), `SessionManager.cs` (session caps, token rotation), `AuthorizationContext.cs` (legacy gates), `ServerConfiguration.cs` (legacy flag), `ItemsController.cs` (400/404 ordering)
- https://github.com/jellyfin/jellyfin/issues/12990 — wire-level header-failure reproduction and challenge log line
- https://api.github.com/repos/jellyfin/jellyfin/pulls/9321 — NextUp userId omission crash evidence (also pulls/11956, pulls/12414, issue #12367 for the limit saga)
- https://gist.github.com/nielsvanvelzen/ea047d9028f676185832e51ffaf12a6f — core-developer authorization guide (legacy table, disable steps, removal timeline)
- https://kotlin-sdk.jellyfin.org/guide/authentication.html — 401-on-bad-credentials, Quick Connect cadence
- https://mintlify.wiki/jellyfin/jellyfin/api/authentication/overview — official docs error table (contrast case)
