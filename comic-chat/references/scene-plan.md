# Scene Plan

The top-level object has `width`, `height`, `gutter`, and a nonempty `panels` list. Dimensions are pixels. Panels are arranged horizontally at equal width.

Each panel accepts:

```json
{
  "backdrop": "field.bmp",
  "caption": "Optional caption",
  "characters": [{
    "avatar": "anna.avb",
    "face_pose": 0,
    "torso_pose": 0,
    "fallback_face": "fc_hap_s.bmp",
    "x": 0.18,
    "y": 0.32,
    "scale": 1.4,
    "flip": false,
    "say": "Speech is drawn in a balloon.",
    "balloon": "speech"
  }]
}
```

`x` and `y` are panel-relative coordinates from 0 through 1. `scale` must be positive and no greater than 4.0. `flip` is boolean. `caption` and `say` are strings. Asset names (`backdrop`, `avatar`, and optional `fallback_face`) must be bare filenames, not paths.

## Resource Limits

Validation runs before the renderer allocates the output image or resizes any source art. A scene may be at most 8,192 pixels wide, 8,192 pixels high, and 32,000,000 total pixels. It may contain at most 16 panels and 12 characters in any one panel. Avatar `scale` may not exceed 4.0. Values beyond these limits fail with `SceneError`.

For a simple AVB, provide `pose`, a zero-based body-record index. For a complex AVB, provide `face_pose` and `torso_pose`, zero-based indices into their respective tables; `pose` is rejected for complex AVBs. If either complex index is omitted, the renderer uses the first source record whose emotion is zero and intensity is zero, or record zero when no such record exists. This follows the source's neutral-selection fallback rather than treating one table as a complete avatar. All pose fields are nonnegative integers.

Complex figures preserve the source placement formula `torso.xCX + face.delta_xCX - face.xCX` (and its Y equivalent) and source layer order. The renderer distributes any panel-width remainder across the first panels, so the strip width is completely allocated.

When `say` is nonempty, `balloon` selects its visual treatment. It defaults to `speech`; accepted values are `speech` (rounded outline and pointed tail), `thought` (oval with bubble trail), `shout` (starburst outline), and `whisper` (fine dashed outline). Other values fail scene validation rather than silently rendering as speech. The renderer wraps long words, keeps the balloon and its tail within its panel, and moves later balloons to avoid overlap. If the panel has no remaining space, rendering fails instead of hiding text.
