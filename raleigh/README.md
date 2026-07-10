# Raleigh Open Data — City of Raleigh Public Data

Query, search, and download public datasets from the City of Raleigh Open Data portal. Access 200+ datasets — crime reports, food inspections, building permits, bike lanes, parks, zoning, traffic, budgets, and more.

## Why Install This Skill

When your agent loads this skill, it becomes a **Raleigh civic data specialist**. That means:

- **Discover datasets** — catalog, search, and browse 200+ datasets
- **Query with filters** — SQL-like WHERE clauses on city data
- **Download in multiple formats** — CSV, GeoJSON, JSON
- **Understand schema** — inspect field names, types, and sample data before querying
- **No API key required** — all data is publicly available

## What You Get

| Directory | Purpose |
|-----------|---------|
| `SKILL.md` | Complete command reference with examples |
| `scripts/raleigh` | Python CLI for the ArcGIS REST API |
| `references/` | Dataset catalog and category reference |

## Quick Start

```bash
raleigh search "food inspection"
raleigh query "Food Inspections" --where "SCORE < 70"
raleigh download "Raleigh Dog Parks" -f csv -o dog_parks.csv
```

## Triggers

Load this for any City of Raleigh data — crime, food inspections, permits, zoning, traffic, parks, or budgets.

## Requirements

Python 3.8+ with `requests` library. No API key required.
