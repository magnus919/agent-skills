# Nous Branding — Post-Processing

Load this file whenever a generated image is about to be delivered: raw AI
output is never the final deliverable. This file holds the post-processing
modes, intensity calibration, and integration commands for
`scripts/postprocess.py`.

Raw AI-generated images are too clean for the Nous aesthetic.
**Post-processing is mandatory** after every generation. The
`scripts/postprocess.py` script applies analog-print degradation effects
locally using Pillow + numpy — no API calls needed.

## Quick Start

```bash
python3 scripts/postprocess.py input.png output.png --mode imprint --intensity 0.7
```

## Modes

| Mode | Effects | When |
|------|---------|------|
| `imprint` | All 14 effects: warm grade, CRT scanlines, film grain, Bayer dither, vignette, chromatic aberration, screen print texture, paper fiber, ink bleed, palette compression, xerox threshold, registration offset, plate wobble, print scuffs | **Default for v9/v10/v11 targets** — maximum analog print character |
| `nous` | Base 9 effects (warm grade → ink bleed) — no xerox/registration/wobble/scuffs | Legacy luminous PNW/celestial requests |
| `standard` | Base 6 effects (warm grade → chromatic aberration) only | When you want just a light texture touch |

## Intensity Calibration

| Intensity | Best for |
|-----------|----------|
| `0.45–0.55` | Fine manga linework, Future Halftone, Portal Minimal — keep detail visible |
| `0.55–0.65` | Blueprint Scene, general use — avoid crushing midtones |
| `0.65–0.8` | Xerox Poster, Acid Signal, heavy print effect — when the raw output is too clean |
| `0.8+` | Aggressive degradation — typography may become hard to read |

## Integration

Run post-processing as the final step after any generation method (text-only,
img2img, multi-pass, or any provider):

```bash
# After any generation method:
python3 scripts/postprocess.py output-raw.png output-final.png --mode imprint --intensity 0.7

# For legacy luminous targets:
python3 scripts/postprocess.py output-raw.png output-final.png --mode nous --intensity 0.5
```

**The raw generated image is never the final deliverable.**
