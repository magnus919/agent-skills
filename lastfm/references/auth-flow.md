# Last.fm API Authentication Flow

Write operations (scrobble, love, now-playing, add/remove tags) require a **session key** obtained through a three-step web auth flow. Read operations (getInfo, getSimilar, search, chart, geo, tag) need only an API key.

## Prerequisites

```
LASTFM_API_KEY       # Required for ALL requests (read + write)
LASTFM_API_SECRET    # Required only for signed (write) requests
```

Get both from https://www.last.fm/api/account/create — they come together when you register an API application.

## Step 1: Get a Token

```bash
lastfm-cli auth get-token
```

Returns a short-lived token (like a one-time use code). The token is valid for only a few minutes.

## Step 2: User Authorizes the Token

The user must visit this URL in a browser:

```
https://www.last.fm/api/auth/?api_key=***&token=***
```

This page asks the user to authorize your application to scrobble/love on their behalf. They click "Allow" and the token becomes authorized.

**Important:** This step MUST be done by a human in a browser. There's no programmatic way to authorize — the whole point is that the user grants permission explicitly.

## Step 3: Exchange Token for Session Key

```bash
lastfm-cli auth get-session <token>
```

Returns:
- `session.key` — the session key (store this, it doesn't expire)
- `session.name` — the Last.fm username that authorized

## Step 4: Store and Use

```bash
export LASTFM_SESSION_KEY="<the session key>"
```

Once set, write operations work:

```bash
lastfm-cli track love "Radiohead" "Karma Police"
lastfm-cli track scrobble "Massive Attack" "Teardrop" --album "Mezzanine"
lastfm-cli track now-playing "Portishead" "Glory Box"
```

## Important Notes

- **The session key does not expire.** Set it once, use it forever (or until the user revokes your API app's access from their Last.fm account settings).
- **Each user needs their own session key.** If you're building something for multiple users, each one goes through steps 1-3 separately.
- **The API secret is NOT the session key.** The secret comes from your API app registration page. The session key comes from the auth flow. They are different values.
- **Signing:** Write requests are "signed" — the CLI sorts all parameters alphabetically, concatenates them with the API secret, MD5-hashes them, and sends the hash as `api_sig`. The CLI handles this automatically when you provide `LASTFM_API_SECRET` and `LASTFM_SESSION_KEY`.
- **The token is single-use.** If the auth page errors or times out, get a new token and try again.