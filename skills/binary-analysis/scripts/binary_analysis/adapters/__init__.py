"""Backend adapters — abstract interface, FakeAdapter for testing, Ghidra adapter."""

from __future__ import annotations

from binary_analysis.adapters.base import (
    AnalysisProfile,
    AnalysisResult,
    BackendAdapter,
    BinaryMetadata,
    CallEdge,
    ConcurrencyMode,
    DecompilationResult,
)
from binary_analysis.adapters.fake import FakeAdapter

__all__ = [
    "AnalysisProfile",
    "AnalysisResult",
    "BackendAdapter",
    "BinaryMetadata",
    "CallEdge",
    "ConcurrencyMode",
    "DecompilationResult",
    "FakeAdapter",
]
