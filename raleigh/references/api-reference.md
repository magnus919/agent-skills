# ArcGIS REST API Reference

The Raleigh Open Data portal is built on ArcGIS Hub and exposes datasets through standard ArcGIS REST API endpoints.

## Live Catalog Discovery

The CLI discovers the current catalog from the ArcGIS Hub Search API:

```text
https://data.raleighnc.gov/api/search/v1/collections/{collection}/items?startindex={startindex}&limit={limit}
```

Collections: `dataset`, `document`, `appAndMap`.

The CLI paginates through each collection, normalizes records, caches the result, and validates canonical URLs on demand.

## Layer Info

Get metadata about a specific layer:

```text
{serviceUrl}?f=json
```

For FeatureServer:

```text
https://services.arcgis.com/v400IkDOw1ad7Yad/arcgis/rest/services/DogParkLocations_Existing_PUBLIC/FeatureServer/0?f=json
```

For MapServer:

```text
https://maps.wake.gov/arcgis/rest/services/Inspections/RestaurantInspectionsOpenData/MapServer/1?f=json
```

## Query Records

```text
{serviceUrl}/query?where={where}&outFields={fields}&returnGeometry={true|false}&f={format}&resultRecordCount={limit}&resultOffset={offset}&orderByFields={fields}&outSR=4326
```

| Parameter | Description | Example |
|-----------|-------------|---------|
| `where` | SQL WHERE clause | `1=1`, `SCORE<70` |
| `outFields` | Comma-separated field names | `*`, `SITE,ADDRESS` |
| `returnGeometry` | Include spatial data | `true`, `false` |
| `f` | Output format | `geojson`, `json`, `html` |
| `resultRecordCount` | Max records per request | `10`, `1000` |
| `resultOffset` | Pagination offset | `0`, `1000` |
| `orderByFields` | Sort fields | `SCORE DESC` |
| `outSR` | Output spatial reference | `4326` |

## Export Formats

| Format | Parameter | Use Case |
|--------|-----------|----------|
| GeoJSON | `f=geojson` | Spatial data in standard format |
| JSON | `f=json` | Tabular/attribute data |
| HTML | `f=html` | Human-readable table |

## Notes

- All endpoints are public; no API key is required.
- Dates are returned as Unix timestamps in milliseconds.
- `returnGeometry=false` is faster for tabular queries.
- MapServer layers with `type: "Table"` have no geometry.
- String values in WHERE must be single-quoted.
