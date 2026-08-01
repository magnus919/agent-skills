"""Dependency discovery — precedence, verification, bootstrap plan."""

from __future__ import annotations

from binary_analysis.bootstrap.deps import Dependency, discover_dependencies

__all__ = [
    "Dependency",
    "discover_dependencies",
]
