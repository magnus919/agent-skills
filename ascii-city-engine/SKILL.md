---
name: ascii-city-engine
description: Build portable, first-person colored ASCII city engines and small GIS-derived city packs. Use when designing terrain-following walking, raycast character rendering, city-provider schemas, or reproducible public-GIS ingestion. Do not use for conventional 3D/WebGL games, multi-level interiors, general GIS analysis, or committing full-resolution GIS archives.
---

# ASCII City Engine

Build a portable city experience in three layers: an engine, a city-provider contract, and a city pack. Keep city-specific facts out of engine code.

## Workflow

1. Define the pack boundary and local meter-based CRS.
2. Acquire elevation, building, and road/path data from public sources.
3. Verify downloads, licenses, units, and provenance before conversion.
4. Reproject all geometry to local meters and emit the manifest plus world tiles.
5. Validate the pack offline:
   ```sh
   python3 scripts/validate-city-pack.py path/to/city-pack
   ```
6. Load the pack's first tile in `assets/ascii-city-engine.html` and test movement, grade following, and solid footprints.
7. Record data limitations and human acceptance evidence.

## Required invariants

- Compute `feet_z` from terrain and `eye_z` from feet plus eye height.
- Reject null terrain, over-steep steps, and movement touching a solid footprint.
- Use deterministic building colors and clear missed rays every frame.
- Treat v1 as one ground height per `(x, y)` column; reserve, but do not implement, a surface graph.
- Keep the engine independent of any city, vendor, agent harness, or private infrastructure.
- Do not commit large or full-resolution source data. Commit only a small redistributable sample; document acquisition for the rest.

## Reference routing

- Read [references/engine-architecture.md](references/engine-architecture.md) for world math, rendering, collisions, and the scaffold contract.
- Read [references/city-provider-contract.md](references/city-provider-contract.md) when creating or validating a provider.
- Read [references/gis-ingestion.md](references/gis-ingestion.md) before downloading or converting GIS sources.
- Read [references/raleigh-poc.md](references/raleigh-poc.md) for the reproducible Raleigh proof of concept.
- Use [templates/city-pack-manifest.schema.json](templates/city-pack-manifest.schema.json) and [templates/world.schema.json](templates/world.schema.json) as authoritative data contracts.

## Boundaries

Use a different skill or implementation approach for WebGL/GPU rendering, mobile controls, combat, interiors, bridges with traversable space below, tunnels, or general-purpose geospatial analysis. If asked to specialize this skill for one agent runtime, preserve the portable core and put runtime integration outside this skill. If asked to commit large GIS binaries, refuse and provide reproducible download/conversion commands instead.
