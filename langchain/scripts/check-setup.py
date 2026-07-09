#!/usr/bin/env python3
"""Verify LangChain installation and basic functionality."""
import sys

REQUIRED = ["langchain_core", "langchain_openai", "langchain"]
OPTIONAL = ["langchain_anthropic", "langchain_community", "langserve"]

for pkg in REQUIRED:
    try:
        __import__(pkg.replace("-", "_").replace(".", "_"))
        print(f"  [OK] {pkg}")
    except ImportError:
        print(f"  [FAIL] {pkg} — install with pip install {pkg}")
        sys.exit(1)

for pkg in OPTIONAL:
    try:
        __import__(pkg.replace("-", "_").replace(".", "_"))
        print(f"  [OK] {pkg} (optional)")
    except ImportError:
        print(f"  [—] {pkg} (optional, not installed)")

# Test Runnable interface
from langchain_core.runnables import RunnableLambda
r = RunnableLambda(lambda x: x.upper())
assert r.invoke("hello") == "HELLO"
print("  [OK] Runnable interface works")
print("\nSetup check: ALL REQUIRED PACKAGES OK")
