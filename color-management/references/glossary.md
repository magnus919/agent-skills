# Color Management Glossary

| Term | Definition |
|------|------------|
| **BPC** | Black Point Compensation. LCMS2 algorithm that maps source black point to destination black point so darkest shadows aren't crushed. Essential for LCD monitors (which can't display true black). |
| **Chromaticity** | Color quality defined by hue and saturation, independent of luminance. Expressed as xy coordinates in the CIE xyY chromaticity diagram. |
| **Chromaticity coordinates** | The xy values that define a color's position in the chromaticity diagram. Working space primaries are defined by their chromaticity coordinates. |
| **CIELAB (CIE L*a*b*)** | Perceptually uniform reference color space derived from XYZ. L* = lightness, a* = green-red, b* = blue-yellow. Primary reference space for ICC profile conversions. |
| **Clipping** | Loss of color information when out-of-gamut colors are forced to the nearest in-gamut values. Occurs during conversions to smaller color spaces. |
| **Color gamut** | The subset of all visible colors that a device (monitor, printer, camera) can reproduce or a working space can encode. |
| **Color space** | A method of representing color numerically. RGB, CMYK, CIELAB, and xyY are different "color spaces" — they define different coordinate systems for the same colors. |
| **Conversion (ICC profile)** | Changing an image from one color space to another. Colors are preserved; RGB numbers change. |
| **D50** | Standard illuminant — 5000K daylight. ICC profile connection space (PCS) uses D50 as the reference white point. |
| **D65** | Standard illuminant — 6500K daylight. sRGB's white point. Roughly corresponds to daylight on a slightly overcast day. |
| **dcraw** | Dave Coffin's open-source raw file decoder. Supports essentially every digital camera ever made. The foundation of most open-source raw workflows. |
| **Display-referred** | Image data where RGB values are bounded by 0.0-1.0, where (1,1,1) = maximum display white. Standard for web and print output. |
| **Embedded profile** | An ICC profile stored in the image file's metadata. Tells color-managed software how to interpret the image's RGB values. |
| **Gamut** | See **Color gamut**. |
| **Hex quantization** | Rounding of ICC profile values during the encoding process because ICC V2 format uses 16-bit integer encoding. Causes minor deviations from mathematical ideal. ArgyllCMS compensates for this; LCMS does not. |
| **Imaginary colors** | Colors that can be encoded in a working space but don't correspond to any real visible color. ProPhotoRGB and ACES include many imaginary colors — this is deliberate, to capture all possible real colors. |
| **Input profile** | A profile that describes how a device (camera, scanner) captures color. Camera input profiles often require negative tristimulus values. |
| **LCMS** | LittleCMS (LCMS2). The open-source color management engine used by GIMP, Krita, digiKam, RawTherapee, and most Linux imaging software. |
| **LCH** | Lightness, Chroma, Hue — a polar transform of CIELAB. Allows separate editing of tonality (Lightness) and color (Chroma + Hue). |
| **LUT profile** | A profile defined by lookup tables rather than matrix math. Required for perceptual intent. Printer profiles and many monitor profiles are LUT. |
| **Matrix profile** | A profile defined by a 3×3 matrix + TRC. Simpler, smaller, but cannot support perceptual or saturation intents. All standard working spaces (sRGB, ProPhotoRGB, etc.) are matrix. |
| **Monitor profile** | An ICC profile describing a specific monitor's color behavior. Created by measuring the monitor with a hardware colorimeter + ArgyllCMS or proprietary software. |
| **Negative tristimulus** | XYZ or RGB values below zero. Required for accurate camera profiles because camera sensors don't see like human eyes. ICC V2 prohibited them; V4 allows via floating point. |
| **Perceptual uniformity** | A property where equal numerical changes produce equal perceptual changes. CIELAB is approximately perceptually uniform; XYZ is not. |
| **Primary** | The most intense red, green, or blue color a color space can encode. Working spaces are defined by their primaries' locations in XYZ/xyY. |
| **Profile** | See **ICC profile**. |
| **Profile Connection Space (PCS)** | The reference color space (CIELAB or XYZ) used for ICC profile conversions. All profiles define their color gamut relative to the PCS. |
| **Radiometrically correct** | Editing that accurately models how light behaves in the real world. Requires linear gamma RGB and appropriate blend modes. |
| **Reference color space** | A mathematically defined color space that encompasses all visible colors. XYZ and CIELAB are reference spaces. |
| **Relative colorimetric** | Conversion intent that preserves in-gamut colors exactly and clips out-of-gamut colors to the nearest in-gamut equivalent. The standard intent for display. |
| **Scene-referred** | Image data proportional to the original scene's light intensities. No upper bound on RGB values. Used for HDR and maximum editing flexibility. |
| **Soft proofing** | Previewing how an image will look when converted to a different (usually smaller) color space, before actually doing the conversion. Essential for avoiding unwanted clipping. |
| **sRGB** | Color space created by HP and Microsoft in 1996 to match CRT monitor phosphors. The universal standard for web images. Too small for many photographic colors. |
| **TRC** | Tone Reproduction Curve. Defines how RGB values map to linear light intensity. Gamma curves, sRGB piecewise curve, and LAB L curves are examples. |
| **Tristimulus values** | Three numbers (e.g., RGB, XYZ) that define a color in a three-dimensional color space. Based on the trichromatic theory of human color vision. |
| **Unbounded conversion** | ICC profile conversion at 32-bit floating point that allows negative and >1.0 RGB values, preventing gamut clipping. Requires true gamma TRC profiles. |
| **Well-behaved** | A working space where R=G=B produces neutral gray (a*=b*=0) and R=G=B=0 produces true black. Only ~9 of 30 surveyed profiles are fully well-behaved. |
| **Working space** | A well-behaved color space used for editing images. sRGB, AdobeRGB, and ProPhotoRGB are common working spaces. |
| **xyY** | A reference color space that separates chromaticity (xy) from luminance (Y). The xy projection is the familiar "horseshoe" chromaticity diagram. |
| **XYZ** | The 1931 CIE standard reference color space. All color management ultimately traces back to XYZ. |
