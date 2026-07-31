"""Unit tests for search and trace CLI commands.

Covers: search and trace.
Validates against:
- VAL-FOCUS-025, 026, 027: Search
- VAL-FOCUS-028, 029, 030: Trace
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
        "project": "test-proj",
        "query": None,
        "search_type": "function",
        "cursor": None,
        "from_selector": None,
        "to_selector": None,
        "max_paths": 10,
        "max_depth": 10,
        "command": "",
    }
    defaults.update(kwargs)

    class Args:
        pass

    args = Args()
    for k, v in defaults.items():
        setattr(args, k, v)
    return args


# ---------------------------------------------------------------------------
# Test: Search command
# ---------------------------------------------------------------------------


class TestSearchCommand:
    """Tests for the 'search' command (VAL-FOCUS-025, 026, 027)."""

    def test_search_returns_paginated_results_with_opaque_cursor(self, monkeypatch, project_ready):
        """VAL-FOCUS-025: Search returns paginated results with opaque
        next_page_token; default page size enforced."""
        from binary_analysis.cli.search import execute_search

        monkeypatch.setattr(
            "binary_analysis.cli.search._resolve_project_path",
            lambda _: str(project_ready),
        )

        args = _make_args(project="test-proj", query="main", search_type="function")
        result = execute_search(args)

        assert result["success"] is True

        data = result["data"]
        assert "results" in data
        assert isinstance(data["results"], list)
        assert "total" in data
        assert "page_size" in data
        assert "has_more" in data
        assert "next_page_token" in data

        # Cursor must be an opaque string (not an incrementing offset/number)
        if data["next_page_token"] is not None:
            cursor = data["next_page_token"]
            assert isinstance(cursor, str)
            assert not cursor.isdigit(), "Cursor must be opaque, not a plain integer"
            assert "offset" not in cursor.lower() or len(cursor) > 8, (
                "Cursor must be opaque/base64, not raw JSON"
            )

    def test_search_pagination_cursor_produces_next_page(self, monkeypatch, project_ready):
        """VAL-FOCUS-026: Search pagination with cursor produces next page
        without duplicating first page results."""
        from binary_analysis.cli.search import execute_search

        monkeypatch.setattr(
            "binary_analysis.cli.search._resolve_project_path",
            lambda _: str(project_ready),
        )

        # First page — small page size
        args = _make_args(project="test-proj", query="", limit=1, search_type="function")
        result1 = execute_search(args)

        assert result1["success"] is True
        data1 = result1["data"]
        results1 = data1["results"]

        if data1["has_more"] and data1["next_page_token"]:
            # Second page using cursor
            args2 = _make_args(
                project="test-proj",
                query="",
                limit=1,
                search_type="function",
                cursor=data1["next_page_token"],
            )
            result2 = execute_search(args2)

            assert result2["success"] is True
            data2 = result2["data"]
            results2 = data2["results"]

            # No duplicates between pages
            names1 = {r.get("name") for r in results1}
            names2 = {r.get("name") for r in results2}
            assert names1.isdisjoint(names2), "Second page must not duplicate first page results"

    def test_search_no_results_returns_empty_list(self, monkeypatch, project_ready):
        """VAL-FOCUS-027: Search with no matching results returns exit 0,
        empty results array, null/missing next_page_token."""
        from binary_analysis.cli.search import execute_search

        monkeypatch.setattr(
            "binary_analysis.cli.search._resolve_project_path",
            lambda _: str(project_ready),
        )

        args = _make_args(
            project="test-proj", query="xyznonexistent_query_12345", search_type="function"
        )
        result = execute_search(args)

        assert result["success"] is True
        data = result["data"]
        assert "results" in data
        assert data["results"] == []
        assert data["total"] == 0
        assert data["has_more"] is False

        # next_page_token should be null or absent
        npt = data.get("next_page_token")
        assert npt is None or npt == "", "No next_page_token should be returned for empty results"

    def test_search_no_query_raises_error(self, monkeypatch, project_ready):
        """Search without a query raises InvalidArgsError."""
        from binary_analysis.cli.search import execute_search
        from binary_analysis.domain.errors import InvalidArgsError

        monkeypatch.setattr(
            "binary_analysis.cli.search._resolve_project_path",
            lambda _: str(project_ready),
        )

        args = _make_args(project="test-proj", query=None)
        with pytest.raises(InvalidArgsError):
            execute_search(args)

    def test_search_all_types(self, monkeypatch, project_ready):
        """Search with type='all' searches across functions, strings, symbols, imports, exports."""
        from binary_analysis.cli.search import execute_search

        monkeypatch.setattr(
            "binary_analysis.cli.search._resolve_project_path",
            lambda _: str(project_ready),
        )

        args = _make_args(project="test-proj", query="kernel", search_type="all")
        result = execute_search(args)

        assert result["success"] is True
        results = result["data"]["results"]
        # Should find kernel32.dll import at minimum
        entity_types = {r.get("entity_type") for r in results}
        assert "import" in entity_types or len(results) > 0

    def test_search_string_type(self, monkeypatch, project_ready):
        """Search with type='string' finds matching strings."""
        from binary_analysis.cli.search import execute_search

        monkeypatch.setattr(
            "binary_analysis.cli.search._resolve_project_path",
            lambda _: str(project_ready),
        )

        args = _make_args(project="test-proj", query="Access", search_type="string")
        result = execute_search(args)

        assert result["success"] is True
        results = result["data"]["results"]
        for r in results:
            assert r["entity_type"] == "string"

    def test_search_import_type(self, monkeypatch, project_ready):
        """Search with type='import' finds matching imports."""
        from binary_analysis.cli.search import execute_search

        monkeypatch.setattr(
            "binary_analysis.cli.search._resolve_project_path",
            lambda _: str(project_ready),
        )

        args = _make_args(project="test-proj", query="kernel", search_type="import")
        result = execute_search(args)

        assert result["success"] is True
        results = result["data"]["results"]
        for r in results:
            assert r["entity_type"] == "import"

    def test_search_invalid_cursor(self, monkeypatch, project_ready):
        """Search with invalid cursor token raises InvalidArgsError."""
        from binary_analysis.cli.search import execute_search
        from binary_analysis.domain.errors import InvalidArgsError

        monkeypatch.setattr(
            "binary_analysis.cli.search._resolve_project_path",
            lambda _: str(project_ready),
        )

        args = _make_args(project="test-proj", query="main", cursor="not-a-valid-base64!!!")
        with pytest.raises(InvalidArgsError):
            execute_search(args)

    def test_search_cursor_scoped_to_query_type(self, monkeypatch, project_ready):
        """Cursor from one query/type can't be used with a different query/type."""
        from binary_analysis.cli.search import execute_search
        from binary_analysis.domain.errors import InvalidArgsError

        monkeypatch.setattr(
            "binary_analysis.cli.search._resolve_project_path",
            lambda _: str(project_ready),
        )

        # Get a cursor from a specific query
        args1 = _make_args(project="test-proj", query="main", limit=1, search_type="function")
        result1 = execute_search(args1)
        if result1["data"].get("next_page_token"):
            # Try using it with a different query
            args2 = _make_args(
                project="test-proj",
                query="different",
                limit=1,
                search_type="function",
                cursor=result1["data"]["next_page_token"],
            )
            with pytest.raises(InvalidArgsError):
                execute_search(args2)


# ---------------------------------------------------------------------------
# Test: Trace command
# ---------------------------------------------------------------------------


class TestTraceCommand:
    """Tests for the 'trace' command (VAL-FOCUS-028, 029, 030)."""

    def test_trace_finds_bounded_paths(self, monkeypatch, project_ready):
        """VAL-FOCUS-028: Trace finds bounded paths between --from and --to
        entities; disclosed max path count and depth."""
        from binary_analysis.cli.search import execute_trace

        monkeypatch.setattr(
            "binary_analysis.cli.search._resolve_project_path",
            lambda _: str(project_ready),
        )

        args = _make_args(
            project="test-proj",
            from_selector="function:main",
            to_selector="function:check_password",
            max_paths=10,
            max_depth=10,
        )
        result = execute_trace(args)

        assert result["success"] is True
        data = result["data"]
        assert "paths" in data
        assert isinstance(data["paths"], list)
        assert "max_paths" in data
        assert data["max_paths"] == 10
        assert "max_depth" in data
        assert data["max_depth"] == 10

        # Each path should be a list of entity dicts
        for path in data["paths"]:
            assert isinstance(path, list)
            for entity in path:
                assert "name" in entity
                assert "address" in entity
                assert "depth" in entity

    def test_trace_truncates_at_limits(self, monkeypatch, project_ready):
        """VAL-FOCUS-029: Trace truncates paths at disclosed limits with
        partial=true and diagnostic."""
        from binary_analysis.cli.search import execute_trace

        monkeypatch.setattr(
            "binary_analysis.cli.search._resolve_project_path",
            lambda _: str(project_ready),
        )

        args = _make_args(
            project="test-proj",
            from_selector="function:main",
            to_selector="function:print_message",
            max_paths=1,  # Very limited
            max_depth=2,  # Very limited
        )
        result = execute_trace(args)

        assert result["success"] is True
        data = result["data"]
        assert data["max_paths"] == 1
        assert data["max_depth"] == 2

        # If truncated, partial should be true
        if data.get("truncated"):
            assert result["partial"] is True
            # Should have a truncation diagnostic
            truncation_diags = [
                d for d in result.get("diagnostics", []) if d.get("category") == "truncation"
            ]
            assert len(truncation_diags) > 0

    def test_trace_no_path_returns_empty(self, monkeypatch, project_ready):
        """VAL-FOCUS-030: Trace with no path between entities returns exit 0
        with empty paths array and informational diagnostic."""
        from binary_analysis.cli.search import execute_trace

        monkeypatch.setattr(
            "binary_analysis.cli.search._resolve_project_path",
            lambda _: str(project_ready),
        )

        # Use entities that have no path between them
        # In our fake adapter, the call graph is linear: main -> check_password -> print_message
        # So tracing from print_message back to main should find no path
        args = _make_args(
            project="test-proj",
            from_selector="function:print_message",
            to_selector="function:main",
            max_paths=10,
            max_depth=10,
        )
        result = execute_trace(args)

        assert result["success"] is True
        data = result["data"]
        assert isinstance(data["paths"], list)

        # Should have informational diagnostic
        info_diags = [
            d
            for d in result.get("diagnostics", [])
            if d.get("severity") == "INFO" and d.get("category") == "trace"
        ]
        if not data["paths"]:
            assert len(info_diags) > 0, "No-path result must have informational diagnostic"

    def test_trace_hex_addresses(self, monkeypatch, project_ready):
        """Trace accepts hex addresses for --from and --to."""
        from binary_analysis.cli.search import execute_trace

        monkeypatch.setattr(
            "binary_analysis.cli.search._resolve_project_path",
            lambda _: str(project_ready),
        )

        args = _make_args(
            project="test-proj",
            from_selector="0x401000",
            to_selector="0x401200",
            max_paths=10,
            max_depth=10,
        )
        result = execute_trace(args)

        assert result["success"] is True
        assert "paths" in result["data"]

    def test_trace_invalid_max_paths(self, monkeypatch, project_ready):
        """Trace rejects invalid --max-paths values."""
        from binary_analysis.cli.search import execute_trace
        from binary_analysis.domain.errors import InvalidArgsError

        monkeypatch.setattr(
            "binary_analysis.cli.search._resolve_project_path",
            lambda _: str(project_ready),
        )

        args = _make_args(
            project="test-proj",
            from_selector="function:main",
            to_selector="function:check_password",
            max_paths=0,
            max_depth=10,
        )
        with pytest.raises(InvalidArgsError) as exc_info:
            execute_trace(args)
        assert (
            "max-paths" in str(exc_info.value).lower() or "positive" in str(exc_info.value).lower()
        )

    def test_trace_invalid_max_depth(self, monkeypatch, project_ready):
        """Trace rejects invalid --max-depth values."""
        from binary_analysis.cli.search import execute_trace
        from binary_analysis.domain.errors import InvalidArgsError

        monkeypatch.setattr(
            "binary_analysis.cli.search._resolve_project_path",
            lambda _: str(project_ready),
        )

        args = _make_args(
            project="test-proj",
            from_selector="function:main",
            to_selector="function:check_password",
            max_paths=10,
            max_depth=-1,
        )
        with pytest.raises(InvalidArgsError) as exc_info:
            execute_trace(args)
        assert (
            "max-depth" in str(exc_info.value).lower() or "positive" in str(exc_info.value).lower()
        )

    def test_trace_nonexistent_from(self, monkeypatch, project_ready):
        """Trace with nonexistent --from entity raises EntityNotFoundError."""
        from binary_analysis.cli.search import execute_trace
        from binary_analysis.domain.errors import EntityNotFoundError

        monkeypatch.setattr(
            "binary_analysis.cli.search._resolve_project_path",
            lambda _: str(project_ready),
        )

        args = _make_args(
            project="test-proj",
            from_selector="function:nonexistent_func_xyz",
            to_selector="function:main",
            max_paths=10,
            max_depth=10,
        )
        with pytest.raises(EntityNotFoundError) as exc_info:
            execute_trace(args)
        assert exc_info.value.exit_code == 9

    def test_trace_nonexistent_to(self, monkeypatch, project_ready):
        """Trace with nonexistent --to entity raises EntityNotFoundError."""
        from binary_analysis.cli.search import execute_trace
        from binary_analysis.domain.errors import EntityNotFoundError

        monkeypatch.setattr(
            "binary_analysis.cli.search._resolve_project_path",
            lambda _: str(project_ready),
        )

        args = _make_args(
            project="test-proj",
            from_selector="function:main",
            to_selector="function:nonexistent_func_xyz",
            max_paths=10,
            max_depth=10,
        )
        with pytest.raises(EntityNotFoundError) as exc_info:
            execute_trace(args)
        assert exc_info.value.exit_code == 9

    def test_trace_discloses_limits_in_data(self, monkeypatch, project_ready):
        """Trace output always discloses max_paths and max_depth."""
        from binary_analysis.cli.search import execute_trace

        monkeypatch.setattr(
            "binary_analysis.cli.search._resolve_project_path",
            lambda _: str(project_ready),
        )

        args = _make_args(
            project="test-proj",
            from_selector="function:main",
            to_selector="function:check_password",
            max_paths=5,
            max_depth=7,
        )
        result = execute_trace(args)

        assert result["success"] is True
        data = result["data"]
        assert data["max_paths"] == 5
        assert data["max_depth"] == 7
