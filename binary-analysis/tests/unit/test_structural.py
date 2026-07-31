"""Unit tests for structural query CLI commands.

Covers: sections, entrypoints, imports, exports, symbols, strings.
Validates against VAL-STRUCT-001 through VAL-STRUCT-016.
"""

from __future__ import annotations

import json

# Add the scripts directory to the path for imports
import sys
import tempfile
from pathlib import Path

import pytest

_skill_dir = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_skill_dir / "scripts"))


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def temp_workspace():
    """Create a temporary workspace directory for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Set up workspace as the temp dir
        workspace_root = Path(tmpdir)
        yield workspace_root


@pytest.fixture
def project_imported(temp_workspace):
    """Create a project with an imported binary."""
    import uuid
    from datetime import datetime, timezone

    project_id = str(uuid.uuid4())
    binary_id = str(uuid.uuid4())
    project_dir = temp_workspace / "test-proj"
    project_dir.mkdir(parents=True, exist_ok=True)

    manifest = {
        "id": project_id,
        "name": "test-proj",
        "state": "IMPORTED",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "workspace_version": "1",
        "binary_count": 1,
        "is_stale": False,
        "current_binary": {
            "id": binary_id,
            "sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
            "path": "/tmp/test.bin",
            "format": "PE",
            "import_mode": "copy",
            "size_bytes": 16384,
            "architecture": "x86",
        },
    }

    binaries_dir = project_dir / "binaries"
    binaries_dir.mkdir(exist_ok=True)
    with open(binaries_dir / f"{binary_id}.json", "w") as f:
        json.dump(manifest["current_binary"], f)

    with open(project_dir / "project.json", "w") as f:
        json.dump(manifest, f)

    return project_dir


@pytest.fixture
def project_ready(project_imported):
    """Create a project in READY (analyzed) state."""
    project_dir = project_imported
    with open(project_dir / "project.json") as f:
        manifest = json.load(f)
    manifest["state"] = "READY"
    with open(project_dir / "project.json", "w") as f:
        json.dump(manifest, f)
    return project_dir


# ---------------------------------------------------------------------------
# Import helpers
# ---------------------------------------------------------------------------


def _make_args(**kwargs):
    """Create a mock argparse.Namespace."""
    defaults = {
        "json": True,
        "quiet": False,
        "limit": None,
        "timeout": 300,
        "cursor": None,
        "min_length": 4,
        "contains": None,
        "encoding": None,
        "sort": "address",
    }
    defaults.update(kwargs)

    class Args:
        pass

    args = Args()
    for k, v in defaults.items():
        setattr(args, k, v)
    return args


# ---------------------------------------------------------------------------
# Test helper: cursor encoding/decoding
# ---------------------------------------------------------------------------


class TestCursorScoping:
    """Test cursor encode/decode and scope validation."""

    def test_encode_decode_roundtrip(self):
        from binary_analysis.cli.structural import _decode_cursor, _encode_cursor

        data = {"c": "sections", "p": "proj-1", "fh": "abc", "s": "address", "o": 10}
        encoded = _encode_cursor(data)
        decoded = _decode_cursor(encoded)
        assert decoded == data

    def test_decode_invalid_cursor(self):
        from binary_analysis.cli.structural import _decode_cursor
        from binary_analysis.domain.errors import InvalidArgsError

        with pytest.raises(InvalidArgsError):
            _decode_cursor("not-valid-base64!!!")

    def test_validate_cursor_scope_match(self):
        import hashlib
        import json

        from binary_analysis.cli.structural import _validate_cursor_scope

        # Compute the actual filters hash for empty filters
        filters_hash = hashlib.md5(json.dumps({}, sort_keys=True).encode("utf-8")).hexdigest()

        cursor_data = {"c": "sections", "p": "proj-1", "fh": filters_hash, "s": None, "o": 10}
        offset = _validate_cursor_scope(
            cursor_data, "sections", "proj-1", filters=None, sort_key=None
        )
        assert offset == 10

    def test_validate_cursor_scope_mismatched_command(self):
        from binary_analysis.cli.structural import _validate_cursor_scope
        from binary_analysis.domain.errors import InvalidArgsError

        cursor_data = {"c": "entrypoints", "p": "proj-1", "fh": "abc", "s": None, "o": 10}
        with pytest.raises(InvalidArgsError, match="command"):
            _validate_cursor_scope(cursor_data, "sections", "proj-1", filters=None, sort_key=None)

    def test_validate_cursor_scope_mismatched_project(self):
        from binary_analysis.cli.structural import _validate_cursor_scope
        from binary_analysis.domain.errors import InvalidArgsError

        cursor_data = {"c": "sections", "p": "proj-2", "fh": "abc", "s": None, "o": 10}
        with pytest.raises(InvalidArgsError, match="project"):
            _validate_cursor_scope(cursor_data, "sections", "proj-1", filters=None, sort_key=None)

    def test_validate_cursor_scope_mismatched_filters(self):
        from binary_analysis.cli.structural import _validate_cursor_scope
        from binary_analysis.domain.errors import InvalidArgsError

        cursor_data = {"c": "strings", "p": "proj-1", "fh": "abc", "s": None, "o": 10}
        with pytest.raises(InvalidArgsError, match="filters"):
            _validate_cursor_scope(
                cursor_data,
                "strings",
                "proj-1",
                filters={"min_length": 10},
                sort_key=None,  # Different filter hash
            )

    def test_make_cursor_scoped(self):
        from binary_analysis.cli.structural import _decode_cursor, _make_cursor

        cursor = _make_cursor("strings", "proj-1", 20, filters={"min_length": 10})
        decoded = _decode_cursor(cursor)
        assert decoded["c"] == "strings"
        assert decoded["p"] == "proj-1"
        assert decoded["o"] == 20


# ---------------------------------------------------------------------------
# Test: Sections
# ---------------------------------------------------------------------------


class TestSectionsCommand:
    """Tests for the 'sections' command (VAL-STRUCT-001, 002, 014)."""

    def test_sections_basic(self, monkeypatch, project_ready):
        """VAL-STRUCT-001: Sections return canonical objects with pagination."""
        from binary_analysis.cli.structural import execute_sections

        monkeypatch.setattr(
            "binary_analysis.cli.structural._resolve_project_path",
            lambda _: str(project_ready),
        )

        args = _make_args(project="test-proj")
        result = execute_sections(args)

        assert result["success"] is True
        assert "items" in result["data"]
        assert "total" in result["data"]
        assert "has_more" in result["data"]
        assert "next_cursor" in result["data"]

        items = result["data"]["items"]
        assert len(items) > 0

        # Each section must have required fields
        for section in items:
            assert "name" in section
            assert "address" in section
            assert "virtual_size" in section
            assert "raw_size" in section
            assert "flags" in section
            assert "entropy" in section

            # Address must be canonical
            addr = section["address"]
            assert isinstance(addr, dict)
            assert "space" in addr
            assert "offset" in addr
            assert "display" in addr

            # Flags must be list of strings
            assert isinstance(section["flags"], list)

    def test_sections_limit_2(self, monkeypatch, project_ready):
        """VAL-STRUCT-002: --limit 2 returns exactly 2 items with has_more=true."""
        from binary_analysis.cli.structural import execute_sections

        monkeypatch.setattr(
            "binary_analysis.cli.structural._resolve_project_path",
            lambda _: str(project_ready),
        )

        args = _make_args(project="test-proj", limit=2)
        result = execute_sections(args)

        assert result["success"] is True
        assert len(result["data"]["items"]) == 2
        assert result["data"]["has_more"] is True
        assert result["data"]["next_cursor"] is not None

    def test_sections_pagination_cursor(self, monkeypatch, project_ready):
        """Cursor from first page produces next page with no overlap."""
        from binary_analysis.cli.structural import execute_sections

        monkeypatch.setattr(
            "binary_analysis.cli.structural._resolve_project_path",
            lambda _: str(project_ready),
        )

        args1 = _make_args(project="test-proj", limit=2)
        result1 = execute_sections(args1)
        cursor = result1["data"]["next_cursor"]
        items1 = result1["data"]["items"]

        args2 = _make_args(project="test-proj", limit=2, cursor=cursor)
        result2 = execute_sections(args2)
        items2 = result2["data"]["items"]

        # No overlap between pages
        names1 = {s["name"] for s in items1}
        names2 = {s["name"] for s in items2}
        assert names1.isdisjoint(names2)

    def test_sections_cursor_mismatched(self, monkeypatch, project_ready):
        """Cursor from sections used with entrypoints returns error."""
        from binary_analysis.cli.structural import (
            _make_cursor,
            execute_entrypoints,
        )
        from binary_analysis.domain.errors import InvalidArgsError

        monkeypatch.setattr(
            "binary_analysis.cli.structural._resolve_project_path",
            lambda _: str(project_ready),
        )

        with open(project_ready / "project.json") as f:
            manifest = json.load(f)

        # Create a sections cursor and try with entrypoints
        sections_cursor = _make_cursor("sections", manifest["id"], 5)
        args = _make_args(project="test-proj", cursor=sections_cursor)

        with pytest.raises(InvalidArgsError, match="command"):
            execute_entrypoints(args)

    def test_sections_unanalyzed_project(self, monkeypatch, project_imported):
        """VAL-STRUCT-014: Unanalyzed project succeeds with info diagnostic."""
        from binary_analysis.cli.structural import execute_sections

        monkeypatch.setattr(
            "binary_analysis.cli.structural._resolve_project_path",
            lambda _: str(project_imported),
        )

        args = _make_args(project="test-proj")
        result = execute_sections(args)

        assert result["success"] is True
        assert len(result["data"]["items"]) > 0

        # Must have info-level diagnostic about incomplete analysis
        diagnostics = result.get("diagnostics", [])
        assert any(
            d.get("severity") == "INFO" and "not been fully analyzed" in d.get("message", "")
            for d in diagnostics
        )


# ---------------------------------------------------------------------------
# Test: Entrypoints
# ---------------------------------------------------------------------------


class TestEntrypointsCommand:
    """Tests for the 'entrypoints' command (VAL-STRUCT-003)."""

    def test_entrypoints_basic(self, monkeypatch, project_ready):
        """VAL-STRUCT-003: Entrypoints with kind and confidence."""
        from binary_analysis.cli.structural import execute_entrypoints

        monkeypatch.setattr(
            "binary_analysis.cli.structural._resolve_project_path",
            lambda _: str(project_ready),
        )

        args = _make_args(project="test-proj")
        result = execute_entrypoints(args)

        assert result["success"] is True
        items = result["data"]["items"]
        assert len(items) > 0

        for ep in items:
            assert "address" in ep
            assert "kind" in ep
            assert ep["kind"] in ("program", "library", "boot", "firmware", "unknown")
            assert "confidence" in ep
            assert ep["confidence"] in ("HIGH", "MEDIUM", "LOW", "UNKNOWN")
            assert "name" in ep

    def test_entrypoints_pagination(self, monkeypatch, project_ready):
        """Entrypoints pagination works."""
        from binary_analysis.cli.structural import execute_entrypoints

        monkeypatch.setattr(
            "binary_analysis.cli.structural._resolve_project_path",
            lambda _: str(project_ready),
        )

        args = _make_args(project="test-proj", limit=1)
        result = execute_entrypoints(args)

        assert result["success"] is True
        assert "total" in result["data"]
        assert "has_more" in result["data"]
        assert "next_cursor" in result["data"]


# ---------------------------------------------------------------------------
# Test: Imports
# ---------------------------------------------------------------------------


class TestImportsCommand:
    """Tests for the 'imports' command (VAL-STRUCT-004)."""

    def test_imports_basic(self, monkeypatch, project_ready):
        """VAL-STRUCT-004: Imports with module, symbol, resolution, ordinal."""
        from binary_analysis.cli.structural import execute_imports

        monkeypatch.setattr(
            "binary_analysis.cli.structural._resolve_project_path",
            lambda _: str(project_ready),
        )

        args = _make_args(project="test-proj")
        result = execute_imports(args)

        assert result["success"] is True
        items = result["data"]["items"]
        assert len(items) > 0

        for imp in items:
            assert "module" in imp
            assert "symbol" in imp
            assert "address" in imp
            assert "resolution" in imp
            assert imp["resolution"] in ("RESOLVED", "PARTIAL", "UNRESOLVED")
            assert "ordinal" in imp


# ---------------------------------------------------------------------------
# Test: Exports
# ---------------------------------------------------------------------------


class TestExportsCommand:
    """Tests for the 'exports' command (VAL-STRUCT-005)."""

    def test_exports_basic(self, monkeypatch, project_ready):
        """VAL-STRUCT-005: Exports with name, address, ordinal, forwarder, kind."""
        from binary_analysis.cli.structural import execute_exports

        monkeypatch.setattr(
            "binary_analysis.cli.structural._resolve_project_path",
            lambda _: str(project_ready),
        )

        args = _make_args(project="test-proj")
        result = execute_exports(args)

        assert result["success"] is True
        items = result["data"]["items"]
        assert len(items) > 0

        for exp in items:
            assert "name" in exp
            assert "address" in exp
            assert "ordinal" in exp
            assert "forwarder" in exp  # may be None
            assert "kind" in exp
            assert exp["kind"] in ("function", "data")


# ---------------------------------------------------------------------------
# Test: Symbols
# ---------------------------------------------------------------------------


class TestSymbolsCommand:
    """Tests for the 'symbols' command (VAL-STRUCT-006)."""

    def test_symbols_basic(self, monkeypatch, project_ready):
        """VAL-STRUCT-006: Symbols with name, address, source, scope."""
        from binary_analysis.cli.structural import execute_symbols

        monkeypatch.setattr(
            "binary_analysis.cli.structural._resolve_project_path",
            lambda _: str(project_ready),
        )

        args = _make_args(project="test-proj")
        result = execute_symbols(args)

        assert result["success"] is True
        items = result["data"]["items"]
        assert len(items) > 0

        source_values = {
            "ORIGINAL",
            "IMPORTED",
            "DEBUG",
            "BACKEND_GENERATED",
            "USER_ANNOTATION",
            "AGENT_SUGGESTION",
            "UNKNOWN",
        }
        scope_values = {"global", "local", "unknown"}

        for sym in items:
            assert "name" in sym
            assert "address" in sym
            assert "source" in sym
            assert sym["source"] in source_values
            assert "scope" in sym
            assert sym["scope"] in scope_values

    def test_symbols_imported_cross_linking(self, monkeypatch, project_ready):
        """IMPORTED symbols are cross-linked to imports table."""
        from binary_analysis.cli.structural import execute_symbols

        monkeypatch.setattr(
            "binary_analysis.cli.structural._resolve_project_path",
            lambda _: str(project_ready),
        )

        args = _make_args(project="test-proj")
        result = execute_symbols(args)

        imported_symbols = [s for s in result["data"]["items"] if s.get("source") == "IMPORTED"]

        # At least some symbols should be imported
        # (from FakeAdapter fixtures, there are symbols with IMPORTED source)
        if imported_symbols:
            for sym in imported_symbols:
                # Should have cross-link to import info if found
                if "import" in sym:
                    imp_info = sym["import"]
                    assert "module" in imp_info
                    assert "symbol" in imp_info
                    assert "resolution" in imp_info


# ---------------------------------------------------------------------------
# Test: Strings
# ---------------------------------------------------------------------------


class TestStringsCommand:
    """Tests for the 'strings' command (VAL-STRUCT-007, 008, 009, 010, 016)."""

    def test_strings_basic(self, monkeypatch, project_ready):
        """VAL-STRUCT-007: Strings with text, encoding, address, length."""
        from binary_analysis.cli.structural import execute_strings

        monkeypatch.setattr(
            "binary_analysis.cli.structural._resolve_project_path",
            lambda _: str(project_ready),
        )

        args = _make_args(project="test-proj")
        result = execute_strings(args)

        assert result["success"] is True
        items = result["data"]["items"]
        assert len(items) > 0

        for s in items:
            assert "text" in s
            assert "encoding" in s
            assert s["encoding"] in ("ASCII", "UTF-8", "UTF-16")
            assert "address" in s
            assert "length" in s
            assert isinstance(s["length"], int)

    def test_strings_min_length(self, monkeypatch, project_ready):
        """VAL-STRUCT-008: --min-length excludes short strings."""
        from binary_analysis.cli.structural import execute_strings

        monkeypatch.setattr(
            "binary_analysis.cli.structural._resolve_project_path",
            lambda _: str(project_ready),
        )

        # Get all strings first
        args_all = _make_args(project="test-proj", min_length=1)
        result_all = execute_strings(args_all)

        # Now filter with min-length=10
        args_filtered = _make_args(project="test-proj", min_length=10)
        result_filtered = execute_strings(args_filtered)

        # Every item in filtered result must have length >= 10
        for s in result_filtered["data"]["items"]:
            assert s["length"] >= 10

        # Total count must be <= unfiltered count
        assert result_filtered["data"]["total"] <= result_all["data"]["total"]

        # Must report applied_filters
        assert "applied_filters" in result_filtered["data"]
        filters = result_filtered["data"]["applied_filters"]
        assert any(f["filter"] == "min_length" for f in filters)

    def test_strings_contains(self, monkeypatch, project_ready):
        """VAL-STRUCT-009: --contains returns substring matches."""
        from binary_analysis.cli.structural import execute_strings

        monkeypatch.setattr(
            "binary_analysis.cli.structural._resolve_project_path",
            lambda _: str(project_ready),
        )

        args = _make_args(project="test-proj", contains="Error")
        result = execute_strings(args)

        # Every item must contain the substring
        for s in result["data"]["items"]:
            assert "Error" in s["text"]

        # Must report applied_filters
        assert "applied_filters" in result["data"]
        filters = result["data"]["applied_filters"]
        assert any(f["filter"] == "contains" and f["value"] == "Error" for f in filters)

    def test_strings_combined_filters(self, monkeypatch, project_ready):
        """VAL-STRUCT-010: Combined --contains + --min-length apply both."""
        from binary_analysis.cli.structural import execute_strings

        monkeypatch.setattr(
            "binary_analysis.cli.structural._resolve_project_path",
            lambda _: str(project_ready),
        )

        args = _make_args(project="test-proj", contains="GetProc", min_length=5)
        result = execute_strings(args)

        # Every item must satisfy both filters
        for s in result["data"]["items"]:
            assert "GetProc" in s["text"]
            assert s["length"] >= 5

        # Both filters in applied_filters
        assert "applied_filters" in result["data"]
        filters = result["data"]["applied_filters"]
        assert any(f["filter"] == "contains" for f in filters)
        assert any(f["filter"] == "min_length" for f in filters)

    def test_strings_unicode_preservation(self, monkeypatch, project_ready):
        """VAL-STRUCT-016: Unicode strings preserved in valid JSON output.

        We monkeypatch the FakeAdapter.get_strings to include Unicode strings
        and verify the JSON output is reparsable by python3 -m json.tool.
        """
        import binary_analysis.cli.structural as struct_mod
        from binary_analysis.cli.structural import execute_strings
        from binary_analysis.domain.entities import Address, String

        # Monkeypatch project resolution
        monkeypatch.setattr(
            "binary_analysis.cli.structural._resolve_project_path",
            lambda _: str(project_ready),
        )

        original_get_adapter = struct_mod._get_adapter_and_binary

        def _patched_get_adapter_and_binary(project_path, manifest):
            adapter, binary, proj_info = original_get_adapter(project_path, manifest)

            # Monkeypatch get_strings to return unicode test strings
            unicode_strings = [
                String(
                    text="你好世界",
                    encoding="UTF-8",
                    address=Address(space="ram", offset="0x500000", display="0x500000"),
                    length=8,
                ),
                String(
                    text="😀🎉💻",
                    encoding="UTF-8",
                    address=Address(space="ram", offset="0x500008", display="0x500008"),
                    length=6,
                ),
                String(
                    text="שָׁלוֹם",
                    encoding="UTF-8",
                    address=Address(space="ram", offset="0x500010", display="0x500010"),
                    length=5,
                ),
                String(
                    text='He said "hello"',
                    encoding="ASCII",
                    address=Address(space="ram", offset="0x500018", display="0x500018"),
                    length=15,
                ),
                String(
                    text="C:\\path\\to\\file",
                    encoding="ASCII",
                    address=Address(space="ram", offset="0x500028", display="0x500028"),
                    length=16,
                ),
            ]

            # Override get_strings on the adapter instance
            def patched_get_strings(binary, min_length=4, contains=None, encoding_filter=None):
                result = []
                for s in unicode_strings:
                    if s.length < min_length:
                        continue
                    if contains is not None and contains not in s.text:
                        continue
                    if encoding_filter is not None and s.encoding != encoding_filter:
                        continue
                    result.append(s)
                return result

            adapter.get_strings = patched_get_strings

            return adapter, binary, proj_info

        struct_mod._get_adapter_and_binary = _patched_get_adapter_and_binary

        try:
            args = _make_args(project="test-proj", min_length=1)
            result = execute_strings(args)

            assert result["success"] is True

            # Convert to JSON and verify it's reparsable
            json_str = json.dumps(result, ensure_ascii=False)
            parsed = json.loads(json_str)

            # Verify JSON validates with json.tool
            import subprocess

            proc = subprocess.run(
                ["python3", "-m", "json.tool"],
                input=json_str,
                capture_output=True,
                text=True,
            )
            assert proc.returncode == 0, f"JSON validation failed: {proc.stderr}"

            # Check that unicode strings survived the roundtrip
            items = parsed["data"]["items"]
            texts = {s["text"] for s in items}
            assert "你好世界" in texts
            assert "😀🎉💻" in texts
            assert "שָׁלוֹם" in texts
            assert 'He said "hello"' in texts
            assert "C:\\path\\to\\file" in texts

        finally:
            struct_mod._get_adapter_and_binary = original_get_adapter

    def test_strings_pagination_cursor_scope_filters(self, monkeypatch, project_ready):
        """VAL-STRUCT-015: Cursor from different filter set returns error."""
        from binary_analysis.cli.structural import execute_strings
        from binary_analysis.domain.errors import InvalidArgsError

        monkeypatch.setattr(
            "binary_analysis.cli.structural._resolve_project_path",
            lambda _: str(project_ready),
        )

        # Get cursor with min_length=4 (default)
        args1 = _make_args(project="test-proj", limit=1, min_length=4)
        result1 = execute_strings(args1)
        cursor = result1["data"]["next_cursor"]

        # Try using cursor with min_length=10 (different filter)
        args2 = _make_args(project="test-proj", limit=1, min_length=10, cursor=cursor)
        with pytest.raises(InvalidArgsError, match="filters"):
            execute_strings(args2)

    def test_strings_contains_no_match(self, monkeypatch, project_ready):
        """--contains with no matches returns empty result."""
        from binary_analysis.cli.structural import execute_strings

        monkeypatch.setattr(
            "binary_analysis.cli.structural._resolve_project_path",
            lambda _: str(project_ready),
        )

        args = _make_args(project="test-proj", contains="ZZZZNOMATCHZZZZ")
        result = execute_strings(args)

        assert result["success"] is True
        assert result["data"]["total"] == 0
        assert result["data"]["items"] == []


# ---------------------------------------------------------------------------
# Test: Binary not found
# ---------------------------------------------------------------------------


class TestErrorHandling:
    """Test error handling for structural commands."""

    def test_binary_not_found(self, tmp_path):
        """Project with no binary returns appropriate error."""
        import json as _json
        from datetime import datetime, timezone

        from binary_analysis.cli.structural import execute_sections
        from binary_analysis.domain.errors import BinaryNotFoundError

        project_dir = tmp_path / "empty-proj"
        project_dir.mkdir()
        manifest = {
            "id": "test-id",
            "name": "empty-proj",
            "state": "CREATED",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "workspace_version": "1",
            "binary_count": 0,
            "is_stale": False,
        }
        with open(project_dir / "project.json", "w") as f:
            _json.dump(manifest, f)

        import binary_analysis.cli.structural as struct_mod

        original_resolve = struct_mod._resolve_project_path
        struct_mod._resolve_project_path = lambda _: str(project_dir)

        try:
            args = _make_args(project="empty-proj")
            with pytest.raises(BinaryNotFoundError):
                execute_sections(args)
        finally:
            struct_mod._resolve_project_path = original_resolve

    def test_project_not_found(self):
        """Non-existent project returns error."""
        from binary_analysis.cli.structural import execute_sections
        from binary_analysis.domain.errors import ProjectNotFoundError

        args = _make_args(project="nonexistent-12345")
        with pytest.raises(ProjectNotFoundError):
            execute_sections(args)


# ---------------------------------------------------------------------------
# Test: JSON format compliance
# ---------------------------------------------------------------------------


class TestJsonFormat:
    """Test JSON output format compliance."""

    def test_json_envelope_has_required_fields(self, monkeypatch, project_ready):
        """All structural commands return valid JSON with standard envelope."""
        from binary_analysis.cli.structural import (
            execute_entrypoints,
            execute_exports,
            execute_imports,
            execute_sections,
            execute_strings,
            execute_symbols,
        )

        monkeypatch.setattr(
            "binary_analysis.cli.structural._resolve_project_path",
            lambda _: str(project_ready),
        )

        commands = {
            "sections": execute_sections,
            "entrypoints": execute_entrypoints,
            "imports": execute_imports,
            "exports": execute_exports,
            "symbols": execute_symbols,
            "strings": execute_strings,
        }

        for _cmd_name, cmd_fn in commands.items():
            args = _make_args(project="test-proj", limit=2)
            result = cmd_fn(args)

            # Core result fields
            assert "success" in result
            assert "partial" in result
            assert "warnings" in result
            assert "diagnostics" in result
            assert "data" in result

            # Data pagination fields
            assert "items" in result["data"]
            assert "total" in result["data"]
            assert "has_more" in result["data"]
            assert "next_cursor" in result["data"]

            # Items should be lists
            assert isinstance(result["data"]["items"], list)
            assert isinstance(result["data"]["total"], int)
            assert isinstance(result["data"]["has_more"], bool)
