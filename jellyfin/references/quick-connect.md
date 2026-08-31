# Jellyfin quick connect

Quick Connect is Jellyfin's passwordless login: the server displays a short code, the user
approves it on a device where they are already signed in, and your client polls until the
approval lands. Use it for headless or shared setups where you do not want to handle a
password — or when the user account has no password at all (send an empty-string `Pw` for
those in the final exchange).

## When Quick Connect is the right flow

- The CLI runs where you cannot (or should not) type a password: CI, SSH sessions, cron.
- You do not want the script to ever see the user's password.
- The server has Quick Connect enabled — otherwise `POST /QuickConnect/Initiate` answers
  **401** with "Quick connect is not active on this server" (that 401 is the disable
  signal, not an auth failure).

## The flow

```
1. POST /QuickConnect/Initiate                 # no authentication required
   → 200 { "Secret": "<secret>", "Code": "123456", "Authenticated": false }
   → 401 = feature disabled on this server

2. Show the Code to the user; on another signed-in client they approve it
   (Dashboard or the client prompt).

3. Poll every ~5 seconds:
   GET /QuickConnect/Connect?secret={Secret}   # quick-connect state
   → QuickConnectResult with Authenticated flipping to true when approved

4. POST /Users/AuthenticateWithQuickConnect    # body: {"Secret": "<secret>"}
   → 200 AuthenticationResult                  # SAME capture as password login
```

`AuthenticationResult` is identical to the password flow's: capture `User.Id` as
`USER_ID` and `AccessToken` as `TOKEN`, then send the standard
`Authorization: MediaBrowser ... Token="..."` header on every subsequent call. The same
session rules apply — one token per `(DeviceId, user)` pair, re-login revokes the pair's
previous token — so still send a complete `Client`/`Device`/`DeviceId`/`Version` header
with the `AuthenticateWithQuickConnect` call.

Error paths: `400 "Missing token"` on step 4 when `Secret` is absent; the 401-on-initiate
disable case above; polling forever if the user never approves — bound your loop.

## Which login flow should my client use?

| Situation | Flow |
| --- | --- |
| Scripting with a persistent admin credential | API key from Dashboard → API Keys (`Authorization: MediaBrowser Token="<key>"`) |
| Interactive one-user session | `POST /Users/AuthenticateByName` with the full pre-token MediaBrowser header |
| Headless / passwordless / shared device | Quick Connect (this reference) |
| Server with legacy auth disabled and a very old client | Nothing helps — upgrade the client to speak the modern header |

## Sources

- https://api.jellyfin.org/openapi/jellyfin-openapi-stable.json — canonical OpenAPI spec (QuickConnect operations: Enabled, Initiate, Connect state, AuthenticateWithQuickConnect; AuthenticationResult schema)
- https://kotlin-sdk.jellyfin.org/guide/authentication.html — official Kotlin SDK authentication guide (Quick Connect cadence ~5s poll, disabled-server 401, empty-password note)
- https://mintlify.wiki/jellyfin/jellyfin/api/authentication/overview — official server docs (token usage after login, session lifetime)
- https://jellyfin.org/docs/general/server/quick-connect — Quick Connect feature overview
- https://gist.github.com/nielsvanvelzen/ea047d9028f676185832e51ffaf12a6f — core-developer authorization guide (device identity and token pairing rules)
