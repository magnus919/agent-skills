"""Backend adapters — abstract interface, FakeAdapter for testing, Ghidra adapter."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from binary_analysis.adapters.base import (
    AnalysisProfile,
    AnalysisResult,
    BackendAdapter,
    BinaryMetadata,
    CallEdge,
    ConcurrencyMode,
    DecompilationResult,
)
from binary_analysis.adapters.ghidra import GhidraAdapter

if TYPE_CHECKING:
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
    "GhidraAdapter",
]


def __getattr__(name: str) -> Any:
    """Load the test fake only when a caller explicitly requests it."""
    if name == "FakeAdapter":
        from binary_analysis.adapters.fake import FakeAdapter

        return FakeAdapter
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
