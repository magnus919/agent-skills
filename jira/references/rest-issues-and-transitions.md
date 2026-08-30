# Jira Cloud REST API v3 — Issues, Transitions & ADF

Field-level semantics for the issue lifecycle: reading, creating, editing, commenting, and — the part everyone gets wrong — transitioning. Plus the Atlassian Document Format rules that decide whether your payload is accepted at all.

## Reading Issues

`GET /rest/api/3/issue/{issueIdOrKey}`

- Query params: `fields`, `fieldsByKeys`, `expand`, `properties`, `updateHistory`, `failFast`.
- Default response includes all navigable fields. Trim with `?fields=summary,status,assignee` — faster pages, less noise.
- Non-matching keys get a case-insensitive lookup plus moved-issue check; a found match returns directly (no redirect).
- Response top level: `{id, key, self, fields:{...}}`.

Field access patterns:

```json
{
  "fields": {
    "summary": "Main order flow broken",
    "status": {"name": "In Progress", "statusCategory": {"key": "in-flight"}},
    "issuetype": {"name": "Bug"},
    "priority": {"name": "High"},
    "assignee": {"accountId": "5b10a2844c20165700ede21g", "displayName": "Mia Krystof"},
    "reporter": {"accountId": "...", "displayName": "..."},
    "created": "2019-04-05T10:30:00.000+1000",
    "updated": "2024-01-11T08:15:00.000+0000",
    "description": {"type": "doc", "version": 1, "content": []}
  }
}
```

Gotchas:

- `assignee`/`reporter` may be `null` (unassigned) — null-check before `.displayName`.
- `description` is an ADF object, not text (see ADF section).
- User identity is `accountId` everywhere; `username`/`userKey` were removed in the GDPR migration (April 2019). Email visibility depends on each user's privacy settings.

## Creating Issues

`POST /rest/api/3/issue` with body root keys `fields`, `update`, `historyMetadata`, `properties`, `transition`. Only `fields` matters for basic creation.

```json
{
  "fields": {
    "project":   { "key": "EX" },
    "summary":   "Order entry fails when selecting supplier.",
    "issuetype": { "name": "Bug" },
    "description": {
      "type": "doc", "version": 1,
      "content": [ { "type": "paragraph", "content": [ { "type": "text", "text": "Steps to reproduce..." } ] } ]
    },
    "priority":  { "name": "High" },
    "labels":    ["bugfix"],
    "parent":    { "key": "PROJ-123" }
  }
}
```

Rules:

- Project by `{"key": ...}` or `{"id": ...}`; issuetype by name or id.
- `description`, `environment`, and any `textarea`-type custom fields **require ADF objects**; plain strings are rejected. Single-line `textfield` custom fields take plain strings.
- Users are addressed as `assignee: {"accountId": "..."}` or `{"id": "<accountId>"}`.
- Success: 201 with `{id, key, self}` (+ optional transition echo).
- Failure: 400/422 with the error collection; `errors` map names the offending field ("Project 'XYZ' does not exist or you do not have permission...").

## Editing Issues

`PUT /rest/api/3/issue/{issueIdOrKey}`

```json
{ "fields": { "summary": "Completed orders still displaying in pending",
              "labels": ["bugfix", "triage"] } }
```

- Fields sit under `fields` (or granular ops under `update`, e.g. array field manipulation).
- Success is **204 No Content** — an empty response body means it worked; don't parse for confirmation JSON.
- Transitions are ignored on this endpoint; changing status requires the transitions endpoint below.
- Suppress notification emails with query param `notifyUsers=false` (bulk edits especially).

Deleting: `DELETE /rest/api/3/issue/{key}` refuses when subtasks exist unless you pass `deleteSubtasks=true`; success is 204.

## Comments

`GET /rest/api/3/issue/{key}/comment?startAt=0&maxResults=50` → `{comments: [...], startAt, maxResults, total}` (offset paging, like legacy search).

Each comment: `{id, author:{accountId, displayName}, body: <ADF>, created, updated, updateAuthor}`.

Add one: `POST /rest/api/3/issue/{key}/comment` with `{"body": {ADF doc}}`. The body must be an ADF object — a bare string fails with a 400/500-class error naming the wrong type.

## Transitions: GET First, Then POST

This is the highest-friction endpoint pair in Jira integration work. Two calls are always required because **transition IDs differ per workflow, per project, and per current status**, and names alone are ambiguous across workflows.

### Step 1 — discover available transitions

`GET /rest/api/3/issue/{key}/transitions?expand=transitions.fields`

```json
{
  "transitions": [
    {
      "id": "31",
      "name": "Done",
      "hasScreen": true,
      "isGlobal": false,
      "isConditional": false,
      "to": { "name": "Done", "statusCategory": {"key": "completed"} },
      "fields": {
        "resolution": { "required": true, "allowedValues": [{"name": "Done"}, {"name": "Fixed"}] },
        "comment": { "required": false }
      }
    }
  ]
}
```

Reading this shape:

- `id` is the string you POST back. Never hardcode it across projects.
- `to.statusCategory.key` (`to-do` / `in-flight` / `completed`) is the stable way to find "the Done-ish transition" without knowing its display name.
- With `expand=transitions.fields`, `fields` lists what the target screen demands and each field's `required` flag plus `allowedValues`.
- Asking for a nonexistent or status-invalid transition yields an **empty list**, not an error.

### Step 2 — apply the transition

`POST /rest/api/3/issue/{key}/transitions`

Minimal payload:

```json
{ "transition": { "id": "31" } }
```

Setting fields during the move (resolution, assignee, comments ride along):

```json
{
  "transition": { "id": "31" },
  "fields": { "resolution": { "name": "Fixed" } },
  "update": {
    "comment": [ { "add": { "body": { "type": "doc", "version": 1,
      "content": [ { "type": "paragraph", "content": [ { "type": "text", "text": "Shipped in build 47" } ] } ] } } } ]
  }
}
```

Semantics that bite:

- Success is **204 No Content**.
- If the target screen marks a field `required: true` and you omit it — classically `resolution` on a Done transition — you get **400** with `"errors": {"resolution": "..."}` naming the missing field. Pre-read the fields map from step 1 instead of guessing.
- `resolution` values come from `allowedValues`; sending `{"name": "Done"}` where the site expects `"Fixed"` fails validation.
- Transition names repeat across workflows; IDs do not. Resolve by ID after discovery, optionally filtering by `to.statusCategory.key`.

### Worked recipe: bulk-close stalled sprint issues

```python
# 1) find candidates (legacy search shown; see rest-auth-and-search.md for token paging)
issues = search('sprint in openSprints() AND updated < -14d AND resolution = Unresolved')

# 2) per issue: discover + apply
for issue in issues:
    trans = get(f"/issue/{issue['key']}/transitions")["transitions"]
    done = next(t for t in trans if t["to"]["statusCategory"]["key"] == "completed")
    post(f"/issue/{issue['key']}/transitions",
         json={"transition": {"id": done["id"]},
               "fields": {"resolution": {"name": "Done"}}})
```

Rate-limit note: writes count toward per-issue windows (20 per 2s) — sleep briefly between issues in loops.

## Atlassian Document Format (ADF)

The document model for every rich-text field in v3 payloads: issue `description`/`environment`, comment bodies, textarea custom fields. Plain-text strings are rejected for these fields.

### Minimal document

```json
{ "type": "doc", "version": 1,
  "content": [
    { "type": "paragraph",
      "content": [ { "type": "text", "text": "Hello world" } ] }
  ] }
```

Structure invariants: exactly one root `doc` with `version: 1`; content is an ordered tree of block nodes (`paragraph`, `heading`, `bulletList`/`orderedList` > `listItem` > `paragraph`, `codeBlock`, `panel`, `table`, `blockquote`); inline content is `text` nodes carrying optional `marks`.

### Formatting quick reference

| Effect | Node/mark shape |
|--------|-----------------|
| Bold | `{"type":"text","text":"world","marks":[{"type":"strong"}]}` |
| Italic | `marks: [{"type":"em"}]` |
| Code | `marks: [{"type":"code"}]` |
| Link | `marks: [{"type":"link","attrs":{"href":"https://..."}}]` |
| Bullet list | `bulletList` node whose `listItem`s contain paragraphs |
| Mention | inline node `{"type":"mention","attrs":{"id":"<accountId>"}}` |

### Practical guidance

- Building from user input? Wrap each line/paragraph as its own `paragraph` node; escape nothing manually — text goes in the `text` property verbatim.
- Extracting? Walk `content[]` recursively collecting `text` nodes' `text` values joined by newlines (the bundled CLI's `view` does this for descriptions).
- Round-tripping rich content through plain text loses formatting permanently; if fidelity matters, fetch the ADF and re-post the same structure.

## Sources

- Issues group (get/create/edit/delete, transitions GET+POST): https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issues/
- Issue comments group: https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-comments/
- Issue links group (link payload shapes): https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-links/
- Projects group (paginated vs deprecated bare-array): https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-projects/
- Myself resource: https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-myself/
- REST v3 intro (error collection schema): https://developer.atlassian.com/cloud/jira/platform/rest/v3/intro/
- ADF structure reference: https://developer.atlassian.com/cloud/jira/platform/apis/document/structure/
- GDPR accountId migration guide: https://developer.atlassian.com/cloud/jira/platform/deprecation-notice-user-privacy-api-migration-guide/
