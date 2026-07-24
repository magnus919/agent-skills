"""Adapter protocol defining the harness contract."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from .models import AdapterInput, AdapterOutput


@runtime_checkable
class HarnessAdapter(Protocol):
    """Contract for executing an eval case against a candidate skill.

    Implementations must be non-interactive and deterministic given the same
    inputs (modulo model non-determinism in real adapters). Raw traces may
    remain adapter-specific; only evidence required by declared graders is
    normalized in AdapterOutput.
    """

    @property
    def name(self) -> str:
        """Stable adapter identifier, e.g. 'fake', 'cli-subprocess'."""
        ...

    @property
    def version(self) -> str:
        """Adapter implementation version."""
        ...

    def execute(self, input: AdapterInput) -> AdapterOutput:
        """Run one eval case and return normalized results.

        Must not raise on expected failure modes (timeout, model error, skill
        not found). Encode failures in AdapterOutput.exit_status and .error.
        Unexpected infrastructure errors may raise.
        """
        ...
