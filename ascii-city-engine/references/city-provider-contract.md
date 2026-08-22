# City Provider Contract

A city pack is a directory with `manifest.json` and one or more JSON world tiles. The engine reads only this contract; it must not branch on city name.

## Manifest semantics

Validate `manifest.json` against `../templates/city-pack-manifest.schema.json`.

- `name`: stable lowercase pack identifier.
- `version`: pack release version.
- `crs`: local meter CRS description, including origin or EPSG code.
- `bounds`: inclusive `min_x`, `min_y`, `max_x`, `max_y` in that CRS.
- `tiles`: non-empty relative paths contained by the pack directory.
- `spawn`: optional walkable local coordinate and heading.
- `provenance`: source records with public URL, license, ISO retrieval date, and optional confidence.

Paths must be relative, resolve inside the pack, and refer to regular JSON files. Manifest bounds must contain every tile's terrain, footprint, surface, and prop extent.

## World-tile semantics

Validate each tile against `../templates/world.schema.json`.

- `terrain`: rectangular row-major elevations, meter resolution, local origin, and provenance. The extent is `[origin_x, origin_x+(columns-1)*resolution]` by `[origin_y, origin_y+(rows-1)*resolution]`. Null denotes a DEM void.
- `buildings`: globally unique IDs, simple closed-by-interpretation footprint polygons with at least three distinct vertices, meter base and positive height, stable color, and provenance/confidence.
- `surfaces`: IDs, kinds such as road/sidewalk/path/park/water, polyline or polygon geometry, and an explicit `walkable` flag. Surfaces annotate and render the ground; they do not replace terrain height.
- `props`: lightweight point objects such as trees, lamps, signals, and signs. Each carries `id`, `kind`, `x`, `y`, optional `label`, and provenance. The documented per-kind glyph map is: `traffic_signal=T, street_lamp=i, tree=t, bus_stop=B, bench=b, bollard=o, fire_hydrant=f, crossing==`. A kind with no mapping renders with the fallback glyph `?` and is flagged by the validator.
- `signs` (optional): street-name text billboards anchored at a real location, each carrying `id`, `text`, `x`, `y`, optional `anchor_way` (the source road's way id), and provenance. Sign `text` must equal a `name` tag present in the source road data — never invented.

A provider may split content into tiles, but duplicate building and surface IDs are forbidden. A consumer may stream or spatially index tiles without changing semantics.

## V1 vertical limitation

V1 models **exactly one ground height per `(x, y)` column**. It cannot represent a walkable bridge with walkable space beneath it, a tunnel under terrain, stacked interiors, or stairs between levels. Buildings are solid and non-enterable.

The top-level `extensions.surface_graph` name is reserved for a future graph of distinct walkable surfaces, portals, and vertical relationships. Producers may preserve source hints there, but v1 engines must ignore the extension and must not claim bridge/tunnel traversal. Do not overload the terrain array or surface records to fake multiple heights.

## Validation behavior

Run:

```sh
python3 scripts/validate-city-pack.py path/to/pack
```

The validator uses only the Python standard library and network-free local files. It prints one `PASS` or `FAIL` line per rule, then summary counts. Exit 0 means every rule passed; any schema, geometry, extent, provenance, or uniqueness failure exits 1. The fixture at `../assets/deliberately-broken-pack/` intentionally demonstrates failures and is not a usable provider.
