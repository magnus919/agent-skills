"""Heuristic and capability rules engine.

Provides:
- TriageEngine: produces Observations, Heuristics, and Unknowns from backend data.
- Rule evaluation infrastructure (extensible for suspicious-apis, capability-map).
"""

from __future__ import annotations

from binary_analysis.rules.engine import TriageEngine

__all__ = ["TriageEngine"]
