"""Unit tests for entity selectors."""

from __future__ import annotations

import sys
from pathlib import Path
_scripts_dir = Path(__file__).resolve().parents[2] / "scripts"
if str(_scripts_dir) not in sys.path:
    sys.path.insert(0, str(_scripts_dir))

import pytest
from binary_analysis.domain.entities import Address, Function
from binary_analysis.domain.errors import AmbiguousSelectorError, EntityNotFoundError
from binary_analysis.domain.selectors import (
    SelectorKind,
    format_candidates,
    parse_selector,
    resolve_function,
    resolve_functions,
)


class TestParseSelector:
    """Tests for selector parsing."""

    def test_parse_function_by_name(self) -> None:
        parsed = parse_selector("function:main")
        assert parsed.kind == SelectorKind.FUNCTION
        assert parsed.value == "main"
        assert parsed.is_address is False

    def test_parse_function_by_address(self) -> None:
        parsed = parse_selector("function:0x401000")
        assert parsed.kind == SelectorKind.FUNCTION
        assert parsed.value == "0x401000"
        assert parsed.is_address is True
        assert parsed.address_value == "401000"

    def test_parse_address_range(self) -> None:
        parsed = parse_selector("address:0x1000..0x2000")
        assert parsed.kind == SelectorKind.ADDRESS
        assert parsed.is_range is True
        assert parsed.range_start == "0x1000"
        assert parsed.range_end == "0x2000"

    def test_parse_implicit_function_name(self) -> None:
        """Bare name should be parsed as implicit function selector."""
        parsed = parse_selector("main")
        assert parsed.kind == SelectorKind.FUNCTION
        assert parsed.value == "main"

    def test_parse_implicit_address(self) -> None:
        """Bare hex address should be parsed as implicit address selector."""
        parsed = parse_selector("0x401000")
        assert parsed.kind == SelectorKind.ADDRESS
        assert parsed.value == "0x401000"
        assert parsed.is_address is True

    def test_parse_case_insensitive_kind(self) -> None:
        """Selector kind should be case-insensitive."""
        parsed = parse_selector("FUNCTION:main")
        assert parsed.kind == SelectorKind.FUNCTION

    def test_parse_name_selector(self) -> None:
        parsed = parse_selector("name:my_entity")
        assert parsed.kind == SelectorKind.NAME
        assert parsed.value == "my_entity"

    def test_parse_address_without_prefix(self) -> None:
        """Address without 0x prefix is still recognized as address."""
        parsed = parse_selector("401000")
        assert parsed.kind == SelectorKind.ADDRESS
        assert parsed.is_address is True

    def test_parse_function_without_prefix(self) -> None:
        """function:addr without 0x prefix still works."""
        parsed = parse_selector("function:401000")
        assert parsed.kind == SelectorKind.FUNCTION
        assert parsed.is_address is True
        assert parsed.address_value == "401000"

    def test_parse_empty_string(self) -> None:
        """Empty string should still parse without error."""
        parsed = parse_selector("")
        assert parsed.kind == SelectorKind.FUNCTION
        assert parsed.value == ""


class TestResolveFunction:
    """Tests for function resolution."""

    def _make_functions(self) -> list[Function]:
        """Create a standard set of test functions."""
        return [
            Function(
                name="main",
                address=Address(space="ram", offset="0x401000", display="0x401000"),
                size_bytes=256,
            ),
            Function(
                name="_start",
                address=Address(space="ram", offset="0x401100", display="0x401100"),
                size_bytes=64,
            ),
            Function(
                name="helper_func",
                address=Address(space="ram", offset="0x401200", display="0x401200"),
                size_bytes=128,
            ),
            Function(
                name="helper_other",
                address=Address(space="ram", offset="0x401300", display="0x401300"),
                size_bytes=96,
            ),
        ]

    def test_resolve_by_exact_name(self) -> None:
        """Resolve function by exact name."""
        funcs = self._make_functions()
        parsed = parse_selector("function:main")
        result = resolve_function(parsed, funcs)
        assert result.name == "main"
        assert result.address is not None
        assert result.address.offset == "0x401000"

    def test_resolve_by_address(self) -> None:
        """Resolve function by address."""
        funcs = self._make_functions()
        parsed = parse_selector("function:0x401200")
        result = resolve_function(parsed, funcs)
        assert result.name == "helper_func"

    def test_resolve_by_fuzzy_name(self) -> None:
        """Resolve function by fuzzy name (substring match)."""
        funcs = self._make_functions()
        parsed = parse_selector("function:helper")
        # "helper" matches both helper_func and helper_other
        # When require_unique=True, this should raise AmbiguousSelectorError
        with pytest.raises(AmbiguousSelectorError) as exc_info:
            resolve_function(parsed, funcs, require_unique=True)
        assert len(exc_info.value.candidates) == 2

    def test_resolve_fuzzy_not_unique(self) -> None:
        """resolve_functions returns all matches for fuzzy selector."""
        funcs = self._make_functions()
        parsed = parse_selector("function:helper")
        results = resolve_functions(parsed, funcs)
        assert len(results) == 2

    def test_resolve_not_found(self) -> None:
        """Resolve nonexistent function raises EntityNotFoundError."""
        funcs = self._make_functions()
        parsed = parse_selector("function:nonexistent")
        with pytest.raises(EntityNotFoundError) as exc_info:
            resolve_function(parsed, funcs)
        assert exc_info.value.entity_type == "Function"
        assert exc_info.value.selector == "function:nonexistent"

    def test_resolve_implicit_function_name(self) -> None:
        """Bare name should resolve as function."""
        funcs = self._make_functions()
        parsed = parse_selector("_start")
        result = resolve_function(parsed, funcs)
        assert result.name == "_start"

    def test_resolve_unique_match_no_ambiguity(self) -> None:
        """Unique match should not raise AmbiguousSelectorError."""
        funcs = self._make_functions()
        parsed = parse_selector("function:_start")
        result = resolve_function(parsed, funcs, require_unique=True)
        assert result.name == "_start"


class TestFormatCandidates:
    """Tests for candidate formatting."""

    def test_format_candidates(self) -> None:
        candidates = [
            {"name": "func_a", "address": {"display": "0x401000"}},
            {"name": "func_b", "address": {"display": "0x402000"}},
        ]
        output = format_candidates(candidates)
        assert "Ambiguous selector matches multiple entities:" in output
        assert "func_a @ 0x401000" in output
        assert "func_b @ 0x402000" in output

    def test_format_candidates_empty(self) -> None:
        output = format_candidates([])
        assert output  # Should not error, just be empty-list message
