# Soft Proofing Workflow

Soft proofing is the art of previewing how an image will look after
conversion to a (usually smaller) color space, before actually committing
to the conversion. Essential for avoiding unwanted color clipping, hue
shifts, and detail loss.

---

## When to Soft Proof

| Scenario | Why |
|----------|-----|
| Converting from ProPhotoRGB to sRGB for web | sRGB is much smaller; saturated colors will clip |
| Sending to a printer with a known profile | Printer gamut differs from monitor gamut |
| Any conversion where source gamut > destination gamut | Uncontrolled clipping produces hue shifts |
| Preparing images for a specific display (projector, kiosk) | The output device may have a limited gamut |

## Required Tools

- **ImageMagick** (`convert`, `compare`) — primary soft proof engine
- **ArgyllCMS** (`iccgamut`, `viewgam`) — 3D gamut visualization
- **Destination ICC profile** — the profile for your output device/web space

## Method 1: The NULL Curves Technique (Command Line)

This is the most reliable technique for detecting out-of-gamut colors
before conversion. It works by forcing an ICC conversion at floating point
and comparing the result to the original.

```bash
# 1. Convert to destination profile (ImageMagick, relative colorimetric)
convert input.tif \
  -profile destination.icc \
  -intent Relative \
  -black-point-compensation \
  converted.tif

# 2. Make a "NULL Curves" reference — a straight convert back to source
#    that clips any out-of-gamut values
convert converted.tif \
  -profile destination.icc \
  -profile source.icc \
  null-curves.tif

# 3. Compare to find out-of-gamut pixels
compare -metric AE input.tif null-curves.tif difference.png
# The AE (Absolute Error) count = number of pixels that changed
```

A pixel that changes between `input.tif` and `null-curves.tif` had colors
outside the destination gamut. Those pixels were clipped and then
reinterpreted differently when converted back.

## Method 2: Gamut Check with Full Statistics

The `gamut-check.py` script automates this:

```bash
python3 scripts/gamut-check.py input.tif \
  --to-profile destination.icc \
  --overlay gamut-overlay.png \
  --verbose
```

This produces:
- Count and percentage of out-of-gamut pixels
- Channel extremes (min/max per channel after conversion)
- Visual overlay highlighting clipped regions

## Method 3: 3D Gamut Visualization

For a visual understanding of how the image gamut relates to the
destination gamut:

```bash
# Create 3D gamut of the destination profile
iccgamut -ir destination.icc destination.gam
viewgam -w destination.gam destination.wrl

# View in a VRML viewer
view3dscene destination.wrl
```

This is useful for understanding *why* certain colors clip — are they
too saturated? too bright? too dark?

## The Four Strategies for Handling Out-of-Gamut Colors

### 1. Reduce Chroma (saturation)

Most effective for saturated colors that just barely exceed the gamut.
Use a Channel Mixer layer with reduced gain, or apply a selective
saturation reduction.

```bash
# Reduce overall saturation by 20% before conversion
convert input.tif -modulate 100,80 input-desaturated.tif
```

### 2. Reduce Lightness

More effective for bright colors (Y > 0.8) that clip. A slight
lightness reduction preserves hue and chroma better than clipping.

In GIMP LCH workflow: reduce Lightness in the LCH Lightness group
before the final conversion.

### 3. Shift Hue

Sometimes moving a color's hue slightly (e.g., shifting orange toward
yellow) keeps it within gamut while maintaining the image's color
harmony. Use the Hue-Chroma tool or selective HSL adjustments.

### 4. Let It Clip

Not every out-of-gamut pixel needs fixing. If only a small percentage
of pixels (<<1%) are affected, or if the affected areas are in regions
where hue shifts are imperceptible (e.g., specular highlights), letting
the colors clip is often the best artistic choice.

## GIMP Soft Proofing

GIMP 2.9+ (and GIMP-CCE) provide soft proofing:

1. **Edit → Preferences → Color Management** (GIMP 2.8)
2. Set "Mode of operation" to "Print Simulation"
3. Choose the proof profile (destination profile)
4. Set rendering intent and BPC
5. Enable "Mark out of gamut colors" to see what will clip

**Limitations:**
- GIMP only provides *global* soft proofing settings — you can't have
  the original and proof open side-by-side in the same window
- The gamut check marker uses a solid color that can obscure detail
- For side-by-side comparison, open a second copy in another editor

## LCMS2 Soft Proofing Bug (Linear Gamma)

LCMS2 versions before 2.8 produce **inaccurate gamut checks** for images
in linear gamma color spaces. If your image uses a gamma=1.0 profile,
create a flattened copy and convert it to a perceptually uniform TRC
(e.g., sRGB TRC or LAB L TRC) before running the gamut check.

Workaround:

```bash
# Convert to perceptually uniform TRC for accurate gamut check
convert linear-image.tif \
  -profile linear-srgb.icc \
  -profile srgb-perceptual.icc \
  perceptual-image.tif

# Now run gamut check on perceptual-image.tif
# The gamut check will be accurate even with older LCMS
```

## Soft Proofing with Perceptual Intent

Only use perceptual intent when the **destination profile is a LUT
profile** (printer profiles, some monitor profiles). Perceptual intent
with matrix profiles silently falls back to relative colorimetric.

```bash
# Perceptual intent — only valid for LUT destination profiles
convert input.tif \
  -profile printer-profile.icc \
  -intent Perceptual \
  soft-proofed.tif
```

The difference between relative colorimetric and perceptual:
- **Relative colorimetric**: in-gamut colors preserved exactly;
  out-of-gamut clipped to nearest surface color
- **Perceptual**: entire gamut compressed to fit; relationships
  preserved, absolute accuracy traded for gradation

## Reference

- ninedegreesbelow.com: "Autumn colors" tutorial (LCH layer stack +
  soft proofing workflow)
- ninedegreesbelow.com: "ICC Profile Conversion Settings" (CMS options
  comparison across GIMP, Krita, Cinepaint, digiKam)
- GIMP documentation: Color Management preferences
