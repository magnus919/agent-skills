# Raleigh Open Data — City of Raleigh Public Data

Query, search, and download public datasets and civic information for the City of Raleigh. Discover live ArcGIS Hub datasets, query FeatureServer and MapServer layers, export imagery, geocode addresses, read transit feeds, search public development and fire records, browse RaleighNC.gov content, and extract public meetings.

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
- **Active incidents** — live RWECC public incident feed (undocumented endpoint, clearly labeled)
- **Fire protection** — Wake County MAR station proximity, ISO ratings, and hydrant distances
- **Fire records** — authoritative ArcGIS report summaries plus guarded RFD narratives and inspection searches
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
scripts/raleigh incidents active --agency raleigh-fire
scripts/raleigh fire protection --address "222 W Hargett St"
scripts/raleigh fire reports --date 2026-07-24
# RFD has no usable TLS endpoint; this sends the search term over plain HTTP.
scripts/raleigh fire inspections --business "Example" --acknowledge-insecure-rfd
```

## Triggers

Load this for any City of Raleigh civic data — crime, food or fire inspections, fire reports, permits, zoning, traffic, parks, budgets, transit, news, events, or public meetings.

## Requirements

Python 3.10+. All static features use only the Python standard library. GTFS-Realtime vehicle positions, trip updates, and alerts require the optional `protobuf` runtime (`google.protobuf>=6.31.1,<7`); a vendored binding generated with protoc 31.1 supplies message definitions, but it does not replace the runtime. No API key required.

## Testing

Run the deterministic unit suite from the repository root:

```bash
python3 -m unittest raleigh/tests/test_raleigh.py
```

## Eval Suite

The Raleigh skill ships executable eval cases in `evals/evals.json` that grade agent output quality — not just CLI correctness. Cases cover public-safety data provenance, privacy language, stale-endpoint detection, dispatch disclaimer, empty-feed handling, and security refusal.

Run the paired eval pipeline (fake adapter, no model needed):

```bash
python3 -m eval_runner.paired raleigh/evals/evals.json --adapter fake --output-dir eval-output/raleigh
```

Run with a real model (requires an OpenAI-compatible endpoint):

```bash
python3 -m eval_runner.paired raleigh/evals/evals.json \
  --adapter openai \
  --base-url http://localhost:8080 \
  --model your-model-id \
  --output-dir eval-output/raleigh
```

Assertions use deterministic graders (`response_contains:`, `response_not_contains:`, `exit_status:`, `activation_evidence_contains:`). A candidate that cites a stale endpoint, deprecated field, or unsupported completeness claim fails. Infrastructure errors (timeout, crash) are reported separately from skill-quality failures.

## Safety Notes

All operations are read-only against fixed public endpoints. The general client enforces HTTPS. The isolated RFD adapter permits only four fixed plain-HTTP contracts after per-invocation acknowledgement, rejects empty searches and redirects, and never follows or exposes invoice links. Authentication, payment, submission, bulk crawling, and private-data endpoints are unsupported.
