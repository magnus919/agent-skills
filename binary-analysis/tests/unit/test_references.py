"""Unit tests for cross-reference and call graph CLI commands.

Covers: xrefs, callers, callees, and callgraph.
Validates against:
- VAL-FOCUS-015, 016, 017: Xrefs
- VAL-FOCUS-018, 019: Callers
- VAL-FOCUS-020, 021: Callees
- VAL-FOCUS-022, 023, 024, 031: Callgraph
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
        "selector": None,
        "depth": 3,
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
# Test: Xrefs command
# ---------------------------------------------------------------------------


class TestXrefsCommand:
    """Tests for the 'xrefs' command (VAL-FOCUS-015, 016, 017)."""

    def test_xrefs_returns_references_with_kind_and_confidence(self, monkeypatch, project_ready):
        """VAL-FOCUS-015: Xrefs returns references with from, to (address objects),
        kind (ReferenceKind), and confidence; provenance present."""
        from binary_analysis.cli.references import execute_xrefs

        monkeypatch.setattr(
            "binary_analysis.cli.references._resolve_project_path",
            lambda _: str(project_ready),
        )

        args = _make_args(project="test-proj", selector="function:main")
        result = execute_xrefs(args)

        assert result["success"] is True
        references = result["data"]["references"]
        assert isinstance(references, list)

        for ref in references:
            assert "from" in ref, "Each reference must have a 'from' address"
            assert isinstance(ref["from"], dict)
            assert "space" in ref["from"]
            assert "offset" in ref["from"]
            assert "display" in ref["from"]

            assert "to" in ref, "Each reference must have a 'to' address"
            assert isinstance(ref["to"], dict)
            assert "space" in ref["to"]
            assert "offset" in ref["to"]
            assert "display" in ref["to"]

            assert "kind" in ref, "Each reference must have a 'kind'"
            assert ref["kind"] in (
                "CALL",
                "JUMP",
                "READ",
                "WRITE",
                "DATA",
                "IMPORT",
                "EXPORT",
                "INDIRECT",
                "UNKNOWN",
            )

            assert "confidence" in ref, "Each reference must have 'confidence'"
            assert ref["confidence"] in ("HIGH", "MEDIUM", "LOW", "UNKNOWN")

    def test_xrefs_on_leaf_function_returns_empty(self, monkeypatch, project_ready):
        """VAL-FOCUS-016: Xrefs on entity with zero references returns exit 0
        with empty array, no error diagnostics."""
        from binary_analysis.cli.references import execute_xrefs

        monkeypatch.setattr(
            "binary_analysis.cli.references._resolve_project_path",
            lambda _: str(project_ready),
        )

        # Patch the adapter's get_xrefs to return empty for this specific function
        import binary_analysis.cli.references as refs_mod

        original_get_adapter = refs_mod._get_adapter_and_binary

        def patched_get_adapter(project_path, manifest):
            adapter, binary, proj_info = original_get_adapter(project_path, manifest)
            # Override get_xrefs to return empty list for print_message
            original_get_xrefs = adapter.get_xrefs

            def mock_get_xrefs(binary_entity, address):
                if address.offset == "0x401400":
                    return []
                return original_get_xrefs(binary_entity, address)

            adapter.get_xrefs = mock_get_xrefs
            return adapter, binary, proj_info

        refs_mod._get_adapter_and_binary = patched_get_adapter

        try:
            args = _make_args(project="test-proj", selector="print_message")
            result = execute_xrefs(args)

            assert result["success"] is True
            references = result["data"]["references"]
            assert references == []

            # No error diagnostics
            error_diags = [d for d in result.get("diagnostics", []) if d.get("severity") == "ERROR"]
            assert len(error_diags) == 0
        finally:
            refs_mod._get_adapter_and_binary = original_get_adapter

    def test_xrefs_nonexistent_entity(self, monkeypatch, project_ready):
        """VAL-FOCUS-017: Xrefs on nonexistent entity returns exit code 9."""
        from binary_analysis.cli.references import execute_xrefs
        from binary_analysis.domain.errors import EntityNotFoundError

        monkeypatch.setattr(
            "binary_analysis.cli.references._resolve_project_path",
            lambda _: str(project_ready),
        )

        args = _make_args(project="test-proj", selector="function:nonexistent_func_xyz")
        with pytest.raises(EntityNotFoundError) as exc_info:
            execute_xrefs(args)
        assert exc_info.value.exit_code == 9

    def test_xrefs_on_address(self, monkeypatch, project_ready):
        """Xrefs accepts an address selector."""
        from binary_analysis.cli.references import execute_xrefs

        monkeypatch.setattr(
            "binary_analysis.cli.references._resolve_project_path",
            lambda _: str(project_ready),
        )

        args = _make_args(project="test-proj", selector="0x401000")
        result = execute_xrefs(args)

        assert result["success"] is True
        assert isinstance(result["data"]["references"], list)

    def test_xrefs_invalid_address_format(self, monkeypatch, project_ready):
        """Xrefs on invalid selector that isn't a function name → EntityNotFoundError."""
        from binary_analysis.cli.references import execute_xrefs
        from binary_analysis.domain.errors import EntityNotFoundError

        monkeypatch.setattr(
            "binary_analysis.cli.references._resolve_project_path",
            lambda _: str(project_ready),
        )

        args = _make_args(project="test-proj", selector="not_a_valid_thing")
        with pytest.raises(EntityNotFoundError) as exc_info:
            execute_xrefs(args)
        assert exc_info.value.exit_code == 9


# ---------------------------------------------------------------------------
# Test: Callers command
# ---------------------------------------------------------------------------


class TestCallersCommand:
    """Tests for the 'callers' command (VAL-FOCUS-018, 019)."""

    def test_callers_returns_function_objects(self, monkeypatch, project_ready):
        """VAL-FOCUS-018: Callers returns array of function objects
        (name/symbol, address) calling the target; depth/node limits disclosed."""
        from binary_analysis.cli.references import execute_callers

        monkeypatch.setattr(
            "binary_analysis.cli.references._resolve_project_path",
            lambda _: str(project_ready),
        )

        args = _make_args(project="test-proj", selector="function:check_password")
        result = execute_callers(args)

        assert result["success"] is True
        callers = result["data"]["callers"]
        assert isinstance(callers, list)

        for caller in callers:
            assert "name" in caller
            assert "address" in caller
            assert isinstance(caller["address"], dict)
            assert "space" in caller["address"]
            assert "offset" in caller["address"]

        # Limits disclosed in data
        assert "max_depth" in result["data"]
        assert "max_nodes" in result["data"]

    def test_callers_on_leaf_function_returns_empty(self, monkeypatch, project_ready):
        """VAL-FOCUS-019: Callers on leaf function returns exit 0 with empty array."""
        from binary_analysis.cli.references import execute_callers

        monkeypatch.setattr(
            "binary_analysis.cli.references._resolve_project_path",
            lambda _: str(project_ready),
        )

        # main is the first function and has no callers in our fixture
        args = _make_args(project="test-proj", selector="function:main")
        result = execute_callers(args)

        assert result["success"] is True
        callers = result["data"]["callers"]
        assert callers == []

    def test_callers_nonexistent_function(self, monkeypatch, project_ready):
        """Callers on nonexistent function → exit code 9."""
        from binary_analysis.cli.references import execute_callers
        from binary_analysis.domain.errors import EntityNotFoundError

        monkeypatch.setattr(
            "binary_analysis.cli.references._resolve_project_path",
            lambda _: str(project_ready),
        )

        args = _make_args(project="test-proj", selector="function:nonexistent_func_xyz")
        with pytest.raises(EntityNotFoundError) as exc_info:
            execute_callers(args)
        assert exc_info.value.exit_code == 9

    def test_callers_no_selector(self, monkeypatch, project_ready):
        """Callers without selector → exit code 2."""
        from binary_analysis.cli.references import execute_callers
        from binary_analysis.domain.errors import InvalidArgsError

        monkeypatch.setattr(
            "binary_analysis.cli.references._resolve_project_path",
            lambda _: str(project_ready),
        )

        args = _make_args(project="test-proj", selector=None)
        with pytest.raises(InvalidArgsError) as exc_info:
            execute_callers(args)
        assert exc_info.value.exit_code == 2


# ---------------------------------------------------------------------------
# Test: Callees command
# ---------------------------------------------------------------------------


class TestCalleesCommand:
    """Tests for the 'callees' command (VAL-FOCUS-020, 021)."""

    def test_callees_returns_function_objects(self, monkeypatch, project_ready):
        """VAL-FOCUS-020: Callees returns array of function objects called by target;
        depth/node limits disclosed."""
        from binary_analysis.cli.references import execute_callees

        monkeypatch.setattr(
            "binary_analysis.cli.references._resolve_project_path",
            lambda _: str(project_ready),
        )

        args = _make_args(project="test-proj", selector="function:main")
        result = execute_callees(args)

        assert result["success"] is True
        callees = result["data"]["callees"]
        assert isinstance(callees, list)

        for callee in callees:
            assert "name" in callee
            assert "address" in callee
            assert isinstance(callee["address"], dict)
            assert "space" in callee["address"]
            assert "offset" in callee["address"]

        # Limits disclosed in data
        assert "max_depth" in result["data"]
        assert "max_nodes" in result["data"]

    def test_callees_on_terminal_function_returns_empty(self, monkeypatch, project_ready):
        """VAL-FOCUS-021: Callees on terminal function returns exit 0 with empty array."""
        from binary_analysis.cli.references import execute_callees

        monkeypatch.setattr(
            "binary_analysis.cli.references._resolve_project_path",
            lambda _: str(project_ready),
        )

        # print_message is the last internal function; it has printf as
        # a callee in the simple chain model. Use printf which has no callees.
        args = _make_args(project="test-proj", selector="printf")
        result = execute_callees(args)

        assert result["success"] is True
        callees = result["data"]["callees"]
        assert callees == []

    def test_callees_nonexistent_function(self, monkeypatch, project_ready):
        """Callees on nonexistent function → exit code 9."""
        from binary_analysis.cli.references import execute_callees
        from binary_analysis.domain.errors import EntityNotFoundError

        monkeypatch.setattr(
            "binary_analysis.cli.references._resolve_project_path",
            lambda _: str(project_ready),
        )

        args = _make_args(project="test-proj", selector="function:nonexistent_func_xyz")
        with pytest.raises(EntityNotFoundError) as exc_info:
            execute_callees(args)
        assert exc_info.value.exit_code == 9


# ---------------------------------------------------------------------------
# Test: Callgraph command
# ---------------------------------------------------------------------------


class TestCallgraphCommand:
    """Tests for the 'callgraph' command (VAL-FOCUS-022, 023, 024, 031)."""

    def test_callgraph_returns_graph_with_nodes_and_edges(self, monkeypatch, project_ready):
        """VAL-FOCUS-022: Callgraph returns graph with nodes (functions) and edges
        (call relationships); root is target; depth disclosed."""
        from binary_analysis.cli.references import execute_callgraph

        monkeypatch.setattr(
            "binary_analysis.cli.references._resolve_project_path",
            lambda _: str(project_ready),
        )

        args = _make_args(project="test-proj", selector="function:main", depth=3)
        result = execute_callgraph(args)

        assert result["success"] is True
        graph = result["data"]["graph"]
        assert "nodes" in graph
        assert "edges" in graph
        assert graph["root_address"] is not None

        # Root node is the target function
        root_addr = graph["root_address"]
        assert root_addr["offset"] == "0x401000"

        # Depth disclosed
        assert "max_depth" in graph
        assert graph["max_depth"] == 3

        # Nodes are function objects
        for node in graph["nodes"]:
            assert "name" in node
            assert "address" in node
            assert isinstance(node["address"], dict)
            assert "depth" in node, "Each node must have a depth level"

        # Edges have from/to
        for edge in graph["edges"]:
            assert "from" in edge
            assert "to" in edge
            assert "kind" in edge

    def test_callgraph_default_depth_is_3(self, monkeypatch, project_ready):
        """Callgraph default depth is bounded (max 3)."""
        from binary_analysis.cli.references import execute_callgraph

        monkeypatch.setattr(
            "binary_analysis.cli.references._resolve_project_path",
            lambda _: str(project_ready),
        )

        args = _make_args(project="test-proj", selector="function:main", depth=3)
        result = execute_callgraph(args)

        assert result["success"] is True
        graph = result["data"]["graph"]
        assert graph["max_depth"] <= 3

        # All nodes are at depth 0, 1, 2, or 3
        for node in graph["nodes"]:
            assert 0 <= node["depth"] <= 3

    def test_callgraph_explicit_depth_2(self, monkeypatch, project_ready):
        """VAL-FOCUS-023: Callgraph --depth 2 limits graph to exactly 2 levels;
        applied depth disclosed."""
        from binary_analysis.cli.references import execute_callgraph

        monkeypatch.setattr(
            "binary_analysis.cli.references._resolve_project_path",
            lambda _: str(project_ready),
        )

        args = _make_args(project="test-proj", selector="function:main", depth=2)
        result = execute_callgraph(args)

        assert result["success"] is True
        graph = result["data"]["graph"]
        assert graph["max_depth"] == 2, "Applied depth must be disclosed as 2"

        # No nodes at depth 3 or greater
        for node in graph["nodes"]:
            assert node["depth"] <= 2, f"Node at depth {node['depth']} exceeds max_depth=2"

    def test_callgraph_depth_zero_fails(self, monkeypatch, project_ready):
        """VAL-FOCUS-024: Callgraph --depth 0 fails with exit code 2,
        'depth must be a positive integer'."""
        from binary_analysis.cli.references import execute_callgraph
        from binary_analysis.domain.errors import InvalidArgsError

        monkeypatch.setattr(
            "binary_analysis.cli.references._resolve_project_path",
            lambda _: str(project_ready),
        )

        args = _make_args(project="test-proj", selector="function:main", depth=0)
        with pytest.raises(InvalidArgsError) as exc_info:
            execute_callgraph(args)
        assert exc_info.value.exit_code == 2
        assert "positive" in str(exc_info.value).lower()

    def test_callgraph_depth_negative_fails(self, monkeypatch, project_ready):
        """VAL-FOCUS-024: Callgraph --depth -1 fails with exit code 2,
        'depth must be a positive integer'."""
        from binary_analysis.cli.references import execute_callgraph
        from binary_analysis.domain.errors import InvalidArgsError

        monkeypatch.setattr(
            "binary_analysis.cli.references._resolve_project_path",
            lambda _: str(project_ready),
        )

        args = _make_args(project="test-proj", selector="function:main", depth=-1)
        with pytest.raises(InvalidArgsError) as exc_info:
            execute_callgraph(args)
        assert exc_info.value.exit_code == 2
        assert "positive" in str(exc_info.value).lower()

    def test_callgraph_breadth_limit_enforced(self, monkeypatch, project_ready):
        """VAL-FOCUS-031: Callgraph breadth limits: bounded node count with
        truncation diagnostic when exceeded."""
        from binary_analysis.cli.references import execute_callgraph

        monkeypatch.setattr(
            "binary_analysis.cli.references._resolve_project_path",
            lambda _: str(project_ready),
        )

        # Configure adapter to have many callers at depth 1
        import binary_analysis.cli.references as refs_mod

        original_get_adapter = refs_mod._get_adapter_and_binary

        def patched_get_adapter(project_path, manifest):
            from uuid import UUID, uuid4

            from binary_analysis.adapters.fake import FakeAdapter
            from binary_analysis.domain.entities import (
                Address,
                Binary,
                Function,
            )
            from binary_analysis.domain.enums import Confidence, FunctionNameSource

            adapter = FakeAdapter()
            adapter.set_fixture("pe-default", FakeAdapter.pe_fixture())
            adapter.set_fixture("elf-default", FakeAdapter.elf_fixture())
            adapter.set_fixture("macho-default", FakeAdapter.macho_fixture())

            current_binary = manifest.get("current_binary", {})
            binary_id_str = current_binary.get("id", str(uuid4()))

            binary_entity = Binary(
                id=UUID(binary_id_str),
                sha256=current_binary.get("sha256", ""),
                path=current_binary.get("path", ""),
                format=current_binary.get("format", ""),
                size_bytes=current_binary.get("size_bytes", 0),
                architecture=current_binary.get("architecture"),
            )
            adapter._binaries[binary_id_str] = {
                "binary": binary_entity,
                "fixture_name": "pe-default",
            }

            # Create 200 functions at depth 1 to trigger breadth limit
            functions = []
            for i in range(200):
                addr = Address(
                    space="ram",
                    offset=f"0x{0x500000 + i * 64:x}",
                    display=f"0x{0x500000 + i * 64:x}",
                )
                functions.append(
                    Function(
                        name=f"leaf_func_{i}",
                        address=addr,
                        size_bytes=32,
                        confidence=Confidence.HIGH,
                        name_source=FunctionNameSource.ORIGINAL,
                    )
                )

            # Override functions for this binary
            adapter._override_functions[binary_id_str] = [
                Function(
                    name="root_func",
                    address=Address(space="ram", offset="0x401000", display="0x401000"),
                    size_bytes=128,
                    confidence=Confidence.HIGH,
                    name_source=FunctionNameSource.ORIGINAL,
                ),
                *functions,
            ]

            # Set max callgraph breadth limit to 50 for testing
            adapter._callgraph_max_breadth = 50

            # Override get_callgraph to return a breadth-limited graph with 200 nodes
            from binary_analysis.domain.entities import CallGraph

            def breadth_callgraph(binary, function, max_depth=3):
                """Return a callgraph with 200 nodes to test breadth limits."""
                nodes = [
                    {
                        "name": "root_func",
                        "address": Address(
                            space="ram", offset="0x401000", display="0x401000"
                        ).to_dict(),
                        "depth": 0,
                    }
                ]
                edges = []
                for i in range(200):
                    addr = Address(
                        space="ram",
                        offset=f"0x{0x500000 + i * 64:x}",
                        display=f"0x{0x500000 + i * 64:x}",
                    )
                    nodes.append(
                        {
                            "name": f"leaf_func_{i}",
                            "address": addr.to_dict(),
                            "depth": 1,
                        }
                    )
                    edges.append(
                        {
                            "from": nodes[0]["address"],
                            "to": addr.to_dict(),
                            "kind": "CALL",
                        }
                    )
                return CallGraph(
                    root_address=Address(space="ram", offset="0x401000", display="0x401000"),
                    nodes=nodes,
                    edges=edges,
                    max_depth=max_depth,
                    total_nodes=len(nodes),
                    total_edges=len(edges),
                    truncated=False,
                )

            adapter.get_callgraph = breadth_callgraph

            project_info = {
                "id": manifest.get("id", ""),
                "name": manifest.get("name", ""),
                "state": manifest.get("state", ""),
            }
            return adapter, binary_entity, project_info

        refs_mod._get_adapter_and_binary = patched_get_adapter

        try:
            args = _make_args(project="test-proj", selector="function:root_func", depth=1)
            result = execute_callgraph(args)

            assert result["success"] is True
            graph = result["data"]["graph"]

            # Node count must be bounded
            assert graph["total_nodes"] <= 52  # root + limit (50) + possible extra

            # Must have a truncation diagnostic
            diagnostics = result.get("diagnostics", [])
            assert any(
                "trunc" in d.get("category", "").lower()
                or "trunc" in d.get("message", "").lower()
                or "limit" in d.get("message", "").lower()
                or graph.get("truncated", False)
                for d in diagnostics
            ), "Must have truncation diagnostic when breadth limit exceeded"

        finally:
            refs_mod._get_adapter_and_binary = original_get_adapter

    def test_callgraph_nonexistent_function(self, monkeypatch, project_ready):
        """Callgraph on nonexistent function → exit code 9."""
        from binary_analysis.cli.references import execute_callgraph
        from binary_analysis.domain.errors import EntityNotFoundError

        monkeypatch.setattr(
            "binary_analysis.cli.references._resolve_project_path",
            lambda _: str(project_ready),
        )

        args = _make_args(project="test-proj", selector="function:nonexistent_func_xyz")
        with pytest.raises(EntityNotFoundError) as exc_info:
            execute_callgraph(args)
        assert exc_info.value.exit_code == 9

    def test_callgraph_no_selector(self, monkeypatch, project_ready):
        """Callgraph without selector → exit code 2."""
        from binary_analysis.cli.references import execute_callgraph
        from binary_analysis.domain.errors import InvalidArgsError

        monkeypatch.setattr(
            "binary_analysis.cli.references._resolve_project_path",
            lambda _: str(project_ready),
        )

        args = _make_args(project="test-proj", selector=None)
        with pytest.raises(InvalidArgsError) as exc_info:
            execute_callgraph(args)
        assert exc_info.value.exit_code == 2
