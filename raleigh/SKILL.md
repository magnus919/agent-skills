---
name: raleigh
description: >-
  Query, search, and download public datasets from the City of Raleigh Open Data
  portal. Use this whenever someone wants to explore city data — crime reports,
  food inspections, building permits, bike lanes, parks, zoning, traffic,
  budgets, or any of 200+ public datasets.
license: MIT
metadata:
  source: https://data.raleighnc.gov
  author: Jasper
  datasets: "198+"
---

# Raleigh Open Data

A CLI tool for the City of Raleigh's open data portal (data.raleighnc.gov). Wraps the ArcGIS REST API to discover, query, and download from 200+ public datasets — all read-only, no API key needed.

## Quick Start

```bash
# List all datasets
raleigh catalog

# Search for specific data
raleigh search "food inspection"

# Show a dataset's schema
raleigh info "Food Inspections"

# Query records with filters
raleigh query "Food Inspections" --where "SCORE < 70"

# Download a dataset
raleigh download "Raleigh Dog Parks" -f csv -o dog_parks.csv
```

## Commands

| Command | Purpose | Example |
|---------|---------|---------|
| `catalog` | List all datasets | `raleigh catalog --category Transportation` |
| `search` | Search datasets by keyword | `raleigh search "building permit" --limit 5` |
| `info` | Show dataset schema + sample | `raleigh info "Raleigh Dog Parks"` |
| `query` | Query records with filters | `raleigh query "Food Inspections" --where "SCORE<70" --limit 20` |
| `download` | Export to a file | `raleigh download "Parcels" -f geojson -o parcels.geojson` |
| `categories` | List data categories | `raleigh categories` |

## Global Flags

| Flag | Effect |
|------|--------|
| `--json` | JSON output instead of table |
| `--csv` | CSV output |
| `--quiet` | Suppress extra messages |
| `--server URL` | Override API server |

## References

| Reference | Load when | File |
|-----------|-----------|------|
| Full dataset catalog | Browsing what's available | `references/dataset-catalog.md` |
| API reference | Building custom queries or using the API directly | `references/api-reference.md` |

## Pitfalls

- **Date values** from ArcGIS are Unix timestamps in milliseconds. Divide by 1000 for standard timestamps.
- **MapServer Table layers** have no geometry (`type: "Table"`). Always use `returnGeometry=false`.
- **String values in WHERE** must use single quotes: `WHERE NAME='Millbrook-Exchange'`
- **Rate limits** are undocumented but generous. Add `--limit` to keep queries responsive.
- **Some datasets** have multiple layers (e.g., Building Permits exists on both Raleigh and Wake County servers). The CLI picks the best match or lists options.
