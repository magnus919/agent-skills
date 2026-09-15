# Guide plan contract

Use this small record for multi-file guides. Keep it beside the participant and
facilitator materials; paths resolve from its directory. It coordinates records,
not prose generation. Do not require participants to edit it.

The checker accepts JSON with the following required fields:

```json
{
  "schema_version": 1,
  "title": "A community program",
  "modules": [{
    "id": "practice",
    "title": "Practice a handoff",
    "duration_minutes": 30,
    "activities": [{"title": "Exercise and debrief", "minutes": 30}],
    "worksheet_ids": ["handoff"]
  }],
  "worksheets": [{"id": "handoff", "path": "handoff.md"}],
  "materials": {"participant": "guide.md", "facilitator": "host.md"},
  "maintenance": {
    "owner": "Workshop host",
    "status": "proposed",
    "review_date": "2027-01-15"
  },
  "sources": [{
    "id": "brief",
    "locator": "Supplied community brief, section 1",
    "checked_on": "2026-09-15",
    "status": "supplied"
  }]
}
```

IDs must be unique within their list; titles and other text fields nonblank.
Module and activity durations are positive integer minutes. The activities must
fit the module duration. Modules and activity lists cannot be empty. Worksheets and sources may be
empty when unnecessary. Every worksheet reference must resolve to a worksheet ID.
Every material/worksheet path must name an existing file inside the plan folder,
including after symlink resolution. Absolute paths, backslashes, and parent traversal are invalid.
Dates are real ISO calendar dates. Source status is `verified`, `supplied`, or
`unresolved`; maintenance status is `proposed` or `confirmed`.

The read-only CLI emits `valid`, `errors`, and `warnings` as JSON. Exit codes are
0 for structurally valid, 1 for invalid records, and 2 for unreadable/malformed
input. Unresolved sources and proposed maintenance ownership produce warnings.

Validation does not establish that a source is current, an owner accepted a role,
translations are accurate, the host notes match the prose, or participants can
use the guide. Check those separately and report the evidence.
