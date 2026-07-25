# RPD Incident Data Reference

## Data Sources

The `police` command group resolves four stable ArcGIS item IDs at runtime:

| Source Key | Item ID | Title | Coverage |
|-----------|---------|-------|----------|
| `nibrs` | `24c0b37fa9bb4e16ba8bcaa7e806c615` | Raleigh Police Incidents (NIBRS) | June 2014–present |
| `srs` | `09af62a32ae8436bae6eda74aa7f172b` | Raleigh Police Incidents (SRS) | 2005–May 2014 |
| `previous-day` | `693811eb361f4da286891eca1fae5943` | Daily Raleigh Police Incidents | Previous day |
| `crimemapper-90d` | `a1f2d9204a184404b5a4c7e0fdceb6d0` | Raleigh Police Department Crime Incidents - Past 90 Days | Rolling 90 days |

## Item Resolution

Item IDs are resolved to service URLs via:

```
https://ral.maps.arcgis.com/sharing/rest/content/items/{item_id}?f=json
```

The returned `url` field is then resolved to a queryable layer via `arcgis.resolve_queryable_layer()`.

## Field Schemas

### NIBRS, CrimeMapper-90d, Previous-day (shared schema)

| Field | Type | Description |
|-------|------|-------------|
| `case_number` | String | Case Number |
| `crime_category` | String | Crime Category |
| `crime_code` | String | Crime Code |
| `crime_description` | String | Crime Description |
| `crime_type` | String | Crime Type |
| `reported_block_address` | String | Reported Block Address |
| `city` | String | City |
| `district` | String | District |
| `reported_date` | Date | Reported Date |
| `reported_year` | Integer | Reported Year |
| `reported_month` | Integer | Reported Month |
| `reported_day` | Integer | Reported Day |
| `reported_hour` | Integer | Reported Hour |
| `reported_dayofwk` | String | Reported Day of Week |
| `latitude` | Double | Latitude |
| `longitude` | Double | Longitude |
| `agency` | String | Agency |

### SRS (legacy schema)

| Field | Type | Description |
|-------|------|-------------|
| `LCR` | String | LCR Code |
| `LCR_DESC` | String | LCR Description (incident type) |
| `INC_DATETIME` | Date | Incident Date |
| `INC_NO` | String | Incident # |
| `DISTRICT` | String | District |

## Filter Field Mapping

| Durable Filter | NIBRS / CrimeMapper / Previous-day | SRS |
|---------------|-----------------------------------|-----|
| `--category` | `crime_description` | `LCR_DESC` |
| `--district` | `district` | `DISTRICT` |
| `--since` (date) | `reported_date` | `INC_DATETIME` |

## Privacy and Data Caveats

- **Locations are block-level and may be randomized or redacted.** The RPD randomizes locations to the general neighborhood area. Sexual assault, child abuse, juvenile, domestic abuse, and related incidents have all location information redacted.
- **This data does not include arrests, convictions, or dispositions.** Each row represents a report made by a police officer; not all reports result in arrests or convictions.
- **Empty coordinates are suppressed.** Records with null or `(0,0)` geometry are returned with `geometry: null` and `_location_status: "redacted"`.
- **The CrimeMapper 90-day feed is not in the curated Hub catalog.** It is resolved directly by item ID.
- **The previous-day feed may lag.** It may be empty on some days due to pipeline delays.

## Duration Format

The `--since` flag accepts `<positive-integer><unit>`:

| Unit | Meaning | Example |
|------|---------|---------|
| `h` | Hours | `24h` |
| `d` | Days | `7d` |
| `w` | Weeks | `2w` |

## JSON Output Enrichment

Every feature in JSON output includes:

| Property | Description |
|----------|-------------|
| `_source` | Source key: `nibrs`, `srs`, `previous-day`, or `crimemapper-90d` |
| `_item_id` | ArcGIS item ID |
| `_retrieved_at` | ISO-8601 UTC timestamp of the query |
| `_location_status` | One of: `block_level`, `redacted`, `out_of_area`, `unknown` |

The top-level FeatureCollection includes a `_sources` array with `item_id`, `label`, and `caveats` for each source used.
