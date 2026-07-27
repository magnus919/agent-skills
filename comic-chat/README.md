# Comic Chat: Deterministic PNG Comic Strips

Turn a small JSON scene plan into a static Comic Chat-style strip using a bundled, portable rendition of the historical Microsoft artwork. There is no image model, chat server, or network dependency at render time.

## Why Install This Skill

The original Comic Chat art is charming but hard to reuse: v2.5 backdrops and avatars live in proprietary BGB and AVB containers, and complex characters need source-defined face, torso, mask, and layer composition. This skill bundles the converted v2.5 beta 1 art as PNG layers and JSON manifests, then renders it deterministically.

Use it for screenshots, documentation illustrations, workshop handouts, or reproducible visual stories. You define panels, dialogue, and character placement in JSON; the renderer produces the same PNG from the same scene and bundled assets.

## What You Get

| Contents | Provides |
|---|---|
| `assets/v2.5-beta-1/` | Bundled PNG backdrops, PNG avatar layers, JSON manifests, and upstream license |
| `scripts/render_comic.py` | Deterministic Pillow renderer for the bundled pack |
| `scripts/convert_art.py` | Reproducible BGB/AVB-to-PNG conversion from the pinned Microsoft source |
| `examples/scene.json` | Runnable three-panel, two-speaker scene |
| `references/` | Scene contract, source lineage, and licensing notes |
| `evals/evals.json` | Portable output-quality cases |

## Quick Start

```sh
python3 -m pip install Pillow
python3 scripts/render_comic.py \
  --assets-dir assets/v2.5-beta-1 \
  --scene examples/scene.json \
  --output comic.png
```

The render command writes `comic.png` and prints selected-asset provenance. PNG metadata records relative asset names and SHA-256 digests plus the pinned Microsoft source label, never your local asset path.

## Triggers

- Render a static Comic Chat-style PNG strip.
- Compose a panel scene from bundled Comic Chat avatars, face art, and backdrops.
- Convert Microsoft Comic Chat v2.5 BGB or AVB source art into reusable PNG assets.

## Requirements

- Python 3.9 or newer
- Pillow (`python3 -m pip install Pillow`)
- No network access for rendering with the bundled pack
- Git and network access only when obtaining the upstream source to regenerate assets
