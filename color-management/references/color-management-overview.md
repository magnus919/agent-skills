# Color Management Overview

Foundational concepts for understanding ICC profile color management, derived from the work of Elle Stone (ninedegreesbelow.com) and Bruce Lindbloom.

## Reference Color Spaces

### CIE 1931 XYZ
- Mathematically derived from 1920s Wright/Guild experiments where observers matched test colors by mixing RGB primaries
- Y = luminance (brightness); X, Z carry chromaticity information
- Made "just positive enough" for paper-and-pencil calculations (not physical reality)
- Camera sensors don't see like humans — accurate camera profiles require negative XYZ values

### CIE xyY
- Chromaticity diagram: x = X/(X+Y+Z), y = Y/(X+Y+Z), Y = Y (luminance)
- The "horseshoe" = all visible colors as xy projection (looking down Y axis)
- Wavelengths marked around edge (380nm blue-violet to 700nm red)
- Straight line at bottom = purple/magenta (construct of eye-brain, not spectral)
- sRGB, ProPhotoRGB, etc. are triangles inside the horseshoe

### CIELAB (CIE L*a*b*)
- Perceptually uniform transform of XYZ
- L* = lightness (0-100), a* = green-red (-128 to +127), b* = blue-yellow (-128 to +127)
- R=G=B = neutral gray (a*=b*=0) in a well-behaved working space
- L* = 100, a* = 0, b* = 0 = solid white; L* = 0, a* = 0, b* = 0 = solid black
- CIELAB clipping: many editors clip a*/b* to ±128, losing real visible colors; LCMS2 unbounded mode can avoid this

### LCH
- Polar transform of CIELAB: Lightness (same as L*), Chroma (saturation from gray), Hue (color angle)
- Allows separate editing of tonality (Lightness) from color (Chroma + Hue)
- GIMP's LCH blend modes (Lightness, Chroma, Hue) are the first correct open-source implementation

## ICC Profile Types

### Matrix Profiles
- Define color space via 3×3 matrix + Tone Reproduction Curve (TRC)
- Examples: sRGB, AdobeRGB, ProPhotoRGB, Rec.2020, ACEScg
- **Only support colorimetric intents** (relative and absolute — NOT perceptual or saturation)
- Smaller file size, computationally cheaper
- Cannot be used for soft proofing with perceptual intent

### Lookup Table (LUT) Profiles
- Define color space via tables of corresponding RGB↔XYZ/Lab values
- Examples: Most monitor profiles, printer profiles, camera input profiles
- Can support all four conversion intents
- Larger file size, more accurate for device characterization

## ICC Profile Conversion Intents

Only four intents exist. Matrix profiles only support #1 and #2.

### 1. Relative Colorimetric
- **With BPC (black point compensation)**: Align white points and black points; scale gray axis; clip out-of-gamut colors to destination surface. **Default for display.**
- **Without BPC**: Same but don't scale black point. Darkest colors crushed to black on LCD monitors.
- Effect: Colors that fit in destination gamut are preserved exactly. Out-of-gamut colors clip to nearest in-gamut color.

### 2. Absolute Colorimetric
- Don't align white points. Clip out-of-gamut colors.
- Use: proofing to simulate paper white color (e.g., simulating how a print will look on newsprint).
- V4 ICC change: for matrix-to-matrix conversions, absolute colorimetric may silently become relative colorimetric (controversial).

### 3. Perceptual
- Scale the entire color gamut to fit the destination gamut. Relationships preserved, absolute accuracy sacrificed.
- **Only available with LUT destination profiles.** Matrix profiles silently substitute relative colorimetric.
- Use: photographic reproduction where preserving gradations matters more than matching specific colors.

### 4. Saturation
- Preserve saturation at expense of hue and lightness.
- **Only available with LUT destination profiles.** Matrix profiles silently substitute relative colorimetric.
- Use: business graphics/charts where vivid colors matter.

## "Well-Behaved" Working Space Criteria

A working space is "well-behaved" when:

1. **Color balanced**: if R=G=B anywhere in the space, the color is neutral gray (a*=b*=0 in CIELAB)
2. **Normalized**: R=G=B=0 = solid black (0,0,0); R=G=B=max = solid white (100,0,0)

**Why this matters**: At high bit depths, a not-quite-well-behaved profile can introduce a false color cast during extreme edits (extreme levels adjustments, channel mixing). At 8-bit, the deviations are too small to notice.

**Reality check**: A survey of 30 widely-distributed profiles found only 9 were completely well-behaved (5 AdobeRGB, 3 sRGB, 1 WideGamut). Many well-known profiles (ProPhotoRGB, AppleRGB, ColorMatchRGB) are only approximately well-behaved. See `working-spaces-reference.md` for details.

**How to test**: `xicclu -ir -pl -s255 -v0 profile.icc` — enter 255 255 255 and check output is 100.000000 0.000000 0.000000.

## Display-Referred vs Scene-Referred

| Property | Display-Referred | Scene-Referred |
|----------|-----------------|----------------|
| Max value | 1.0 (solid white) | Unlimited |
| Min value | 0.0 (solid black) | 0.0 |
| Dynamic range | ~9 stops | 20+ stops (OpenEXR) |
| Clamping | Operations clip to 0-1 | No clamping |
| White (1,1,1) | Max brightness | Just another gray point |
| Best for | Web, print output | HDR, maximum editing flexibility |
| Gamma required | Any (sRGB TRC typical) | Linear only (radiometric correctness) |

## LCMS2 Unbounded Mode

When all three conditions are met:
1. 32-bit floating point precision
2. True gamma TRC profiles (not point curves — true gamma=1.0, 1.8, etc.)
3. File format supporting extended range (OpenEXR, PFM, floating-point TIFF)

...LCMS2 unbounded mode enables **lossless** ICC profile conversions. Colors that would be clipped to the destination gamut surface instead get negative or >1.0 RGB values. Bruce Lindbloom's RGB16Million test image: bounded conversion altered 12.5M of 16M pixels; unbounded was completely lossless.

**Warning**: Multiply/divide operations on out-of-gamut colors (negative channel values) produce meaningless results. Addition/subtraction is fine.

## Color Difference (dE)

Standard metrics for quantifying the perceptual difference between two colors:

- **CIE76 (dE*ab)**: Simple Euclidean distance in CIELAB. Does not account for perceptual non-uniformities.
- **CIE94**: Corrects for non-uniformity in blue regions. Used in textile and printing industries.
- **CIEDE2000 (dE00)**: Most accurate perceptual metric. Accounts for hue, chroma, and lightness interactions. **Preferred for quality assessment.**
- **CMC l:c**: Used in textile industry. Two parameters (luminance and chroma weighting).

## Chromaticity-Dependent vs Independent Operations

57% of common editing operations are chromaticity-dependent — they produce different results in different RGB working spaces. Key examples:

**Chromaticity-independent** (results same in any linear gamma space):
- Normal, Addition, Subtract blend modes
- Gaussian Blur, Unsharp Mask
- Scaling, rotation, transforms
- Value channel Levels (upper/lower sliders)
- Desaturate to Luminance
- Invert Colors

**Chromaticity-dependent** (results differ by working space):
- Multiply, Divide, Screen, Overlay blend modes (and all derivative modes)
- Curves
- Per-channel Levels
- Color Balance, Channel Mixer
- Hue, Saturation, Color, Value blend modes
- Color correction (white balance eyedropper)
- Levels gamma slider adjustment

**Implication**: There is no "universal" working space for editing. The choice of chromaticities matters for chromaticity-dependent operations. Unbounded sRGB is fine for *display* but produces wrong results for many editing operations.
