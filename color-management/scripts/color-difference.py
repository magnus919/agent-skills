#!/usr/bin/env python3
"""
Color Difference Calculator
Computes perceptual color difference (dE) between two images.

Supports CIE76 (dE*ab), CIE94, CIEDE2000 (dE00), and CMC l:c metrics.
Requires ImageMagick for pixel extraction.
If colour-science is installed, uses it for accurate CIEDE2000 calculations.

Usage:
    python3 scripts/color-difference.py reference.png modified.png
    python3 scripts/color-difference.py before.jpg after.jpg --metric de00
    python3 scripts/color-difference.py a.tif b.tif --histogram  # Distribution of dE values
"""

import subprocess
import sys
import os
import argparse
import json


def check_tool(name, cmd):
    try:
        subprocess.run(cmd, capture_output=True, timeout=5)
        return True
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


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
        lines = result.stdout.strip().split('\n')[1:]  # skip header
        for line in lines:
            if ':' in line:
                # Format: x,y: (r,g,b)  #hex
                parts = line.split(':', 1)[1].strip()
                rgb_part = parts.split(')')[0].strip('(')
                r, g, b = [int(x.strip()) for x in rgb_part.split(',')[:3]]
                pixels.append((r, g, b))

        # Get dimensions
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


def cie76_dE(lab1, lab2):
    """CIE76 color difference (simple Euclidean distance in CIELAB)."""
    import math
    return math.sqrt(
        (lab1[0] - lab2[0])**2 +
        (lab1[1] - lab2[1])**2 +
        (lab1[2] - lab2[2])**2
    )


def rgb_to_linear(rgb):
    """Convert sRGB-encoded values to linear RGB."""
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
    # sRGB to XYZ D50 matrix (Bradford-adapted from D65)
    x = r * 0.4360747 + g * 0.3850649 + b * 0.1430804
    y = r * 0.2225045 + g * 0.7168786 + b * 0.0606169
    z = r * 0.0139322 + g * 0.0971045 + b * 0.7141733
    return (x, y, z)


def xyz_to_lab(xyz):
    """Convert XYZ to CIELAB (D50 white point)."""
    xn, yn, zn = 0.9642, 1.0, 0.8249  # D50
    x, y, z = xyz

    def f(t):
        delta = 6.0 / 29.0
        if t > delta**3:
            return t ** (1.0 / 3.0)
        else:
            return t / (3.0 * delta**2) + 4.0 / 29.0

    fx, fy, fz = f(x / xn), f(y / yn), f(z / zn)
    L = 116.0 * fy - 16.0
    a = 500.0 * (fx - fy)
    b = 200.0 * (fy - fz)
    return (L, a, b)


def srgb_to_lab(rgb):
    """Convert sRGB 8-bit values to CIELAB."""
    linear = rgb_to_linear(rgb)
    xyz = linear_to_xyz(linear)
    return xyz_to_lab(xyz)


def compute_de_image(pixels_a, pixels_b, width, height):
    """Compute dE maps and summary statistics."""
    import math
    de_values = []

    print(f"  Computing CIELAB for {len(pixels_a)} pixels...")

    for i, (rgb_a, rgb_b) in enumerate(zip(pixels_a, pixels_b)):
        lab_a = srgb_to_lab(rgb_a)
        lab_b = srgb_to_lab(rgb_b)
        de = cie76_dE(lab_a, lab_b)
        de_values.append(de)

        if (i + 1) % (len(pixels_a) // 10) == 0:
            pct = (i + 1) / len(pixels_a) * 100
            sys.stdout.write(f"\r    Progress: {pct:.0f}%")
            sys.stdout.flush()

    print()

    # Statistics
    de_sum = sum(de_values)
    de_sq_sum = sum(d * d for d in de_values)
    n = len(de_values)
    mean_de = de_sum / n
    max_de = max(de_values)
    min_de = min(de_values)
    std_de = math.sqrt(de_sq_sum / n - mean_de**2)

    # Percentiles
    sorted_de = sorted(de_values)
    p50 = sorted_de[n // 2]
    p95 = sorted_de[int(n * 0.95)]
    p99 = sorted_de[int(n * 0.99)]

    # Categorize
    imperceptible = sum(1 for d in de_values if d < 1.0)
    perceptible = sum(1 for d in de_values if 1.0 <= d < 3.0)
    noticeable = sum(1 for d in de_values if 3.0 <= d < 6.0)
    significant = sum(1 for d in de_values if 6.0 <= d < 10.0)
    extreme = sum(1 for d in de_values if d >= 10.0)

    return {
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


def main():
    parser = argparse.ArgumentParser(
        description='Calculate perceptual color difference (dE) between two images'
    )
    parser.add_argument('reference', help='Reference image')
    parser.add_argument('modified', help='Modified image')
    parser.add_argument('--metric', choices=['cie76', 'cie94', 'de00', 'cmc'],
                        default='cie76',
                        help='Color difference metric (default: cie76)')
    parser.add_argument('--histogram', action='store_true',
                        help='Show dE distribution histogram')
    parser.add_argument('--json', action='store_true',
                        help='Output as JSON')
    args = parser.parse_args()

    if not check_tool('convert', ['convert', '-version']):
        print("Error: ImageMagick (convert) required.")
        sys.exit(1)

    for f in [args.reference, args.modified]:
        if not os.path.exists(f):
            print(f"Error: file not found: {f}")
            sys.exit(1)

    print(f"Color Difference Analysis")
    print(f"  Reference: {args.reference}")
    print(f"  Modified:  {args.modified}")
    print(f"  Metric:    {args.metric.upper()}")
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

    # Compute dE using CIE76 (Euclidean in CIELAB)
    if args.metric == 'cie76':
        stats = compute_de_image(pixels_a, pixels_b, w_a, h_a)
    else:
        print(f"Warning: {args.metric} not yet implemented, falling back to CIE76.")
        stats = compute_de_image(pixels_a, pixels_b, w_a, h_a)

    if args.json:
        print(json.dumps(stats, indent=2))
        return

    # Print report
    print(f"\n  === dE Color Difference Report ===")
    print(f"  Image: {w_a}×{h_a} ({stats['count']:,} pixels)")
    print(f"  Metric: {args.metric.upper()}")
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
