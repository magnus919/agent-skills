"""Ghidra backend adapter — PyGhidra bridge.

Provides the GhidraAdapter that bridges the canonical domain model to
PyGhidra/Ghidra. The adapter module contains the GhidraAdapter class and
the bridge module handles JVM startup and Ghidra API translation.

Exports:
    GhidraAdapter: Backend adapter implementing the BackendAdapter interface
        with PROJECT_SERIALIZED concurrency and capability detection.
"""

from __future__ import annotations

from binary_analysis.adapters.ghidra.adapter import GhidraAdapter

__all__ = ["GhidraAdapter"]
