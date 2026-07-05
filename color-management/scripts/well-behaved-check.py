#!/usr/bin/env python3
"""
Well-Behaved Profile Checker
Verifies whether an ICC profile is "well-behaved" (color-balanced, normalized)
by testing R=G=B values against CIELAB neutrality.

Uses xicclu (ArgyllCMS) when available, with a mathematical fallback
for known working space primaries.

A well-behaved profile must have:
1. R=G=B → neutral gray (a*=b*=0 in CIELAB)
2. R=G=B=0 → Lab(0, 0, 0)
3. R=G=B=255 → Lab(100, 0, 0)
4. All R=G=B values on the neutral axis produce a*=b*=0

Usage:
    python3 scripts/well-behaved-check.py path/to/profile.icc
    python3 scripts/well-behaved-check.py path/to/image.jpg  # extract embedded
"""

import subprocess
import sys
import os
import struct
import json


KNOWN_WELL_BEHAVED = {
    'ArgyllCMS sRGB.icm': '100.000000 0.000000 0.000000',
    'ClayRGB (ArgyllCMS AdobeRGB)': '100.000000 0.000000 0.000000',
    'colord Shared sRGB.icm': '100.000000 0.000000 0.000000',
    'Canon WideGamut': '100.000000 0.000000 0.000000',
    'Krita scRGB.icm': '100.000000 0.000000 0.000000',
    'Adobe AdobeRGB1998': '100.000000 0.000000 0.000000',
}

KNOWN_NOT_WELL_BEHAVED = {
    'Krita sRGB.icm (unadapted)': '100.001200, a*=-2.390, b*=-19.404 (DO NOT USE)',
    'Adobe sRGB.icm': '99.998820, a*=0.018, b*=-0.017',
    'color.org sRGB_v4': '99.998820, a*=0.018, b*=-0.017',
    'Windows 2000 sRGB.icm': '99.998820, a*=0.018, b*=-0.017',
    'LCMS v1 sRGB': '99.998820, a*=0.018, b*=-0.017',
    'ProPhotoRGB (OpenICC)': '100.000590, a*=-0.003, b*=-0.008',
    'AppleRGB (Shared)': '100.001180, a*=-0.002, b*=-0.000',
    'ColorMatchRGB (Shared)': '100.001180, a*=-0.002, b*=-0.000',
    'WideGamut (digiKam/Krita)': '100.001180, a*=0.016, b*=-0.015',
}


def get_file_hash(path: str) -> str:
    """Get MD5 hash of file (for identification)."""
    try:
        import hashlib
        with open(path, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()
    except ImportError:
        return ''


def extract_icc_from_image(path: str) -> Optional[str]:
    """Extract embedded ICC profile from image file."""
    # Try exiftool first
    try:
        result = subprocess.run(
            ['exiftool', '-b', '-ICC_Profile', path],
            capture_output=True, timeout=15
        )
        if result.returncode == 0 and len(result.stdout) > 100:
            temp_path = path + '.wb-check.icc'
            with open(temp_path, 'wb') as f:
                f.write(result.stdout)
            return temp_path
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass

    # Try ImageMagick
    try:
        result = subprocess.run(
            ['convert', path, 'wb-temp-profile.icc'],
            capture_output=True, timeout=15
        )
        if result.returncode == 0 and os.path.exists('wb-temp-profile.icc'):
            return 'wb-temp-profile.icc'
    except FileNotFoundError:
        pass

    return None


def check_with_xicclu(path: str) -> dict:
    """Use ArgyllCMS xicclu to check well-behaved status."""
    test_values = [
        ("255 255 255", "white"),
        ("0 0 0", "black"),
        ("128 128 128", "mid-gray"),
        ("64 64 64", "dark-gray"),
        ("192 192 192", "light-gray"),
    ]

    results = {}
    for rgb_str, label in test_values:
        try:
            proc = subprocess.run(
                ['xicclu', '-ir', '-pl', '-s255', '-v0', path],
                input=rgb_str + '\n',
                capture_output=True, text=True, timeout=10
            )
            if proc.returncode == 0:
                line = proc.stdout.strip().split('\n')[0]
                parts = line.split()
                if len(parts) >= 3:
                    results[label] = {
                        'L': float(parts[0]),
                        'a': float(parts[1]),
                        'b': float(parts[2]),
                        'input': rgb_str,
                    }
        except (FileNotFoundError, subprocess.TimeoutExpired, ValueError):
            pass

    return results


def verdict(results: dict) -> dict:
    """Determine if profile is well-behaved from xicclu results."""
    if not results:
        return {'well_behaved': None, 'reason': 'No xicclu data available'}

    issues = []
    for label, vals in results.items():
        ab_max = max(abs(vals['a']), abs(vals['b']))
        if ab_max > 0.001:
            issues.append(f"{label}: a*={vals['a']:.4f}, b*={vals['b']:.4f} (should be 0.0000)")

    passes_white = 'white' in results and abs(results['white']['L'] - 100.0) < 0.01 and abs(results['white']['a']) < 0.001 and abs(results['white']['b']) < 0.001
    passes_black = 'black' in results and abs(results['black']['L']) < 0.01 and abs(results['black']['a']) < 0.001 and abs(results['black']['b']) < 0.001

    is_wb = len(issues) == 0 and passes_white and passes_black

    return {
        'well_behaved': is_wb,
        'issues': issues,
        'passes_white': passes_white,
        'passes_black': passes_black,
        'reason': 'All checks passed' if is_wb else ('; '.join(issues) if issues else 'Failed basic RGB→Lab mapping'),
    }


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 well-behaved-check.py <profile.icc>")
        print("   or: python3 well-behaved-check.py <image.jpg>")
        print("\nChecks if an ICC profile is 'well-behaved' (neutral gray axis).")
        print("Uses xicclu (ArgyllCMS) — install with: brew install argyllcms")
        sys.exit(1)

    path = sys.argv[1]

    if not os.path.exists(path):
        print(f"Error: file not found: {path}")
        sys.exit(1)

    # Handle image files
    ext = os.path.splitext(path)[1].lower()
    image_exts = {'.jpg', '.jpeg', '.tif', '.tiff', '.png', '.psd'}
    icc_path = path

    if ext in image_exts:
        print(f"Detected image: {path}")
        extracted = extract_icc_from_image(path)
        if extracted:
            print(f"Extracted profile to: {extracted}")
            icc_path = extracted
        else:
            print("No embedded ICC profile found. Install exiftool or ImageMagick.")
            sys.exit(1)

    print(f"\nChecking: {icc_path}")
    print("=" * 50)

    # Quick identification
    hash_val = get_file_hash(icc_path)

    # Run xicclu check
    result = check_with_xicclu(icc_path)

    if not result:
        print("\n❌ xicclu (ArgyllCMS) not found or failed.")
        print("  Install: brew install argyllcms")
        print("  Or: apt install argyll / dnf install ArgyllCMS")
        print("\n  Without xicclu, cannot verify well-behaved status programmatically.")
        print("  See references/working-spaces-reference.md for known-good profiles.")
        sys.exit(1)

    # Print results table
    print(f"\n  {'Test Point':<20} {'L*':>10} {'a*':>10} {'b*':>10}  {'Status'}")
    print(f"  {'-'*60}")
    for label, vals in sorted(result.items()):
        is_neutral = abs(vals['a']) < 0.001 and abs(vals['b']) < 0.001
        status = "✅" if is_neutral else "❌"
        print(f"  {label:<20} {vals['L']:>10.4f} {vals['a']:>10.4f} {vals['b']:>10.4f}  {status}")

    # Verdict
    v = verdict(result)

    print(f"\n  Verdict:")
    if v['well_behaved'] is None:
        print("    ⚠️  Unable to determine (install ArgyllCMS)")
    elif v['well_behaved']:
        print("    ✅ This profile is WELL-BEHAVED")
        print("       R=G=B produces neutral gray throughout the tone range.")
        print("       Suitable for use as a working space at any bit depth.")
    else:
        print("    ❌ This profile is NOT well-behaved")
        for issue in v['issues']:
            print(f"       • {issue}")
        print("\n    At 8-bit, the deviation is usually unnoticeable.")
        print("    At 16-bit+ floating point, extreme edits may introduce a false color cast.")
        print("    Consider switching to a well-behaved equivalent.")
        print("    See references/working-spaces-reference.md for recommended profiles.")

    # Cleanup temp files
    if icc_path != path and icc_path.endswith('.wb-check.icc'):
        os.remove(icc_path)
    if os.path.exists('wb-temp-profile.icc') and icc_path != path:
        os.remove('wb-temp-profile.icc')


if __name__ == '__main__':
    main()
