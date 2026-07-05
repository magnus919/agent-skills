#!/usr/bin/env python3
"""
Color Difference Calculator
Computes perceptual color difference (dE) between two images.

Supports CIE76 (dE*ab), CIE94 (dE*94), CIEDE2000 (dE00), and CMC l:c metrics.
If colour-science is installed, uses it for accurate CIEDE2000.
All metrics have pure-Python fallbacks.

Usage:
    python3 scripts/color-difference.py reference.png modified.png
    python3 scripts/color-difference.py before.jpg after.jpg --metric de00
    python3 scripts/color-difference.py a.tif b.tif --histogram
"""

import subprocess
import sys
import os
import argparse
import json
import math

# ── Engine detection ──────────────────────────────────────────────────────

_has_colour_science = False
try:
    import colour
    _has_colour_science = True
    # Verify we can actually compute delta E
    try:
        colour.delta_E((50, 0, 0), (50, 1, 0))
    except AttributeError:
        # colour-science is installed but may not have delta_E (old version)
        _has_colour_science = False
except ImportError:
    pass


# ── Tool check ────────────────────────────────────────────────────────────

def check_tool(name, cmd):
    try:
        subprocess.run(cmd, capture_output=True, timeout=5)
        return True
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


# ── Pixel extraction ──────────────────────────────────────────────────────

def get_pixel_data(path):
    """Extract RGB pixel data using ImageMagick text format."""
    try:
        result = subprocess.run(
            ['convert', path, '-depth', '8', 'txt:-'],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode != 0:
            return None, 0, 0

        pixels = []
        lines = result.stdout.strip().split('\n')[1:]
        for line in lines:
            if ':' in line:
                parts = line.split(':', 1)[1].strip()
                rgb_part = parts.split(')')[0].strip('(')
                r, g, b = [int(x.strip()) for x in rgb_part.split(',')[:3]]
                pixels.append((r, g, b))

        dim_result = subprocess.run(
            ['identify', '-format', '%w %h', path],
            capture_output=True, text=True, timeout=10
        )
        if dim_result.returncode == 0:
            parts = dim_result.stdout.strip().split()
            return pixels, int(parts[0]), int(parts[1])
        return pixels, 0, 0

    except (FileNotFoundError, subprocess.TimeoutExpired, ValueError):
        return None, 0, 0


# ── Color space conversion (sRGB 8-bit → CIELAB D50) ─────────────────────

def srgb_to_linear(rgb):
    """Convert sRGB 8-bit to linear RGB."""
    result = []
    for c in rgb:
        c_norm = c / 255.0
        if c_norm <= 0.04045:
            result.append(c_norm / 12.92)
        else:
            result.append(((c_norm + 0.055) / 1.055) ** 2.4)
    return result


def linear_to_xyz(rgb):
    """Convert linear RGB (sRGB primaries) to XYZ D50."""
    r, g, b = rgb
    x = r * 0.4360747 + g * 0.3850649 + b * 0.1430804
    y = r * 0.2225045 + g * 0.7168786 + b * 0.0606169
    z = r * 0.0139322 + g * 0.0971045 + b * 0.7141733
    return (x, y, z)


def xyz_to_lab(xyz):
    """Convert XYZ to CIELAB (D50 white point)."""
    xn, yn, zn = 0.9642, 1.0, 0.8249
    x, y, z = xyz
    delta = 6.0 / 29.0

    def f(t):
        if t > delta ** 3:
            return t ** (1.0 / 3.0)
        else:
            return t / (3.0 * delta ** 2) + 4.0 / 29.0

    fx, fy, fz = f(x / xn), f(y / yn), f(z / zn)
    L = 116.0 * fy - 16.0
    a = 500.0 * (fx - fy)
    b = 200.0 * (fy - fz)
    return (L, a, b)


def srgb_to_lab(rgb):
    """Convert sRGB 8-bit values to CIELAB D50."""
    linear = srgb_to_linear(rgb)
    xyz = linear_to_xyz(linear)
    return xyz_to_lab(xyz)


# ── CIE76: dE*ab ──────────────────────────────────────────────────────────

def cie76_dE(lab1, lab2):
    """CIE76 color difference (simple Euclidean in CIELAB)."""
    return math.sqrt(
        (lab1[0] - lab2[0]) ** 2 +
        (lab1[1] - lab2[1]) ** 2 +
        (lab1[2] - lab2[2]) ** 2
    )


# ── CIE94: dE*94 ──────────────────────────────────────────────────────────

def cie94_dE(lab1, lab2, application='graphic_arts'):
    """
    CIE94 color difference.

    application: 'graphic_arts' (kL=1, K1=0.045, K2=0.015) or
                 'textiles' (kL=2, K1=0.048, K2=0.014)
    """
    L1, a1, b1 = lab1
    L2, a2, b2 = lab2

    if application == 'graphic_arts':
        kL, K1, K2 = 1.0, 0.045, 0.015
    else:
        kL, K1, K2 = 2.0, 0.048, 0.014

    dL = L1 - L2
    C1 = math.sqrt(a1 ** 2 + b1 ** 2)
    C2 = math.sqrt(a2 ** 2 + b2 ** 2)
    dC = C1 - C2
    dH_sq = (a1 - a2) ** 2 + (b1 - b2) ** 2 - dC ** 2
    # Guard against tiny negative from floating point
    if dH_sq < 0:
        dH_sq = 0.0
    dH = math.sqrt(dH_sq)

    SL = 1.0
    SC = 1.0 + K1 * C1
    SH = 1.0 + K2 * C1

    return math.sqrt(
        (dL / (kL * SL)) ** 2 +
        (dC / SC) ** 2 +
        (dH / SH) ** 2
    )


# ── CMC l:c ───────────────────────────────────────────────────────────────

def cmc_dE(lab1, lab2, l=2.0, c=1.0):
    """
    CMC l:c color difference.

    Standard parameters:
      - Perceptibility: l=1, c=1
      - Acceptability:  l=2, c=1 (textile industry default)
    """
    L1, a1, b1 = lab1
    L2, a2, b2 = lab2

    dL = L1 - L2
    C1 = math.sqrt(a1 ** 2 + b1 ** 2)
    C2 = math.sqrt(a2 ** 2 + b2 ** 2)
    dC = C1 - C2

    dH_sq = (a1 - a2) ** 2 + (b1 - b2) ** 2 - dC ** 2
    if dH_sq < 0:
        dH_sq = 0.0
    dH = math.sqrt(dH_sq)

    # Arithmetic mean chroma
    Cab = (C1 + C2) / 2.0

    # Hue angle in degrees
    def hue_angle(a, b):
        h = math.degrees(math.atan2(b, a))
        if h < 0:
            h += 360
        return h

    h1 = hue_angle(a1, b1)

    # SL
    if L1 < 16:
        SL = 0.511
    else:
        SL = 0.040975 * L1 / (1 + 0.01765 * L1)

    # SC
    SC = 0.0638 * Cab / (1 + 0.0131 * Cab) + 0.638

    # SH
    f = math.sqrt(Cab ** 4 / (Cab ** 4 + 1900))
    T = (0.36 + abs(0.4 * math.cos(math.radians(h1 + 35))))
    if h1 >= 164 and h1 <= 345:
        T = 0.56 + abs(0.2 * math.cos(math.radians(h1 + 168)))
    SH = SC * (f * T + 1 - f)

    return math.sqrt(
        (dL / (l * SL)) ** 2 +
        (dC / (c * SC)) ** 2 +
        (dH / SH) ** 2
    )


# ── CIEDE2000 (dE00) — pure Python fallback ──────────────────────────────

def _deg(rad):
    return rad * 180.0 / math.pi


def _rad(deg):
    return deg * math.pi / 180.0


def ciede2000_dE(lab1, lab2):
    """
    CIEDE2000 color difference.
    Based on the corrected formula from: Sharma, Wu, Dalal (2005)
    """
    L1, a1, b1 = lab1
    L2, a2, b2 = lab2

    dLp = L2 - L1
    Lbar = (L1 + L2) / 2.0

    C1 = math.sqrt(a1 ** 2 + b1 ** 2)
    C2 = math.sqrt(a2 ** 2 + b2 ** 2)
    Cbar = (C1 + C2) / 2.0

    # G factor for CIEDE2000
    G = 0.5 * (1 - math.sqrt(Cbar ** 7 / (Cbar ** 7 + 25 ** 7)))

    ap1 = a1 * (1 + G)
    ap2 = a2 * (1 + G)
    Cp1 = math.sqrt(ap1 ** 2 + b1 ** 2)
    Cp2 = math.sqrt(ap2 ** 2 + b2 ** 2)
    Cpbar = (Cp1 + Cp2) / 2.0
    dCp = Cp2 - Cp1

    # Hue angles
    def hp(a, b):
        if a == 0 and b == 0:
            return 0.0
        h = _deg(math.atan2(b, a))
        if h < 0:
            h += 360
        return h

    hp1 = hp(ap1, b1)
    hp2 = hp(ap2, b2)

    # dHp
    dhp = hp2 - hp1
    if Cp1 == 0.0 or Cp2 == 0.0:
        dhp = 0.0
    elif abs(dhp) > 180:
        if dhp <= 180:
            dhp += 360
        else:
            dhp -= 360
    dHp = 2 * math.sqrt(Cp1 * Cp2) * math.sin(_rad(dhp) / 2.0)

    # Hpbar
    if Cp1 == 0.0 or Cp2 == 0.0:
        Hpbar = hp1 + hp2
    elif abs(hp1 - hp2) <= 180:
        Hpbar = (hp1 + hp2) / 2.0
    elif abs(hp1 - hp2) > 180 and (hp1 + hp2) < 360:
        Hpbar = (hp1 + hp2 + 360) / 2.0
    else:
        Hpbar = (hp1 + hp2 - 360) / 2.0

    # Lightness weight
    T_ = (
        1 - 0.17 * math.cos(_rad(Hpbar - 30)) +
        0.24 * math.cos(_rad(2 * Hpbar)) +
        0.32 * math.cos(_rad(3 * Hpbar + 6)) -
        0.20 * math.cos(_rad(4 * Hpbar - 63))
    )

    # Rotation term
    dtheta = 30 * math.exp(-((Hpbar - 275) / 25) ** 2)
    RC = 2 * math.sqrt(Cpbar ** 7 / (Cpbar ** 7 + 25 ** 7))
    RT = -math.sin(_rad(2 * dtheta)) * RC

    # Weights
    SL = 1 + (0.015 * (Lbar - 50) ** 2) / math.sqrt(20 + (Lbar - 50) ** 2)
    SC = 1 + 0.045 * Cpbar
    SH = 1 + 0.015 * Cpbar * T_

    dE = math.sqrt(
        (dLp / SL) ** 2 +
        (dCp / SC) ** 2 +
        (dHp / SH) ** 2 +
        RT * (dCp / SC) * (dHp / SH)
    )
    return dE


# ── Dispatcher ────────────────────────────────────────────────────────────

def compute_dE(lab1, lab2, metric, **kwargs):
    """Dispatch to the correct delta-E implementation."""
    if metric == 'cie76':
        return cie76_dE(lab1, lab2)
    elif metric == 'cie94':
        return cie94_dE(lab1, lab2, **kwargs)
    elif metric == 'de00':
        if _has_colour_science:
            try:
                import colour
                return float(colour.delta_E(lab1, lab2))
            except Exception:
                pass
        return ciede2000_dE(lab1, lab2)
    elif metric == 'cmc':
        return cmc_dE(lab1, lab2, **kwargs)
    return cie76_dE(lab1, lab2)


def engine_label(metric):
    """Report which engine computed the result."""
    if metric == 'de00' and _has_colour_science:
        return 'colour-science library'
    elif metric in ('cie76', 'cie94', 'cmc'):
        return 'pure Python (closed-form)'
    elif metric == 'de00':
        return 'pure Python (Sharma/Wu/Dalal 2005)'
    return 'pure Python'


# ── Image-level computation ───────────────────────────────────────────────

def compute_de_image(pixels_a, pixels_b, width, height, metric):
    """Compute dE for all pixels with the given metric. Returns (stats_dict, raw_de_values)."""
    de_values = []
    n = len(pixels_a)
    print(f"  Computing {metric.upper()} for {n:,} pixels...")

    for i, (rgb_a, rgb_b) in enumerate(zip(pixels_a, pixels_b)):
        lab_a = srgb_to_lab(rgb_a)
        lab_b = srgb_to_lab(rgb_b)
        de = compute_dE(lab_a, lab_b, metric)
        de_values.append(de)

        if (i + 1) % max(n // 10, 1) == 0:
            pct = (i + 1) / n * 100
            sys.stdout.write(f"\r    Progress: {pct:.0f}%")
            sys.stdout.flush()

    print()

    # Statistics
    de_sum = sum(de_values)
    de_sq_sum = sum(d * d for d in de_values)
    mean_de = de_sum / n
    max_de = max(de_values)
    min_de = min(de_values)
    std_de = math.sqrt(de_sq_sum / n - mean_de ** 2)

    # Percentiles
    sorted_de = sorted(de_values)
    p50 = sorted_de[n // 2]
    p95 = sorted_de[int(n * 0.95)]
    p99 = sorted_de[int(n * 0.99)]

    # Categories
    imperceptible = sum(1 for d in de_values if d < 1.0)
    perceptible = sum(1 for d in de_values if 1.0 <= d < 3.0)
    noticeable = sum(1 for d in de_values if 3.0 <= d < 6.0)
    significant = sum(1 for d in de_values if 6.0 <= d < 10.0)
    extreme = sum(1 for d in de_values if d >= 10.0)

    return {
        'metric': metric,
        'engine': engine_label(metric),
        'count': n,
        'width': width,
        'height': height,
        'mean': mean_de,
        'std': std_de,
        'min': min_de,
        'max': max_de,
        'p50': p50,
        'p95': p95,
        'p99': p99,
        'categories': {
            'imperceptible (dE<1)': (imperceptible, imperceptible / n * 100),
            'perceptible (1-3)': (perceptible, perceptible / n * 100),
            'noticeable (3-6)': (noticeable, noticeable / n * 100),
            'significant (6-10)': (significant, significant / n * 100),
            'extreme (10+)': (extreme, extreme / n * 100),
        }
    }

    return stats, de_values


# ── Main ──────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description='Calculate perceptual color difference (dE) between two images'
    )
    parser.add_argument('reference', help='Reference image')
    parser.add_argument('modified', help='Modified image')
    parser.add_argument('--metric', choices=['cie76', 'cie94', 'de00', 'cmc'],
                        default='de00',
                        help='Color difference metric (default: de00)')
    parser.add_argument('--histogram', action='store_true',
                        help='Show dE distribution as ASCII histogram')
    parser.add_argument('--json', action='store_true',
                        help='Output as JSON')
    args = parser.parse_args()

    if not check_tool('convert', ['convert', '-version']):
        print("Error: ImageMagick (convert) required.")
        print("Install: brew install imagemagick")
        sys.exit(1)

    for f in [args.reference, args.modified]:
        if not os.path.exists(f):
            print(f"Error: file not found: {f}")
            sys.exit(1)

    print(f"Color Difference Analysis")
    print(f"  Reference: {args.reference}")
    print(f"  Modified:  {args.modified}")
    print(f"  Metric:    {args.metric.upper()}")
    if _has_colour_science:
        print(f"  Engine:    colour-science library available")
    else:
        print(f"  Engine:    pure Python fallback (install colour-science for better accuracy)")
    print()

    pixels_a, w_a, h_a = get_pixel_data(args.reference)
    pixels_b, w_b, h_b = get_pixel_data(args.modified)

    if pixels_a is None or pixels_b is None:
        print("Error: could not read image pixels.")
        print("Install ImageMagick with: brew install imagemagick")
        sys.exit(1)

    if len(pixels_a) != len(pixels_b):
        print(f"Error: image dimensions differ.")
        print(f"  Reference: {w_a}×{h_a} = {len(pixels_a)} pixels")
        print(f"  Modified:  {w_b}×{h_b} = {len(pixels_b)} pixels")
        sys.exit(1)

    stats, de_values = compute_de_image(pixels_a, pixels_b, w_a, h_a, args.metric)

    if args.json:
        print(json.dumps(stats, indent=2))
        return

    # Print report
    print(f"\n  === {stats['metric'].upper()} Color Difference Report ===")
    print(f"  Image:   {w_a}×{h_a} ({stats['count']:,} pixels)")
    print(f"  Metric:  {stats['metric'].upper()}")
    print(f"  Engine:  {stats['engine']}")
    print()
    print(f"  Statistics:")
    print(f"    Mean dE:    {stats['mean']:.3f}")
    print(f"    Std dev:    {stats['std']:.3f}")
    print(f"    Min dE:     {stats['min']:.3f}")
    print(f"    Max dE:     {stats['max']:.3f}")
    print(f"    Median:     {stats['p50']:.3f}")
    print(f"    95th pctl:  {stats['p95']:.3f}")
    print(f"    99th pctl:  {stats['p99']:.3f}")
    print()
    print(f"  Breakdown:")
    for label, (count, pct) in stats['categories'].items():
        bar = '█' * int(pct / 2)
        print(f"    {label:<25}: {count:>8,} ({pct:5.1f}%) {bar}")

    if args.histogram:
        print(f"\n  Distribution:")
        for bucket in range(0, int(stats['max']) + 2, 2):
            count = sum(1 for d in de_values if bucket <= d < bucket + 2)
            pct = count / stats['count'] * 100
            bar = '█' * max(int(pct * 2), 1) if pct > 0 else ''
            print(f"    {bucket:>3}-{bucket+2:<3}: {bar} ({pct:.1f}%)")

    print()
    if stats['mean'] < 1.0 and stats['max'] < 5.0:
        print(f"  ✅ Colors are visually nearly identical")
    elif stats['mean'] < 3.0:
        print(f"  ⚠️  Small visible differences — within typical reproduction tolerance")
    elif stats['mean'] < 6.0:
        print(f"  ⚠️  Noticeable differences — check the working space and intent settings")
    else:
        print(f"  ❌ Large differences — likely a different color space or significant gamut clipping")


if __name__ == '__main__':
    main()
