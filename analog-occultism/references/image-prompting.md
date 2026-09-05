# Image Prompting Reference

## Still-image structure

Lead with the subject and its spatial relationships, then specify the visual grammar:

```text
SUBJECT: [specific object/person/place/form], [position and relationship to frame]

LIGHT: one [screen/projector/industrial practical] from [direction]; selected
surfaces illuminated; surrounding space falls into deep shadow; clipped ivory
highlights and hard falloff.

AESTHETIC: analog occultism / industrial CRT noir; near-monochrome black, charcoal,
smoked gray, dirty silver, aged ivory; sparse midtones; tactile archival authenticity;
claustrophobic geometry; strong negative space; discovered technical artifact.

SIGNAL: this must look like a low-fidelity monochrome CRT screen capture or a
photograph of a CRT, not a sharp digital image with a filter. Use a small, soft,
interlaced broadcast raster; visible horizontal scanlines; coarse phosphor structure;
phosphor persistence trails; unstable vertical hold; slight horizontal tearing; sync
wobble; uneven brightness across the tube; clipped whites blooming around luminous
areas; crushed blacks hiding fine detail; dirty glass; dust; scratches; ghosting;
barrel distortion; and imperfect analog recording. Signal defects are structural and
must visibly reduce fidelity while preserving the essential subject.

MOOD: quiet unease, contemplation, precision, ritual, mechanical intelligence,
severe beauty, unresolved tension.

AVOID: broad neon color, glossy CGI, clean studio exposure, generic glitch art,
busy interface clutter, conventional horror, gore, cartoon treatment.
```

Use concrete nouns and verbs. For a portrait, specify what the light catches on the
face, hands, clothing, or reflective surfaces. For a product, specify contact with the
floor, table, cable, or enclosure. For a diagram or interface, specify what each panel,
line, or symbol communicates before describing the treatment.

## Capture-layer variants

Choose one before writing the prompt. Do not combine them accidentally.

### CRT-display view

The image is an image displayed on a square monochrome CRT. Emphasize the tube,
curved glass, phosphor, raster, scanlines, bloom, and signal instability. This is what
the previous test primarily achieved.

### Analog-camera documentary view

The subject is a real-world object or scene physically present in a room, photographed
or recorded directly by a period monochrome video camera. Say so plainly:

```text
A real physical [subject] in a real [location], captured directly by a period
monochrome analog video camera, not a digital render and not an image displayed on a
CRT. The camera sees actual surfaces, depth, reflections, lens focus falloff, exposure
imperfections, practical shadows, dust in the room, cable slack, worn edges, and
incidental background detail. Use a small low-resolution interlaced broadcast raster,
soft focus, scanlines, phosphor-like bloom, sync wobble, tracking noise, ghosting,
barrel distortion, crushed blacks, clipped whites, and dropped detail from the camera
and tape chain. The object must remain physically plausible and materially present.
```

A CRT monitor may appear in the room, but it is not required. The analog defects belong
to the camera, lens, tape, and playback chain. Do not describe only a digital scene
"with CRT effects," which encourages the model to render a clean synthetic object first.


Default to black, charcoal, smoked gray, dirty silver, aged ivory, and dirty white.
Use only a restrained cold green, blue-gray, or desaturated amber cast when it serves
the recording-medium illusion. A brief signal-error fringe is acceptable; broad neon
fields are not.

## Composition discipline

Prefer square or portrait crops, or tightly framed landscape shots when the brief
requires them. Anchor the frame with a luminous rectangle, receding grid, corridor,
foreground obstruction, or a small central object. Preserve large areas of darkness.
Controlled symmetry is useful, but add small physical imperfections so the frame feels
observed and recovered rather than digitally designed.

## Reference images

If a reference is supplied, pass it to the image generator. State what must be
preserved, what should be reinterpreted, and what must not carry over:

```text
PRESERVE: [identity, silhouette, proportions, essential markings, or composition]
REINTERPRET: [the supplied subject] through analog occultism / industrial CRT noir...
ADD: [new setting, light, or physical context]
DO NOT IMPORT: [unwanted logos, labels, background, or unrelated props]
```

The aesthetic is a treatment, not a license to alter the subject's identity. Use
`image-gen-reference` for the tool-specific edit workflow and anatomy gates.

## Text and symbols

Prefer no text unless it carries necessary meaning. When text is required, limit it to
short labels, indexes, specimen numbers, or system annotations. Use original symbols,
not recognizable logos or existing wordmarks. Verify visible text manually or with
vision inspection; generated text is not trustworthy merely because the prompt calls
it legible.

## Negative prompt

```text
bright even exposure, broad neon colors, RGB cyberpunk, vaporwave, teal-orange
cinematic grade, glossy commercial product photo, pristine CGI, clean vector art,
stock-photo smile, generic hacker room, random interface clutter, decorative glitch,
frenetic distortion, jump scare, gore, cartoon horror, fantasy ornament, nostalgic
prop collage
```
