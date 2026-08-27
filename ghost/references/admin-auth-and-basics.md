# Ghost Admin API Authentication and Basics

The Admin API is Ghost's management plane at `https://{admin_domain}/ghost/api/admin/`. It handles full CRUD on posts, pages, tags, and more, including drafts and scheduled content. Every request below assumes you have an Admin API key from **Ghost Admin → Settings → Integrations → Custom Integration**.

## The Admin API key

An Admin API key is a single string of two colon-separated halves:

```
{id}:{secret}
```

- `{id}` — a 24-character hexadecimal identifier (a Ghost ObjectID).
- `{secret}` — a 64-character hexadecimal string encoding 32 random bytes.

Parse the key by splitting on the first `:`. Never assume total length; both halves are hex, but treat them as opaque strings until the moment you use them. Regenerating the key in Ghost Admin immediately invalidates every script holding the old one. Treat the whole key as a server-side secret: it signs tokens that can create, edit, and delete content. Use placeholders like `<RECORD_KEY>` in examples and CI; never paste real keys into code review tools.

## JWT token contract, end to end

Ghost does not accept the Admin API key directly. You exchange it for a short-lived JSON Web Token per request:

1. Split the key on `:` into `id` and `secret`.
2. **Hex-decode the secret** into its 32 raw bytes. Signing with the literal hex characters produces an invalid signature; this is the single most common integration bug.
3. Build a JWT header with `alg: HS256`, `kid: <id>`, `typ: JWT`.

```json
{
  "alg": "HS256",
  "kid": "<API_KEY_ID>",
  "typ": "JWT"
}
```

4. Build a payload with integer-second timestamps and the audience claim:

```json
{
  "iat": 1700000000,
  "exp": 1700000300,
  "aud": "/admin/"
}
```

5. Base64url-encode each segment without padding (`=` stripped), sign the `header.payload` string with HMAC-SHA256 keyed by the decoded bytes, append the base64url signature as the third dot-separated segment.
6. Send it as `Authorization: Ghost <token>` — the scheme is `Ghost`, not `Bearer`.
7. Include `Accept-Version: v6.0` and, for JSON writes, `Content-Type: application/json`.

Python equivalent of the bundled script's signer:

```python
import base64, hashlib, hmac, json, time

def admin_token(key: str, request_path: str = "/ghost/api/admin/") -> str:
    key_id, secret_hex = key.split(":", 1)
    hmac_key = bytes.fromhex(secret_hex)          # decode hex to raw bytes
    now = int(time.time())
    def b64url(obj) -> str:
        return base64.urlsafe_b64encode(
            json.dumps(obj, separators=(",", ":")).encode()).rstrip(b"=").decode()
    header = b64url({"alg": "HS256", "typ": "JWT", "kid": key_id})
    audience = "/admin/"                          # see audience rules below
    payload = b64url({"iat": now, "exp": now + 300, "aud": audience})
    signing_input = f"{header}.{payload}".encode()
    signature = hmac.new(hmac_key, signing_input, hashlib.sha256).digest()
    return f"{header}.{payload}." + base64.urlsafe_b64encode(signature).rstrip(b"=").decode()
```

### Rules that decide whether a token works

- **Algorithm must be HS256.** A token signed with HS512 is rejected outright (`Invalid token: invalid algorithm`). Do not "upgrade" the algorithm; Ghost's verifier allow-lists HS256 only.
- **aud (audience)** for current unversioned URLs (`/ghost/api/admin/...`) is exactly `/admin/`. Legacy versioned routes scope the audience to their URL version (`/v3/admin/`, `/v4/admin/`; v5 has no such form — Ghost 5 removed versioned URLs entirely). Sending `Accept-Version: v6.0` does not change the audience.
- **exp ≤ iat + 300.** Five minutes is the documented maximum token lifetime. The server additionally enforces a five-minute maximum age measured from `iat`, so a long-lived token fails even mid-window. Mint a fresh token for each request rather than caching them.
- **Timestamps are seconds**, not milliseconds. Millisecond values produce oversized `iat`/`exp` and fail validation.
- **NTP matters.** A skewed system clock shifts `iat` outside the acceptance window even though your code looks correct.

## Error signatures for auth failures

Ghost returns JSON errors shaped like `{"errors": [{"message", "context", "type", "code", ...}]}`. Distinct auth failure modes have distinct signatures worth memorizing:

| Symptom | Status | Meaning |
| --- | --- | --- |
| `Invalid token: jwt expired` / `maxAge exceeded`, code `INVALID_JWT` | 401 | Token lifetime violated — mint fresher tokens |
| `Invalid token: invalid algorithm`, `INVALID_JWT` | 401 | Wrong alg (e.g. HS512); sign HS256 |
| `jwt audience invalid`, `INVALID_JWT` | 401 | Wrong aud; use `/admin/` for unversioned URLs |
| `Admin API kid missing.`, `MISSING_ADMIN_API_KID` | 400 | JWT header lacks `kid` |
| `Unknown Admin API Key`, `UNKNOWN_ADMIN_API_KEY` | 401 | kid does not match any integration; key regenerated? |
| `Authorization header format is "Authorization: Ghost [token]"`, `INVALID_AUTH_HEADER` | 401 | Used `Bearer` instead of the `Ghost` scheme |
| Malformed token JSON/base64, `INVALID_JWT` | 400 | Structurally undecodable token |
| No auth at all → `Authorization failed`, type `NoPermissionError` | 403 | Missing `Authorization` header entirely |

The CLI maps each of these to exit code 2 with the server message plus a hint.

## Request conventions

```http
GET /ghost/api/admin/posts/?limit=15&page=1 HTTP/1.1
Host: example.com
Authorization: Ghost <token>
Accept-Version: v6.0
Accept: application/json
```

- All resources ride in plural envelopes: `{"posts": [...], "meta": {...}}`. Writes must wrap payloads the same way: `{"posts": [{...}]}`. `/site/` and `/settings/` are the sole exceptions (single objects).
- Pagination defaults to `page=1&limit=15`; Ghost 6 caps page size at 100 and no longer honors `limit=all`.
- Filter syntax follows NQL: `filter=status:draft` uses URL-encoded `property:value`, comma is OR, parentheses group, `-` negates.
- `include=tags,authors` hydrates relations; `fields=title,slug,status` slims responses.

## Sources

- https://docs.ghost.org/admin-api
- https://docs.ghost.org/admin-api/#token-generation
- https://docs.ghost.org/admin-api/#accept-version-header
- https://docs.ghost.org/faq/api-versioning
- https://docs.ghost.org/content-api/pagination
- https://github.com/TryGhost/Ghost/blob/main/ghost/core/core/server/services/auth/api-key/admin.js
