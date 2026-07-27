---
name: comic-chat
description: Render deterministic PNG comic strips from scene JSON using bundled historical Microsoft Comic Chat art. Use for a static Comic Chat-style panel or strip, not a chat application, IRC client, image generation, or animation.
license: MIT
compatibility: Python 3.9+ and Pillow; bundled v2.5 beta 1 assets require no network access.
---

# Comic Chat PNG Renderer

Render a static PNG comic strip from declarative scene JSON. The skill ships a reusable, portable asset pack converted from the Microsoft Comic Chat v2.5 beta 1 source distribution: PNG backdrops, PNG avatar pose layers, and JSON pose manifests. It does not connect to IRC or generate art.

## Workflow

1. Read [references/scene-plan.md](references/scene-plan.md) before designing a multi-panel strip.
2. Start from [examples/scene.json](examples/scene.json). Use bare filenames, for example `field.png` and `anna.json`.
3. Render against the bundled pack:

```sh
python3 scripts/render_comic.py \
  --assets-dir assets/v2.5-beta-1 \
  --scene examples/scene.json \
  --output comic.png
```

4. Inspect the image and PNG text metadata. It records the renderer, scene SHA-256, pinned Microsoft source label, and every selected bundled asset with a SHA-256 digest. It never records the local asset path.

Read [references/source-lineage.md](references/source-lineage.md) when changing conversion or asset setup. Read [references/licensing.md](references/licensing.md) before redistributing source art or a rendered strip.

## Asset Behavior

`--assets-dir` must contain `backdrop/` and `avatars/`. The bundled avatar manifests use `pose` for simple avatars and `face_pose` plus `torso_pose` for complex avatars. Their converted PNG layers retain source coordinates, `TORSOFIRST` ordering, and enabled `HEADMASK`/`TORSOMASK` raster composition. Missing complex poses select the source-style neutral record deterministically.

`convert_art.py` is the reproducible converter for the pinned Microsoft v2.5 beta 1 BGB and AVB containers. Do not download arbitrary art during rendering or claim pixel-perfect Windows-app compatibility.

## When Not To Use

Do not use this for a live chat product or IRC client. Use frontend/backend engineering for an application and a video-composition skill for animation.
