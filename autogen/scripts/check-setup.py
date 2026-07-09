#!/usr/bin/env python3
"""Verify AutoGen installation."""

import sys

REQUIRED = ["autogen_agentchat", "autogen_ext"]
OPTIONAL = ["autogen_core"]

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

from autogen_agentchat.agents import AssistantAgent
print("  [OK] AutoGen imports work")

print("\nAutoGen setup check: ALL REQUIRED PACKAGES OK")
