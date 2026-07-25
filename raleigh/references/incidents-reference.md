# Active Incidents (RWECC) Reference

## Source

- Public map: https://incidents.rwecc.com/
- JSON endpoint: `GET https://incidents.rwecc.com/getdata`
- Publisher: Raleigh-Wake Emergency Communications Center (RWECC)
- Contract: **Undocumented application endpoint** — not a versioned public API.

## Schema (observed 2026-07)

The endpoint returns a JSON array of objects:

```json
[
  {
    "jurisdiction": "Raleigh Police Department",
    "problem": "MVC - Fatal",
    "address": "Blue Ridge Rd / Macon Pond Rd",
    "lat": 35.81933,
    "long": -78.704862,
    "timestamp": "2026-07-24 22:28:54.000"
  }
]
```

| Field | Type | Notes |
|-------|------|-------|
| `jurisdiction` | string | Agency name (e.g. "Raleigh Police Department", "Raleigh Fire Department") |
| `problem` | string | Incident type or classification |
| `address` | string | Block-level or intersection; may be approximate |
| `lat` | float or null | WGS84 latitude; may be absent |
| `long` | float or null | WGS84 longitude; may be absent |
| `timestamp` | string | `YYYY-MM-DD HH:MM:SS.mmm` (observed; timezone unconfirmed) |

## Schema guard

The adapter validates every record before inclusion:

- `jurisdiction` and `problem` must be non-empty strings.
- `lat`/`long` are nulled if non-numeric, boolean, or out of range.
- Non-dict records are silently skipped with a warning count.
- Duplicate records (same jurisdiction + problem + address + timestamp) are deduplicated.
- If the top-level response is an object instead of a list, the adapter raises `IncidentFeedError` (schema drift).

## Caching

- Cache key: `incidents-rwecc-active.json`
- TTL: 90 seconds
- Bypass: `--no-cache` flag or `use_cache=False`

## Disable switch

```bash
export RALEIGH_DISABLE_INCIDENTS=1
```

When set, all `incidents` commands raise `IncidentFeedError` immediately without network I/O.

## Provenance requirements

Every response (JSON and human) must:

1. Identify the source as an undocumented, filtered public incident feed.
2. Include retrieval time.
3. State this is NOT all 911 calls and NOT authoritative emergency status.
4. Warn distinctly on empty, stale, malformed, or unavailable responses.
5. Never represent an empty feed as proof of no incidents.

## Known agencies

- Raleigh Police Department
- Raleigh Fire Department

The `--agency` flag normalizes hyphens to spaces and matches by substring.
