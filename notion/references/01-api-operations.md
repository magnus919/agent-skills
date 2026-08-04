# Notion API Operations

> **Last Updated:** 2026-08-03

Operational detail for the Notion API surface the skill owns: endpoints, the version header, pagination, property values, filters, and error handling. The bundled `notion-cli` implements this reference; use this document when a call behaves unexpectedly.

## Request conventions

- Base URL: `https://api.notion.com/v1`. Every request carries `Authorization: Bearer <integration_token>` and the `Notion-Version` header (default `2022-06-28`; `notion-cli` honors `NOTION_VERSION`).
- Bodies are JSON. Reads with bodies (search, database query) are `POST`; single-object reads are `GET`; updates are `PATCH`; creates are `POST`.

## Endpoint surface

| Operation | Endpoint | Method | Notes |
|---|---|---|---|
| Retrieve a page | `/pages/{id}` | GET | Summarized as id, title, url, timestamps |
| Create a page | `/pages` | POST | Guarded mutation; `parent` is `page_id` or `database_id` |
| Update page properties | `/pages/{id}` | PATCH | Guarded mutation; overwrites the given property values |
| Query a database | `/databases/{id}/query` | POST | `page_size` cap + optional `filter` object |
| Search | `/search` | POST | Finds pages and databases by text; `page_size` cap |

## Pagination and bounded reads

- Search and database queries take `page_size` (max 100) and return `has_more` plus a `next_cursor` when more rows exist.
- **Bounded-read rule:** request only what the task needs; `notion-cli --limit` caps `page_size` at the request level. If a task needs more, raise the limit or page with the cursor, and stop when the question is answered.
- Always report `has_more` when summarizing a query so the reader knows the cap hid further rows.

## Property values

- A page's `properties` is a map of property names to value objects. Title extraction: `notion-cli` looks for a property typed `title` (commonly named `title` or `Name`).
- Common value objects for updates: `{"select": {"name": "..."}}`, `{"status": {"name": "..."}}`, `{"checkbox": true|false}`, `{"rich_text": [{"text": {"content": "..."}}]}`, `{"number": 42}`, `{"date": {"start": "2026-08-03"}}`.
- An update `PATCH` sends only the properties you include; properties you omit are left unchanged. Omitted properties are safe; *wrong* values for included properties are the risk, so preview the exact payload with `--dry-run`.

## Filters

Database query filters are structured JSON, e.g.:

```json
{"property": "Status", "select": {"equals": "Open"}}
{"or": [
  {"property": "Priority", "select": {"equals": "High"}},
  {"property": "Priority", "select": {"equals": "Critical"}}
]}
```

A `--filter` file must be a single JSON object; `notion-cli` validates it parses before sending.

## Error handling

- HTTP 400 `validation_error`: the body shape or filter is wrong — the message names the offending field. Fix the payload, never retry blindly.
- HTTP 404 `object_not_found`: almost always the page/database is **not shared with the integration**, not deleted. Check sharing settings before concluding data loss.
- HTTP 401 `unauthorized`: token invalid or revoked — rotate the integration token.
- HTTP 429 `rate_limited`: slow down; Notion rate limits per integration.
- `notion-cli` exit 1 with a `Notion API HTTP <code>: <message>` line; the `--json` variant emits `{"ok": false, "error": "..."}`.

## Integration access model

- An integration sees exactly the pages and databases **shared with it**. Sharing a parent page shares descendants unless a child overrides.
- Search only covers content the integration can access — a workspace-wide search from the app may find more than the API search will.
- Tokens are workspace-scoped credentials; store in `NOTION_TOKEN`, never in code, chat, or commits. Revoke a leaked token in the integration settings.
