# RFD Incident Data Reference

## Data Sources

The `fire` command group resolves two stable ArcGIS item IDs at runtime:

| Source Key | Item ID | Title | Coverage |
|-----------|---------|-------|----------|
| `full-history` | `ea466e39e9ca4448b645c33a0d6c60ad` | Fire Incidents | Full public history, 2007–present |
| `past-month` | `c983765e304a41d19087c8d95aa46d54` | Fire Incidents Past Month | Rolling past month |

## Item Resolution

Item IDs are resolved to service URLs via:

```
https://ral.maps.arcgis.com/sharing/rest/content/items/{item_id}?f=json
```

The returned `url` field is then resolved to a queryable layer via `arcgis.resolve_queryable_layer()`.

## Field Schemas

### full-history (Fire Incidents)

| Field | Type | Description |
|-------|------|-------------|
| `incident_number` | String | Incident Number |
| `incident_type` | Single | Legacy NFIRS incident type code (pre-2026) |
| `incident_type_description` | String | Legacy incident description (pre-2026) |
| `incident_group_name` | String | Incident Group (2026+) |
| `incident_subgroup_code` | String | Incident Subgroup (2026+) |
| `incident_type_name` | String | Incident Type name (2026+) |
| `dispatch_date_time` | Date | Dispatch Date |
| `arrive_date_time` | Date | Arrival Date |
| `cleared_date_time` | Date | Cleared Date |
| `exposure` | Integer | Exposure |
| `platoon` | String | Platoon |
| `station` | Integer | Station |
| `address` | String | Address |
| `GlobalID` | GlobalID | GlobalID |

### past-month (Fire Incidents Past Month)

| Field | Type | Description |
|-------|------|-------------|
| `incident_number` | String | Incident Number |
| `incident_group_name` | String | Incident Group |
| `incident_subgroup_code` | String | Incident Subgroup |
| `incident_type_name` | String | Incident Type name |
| `dispatch_date_time` | Date | Dispatch Date |
| `arrive_date_time` | Date | Arrival Date |
| `cleared_date_time` | Date | Cleared Date |
| `platoon` | String | Platoon |
| `station_name` | String | Station Name (e.g. `Station 09`) |
| `address` | String | Address |
| `GlobalID` | GlobalID | GlobalID |

The past-month feed carries only the current classification fields and uses `station_name` instead of the integer `station`.

## 2026 Classification Schema Transition

RFD deprecated `incident_type` and `incident_type_description` for new records after January 1, 2026. They are replaced by `incident_group_name`, `incident_subgroup_code`, and `incident_type_name`. The cutover is clean: the last legacy record is `25-062155` (2025-12-31) and the first current record is `26-000001` (2026-01-01). Records do not populate both field sets.

### Normalization rules

Every feature carries stable derived keys alongside the preserved raw fields:

| Derived Key | Source (current era) | Source (legacy era) |
|-------------|---------------------|---------------------|
| `_classification_era` | `current` | `legacy` (or `unknown` when neither set is populated) |
| `_incident_group` | `incident_group_name` | not mapped (never fabricated from legacy codes) |
| `_incident_subgroup` | `incident_subgroup_code` | not mapped |
| `_incident_type` | `incident_type_name` | `incident_type_description` |
| `_incident_code` | not populated | `incident_type` (legacy NFIRS code) |
| `_station` | parsed from `station_name` (`Station 09` → 9) | integer `station` |

- Empty and whitespace-only strings are treated as missing.
- Pre-2026 records retain their available historical classification; no cross-era code-to-group mapping is invented.
- If a record ever populates both field sets (schema drift), the replacement fields win and the era is reported as `current`. Raw fields are always preserved in JSON output.
- `_station` is `null` when neither field carries a usable value.

## Filter Field Mapping

| Durable Filter | full-history | past-month |
|---------------|--------------|------------|
| `--since` (date) | `dispatch_date_time >= TIMESTAMP '…'` | `dispatch_date_time >= TIMESTAMP '…'` |
| `--station` | `station = N` (integer) | `station_name` matched as `Station NN` (zero-padded and bare) |
| `--platoon` | `UPPER(platoon) = 'X'` | `UPPER(platoon) = 'X'` |
| `--group` | `UPPER(incident_group_name) LIKE '%X%'` | `UPPER(incident_group_name) LIKE '%X%'` |
| `--type` | `incident_type_name` OR `incident_type_description` substring, plus exact `incident_type = N` when the value is numeric | `incident_type_name` substring |

Date filters use ArcGIS `TIMESTAMP` literals because these layers reject bare epoch-millisecond literals. The `--group` filter only matches 2026+ records (the field is null before the transition). The `--station` filter on `full-history` only matches records whose integer `station` is populated (mostly 2007 through early 2021); use `--source past-month` for current station data.

## Response-Time Calculations

`fire response-times` derives three durations per record, in seconds, from the raw timestamp fields:

| Derived Key | Pair |
|-------------|------|
| `_dispatch_to_arrive_seconds` | `dispatch_date_time` → `arrive_date_time` |
| `_arrive_to_clear_seconds` | `arrive_date_time` → `cleared_date_time` |
| `_dispatch_to_clear_seconds` | `dispatch_date_time` → `cleared_date_time` |

Each pair is validated independently and carries a `_…_status` key:

| Status | Meaning |
|--------|---------|
| `ok` | both timestamps valid; duration computed in seconds |
| `missing_timestamp` | one or both timestamps absent |
| `malformed_timestamp` | a timestamp is non-numeric, negative, or non-finite |
| `reversed_timestamps` | the end timestamp precedes the start |

Invalid pairs yield `null`, never a fabricated or zeroed duration. Older full-history records commonly have null timestamps and are excluded from any duration summary.

## Privacy and Data Caveats

- **RFD excludes incident types 300–399 and 661 from this public feed for EMS/privacy reasons.** The feed is not a complete record of all fire department responses.
- **This data must not be used for emergency response.** It is read-only public data that may lag the live system.
- **The past-month feed is a rolling window.** Records age out after roughly a month; use `full-history` for durable history.
- **Empty coordinates are suppressed.** Records with null or `(0,0)` geometry are returned with `geometry: null`.

## Duration Format

The `--since` flag accepts `<positive-integer><unit>`:

| Unit | Meaning | Example |
|------|---------|---------|
| `h` | Hours | `24h` |
| `d` | Days | `7d` |
| `w` | Weeks | `2w` |
| `y` | Years (365 days) | `1y` |

## JSON Output Enrichment

Every feature in JSON output includes:

| Property | Description |
|----------|-------------|
| `_source` | Source key: `full-history` or `past-month` |
| `_item_id` | ArcGIS item ID |
| `_retrieved_at` | ISO-8601 UTC timestamp of the query |
| `_classification_era` | One of: `current`, `legacy`, `unknown` |
| `_incident_group` | Normalized incident group (2026+ only) |
| `_incident_subgroup` | Normalized incident subgroup (2026+ only) |
| `_incident_type` | Normalized incident type label |
| `_incident_code` | Legacy NFIRS code (pre-2026 only) |
| `_station` | Normalized station number or null |

With `fire response-times`, each feature also includes the `_…_seconds` and `_…_status` keys above. The top-level FeatureCollection includes a `_sources` array with `item_id`, `label`, and `caveats` for the source used.
