# Raleigh Proof of Concept

This walkthrough reproduces the committed `../assets/raleigh-downtown-sample/` pack and scales it up to a fuller downtown pack. The committed sample is intentionally coarse (10 m terrain, simplified footprints, <= 2 MB) so the repository stays light; the full pipeline below is what you run for a denser local pack.

## Downtown bounding box (authoritative for this POC)

WGS84 (EPSG:4326), south-west to north-east:

```text
min: lon -78.6420, lat 35.7760
max: lon -78.6350, lat 35.7830
```

This box covers the Fayetteville Street core, the State Capitol grounds, Nash and Moore Squares' west edges, and the Hillsborough Street corridor — roughly 630 m east-west by 770 m north-south. It is deliberately compact so the committed sample stays small and every acceptance check is walkable in minutes. Expand symmetrically (for example to `-78.6520..-78.6280, 35.7680..35.7910`) for a fuller downtown pack.

Local pack CRS: equirectangular tangent plane, origin `[-78.6420, 35.7760]`, x east / y north, meters (see `gis-ingestion.md` §Local tangent-plane fallback).

## Data sources (all retrieved 2026-08-15)

| Layer | Source | URL | License | Role |
|---|---|---|---|---|
| Elevation | USGS 3DEP Elevation Point Query Service | `https://epqs.nationalmap.gov/v1/json` | US public domain | Terrain heights |
| Buildings (footprints + heights) | OpenStreetMap via Overpass | `https://overpass-api.de/api/interpreter` | ODbL 1.0 | Runtime footprints, tagged/estimated heights |
| Roads, sidewalks, paths | OpenStreetMap via Overpass (Kumi mirror) | `https://overpass.kumi.systems/api/interpreter` | ODbL 1.0 | Walkable surface network |
| Buildings (municipal cross-check) | City of Raleigh Building Footprints FeatureServer | `https://services.arcgis.com/v400IkDOw1ad7Yad/arcgis/rest/services/Building_Footprints/FeatureServer` | City of Raleigh Open Data terms; attribution required | Geometry verification; heights absent |

Observed yields on 2026-08-15 for the authoritative box: OSM returned 160 building ways, 41 carrying `height` or `building:levels`; the Raleigh FeatureServer returned 95 footprint polygons in the same box; EPQS center observation `(-78.6385, 35.7795)` = 106.517 m. EPQS corner observations for the sample grid: 95.727, 97.789, 101.578, 104.562 m — about 9 m of relief across the box.

## Acquisition commands

Run from anywhere; outputs land in `/tmp`. Each step must succeed before the next (fail on HTTP error, then sanity-check the parse).

```sh
# 1. OSM buildings (footprints + height/level tags)
curl --fail --silent --show-error --get \
  --data-urlencode 'data=[out:json][timeout:60];(way[building](35.7760,-78.6420,35.7830,-78.6350););out tags geom;' \
  --output /tmp/raleigh-buildings.json \
  https://overpass-api.de/api/interpreter

# 2. OSM roads/sidewalks/paths (primary endpoint 504s under load; use a mirror)
curl --fail --silent --show-error --get \
  --data-urlencode 'data=[out:json][timeout:90];way[highway](35.7760,-78.6420,35.7830,-78.6350);out tags geom;' \
  --output /tmp/raleigh-roads.json \
  https://overpass.kumi.systems/api/interpreter

# 3. Municipal footprints (cross-check; 1 page is enough at this box size)
curl --fail --silent --show-error --get \
  --data-urlencode 'where=1=1' \
  --data-urlencode 'geometry=-78.6420,35.7760,-78.6350,35.7830' \
  --data-urlencode 'geometryType=esriGeometryEnvelope' \
  --data-urlencode 'inSR=4326' \
  --data-urlencode 'spatialRel=esriSpatialRelIntersects' \
  --data-urlencode 'outFields=*' \
  --data-urlencode 'returnGeometry=true' \
  --data-urlencode 'f=geojson' \
  --output /tmp/raleigh-city-footprints.geojson \
  'https://services.arcgis.com/v400IkDOw1ad7Yad/arcgis/rest/services/Building_Footprints/FeatureServer/0/query'

# 4. Elevation: one EPQS call per grid node for a coarse sample;
#    for a full pack, download the 3DEP 1/3 arc-second DEM for the tile and resample.
curl --fail --silent --show-error \
  --output /tmp/raleigh-elevation-center.json \
  'https://epqs.nationalmap.gov/v1/json?x=-78.6385&y=35.7795&units=Meters&wkid=4326&includeDate=False'
```

Verification per `gis-ingestion.md`: check HTTP status, byte size, JSON parseability, and record a SHA-256 per file before conversion. If the City of Raleigh URL has moved, search the portal (`https://data.raleighnc.gov`) for "Building Footprints" and record the new service URL plus your retrieval date; the committed sample keeps this POC runnable regardless.

## Conversion

Reproject lon/lat to the local tangent plane (`gis-ingestion.md` §fallback), clip to the box, normalize polygons, estimate missing heights at **3.2 m per floor** with lowered confidence, emit `manifest.json` plus `world/tile-0.json`, then validate:

```sh
python3 scripts/validate-city-pack.py assets/raleigh-downtown-sample
```

Expected tail of a good run:

```text
PASS tile[0].content.bounds — world/tile-0.json
PASS buildings.unique-ids
PASS surfaces.unique-ids
PASS manifest.spawn.bounds
SUMMARY rules_passed=... rules_failed=0 buildings=30 terrain_extent=[0.0, 0.0]..[630.0, 770.0] surfaces=25
```

The deliberately-broken fixture must fail:

```sh
python3 scripts/validate-city-pack.py assets/deliberately-broken-pack
# FAIL manifest.bounds / manifest.tiles.nonempty / manifest.provenance ... ; exit 1
```

## Human acceptance checks (run after any acquisition)

Serve the repo root (`python3 -m http.server 8000`) and open `http://localhost:8000/assets/ascii-city-engine.html`.

1. **Load.** The status line reads `30 buildings · 25 surfaces` with no error text, and colored building walls appear against dark sky.
2. **Spawn.** Camera starts at local `(315, 385)` — mid-box, on the Fayetteville Street axis. The HUD elevation reads about 99–100 m.
3. **Walk >= 100 m with a grade.** Face north (heading 0) and hold W for ~30 seconds. The HUD elevation climbs steadily toward the north edge (~104 m). The steepest actual street grade in this box is the **Hillsborough Street rise west of the Capitol** — crossing it, you should see the horizon and building bases shift as `feet_z` follows terrain; movement is never rejected on this gentle grade.
4. **Solid footprint.** Turn toward the nearest large wall (the commercial block south-west of spawn, an OSM `COMMERCIAL` footprint) and hold W into it. Forward motion stops at the wall face; strafing (A/D while holding W) slides along it. You cannot pass through or under it.

Re-run the validator after every fresh acquisition; if a data update moves a footprint onto the documented spawn, pick a new walkable spawn inside bounds and update `manifest.json` before publishing the pack.

## Known limitations of the committed sample

- Terrain is bilinear interpolation of four EPQS corner observations — smooth and correct in trend, but it cannot show curb-level detail. A full pack should resample the 3DEP DEM at 2–5 m.
- Only ~26% of OSM buildings carry explicit heights; the rest use the 3.2 m/floor estimate with confidence 0.55 (or class default 0.35). Skyline proportions are right; individual roof elevations may not be.
- Raleigh municipal footprints are used as a geometry cross-check only; runtime footprints stay on ODbL-licensed OSM geometry so the sample remains redistributable with attribution.
