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
from binary_analysis.adapters.ghidra import GhidraAdapter

__all__ = [
    "AnalysisProfile",
    "AnalysisResult",
    "BackendAdapter",
    "BinaryMetadata",
    "CallEdge",
    "ConcurrencyMode",
    "DecompilationResult",
    "FakeAdapter",
    "GhidraAdapter",
]
