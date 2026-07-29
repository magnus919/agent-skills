#!/usr/bin/env python3
"""Check that pinned dependencies have a minimum release age.

Reads requirements-dev.txt and verifies each ==-pinned package
was released at least MIN_AGE_DAYS ago on PyPI. Packages without
a == pin (using >= or no version) are skipped.

Used in CI to enforce a minimum adoption delay for new releases,
mitigating supply chain attacks from compromised new releases.
"""

from __future__ import annotations

import json
import re
import sys
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REQUIREMENTS = ROOT / "requirements-dev.txt"
MIN_AGE_DAYS = 7
PYPI_API = "https://pypi.org/pypi/{package}/json"


def parse_pinned_deps(path: Path) -> list[tuple[str, str]]:
    """Extract (package, version) for ==-pinned dependencies."""
    pinned: list[tuple[str, str]] = []
    pin_pattern = re.compile(r"^([a-zA-Z0-9_.-]+(?:\[[^\]]*\])?)==([^;]+)")
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        match = pin_pattern.match(line)
        if match:
            name = match.group(1).split("[")[0]
            version = match.group(2).strip()
            pinned.append((name, version))
    return pinned


def get_release_date(package: str, version: str) -> datetime | None:
    """Fetch the upload date for a specific package version from PyPI.

    Returns None if the version or package cannot be found.
    """
    url = PYPI_API.format(package=package)
    try:
        with urllib.request.urlopen(url, timeout=15) as resp:  # nosec B310
            data = json.loads(resp.read().decode("utf-8"))
    except (urllib.error.URLError, urllib.error.HTTPError, json.JSONDecodeError):
        print(f"  WARNING: Could not fetch metadata for {package}", file=sys.stderr)
        return None

    releases = data.get("releases", {})
    version_files = releases.get(version, [])
    if not version_files:
        print(f"  WARNING: Version {version} of {package} not found on PyPI", file=sys.stderr)
        return None

    upload_time_str = version_files[0].get("upload_time", "")
    if not upload_time_str:
        return None

    try:
        return datetime.fromisoformat(upload_time_str).replace(tzinfo=timezone.utc)
    except ValueError:
        return None


def main() -> int:
    if not REQUIREMENTS.exists():
        print(f"ERROR: {REQUIREMENTS} not found", file=sys.stderr)
        return 1

    deps = parse_pinned_deps(REQUIREMENTS)
    if not deps:
        print("No ==-pinned dependencies found. Nothing to check.")
        return 0

    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(days=MIN_AGE_DAYS)
    violations: list[tuple[str, str, datetime]] = []

    print(f"Checking {len(deps)} pinned dependencies for {MIN_AGE_DAYS}+ day release age...\n")
    for package, version in deps:
        release_date = get_release_date(package, version)
        if release_date is None:
            print(f"  {package}=={version}: skipped (could not determine release date)")
            continue

        age_days = (now - release_date).days
        status = "OK" if release_date <= cutoff else "TOO NEW"
        print(
            f"  {package}=={version}: released {release_date.date()} ({age_days}d ago) - {status}"
        )

        if release_date > cutoff:
            violations.append((package, version, release_date))

    if violations:
        print(
            f"\nERROR: {len(violations)} pinned package(s) released less than {MIN_AGE_DAYS} days ago:"
        )
        for pkg, ver, date in violations:
            age = (now - date).days
            print(f"  - {pkg}=={ver} (released {date.date()}, only {age}d ago)")
        print(
            f"\nPolicy requires a minimum of {MIN_AGE_DAYS} days between a PyPI release and adoption."
        )
        print("This reduces supply chain risk from compromised new releases.")
        print("See docs/dependency-policy.md for details.")
        return 1

    print(f"\nAll pinned dependencies are at least {MIN_AGE_DAYS} days old. Policy satisfied.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
