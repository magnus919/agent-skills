# PeerTube gotchas field guide

Failure signatures and behavioral traps, distilled from the official docs, the server
source, and live probes. Each entry: symptom → cause → what to do.

## Instance plurality (the big one)

- **Symptom**: same CLI command works on one instance and 400s/401s/empty-results on
  another; or a token that worked on instance A 401s on instance B.
- **Cause**: PeerTube is federated software, not a single API. Every instance is an
  independent deployment with its own rules, allowances, moderation policy, enabled
  features (NSFW policy, search-index support, registration, transcoding) and its own user
  accounts and OAuth tokens. A token minted by instance A is meaningless to instance B;
  instance B may have closed registrations, disabled uploads, or set its own NSFW default.
- **Do**: always configure the instance host per operation (`PEERTUBE_SERVER` or
  `--server`); keep per-instance token files; never assume an account or video exists on a
  different instance. Federated content viewed on instance X still **belongs** to the
  origin instance (`channel.host` / `account.host` / video `url` tell you which).

## Search scope confusion

- **Symptom**: "search across the fediverse" expectations return only a handful of local
  results; or results reference videos the instance doesn't host.
- **Cause**: `searchTarget` has two scopes: `local` (instance-known objects only) and
  `search-index` (external fediverse index, admin-enabled). Omitting the parameter gives
  the instance's own scope on current servers (observed), not the fediverse.
- **Do**: pass `searchTarget=local` explicitly for instance scope; use SepiaSearch
  (`https://sepiasearch.org/api/v1/search/videos`) for fediverse-wide scope. Index results
  point at origin instances — follow `channel.host`/`url` rather than expecting the
  queried instance to serve them.

## Pagination: `start`/`count`, never `page`

- **Symptom**: client pages with `page=1&count=15` and gets identical results forever.
- **Cause**: the API has no `page` parameter; unknown params are ignored, so `page=1`
  requests silently return the first `count` rows every time.
- **Do**: advance `start` by the page size until `start >= total` or an empty page. Max
  `count` is 100 (higher values are rejected). `skipCount=true` trades the `total` field
  for speed — then you must stop on the first short page.

## Comment route spelling

- **Symptom**: fetching comments with `/videos/{id}/comments` or
  `/videos/{id}/commentthreads` returns 400 (current servers answer 400, not 404, for bad
  routes — see below) while other endpoints work.
- **Cause**: the route is `GET /videos/{id}/comment-threads` (hyphenated). The v8.3
  `/comments/{commentId}/replies` route is for replies, not top-level threads.
- **Do**: use `/comment-threads` with `start`/`count`/`sort=-createdAt|-totalReplies`.

## Instance metadata endpoint names

- **Symptom**: `/instance/stats`, `/instance/about`, `/instance/config` all 400/404.
- **Cause**: mixed current naming: stats live at **`/server/stats`** (operation *titled*
  "Get instance stats"), about at **`/config/about`**, config at **`/config`**.
- **Do**: compose `/config/about` + `/server/stats` for a full instance picture.

## oauth-clients/local secret masking

- **Symptom**: `GET /oauth-clients/local` returns
  `"client_secret": "********************************"`; the following token request 400s
  with invalid_client.
- **Cause**: current production servers mask the secret in this response (the value is
  still delivered to the web client via served front-end assets; the API response masks
  it). Older instances/versions return the real secret.
- **Do**: detect the masked value; if masked, obtain the client pair from the instance's
  served front-end JS (the same source its own web UI uses) before the token request. Never
  persist the masked string as a secret. The endpoint is also Host-header-guarded (403 if
  the `Host` header disagrees with the configured webserver hostname — mind reverse
  proxies).

## Auth error signatures

| Status | Where | Meaning |
| --- | --- | --- |
| 400 on `POST /users/token` | invalid client pair (including the masked-secret case) or wrong credentials | RFC7807-style `application/problem+json` body; check `detail` |
| 401 on `POST /users/token` | account has 2FA and no `x-peertube-otp` header supplied | supply OTP header |
| 401 on authenticated GETs | token expired/revoked/malformed, or missing | re-run password grant |
| 403 on `oauth-clients/local` | Host-header mismatch (proxy misconfiguration) | fix the proxy/Host |
| 429 anywhere | rate limit (default 50 req/10 s; token endpoint tighter) | read `Retry-After` + `X-RateLimit-*` headers, back off |
| 400 on unknown routes | current servers answer 400 with an error body for unrecognized API routes | read the body; the classic "404 means missing route" assumption misleads here |
| connection errors | wrong/unreachable `PEERTUBE_SERVER` | no HTTP response at all; classify as transport failure |

## Shape and value traps

- **duration is seconds** (integer). Sample list value `1419` = 23:39, not milliseconds.
- **ids are triple**: numeric `id`, `uuid` (UUIDv4), and `shortUUID` — all three are
  accepted by `/videos/{id}` and family; `uuid` is the safest portable choice in scripts.
- **`users/me` sample is an array in the docs**; live servers return a single object.
  Tolerate both when writing generic parsers.
- **`role` is an object** `{id, label}` on `/users/me` — don't stringify the dict.
- **`videoQuota` is bytes** (large integer).
- **`{total, data}` everywhere**: collections never wrap in `{"videos": []}` at the API
  layer (the bundled CLI adds that key in its JSON output; know which layer you're
  reading).
- **`nsfw` filter is a string** (`"true"`/`"false"`) in query params.
- **filter names end in `OneOf`/`AllOf`** (`categoryOneOf`, `tagsAllOf`, ...); bare
  `category=` from old wrappers is ignored silently.
- **federated results**: a video listed on instance X may be hosted on instance Y
  (`account.host`/`channel.host`). Views/likes counters are local-ish and eventually
  consistent across the federation — don't expect exact global numbers.

## Version drift

- Docs reference page currently identifies PeerTube **8.1.0** while the changelog already
  carries 8.3.0 material — instance versions vary; validate optional parameters
  (`stateOneOf` >= 8.2, `autoTagOneOf` >= 6.2) before relying on them.
- Historical renames worth knowing when reading old code: `/videos/channels/*` →
  `/video-channels/*`, `/videos/accounts/{id}/channels` → `/accounts/{id}/video-channels`
  (v1.0.0-beta.4).
- Refresh-token request fields are underspecified in official docs; don't build
  refresh-critical logic without testing against your target instance.

## Sources

- https://docs.joinpeertube.org/api-rest-reference.html (operation pages: searchVideos,
  getVideos, comment-threads, getOAuthToken, revokeOAuthToken, getInstanceStats; Errors,
  Rate-limits sections)
- https://docs.joinpeertube.org/api/rest-getting-started
- https://docs.joinpeertube.org/use/search (scope semantics)
- https://docs.joinpeertube.org/admin/configuration (global-search admin enablement)
- https://docs.joinpeertube.org/CHANGELOG (route renames, version additions)
- https://raw.githubusercontent.com/Chocobozzz/PeerTube/develop/server/core/controllers/api/oauth-clients.ts
  (Host guard)
- Live anonymous probes (secret masking, search default scope, route status codes,
  response shapes), 2026-08-29.
