# Comic Chat: Deterministic PNG Comic Strips

Turn a small JSON scene plan into a static comic strip using the historical Comic Chat artwork, with no image model or chat server involved.

## Why Install This Skill

Comic Chat's original art is charming but difficult to reuse: avatars are stored as old AVB files with embedded bitmaps, and complex face and torso records need source-defined composition. This skill provides a command-line renderer that does that work locally and records non-sensitive provenance in the finished PNG.

Use it for screenshots, documentation illustrations, workshop handouts, or reproducible visual stories. You define panels, dialogue, and character placement in JSON; the renderer produces the same PNG from the same scene and assets.

## What You Get

| Contents | Provides |
|---|---|
| `scripts/render_comic.py` | Pillow renderer and AVB embedded-DIB extractor |
| `scripts/fetch_assets.py` | Pinned, cache-controlled upstream asset setup |
| `examples/scene.json` | Runnable three-panel, two-speaker scene |
| `references/` | Scene contract, source lineage, and licensing notes |
| `evals/evals.json` | Portable output-quality cases |

## Quick Start

```sh
python3 -m pip install Pillow
python3 scripts/fetch_assets.py --cache-dir "$HOME/.cache/comic-chat"
python3 scripts/render_comic.py --assets-dir "$HOME/.cache/comic-chat/source/v1.0-pre-modern/comicart" --scene examples/scene.json --output comic.png
```

`fetch_assets.py` creates or updates the pinned archive checkout at `$HOME/.cache/comic-chat/source`; use a cache directory you control. The render command writes `comic.png` and prints the selected asset provenance. PNG metadata stores relative asset names and digests plus the pinned upstream source label, never your local asset path.

## Triggers

- Render a static Comic Chat-style PNG strip.
- Compose a panel scene from Comic Chat avatars, face art, and backdrops.
- Extract an embedded DIB from a Comic Chat AVB asset for a reproducible illustration.

## Requirements

- Python 3.9 or newer
- Pillow (`python3 -m pip install Pillow`)
- Git and network access only when running `fetch_assets.py`
- A local asset tree supplied through `--assets-dir`
