# ArcGIS REST API Reference

The Raleigh Open Data portal is built on ArcGIS Hub, exposing datasets through standard ArcGIS REST API endpoints.

## URL Patterns

### Dataset Discovery

Search the Raleigh catalog:

```
GET https://ral.maps.arcgis.com/sharing/rest/search
  ?q=group:7961306fe9cd49e3a0fb8f1cd1180798%20OR%20group:33b8fd49e9e64a3999daf98b697eeddd
  &f=json
  &num=100
  &sortField=title
  &sortOrder=asc
```

- `q`: Search query. Use `group:...` to search within a specific group, or `title:keyword` for title search.
- `f`: Output format (`json`, `html`, `geojson`)
- `num`: Results per page (max 100)
- `start`: Offset for pagination

### Layer Info

Get metadata about a specific layer, including field names, types, and aliases:

```
GET {serviceUrl}/{serviceType}/{layerId}?f=json
```

For FeatureServer (spatial services):
```
GET https://services.arcgis.com/v400IkDOw1ad7Yad/arcgis/rest/services/DogParkLocations_Existing_PUBLIC/FeatureServer/0?f=json
```

For MapServer (mapping services):
```
GET https://maps.wake.gov/arcgis/rest/services/Inspections/RestaurantInspectionsOpenData/MapServer/1?f=json
```

### Query Records

Query features from a layer with optional filters:

```
GET {serviceUrl}/{serviceType}/{layerId}/query
  ?where={whereClause}
  &outFields={fieldList}
  &returnGeometry={true|false}
  &f={format}
  &resultRecordCount={limit}
  &resultOffset={offset}
  &orderByFields={field1,field2}
  &outSR=4326
```

| Parameter | Description | Example |
|-----------|-------------|---------|
| `where` | SQL WHERE clause, URL-encoded | `1%3D1` (all), `SCORE%3C70` (score < 70) |
| `outFields` | Comma-separated field names | `*` (all), `SITE,ADDRESS` (specific) |
| `returnGeometry` | Include spatial data | `true` (default for FeatureServer), `false` |
| `f` | Output format | `geojson`, `json`, `html`, `kmz` |
| `resultRecordCount` | Max records to return | `10`, `100`, `1000` |
| `resultOffset` | Pagination offset | `0`, `100`, `200` |
| `orderByFields` | Sort fields | `SCORE DESC`, `DATE_ ASC` |
| `outSR` | Output spatial reference | `4326` (WGS84 lat/lng) |

### Export Formats

ArcGIS supports multiple export formats from the query endpoint:

| Format | `f=` Parameter | Use Case |
|--------|---------------|----------|
| GeoJSON | `geojson` | Spatial data in standard format |
| JSON | `json` | Tabular/attribute data |
| HTML | `html` | Human-readable table |
| KMZ | `kmz` | Google Earth import |

FeatureServer also supports download via `supportedExportFormats`:
csv, shapefile, sqlite, geoPackage, fileGDB, featureCollection, geojson, kml, excel

## Server Registry

The Raleigh Open Data portal aggregates from these ArcGIS servers:

| Server | Base URL | Content |
|--------|----------|---------|
| Raleigh City | `https://services.arcgis.com/v400IkDOw1ad7Yad/arcgis/rest/services/` | ~61 FeatureServer datasets |
| Raleigh Maps | `https://maps.raleighnc.gov/arcgis/rest/services/` | ~23 MapServer layers |
| Wake County | `https://maps.wake.gov/arcgis/rest/services/` | ~38 MapServer services |
| Wake County (alt) | `https://maps.wakegov.com/arcgis/rest/services/` | Alternative county endpoint |

## Query Examples

### All dog parks with shade
```
GET https://services.arcgis.com/v400IkDOw1ad7Yad/arcgis/rest/services/DogParkLocations_Existing_PUBLIC/FeatureServer/0/query
  ?where=SHADE%3D%27Yes%27
  &outFields=*
  &returnGeometry=true
  &f=geojson
```

### Food inspections with scores under 75
```
GET https://maps.wake.gov/arcgis/rest/services/Inspections/RestaurantInspectionsOpenData/MapServer/1/query
  ?where=SCORE%3C75
  &outFields=*&returnGeometry=false
  &f=json
  &resultRecordCount=20
  &orderByFields=SCORE%20ASC
```

### Recent building permits
```
GET https://services.arcgis.com/v400IkDOw1ad7Yad/arcgis/rest/services/Building_Permits_Issued_Past_180_Days/FeatureServer/0/query
  ?where=1%3D1
  &outFields=*
  &returnGeometry=false
  &f=json
  &resultRecordCount=50
  &orderByFields=ISSUE_DATE%20DESC
```

### Find crashes near a location (not natively supported — use where clause on spatial fields where available)
```
GET https://maps.wake.gov/arcgis/rest/services/CrashesInvolvingCyclists/MapServer/0/query
  ?where=1%3D1
  &outFields=*
  &returnGeometry=true
  &f=geojson
  &resultRecordCount=100
```

## Notes

- All endpoints are public — no API key required
- Rate limits are generous but not documented; use reasonable pagination
- Dates are returned as Unix timestamps in milliseconds (divide by 1000 for seconds)
- `returnGeometry=false` is faster for tabular queries when you don't need spatial data
- MapServer layers with `type: "Table"` have no geometry — always use `returnGeometry=false`
- The `where` parameter supports standard SQL operators: `=`, `<`, `>`, `<=`, `>=`, `<>`, `LIKE`, `IN`, `AND`, `OR`, `NOT`
- String values in WHERE must be single-quoted: `WHERE NAME='Millbrook-Exchange'`
