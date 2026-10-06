"""Explicit fixture backend injection for the legacy offline contract suite.

Production CLI subprocess tests in scripts/test_runtime_backend.py run without
this injection and verify that fixture data can never masquerade as analysis.
"""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))


@pytest.fixture(autouse=True)
def fixture_backend(monkeypatch):
    from binary_analysis.adapters import runtime
    from binary_analysis.adapters.fake import FakeAdapter

    original = FakeAdapter._get_binary_fixture

    def resolve_fixture(self, binary):
        if str(binary.id) not in self._binaries:
            fmt = binary.format.lower()
            name = 'elf-default' if 'elf' in fmt else 'macho-default' if 'mach' in fmt else 'pe-default'
            self.register_binary(binary, name)
        return original(self, binary)

    def factory():
        adapter = FakeAdapter()
        adapter.set_fixture('pe-default', FakeAdapter.pe_fixture())
        adapter.set_fixture('elf-default', FakeAdapter.elf_fixture())
        adapter.set_fixture('macho-default', FakeAdapter.macho_fixture())
        return adapter

    monkeypatch.setattr(FakeAdapter, '_get_binary_fixture', resolve_fixture)
    monkeypatch.setattr(runtime, 'get_adapter', factory)
