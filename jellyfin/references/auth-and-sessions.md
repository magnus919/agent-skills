# Jellyfin authentication and sessions

How tokens are minted, how they travel, and what each failure looks like on the wire.
Every behavioral claim here traces to the canonical OpenAPI spec served from api.jellyfin.org,
the Jellyfin server source code, or a document authored by a Jellyfin core developer (Sources footer).

## The two token postures

Jellyfin has two credential families plus anonymous access:

| Posture | Obtained via | Lifetime | Identity | Typical use |
| --- | --- | --- | --- | --- |
| User access token | `POST /Users/AuthenticateByName` (or Quick Connect) | Session-based, valid until logout or revocation | Bound to one user (and one device id) | Acting as a person; playstate, per-user views |
| API key | Dashboard → API Keys (admin panel) | Persistent until revoked | No user identity; administrator-level privileges | Server automation, read-only browsing CLIs |

Anonymous access (no header at all) works only for endpoints that opt in, notably
`GET /System/Info/Public`, `GET /Users/Public`, and `POST /QuickConnect/Initiate`.
`GET /System/Info/Public` is the recommended pre-auth probe: it returns `ServerName` and
`Version` without credentials, which is how a client learns the server version before
adapting its behavior.

An API key is not a lesser credential: it bypasses user identity entirely and gets
administrator role. It also means every user-scoped concept (per-user views, playstate,
"my" recent items) has no one to attach to unless you pass an explicit `userId` parameter.

## The MediaBrowser authorization scheme (required BEFORE any token exists)

Jellyfin's `Authorization` header uses a custom scheme named `MediaBrowser` with
comma-separated, order-insensitive `Key="value"` parameters:

```
Authorization: MediaBrowser Client="my-cli", Device="terminal", DeviceId="unique-device-id", Version="1.0.0"
```

Parameter keys (case-sensitive, alphanumeric, unknown keys ignored by the server):

| Key | Meaning |
| --- | --- |
| `Client` | Name of the client application |
| `Device` | Human-readable device name |
| `DeviceId` | Client-generated unique device identifier |
| `Version` | Client application version |
| `Token` | Access token or API key — present only AFTER you have one |

Values must be wrapped in double quotes and should be URL-encoded; the official TypeScript
SDK wraps every value in `encodeURIComponent`. The server URL-decodes values after parsing.

**The login chicken-and-egg.** `POST /Users/AuthenticateByName` must be sent with a
COMPLETE `Client`/`Device`/`DeviceId`/`Version` header — before any token exists. The server
uses those four strings as the new session's identity: the controller builds an
`AuthenticationRequest` from the parsed header values, and `SessionManager` hard-fails with
`ArgumentException.ThrowIfNullOrEmpty` on any missing `App`, `DeviceId`, `DeviceName`, or
`AppVersion`. The exception middleware maps `ArgumentException` to HTTP 400, so the classic
CLI failure mode — sending no header, or only `Content-Type` — looks like this on the wire:

```
HTTP/1.1 400 Bad Request
Content-Type: text/plain

Error processing request.
```

(Non-development servers replace the real exception text with the literal string
`Error processing request.`.) A bare-token `Authorization: <key>` without the MediaBrowser
scheme fails the same class of parse and was observed as 401 in issue #12990; the
correctly-wrapped header succeeded. DeviceId hygiene: the server permits a single access
token per `DeviceId`, and re-logging-in the same `(DeviceId, user)` pair silently revokes
that pair's previous token — mix a per-profile discriminator (e.g. hashed username) into the
DeviceId when one machine drives several accounts.

## Exact login flow

Request (note: full MediaBrowser header, NO Token segment yet):

```
curl -X POST "http://localhost:8096/Users/AuthenticateByName" \
  -H "Content-Type: application/json" \
  -H 'Authorization: MediaBrowser Client="my-cli", Device="terminal", DeviceId="dev-1", Version="1.0.0"' \
  -d '{"Username": "alice", "Pw": "secret"}'
```

Body schema `AuthenticateUserByName`: `Username` (string) and `Pw` (PLAIN TEXT password).
There is an older `Password` sha1-hash slot in some legacy documentation — do not use it;
send plaintext in `Pw`.

Response 200 (`AuthenticationResult`; properties shown PascalCase, the server default):

```json
{
  "User":         { "Name": "alice", "Id": "6eec632a-ff0d-4d09-aad0-bf9e90b14bc6", "HasPassword": true },
  "SessionInfo":  { "Id": "a1b2c3d4e5f6", "UserId": "6eec632a-ff0d-4d09-aad0-bf9e90b14bc6",
                    "UserName": "alice", "Client": "my-cli", "DeviceId": "dev-1",
                    "DeviceName": "terminal", "ApplicationVersion": "1.0.0" },
  "AccessToken":  "<ACCESS_TOKEN>",
  "ServerId":     "abc123def456"
}
```

Capture `User.Id` (this is the user id every user-scoped endpoint wants) and `AccessToken`.
The spec marks the operation's only documented non-200 as 503 (server starting); credential
failures arrive via exception mapping instead: wrong username/password → 401
("Invalid username or password entered." in server logs), disabled user or device/session
policy rejection → 403, missing/partial MediaBrowser header → 400 as above.

After login, `GET /Users/Me` with the token is the cleanest identity re-check; it returns
the authenticated user's `UserDto`. With an API key instead of a user token, `/Users/Me`
answers 400 with the JSON body `Token is not owned by a user.` — API keys are userless.

## Sending the token afterwards

| Channel | Form | Status |
| --- | --- | --- |
| `Authorization` header, full scheme | `Authorization: MediaBrowser Client="c", Device="d", DeviceId="i", Version="v", Token="<token>"` | Recommended |
| `Authorization` header, token-only | `Authorization: MediaBrowser Token="<api-key>"` | Valid (API-key example in official docs) |
| Query parameter | `?ApiKey=<token>` | Discouraged (leak risk in logs); never combine with the header |
| `X-Emby-Token` header | `X-Emby-Token: <token>` | Deprecated (legacy) |
| `X-MediaBrowser-Token` header | `X-MediaBrowser-Token: <token>` | Deprecated (legacy) |
| `X-Emby-Authorization` header | full MediaBrowser scheme on a legacy header name | Deprecated (legacy) |

The bundled `scripts/jellyfin` sends the modern form:
`Authorization: MediaBrowser Client="...", Device="...", DeviceId="...", Version="...", Token="<token-or-api-key>"`.
It is wire-equivalent to the legacy `X-Emby-Token` header on every server that supports
legacy auth, and it keeps working when legacy channels are switched off.

Never send two different tokens in one request — server precedence across channels is
unspecified at the contract level and the value used becomes uncertain. The bundled CLI
takes this literally: after login it puts the token in exactly ONE channel per request
(the `Token=` parameter of the modern header) and never attaches `X-Emby-Token` alongside
it; the offline suite pins that single-channel contract with a request-capture test.

### Legacy kill-switch and deprecation timeline

- All legacy channels above are gated by server config `EnableLegacyAuthorization`
  (`system.xml`), default **true** through 10.11.x. Setting it to `false` (introduced in
  10.11) makes `X-Emby-Token`, `X-MediaBrowser-Token`, `api_key`, and
  `X-Emby-Authorization` stop resolving — a client that "worked yesterday" and now gets
  uniform 401s has almost certainly met this toggle.
- Maintainers have targeted disabling the deprecated options starting with the 12.0
  release. Speak the modern `Authorization` header natively; if you must support a server
  with legacy auth locked off, substitute the legacy header for the modern one on that
  server's requests — never send both on the same request.

## Error signatures worth mocking

| Scenario | Status | Body |
| --- | --- | --- |
| AuthenticateByName without (full) MediaBrowser header | 400 | text/plain `Error processing request.` |
| AuthenticateByName with wrong credentials | 401 | text/plain `Error processing request.` |
| Disabled user / device or session policy reject | 403 | text/plain |
| Token matches nothing (garbage token on a secured read) | 403 | `Invalid token.` (SecurityException mapping; some doc renders simplify this to 401 — trust the middleware mapping) |
| Secured read with no token at all | 401 | challenge |
| API key on `GET /Users/Me` | 400 | JSON ProblemDetails containing `Token is not owned by a user.` |
| Server starting / restarting | 503 | HTML/text body with `Retry-After: <seconds>` and `Message: <reason>` headers |

The 503 can appear on ANY endpoint during startup; retry loops should honor `Retry-After`.

## Quick Connect (passwordless alternative)

For shared or headless setups where you do not want to handle a password:

1. `POST /QuickConnect/Initiate` (no auth) → 200 `QuickConnectResult` with `Secret`,
   `Code`, `Authenticated:false`. A 401 here means Quick Connect is disabled on that server.
2. Poll the quick-connect state endpoint (about every 5 seconds) until
   `Authenticated` flips to `true`, while the user approves the `Code` in their client.
3. `POST /Users/AuthenticateWithQuickConnect` with body `{"Secret": "<secret>"}` →
   200 `AuthenticationResult` — same capture and follow-up as the password flow.

## Sources

- https://api.jellyfin.org/ — official Jellyfin API reference (ReDoc), version 12.0.0 stable
- https://api.jellyfin.org/openapi/jellyfin-openapi-stable.json — canonical OpenAPI spec (AuthenticateByName schema, 503 blocks, /Users/Me 400)
- https://gist.github.com/nielsvanvelzen/ea047d9028f676185832e51ffaf12a6f — "Jellyfin API Authorization" by a Jellyfin core developer (MediaBrowser scheme, legacy table, kill-switch steps, removal-to-12.0 quote)
- https://mintlify.wiki/jellyfin/jellyfin/api/authentication/overview — official server docs, authentication overview (login curl examples, API key vs user token table, logout)
- https://jmshrv.com/posts/jellyfin-api/ — community API overview by the Jellyfin for Jellyfin/Roku author
- https://typescript-sdk.jellyfin.org/ — official TypeScript SDK (getAuthorizationHeader construction, login-then-update flow)
- https://kotlin-sdk.jellyfin.org/guide/authentication.html — official Kotlin SDK authentication guide (401-on-bad-credentials, Quick Connect cadence)
- https://github.com/jellyfin/jellyfin/issues/12990 — wire-level reproduction of missing/bare-token header failures
- https://github.com/jellyfin/jellyfin — server source: `AuthorizationContext.cs`, `SessionManager.cs`, `UserController.cs`, `ExceptionMiddleware.cs`, `AuthService.cs`, `CustomAuthenticationHandler.cs`, `ServerConfiguration.cs`
- https://github.com/jellyfin/jellyfin-apiclient-python — reference client implementation
