# Raleigh Open Data — City of Raleigh Public Data

Query, search, and download public datasets and civic information for the City of Raleigh. Discover live ArcGIS Hub datasets, query FeatureServer and MapServer layers, export ImageServer imagery, geocode addresses, read GoRaleigh transit feeds, search guest-public development records, browse RaleighNC.gov content, and extract eSCRIBE public meetings.

## Why Install This Skill

When your agent loads this skill, it becomes a **Raleigh civic data specialist**. That means:

- **Live dataset discovery** — search a current catalog instead of a stale embedded list
- **Query with filters** — SQL-like WHERE clauses on city data
- **Export in multiple formats** — CSV, GeoJSON, JSON
- **Imagery** — export bounded orthophotos and identify pixel values
- **Geocoding** — use Raleigh's official address locator
- **Transit** — static GTFS schedules and GTFS-Realtime positions/alerts
- **Development records** — guest-public searches in the Permit and Development Portal
- **Civic content** — news, events, projects, services, directory entries, and alerts from RaleighNC.gov
- **Public meetings** — agendas, minutes, and videos from eSCRIBE
- **No API key required** — all data is publicly available

## What You Get

| Directory | Purpose |
|-----------|---------|
| `SKILL.md` | Command reference and safety boundaries |
| `scripts/raleigh` | Executable Python CLI |
| `scripts/raleighlib/` | Modular implementation package |
| `tests/` | Deterministic unit tests and fixtures |
| `references/` | Endpoint contracts and detailed guides |
| `EVIDENCE-LEDGER.md` | Verified commands and boundary notes |

## Quick Start

Run the CLI from the skill directory:

```bash
scripts/raleigh search "food inspection"
scripts/raleigh info "Food Inspections" --json
scripts/raleigh query "Food Inspections" --where "SCORE < 70"
scripts/raleigh download "Raleigh Dog Parks" -f csv -o dog_parks.csv
scripts/raleigh geocode "222 W Hargett St"
scripts/raleigh transit routes
scripts/raleigh news --limit 5
```

## Triggers

Load this for any City of Raleigh civic data — crime, food inspections, permits, zoning, traffic, parks, budgets, transit, news, events, or public meetings.

## Requirements

Python 3.10+. All static features use only the Python standard library. GTFS-Realtime vehicle positions, trip updates, and alerts require the optional `protobuf` runtime (`google.protobuf>=6.31.1,<7`); a vendored binding generated with protoc 31.1 supplies message definitions, but it does not replace the runtime. No API key required.

## Safety Notes

All operations are read-only against public endpoints. The CLI enforces a fixed allowlist of service hosts and never calls authentication, payment, submission, or private-data endpoints.
