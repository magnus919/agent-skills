# ASCII City Engine

## Why Install This Skill

Turn public elevation, building, and street data into a portable, first-person colored-ASCII city without re-deriving coordinate, collision, and provenance rules. The skill keeps the renderer city-neutral and city packs interchangeable.

## What You Get

- A heightfield and solid-footprint engine architecture.
- JSON Schemas for manifests and world tiles.
- A deterministic offline city-pack validator.
- A pure browser, single-file Canvas 2D reference engine.
- A small redistributable downtown Raleigh sample with real public footprints.
- Reproducible GIS ingestion and Raleigh walkthrough references.

## Quick Start

```sh
python3 scripts/validate-city-pack.py assets/raleigh-downtown-sample
python3 -m http.server 8000
```

Then open `http://localhost:8000/assets/ascii-city-engine.html`. The scaffold reads `assets/raleigh-downtown-sample/manifest.json` for the spawn point and first world tile; use W/S or arrow keys to move and A/D or left/right arrows to turn.

## Triggers

Load this skill for requests to build a colored ASCII city renderer, create a terrain-following first-person walker, define a pluggable city pack, ingest public GIS into the provided contract, or reproduce the Raleigh proof of concept.

Do not load it for ordinary GIS analysis, WebGL/3D engines, multi-level interiors or tunnels, gameplay systems, or requests to commit full-resolution GIS archives.

## Requirements

- Python 3 standard library for validation and conversion examples.
- A current desktop browser with Canvas 2D and `fetch` support.
- Network access only while acquiring full-resolution public GIS data; validation and the committed sample run offline.
- Source licenses that permit redistribution, with attribution and retrieval metadata.
