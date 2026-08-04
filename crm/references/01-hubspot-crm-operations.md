# HubSpot CRM Operations

> **Last Updated:** 2026-08-03

Operational detail for the HubSpot CRM v3 API surface the skill owns: contact records, contact search, deal pipeline views, and guarded deal stage updates. The bundled `crm-cli` implements this reference; use this document when a call behaves unexpectedly.

## API conventions

- Base URL: `https://api.hubapi.com/crm/v3`. Every request carries `Authorization: Bearer <private_app_token>` and JSON bodies.
- Access is scope-based: private app tokens grant per-object read/write. A 403 means the token lacks the scope — check `crm.objects.contacts.read`, `crm.objects.deals.read` (reads) and `crm.objects.deals.write` (stage updates) before concluding anything else.
- `crm-cli` honors `HUBSPOT_API_BASE` (test/stub override); production default is the v3 base.

## Endpoint surface

| Operation | Endpoint | Method | Notes |
|---|---|---|---|
| List contacts | `/objects/contacts?limit=N` | GET | Summarized as name, email, company, createdate |
| Get a contact | `/objects/contacts/{id}` | GET | Single record |
| Search contacts | `/objects/contacts/search` | POST | JSON body `{"query": ..., "limit": N}` |
| List deals | `/objects/deals?limit=N` (+ `pipeline`, `dealstage`) | GET | Pipeline view with amount + stage |
| Move a deal | `/objects/deals/{id}` | PATCH | Guarded mutation: sets the `dealstage` property |
| List pipelines | `/pipelines/deals` | GET | Pipelines with stage IDs and labels |

## Object model

- Every object is an `id` plus a `properties` map keyed by property name. Property values are strings in list/search responses (e.g. `dealstage`, `dealname`, `amount`, `email`, `firstname`, `lastname`, `company`).
- Deals belong to a pipeline (`pipeline` property) and a stage (`dealstage` property) whose valid values come from `/pipelines/deals`. **Stage changes use the stage ID, never the label.**
- Search (`POST /objects/contacts/search`) accepts a `query` string and a `limit`; it matches across default contact searchable properties.

## Pagination and bounded reads

- List endpoints return `results` plus `total` and `paging.next.after` (offset cursor). `limit` caps per-request results (max 100 for most object APIs).
- **Bounded-read rule:** request only what the task needs; `crm-cli --limit` caps at the request level. Report the `total` alongside the returned results so the reader knows the cap hid further records.

## Guarded stage updates

- Moving a deal sets `{"properties": {"dealstage": "<stage-id>"}}` via PATCH. Preview with `--dry-run` (prints the exact deal + target stage), confirm with `--yes`, then verify by re-reading the deal.
- Stage moves are visible to the whole revenue team and land in audit history. They are reversible, but every move is a recorded change — confirm before acting.
- Only the `dealstage` property is in this skill's mutation surface. Other deal property edits are application work.

## Error handling

- 401 `unauthorized`: token invalid or revoked — rotate the private app token.
- 403 `forbidden`: token lacks object scope — grant the scope in the private app settings, don't retry blindly.
- 404 `not found`: object does not exist **or** the token cannot see it — verify object ID and scope before concluding deletion.
- 429 `RATE_LIMIT`: slow down; HubSpot rate limits per token.
- `crm-cli` exit 1 with `HubSpot API HTTP <code>: <message>` (human) or `{"ok": false, "error": "..."}` (JSON). Exit 2 is a usage error.

## Credential hygiene

- Private app tokens are full object-scope credentials: store in `HUBSPOT_TOKEN`, never in code, chat, or commits. Scope tokens to the objects the task needs and rotate on leak.
- Personal data (emails, names, amounts) lives in CRM records; quote only what the question needs and never dump full records into chat.
