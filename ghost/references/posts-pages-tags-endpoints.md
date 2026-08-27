# Admin Endpoint Guide: Posts, Pages, Tags, Pagination, Errors

All paths relative to `https://{admin_domain}/ghost/api/admin/`. Authentication per [admin-auth-and-basics.md](admin-auth-and-basics.md).

## Posts

```text
GET    /posts/              browse (filter, limit, page, order, include, fields, formats)
GET    /posts/{id}/         read by id
GET    /posts/slug/{slug}/  read by slug
POST   /posts/              create
PUT    /posts/{id}/         edit
DELETE /posts/{id}/         delete (204 No Content)
```

Post fields include `id`, `uuid`, `title`, `slug`, `html` (rendered), `lexical` (Ghost 5+ source format, replacing Mobiledoc), `status`, `visibility`, `created_at`, `updated_at`, `published_at`, plus tag/author relations and computed `url`/`excerpt`. Ghost 6 returns `lexical` by default; pass `formats=html,lexical` when you need rendered HTML alongside the source.

### Creating posts

Only `title` is required. Omitting `status` creates a draft — the safest default for automation.

```bash
curl -sS -X POST "$BASE/posts/" \
  -H "Authorization: Ghost $TOKEN" \
  -H "Content-Type: application/json" \
  -H "Accept-Version: v6.0" \
  --data '{"posts":[{"title":"Release notes"}]}'
```

Add content either as a JSON-encoded Lexical document in `lexical`, or with `html` **plus the `?source=html` query flag**, which converts HTML to Lexical server-side. The conversion is lossy; wrap markup you must preserve verbatim in an HTML card (`<!--kg-card-begin: html--> ... <!--kg-card-end: html-->`). Scheduled posts require `status: scheduled` and a future ISO 8601 `published_at`.

### Editing posts: the collision guard

PUT updates are partial, but every edit payload MUST carry the resource's current `updated_at`. Treat it as proof you read the latest version. The recommended sequence is GET immediately before PUT.

```json
{"posts": [{"updated_at": "<RECORD_UPDATED_AT>", "status": "published"}]}
```

Sending a stale `updated_at` fails with HTTP 409 `UpdateCollisionError` ("Saving failed! Someone else is editing this post."). A second editor (or another script) racing your automation is the usual trigger; re-GET, merge, retry.

**Tag and author relations replace, never merge:** PUTting `tags:["news"]` removes all other tags. Fetch the post, modify the complete array, send it back whole.

### Status lifecycle

`draft` → editable, invisible to public plane → `scheduled` (requires future `published_at`; Ghost flips it to `published` automatically) → `published` → back to `draft` via PUT if needed. Email-only posts report `sent` after dispatch.

## Pages

Same verb set as posts at `/pages/`, plus `POST /pages/{id}/copy/` to duplicate. Pages are API-shape-identical to posts but render outside collection channels (about pages, landing pages). Creation is identical: only `title` required, omitting status drafts it.

## Tags

```text
GET    /tags/      browse (add include=count.posts for usage counts)
POST   /tags/      create
PUT    /tags/{id}/ edit
DELETE /tags/{id}/ delete
```

Creating a tag that already exists by name/slug errors with a validation message rather than deduplicating; browse first when unsure. Hidden/internal tags carry `visibility: internal` and code-style slugs (`hash-...`).

## Site info

`GET /site/` is unauthenticated and returns a single object (no envelope): `{title, description, logo, url, version}`. Handy as a connectivity check before sending authenticated requests.

## Pagination

Browse endpoints default to `page=1&limit=15`. Ghost 6 caps page size at 100 — `limit=all` and `limit=9999` no longer error but silently return at most 100 rows. Consumers MUST loop:

```python
page = 1
while True:
    doc = get_posts(page=page, limit=100)
    yield from doc["posts"]
    nxt = doc["meta"]["pagination"]["next"]
    if nxt is None:
        break
    page = nxt
```

`meta.pagination` shape: `{"page": 1, "limit": 100, "pages": 7, "total": 624, "next": 2, "prev": null}`. Drive loops from `next` (null terminates), never from precomputed arithmetic on `total`, which can move mid-run under concurrent edits. Add a small delay between pages on large exports; hosts throttle aggressive crawlers even though Ghost itself documents no fixed rate limit.

## Error envelope and status codes

```json
{
  "errors": [{
    "message": "...", "context": null,
    "type": "NotFoundError",
    "details": null, "property": null,
    "help": null, "code": null,
    "id": "...", "ghostErrorCode": null
  }]
}
```

| Status | type | When |
| --- | --- | --- |
| 400 | ValidationError / BadRequestError | Malformed query or payload, invalid field values |
| 401 | UnauthorizedError | Bad/expired/malformed JWT (see auth reference table) |
| 403 | NoPermissionError | Missing header, insufficient integration permissions |
| 404 | NotFoundError | Unknown id/slug, or non-public resource via Content API |
| 409 | UpdateCollisionError | Stale `updated_at` on PUT |
| 429 | TooManyRequestsError | Host throttling; back off, honor any Retry-After |
| 500 |ServerError | Ghost-side failure; safe to retry idempotent reads |

Match errors on `errors[].code` where present (`UPDATE_COLLISION`, `INVALID_JWT`); messages change copy between releases less often than types, but codes are most stable of all.

## Sources

- https://docs.ghost.org/admin-api/posts/overview
- https://docs.ghost.org/admin-api/posts/creating-a-post
- https://docs.ghost.org/admin-api/posts/updating-a-post
- https://docs.ghost.org/admin-api/posts/publishing-a-post
- https://docs.ghost.org/admin-api/posts/scheduling-a-post
- https://docs.ghost.org/admin-api/pages/overview
- https://docs.ghost.org/admin-api/site/overview
- https://docs.ghost.org/content-api/pagination
- https://docs.ghost.org/content-api/errors
- https://docs.ghost.org/changes
