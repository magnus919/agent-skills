# dcraw Raw Processing Pipeline

How raw file decoding fits into a color-managed workflow, using Dave
Coffin's dcraw — the foundation of most open-source raw processing.

---

## Why Raw Matters for Color Management

A camera-saved JPEG is:
- **Display-referred**: RGB values are already processed for display
- **White-balanced**: the camera applies a white balance that may not match
  your intent
- **Gamma-encoded**: non-linear encoding applied in-camera
- **Gamut-clipped**: any colors outside sRGB/AdobeRGB are already lost

A raw file is:
- **Scene-referred**: pixel values proportional to actual light in the scene
- **Linear**: sensor response is approximately linear to light
- **Unclipped**: no gamut mapping has been applied
- **Un-white-balanced**: the raw color filter array values are unprocessed

For color management, starting from raw means you have complete control
over every color decision — white balance, camera profile assignment,
working space selection, and gamut mapping.

## dcraw Basics

dcraw decodes raw files from essentially every digital camera ever made.
It outputs either:
- **PPNM/PPM** (16-bit linear): the default, no gamma, no white balance
- **TIFF** (with `-T`): 8-bit gamma-encoded sRGB by default
- **TIFF** (with `-4 -T`): 16-bit linear, no color processing

### Key Flags

| Flag | Purpose |
|------|---------|
| `-c` | Write to stdout (for piping) |
| `-w` | Use camera white balance (not the default) |
| `-T` | Output TIFF instead of PPM |
| `-4` | 16-bit linear (no gamma, no white balance) |
| `-D` | Raw data only (no interpolation) — for analysis |
| `-i -v` | Show image metadata, no decode |
| `-o 0` | Output in raw color space (no camera profile applied) |
| `-o 1` to `-o 5` | Output in sRGB, AdobeRGB, WideGamut, ProPhoto, XYZ |
| `-p file.icc` | Apply custom camera input profile |
| `-W` | No white balance at all (raw sensor data) |

## Workflow: Raw to Color-Managed Editing

### Step 1: Check camera support and metadata

```bash
dcraw -i -v raw-file.CR2
```

This shows: camera model, ISO, shutter speed, aperture, black levels,
white balance multipliers, and — critically — whether dcraw has a
camera matrix for this model.

### Step 2: Decode to linear 16-bit TIFF with camera white balance

```bash
dcraw -4 -T -w raw-file.CR2
```

This produces a 16-bit linear TIFF (`raw-file.tiff`) with camera-applied
white balance but NO color space profile. The file has:
- Linear gamma (radiometrically correct)
- Camera white balance applied
- No embedded ICC profile
- 16-bit per channel

### Step 3: Assign a camera input profile

The linear TIFF needs an ICC profile to be interpreted correctly by
color-managed software:

```bash
# Assign a camera input profile using ImageMagick
# (this does NOT convert — it tags the image so software knows
#  what the RGB values mean)
convert raw-file.tiff \
  -profile camera-input-profile.icc \
  raw-tagged.tiff
```

Camera input profiles can come from:
- **dcraw's built-in matrices** (`dcraw -v` shows the `adobe_coeff` values)
- **Custom ArgyllCMS profile** (photograph an IT8 target, use `scanin` + `colprof`)
- **DNG camera profile** (Adobe's DNG Profile format, `.dcp`)
- **Elle Stone's custom matrix profiles** (from the elles_icc_profiles repo)

### Step 4: Convert to a working space

```bash
# Convert to ProPhotoRGB for editing (preserves all captured colors)
convert raw-tagged.tiff \
  -profile camera-input-profile.icc \
  -profile ProPhotoRGB.icc \
  -intent Relative \
  -black-point-compensation \
  for-editing.tiff
```

**Important:** If you convert directly to sRGB here, you lose any colors
that exceed the sRGB gamut (see `references/srgb-versus-photographic-colors.md`
from the ninedegreesbelow.com archive). Use ProPhotoRGB or Rec.2020 for
the editing stage, and only convert to sRGB as the final output step.

### Step 5: Edit in high bit depth

The resulting TIFF is ready for:
- GIMP 2.9+/2.10 high bit depth editing
- Krita
- RawTherapee (though RawTherapee has its own raw decoder)
- Darktable (has its own raw decoder)

## The Negative Tristimulus Problem

Camera sensors don't see color the same way human eyes do. To accurately
map raw sensor values to human-visible colors, camera input profiles
require **negative XYZ tristimulus values**.

Analysis of 233 cameras from dcraw's `adobe_coeff` table:
- **100%** had negative green Z values
- **93%** had negative blue Y values
- **ALL cameras** had at least 2 negative tristimulus values

When a raw file is converted directly to sRGB during decoding, these
negative values are clipped, losing blue and green channel detail.

**The fix:** Decode to a large working space (ProPhotoRGB or Rec.2020)
at 16-bit, and use unbounded floating point conversions if available.
The negative values are real color information — clipping them destroys
it.

## dcraw Workarounds for Specific Cameras

### Sony A7 series

Sony A7 raw files have several issues documented by Elle Stone:

- **Lossy compression**: The A7 uses lossy 11-bit compression even for
  14-bit captures. No uncompressed option is available on early A7 models.
- **Star-eating algorithm**: Automatic noise reduction that can't be
  disabled removes faint stars in astrophotography.
- **Bulb mode drops to 12-bit**: Exposures longer than 30 seconds use
  only 12-bit ADC.
- **Continuous bracketing drops to 12-bit**: Using continuous mode for
  exposure bracketing cuts bit depth in half.

Mitigation: Use single-shot bracketing with `dcraw -4 -T` and manually
merge exposures. Consider tools like `align_image_stack` for alignment.

## Alternative Raw Processors

While dcraw is the canonical reference implementation, these tools build
on it with additional color management features:

| Tool | Based On | Color Mgmt Features |
|------|----------|-------------------|
| **RawTherapee** | Custom (dcraw-like) | Per-channel ICC profile assignment, DCP support, soft proofing, CIELAB editing |
| **Darktable** | Custom (RawSpeed) | Scene-referred workflow, ICC profile support, color check, display-referred toggle |
| **UFRaw** | dcraw | GIMP plugin, camera profile assignment dialog |
| **digiKam/showFoto** | dcraw (via libRaw) | Full CMS settings (Behavior + Profiles + Advanced tabs) |

The choice depends on your workflow:
- **dcraw CLI**: Fastest, scriptable, full control. Best for batch processing.
- **RawTherapee**: Most complete color management. Best for individual
  image development.
- **Darktable**: Scene-referred pipeline. Best for maximum dynamic range
  retention.
- **UFRaw**: Quick integration with GIMP editing.

## References

- dcraw documentation: https://www.cybercom.net/~dcoffin/dcraw/
- ninedegreesbelow.com: "Color Science History and ICC Profile
  Specifications" (negative tristimulus analysis)
- ninedegreesbelow.com: "Photographic Colors That Exceed sRGB"
- ArgyllCMS camera profiling: https://argyllcms.com/doc/Scenarios.html#PS4
- Elle Stone's annotated dcraw: ninedegreesbelow.com (dcraw C code outlined)
