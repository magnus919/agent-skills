# LCH Layer Stack Template

A repeatable layer group architecture for editing tonality and color
separately using GIMP 2.9+/2.10 LCH blend modes.

Source: ninedegreesbelow.com "Autumn Colors" tutorial by Elle Stone.

---

## Layer Group Structure

Create three layer groups, each set to a different LCH blend mode:

```
┌─ Chroma (mode: Chroma LCh) ─────────────────────┐
│   Layer: Scene-referred base (mode: Normal)       │
│   Layer: Channel Mixer (mode: Normal, masked)      │
└────────────────────────────────────────────────────┘
┌─ Lightness (mode: Lightness LCh) ────────────────┐
│   Layer: Scene-referred, desaturated (Normal)      │
│   Layer: Exposure +0.34 (Normal)                   │
│   Layer: Curves adjustment (Normal, masked)        │
│   Layer: New from Visible, Curves (Normal, masked) │
│   Layer: High Pass sharpen (Soft light)            │
└────────────────────────────────────────────────────┘
┌─ Hue (mode: Hue LCh) ────────────────────────────┐
│   Layer: Scene-referred base (mode: Normal)       │
│   Layer: Hue-Chroma adjustment (Normal, masked)    │
└────────────────────────────────────────────────────┘
```

## Setup Instructions

### 1. Prepare the base image

Start with a scene-referred, linear gamma image at 32-bit floating point
precision. If your image is display-referred or 8-bit, the LCH blend modes
still work but the separation of tonality and color will be less effective.

### 2. Create the three layer groups

```
1. Duplicate base layer 3 times
2. Create Layer Groups: "Chroma", "Lightness", "Hue"
3. Set Chroma group → mode: Chroma (LCh)
4. Set Lightness group → mode: Lightness (LCh)
5. Set Hue group → mode: Hue (LCh)
6. Place one layer copy in each group (mode: Normal)
```

### 3. Build the Chroma group

**Layer: Channel Mixer** (adds saturation)
```
Red channel:    2.000  / -0.500 / -0.500
Green channel: -0.500 /  2.000  / -0.500
Blue channel:  -0.500 / -0.500 /  2.000
```

**Create the Chroma mask:**
1. Select the Channel Mixer layer
2. Colors → Components → Decompose → LCH
3. Use the "C" (Chroma) channel
4. Invert it (Colors → Invert)
5. Drag back to the RGB layer stack as a layer mask

Optional: Use Levels on the mask to limit the Chroma boost to specific
tonal ranges (e.g., Output sliders to 0-76 for subtle effect).

### 4. Build the Lightness group

**Important:** Desaturate each new layer to **Luminance**
(`Colors → Desaturate → Luminance`) before applying any edit. This
prevents out-of-gamut values from accumulating in the Lightness group.

```
Layer 1: Base scene-referred layer (desaturated to Luminance)
Layer 2: Colors → Exposure (+0.34 stops, desaturated)
Layer 3: Curves adjustment for sky (desaturated, masked)
Layer 4: New from Visible → Curves for ground (desaturated, masked)
Layer 5: Filters → Enhance → High Pass (Std Dev: 2.0, Contrast: 0.5)
         Blend mode: Soft light, masked for sky exclusion
```

### 5. Build the Hue group

Only needed when you want to shift hues:

1. Select a range using Select by Color Tool
2. Colors → Hue-Chroma → move Hue slider
   (Negative = clockwise, Positive = counter-clockwise)
3. Mask to limit the effect to specific areas

The Hue (LCh) blend mode applies only the hue component — lightness
and chroma from the layers below are preserved unchanged.

## Monitoring Out-of-Gamut Colors

Place color sample points on suspect regions (bright saturated colors):

```
1. View → Dockable Dialogs → Sample Points
2. Click on image regions to add sample points
3. Each sample point shows R, G, B values
4. Out of gamut = any channel < 0.0 or > 1.0 (at 32-bit float)
```

## Before Export

1. Flatten the image (New from Visible)
2. Optional: Apply a NULL Curves pass to clip extreme out-of-gamut values
   (Open Curves, click OK without changing anything)
3. Convert to output profile (e.g., sRGB for web)
4. Export as 8-bit JPEG/PNG

## Reference

- ninedegreesbelow.com: "Autumn Colors" tutorial (full worked example)
- ninedegreesbelow.com: "GIMP LCH Blend Modes" tutorial
