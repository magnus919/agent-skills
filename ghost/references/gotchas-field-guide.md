# Ghost CMS Gotchas Field Guide

Real-world failure modes, their symptoms, and their fixes. Each entry states the symptom first so this file can be scanned mid-incident.

## Auth and keys

**Symptom: 401 with `Invalid token: jwt expired` or `maxAge exceeded`.**
Your token outlived its five-minute window. Ghost both rejects `exp` more than 300 seconds past `iat` *and* independently caps token age at five minutes from `iat`, so caching tokens across a long batch job fails midway. Mint a fresh token per request — the bundled CLI does this automatically.

**Symptom: 401 `Invalid token: invalid algorithm`.**
The token was signed HS512 (or another algorithm). Ghost's verifier allow-lists exactly `['HS256']`; "stronger" algorithms are rejected, not gracefully accepted. Sign HS256.

**Symptom: signature looks right but still 401.**
You signed the HMAC key with the literal hex characters of the secret half instead of the raw bytes they encode. Hex-decode first (`bytes.fromhex(secret_hex)` in Python; `-macopt hexkey:$SECRET` in the official OpenSSL example). This is the most common hand-rolled signer bug.

**Symptom: used `Authorization: Bearer ...` → 401 `INVALID_AUTH_HEADER`.**
Ghost's scheme is `Ghost`: `Authorization: Ghost <token>`.

**Symptom: worked for months, suddenly 401 `UNKNOWN_ADMIN_API_KEY`.**
Someone regenerated the integration key in Ghost Admin. Old scripts keep signing tokens under a kid the server no longer knows. Update every deployment holding the old key.

**Symptom: fails only on one machine.**
Clock skew. Tokens are valid within tight iat/exp windows and NTP drift breaks them. Sync the clock.

## Content visibility

**Drafts invisible even though everything authenticates:** you are hitting the Content API (Content key, `/ghost/api/content/`). It serves published posts only, silently ignoring filters like `status:draft`, and it never errors about what it hides. Use the Admin API (Admin key + JWT) to reach drafts and scheduled posts. See [content-vs-admin-api.md](content-vs-admin-api.md).

**Reading a known post id returns 404 from site code but renders in Admin:** same asymmetry from the other side — non-public content simply does not exist on the public plane.

## Editing

**409 `UpdateCollisionError` ("Saving failed! Someone else is editing this post."):** your PUT carried a stale `updated_at`. Every edit payload must include the version you actually read; re-GET immediately before PUT and pass its exact timestamp string. Concurrent editors and parallel automation make this likelier, not less.

**Tags/authors vanished after an edit:** relation arrays REPLACE on update rather than merge. `PUT {"tags":["news"]}` deletes every other tag. Fetch-modify-send the complete array.

**HTML came through mangled or stripped:** native post source is Lexical. Passing `html` requires the `?source=html` flag, and Ghost's HTML→Lexical conversion is lossy — inline styles and exotic tags get normalized. Preserve verbatim markup inside an HTML card (`<!--kg-card-begin: html-->…<!--kg-card-end: html-->`) or send proper Lexical JSON.

**Slug differed from what you sent:** slugs are uniquified (`my-post-2`) and sanitized (lowercase, hyphens) server-side. Read back `slug` from the create/edit response rather than assuming echo.

## Pagination and volume

**Only ever see ~15 (or at most 100) results:** default page size is 15; Ghost 6 caps limit at 100 and removed `limit=all` (oversized limits no longer error — they silently return ≤100 rows). Loop pages via `meta.pagination.next` until null. Treat totals as advisory; iterate by `next`.

**Bulk script gets slow/rate-limited on big exports:** stagger requests between pages. There is no single documented universal rate limit; throttling is host-dependent and appears as 429 `TooManyRequestsError`. Back off exponentially and honor any Retry-After header seen in practice.

## Versions

**Requests work locally but docs examples conflict:** send `Accept-Version: v6.0` on every request. Versioning lives in headers since Ghost 5 removed versioned URLs; legacy URLs redirect internally and mark responses `Deprecation`. Breaking changes arrive only with major versions (~annually), and Ghost emails admins if a client sends unservable versions — another reason stale CI integrations suddenly "stop working" after upgrades.

**Mobiledoc field errors after an upgrade:** Ghost 5+ replaced Mobiledoc with Lexical as the canonical content format. Integrations writing Mobiledoc must migrate to `lexical` (or use HTML cards).

## Skill boundary reminder

This skill drives the REST APIs. Server installation, nginx/SSL/systemd setup, `ghost start/stop/update/backup/doctor`, and theme-file editing belong to Ghost's separate npm `ghost-cli` ops tooling — different tool entirely.

## Sources

- https://docs.ghost.org/admin-api
- https://docs.ghost.org/content-api
- https://docs.ghost.org/changes
- https://docs.ghost.org/faq/api-versioning
