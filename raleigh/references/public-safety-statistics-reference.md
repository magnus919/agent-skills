# Official Police and Fire Aggregate Statistics

## Source Contract

The aggregate commands make one HTTPS request to each official RaleighNC.gov Drupal service node with `include=field_content_primary`. The response contains the page metadata and published HTML fragments in structured JSON:API data.

| Agency | Official page | Stable service UUID |
|---|---|---|
| RPD | `https://raleighnc.gov/police/services/raleighs-crime-data` | `40ebbee4-2477-4f7d-9623-257685345e3d` |
| RFD | `https://raleighnc.gov/fire/services/view-raleigh-fire-statistics` | `f95a0f43-3dbf-4378-b7c7-b1bdda20eb24` |

The adapter verifies the node UUID, type, publication status, title, and canonical path. It then parses only named content sections. Missing sections, changed table headers, malformed values, unknown publication labels, unsupported link origins, unavailable years, and absent requested quarters fail visibly.

## Commands

```bash
# Omit --year to enumerate years from the current official page.
scripts/raleigh police stats
scripts/raleigh police stats --year 2025
scripts/raleigh police reports --year 2025 --quarter 4

scripts/raleigh fire stats
scripts/raleigh fire stats --year 2026
scripts/raleigh fire reports --year 2025 --quarter 1

# This remains the separate incident-report lookup mode.
scripts/raleigh fire reports --date 2026-07-24
```

## Output Contract

- `classification: official_published_statistics` identifies source-published aggregate values.
- `classification: official_published_reports` identifies publication-index results.
- Structured rows preserve year, dataset kind, label, parsed numeric value where applicable, the exact displayed value, source URL, page revision time, and retrieval time.
- Annual and quarterly reports preserve publication labels and canonical URLs. A bounded `HEAD` request verifies each returned document is available, but the CLI does not download or parse PDFs because no stable extraction contract has been established.
- A requested year with report links but no inline table succeeds with an explicit `document-only` warning. A year absent from the live index fails.

## Data Boundaries

These commands do not aggregate ArcGIS incident rows. Incident records, the filtered active-dispatch feed, and official aggregate reports are separate products with different coverage and privacy boundaries.

RFD's official aggregate table includes medical calls. The public incident feed excludes EMS-related types 300-399 and 661. The aggregate medical total must not be joined back to, apportioned across, or used to infer excluded incident-level records.

## Approved Links

Publication links are returned only when they remain on the official Raleigh page or the fixed City of Raleigh government-cloud document origin. The CLI verifies availability without downloading document contents.
