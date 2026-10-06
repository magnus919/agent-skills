#!/usr/bin/env python3
"""Verify AutoGen installation."""

import sys
from importlib.metadata import PackageNotFoundError, version

REQUIRED = {
    "autogen-agentchat": "autogen_agentchat",
    "autogen-ext": "autogen_ext",
}

for distribution, module in REQUIRED.items():
    try:
        __import__(module)
        installed = version(distribution)
        if installed != "0.7.5":
            print(f"  [FAIL] {distribution} {installed} — expected 0.7.5 from requirements.txt")
            sys.exit(1)
        print(f"  [OK] {distribution}=={installed}")
    except ImportError:
        print(f"  [FAIL] {distribution} — run python -m pip install -r requirements.txt")
        sys.exit(1)
    except PackageNotFoundError:
        print(f"  [FAIL] {distribution} distribution metadata is unavailable")
        sys.exit(1)

from autogen_agentchat.agents import AssistantAgent
print("  [OK] AutoGen imports work")

print("\nAutoGen setup check: ALL REQUIRED PACKAGES OK")
