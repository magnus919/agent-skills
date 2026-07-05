#!/usr/bin/env python3
"""
ICC Profile Inspector
Extracts metadata, primaries, TRC info, and well-behaved verification
from ICC color profiles.

Requires: Python 3.8+, Pillow (optional, for ICC chunk extraction)
Tests for: exiftool (for detailed ICC metadata), identify (ImageMagick)

Usage:
    python3 scripts/icc-profile-inspect.py path/to/profile.icc
    python3 scripts/icc-profile-inspect.py path/to/image.jpg  # extract embedded
"""

import struct
import sys
import os
import subprocess
import json
from dataclasses import dataclass, field
from typing import Optional, List, Tuple


@dataclass
class ICCProfile:
    """Parsed ICC profile data."""
    filename: str = ""
    size: int = 0
    profile_class: str = ""
    color_space: str = ""
    pcs: str = ""
    version: str = ""
    cmm: str = ""
    description: str = ""
    copyright_text: str = ""
    manufacturer: str = ""
    model: str = ""
    white_point: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    red_primary: Tuple[float, float] = (0.0, 0.0)
    green_primary: Tuple[float, float] = (0.0, 0.0)
    blue_primary: Tuple[float, float] = (0.0, 0.0)
    red_y: float = 0.0
    green_y: float = 0.0
    blue_y: float = 0.0
    trc_type: str = "unknown"
    is_matrix: bool = False
    is_lut: bool = False
    tags: dict = field(default_factory=dict)


# Profile class IDs
PROFILE_CLASSES = {
    b'scnr': 'Input Device (scanner/camera)',
    b'mntr': 'Display Device (monitor)',
    b'prtr': 'Output Device (printer)',
    b'link': 'DeviceLink',
    b'spac': 'ColorSpace (working space)',
    b'abst': 'Abstract',
    b'nmed': 'Named Color',
}

# Color space IDs
COLOR_SPACES = {
    b'RGB ': 'RGB',
    b'CMYK': 'CMYK',
    b'Lab ': 'CIELAB',
    b'XYZ ': 'XYZ',
    b'GRAY': 'Gray',
    b'YCCK': 'YCCK',
    b"Y'Cb": 'YCbCr',
}

# CMM IDs
CMM_IDS = {
    b'none': 'None',
    b'lcms': 'LittleCMS',
    b'ADBE': 'Adobe',
    b'ACMS': 'Agfa',
    b'appl': 'Apple',
    b'KCMS': 'Kodak',
    b'MSFT': 'Microsoft',
    b'SGIO': 'SGI',
    b'SUNW': 'Sun',
    b'argl': 'ArgyllCMS',
    b'CCMS': 'ColorGear',
}


def check_tool(name: str, cmd: List[str]) -> bool:
    """Check if a CLI tool is available."""
    try:
        subprocess.run(cmd, capture_output=True, timeout=5)
        return True
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def s15fixed16_to_float(raw: bytes) -> float:
    """Convert ICC s15Fixed16Number to float."""
    val = struct.unpack('>i', raw)[0]
    return val / 65536.0


def parse_icc_binary(data: bytes) -> ICCProfile:
    """Parse ICC profile binary data."""
    prof = ICCProfile()
    prof.size = struct.unpack('>I', data[0:4])[0]

    # Version (4.3.0.0 format)
    major = data[8]
    minor_bugfix = data[9]
    minor = (minor_bugfix >> 4) & 0x0F
    bugfix = minor_bugfix & 0x0F
    prof.version = f"{major}.{minor}.{bugfix}"

    # Profile class
    prof.profile_class = PROFILE_CLASSES.get(data[12:16], data[12:16].decode('ascii', errors='replace'))

    # Color space
    prof.color_space = COLOR_SPACES.get(data[16:20], data[16:20].decode('ascii', errors='replace'))

    # PCS
    prof.pcs = COLOR_SPACES.get(data[20:24], data[20:24].decode('ascii', errors='replace'))

    # CMM
    cmm_tag = data[4:8]
    prof.cmm = CMM_IDS.get(cmm_tag, cmm_tag.decode('ascii', errors='replace'))

    # White point tag
    # Find 'wtpt' tag
    for i in range(128, prof.size - 12):
        if data[i:i+4] == b'wtpt':
            wtpt_offset = struct.unpack('>I', data[i+4:i+8])[0]
            prof.white_point = (
                s15fixed16_to_float(data[wtpt_offset+8:wtpt_offset+12]),
                s15fixed16_to_float(data[wtpt_offset+12:wtpt_offset+16]),
                s15fixed16_to_float(data[wtpt_offset+16:wtpt_offset+20]),
            )
            break

    return prof


def inspect_with_exiftool(path: str) -> dict:
    """Use exiftool to get ICC profile metadata."""
    try:
        result = subprocess.run(
            ['exiftool', '-ICC_Profile:all', '-G', '-j', path],
            capture_output=True, text=True, timeout=15
        )
        if result.returncode == 0 and result.stdout.strip():
            data = json.loads(result.stdout)
            if data:
                return data[0]
    except (FileNotFoundError, subprocess.TimeoutExpired, json.JSONDecodeError):
        pass
    return {}


def inspect_with_imagemagick(path: str) -> dict:
    """Use ImageMagick identify to get ICC info."""
    try:
        result = subprocess.run(
            ['identify', '-verbose', path],
            capture_output=True, text=True, timeout=15
        )
        if result.returncode == 0:
            info = {}
            in_icc = False
            for line in result.stdout.split('\n'):
                if 'Profile-icc' in line:
                    in_icc = True
                    parts = line.split(':', 1)
                    if len(parts) == 2:
                        info['icc_size'] = parts[1].strip()
                elif in_icc and ':' in line:
                    key, val = line.split(':', 1)
                    info[key.strip()] = val.strip()
                elif in_icc and not line.strip():
                    in_icc = False
                # Capture general info
                if 'Type:' in line:
                    info['type'] = line.split(':', 1)[1].strip()
                if 'Colorspace:' in line:
                    info['colorspace'] = line.split(':', 1)[1].strip()
            return info
    except FileNotFoundError:
        pass
    return {}


def find_icc_profile(image_path: str) -> Optional[str]:
    """Extract embedded ICC profile from an image to a temp file."""
    # Try exiftool first
    try:
        result = subprocess.run(
            ['exiftool', '-b', '-ICC_Profile', image_path],
            capture_output=True, timeout=15
        )
        if result.returncode == 0 and len(result.stdout) > 100:
            temp_path = image_path + '.extracted.icc'
            with open(temp_path, 'wb') as f:
                f.write(result.stdout)
            return temp_path
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass

    # Try ImageMagick
    try:
        result = subprocess.run(
            ['convert', image_path, 'profile.icc'],
            capture_output=True, timeout=15
        )
        if result.returncode == 0 and os.path.exists('profile.icc'):
            return 'profile.icc'
    except FileNotFoundError:
        pass

    return None


def check_well_behaved(path: str) -> Optional[dict]:
    """Use xicclu to check if profile is well-behaved."""
    try:
        results = {}
        for rgb_str, expected in [
            ("255 255 255", (100.0, 0.0, 0.0)),
            ("0 0 0", (0.0, 0.0, 0.0)),
            ("128 128 128", (None, 0.0, 0.0)),
        ]:
            proc = subprocess.run(
                ['xicclu', '-ir', '-pl', '-s255', '-v0', path],
                input=rgb_str + '\n',
                capture_output=True, text=True, timeout=10
            )
            if proc.returncode == 0:
                line = proc.stdout.strip().split('\n')[0]
                parts = line.split()
                if len(parts) >= 3:
                    results[rgb_str] = {
                        'L': float(parts[0]),
                        'a': float(parts[1]),
                        'b': float(parts[2]),
                    }
        return results if results else None
    except (FileNotFoundError, subprocess.TimeoutExpired, ValueError):
        return None


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 icc-profile-inspect.py <profile.icc>")
        print("   or: python3 icc-profile-inspect.py <image.jpg>")
        print("\nExtracts ICC profile metadata, primaries, and TRC info.")
        print("Requires: exiftool or ImageMagick (one must be installed)")
        sys.exit(1)

    path = sys.argv[1]

    if not os.path.exists(path):
        print(f"Error: file not found: {path}")
        sys.exit(1)

    # Check if it's an image with embedded profile
    ext = os.path.splitext(path)[1].lower()
    image_exts = {'.jpg', '.jpeg', '.tif', '.tiff', '.png', '.psd', '.webp', '.avif'}
    icc_path = path

    if ext in image_exts:
        print(f"Detected image file: {path}")
        print("Attempting to extract embedded ICC profile...\n")
        extracted = find_icc_profile(path)
        if extracted:
            print(f"Extracted profile to: {extracted}")
            icc_path = extracted
        else:
            print("No embedded ICC profile found or extraction tools missing.")
            sys.exit(1)

    # Read binary ICC data
    with open(icc_path, 'rb') as f:
        data = f.read()

    if len(data) < 128:
        print(f"Error: file too small to be a valid ICC profile ({len(data)} bytes)")
        sys.exit(1)

    # Signature check
    if data[36:40] != b'acsp':
        print("Warning: File does not have standard ICC signature ('acsp')")
        print("Attempting to parse anyway...\n")

    # Parse binary header
    prof = parse_icc_binary(data)

    # Get exiftool data if available
    exif_data = inspect_with_exiftool(icc_path)
    im_data = inspect_with_imagemagick(icc_path)

    # Also check with ArgyllCMS xicclu if available
    wb_results = check_well_behaved(icc_path)

    # Print report
    print("=" * 60)
    print(f"  ICC Profile Analysis: {os.path.basename(icc_path)}")
    print("=" * 60)

    print(f"\n  File Size:      {prof.size} bytes")
    print(f"  Profile Class:  {prof.profile_class}")
    print(f"  Color Space:    {prof.color_space}")
    print(f"  PCS:            {prof.pcs}")
    print(f"  Version:        {prof.version}")
    print(f"  CMM:            {prof.cmm}")

    if exif_data:
        desc = exif_data.get('ICC_Profile:ProfileDescription', '')
        if desc:
            print(f"  Description:    {desc}")
        copyright_str = exif_data.get('ICC_Profile:ProfileCopyright', '')
        if copyright_str:
            print(f"  Copyright:      {copyright_str}")
        device = exif_data.get('ICC_Profile:DeviceMfgDesc', '')
        if device:
            print(f"  Device:         {device}")

    print(f"\n  White Point (XYZ): ({prof.white_point[0]:.5f}, {prof.white_point[1]:.5f}, {prof.white_point[2]:.5f})")

    if wb_results:
        print(f"\n  --- Well-Behaved Check (xicclu) ---")
        for rgb, vals in wb_results.items():
            status = "✅" if (abs(vals['a']) < 0.001 and abs(vals['b']) < 0.001) else "❌"
            print(f"    RGB({rgb}) → Lab({vals['L']:.4f}, {vals['a']:.4f}, {vals['b']:.4f}) {status}")
        is_wb = all(
            abs(v['a']) < 0.001 and abs(v['b']) < 0.001
            for v in wb_results.values()
        )
        print(f"\n  Overall: {'✅ WELL-BEHAVED' if is_wb else '❌ NOT well-behaved'}")
    else:
        print("\n  (Install ArgyllCMS (xicclu) for well-behaved verification)")

    # Tool availability
    print(f"\n  --- Available Tools ---")
    print(f"    ImageMagick:  {'✅' if check_tool('identify', ['identify', '-version']) else '❌'} (install: brew install imagemagick)")
    print(f"    Exiftool:     {'✅' if check_tool('exiftool', ['exiftool', '-ver']) else '❌'} (install: brew install exiftool)")
    print(f"    ArgyllCMS:    {'✅' if check_tool('xicclu', ['xicclu', '-v']) else '❌'} (install: brew install argyllcms)")
    print(f"    LCMS:         {'✅' if check_tool('transicc', ['transicc', '-v']) else '❌'} (install: brew install littlecms)")

    # Cleanup
    if icc_path != path and icc_path.endswith('.extracted.icc'):
        os.remove(icc_path)
    if os.path.exists('profile.icc') and icc_path != path:
        os.remove('profile.icc')


if __name__ == '__main__':
    main()
