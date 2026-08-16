# GIS Ingestion

## Public source classes

Use sources whose terms permit the intended output and record the exact layer, not just a portal home page.

| Class | Named source | URL | Typical use |
|---|---|---|---|
| Elevation DEM | USGS 3D Elevation Program through The National Map | https://apps.nationalmap.gov/ and https://epqs.nationalmap.gov/v1/json | Ground elevations in meters; the point service is suitable for a coarse sample and 3DEP downloads for full packs. |
| Building footprints/heights | OpenStreetMap contributors through Overpass API | https://overpass-api.de/api/interpreter | Footprints plus `height` or `building:levels` tags under ODbL 1.0. |
| Municipal building footprints | City of Raleigh Building Footprints FeatureServer | https://services.arcgis.com/v400IkDOw1ad7Yad/arcgis/rest/services/Building_Footprints/FeatureServer | Authoritative annual aerial-derived planimetry; review the portal's custom license before redistribution. |
| Road/path vectors | OpenStreetMap contributors through Overpass API | https://overpass-api.de/api/interpreter | `highway=*`, sidewalk, footway, path, and name tags under ODbL 1.0. |
| Street furniture (props) | OpenStreetMap contributors through Overpass API | https://overpass.kumi.systems/api/interpreter | Point nodes: `highway=traffic_signals`, `highway=crossing`, `highway=bus_stop`, `natural=tree`, `barrier=bollard`, `amenity=bench`, `emergency=fire_hydrant`, `highway=street_lamp`. |

For Raleigh, municipal footprint geometry may be cross-checked with OSM; OSM height tags can enrich municipal records. Keep both source claims when geometry and height come from different places.

### Street furniture acquisition

Pull point furniture in one node query over the same bbox (`out body;` to keep coordinates):

```sh
curl --fail --silent --show-error --get \
  --data-urlencode 'data=[out:json][timeout:120];(node[highway=traffic_signals](S,W,N,E);node[highway=street_lamp](S,W,N,E);node[natural=tree](S,W,N,E);node[highway=bus_stop](S,W,N,E);node[amenity=bench](S,W,N,E);node[barrier=bollard](S,W,N,E);node[emergency=fire_hydrant](S,W,N,E);node[highway=crossing](S,W,N,E););out body;' \
  --output /tmp/city-props.json \
  https://overpass.kumi.systems/api/interpreter
```

The primary `overpass-api.de` endpoint can return HTTP 504 under this multi-clause load; the `overpass.kumi.systems` mirror answers the same QL. Map each node to a `kind` (and the documented glyph) by its tag, project `lon/lat` to local meters, and drop nodes that fall outside the pack bounds. Record per-prop provenance.

Street-name **signs** are derived, not downloaded: take each distinct `name` on a road/path way, anchor the sign at that way's centroid (clipped into bounds), set `text` to the exact `name` string, and record `anchor_way` as the source way id so every sign traces to a real record.

## Reproducible pipeline

1. Fix a WGS84 bounding box and source retrieval date.
2. Download each response to a separate immutable source file. Fail on HTTP errors. Verify content type, nontrivial byte size, parseability, and a SHA-256 checksum before conversion; an HTML error page or truncated response must not proceed.
3. Read source metadata and verify horizontal CRS, vertical datum, and elevation units. Convert feet to meters explicitly with `meters=feet*0.3048`; never infer units silently.
4. Reproject all geometry into a local meter-based CRS before resampling. UTM Zone 17N (`EPSG:32617`) is suitable for Raleigh; a documented local tangent plane also works for a small pack. Geographic degrees have different east-west and north-south scales and cannot support correct meter-based step, slope, distance, FOV, or collision calculations.
5. Clip features to bounds. For a building crossing the boundary, clip its polygon and record `clipped: true`.
6. Resample the DEM to a regular grid. Preserve voids as JSON `null`; do not interpolate across unknown coverage without marking the result and lowering confidence.
7. Normalize building polygons, reject self-intersections, and convert heights to meters. A nonpositive height is missing. When height is absent, use `height_m = floors * 3.2` with **3.2 meters per floor**. If floors are also absent, use a documented class default. Mark estimated values, lower confidence (for example 0.55 for tagged floors or 0.35 for a class default), and retain the method.
8. If height sources disagree, select the value with the higher documented confidence and retain the losing observation in provenance notes.
9. Normalize roads, sidewalks, and paths into surface geometry and set `walkable` deliberately rather than inferring it at runtime.
10. Emit the manifest and tile JSON, then run the offline validator.

## Provenance requirements

Every terrain tile and emitted building must carry or reference:

- source name;
- exact public source URL;
- license or terms identifier;
- retrieval date in `YYYY-MM-DD` form;
- confidence from `0.0` through `1.0`.

Record whether geometry, elevation, and height came from separate sources. The manifest lists all pack-level sources; feature-level provenance identifies the source actually used. Confidence is an evidence judgment, not positional precision. Also retain checksums in acquisition notes even when the runtime schema does not require them.

## Local tangent-plane fallback

For a compact box centered at `(lon0,lat0)`, stdlib-only conversion can use:

```text
x = radians(lon-lon0) * 6378137 * cos(radians(lat0))
y = radians(lat-lat0) * 6378137
```

Document this as an equirectangular local tangent approximation, use it only over a small area, and keep the origin in `crs`. For larger packs, use a vetted projection library and EPSG CRS.
