# ICC Profile Operations

Practical guide for common ICC profile operations using CLI tools.

## ImageMagick

### Convert image from one color space to another
```bash
# Convert from sRGB to ProPhotoRGB (relative colorimetric)
convert input.jpg -profile sRGB.icm -profile ProPhotoRGB.icc output.tif

# Specify rendering intent: 0=Perceptual, 1=Relative, 2=Saturation, 3=Absolute
convert input.jpg -intent Relative -profile sRGB.icm -profile ProPhotoRGB.icc output.tif

# With black point compensation
convert input.jpg -black-point-compensation -profile sRGB.icm -profile ProPhotoRGB.icc output.tif
```

### Assign vs Convert
```bash
# ASSIGN (reinterpret existing RGB numbers with new profile — colors change)
convert input.jpg -profile sRGB.icm input-assigned.jpg   # if untagged
convert input.jpg -set profile 'sRGB.icm' input-assigned.jpg  # force assign over existing

# CONVERT (preserve colors, change RGB numbers)
convert input.jpg -profile sRGB.icm -profile ProPhotoRGB.icc output.tif
```

### Extract embedded ICC profile
```bash
convert input.jpg profile.icc
identify -verbose input.jpg | grep -A 100 "Profile-icc"
```

### Strip ICC profile
```bash
convert input.jpg +profile icc output.jpg
```

### Get image color space info
```bash
identify -verbose input.jpg | grep -E "Type:|Colorspace:|Profile-icc"
```

### Create difference image for comparing before/after
```bash
composite -compose difference before.tif after.tif difference.tif
convert difference.tif -fill white +opaque "rgb(0,0,0)" histogram.png
```

### Count pixels altered by a conversion
```bash
composite -compose difference original.tif converted.tif diff.tif
convert diff.tif -fill white +opaque "rgb(0,0,0)" -format %c histogram:info:
# Black pixels = unchanged; White pixels = altered
```

## ArgyllCMS

### Check if a profile is well-behaved
```bash
# Interactive mode — type "255 255 255" then "0 0 0" then "128 128 128"
xicclu -ir -pl -s255 -v0 profile.icc

# Non-interactive: echo values to stdin
echo "255 255 255" | xicclu -ir -pl -s255 -v0 sRGB.icm
# Expected: 100.000000 0.000000 0.000000 for well-behaved at white

echo "0 0 0" | xicclu -ir -pl -s255 -v0 sRGB.icm
# Expected: 0.000000 0.000000 0.000000

echo "128 128 128" | xicclu -ir -pl -s255 -v0 sRGB.icm
# Expected: L* around 53-54, a*=b*=0.000000
```

### Create a VRML gamut visualization
```bash
iccgamut -ir profile.icc profile.gam
viewgam -w profile.gam profile.wrl
# Open profile.wrl in a VRML viewer (view3dscene, etc.)
```

### Convert between color spaces
```bash
# Using cctiff (Argyll CMS color conversion TIFF tool)
cctiff -i source_profile.icc -o dest_profile.icc input.tif output.tif

# Specify intent: -t 0=Perceptual, 1=Relative colorimetric, 2=Saturation, 3=Absolute
cctiff -t 1 -i sRGB.icm -o ProPhotoRGB.icc input.tif output.tif
```

### Extract embedded ICC profile
```bash
extracticc input.jpg extracted_profile.icc
```

### Profile a monitor (requires hardware colorimeter)
```bash
# See full ArgyllCMS documentation at https://argyllcms.com/
# Typical workflow:
# 1. dispcal -v -d 1 -t 6500 -g 2.2 -f 2.0 calibration_target
# 2. dispread -v -d 1 calibration_target
# 3. colprof -v -qh -D "My Monitor Profile" calibration_target
```

### Profile a camera (requires IT8 target)
```bash
# 1. Photograph an IT8 target
# 2. Extract target values from the image
# 3. Run:
scanin -v targ_file.it8 target_measurements.ti3
colprof -v -qh camera_profile.icc target_measurements.ti3
```

## Exiftool

### Show all ICC profile metadata
```bash
exiftool -ICC_Profile:all -G image.jpg
```

### Show color space metadata (DCF tags)
```bash
exiftool -ColorSpace -InteropIndex -WhitePoint -PrimaryChromaticities -Gamma image.jpg
```

### Show all metadata (quick overview)
```bash
exiftool -a -S -G0 -ColorSpace -InteropIndex -ICC_Profile:all image.jpg
```

### Remove embedded ICC profile
```bash
exiftool -ICC_Profile= image.jpg
# Makes backup: image.jpg_original
```

### Embed an ICC profile
```bash
exiftool -ICC_Profile<=profile.icc image.jpg
```

## LittleCMS (LCMS2)

### Convert image using tificc
```bash
# Bounded mode (standard):
tificc -c 0 -w 16 -e -t 1 -i source.icc -o dest.icc input.tif output.tif

# Unbounded mode (32-bit floating point, requires true gamma TRC profiles):
tificc -c 0 -w 32 -e -t 1 -i source-g100.icc -o dest-g100.icc input.tif output.tif
```

### tificc parameters:
- `-c 0`: 0=use LCMS, 1=use built-in sRGB
- `-w 16|32`: bit depth (16 or 32)
- `-e`: embed source profile in output
- `-t 0|1|2|3`: intent (Perceptual, Relative, Saturation, Absolute)
- `-i profile.icc`: source profile
- `-o profile.icc`: destination profile

### Interactive lookup with transicc
```bash
# Start interactive session:
transicc -w

# Or pipe values:
echo "128 128 128" | transicc -w
```

### Check profile type and capabilities
```bash
# transicc can reveal whether a profile uses matrix or LUT tables
transicc -v profile.icc 2>&1 | head -20
```

## Firefox Color Management

### about:config settings for Linux/Firefox:
```
gfx.color_management.enabled = true
gfx.color_management.mode = 1         (0=off, 1=full, 2=tagged only)
gfx.color_management.display_profile = /path/to/your/monitor/profile.icc
```

### Firefox limitations:
- Does NOT support black point compensation as of 2015 (and likely since)
- Dropped LittleCMS after a security alert — rolled their own CMS
- V4 profiles may not work; use V2 for web export
- Shadow details will appear more crushed than in color-managed editors

## GIMP 2.9+/2.10 Color Management

### Key settings:
- Display rendering intent: Relative colorimetric with BPC (default)
- Only edit sRGB images — GIMP has hard-coded sRGB parameters
- LCH blend modes are a game-changer: separate Lightness, Chroma, Hue groups
- For radiometrically correct editing: use "Linear light" precision
- For safe out-of-gamut avoidance: use integer precision (clips automatically)

### LCH Layer Setup (from Elle Stone's tutorial):
1. Duplicate scene-referred layer
2. Create three layer groups: Lightness (LCh Lightness mode), Chroma (LCh Chroma mode), Hue (LCh Hue mode)
3. Put layer copies in each group
4. Edit Chroma with Channel Mixer + Chroma mask from LCH decompose
5. Edit Lightness with Exposure, Curves, High Pass (desaturate each layer to Luminance first)
6. Edit Hue with Hue-Chroma tool
7. Outside of gamut colors: monitor with Color Picker + Sample Points
8. Before export: soft proof or clip to gamut
