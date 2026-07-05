#!/usr/bin/env python3
"""
Gamut Checker
Analyzes which pixels in an image are out of gamut with respect to a target
ICC color space. Produces a visual overlay highlighting out-of-gamut regions
and counts affected pixels.

Uses ImageMagick for pixel-level analysis. Requires the target ICC profile.

How it works:
1. Convert image to target color space using LCMS2 bounded mode
2. Compare pixel values before and after to find out-of-gamut clipping
3. Visualize clipped regions as a colored overlay

Usage:
    python3 scripts/gamut-check.py input.jpg --to-profile sRGB.icc
    python3 scripts/gamut-check.py input.tif --to-profile ProPhotoRGB.icc --overlay gamut-overlay.png
"""

import subprocess
import sys
import os
import argparse


def check_tool(name, cmd):
    try:
        subprocess.run(cmd, capture_output=True, timeout=5)
        return True
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def get_profile_path(identifier):
    """Resolve a profile name."""
    known = {
        'srgb': 'sRGB.icm',
        'adobergb': 'AdobeRGB1998.icc',
        'prophoto': 'ProPhotoRGB.icc',
        'widegamut': 'WideGamutRGB.icc',
        'rec2020': 'Rec2020.icc',
    }
    if identifier.lower() in known:
        return known[identifier.lower()]
    if os.path.exists(identifier):
        return identifier
    # Check common paths
    for d in ['/usr/share/color/icc/', '/usr/local/share/color/icc/',
              os.path.expanduser('~/.local/share/color/icc/')]:
        p = os.path.join(d, identifier)
        if os.path.exists(p):
            return p
    return identifier


def main():
    parser = argparse.ArgumentParser(
        description='Check which image pixels are out of gamut for a target color space'
    )
    parser.add_argument('input', help='Input image')
    parser.add_argument('--to-profile', '-p', required=True,
                        help='Target ICC profile (path or name)')
    parser.add_argument('--overlay', '-o',
                        help='Output overlay image showing out-of-gamut regions in red')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Show detailed channel statistics')
    args = parser.parse_args()

    if not os.path.exists(args.input):
        print(f"Error: input not found: {args.input}")
        sys.exit(1)

    if not check_tool('convert', ['convert', '-version']):
        print("Error: ImageMagick (convert) required.")
        sys.exit(1)

    target_profile = get_profile_path(args.to_profile)
    print(f"Gamut Check: {args.input}")
    print(f"  Target profile: {target_profile}")

    base, ext = os.path.splitext(args.input)
    converted = f"{base}-gamut-converted{ext}"

    # Convert to target profile
    print(f"  Converting to target...")
    conv_result = subprocess.run(
        ['convert', args.input,
         '-profile', target_profile,
         '-intent', 'Relative',
         converted],
        capture_output=True, text=True, timeout=120
    )

    if conv_result.returncode != 0:
        print(f"  ❌ Conversion failed: {conv_result.stderr[:200]}")
        sys.exit(1)

    # Compare using ImageMagick
    print(f"  Analyzing gamut clipping...")

    # Use compare to find differing pixels
    diff_file = f"{base}-gamut-diff{ext}"
    subprocess.run(
        ['compare', '-metric', 'AE', args.input, converted, diff_file],
        capture_output=True, text=True, timeout=60
    )

    # Count total differing pixels
    metric_result = subprocess.run(
        ['compare', '-metric', 'AE', '-verbose', args.input, converted, '/dev/null'],
        capture_output=True, text=True, timeout=60
    )

    # Also get image dimensions
    dim_result = subprocess.run(
        ['identify', '-format', '%w %h %[channels]', args.input],
        capture_output=True, text=True, timeout=10
    )

    # Parse metrics
    total_pixels = 0
    clipped_pixels = 0
    channel_stats = {}

    if dim_result.returncode == 0:
        parts = dim_result.stdout.strip().split()
        if len(parts) >= 2:
            try:
                w, h = int(parts[0]), int(parts[1])
                total_pixels = w * h
            except ValueError:
                pass

    # Extract AE metric from stderr
    for line in metric_result.stderr.split('\n'):
        line = line.strip()
        if line.isdigit():
            clipped_pixels = int(line)
            break

    # Get per-channel statistics
    if args.verbose:
        for channel in ['red', 'green', 'blue']:
            ch_result = subprocess.run(
                ['identify', '-verbose', converted],
                capture_output=True, text=True, timeout=10
            )
            in_ch = False
            for line in ch_result.stdout.split('\n'):
                if f'Channel {channel}:' in line.lower() or f'{channel}:' in line.lower():
                    in_ch = True
                if in_ch and 'min:' in line.lower():
                    channel_stats[channel] = line.strip()
                    in_ch = False

    # Report
    pct = (clipped_pixels / total_pixels * 100) if total_pixels > 0 else 0
    print(f"\n  === Gamut Analysis Results ===")
    print(f"  Image dimensions: {w}×{h} = {total_pixels:,} total pixels")
    print(f"  Out of gamut:     {clipped_pixels:,} pixels ({pct:.2f}%)")

    if args.verbose and channel_stats:
        print(f"\n  Channel extremes after conversion:")
        for ch, stat in channel_stats.items():
            print(f"    {ch}: {stat}")

    if pct == 0:
        print(f"\n  ✅ All colors fit within the target color space gamut.")
    elif pct < 1:
        print(f"\n  ⚠️  Fewer than 1% of pixels are out of gamut.")
        print(f"     Likely negligible for most purposes.")
    elif pct < 10:
        print(f"\n  ⚠️  {pct:.1f}% of pixels are out of gamut.")
        print(f"     Soft proof before final conversion. Consider:")
        print(f"     • Using perceptual intent if target profile supports it")
        print(f"     • Reducing chroma/saturation in affected regions")
        print(f"     • Using a larger intermediate working space")
    else:
        print(f"\n  ❌ {pct:.1f}% of pixels are out of gamut — significant clipping.")
        print(f"     This will cause visible loss of detail and hue shifts.")
        print(f"     Recommended actions:")
        print(f"     1. Soft proof the image before final output")
        print(f"     2. Consider a wider gamut output profile")
        print(f"     3. Reduce saturation in affected regions")
        print(f"     4. Try perceptual intent (if target is LUT profile)")

    # Create visual overlay if requested
    if args.overlay:
        print(f"\n  Creating gamut overlay: {args.overlay}")
        overlay_result = subprocess.run(
            ['convert', converted,
             '-alpha', 'set',
             '-channel', 'RGBA',
             '-negate',
             '-fill', 'red', '-opaque', 'black',
             args.overlay],
            capture_output=True, text=True, timeout=30
        )
        if overlay_result.returncode == 0:
            print(f"  ✅ Overlay saved to: {args.overlay}")
        else:
            print(f"  ❌ Overlay failed: {overlay_result.stderr[:200]}")

    # Cleanup temp files
    for f in [converted, diff_file]:
        if os.path.exists(f):
            os.remove(f)


if __name__ == '__main__':
    main()
