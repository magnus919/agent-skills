# Transistor API: Authentication, JSON:API Envelope, and Request Basics

Everything in this file is from the official API reference
(developers.transistor.fm) and Transistor's own support pages, verified
live at authoring time. Transistor.fm's public API is v1 and speaks
JSON:API on responses; there is exactly one authentication mode.

## Authentication

- Every request carries an HTTP header `x-api-key` whose value is the API
  key. There is no OAuth, no bearer token, and no signing on the REST API.
- Keys are created, viewed, and reset in the Transistor Dashboard's Account
  page, in the section marked **API Access**
  (https://dashboard.transistor.fm/account). Transistor's support article
  "Does Transistor have an API?" (updated 2026-07) names exactly this
  location; the bundled CLI prints it on every auth error.
- A key grants whatever the associated dashboard user can see: access to
  podcasts and episodes follows the user's podcast role — **owner**,
  **admin**, or **regular team member**. There are no narrower per-key
  scopes: a leaked key is as powerful as its user. Treat it like a
  password; reset it from the same Account page if it leaks.
- The authorization probe is `GET /v1` — it returns the authenticated
  `user` resource and nothing else. There is **no `/v1/user` and no
  `/v1/authorization` route**; older tutorials that call `/v1/user` get a
  404. The `user` resource has `name`, `time_zone`, `image_url`, and
  timestamps — **it has no email attribute**.

```sh
curl https://api.transistor.fm/v1 -H "x-api-key: <API_KEY>"
```

## Rate limits

- **10 requests per 10 seconds.** Exceeding the limit returns HTTP `429`
  and access is blocked for 10 seconds; after that requests flow again.
- No rate-limit headers (`Retry-After` etc.) are documented — don't parse
  for them; just back off on 429.
- Transistor explicitly states the API is not meant to be the main data
  source for a website or app back end; pull data once, cache it, and parse
  the public RSS feed XML when you would otherwise hammer the API. For
  push-style updates, webhooks (see the endpoint catalog) exist for
  `episode_created`, `episode_published`, `subscriber_created`, and
  `subscriber_deleted`.

## The JSON:API envelope

Responses are JSON:API documents. Learn four keys and every endpoint is
readable:

| Key | Shape | Meaning |
| --- | --- | --- |
| `data` | object (single resource) or array (collections) | The primary resource(s) of the response |
| `attributes` | object inside a resource | The resource's fields (title, status, media_url, ...) |
| `relationships` | object of `{"<name>": {"data": {"id", "type"}}}` | Links to related resources by id and type |
| `included` | array (only when requested with `include[]`) | The full related resources — a "compound document" |

- Resource `type` values: `user`, `show`, `episode`, `subscriber`,
  `show_analytics`, `episodes_analytics`, `episode_analytics`,
  `audio_upload`, `webhook`.
- Single-resource responses wrap one object: `{"data": {"id": ...,
  "type": "episode", "attributes": {...}, "relationships": {...}}}`.
- Collection responses wrap an array plus pagination under `meta`:
  `{"data": [...], "meta": {"currentPage", "totalPages", "totalCount"}}`.
- Ids are **strings** even when numeric ("3056098"); analytics ids may be
  slugs ("the-caffeine-show"). Keep ids as strings end to end.
- `included[]` appears only when you ask for it. `GET
  /v1/episodes/3056098?include[]=show` returns the episode plus the parent
  show in `included`, matched via `data.relationships.show.data.id`.

### jq patterns for the envelope

```sh
# Single resource: unwrap data.attributes
curl -s https://api.transistor.fm/v1/episodes/<EPISODE_ID> -H "x-api-key: <API_KEY>" \
  | jq '.data.attributes | {title, status, published_at}'

# Collection: titles plus ids, one per line
curl -s 'https://api.transistor.fm/v1/episodes?show_id=<SHOW_ID>' -H "x-api-key: <API_KEY>" \
  | jq -r '.data[] | [.id, .attributes.title, .attributes.status] | @tsv'

# Compound document: pull the parent show's title out of included[]
curl -s 'https://api.transistor.fm/v1/episodes/<EPISODE_ID>?include[]=show' -H "x-api-key: <API_KEY>" \
  | jq --arg id "$(curl -s ... | jq -r '.data.relationships.show.data.id')" \
      '.included[] | select(.type == "show" and .id == $id) | .attributes.title'

# Simpler: match included[] by type when only one show was included
... | jq '.included[] | select(.type == "show") | .attributes.title'

# Pagination loop values live in meta
... | jq '{page: .meta.currentPage, last: .meta.totalPages, total: .meta.totalCount}'
```

The bundled CLI does this unwrapping for `--json` output: collections come
back as `{"episodes": [...], "meta": {...}}` with each item flattened to the
fields agents actually need (including `show_id` from relationships), and
single resources as one flat object.

## Pagination

- Page-based, two parameters: `pagination[page]` (documented default `0`;
  the doc examples explicitly request page `1`) and `pagination[per]`
  (default `10`).
- Every collection returns `meta.currentPage`, `meta.totalPages`, and
  `meta.totalCount`. Loop while `currentPage < totalPages`, incrementing
  the page — do not assume the first page is `0` or `1`, read `meta`.
- There is no cursor, no `page[number]`/`page[size]` JSON:API-style
  spelling, and no `pagination[limit]` — unknown params are silently
  ignored, which is exactly how scripts that "paginate" with
  `pagination[limit]` re-read the first page forever.

## Sparse fieldsets and compound documents

Any endpoint accepts JSON:API's standard extras:

- Sparse fieldsets: `fields[episode][]=title&fields[episode][]=media_url`
  returns only those attributes (smaller payloads, faster loops).
- Include related resources: `include[]=show` on an episode, `include[]=show`
  on analytics, `include[]=episode` on episode analytics. Combine both:
  `include[]=show&fields[show][]=title&fields[show][]=feed_url`.

## Request bodies: form-encoded bracket keys (documented), JSON accepted

- The reference intro says endpoints accept **JSON or form-encoded** request
  bodies. Every documented mutation example uses form-encoded bracket keys:
  `episode[show_id]=...`, `episode[title]=...`, `show[title]=...`,
  `subscriber[email]=...`, `episode[status]=published`.
- The docs publish no JSON-body equivalent examples, so the bracket-key
  shapes above are the contract to copy. The bundled CLI sends form-encoded
  bodies byte-compatible with the documented curl examples.
- Required-vs-optional matters: `episode[show_id]` is the only required
  field on episode creation; `episode[status]` is required on the publish
  endpoint; `show_id` is required on subscribers/webhooks listings.

## Error surfaces

Responses use standard HTTP codes. The reference does not document a formal
error schema, so program defensively:

- `401` — key missing/invalid → check `x-api-key` and the Account page.
- `403` — key valid, role insufficient (owner/admin needed for some
  operations on a shared podcast).
- `404` — id/slug not found (and remember: `/v1/user` is not a route).
- `422` — validation errors (e.g. bad `episode[status]` value).
- `429` — rate limit (10 requests / 10 s window).

Error bodies seen in practice are JSON; the bundled CLI accepts either a
JSON:API-style `errors[]` array or a bare `{"message": ...}` object and
flattens whichever it gets into one stderr line.

## Sources

- https://developers.transistor.fm/ (introduction, JSON:API conformance,
  authentication, rate limits, sparse fieldsets/include[] sections; all
  endpoint examples) — fetched live 2026-08-29 (HTTP 200)
- https://developers.transistor.fm/#authentication (header name, Account
  Area key management, owner/admin/team-member access levels)
- https://developers.transistor.fm/#ratelimits (10 requests / 10 s, 429 +
  10 s block, caching/RSS guidance)
- https://developers.transistor.fm/#get-v1 (GET /v1 user resource example)
- https://developers.transistor.fm/#resources (type list; User resource
  fields — no email)
- https://support.transistor.fm/en/article/does-transistor-have-an-api-1b24sjo/
  (API key location: Account page → API Access) — fetched live 2026-08-29
- https://support.transistor.fm/en/article/what-automations-are-possible-with-transistor-bi27am/
  (supported automations, show-creation limitation) — fetched live 2026-08-29
