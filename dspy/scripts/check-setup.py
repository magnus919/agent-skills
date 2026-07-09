#!/usr/bin/env python3
"""Verify DSPy installation and basic functionality."""

import sys

REQUIRED_PACKAGES = ["dspy"]

for pkg in REQUIRED_PACKAGES:
    try:
        __import__(pkg)
        print(f"  [OK] {pkg}")
    except ImportError:
        print(f"  [FAIL] {pkg} — install with pip install {pkg}")
        sys.exit(1)

# Test basic DSPy functionality
import dspy

lm = dspy.LM("openai/gpt-4o-mini")
dspy.configure(lm=lm)

qa = dspy.Predict("question -> answer")
result = qa(question="What is DSPy?")
assert hasattr(result, "answer"), "Answer field missing"
print(f"  [OK] Basic prediction works: {result.answer[:50]}...")

print("\nDSPy setup check: ALL REQUIRED PACKAGES OK")
