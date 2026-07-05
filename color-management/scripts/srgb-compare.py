#!/usr/bin/env python3
"""
sRGB Profile Comparator
Compares multiple sRGB ICC profile variants against a reference
(e.g., ArgyllCMS sRGB.icm) to identify differences in white point,
neutral axis, and primary coordinates.

Helps answer: "Which sRGB profile should I use?"

Usage:
    python3 scripts/srgb-compare.py [--dir /path/to/icc/profiles/]
    python3 scripts/srgb-compare.py --compare profile1.icc profile2.icc
"""

import subprocess
import sys
import os
import argparse
import glob


def check_tool(name, cmd):
    try:
        subprocess.run(cmd, capture_output=True, timeout=5)
        return True
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def get_xicclu_rgb(path, r, g, b, scale=255):
    """Get CIELAB values for RGB input using xicclu."""
    try:
        proc = subprocess.run(
            ['xicclu', '-ir', '-pl', f'-s{scale}', '-v0', path],
            input=f"{r} {g} {b}\n",
            capture_output=True, text=True, timeout=10
        )
        if proc.returncode == 0:
            line = proc.stdout.strip().split('\n')[0]
            parts = line.split()
            if len(parts) >= 3:
                return {'L': float(parts[0]), 'a': float(parts[1]), 'b': float(parts[2])}
    except (FileNotFoundError, subprocess.TimeoutExpired, ValueError):
        pass
    return None


def get_exiftool_icc(path):
    """Get ICC metadata from exiftool."""
    try:
        result = subprocess.run(
            ['exiftool', '-ICC_Profile:all', '-G', path],
            capture_output=True, text=True, timeout=15
        )
        if result.returncode == 0:
            data = {}
            for line in result.stdout.split('\n'):
                if ':' in line:
                    parts = line.split(':', 1)
                    data[parts[0].strip()] = parts[1].strip()
            return data
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    return {}


def find_icc_files(directory):
    """Find all ICC/ICM profiles in a directory."""
    patterns = ['*.icc', '*.icm', '*.ICM']
    files = []
    for p in patterns:
        files.extend(glob.glob(os.path.join(directory, p)))
    return sorted(files)


def classify_profile(name, lab_white, lab_mid):
    """Classify a profile based on well-behaved check."""
    if lab_white is None or lab_mid is None:
        return "unknown"

    white_ok = abs(lab_white['L'] - 100.0) < 0.01 and abs(lab_white['a']) < 0.001 and abs(lab_white['b']) < 0.001
    gray_ok = abs(lab_mid['a']) < 0.001 and abs(lab_mid['b']) < 0.001

    # Check for known poorly-behaved variants
    if abs(lab_white['L'] - 99.9988) < 0.001 and abs(lab_white['a']) > 0.01:
        return "POOR (Adobe/color.org/Windows variant)"
    if abs(lab_white['a']) > 2.0:
        return "BAD (unadapted primaries — DO NOT USE)"
    if white_ok and gray_ok:
        return "WELL-BEHAVED"
    return "approx-well-behaved" if (white_ok or abs(lab_white['L'] - 100.0) < 0.001) else "not-well-behaved"


def main():
    parser = argparse.ArgumentParser(
        description='Compare sRGB ICC profile variants'
    )
    parser.add_argument('--dir', '-d',
                        default='/usr/share/color/icc/',
                        help='Directory to scan for ICC profiles')
    parser.add_argument('--compare', nargs=2, metavar=('PROFILE1', 'PROFILE2'),
                        help='Compare two specific profiles')
    parser.add_argument('--reference',
                        default=None,
                        help='Reference sRGB profile (default: use ArgyllCMS sRGB.icm)')
    args = parser.parse_args()

    has_xicclu = check_tool('xicclu', ['xicclu', '-v'])
    has_exiftool = check_tool('exiftool', ['exiftool', '-ver'])

    if not has_xicclu:
        print("Warning: xicclu (ArgyllCMS) not found. Install with: brew install argyllcms")
        print("Without xicclu, only basic file metadata can be compared.\n")

    profiles_to_test = []

    if args.compare:
        profiles_to_test = [os.path.abspath(p) for p in args.compare]
    else:
        # Scan directory for sRGB profiles
        for f in find_icc_files(args.dir):
            if 'srgb' in os.path.basename(f).lower():
                profiles_to_test.append(f)

    if not profiles_to_test:
        print(f"No sRGB profiles found in {args.dir}")
        print("Try: python3 srgb-compare.py --compare profile1.icc profile2.icc")
        sys.exit(1)

    print(f"Found {len(profiles_to_test)} sRGB profile(s)")
    print("=" * 80)

    # Test each profile
    results = []
    for p in profiles_to_test:
        name = os.path.basename(p)
        size = os.path.getsize(p)

        lab_white = get_xicclu_rgb(p, 255, 255, 255) if has_xicclu else None
        lab_mid = get_xicclu_rgb(p, 128, 128, 128) if has_xicclu else None
        lab_black = get_xicclu_rgb(p, 0, 0, 0) if has_xicclu else None
        classification = classify_profile(name, lab_white, lab_mid)

        meta = get_exiftool_icc(p) if has_exiftool else {}

        results.append({
            'name': name,
            'path': p,
            'size': size,
            'lab_white': lab_white,
            'lab_mid': lab_mid,
            'lab_black': lab_black,
            'classification': classification,
            'description': meta.get('ICC_Profile:ProfileDescription', ''),
        })

    # Print table
    print(f"\n  {'Profile':<35} {'Size':>8} {'L*':>8} {'a*':>8} {'b*':>8}  {'Status'}")
    print(f"  {'-'*80}")
    for r in results:
        lw = r['lab_white']
        if lw:
            l_str = f"{lw['L']:.4f}"
            a_str = f"{lw['a']:.4f}"
            b_str = f"{lw['b']:.4f}"
        else:
            l_str = a_str = b_str = "N/A"

        status_symbol = {
            'WELL-BEHAVED': '✅',
            'POOR (Adobe/color.org/Windows variant)': '⚠️',
            'BAD (unadapted primaries — DO NOT USE)': '❌',
            'approx-well-behaved': '~',
            'not-well-behaved': '⚠️',
        }.get(r['classification'], '?')

        print(f"  {r['name']:<35} {r['size']:>8} {l_str:>8} {a_str:>8} {b_str:>8}  {status_symbol}")

    print(f"\n  Summary:")
    print(f"  ✅ = Well-behaved (ArgyllCMS, colord Shared, Krita built-in, scRGB)")
    print(f"  ⚠️ = Not well-behaved (Adobe, color.org, Windows 2000, LCMS v1)")
    print(f"  ⚠️  = Not well-behaved (OpenICC, digiKam, Canon variants)")
    print(f"  ~  = Approximately well-behaved (small deviation, OK for 8-bit)")
    print(f"  ❌ = BAD — unadapted primaries (Krita sRGB.icm, old digiKam srgb.icm)")
    print(f"\n  Recommendation: Use ArgyllCMS sRGB.icm or colord Shared sRGB.icm.")
    print(f"  See references/working-spaces-reference.md for full survey data.")


if __name__ == '__main__':
    main()
