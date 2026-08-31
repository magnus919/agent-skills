# PeerTube authentication and tokens

How PeerTube's OAuth2 flow actually behaves on the wire, what each failure looks like, and
how to store tokens without leaking them. Every behavioral claim traces to the official
REST reference, the official quick start, or the PeerTube server source (Sources footer).
PeerTube has exactly one authenticated posture: an OAuth2 **bearer access token** minted
from per-instance client credentials. There is no API-key alternative (unlike Jellyfin) and
no header scheme beyond standard `Authorization: Bearer <token>`.

## Step 1 — fetch the instance's OAuth client credentials

`GET /api/v1/oauth-clients/local` (singular `local`, not `locals`) returns the
per-instance client pair. It is anonymous — no authorization block on the operation — and
PeerTube's own web UI calls it before every login:

```json
{ "client_id": "<CLIENT_ID>", "client_secret": "<CLIENT_SECRET>" }
```

**Production servers mask the client_secret.** The current server code returns the real
secret from this endpoint (it is the same secret the web client uses), but production
instances in recent versions respond with the secret replaced by
`"********************************"` — observed live on multiple public instances in
2026 and consistent with the reference page's own masked response example
(`client_secret: "********************************"`). Practical consequences:

- Never persist the response of `oauth-clients/local` as if it were a working secret.
- A login attempt using the masked value fails with HTTP 400 (invalid client). This is
  what you are seeing if your script fetched the client pair and the very next token
  request 400s on a public instance.
- The legacy workaround mirrors what the web client does: the client pair is embedded in
  the instance's front-end JavaScript, and official PeerTube tooling reads it from the
  served assets when the API masks it. Treat the masked behavior as version-dependent —
  always attempt the API first, then fall back to scraping the served JS bundle if the
  secret comes back masked.

The endpoint is also Host-header-guarded: the server compares the request's `Host` header
against its configured webserver hostname and answers **HTTP 403
"Getting client tokens for host ... is forbidden"** when they disagree (proxies that
rewrite the header break clients here; the guard is skipped on test/dev instances).

## Step 2 — the password grant

`POST /api/v1/users/token`, `Content-Type: application/x-www-form-urlencoded`, with form
fields (names exactly as in the reference):

| Field | Required? | Notes |
| --- | --- | --- |
| `client_id` | yes | from step 1 |
| `client_secret` | yes | from step 1 (unmasked) |
| `grant_type` | yes | `password` for login |
| `username` | yes | |
| `password` | yes | |
| `response_type` | no | the official quick-start curl sends `response_type=code`; it is absent from the current OpenAPI request schema. Sending it is harmless; omitting it works with `requests` |
| `x-peertube-otp` | conditional | request header, only when the account has 2FA enabled (server answers 401 without it) |

```bash
curl -X POST "$BASE/users/token" \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  --data-urlencode 'client_id=<CLIENT_ID>' \
  --data-urlencode 'client_secret=<CLIENT_SECRET>' \
  --data-urlencode 'grant_type=password' \
  --data-urlencode 'username=<USERNAME>' \
  --data-urlencode 'password=<PASSWORD>'
```

Success response fields: `access_token`, `token_type` (`"Bearer"`), `expires_in` (seconds),
`refresh_token`, and `refresh_token_expires_in` (seconds; present in the current reference
sample, `1209600` there — a sample value, not a guaranteed default). The quick-start
example shows `expires_in: 14399` (~4 hours). Sample values are not contract: instances can
configure token lifetimes server-side, so read `expires_in` from each response and schedule
refresh from it rather than hard-coding "24 hours" or any other number.

## Refresh, revocation, and lifetime

- **Refresh grant**: `grant_type=refresh_token` is a documented allowed value on the token
  endpoint. The rendered reference does not display a `refresh_token` form-field row, so
  the exact refresh request body is not fully specified in official docs; standard OAuth2
  practice (send `refresh_token` alongside the client pair) is the community-established
  shape, but verify against your instance's version before relying on it.
- **Revocation**: `POST /api/v1/users/revoke-token` with `Authorization: Bearer <token>`,
  no body, returns HTTP 200 and revokes the access token **and** its associated refresh
  token, destroying the session. This is the correct "logout" operation: revoke before
  discarding a stored token.
- **Lifetimes**: no official page documents default lifetime values or the server config
  keys that change them; the only official evidence is the sample `expires_in: 14399` /
  `refresh_token_expires_in: 1209600` (~4 h / ~14 d). Server operators can adjust token
  lifetimes via their production config (all options documented as living in
  `config/default.yaml` overridable by `production.yaml`), so treat expiry as per-instance
  and honor `expires_in`.

## Error signatures on the wire

| Symptom | Status | Meaning / response |
| --- | --- | --- |
| Bad client_id/client_secret, or the masked secret, or wrong username/password | `400` on `POST /users/token` | Reference documents 400 for invalid client or credentials; bodies are RFC7807-style (`application/problem+json` with `type`, `title`, `status`, `detail`, sometimes `code`) |
| 2FA enabled, no `x-peertube-otp` header | `401` on `POST /users/token` | header must be supplied on the token request |
| Expired/revoked token on any authenticated call | `401` | re-run the password grant (or refresh) |
| Wrong `Host` header reaching `oauth-clients/local` | `403` | proxy/header rewriting problem, not auth |
| Rate limit exceeded | `429` | all endpoints are rate-limited; the token endpoint is tighter than most (documented sample: 15 calls per 5 minutes). Inspect `Retry-After` (seconds) and `X-RateLimit-Limit` / `X-RateLimit-Remaining` / `X-RateLimit-Reset` (Unix timestamp) and back off |
| Connection refused / DNS failure | no HTTP response | transport failure — classify separately from API errors; usually `PEERTUBE_SERVER` is wrong or unreachable |

Anonymous-read endpoints (videos, search, channels, `/config`, `/config/about`,
`/server/stats`) need no token at all. Authenticated-only calls include `/users/me`,
`/users/me/videos`, and any state-changing operation. The API answers `401` when a call
needs a token you did not send.

## Token persistence hygiene

PeerTube's docs do not prescribe storage mechanics, so a CLI should follow these
sanctioned-by-logout-support practices:

1. **Store under the user's own profile, not in the repo.** The bundled CLI defaults to
   `~/.config/peertube/token.json` (override with `PEERTUBE_CONFIG_DIR` for tests). Never
   write tokens into a working tree, a shell history, or an eval manifest.
2. **Restrict file permissions.** Create the directory and file so only the owner can read
   the token file (e.g. `os.makedirs(..., mode=0o700)` and `0o600` on the file).
3. **Persist the refresh token alongside the access token and the server base URL**, plus
   the absolute `expires_at` computed from `expires_in`. A token file is only valid for
   the instance it was minted by — re-authenticate when `PEERTUBE_SERVER` changes.
4. **Refresh before expiry; fall back to password re-grant.** Because refresh-request
   semantics are underspecified in official docs, treat refresh as an optimization: try
   `grant_type=refresh_token`, and on any failure re-run the password grant.
5. **Revoke on logout.** `POST /users/revoke-token` invalidates both tokens server-side,
   then delete the local file. Deleting the file alone leaves a live session behind.
6. **Never commit or log tokens.** Examples everywhere in this skill use
   `<ACCESS_TOKEN>`-style placeholders. If a token file ever lands in a diff, revoke it —
   deleting the file does not invalidate the session.
7. **Multi-instance note**: one token file per server URL (or include the server in the
   file) avoids "works on instance A, 401 on instance B" confusion when switching
   `PEERTUBE_SERVER`.

## Detection and headers for API clients

- API responses carry `x-powered-by: PeerTube` and `/api/*` is CORS-enabled; HTML pages
  include `<meta property="og:platform" content="PeerTube">`; NodeInfo is exposed at
  `/nodeinfo/2.0.json`. Any of these distinguishes a PeerTube instance from other servers.
- No special `User-Agent` is required. Use `Accept: application/json`.

## Sources

- https://docs.joinpeertube.org/api-rest-reference.html (Session: getOAuthClient,
  getOAuthToken, revokeOAuthToken; Errors; Rate-limits; CORS; Config; Stats)
- https://docs.joinpeertube.org/api/rest-getting-started (client fetch, password grant
  curl, token response example, instance detection)
- https://docs.joinpeertube.org/maintain/configuration (config file layering)
- https://github.com/Chocobozzz/PeerTube/blob/develop/support/doc/api/openapi.yaml
  (generated OpenAPI spec; openapi-generator clients)
- https://raw.githubusercontent.com/Chocobozzz/PeerTube/develop/server/core/controllers/api/oauth-clients.ts
  (Host-header guard; response construction)
- Live anonymous probes of public instances (`oauth-clients/local` masking, 400 on token
  misuse), 2026-08-29.
