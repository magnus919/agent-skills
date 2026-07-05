#!/usr/bin/env python3
"""
Color Space Converter
Convert images between ICC color spaces with configurable intent and BPC.

Uses ImageMagick (convert) for ICC profile conversions.
Optionally uses LittleCMS (tificc) for 32-bit floating point / unbounded conversions.

Usage:
    python3 scripts/color-space-convert.py input.jpg --to-srgb
    python3 scripts/color-space-convert.py input.tif --from ProPhotoRGB.icc --to sRGB.icc --intent perceptual
    python3 scripts/color-space-convert.py input.tif --info  # just show current color space
"""

import subprocess
import sys
import os
import argparse


def check_tool(name: str, cmd: list) -> bool:
    """Check if CLI tool is available."""
    try:
        subprocess.run(cmd, capture_output=True, timeout=5)
        return True
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def detect_colorspace(path: str) -> dict:
    """Use ImageMagick to detect image color space and profile info."""
    try:
        result = subprocess.run(
            ['identify', '-verbose', path],
            capture_output=True, text=True, timeout=15
        )
        if result.returncode != 0:
            return {}

        info = {}
        for line in result.stdout.split('\n'):
            stripped = line.strip()
            if 'Type:' in stripped and 'Type:' not in info:
                info['type'] = stripped.split(':', 1)[1].strip()
            if 'Colorspace:' in stripped:
                info['colorspace'] = stripped.split(':', 1)[1].strip()
            if 'Profile-icc' in stripped:
                info['icc'] = stripped.split(':', 1)[1].strip()
            if 'Depth:' in stripped:
                info['depth'] = stripped.split(':', 1)[1].strip()
        return info
    except FileNotFoundError:
        return {}


def get_profile_path(identifier: str) -> str:
    """Resolve a profile name to a known path."""
    known_profiles = {
        'srgb': 'sRGB.icm',
        'adobergb': 'AdobeRGB1998.icc',
        'prophoto': 'ProPhotoRGB.icc',
        'widegamut': 'WideGamutRGB.icc',
        'rec2020': 'Rec2020.icc',
        'linear': 'sRGB-elle-V4-g10.icc',
        'linear-srgb': 'sRGB-elle-V4-g10.icc',
        'linear-prophoto': 'ProPhoto-elle-V4-g10.icc',
        'aces': 'ACES-elle-V4-g10.icc',
        'acescg': 'ACEScg-elle-V4-g10.icc',
        'gray': 'Gray-D50-elle-V4-srgbtrc.icc',
        'lab': 'Lab-D50-Identity-elle-V4.icc',
        'xyz': 'XYZ-D50-Identity-elle-V4.icc',
    }

    if identifier.lower() in known_profiles:
        return known_profiles[identifier.lower()]

    # Assume it's a file path
    if os.path.exists(identifier):
        return identifier

    # Check common ICC directories
    common_dirs = [
        '/usr/share/color/icc/',
        '/usr/local/share/color/icc/',
        os.path.expanduser('~/.local/share/color/icc/'),
        os.path.expanduser('~/.color/icc/'),
    ]
    for d in common_dirs:
        full_path = os.path.join(d, identifier)
        if os.path.exists(full_path):
            return full_path
        # Also check if it's just the filename
        for root, dirs, files in os.walk(d):
            if identifier in files:
                return os.path.join(root, identifier)

    return identifier  # return original, let ImageMagick fail with helpful message


def main():
    parser = argparse.ArgumentParser(
        description='Convert images between ICC color spaces'
    )
    parser.add_argument('input', help='Input image file')
    parser.add_argument('--to-srgb', action='store_true',
                        help='Convert to sRGB (most common operation)')
    parser.add_argument('--to-prophoto', action='store_true',
                        help='Convert to ProPhotoRGB')
    parser.add_argument('--to-adobe', action='store_true',
                        help='Convert to AdobeRGB')
    parser.add_argument('--profile', '-p',
                        help='Source profile (default: embedded or auto-detect)')
    parser.add_argument('--to', '-t',
                        help='Destination profile (path or name)')
    parser.add_argument('--output', '-o',
                        help='Output file (default: input-converted.ext)')
    parser.add_argument('--intent', '-i', choices=['perceptual', 'relative', 'saturation', 'absolute'],
                        default='relative',
                        help='Rendering intent (default: relative)')
    parser.add_argument('--bpc', action='store_true', default=True,
                        help='Use black point compensation (default: on)')
    parser.add_argument('--no-bpc', action='store_true',
                        help='Disable black point compensation')
    parser.add_argument('--unbounded', action='store_true',
                        help='Use LCMS2 unbounded mode (32-bit float, requires true gamma TRC)')
    parser.add_argument('--info', action='store_true',
                        help='Just show color space info, no conversion')
    parser.add_argument('--preview', action='store_true',
                        help='Preview: create gamut check warning overlay')

    args = parser.parse_args()

    if not os.path.exists(args.input):
        print(f"Error: input file not found: {args.input}")
        sys.exit(1)

    # Check tools
    has_magick = check_tool('convert', ['convert', '-version'])
    has_tificc = check_tool('tificc', ['tificc', '-?'])

    if not has_magick:
        print("Error: ImageMagick (convert) not found.")
        print("Install: brew install imagemagick")
        sys.exit(1)

    # Show info mode
    if args.info:
        info = detect_colorspace(args.input)
        print(f"Color Space Info: {args.input}")
        print(f"  {'=' * 40}")
        for key, val in info.items():
            print(f"  {key}: {val}")
        return

    # Determine destination profile
    dest_profile = None
    if args.to_srgb:
        dest_profile = get_profile_path('srgb')
    elif args.to_prophoto:
        dest_profile = get_profile_path('prophoto')
    elif args.to_adobe:
        dest_profile = get_profile_path('adobergb')
    elif args.to:
        dest_profile = get_profile_path(args.to)

    if not dest_profile:
        print("Error: no destination profile specified.")
        print("Use --to-srgb, --to-prophoto, --to-adobe, or --to <profile>")
        sys.exit(1)

    # Determine output path
    if args.output:
        output = args.output
    else:
        base, ext = os.path.splitext(args.input)
        dest_name = os.path.splitext(os.path.basename(dest_profile))[0]
        output = f"{base}-to-{dest_name}{ext}"

    # Build ImageMagick command
    use_bpc = not args.no_bpc and args.bpc

    intent_map = {
        'perceptual': 'Perceptual',
        'relative': 'Relative',
        'saturation': 'Saturation',
        'absolute': 'Absolute',
    }

    if args.unbounded and has_tificc:
        # Use LCMS2 unbounded mode
        print("Using LCMS2 unbounded mode (32-bit float)...")
        cmd = [
            'tificc', '-c', '0', '-w', '32', '-e',
            '-t', str(['Perceptual', 'Relative', 'Saturation', 'Absolute'].index(intent_map[args.intent])),
        ]
        if args.profile:
            cmd.extend(['-i', get_profile_path(args.profile)])
        else:
            # Need source profile; extract from image first
            src_info = detect_colorspace(args.input)
            if 'icc' in src_info and src_info['icc'] != '0 bytes':
                cmd.extend(['-i', dest_profile])  # tificc will extract from image
            else:
                cmd.extend(['-i', dest_profile])
        cmd.extend(['-o', dest_profile, args.input, output])
    else:
        # Use ImageMagick
        cmd = ['convert', args.input]

        # Source profile (optional — if not specified, use embedded)
        if args.profile:
            cmd.extend(['-profile', get_profile_path(args.profile)])

        # Black point compensation
        if use_bpc:
            cmd.append('-black-point-compensation')

        # Intent
        cmd.extend(['-intent', intent_map[args.intent]])

        # Destination profile
        cmd.extend(['-profile', dest_profile])

        # Output
        cmd.append(output)

    # Execute
    print(f"Converting: {args.input}")
    print(f"  Intent: {args.intent}")
    print(f"  BPC: {'on' if use_bpc else 'off'}")
    print(f"  Destination: {dest_profile}")
    print(f"  Output: {output}")
    print(f"  Command: {' '.join(cmd)}")

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        if result.returncode == 0:
            size = os.path.getsize(output)
            print(f"\n✅ Conversion complete: {output} ({size:,} bytes)")

            # Show result info
            info = detect_colorspace(output)
            if info.get('icc'):
                print(f"   Embedded profile: {info['icc']}")
            if info.get('colorspace'):
                print(f"   Color space: {info['colorspace']}")
        else:
            print(f"\n❌ Conversion failed:")
            if result.stderr:
                print(f"   {result.stderr[:500]}")
            sys.exit(1)
    except subprocess.TimeoutExpired:
        print("\n❌ Conversion timed out after 300 seconds.")
        print("   Try a smaller image or check that profiles are valid.")
        sys.exit(1)


if __name__ == '__main__':
    main()
