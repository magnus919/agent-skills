---
name: comic-chat
description: Render deterministic PNG comic strips from scene JSON using the historical Microsoft Comic Chat backdrop and avatar art. Use when creating a static Comic Chat-style comic panel or strip from supplied assets; do not use for a chat application, IRC client, generative image creation, or animated video.
license: MIT
compatibility: Python 3.9+ and Pillow; an explicitly supplied Comic Chat asset directory is required to render.
---

# Comic Chat PNG Renderer

Render a static PNG comic strip from declarative scene JSON. This skill uses local raster assets only: it does not connect to IRC, implement a chat application, or generate images with an AI model.

## Workflow

1. Before the first `fetch_assets.py` mutation, confirm all of the following with the user: the target cache directory; scope (a pinned upstream archive checkout only); purpose; interruption/risk (the command creates or updates `<cache-dir>/source` and needs Git/network access); verification (the resolved commit and assets directory printed by the script); and rollback (remove only that explicitly named cache directory). Do not fetch until that confirmation is explicit.
2. After confirmation, obtain the asset tree in a cache directory the user controls. The default is a user cache, never this skill directory:

```sh
python3 scripts/fetch_assets.py --cache-dir "$HOME/.cache/comic-chat"
```

3. Start from [examples/scene.json](examples/scene.json). Keep asset names as bare filenames such as `field.bmp` and `anna.avb`.
4. Render with an explicit asset directory:

```sh
python3 scripts/render_comic.py \
  --assets-dir "$HOME/.cache/comic-chat/source/v1.0-pre-modern/comicart" \
  --scene examples/scene.json \
  --output comic.png
```

5. Inspect the output and its PNG text metadata. It records the renderer, scene SHA-256, pinned upstream source label, and each selected relative asset name with a SHA-256 digest; it does not record the local asset path.

Read [references/scene-plan.md](references/scene-plan.md) before designing a multi-panel scene. Read [references/source-lineage.md](references/source-lineage.md) when changing AVB extraction or asset setup. Read [references/licensing.md](references/licensing.md) before redistributing source art or a rendered strip.

## Asset Behavior

`--assets-dir` must contain `backdrop/` and `avatars/`. Simple AVBs use `pose`; complex AVBs compose `face_pose` and `torso_pose` using their source record coordinates and `TORSOFIRST` layer order. Missing complex poses select the source-style neutral record deterministically. For complex AVBs, enabled `HEADMASK` and `TORSOMASK` layers apply the source `MERGEPAINT` then `SRCAND` raster operations to the panel pixels, so white source art preserves the existing backdrop while black lines draw black. It does not claim pixel-perfect legacy raster emulation. If the AVB is unreadable or has no usable pose, the renderer uses the requested `fallback_face` or `fc_neu_s.bmp`; that explicit BMP fallback is ordinary RGBA composition and is reported in PNG provenance.

Do not silently substitute generated art, download arbitrary art during rendering, or claim pixel-perfect compatibility with the Windows application. Errors identify the scene path, asset, and failed validation.

## When Not To Use

Do not use this for a live chat product or IRC client. Use a frontend or backend engineering skill for an application, and use a video composition skill for animation.
