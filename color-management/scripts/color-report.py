#!/usr/bin/env python3
"""
Color Report Generator
Unified analysis of an image and its ICC profile.

Combines profile inspection, well-behaved check, and gamut check into
a single comprehensive report. Outputs to stdout or a markdown file.

Usage:
    python3 scripts/color-report.py image.jpg
    python3 scripts/color-report.py image.tif --output report.md
    python3 scripts/color-report.py image.jpg --profile sRGB.icc
"""

import subprocess
import sys
import os
import argparse
from datetime import datetime


def check_tool(name, cmd):
    try:
        subprocess.run(cmd, capture_output=True, timeout=5)
        return True
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def run_script(script, *args):
    """Run one of our analysis scripts and capture output."""
    script_path = os.path.join(os.path.dirname(__file__), script)
    if not os.path.exists(script_path):
        return f"[Script not found: {script}]"

    cmd = [sys.executable or 'python3', script_path] + list(args)
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        if result.returncode == 0:
            return result.stdout
        else:
            return f"[Script error ({script}): {result.stderr[:500]}]"
    except subprocess.TimeoutExpired:
        return f"[Script timed out: {script}]"
    except FileNotFoundError:
        return f"[Python not found]"


def get_identify_info(path):
    """Get basic image info from ImageMagick."""
    try:
        result = subprocess.run(
            ['identify', '-verbose', path],
            capture_output=True, text=True, timeout=15
        )
        if result.returncode != 0:
            return ""

        info = {}
        for line in result.stdout.split('\n'):
            s = line.strip()
            if 'Type:' in s:
                info['type'] = s.split(':', 1)[1].strip()
            if 'Colorspace:' in s and 'colorspace' not in info:
                info['colorspace'] = s.split(':', 1)[1].strip()
            if 'Depth:' in s:
                info['depth'] = s.split(':', 1)[1].strip()
            if 'Profile-icc' in s:
                info['icc'] = s.split(':', 1)[1].strip()
            if 'Geometry:' in s:
                info['geometry'] = s.split(':', 1)[1].strip()
            if 'Channel statistics' in s.split(':')[0]:
                break

        parts = []
        for k in ['type', 'colorspace', 'depth', 'geometry', 'icc']:
            if k in info:
                parts.append(f"- **{k}**: {info[k]}")
        return '\n'.join(parts)
    except FileNotFoundError:
        return "[ImageMagick not found]"


def main():
    parser = argparse.ArgumentParser(
        description='Generate a comprehensive color analysis report for an image'
    )
    parser.add_argument('input', help='Input image file')
    parser.add_argument('--profile', '-p',
                        help='Target profile for gamut check (default: detect from image)')
    parser.add_argument('--output', '-o',
                        help='Write report to file instead of stdout')
    args = parser.parse_args()

    if not os.path.exists(args.input):
        print(f"Error: input not found: {args.input}")
        sys.exit(1)

    image_path = os.path.abspath(args.input)
    image_name = os.path.basename(image_path)
    report = []

    # Header
    report.append(f"# Color Analysis Report: {image_name}")
    report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("")
    report.append("## Required Tools Status")
    report.append("")
    report.append(f"| Tool | Status |")
    report.append(f"|------|--------|")
    for tool_name, check_cmd in [
        ('ImageMagick', ['convert', '-version']),
        ('Exiftool', ['exiftool', '-ver']),
        ('ArgyllCMS (xicclu)', ['xicclu', '-v']),
        ('LittleCMS (transicc)', ['transicc', '-v']),
    ]:
        status = '✅' if check_tool(tool_name, [check_cmd[0], '--version' if check_cmd[0] != 'xicclu' else '-v']) or check_tool(tool_name, check_cmd) else '❌'
        if tool_name == 'ImageMagick' and status == '❌':
            status = '❌ (install: brew install imagemagick)'
        report.append(f"| {tool_name} | {status} |")

    # Image info
    report.append("")
    report.append("## Image Information")
    report.append("")
    info = get_identify_info(image_path)
    if info:
        report.append(info)
    else:
        report.append("*ImageMagick identify not available*")

    # ICC profile inspection
    report.append("")
    report.append("## ICC Profile Inspection")
    report.append("")
    report.append("```")
    insp_output = run_script('icc-profile-inspect.py', image_path)
    report.append(insp_output.strip())
    report.append("```")

    # Well-behaved check
    report.append("")
    report.append("## Well-Behaved Check")
    report.append("")
    report.append("```")
    wb_output = run_script('well-behaved-check.py', image_path)
    report.append(wb_output.strip())
    report.append("```")

    # Gamut check (if profile specified or we can find one)
    target_profile = args.profile
    if not target_profile:
        # Try to detect sRGB profile on the system
        for d in ['/usr/share/color/icc/', '/usr/local/share/color/icc/',
                  os.path.expanduser('~/.local/share/color/icc/')]:
            p = os.path.join(d, 'sRGB.icm')
            if os.path.exists(p):
                target_profile = p
                break
            p2 = os.path.join(d, 'sRGB.icc')
            if os.path.exists(p2):
                target_profile = p2
                break

    if target_profile:
        report.append("")
        report.append(f"## Gamut Check (target: {os.path.basename(target_profile)})")
        report.append("")
        report.append("```")
        gamut_output = run_script('gamut-check.py', image_path,
                                   '--to-profile', target_profile)
        report.append(gamut_output.strip())
        report.append("```")
    else:
        report.append("")
        report.append("## Gamut Check")
        report.append("")
        report.append("*No target profile specified or found on system.*")
        report.append("  Re-run with --profile <path> to check gamut clipping.")

    # Summary
    report.append("")
    report.append("---")
    report.append("*Report generated by color-management/scripts/color-report.py*")

    report_text = '\n'.join(report)

    if args.output:
        with open(args.output, 'w') as f:
            f.write(report_text)
        print(f"Report saved to: {args.output}")
    else:
        print(report_text)


if __name__ == '__main__':
    main()
