# Monitor Calibration & Profiling

Step-by-step guide for calibrating and profiling an LCD or LED monitor
using ArgyllCMS and a hardware colorimeter.

---

## Prerequisites

### Required Hardware

A color measurement instrument supported by ArgyllCMS. As of the latest
version, supported devices include:

| Device | Type | Notes |
|--------|------|-------|
| X-Rite i1Display Pro | Colorimeter | Widely available, excellent accuracy |
| X-Rite i1Pro/i1Pro2 | Spectrophotometer | Professional grade, slower |
| X-Rite ColorMunki | Spectrophotometer | Good for beginners |
| Datacolor Spyder 5/X2 | Colorimeter | Widely available, good value |
| Datacolor SpyderX | Colorimeter | Faster than Spyder 5 |
| Colorimetry Research CR-100/250 | Colorimeter | High-end, very accurate |

Check the full list at https://argyllcms.com/doc/ArgyllDoc.html

### Required Software

```bash
# macOS
brew install argyllcms

# Debian/Ubuntu
sudo apt install argyll

# Fedora
sudo dnf install ArgyllCMS
```

### Monitor Preparation

1. **Warm up** the monitor for at least 30 minutes (60 minutes for CRT)
   — display characteristics drift significantly during the first 30 min
2. **Clean the screen** — dust and smudges affect measurements
3. **Set native resolution** — use the monitor's physical native resolution
4. **Ambient light** — use the lighting conditions you normally edit under
5. **Disable dynamic contrast** — turn off any "auto-brightness",
   "dynamic contrast ratio", or power-saving features that change
   brightness based on content

## Calibrate vs. Profile — Critical Distinction

**Calibration** adjusts the monitor hardware to meet target parameters
(white point, brightness, gamma). It changes actual display behavior.

**Profiling** measures the display *after* calibration to create an ICC
profile that describes its actual color behavior. The profile is what
color-managed software uses to display colors accurately.

ArgyllCMS separates these into two steps: `dispcal` (calibrate) and
`dispread` (measure for profiling), followed by `colprof` (create the
profile from measurements).

You can calibrate without profiling (less accurate), but profiling
without calibration produces a profile that describes an unstable target.

## Step-by-Step Calibration Workflow

### Step 1: Choose Target Parameters

| Parameter | Recommended Value | Notes |
|-----------|------------------|-------|
| White point | D65 (6500K) | Standard for photo editing, matches sRGB |
| Gamma | 2.2 | Standard for Windows, sRGB, web |
| Luminance | 120 cd/m² | Standard for photo editing |
| Black point | As low as your monitor allows | LCDs can't reach true black |

Alternative targets:
- **D50 (5000K), gamma 1.8, 80 cd/m²** — legacy print proofing
- **D55 (5500K)** — sometimes used for monitor matching to proofing booths
- **Native white point, gamma 2.2** — use the monitor's native white
  balance for maximum gamut (less accurate but more colorful)

### Step 2: Calibrate with `dispcal`

```bash
# Basic calibration: D65, gamma 2.2, 120 cd/m²
dispcal -v -d 1 -t 6500 -g 2.2 -f 1.0 my-monitor

# Explanation of flags:
# -v        Verbose output
# -d 1      Display number (1 = primary display)
# -t 6500   Target white point in Kelvin (D65)
# -g 2.2    Target gamma
# -f 1.0    Target luminance factor (1.0 = measure, or 120 for cd/m² target)
# my-monitor A base name for output files

# If you want to set a specific luminance target:
dispcal -v -d 1 -t 6500 -g 2.2 -f 120 my-monitor

# For a wide-gamut monitor, consider using the native white point:
dispcal -v -d 1 -N -g 2.2 -f 120 my-monitor
```

`dispcal` will:
1. Place a series of color patches on the screen
2. Guide you through positioning the colorimeter
3. Measure and adjust the monitor's Look-Up Table (LUT) to meet targets
4. Save calibration data to `my-monitor.cal` (and `my-monitor.ti1`)

### Step 3: Measure with `dispread`

After calibration is complete, measure the display's actual color
response:

```bash
dispread -v -d 1 my-monitor
```

This will:
1. Display hundreds of color patches
2. Measure each one with the colorimeter
3. Save measurements to `my-monitor.ti3`

### Step 4: Create ICC Profile with `colprof`

```bash
# Create the profile
colprof -v -qh -D "My Monitor Description" my-monitor

# Explanation of flags:
# -v              Verbose
# -qh             High quality profile
# -D "..."        Profile description (shows in apps)
# my-monitor      Base name (reads my-monitor.ti3, writes my-monitor.icc)
```

### Step 5: Calibrate the Video LUT on Every Boot

ArgyllCMS calibration values are stored in the video card's LUT, which
is reset on reboot. Apply the saved calibration on login:

```bash
# Apply saved calibration
dispwin -d 1 my-monitor.cal

# Verify it's working
dispwin -v -d 1 my-monitor.cal

# For auto-apply on macOS, add dispwin to Login Items
# For Linux, add to ~/.xprofile:
# dispwin -d 1 /path/to/my-monitor.cal
```

## LCD Monitor Limitations

### Why LCDs Can't Match sRGB

1. **Black point never reaches zero** — LCDs always leak some backlight,
   even at full black. This makes black point compensation essential
   (see `references/color-management-overview.md`).

2. **White point may not match D65** — the native white point of an LCD
   is determined by the backlight, not by phosphor blending. It can be
   adjusted but at the cost of reduced luminance range.

3. **Tone response curve** — the default LCD response curve is unlikely
   to match the sRGB TRC exactly. Calibration adjusts the LUT to
   compensate.

4. **Spectral characteristics differ from CRTs** — LCDs use colored
   filters over a white backlight, not phosphors. The resulting
   tristimulus values are close to but not exactly sRGB. A profiled
   (not just calibrated) monitor captures these differences.

### Recalibration Frequency

| Monitor Type | Recommended Interval |
|-------------|---------------------|
| New LCD/LED | Every 2 weeks initially (characteristics drift as the backlight ages) |
| Stable LCD (6+ months old) | Monthly |
| Professional reference monitor | Weekly or before critical work |
| OLED | Every 2-4 weeks (organic materials drift faster) |

Signs your monitor needs recalibration:
- Images look warmer or cooler than you remember
- Grays have a visible color cast
- Shadow detail looks crushed or muddy
- Prints no longer match the screen

## Verifying Your Profile

### Using DisplayCAL

[DisplayCAL](https://displaycal.net/) is the premier GUI frontend for
ArgyllCMS. It wraps the entire dispcal/dispread/colprof workflow in a
user-friendly interface and adds several capabilities not available from
the command line alone.

**Key features:**
- **Colorimeter correction matrices** — different display technologies
  (CCFL, LED, OLED, WLED, GB-LED) require different spectral corrections.
  DisplayCAL ships correction matrices for common instrument+display
  combinations. Using the wrong correction (or none) can produce inaccurate
  profiles, especially on wide-gamut and OLED displays.
- **3D LUT creation** — for video processors (madVR, Prisma, Resolve) and
  hardware LUT boxes. Creates .3dl, .cube, or madVR-specific formats.
- **Profile verification** — measures the display after profiling and
  compares against targets (deltaE report, tone response curve, gamut).
- **Instantaneous loading** — the included DisplayCAL profile loader
  loads calibration curves on macOS and Linux with higher precision than
  the OS defaults.
- **Preset configurations** — tailored settings for common use cases
  (photo editing, video, web, proofing), configurable as starting points.
- **Interactive calibration assistant** — guides through each step with
  visual feedback.
- **Web-based calibration** — displays test patches via a local web server
  for calibrating mobile devices, tablets, or remote displays.
- **Report on uncalibrated display** — Tools menu option that measures
  and reports the display's current gamma, white point, and gamut before
  any calibration.

**Installation:**

```bash
# DisplayCAL wraps ArgyllCMS — install ArgyllCMS first
brew install argyllcms

# Download DisplayCAL from https://displaycal.net/
# macOS: .dmg from the website
# Linux: AppImage or distro package
# Windows: installer from the website
```

**Workflow:**
1. Launch DisplayCAL and select your instrument from the dropdown
2. Choose a preset (e.g., "Photo & Imaging — Relative colorimetric")
3. Attach the colorimeter to the screen (follow on-screen positioning guide)
4. Click "Calibrate & profile"
5. DisplayCAL runs dispcal (interactive adjustment) → dispread → colprof
6. Save the profile and set it as system default
7. Run verification (Tools → Report on profiled display)

**Important note on colorimeter corrections:**
DisplayCAL automatically selects the right correction matrix based on your
display model (if known) or display technology type. If your display is a
white LED-backlit LCD, it needs a different correction than a wide-gamut
GB-LED display. Do NOT skip this step — it's one of the main reasons to
use DisplayCAL over raw command-line ArgyllCMS.

### Check with ArgyllCMS

```bash
# Verify the profile is well-behaved
echo "255 255 255" | xicclu -ir -pl -s255 -v0 my-monitor.icc
echo "0 0 0" | xicclu -ir -pl -s255 -v0 my-monitor.icc

# For a monitor profile, the gray axis will NOT be perfectly neutral
# (monitor profiles are device profiles, not working spaces).
# Acceptable: a*/b* values < 3.0 at mid-gray
```

### Check with Your Eyes

- Visit https://www.lagom.nl/lcd-test/ for comprehensive test patterns
- Check that steps 1-32 are all distinguishable in the black level test
- Check that the white saturation test shows detail to 253+
- Gray should appear neutral (no magenta, green, blue, or yellow cast)

## FireFox Color Management

After profiling, configure Firefox to use your new profile:

```
about:config →
gfx.color_management.enabled = true
gfx.color_management.mode = 1
gfx.color_management.display_profile = /path/to/your/monitor.icc
```

**Important:** Firefox does NOT support black point compensation. Shadows
will appear slightly more crushed than in color-managed image editors.
This is a Firefox limitation, not a profile problem.

## References

- ArgyllCMS documentation: https://argyllcms.com/doc/
- ninedegreesbelow.com: "Profiling Your Monitor" (calibrate vs. profile)
- ninedegreesbelow.com: "sRGB as Monitor Profile" (why sRGB ≠ LCD)
- Lagom LCD test: https://www.lagom.nl/lcd-test/
