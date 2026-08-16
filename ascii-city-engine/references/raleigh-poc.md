# Raleigh Proof of Concept

This walkthrough reproduces the committed `../assets/raleigh-downtown-sample/` pack and scales it up to a fuller downtown pack. The committed sample is intentionally coarse (10 m terrain, simplified footprints, <= 2 MB) so the repository stays light; the full pipeline below is what you run for a denser local pack.

## Downtown bounding box (authoritative for this POC)

WGS84 (EPSG:4326), south-west to north-east:

```text
min: lon -78.6420, lat 35.7760
max: lon -78.6350, lat 35.7830
```

This box covers the Fayetteville Street core, the State Capitol grounds, Nash and Moore Squares' west edges, and the Hillsborough Street corridor. Through the tangent-plane conversion in `gis-ingestion.md` the box measures about 632 m east-west by 779 m north-south; the committed sample's manifest bounds and terrain grid are normalized to an exact 630 m by 770 m working extent (78 rows x 64 cols at 10 m) that sits inside it, so the documented formula and the shipped grid differ by roughly 1-2 m at the edges. It is deliberately compact so the sample stays small and every acceptance check is walkable in minutes. Expand symmetrically (for example to `-78.6520..-78.6280, 35.7680..35.7910`) for a fuller downtown pack.

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

1. **Load.** The HUD reads `159 buildings · 298 props · 29 signs` with no error text. Colored building walls rise against dark sky, and the wayfinding line reads `On: South Wilmington Street` (the spawn street).
2. **Spawn.** Camera starts at local `(340, 390)` facing north (heading 90°), mid-corridor on the Wilmington Street axis. HUD elevation reads about 100 m.
3. **Street-name sign.** Hold W and walk north ~120 m (about 30 s at 4 m/s) along Wilmington Street. The light-gray text `North Wilmington Street` (anchored ~143 m ahead, y≈532) floats in-world as you approach. The `East Hargett Street` sign is ~141 m *behind* the spawn (y≈249), so turn around (hold S or rotate) to see it. These names come from the road `name` tags, never invented.
4. **Street furniture.** Along the walk, yellow `T` traffic signals cluster at intersections, white `=` crosswalk bands cross the road, green `t` trees dot the verges, and a cyan `B` marks a bus stop. All are point records from the OSM furniture layer.
5. **Walk with a grade.** The HUD elevation climbs continuously from ~100.1 m to ~101.0 m over the ~120 m walk — `feet_z` follows terrain and movement is never rejected on this gentle grade.
6. **Solid footprint.** Turn toward the nearest building wall and hold W into it. Forward motion stops at the wall face; strafing (A/D while holding W) slides along it. You cannot pass through or under it.

Re-run the validator after every fresh acquisition; if a data update moves a footprint onto the documented spawn, pick a new walkable spawn inside bounds and update `manifest.json` before publishing the pack.

## Known limitations of the committed sample

- Terrain is bilinear interpolation of four EPQS corner observations — smooth and correct in trend, but it cannot show curb-level detail. A full pack should resample the 3DEP DEM at 2–5 m.
- Most buildings use the `OSM building:levels × 3.2 m/floor` estimate (confidence 0.72); a minority carry an explicit OSM `height` tag (confidence 0.88). The 0.55/0.35 fallback tiers in `gis-ingestion.md` step 7 apply to lower-evidence cases than this sample contains. Skyline proportions are right; individual roof elevations may not be.
- Buildings and surfaces crossing the bbox edge are clipped to the 630 × 770 m working extent and marked `clipped: true`; a small number that collapse below 3 vertices or self-intersect after clipping are dropped rather than weaken the validator's simple-polygon guarantee.
- OSM does not record `highway=street_lamp` nodes for downtown Raleigh, so lamps are absent from props; road `lit` tags still drive ground brightness. Municipal furniture layers (signals, lamps, trees) on the City of Raleigh ArcGIS portal can fill this gap but were not required for the current census.
- Raleigh municipal footprints are used as a geometry cross-check only; runtime footprints stay on ODbL-licensed OSM geometry so the sample remains redistributable with attribution.
