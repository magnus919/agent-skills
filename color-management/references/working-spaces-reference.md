# Working Spaces Reference

Comparative data for common RGB working spaces used in ICC profile color management.

## Primary Data Table

| Working Space | Red xy | Green xy | Blue xy | White Point | Native Gamma | D50 Adapted? | Well-Behaved? |
|--------------|--------|----------|---------|-------------|--------------|--------------|----------------|
| sRGB | 0.6400, 0.3300 | 0.3000, 0.6000 | 0.1500, 0.0600 | D65 | ~2.2 (piecewise) | Yes (V4) | Many variants no |
| Rec.709 | 0.6400, 0.3300 | 0.3000, 0.6000 | 0.1500, 0.0600 | D65 | 2.4 (approx) | Yes | Same as sRGB |
| AdobeRGB (1998) | 0.6400, 0.3300 | 0.2100, 0.7100 | 0.1500, 0.0600 | D65 | 2.19921875 V2 / 2.2 V4 | Yes | Yes (all vendors) |
| ProPhotoRGB (ROMM) | 0.7347, 0.2653 | 0.1596, 0.8404 | 0.0366, 0.0001 | D50 | 1.80078125 V2 / 1.8 V4 | Native D50 | Approx (not all vendors) |
| WideGamutRGB | 0.7350, 0.2650 | 0.1150, 0.8260 | 0.1570, 0.0180 | D50 | 2.19921875 V2 / 2.2 V4 | Native D50 | Canon only |
| AppleRGB | 0.6250, 0.3400 | 0.2800, 0.5950 | 0.1550, 0.0700 | D65 | 1.8 | Yes | No |
| ColorMatchRGB | 0.6300, 0.3400 | 0.2950, 0.6050 | 0.1500, 0.0750 | D50 | 1.8 | Native D50 | No |
| CIE RGB | 0.7350, 0.2650 | 0.2740, 0.7170 | 0.1670, 0.0090 | E (ASTM) | Linear | N/A | ~ |
| BetaRGB | 0.6888, 0.3112 | 0.1986, 0.7551 | 0.1265, 0.0352 | D50 | 2.2 | Native D50 | Yes |
| ACES | 0.7347, 0.2653 | 0.0000, 1.0000 | 0.0001, -0.0770 | D60 | Linear | D60 | Yes |
| ACEScg | 0.7130, 0.2930 | 0.1650, 0.8300 | 0.1280, 0.0440 | D60 | Linear | D60 | Yes |
| Rec.2020 | 0.7080, 0.2920 | 0.1700, 0.7970 | 0.1310, 0.0460 | D65 | ~0.45 (piecewise) | Yes | Yes |
| BruceRGB | 0.6400, 0.3300 | 0.2800, 0.6500 | 0.1500, 0.0600 | D65 | 2.2 | Yes | ~ |
| eciRGB | 0.6700, 0.3300 | 0.2100, 0.7100 | 0.1400, 0.0800 | D50 | 1.8 | Native D50 | Yes |
| PAL/SECAM | 0.6400, 0.3300 | 0.2900, 0.6000 | 0.1500, 0.0600 | D65 | 2.2 | Yes | ~ |

## Luminance (Y) for Primary Colors

| Working Space | Red Y | Green Y | Blue Y | White Y |
|--------------|-------|---------|--------|---------|
| sRGB | 0.2126 | 0.7152 | 0.0722 | 1.0000 |
| AdobeRGB | 0.2973 | 0.6274 | 0.0753 | 1.0000 |
| ProPhotoRGB | 0.2880 | 0.7110 | 0.0001 | 1.0000 |
| Rec.2020 | 0.2627 | 0.6780 | 0.0593 | 1.0000 |
| ACEScg | 0.2722 | 0.6741 | 0.0537 | 1.0000 |

## Gamut Volume Comparison (relative to sRGB)

| Working Space | Approximate Volume |
|--------------|-------------------|
| sRGB | 1.0× (baseline) |
| AppleRGB | 0.96× |
| AdobeRGB | 1.24× |
| BetaRGB | 1.33× |
| WideGamutRGB | 1.80× |
| Rec.2020 | 1.94× |
| ProPhotoRGB | 2.08× |
| ACEScg | 2.15× |
| ACES | 5.00× (includes many imaginary colors) |
| AllColorsRGB | ~5.5× |

## sRGB Profile Variant Comparison

A survey of 13 sRGB profiles from major vendors:

| Source | Filename | Well-Behaved? | L* at 255 | a* at 255 | b* at 255 |
|--------|----------|--------------|-----------|-----------|-----------|
| ArgyllCMS | sRGB.icm | **Yes** ✅ | 100.000000 | 0.000000 | 0.000000 |
| Shared (colord) | sRGB.icm | **Yes** ✅ | 100.000000 | 0.000000 | 0.000000 |
| Krita built-in | krita-built-in.icc | ~ | 100.000600 | -0.002500 | 0.002300 |
| digiKam | srgb-d65.icm | ~ | 100.000590 | -0.002543 | 0.002250 |
| LCMS (code) | lcmsCreate_sRGB.icc | ~ | 100.000590 | -0.002543 | 0.002250 |
| OpenICC | sRGB.icc | ~ | 100.000590 | -0.002543 | 0.002250 |
| Canon | sRGB profile | ~ | 100.000590 | -0.002543 | 0.001017 |
| Krita | sRGB.icm | **NO** ❌ | 100.001200 | -2.390200 | -19.404000 |
| Adobe | sRGB Color Space Profile.icm | **No** ❌ | 99.998820 | 0.018274 | -0.016832 |
| color.org | sRGB_IEC61966-2-1_black_scaled.icc | **No** ❌ | 99.998820 | 0.018274 | -0.016832 |
| LCMS v1 | sRGB Color Space Profile.ICM | **No** ❌ | 99.998820 | 0.018274 | -0.016832 |
| Windows 2000 | sRGB.icm | **No** ❌ | 99.998820 | 0.018274 | -0.016832 |

**Warning**: The Krita `sRGB.icm` (unadapted primaries) causes a cyan-blue color cast. Never use it for editing.

## Guide to Choosing a Working Space

| If you... | Use this working space | Notes |
|-----------|----------------------|-------|
| Export images to web | sRGB (V2 for Firefox compat) | Web standard; use ArgyllCMS or Elle's profiles |
| Print on wide-gamut printer | AdobeRGB, ProPhotoRGB, or Rec.2020 | Match the printer gamut |
| Edit raw files (high bit depth) | Rec.2020 or ACEScg | Better chromaticity performance than ProPhotoRGB |
| Work in VFX/film pipeline | ACEScg | Industry standard; linear gamma |
| Edit 8-bit images | sRGB (small gamut, perceptually uniform) | Avoid posterization |
| Need radiometrically correct results | Linear gamma (g10) variant | Use only at 16-bit+ to avoid posterization |
| Want to edit color and tonality separately | Any + use LCH blend modes | GIMP 2.9+/2.10 required |

## TRC (Tone Reproduction Curve) Reference

| TRC Name | Formula/Type | Use Case |
|----------|-------------|----------|
| Linear (gamma 1.0) | value = code / max | Radiometrically correct editing |
| sRGB | Piecewise: linear slope near 0, ~2.4 gamma above | Web standard, display |
| Gamma 1.8 | value = (code/max)^(1/1.8) | ProPhotoRGB native, Apple displays |
| Gamma 2.2 | value = (code/max)^(1/2.2) | AdobeRGB, Windows displays |
| Rec.709 | ~gamma 2.4 (piecewise) | HDTV broadcast standard |
| LAB L | Perceptually uniform | CIELAB L* encoding, LCH editing |

## Recommended Profiles

For well-behaved profiles that are free to use, the best sources are:

1. **ArgyllCMS** (`sRGB.icm`, `ClayRGB.icm` = AdobeRGB compatible) — ArgyllCMS/ref/ folder
2. **Elle Stone's profiles** — github.com/ellelstone/elles_icc_profiles — V2 and V4, all well-behaved
3. **Krita 2.9+** — ships with well-behaved profiles as of February 2015
4. **colord Shared Color Profiles** — Linux package manager

Avoid profiles from: LCMS built-in (not well-behaved for sRGB/AdobeRGB), color.org (copyright encumbered), and old camera vendor profiles (may not be well-behaved).
