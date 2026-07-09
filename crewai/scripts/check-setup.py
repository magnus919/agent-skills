#!/usr/bin/env python3
"""Verify CrewAI installation."""

import sys

REQUIRED = ["crewai"]
OPTIONAL = ["crewai_tools"]

for pkg in REQUIRED:
    try:
        __import__(pkg.replace("-", "_"))
        print(f"  [OK] {pkg}")
    except ImportError:
        print(f"  [FAIL] {pkg} — install with pip install {pkg}")
        sys.exit(1)

for pkg in OPTIONAL:
    try:
        __import__(pkg.replace("-", "_"))
        print(f"  [OK] {pkg} (optional)")
    except ImportError:
        print(f"  [—] {pkg} (optional, not installed)")

from crewai import Agent
print("  [OK] CrewAI imports work")

print("\nCrewAI setup check: ALL REQUIRED PACKAGES OK")
