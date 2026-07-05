# CLI Tool Reference

Quick commands and usage patterns for color management tools.

## ImageMagick

| Command | Purpose |
|---------|---------|
| `convert -profile` | Apply ICC profile (assign or convert) |
| `identify -verbose` | Full image metadata (including ICC) |
| `composite -compose difference` | Pixel-difference comparison |
| `convert +profile icc` | Strip ICC profile |
| `compare -metric AE` | Count differing pixels |
| `convert -black-point-compensation` | Enable BPC |
| `convert -intent` | Set rendering intent |

### Advanced: Profile conversion with BPC
```bash
convert input.tif \
  -profile sRGB.icm \
  -black-point-compensation \
  -intent Relative \
  -profile ProPhotoRGB.icc \
  output.tif
```

### Advanced: Batch strip profiles
```bash
for f in *.jpg; do convert "$f" +profile icc "stripped/$f"; done
```

### Advanced: Create 3D LUT
```bash
# Create a cube LUT from source to destination profile
convert -profile sRGB.icm -profile ProPhotoRGB.icc hald:8 hald.png
```

## Exiftool

| Command | Purpose |
|---------|---------|
| `exiftool -ICC_Profile:all` | Show ICC profile metadata |
| `exiftool -ICC_Profile=` | Remove ICC profile |
| `exiftool -ICC_Profile<=profile.icc` | Embed ICC profile |
| `exiftool -a -S -G0` | Show all metadata groups |
| `exiftool -b -ICC_Profile` | Extract ICC profile binary |

## ArgyllCMS

| Command | Purpose |
|---------|---------|
| `xicclu -ir -pl` | Interactive CIELAB lookup from RGB |
| `iccgamut -ir` | Generate gamut file from profile |
| `viewgam -w` | Convert gamut to VRML visualization |
| `cctiff` | Color-correct TIFF files |
| `tificc` | LCMS-based TIFF conversion |
| `colprof` | Create profiles from measurement data |
| `dispcal` | Display calibration |
| `dispread` | Display measurement |
| `extracticc` | Extract embedded ICC from image |
| `scanin` | Process scanner/camera target measurements |

## dcraw

| Command | Purpose |
|---------|---------|
| `dcraw -c -w file.CR2` | Decode with camera white balance |
| `dcraw -T file.CR2` | Decode to TIFF |
| `dcraw -4 -D file.CR2` | Linear raw data (no interpolation) |
| `dcraw -i -v file.CR2` | Show raw metadata |

## LittleCMS Utilities

| Command | Purpose |
|---------|---------|
| `tificc` | TIFF ICC profile conversion |
| `transicc` | Interactive color lookup (stdin/stdout) |
| `jpgicc` | JPEG ICC profile conversion |

## Raw Processors

| Tool | Color Management Features |
|------|--------------------------|
| **RawTherapee** | Per-channel ICC profiles, DCP support, soft proofing |
| **Darktable** | Scene-referred workflow, ICC profile support, color check |
| **digiKam/showFoto** | Full CMS settings (Behavior + Profiles + Advanced tabs) |
| **UFRaw** | GIMP plugin, dcraw-based, camera profile assignment |

## Monitor Calibration Hardware Compatibility

ArgyllCMS supports these color measuring instruments (see argyllcms.com for current list):
- X-Rite: ColorMunki, i1Display Pro, i1Pro, i1Studio
- Datacolor: Spyder series
- Colorimetry Research: CR-100, CR-250
- Klein: K-10 series

## Useful Color Science Websites

| Resource | URL |
|----------|-----|
| Bruce Lindbloom | www.brucelindbloom.com |
| Cambridge in Colour | www.cambridgeincolour.com |
| ICC (International Color Consortium) | www.color.org |
| Wolf Faust IT8 Targets | www.colorreference.de |
| ArgyllCMS | www.argyllcms.com |
| LittleCMS | www.littlecms.com |
| Elle Stone's Profiles | github.com/ellelstone/elles_icc_profiles |
