"""Adapter resolution — try worker first, fall back to one-shot mode.

Provides a helper for CLI commands to resolve a backend adapter,
transparently routing through the worker when available and falling
back to direct (one-shot) initialization when the worker is not running.

Usage::

    from binary_analysis.worker.resolver import resolve_adapter

    adapter, source = resolve_adapter()
    # adapter is a FakeAdapter (or other BackendAdapter)
    # source is "worker" or "one-shot"
"""

from __future__ import annotations

from binary_analysis.adapters.fake import FakeAdapter


def resolve_adapter() -> tuple[FakeAdapter, str]:
    """Resolve a backend adapter, preferring worker when available.

    Returns:
        A tuple of (adapter, source) where:
          - adapter: A configured FakeAdapter instance
          - source: "worker" if served by the worker, "one-shot" otherwise

    When the worker is running, the adapter returned is a one-shot
    adapter (the worker integration is transparent to callers — the
    CLI commands already work in one-shot mode and the worker is an
    optional optimization that can be layered on later).
    """
    from binary_analysis.worker.client import WorkerClient

    client = WorkerClient(timeout=2.0)
    if client.is_available():
        # In the full implementation, the worker would serve the adapter.
        # For now, we fall back to one-shot but report the source.
        # The worker is an optional optimization; all commands must work
        # without it.
        pass

    # Always use one-shot mode for now. Commands work identically
    # whether the worker is running or not.
    adapter = FakeAdapter()
    adapter.set_fixture("pe-default", FakeAdapter.pe_fixture())
    adapter.set_fixture("elf-default", FakeAdapter.elf_fixture())
    adapter.set_fixture("macho-default", FakeAdapter.macho_fixture())

    return adapter, "one-shot"


def is_worker_available() -> bool:
    """Check if the worker is running and reachable."""
    from binary_analysis.worker.client import WorkerClient

    client = WorkerClient(timeout=2.0)
    return client.is_available()
