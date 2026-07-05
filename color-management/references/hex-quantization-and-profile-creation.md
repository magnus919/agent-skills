# Hexadecimal Quantization & Profile Creation

How decimal-to-hexadecimal rounding affects ICC profile neutrality and
the methodology for creating well-behaved working space profiles.

Source: ninedegreesbelow.com — "In Quest of Well Behaved Working Spaces"
by Elle Stone (September 2013, updated March 2015).

---

## What is Hexadecimal Quantization?

ICC V2 profiles encode values using the s15Fixed16 number format — a
fixed-point representation where values are stored as 32-bit signed integers
with 16 fractional bits. When decimal chromaticity coordinates (like
x=0.6400, y=0.3300) are converted to this format, rounding occurs.

This rounding — called **hexadecimal quantization** — propagates through
the D50 chromatic adaptation calculation that every ICC profile must
perform. Even a rounding error of 0.0001 in the xy coordinates produces a
measurable deviation in the final profile's a*/b* neutrality.

For example, the sRGB D65 white point has at least 6 different "official"
published values depending on which standard you consult (ASTM E308-01,
correlated color temperature calculations, ICC V4 specifications, etc.).
The differences between these values are smaller than the quantization
step, yet they produce profiles that differ at the 4th decimal place of
a*/b* — enough to be detected by `xicclu -pl` at 6 decimal places.

## Why It Matters

A deviation of 0.001 in a* at white point (R=G=B=255) is invisible at
8-bit but becomes measurable at 16-bit+ after extreme editing:

- Levels adjustments that amplify channel differences also amplify the
  embedded neutrality error
- Channel Mixer operations magnify the offset
- At 32-bit floating point, the error is fully preserved and compounds
  across multiple edits

The practical impact: a profile that is "almost well-behaved" (a*=0.003
instead of 0.000) will produce a false color cast if you apply extreme
Curves or Levels to a 16-bit image. The cast is real but artifactual —
it comes from the profile, not the image.

## Which Profiles Are Affected

**Well-behaved (no hex quantization issue):**
- AdobeRGB1998 (all vendors) — because Adobe published the *D50-adapted*
  XYZ primaries directly, avoiding the D50 adaptation step entirely
- ArgyllCMS `sRGB.icm` — uses pre-quantized primaries
- colord `Shared sRGB.icm` — same source as ArgyllCMS
- Krita built-in sRGB (as of February 2015+)
- Canon `WideGamut` — vendor-corrected
- All profiles made from properly pre-quantized primaries

**Not well-behaved (affected by hex quantization):**
- sRGB profiles from Adobe, color.org, Windows 2000, LCMS v1
- ProPhotoRGB from OpenICC, digiKam, Canon (shared source)
- AppleRGB from Adobe, colord Shared
- ColorMatchRGB from colord Shared
- WideGamut from digiKam, Krita (non-Canon versions)

## The Fix: Pre-quantized Primaries

The methodology, documented by Elle Stone:

### 1. Get correctly quantized D50-adapted XYZ values

ArgyllCMS source code (`src/mkDispProf.c`) calculates the D50-adapted
XYZ primaries accounting for hexadecimal rounding. Use ArgyllCMS to
generate a reference profile, then extract its adapted primaries:

```bash
# Generate a profile with ArgyllCMS to get properly quantized values
colprof -v -qh -D "Reference Profile" -As reference.ti3

# Extract the D50-adapted XYZ values for Re, Gr, Bl matrix columns
xicclu -fif -ir reference.icc
```

### 2. Back-Bradford-adapt to source white point

Using a spreadsheet or script, reverse the chromatic adaptation to
recover "pre-quantized" unadapted xy values:

```
Given: D50-adapted XYZ primaries (from ArgyllCMS)
Given: Source white point (e.g., D65 xy = 0.3127, 0.3290)
1. Bradford-adapt the primaries from D50 back to the source white point
2. Convert resulting XYZ to xy chromaticity coordinates
3. These xy values, when fed through the forward adaptation in LCMS,
   produce the same correctly-quantized D50-adapted values
```

### 3. Feed pre-quantized xy values to LCMS

Use the recovered xy values in your LCMS profile creation code:

```c
cmsCIExyY red_primary   = { 0.6400, 0.3300, 1.0 };
cmsCIExyY green_primary = { 0.3000, 0.6000, 1.0 };
cmsCIExyY blue_primary  = { 0.1500, 0.0600, 1.0 };
```

Replace with pre-quantized values from step 2.

### 4. Verify with xicclu at 6 decimal places

```bash
echo "255 255 255" | xicclu -ir -pl -s255 -v0 my-profile.icc
# Expected: 100.000000 0.000000 0.000000

echo "128 128 128" | xicclu -ir -pl -s255 -v0 my-profile.icc
# Expected: <L* around 54> 0.000000 0.000000

echo "0 0 0" | xicclu -ir -pl -s255 -v0 my-profile.icc
# Expected: 0.000000 0.000000 0.000000
```

## Profiles That Don't Need Pre-quantization

AdobeRGB1998 is the notable exception. Adobe's published specification
includes the D50-adapted XYZ values directly:

```
Red   D50-adapted: X=0.60974, Y=0.31111, Z=0.01947
Green D50-adapted: X=0.20528, Y=0.62567, Z=0.06087
Blue  D50-adapted: X=0.14919, Y=0.06322, Z=0.74457
```

Because these are already in the D50-adapted form that ICC profiles use
internally, no chromatic adaptation step is needed, and hexadecimal
quantization of the *adaptation math* is avoided. All vendors' AdobeRGB
profiles are well-behaved for this reason.

## Practical Implications

| Use Case | Impact |
|----------|--------|
| 8-bit editing | None — quantization is below 8-bit precision |
| 16-bit editing | Minimal — extreme edits may show <0.5 dE shift |
| 32-bit float editing | Measurable — use well-behaved profiles |
| Soft proofing | Affects proof accuracy at high precision |
| Scientific/archival | Always use well-behaved profiles |

**Recommendation:** Standardize on ArgyllCMS profiles or Elle Stone's
profile pack (github.com/ellelstone/elles_icc_profiles) for any working
space where neutrality matters. Avoid the color.org/Adobe v2/LCMS v1
sRGB variants, the OpenICC ProPhotoRGB, and the colord Shared AppleRGB.

## References

- Elle Stone's well-behaved ICC profiles and code:
  https://ninedegreesbelow.com/photography/lcms-make-icc-profiles.html
- ArgyllCMS source: `src/mkDispProf.c` — the canonical compensation
- Bruce Lindbloom: chromatic adaptation equations and working space data:
  http://www.brucelindbloom.com/
- LittleCMS: http://www.littlecms.com/
