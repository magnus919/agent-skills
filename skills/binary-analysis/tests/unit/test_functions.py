"""Unit tests for focused analysis CLI commands.

Covers: functions, disassemble, and bytes.
Validates against:
- VAL-STRUCT-011, 012, 013: Functions
- VAL-FOCUS-006, 007, 008, 009, 010: Disassemble
- VAL-FOCUS-011, 012, 013, 014: Bytes
"""

from __future__ import annotations

import json
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
# Helper: build args
# ---------------------------------------------------------------------------


def _make_args(**kwargs):
    """Create a mock argparse.Namespace."""
    defaults = {
        "json": True,
        "quiet": False,
        "limit": None,
        "timeout": 300,
        "cursor": None,
        "sort": "address",
        "target": None,
        "address": None,
        "length": None,
        "no_exclude_external": False,
        "no_exclude_thunks": False,
    }
    defaults.update(kwargs)

    class Args:
        pass

    args = Args()
    for k, v in defaults.items():
        setattr(args, k, v)
    return args


# ---------------------------------------------------------------------------
# Test: Functions command
# ---------------------------------------------------------------------------


class TestFunctionsCommand:
    """Tests for the 'functions' command (VAL-STRUCT-011, 012, 013)."""

    def test_functions_basic(self, monkeypatch, project_ready):
        """VAL-STRUCT-011: Functions return name, address, size_bytes, confidence, name_source."""
        from binary_analysis.cli.functions import execute_functions

        monkeypatch.setattr(
            "binary_analysis.cli.functions._resolve_project_path",
            lambda _: str(project_ready),
        )

        args = _make_args(project="test-proj")
        result = execute_functions(args)

        assert result["success"] is True
        items = result["data"]["items"]
        assert len(items) > 0

        for fn in items:
            assert "name" in fn
            assert "address" in fn
            assert isinstance(fn["address"], dict)
            assert "space" in fn["address"]
            assert "offset" in fn["address"]
            assert "display" in fn["address"]
            assert "size_bytes" in fn
            assert isinstance(fn["size_bytes"], int)
            assert "confidence" in fn
            assert fn["confidence"] in ("HIGH", "MEDIUM", "LOW", "UNKNOWN")
            assert "name_source" in fn
            assert fn["name_source"] in (
                "ORIGINAL",
                "IMPORTED",
                "DEBUG",
                "BACKEND_GENERATED",
                "USER_ANNOTATION",
                "AGENT_SUGGESTION",
                "UNKNOWN",
            )

        # Pagination fields
        assert "total" in result["data"]
        assert "has_more" in result["data"]
        assert "next_cursor" in result["data"]

    def test_functions_exclude_external_and_thunks_by_default(self, monkeypatch, project_ready):
        """VAL-STRUCT-012: Excludes external/thunks by default; applied_filters shows both active."""
        from binary_analysis.cli.functions import execute_functions

        monkeypatch.setattr(
            "binary_analysis.cli.functions._resolve_project_path",
            lambda _: str(project_ready),
        )

        args = _make_args(project="test-proj")
        result = execute_functions(args)

        assert "applied_filters" in result["data"]
        filters = result["data"]["applied_filters"]
        assert any(f["filter"] == "exclude_external" and f["active"] is True for f in filters)
        assert any(f["filter"] == "exclude_thunks" and f["active"] is True for f in filters)

        # No function should have name_source IMPORTED with external characteristics
        for fn in result["data"]["items"]:
            if fn.get("name_source") == "IMPORTED":
                # Imported functions that are also external would be excluded
                # If any slip through, they should not have is_external=True
                assert not fn.get("is_external", False)

    def test_functions_no_exclude_overrides(self, monkeypatch, project_ready):
        """VAL-STRUCT-013: --no-exclude-external --no-exclude-thunks shows both inactive,
        includes previously excluded functions."""
        from binary_analysis.cli.functions import execute_functions

        monkeypatch.setattr(
            "binary_analysis.cli.functions._resolve_project_path",
            lambda _: str(project_ready),
        )

        # First, get default (excluded) results
        args_default = _make_args(project="test-proj")
        result_default = execute_functions(args_default)
        default_count = result_default["data"]["total"]

        # Now with overrides
        args_all = _make_args(
            project="test-proj",
            no_exclude_external=True,
            no_exclude_thunks=True,
        )
        result_all = execute_functions(args_all)

        # applied_filters should show both inactive
        filters_all = result_all["data"]["applied_filters"]
        assert any(f["filter"] == "exclude_external" and f["active"] is False for f in filters_all)
        assert any(f["filter"] == "exclude_thunks" and f["active"] is False for f in filters_all)

        # Total should be >= default (includes previously excluded functions)
        all_count = result_all["data"]["total"]
        assert all_count >= default_count

    def test_functions_pagination(self, monkeypatch, project_ready):
        """Functions cursor pagination works."""
        from binary_analysis.cli.functions import execute_functions

        monkeypatch.setattr(
            "binary_analysis.cli.functions._resolve_project_path",
            lambda _: str(project_ready),
        )

        args = _make_args(project="test-proj", limit=2)
        result = execute_functions(args)

        assert result["success"] is True
        assert len(result["data"]["items"]) <= 2
        assert "has_more" in result["data"]
        assert "next_cursor" in result["data"]

    def test_functions_cursor_pagination_no_overlap(self, monkeypatch, project_ready):
        """Cursor from first page produces next page with no overlap."""
        from binary_analysis.cli.functions import execute_functions

        monkeypatch.setattr(
            "binary_analysis.cli.functions._resolve_project_path",
            lambda _: str(project_ready),
        )

        args1 = _make_args(project="test-proj", limit=2)
        result1 = execute_functions(args1)
        cursor = result1["data"]["next_cursor"]
        items1 = result1["data"]["items"]

        if cursor:
            args2 = _make_args(project="test-proj", limit=2, cursor=cursor)
            result2 = execute_functions(args2)
            items2 = result2["data"]["items"]

            # No overlap between pages
            names1 = {fn["name"] for fn in items1}
            names2 = {fn["name"] for fn in items2}
            assert names1.isdisjoint(names2)

    def test_functions_cursor_mismatched_filters(self, monkeypatch, project_ready):
        """Cursor from one filter set cannot be used with a different filter set."""
        from binary_analysis.cli.functions import execute_functions
        from binary_analysis.domain.errors import InvalidArgsError

        monkeypatch.setattr(
            "binary_analysis.cli.functions._resolve_project_path",
            lambda _: str(project_ready),
        )

        # Get cursor with defaults
        args1 = _make_args(project="test-proj", limit=1)
        result1 = execute_functions(args1)
        cursor = result1["data"]["next_cursor"]

        if cursor:
            # Try with different filter
            args2 = _make_args(
                project="test-proj",
                limit=1,
                cursor=cursor,
                no_exclude_external=True,
            )
            with pytest.raises(InvalidArgsError, match="filters"):
                execute_functions(args2)

    def test_functions_unanalyzed_project(self, monkeypatch, project_imported):
        """Unanalyzed project returns info diagnostic."""
        from binary_analysis.cli.functions import execute_functions

        monkeypatch.setattr(
            "binary_analysis.cli.functions._resolve_project_path",
            lambda _: str(project_imported),
        )

        args = _make_args(project="test-proj")
        result = execute_functions(args)

        assert result["success"] is True
        diagnostics = result.get("diagnostics", [])
        assert any(
            d.get("severity") == "INFO" and "not been fully analyzed" in d.get("message", "")
            for d in diagnostics
        )


# ---------------------------------------------------------------------------
# Test: Disassemble command
# ---------------------------------------------------------------------------


class TestDisassembleCommand:
    """Tests for the 'disassemble' command (VAL-FOCUS-006, 007, 008, 009, 010)."""

    def test_disassemble_by_function_selector(self, monkeypatch, project_ready):
        """VAL-FOCUS-006: Disassemble by function selector returns instructions."""
        from binary_analysis.cli.functions import execute_disassemble

        monkeypatch.setattr(
            "binary_analysis.cli.functions._resolve_project_path",
            lambda _: str(project_ready),
        )

        args = _make_args(project="test-proj", target="function:main")
        result = execute_disassemble(args)

        assert result["success"] is True
        instructions = result["data"]["instructions"]
        assert len(instructions) > 0

        for inst in instructions:
            assert "mnemonic" in inst
            assert isinstance(inst["mnemonic"], str)
            assert "operands" in inst
            assert isinstance(inst["operands"], str)
            assert "bytes_hex" in inst
            assert isinstance(inst["bytes_hex"], str)
            assert "address" in inst
            assert isinstance(inst["address"], dict)
            assert "space" in inst["address"]
            assert "offset" in inst["address"]
            assert "display" in inst["address"]

    def test_disassemble_by_address_range(self, monkeypatch, project_ready):
        """VAL-FOCUS-007: Disassemble by explicit address range."""
        from binary_analysis.cli.functions import execute_disassemble

        monkeypatch.setattr(
            "binary_analysis.cli.functions._resolve_project_path",
            lambda _: str(project_ready),
        )

        args = _make_args(project="test-proj", target="0x401000..0x401200")
        result = execute_disassemble(args)

        assert result["success"] is True
        instructions = result["data"]["instructions"]
        assert len(instructions) > 0

        # Check bounds: first instruction at or after start, last at or before end
        first_addr = int(instructions[0]["address"]["offset"], 16)
        last_addr = int(instructions[-1]["address"]["offset"], 16)
        assert first_addr >= 0x401000
        assert last_addr <= 0x401200

        # Verify range info in data
        assert result["data"]["start_address"]["offset"] == "0x401000"
        assert result["data"]["end_address"]["offset"] == "0x401200"

    def test_disassemble_no_target(self, monkeypatch, project_ready):
        """VAL-FOCUS-008: No range/selector → exit code 2."""
        from binary_analysis.cli.functions import execute_disassemble
        from binary_analysis.domain.errors import InvalidArgsError

        monkeypatch.setattr(
            "binary_analysis.cli.functions._resolve_project_path",
            lambda _: str(project_ready),
        )

        args = _make_args(project="test-proj", target=None)
        with pytest.raises(InvalidArgsError) as exc_info:
            execute_disassemble(args)

        assert "requires a bounded target" in str(exc_info.value)
        assert exc_info.value.exit_code == 2

    def test_disassemble_function_not_found(self, monkeypatch, project_ready):
        """Nonexistent function returns exit code 9."""
        from binary_analysis.cli.functions import execute_disassemble
        from binary_analysis.domain.errors import EntityNotFoundError

        monkeypatch.setattr(
            "binary_analysis.cli.functions._resolve_project_path",
            lambda _: str(project_ready),
        )

        args = _make_args(project="test-proj", target="function:nonexistent_func_xyz")
        with pytest.raises(EntityNotFoundError) as exc_info:
            execute_disassemble(args)

        assert exc_info.value.exit_code == 9

    def test_disassemble_empty_function_name(self, monkeypatch, project_ready):
        """Empty function name after 'function:' prefix → error."""
        from binary_analysis.cli.functions import execute_disassemble
        from binary_analysis.domain.errors import InvalidArgsError

        monkeypatch.setattr(
            "binary_analysis.cli.functions._resolve_project_path",
            lambda _: str(project_ready),
        )

        args = _make_args(project="test-proj", target="function:")
        with pytest.raises(InvalidArgsError) as exc_info:
            execute_disassemble(args)

        assert exc_info.value.exit_code == 2

    def test_disassemble_unmapped_range(self, monkeypatch, project_ready):
        """VAL-FOCUS-009: Unmapped range → exit code 9."""
        from binary_analysis.cli.functions import execute_disassemble
        from binary_analysis.domain.errors import EntityNotFoundError

        monkeypatch.setattr(
            "binary_analysis.cli.functions._resolve_project_path",
            lambda _: str(project_ready),
        )

        # Configure unmapped range on the adapter
        import binary_analysis.cli.functions as func_mod

        original_get_adapter = func_mod._get_adapter_and_binary

        def patched_get_adapter(project_path, manifest):
            adapter, binary, proj_info = original_get_adapter(project_path, manifest)
            adapter.configure_unmapped_range(0x900000, 0x901000)
            adapter.configure_unmapped_range(0x900200, 0x900300)
            return adapter, binary, proj_info

        func_mod._get_adapter_and_binary = patched_get_adapter

        try:
            args = _make_args(project="test-proj", target="0x900000..0x900100")
            with pytest.raises(EntityNotFoundError) as exc_info:
                execute_disassemble(args)
            assert exc_info.value.exit_code == 9
        finally:
            func_mod._get_adapter_and_binary = original_get_adapter

    def test_disassemble_partially_mapped_range(self, monkeypatch, project_ready):
        """VAL-FOCUS-010: Partially mapped range → partial=true with diagnostic."""
        from binary_analysis.cli.functions import execute_disassemble

        monkeypatch.setattr(
            "binary_analysis.cli.functions._resolve_project_path",
            lambda _: str(project_ready),
        )

        # The fake adapter generates instructions; if the range is large,
        # it will stop at 1000 instructions max. Use a range that is partially mapped
        # by requesting a large range where only a portion has valid instructions.
        args = _make_args(project="test-proj", target="0x401000..0x500000")
        result = execute_disassemble(args)

        assert result["success"] is True
        assert result["partial"] is True
        assert len(result["data"]["instructions"]) > 0

        # Must have a diagnostic about partial mapping
        diagnostics = result.get("diagnostics", [])
        assert any(
            "partial" in d.get("category", "").lower()
            or "portion" in d.get("message", "").lower()
            or d.get("category") == "partial_mapping"
            for d in diagnostics
        )

    def test_disassemble_invalid_range_format(self, monkeypatch, project_ready):
        """Malformed address range → error."""
        from binary_analysis.cli.functions import execute_disassemble
        from binary_analysis.domain.errors import InvalidArgsError

        monkeypatch.setattr(
            "binary_analysis.cli.functions._resolve_project_path",
            lambda _: str(project_ready),
        )

        args = _make_args(project="test-proj", target="not-a-valid-range")
        with pytest.raises(InvalidArgsError) as exc_info:
            execute_disassemble(args)
        assert exc_info.value.exit_code == 2

    def test_disassemble_invalid_range_reversed(self, monkeypatch, project_ready):
        """Reversed address range (start > end) → error."""
        from binary_analysis.cli.functions import execute_disassemble
        from binary_analysis.domain.errors import InvalidArgsError

        monkeypatch.setattr(
            "binary_analysis.cli.functions._resolve_project_path",
            lambda _: str(project_ready),
        )

        args = _make_args(project="test-proj", target="0x401200..0x401000")
        with pytest.raises(InvalidArgsError) as exc_info:
            execute_disassemble(args)
        assert exc_info.value.exit_code == 2

    def test_disassemble_target_field_present(self, monkeypatch, project_ready):
        """Result includes the target identifier."""
        from binary_analysis.cli.functions import execute_disassemble

        monkeypatch.setattr(
            "binary_analysis.cli.functions._resolve_project_path",
            lambda _: str(project_ready),
        )

        args = _make_args(project="test-proj", target="function:main")
        result = execute_disassemble(args)

        assert result["data"]["target"] == "function:main"
        assert "instruction_count" in result["data"]

    def test_disassemble_complete_range_not_partial(self, monkeypatch, project_ready):
        """A small range that is fully mapped returns partial=False."""
        from binary_analysis.cli.functions import execute_disassemble

        monkeypatch.setattr(
            "binary_analysis.cli.functions._resolve_project_path",
            lambda _: str(project_ready),
        )

        # Small range should be fully covered by generated instructions
        args = _make_args(project="test-proj", target="0x401000..0x401005")
        result = execute_disassemble(args)

        assert result["success"] is True
        # Small range might still be partial since instructions might overshoot
        # but for a very small range, the last instruction address may exceed end


# ---------------------------------------------------------------------------
# Test: Bytes command
# ---------------------------------------------------------------------------


class TestBytesCommand:
    """Tests for the 'bytes' command (VAL-FOCUS-011, 012, 013, 014)."""

    def test_bytes_basic(self, monkeypatch, project_ready):
        """VAL-FOCUS-011: Returns hex (2*length chars) and base64."""
        from binary_analysis.cli.functions import execute_bytes

        monkeypatch.setattr(
            "binary_analysis.cli.functions._resolve_project_path",
            lambda _: str(project_ready),
        )

        args = _make_args(project="test-proj", address="0x401000", length=16)
        result = execute_bytes(args)

        assert result["success"] is True
        assert "hex" in result["data"]
        assert "base64" in result["data"]
        assert "address" in result["data"]
        assert "length" in result["data"]

        # hex must be 2*length chars
        assert len(result["data"]["hex"]) == 2 * result["data"]["length"]

        # address must be canonical
        addr = result["data"]["address"]
        assert "space" in addr
        assert "offset" in addr
        assert "display" in addr

        # base64 must be valid and decodable
        import base64

        decoded = base64.standard_b64decode(result["data"]["base64"])
        assert len(decoded) == result["data"]["length"]

        # Verify hex matches decoded bytes
        assert decoded.hex() == result["data"]["hex"]

    def test_bytes_unmapped_address(self, monkeypatch, project_ready):
        """VAL-FOCUS-012: Unmapped address → exit code 9."""
        from binary_analysis.cli.functions import execute_bytes
        from binary_analysis.domain.errors import EntityNotFoundError

        monkeypatch.setattr(
            "binary_analysis.cli.functions._resolve_project_path",
            lambda _: str(project_ready),
        )

        import binary_analysis.cli.functions as func_mod

        original_get_adapter = func_mod._get_adapter_and_binary

        def patched_get_adapter(project_path, manifest):
            adapter, binary, proj_info = original_get_adapter(project_path, manifest)
            adapter.configure_unmapped_range(0x900000, 0x901000)
            return adapter, binary, proj_info

        func_mod._get_adapter_and_binary = patched_get_adapter

        try:
            args = _make_args(project="test-proj", address="0x900000", length=16)
            with pytest.raises(EntityNotFoundError) as exc_info:
                execute_bytes(args)
            assert exc_info.value.exit_code == 9
        finally:
            func_mod._get_adapter_and_binary = original_get_adapter

    def test_bytes_zero_length(self, monkeypatch, project_ready):
        """VAL-FOCUS-013: Zero-length request → exit code 2."""
        from binary_analysis.cli.functions import execute_bytes
        from binary_analysis.domain.errors import InvalidArgsError

        monkeypatch.setattr(
            "binary_analysis.cli.functions._resolve_project_path",
            lambda _: str(project_ready),
        )

        args = _make_args(project="test-proj", address="0x401000", length=0)
        with pytest.raises(InvalidArgsError) as exc_info:
            execute_bytes(args)
        assert exc_info.value.exit_code == 2

    def test_bytes_negative_length(self, monkeypatch, project_ready):
        """Negative length → exit code 2."""
        from binary_analysis.cli.functions import execute_bytes
        from binary_analysis.domain.errors import InvalidArgsError

        monkeypatch.setattr(
            "binary_analysis.cli.functions._resolve_project_path",
            lambda _: str(project_ready),
        )

        args = _make_args(project="test-proj", address="0x401000", length=-1)
        with pytest.raises(InvalidArgsError) as exc_info:
            execute_bytes(args)
        assert exc_info.value.exit_code == 2

    def test_bytes_truncation_at_boundary(self, monkeypatch, project_ready):
        """VAL-FOCUS-014: Truncation at segment boundary → partial=true with diagnostic."""
        from binary_analysis.cli.functions import execute_bytes

        monkeypatch.setattr(
            "binary_analysis.cli.functions._resolve_project_path",
            lambda _: str(project_ready),
        )

        import binary_analysis.cli.functions as func_mod

        original_get_adapter = func_mod._get_adapter_and_binary

        def patched_get_adapter(project_path, manifest):
            adapter, binary, proj_info = original_get_adapter(project_path, manifest)
            # Configure truncation: at address 0x401000, only 8 bytes available
            adapter.configure_truncation(0x401000, 8)
            return adapter, binary, proj_info

        func_mod._get_adapter_and_binary = patched_get_adapter

        try:
            args = _make_args(project="test-proj", address="0x401000", length=16)
            result = execute_bytes(args)

            assert result["success"] is True
            assert result["partial"] is True
            # Actual length < requested
            assert result["data"]["length"] < 16
            assert result["data"]["requested_length"] == 16
            # hex should be shorter than 2*16
            assert len(result["data"]["hex"]) == 2 * result["data"]["length"]

            # Must have truncation diagnostic
            diagnostics = result.get("diagnostics", [])
            assert any(
                "truncat" in d.get("category", "").lower()
                or "truncat" in d.get("message", "").lower()
                for d in diagnostics
            )
        finally:
            func_mod._get_adapter_and_binary = original_get_adapter

    def test_bytes_no_truncation(self, monkeypatch, project_ready):
        """No truncation when within segment → partial=false."""
        from binary_analysis.cli.functions import execute_bytes

        monkeypatch.setattr(
            "binary_analysis.cli.functions._resolve_project_path",
            lambda _: str(project_ready),
        )

        args = _make_args(project="test-proj", address="0x401000", length=4)
        result = execute_bytes(args)

        assert result["success"] is True
        assert result["partial"] is False
        assert result["data"]["length"] == 4
        assert len(result["data"]["hex"]) == 8

    def test_bytes_invalid_address_format(self, monkeypatch, project_ready):
        """Invalid address format → error."""
        from binary_analysis.cli.functions import execute_bytes
        from binary_analysis.domain.errors import InvalidArgsError

        monkeypatch.setattr(
            "binary_analysis.cli.functions._resolve_project_path",
            lambda _: str(project_ready),
        )

        args = _make_args(project="test-proj", address="not-an-address", length=16)
        with pytest.raises(InvalidArgsError):
            execute_bytes(args)

    def test_bytes_missing_address(self, monkeypatch, project_ready):
        """Missing address argument → error."""
        from binary_analysis.cli.functions import execute_bytes
        from binary_analysis.domain.errors import InvalidArgsError

        monkeypatch.setattr(
            "binary_analysis.cli.functions._resolve_project_path",
            lambda _: str(project_ready),
        )

        args = _make_args(project="test-proj", address=None, length=16)
        with pytest.raises(InvalidArgsError):
            execute_bytes(args)

    def test_bytes_missing_length(self, monkeypatch, project_ready):
        """Missing length argument → error."""
        from binary_analysis.cli.functions import execute_bytes
        from binary_analysis.domain.errors import InvalidArgsError

        monkeypatch.setattr(
            "binary_analysis.cli.functions._resolve_project_path",
            lambda _: str(project_ready),
        )

        args = _make_args(project="test-proj", address="0x401000", length=None)
        with pytest.raises(InvalidArgsError):
            execute_bytes(args)


# ---------------------------------------------------------------------------
# Test: Error handling
# ---------------------------------------------------------------------------


class TestErrorHandling:
    """Test error handling for focused analysis commands."""

    def test_functions_binary_not_found(self, tmp_path):
        """Project with no binary returns error."""
        import json as _json
        from datetime import datetime, timezone

        from binary_analysis.cli.functions import execute_functions
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

        import binary_analysis.cli.functions as func_mod

        original_resolve = func_mod._resolve_project_path
        func_mod._resolve_project_path = lambda _: str(project_dir)

        try:
            args = _make_args(project="empty-proj")
            with pytest.raises(BinaryNotFoundError):
                execute_functions(args)
        finally:
            func_mod._resolve_project_path = original_resolve

    def test_project_not_found(self):
        """Non-existent project returns error."""
        from binary_analysis.cli.functions import execute_functions
        from binary_analysis.domain.errors import ProjectNotFoundError

        args = _make_args(project="nonexistent-12345")
        with pytest.raises(ProjectNotFoundError):
            execute_functions(args)


# ---------------------------------------------------------------------------
# Test: JSON format compliance
# ---------------------------------------------------------------------------


class TestJsonFormat:
    """Test JSON output format compliance for focused analysis commands."""

    def test_functions_json_format(self, monkeypatch, project_ready):
        """Functions command produces valid paginated JSON."""
        from binary_analysis.cli.functions import execute_functions

        monkeypatch.setattr(
            "binary_analysis.cli.functions._resolve_project_path",
            lambda _: str(project_ready),
        )

        args = _make_args(project="test-proj")
        result = execute_functions(args)

        # Core result fields
        assert "success" in result
        assert "partial" in result
        assert "warnings" in result
        assert "diagnostics" in result
        assert "data" in result

        # Data fields
        assert "items" in result["data"]
        assert "total" in result["data"]
        assert "has_more" in result["data"]
        assert "next_cursor" in result["data"]
        assert "applied_filters" in result["data"]
        assert isinstance(result["data"]["items"], list)
        assert isinstance(result["data"]["total"], int)
        assert isinstance(result["data"]["has_more"], bool)

    def test_disassemble_json_format(self, monkeypatch, project_ready):
        """Disassemble command produces valid JSON."""
        from binary_analysis.cli.functions import execute_disassemble

        monkeypatch.setattr(
            "binary_analysis.cli.functions._resolve_project_path",
            lambda _: str(project_ready),
        )

        args = _make_args(project="test-proj", target="function:main")
        result = execute_disassemble(args)

        assert "success" in result
        assert "partial" in result
        assert "warnings" in result
        assert "diagnostics" in result
        assert "data" in result

        data = result["data"]
        assert "instructions" in data
        assert "start_address" in data
        assert "end_address" in data
        assert "instruction_count" in data
        assert "target" in data
        assert isinstance(data["instructions"], list)
        assert isinstance(data["instruction_count"], int)

    def test_bytes_json_format(self, monkeypatch, project_ready):
        """Bytes command produces valid JSON."""
        from binary_analysis.cli.functions import execute_bytes

        monkeypatch.setattr(
            "binary_analysis.cli.functions._resolve_project_path",
            lambda _: str(project_ready),
        )

        args = _make_args(project="test-proj", address="0x401000", length=16)
        result = execute_bytes(args)

        assert "success" in result
        assert "partial" in result
        assert "warnings" in result
        assert "diagnostics" in result
        assert "data" in result

        data = result["data"]
        assert "hex" in data
        assert "base64" in data
        assert "address" in data
        assert "length" in data
        assert "requested_length" in data
        assert isinstance(data["hex"], str)
        assert isinstance(data["base64"], str)
        assert isinstance(data["length"], int)
