---
type: <Type name>                         # REQUIRED — e.g. "BigQuery Table", "Metric", "Playbook", "API Endpoint"
title: <Human-readable display name>      # Recommended
description: <One-line summary>           # Recommended — used in index.md entries and search snippets
resource: <Canonical URI>                 # Optional — URL for the underlying asset
tags: [<tag1>, <tag2>]                    # Optional — cross-cutting categorization
timestamp: <YYYY-MM-DDThh:mm:ssZ>         # Optional — ISO 8601 last-modified time
---

# Concept Title

A short paragraph explaining what this concept is and why it matters. What problem does it solve? When would someone reach for this?

## Schema

If this concept describes a structured asset (table, API, dataset), document its fields here.

| Field | Type | Description |
|-------|------|-------------|
| `field_name` | TYPE | Description of the field |
| `foreign_key` | TYPE | FK to [related concept](/path/to/concept.md) |

## Examples

Usage examples as code blocks or scenarios.

```sql
SELECT field_name FROM table WHERE condition;
```

## References

* [Related concept 1](/path/to/concept-1.md)
* [Related concept 2](/path/to/concept-2.md)

## Citations

[1] [External source](https://example.com)
