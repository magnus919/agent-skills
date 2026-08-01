"""Heuristic and capability rules engine.

Provides:
- TriageEngine: produces Observations, Heuristics, and Unknowns from backend data.
- SuspiciousApisEngine: evaluates priority-tagged rules against imported APIs.
- CapabilityMapEngine: produces functional area suggestions from backend data.
- Rule evaluation infrastructure (extensible for suspicious-apis, capability-map).
"""

from __future__ import annotations

from binary_analysis.rules.capabilities import CapabilityMapEngine, CapabilityResult
from binary_analysis.rules.engine import TriageEngine
from binary_analysis.rules.suspicious_apis import SuspiciousApiMatch, SuspiciousApisEngine

__all__ = [
    "CapabilityMapEngine",
    "CapabilityResult",
    "SuspiciousApiMatch",
    "SuspiciousApisEngine",
    "TriageEngine",
]
