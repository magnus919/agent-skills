# Jira Cloud REST API v3 — Auth, Search & Pagination

Ground truth for authenticating against Jira Cloud and for running searches under both pagination models. Every claim traces to the Atlassian sources in the footer.

## Authentication

### Basic auth: email + API token (the default for scripts and CLIs)

Atlassian's recommended method "for personal scripts, bots, and ad-hoc execution of the REST APIs":

1. Create an API token at `https://id.atlassian.com/manage/api-tokens` (shown once; cannot be recovered later).
2. Build the string `email:api_token` — email is your **Atlassian account email address**, never a password.
3. Base64-encode it and send it as a proactively-supplied header:

```
Authorization: Basic base64(email:token)
```

`requests` does this via `auth=(email, token)` tuple — no manual base64 needed.

Facts worth knowing:

- API tokens work even when the org has two-factor authentication or SAML enabled.
- Since December 15 2024 new tokens expire after one year by default (configurable 1 day–1 year); tokens created before that were retroactively given expiry from March 13 2025. Expired tokens surface as 401s.
- Password authentication is fully deprecated; there is no password fallback.
- Jira does not send an auth challenge — clients must send the header unprompted.
- Tokens can optionally carry OAuth-style scopes; scoped tokens are used against `https://api.atlassian.com/ex/jira/{cloudId}` instead of the site URL. Scopeless tokens keep working against `https://your-domain.atlassian.net`.

### The other methods, and when they apply

| Method | Applies to | Header | Base URL |
|--------|-----------|--------|----------|
| Basic + API token | personal scripts, bots | `Basic base64(email:token)` | site URL |
| OAuth 2.0 (3LO) | integrations acting for users, distributable apps | `Bearer ACCESS_TOKEN` | `https://api.atlassian.com/ex/jira/{cloudId}` |
| Forge / Connect apps | apps on those platforms | built-in JWT/requestJira | varies |

### PATs: Data Center yes, Cloud no

Personal Access Tokens (`Authorization: Bearer <token>`) exist only on **Data Center/Server** (Jira 8.14+). Jira Cloud has no PAT feature; its equivalent is the API-token model above. Point anyone asking about "Bearer tokens for Jira" at DC docs or to 3LO for Cloud.

### CAPTCHA lockout symptom

After repeated failed logins Jira may trigger CAPTCHA, which blocks REST auth entirely. Symptom: response header `X-Seraph-LoginReason: AUTHENTICATION_DENIED` — login rejected "without even checking the password". Fix by logging in through the browser once, not by retrying the script.

## Rate Limits

Three systems, all surfacing as HTTP 429 with these headers:

```
Retry-After: <seconds>
X-RateLimit-Limit: <ceiling>
X-RateLimit-Remaining: 0
X-RateLimit-Reset: <ISO 8601 timestamp>
RateLimit-Reason: jira-quota-global-based
```

`RateLimit-Reason` values: `jira-quota-global-based`, `jira-quota-tenant-based` (hourly point quotas), `jira-burst-based` (per-second buckets; defaults ~100 req/s GET/POST), `jira-per-issue-on-write` (20 writes/2s per issue). Honor `Retry-After`; back off with jitter rather than tight retries.

## Error Envelopes

Standard error collection everywhere in v3:

```json
{ "errorMessages": ["..."], "errors": {"field_name": "message"}, "status": 400 }
```

| Status | Meaning |
|--------|---------|
| 400 | Malformed request or bad JQL ("Field 'X' does not exist..."); `errors` map names offending fields |
| 401 | Credentials rejected/expired (or CAPTCHA-gated — check `X-Seraph-LoginReason`) |
| 403 | Authenticated but lacking permission |
| 404 | Resource absent or invisible |
| 422 | Validation failure on create/edit payloads |
| 429 | Rate limited — see headers above |

## Search Endpoints: the Duality

This is the single most important operational fact about Jira Cloud search in the current era: **two search endpoints with incompatible pagination models coexist**, and the legacy one is being removed.

### Legacy: `GET|POST /rest/api/3/search` — offset paging

Status: documented as "**Currently being removed**" and marked deprecated in the OpenAPI spec. Announced 31 October 2024 with removal promised "after May 1, 2025" (CHANGE-2046); sunset has proceeded gradually since.

Request parameters: `jql`, `startAt` (default 0), `maxResults` (default 50), `validateQuery` (`strict` default | `warn` | `none`), `fields`, `expand`, `properties`, `fieldsByKeys`, `failFast`.

Response envelope (`SearchResults`):

```json
{
  "issues": [{"id": "10002", "key": "ED-1", "fields": {}}],
  "startAt": 0,
  "maxResults": 50,
  "total": 1,
  "warningMessages": []
}
```

Loop shape:

```python
start_at = 0
while True:
    page = get("/search", params={"jql": jql, "startAt": start_at, "maxResults": 100})
    yield from page["issues"]
    start_at += len(page["issues"])
    if start_at >= page.get("total", 0) or not page["issues"]:
        break
```

Caveats: `total` can change between pages, so always tolerate an empty page; there is no `isLast` field on this envelope; deep offsets re-scan everything before them.

### Enhanced: `GET|POST /rest/api/3/search/jql` — token paging

The replacement, non-deprecated. Request body/params: `jql`, `nextPageToken`, `maxResults` (default 50, ceiling 5,000 — though real-world pages often cap near 100 even when more are requested, so follow the token instead of assuming page sizes), `fields` (**default is `id` only**, unlike every other endpoint), `expand`, `properties`, `fieldsByKeys`, `failFast`, `reconcileIssues`.

Response envelope (`SearchAndReconcileResults`):

```json
{
  "isLast": false,
  "issues": [{"id": "10002", "key": "ED-1"}],
  "nextPageToken": "CAEaAggB",
  "warnings": []
}
```

Key differences from legacy:

| Aspect | Legacy `/search` | Enhanced `/search/jql` |
|--------|------------------|------------------------|
| Offset param | `startAt` | none — opaque `nextPageToken` |
| Total count | `total` present | absent |
| Last-page signal | none (compute from total) | `isLast` boolean; `nextPageToken` omitted on final page |
| Default fields | all navigable | `id` only — pass explicit `fields` |
| Warnings key | `warningMessages` | `warnings` |
| JQL restriction | unbounded allowed | **bounded queries required** — bare `order by key desc` returns 400 |
| `orderBy` cap | none | max 7 fields |
| Consistency | immediate-ish | eventual; optional `reconcileIssues` (≤50 ids) for read-after-write |

"Bounded" means at least one real condition: `assignee = currentUser() order by key` is bounded; `order by created DESC` alone is not.

Loop shape:

```python
body = {"jql": jql, "maxResults": 100, "fields": ["summary", "status"]}
while True:
    page = post("/search/jql", json_data=body)
    yield from page["issues"]
    if page.get("isLast") or "nextPageToken" not in page:
        break
    body["nextPageToken"] = page["nextPageToken"]
```

Token continuation is sequential-only: you cannot fetch pages in parallel, and you must carry the exact previous token forward.

### Which model fails how — symptoms of mixing them up

- Passing `startAt` to `/search/jql`: parameter ignored/rejected; you silently loop over page one forever if your loop advances the offset instead of the token.
- Reading `total` off `/search/jql`: `KeyError` — the field does not exist; use `/search/approximate-count` first if you need a count.
- Expecting populated `fields` from `/search/jql` without asking: you get `id`/`key` only.
- Sending an unbounded query to `/search/jql`: immediate `400`.
- Calling legacy `/search` after removal completes: connection-level failure/404-class errors; before that, responses still work but the endpoint is formally dead-ended.

### Approximate counts

Need "how many?" without fetching? `POST /rest/api/3/search/approximate-count` with body `{"jql": "project = HSP"}` returns `{"count": 153}`. Works regardless of which search endpoint you use for rows; approximate because it skips permission filtering per row.

## Endpoint Cheat Sheet

| Operation | Call |
|-----------|------|
| Current user | `GET /rest/api/3/myself` → `{accountId, displayName, emailAddress?, timeZone}` |
| Search (legacy) | `GET/POST /rest/api/3/search` — deprecated, offset paging |
| Search (current) | `GET/POST /rest/api/3/search/jql` — token paging |
| Count matches | `POST /rest/api/3/search/approximate-count` |
| Get issue | `GET /rest/api/3/issue/{key}?fields=summary,status,...` |
| Create issue | `POST /rest/api/3/issue` — `{fields: {...}}` |
| Edit issue | `PUT /rest/api/3/issue/{key}` — fields at top level, `notifyUsers=false` to silence mail |
| Delete issue | `DELETE /rest/api/3/issue/{key}?deleteSubtasks=true` |
| List transitions | `GET /rest/api/3/issue/{key}/transitions` |
| Apply transition | `POST /rest/api/3/issue/{key}/transitions` — `{"transition": {"id": "..."}}` |
| Add comment | `POST /rest/api/3/issue/{key}/comment` — ADF body |
| Projects | `GET /rest/api/3/project/search` (paginated; plain `/project` is a deprecated bare array) |

## Sources

- REST API v3 intro (auth modes, error collection): https://developer.atlassian.com/cloud/jira/platform/rest/v3/intro/
- Issue search group (both endpoints, approximate-count): https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-search/
- Basic auth for REST APIs: https://developer.atlassian.com/cloud/jira/platform/basic-auth-for-rest-apis/
- Deprecation changelog entry CHANGE-2046: https://developer.atlassian.com/changelog/#CHANGE-2046
- Rate limiting: https://developer.atlassian.com/cloud/jira/platform/rate-limiting/
- Manage API tokens: https://support.atlassian.com/atlassian-account/docs/manage-api-tokens-for-your-atlassian-account/
- OAuth 2.0 (3LO) apps: https://developer.atlassian.com/cloud/jira/platform/oauth-2-3lo-apps/
- PATs (Data Center/Server only): https://confluence.atlassian.com/enterprise/using-personal-access-tokens-1026032365.html
