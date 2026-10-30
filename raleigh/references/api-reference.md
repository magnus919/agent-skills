# ArcGIS REST API Reference

The Raleigh Open Data portal is built on ArcGIS Hub and exposes datasets through standard ArcGIS REST API endpoints.

## Live Catalog Discovery

The CLI discovers the current catalog from the ArcGIS Hub Search API:

```text
https://data.raleighnc.gov/api/search/v1/collections/{collection}/items?startindex={startindex}&limit={limit}
```

Collections: `dataset`, `document`, `appAndMap`.

The CLI paginates through each collection, normalizes records, caches the result, and validates canonical URLs on demand.

Verified constraints:

- `startindex` is 1-based. `startindex=0` returns HTTP 400 `searchOptions.startindex must not be less than 1`.
- The search endpoint rejects an explicit `f` parameter. Sending `f=json` returns HTTP 400 with `The following provided filters are invalid queryables: ('f')`. Do not append `f=json` to Hub search URLs; the response is always JSON.
- Paginate with `limit` up to 100 and compare accumulated records against `numberMatched`; treat a short page as the end rather than assuming a fixed total.

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
- Layer `0` is not always the layer you want. Resolve the layer id from the service root (`/FeatureServer?f=json` → `layers`) before querying.

## Host-Specific Quirks

### `raleighnc.gov` requires a curl/Wget user agent

The main website and its `/jsonapi`, `/rss.xml`, and article pages sit behind a Cloudflare managed challenge that inspects the `User-Agent` header:

| User agent | Result |
|------------|--------|
| `curl/8.7.1 (compatible; RaleighCivicDataCLI/2.0)` | 200 |
| `curl/8.7.1` | 200 |
| `Wget/1.21` | 200 |
| `Curl/8.7.1` (capital C by request library) | 403 `cf-mitigated: challenge` |
| `Python-urllib/3.x` | 403 |
| `Mozilla/5.0 …` | 403 |

Only a user agent that *begins* with the lowercase token `curl` or with `Wget` passes; suffixes are allowed. `raleighlib.core` sends `TOOL_USER_AGENT` (`curl/8.7.1 (compatible; RaleighCivicDataCLI/2.0; read-only public data)`) to `raleighnc.gov` and the descriptive `USER_AGENT` everywhere else. A 403 with `cf-mitigated` is a user-agent rejection, not an outage or a missing page.

### ImageServer geometry ignores `inSR`

`identify` and `computeStatisticsHistograms` on `maps.raleighnc.gov` return `{"value": "NoData"}` or time out when the spatial reference is supplied only as the `inSR`/`sr` query parameter. Embed it in the geometry JSON instead:

```json
{"x": -78.65, "y": 35.75, "spatialReference": {"wkid": 4326}}
```

The same rule applies to envelopes for statistics. The service then reports coordinates in its native `102719`/`2264` (NC State Plane Feet) frame; convert with `outSR=4326` if you need lon/lat.

### `format=jpgpng` may return JPEG or PNG bytes

`exportImage?format=jpgpng` lets the server choose the cheaper encoding, so the response body may be either. Request `format=png`, `jpg`, or `tiff` when the bytes matter, and check magic bytes rather than trusting the `Content-Type` header. The CLI infers the requested format from the output file extension (`.png` → `png`, `.jpg`/`.jpeg` → `jpg`, `.tif`/`.tiff` → `tiff`) and falls back to `jpgpng` with a warning for unknown extensions.

