#!/usr/bin/env python3
"""Verify Haystack installation."""

import sys

REQUIRED = ["haystack", "haystack_components"]
OPTIONAL = ["hayhooks"]

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

# Test basic pipeline creation
from haystack import Pipeline
p = Pipeline()
print("  [OK] Pipeline creation works")

print("\nHaystack setup check: ALL REQUIRED PACKAGES OK")
