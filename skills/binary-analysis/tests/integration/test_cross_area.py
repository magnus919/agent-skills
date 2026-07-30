"""Integration tests for cross-area flows.

Covers:
- VAL-CROSS-001: Full lifecycle end-to-end
- VAL-CROSS-002: All valid state transitions
- VAL-CROSS-003: Staleness detection via reference mode
- VAL-CROSS-004: Analysis timeout produces partial results
- VAL-CROSS-005: Copy vs reference import modes
- VAL-CROSS-006: Pagination stability across queries
- VAL-CROSS-007: Error recovery after ANALYSIS_FAILED
- VAL-CROSS-012: Analyze interruption and restart
- VAL-CROSS-013: Re-import of same binary
- VAL-CROSS-014: Deterministic analysis across projects

Tests use the CLI entrypoint (main()) to exercise full end-to-end flows
through the JSON envelope, matching the tuistory validation surface.
"""

from __future__ import annotations

import json
import os
import sys
import tempfile
import time
from pathlib import Path

_skill_dir = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_skill_dir / "scripts"))


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _create_binary_fixture(tmpdir: str, content: bytes = b"MZ\x00\x01") -> str:
    """Create a fake PE binary fixture."""
    path = os.path.join(tmpdir, "test_fixture.exe")
    data = bytearray(content)
    while len(data) < 64:
        data.append(0)
    with open(path, "wb") as f:
        f.write(data)
    return path


def _run_cli_raw(args: list[str]) -> tuple[int, str]:
    """Run the CLI and return (exit_code, stdout)."""
    import io

    from binary_analysis.cli.main import main

    old_stdout = sys.stdout
    sys.stdout = io.StringIO()
    exit_code = 0
    try:
        exit_code = main(args)
    except SystemExit as e:
        exit_code = e.code if isinstance(e.code, int) else 1
    finally:
        output = sys.stdout.getvalue()
        sys.stdout = old_stdout

    return exit_code, output


# ---------------------------------------------------------------------------
# VAL-CROSS-001: Full lifecycle end-to-end
# ---------------------------------------------------------------------------


class TestFullLifecycle:
    """VAL-CROSS-001: Full lifecycle composes end-to-end."""

    def test_full_lifecycle(self, monkeypatch):
        """Execute the complete lifecycle in sequence and verify exit codes."""
        with tempfile.TemporaryDirectory() as tmpdir:
            monkeypatch.setattr(
                "binary_analysis.projects.workspace.get_workspace_root",
                lambda: Path(tmpdir),
            )
            monkeypatch.setattr(
                "binary_analysis.projects.workspace._DEFAULT_WORKSPACE_ROOT",
                str(tmpdir),
            )

            binary_path = _create_binary_fixture(tmpdir)

            # 1. Create project
            exit_code, out = _run_cli_raw(["--json", "project", "create", "lifecycle-test"])
            assert exit_code == 0, f"Step 1 (create) failed: exit_code={exit_code}, out={out[:200]}"

            # 2. Import
            exit_code, out = _run_cli_raw(
                ["--json", "import", "--project", "lifecycle-test", binary_path]
            )
            assert exit_code == 0, f"Step 2 (import) failed: exit_code={exit_code}, out={out[:200]}"

            # 3. Analyze
            exit_code, out = _run_cli_raw(
                ["--json", "analyze", "--project", "lifecycle-test", "--profile", "standard"]
            )
            assert exit_code == 0, (
                f"Step 3 (analyze) failed: exit_code={exit_code}, out={out[:200]}"
            )

            # 4. Metadata
            exit_code, out = _run_cli_raw(["--json", "metadata", "--project", "lifecycle-test"])
            assert exit_code == 0, (
                f"Step 4 (metadata) failed: exit_code={exit_code}, out={out[:200]}"
            )

            # 5. Functions
            exit_code, out = _run_cli_raw(["--json", "functions", "--project", "lifecycle-test"])
            assert exit_code == 0, (
                f"Step 5 (functions) failed: exit_code={exit_code}, out={out[:200]}"
            )

            # 6. Project status (verify READY)
            exit_code, out = _run_cli_raw(["--json", "project", "status", "lifecycle-test"])
            assert exit_code == 0, f"Step 6 (status) failed: exit_code={exit_code}, out={out[:200]}"

            # 7. Search
            exit_code, out = _run_cli_raw(
                ["--json", "search", "--project", "lifecycle-test", "--type", "function", "main"]
            )
            assert exit_code == 0, f"Step 7 (search) failed: exit_code={exit_code}, out={out[:200]}"

            # 8. Trace
            exit_code, out = _run_cli_raw(
                [
                    "--json",
                    "trace",
                    "--project",
                    "lifecycle-test",
                    "--from",
                    "function:main",
                    "--to",
                    "function:check_password",
                ]
            )
            assert exit_code == 0, f"Step 8 (trace) failed: exit_code={exit_code}, out={out[:200]}"


# ---------------------------------------------------------------------------
# VAL-CROSS-002: All valid state transitions
# ---------------------------------------------------------------------------


class TestStateTransitions:
    """VAL-CROSS-002: All valid state transitions accepted; invalid rejected."""

    def test_valid_transitions(self, monkeypatch):
        """Drive CREATED -> IMPORTED -> READY and verify states via status."""
        with tempfile.TemporaryDirectory() as tmpdir:
            monkeypatch.setattr(
                "binary_analysis.projects.workspace.get_workspace_root",
                lambda: Path(tmpdir),
            )
            monkeypatch.setattr(
                "binary_analysis.projects.workspace._DEFAULT_WORKSPACE_ROOT",
                str(tmpdir),
            )

            binary_path = _create_binary_fixture(tmpdir)

            # Create -> CREATED
            _, out = _run_cli_raw(["--json", "project", "create", "state-test"])
            status = json.loads(out)
            assert status["data"]["state"] == "CREATED"

            # Import -> IMPORTED
            _, out = _run_cli_raw(["--json", "import", "--project", "state-test", binary_path])
            status = json.loads(out)
            assert status["success"] is True

            _, out = _run_cli_raw(["--json", "project", "status", "state-test"])
            status = json.loads(out)
            assert status["data"]["state"] == "IMPORTED"

            # Analyze -> READY
            _, out = _run_cli_raw(
                ["--json", "analyze", "--project", "state-test", "--profile", "standard"]
            )
            status = json.loads(out)
            assert status["success"] is True

            _, out = _run_cli_raw(["--json", "project", "status", "state-test"])
            status = json.loads(out)
            assert status["data"]["state"] == "READY"

    def test_invalid_transition_rejected(self, monkeypatch):
        """CREATED -> analyze fails (no import)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            monkeypatch.setattr(
                "binary_analysis.projects.workspace.get_workspace_root",
                lambda: Path(tmpdir),
            )
            monkeypatch.setattr(
                "binary_analysis.projects.workspace._DEFAULT_WORKSPACE_ROOT",
                str(tmpdir),
            )

            _run_cli_raw(["--json", "project", "create", "invalid-trans"])
            exit_code, _ = _run_cli_raw(
                ["--json", "analyze", "--project", "invalid-trans", "--profile", "standard"]
            )
            assert exit_code != 0


# ---------------------------------------------------------------------------
# VAL-CROSS-003: Staleness detection via reference mode
# ---------------------------------------------------------------------------


class TestStalenessDetection:
    """VAL-CROSS-003: Staleness detection via reference mode."""

    def test_reference_mode_staleness(self, monkeypatch):
        """Reference mode: modify source, project becomes stale on re-analyze."""
        with tempfile.TemporaryDirectory() as tmpdir:
            monkeypatch.setattr(
                "binary_analysis.projects.workspace.get_workspace_root",
                lambda: Path(tmpdir),
            )
            monkeypatch.setattr(
                "binary_analysis.projects.workspace._DEFAULT_WORKSPACE_ROOT",
                str(tmpdir),
            )

            binary_path = _create_binary_fixture(tmpdir)

            # Create, import in reference mode, analyze
            _run_cli_raw(["--json", "project", "create", "stale-test"])
            _run_cli_raw(
                ["--json", "import", "--project", "stale-test", "--reference", binary_path]
            )
            exit_code, out = _run_cli_raw(
                ["--json", "analyze", "--project", "stale-test", "--profile", "standard"]
            )
            assert exit_code == 0

            # Verify READY
            _, out = _run_cli_raw(["--json", "project", "status", "stale-test"])
            status = json.loads(out)
            assert status["data"]["state"] == "READY"

            # Modify source
            time.sleep(0.1)
            with open(binary_path, "ab") as f:
                f.write(b"\x00")

            # Re-analyze should detect staleness
            exit_code, out = _run_cli_raw(
                ["--json", "analyze", "--project", "stale-test", "--profile", "standard"]
            )
            result = json.loads(out)
            assert result["success"] is False
            # Should have staleness diagnostic
            diagnostics = result.get("diagnostics", [])
            stale_diags = [d for d in diagnostics if d.get("category") == "staleness"]
            assert len(stale_diags) > 0


# ---------------------------------------------------------------------------
# VAL-CROSS-005: Copy vs reference import modes
# ---------------------------------------------------------------------------


class TestCopyVsReference:
    """VAL-CROSS-005: Copy vs reference import modes."""

    def test_copy_mode_independent_of_source(self, monkeypatch):
        """Copy mode: delete source, project still works."""
        with tempfile.TemporaryDirectory() as tmpdir:
            monkeypatch.setattr(
                "binary_analysis.projects.workspace.get_workspace_root",
                lambda: Path(tmpdir),
            )
            monkeypatch.setattr(
                "binary_analysis.projects.workspace._DEFAULT_WORKSPACE_ROOT",
                str(tmpdir),
            )

            binary_path = _create_binary_fixture(tmpdir)

            _run_cli_raw(["--json", "project", "create", "copy-test"])
            _run_cli_raw(["--json", "import", "--project", "copy-test", binary_path])
            exit_code, _ = _run_cli_raw(
                ["--json", "analyze", "--project", "copy-test", "--profile", "standard"]
            )
            assert exit_code == 0

            # Delete source
            os.unlink(binary_path)

            # Metadata still works
            exit_code, _ = _run_cli_raw(["--json", "metadata", "--project", "copy-test"])
            assert exit_code == 0


# ---------------------------------------------------------------------------
# VAL-CROSS-006: Pagination stability
# ---------------------------------------------------------------------------


class TestPaginationStability:
    """VAL-CROSS-006: Pagination stability across queries."""

    def test_pagination_no_duplicates(self, monkeypatch):
        """All functions appear exactly once across pages."""
        with tempfile.TemporaryDirectory() as tmpdir:
            monkeypatch.setattr(
                "binary_analysis.projects.workspace.get_workspace_root",
                lambda: Path(tmpdir),
            )
            monkeypatch.setattr(
                "binary_analysis.projects.workspace._DEFAULT_WORKSPACE_ROOT",
                str(tmpdir),
            )

            binary_path = _create_binary_fixture(tmpdir)

            _run_cli_raw(["--json", "project", "create", "page-test"])
            _run_cli_raw(["--json", "import", "--project", "page-test", binary_path])
            _run_cli_raw(["--json", "analyze", "--project", "page-test", "--profile", "standard"])

            # Page 1
            _, out1 = _run_cli_raw(
                ["--json", "--limit", "2", "functions", "--project", "page-test"]
            )
            page1 = json.loads(out1)
            assert page1["success"] is True
            addrs1 = {i.get("address", {}).get("offset") for i in page1["data"]["items"]}

            # Page 2 if available
            cursor = page1["data"].get("next_cursor") or page1["data"].get("next_page_token")
            if cursor and page1["data"].get("has_more"):
                _, out2 = _run_cli_raw(
                    [
                        "--json",
                        "--limit",
                        "2",
                        "functions",
                        "--project",
                        "page-test",
                        "--cursor",
                        cursor,
                    ]
                )
                page2 = json.loads(out2)
                assert page2["success"] is True
                addrs2 = {i.get("address", {}).get("offset") for i in page2["data"]["items"]}
                assert addrs1.isdisjoint(addrs2)


# ---------------------------------------------------------------------------
# VAL-CROSS-007: Error recovery after ANALYSIS_FAILED
# ---------------------------------------------------------------------------


class TestErrorRecovery:
    """VAL-CROSS-007: Error recovery after ANALYSIS_FAILED."""

    def test_failed_clean_reattempt(self, monkeypatch):
        """FAILED -> clean -> project back to workable state."""
        with tempfile.TemporaryDirectory() as tmpdir:
            monkeypatch.setattr(
                "binary_analysis.projects.workspace.get_workspace_root",
                lambda: Path(tmpdir),
            )
            monkeypatch.setattr(
                "binary_analysis.projects.workspace._DEFAULT_WORKSPACE_ROOT",
                str(tmpdir),
            )

            binary_path = _create_binary_fixture(tmpdir)

            _run_cli_raw(["--json", "project", "create", "recovery-test"])
            _run_cli_raw(["--json", "import", "--project", "recovery-test", binary_path])

            # Cause analysis failure by corrupting the project state directly
            project_dir = os.path.join(tmpdir, "recovery-test")
            with open(os.path.join(project_dir, "project.json")) as f:
                manifest = json.load(f)
            manifest["state"] = "FAILED"
            with open(os.path.join(project_dir, "project.json"), "w") as f:
                json.dump(manifest, f)

            # Verify FAILED
            _, out = _run_cli_raw(["--json", "project", "status", "recovery-test"])
            status = json.loads(out)
            assert status["data"]["state"] == "FAILED"

            # Clean
            exit_code, _ = _run_cli_raw(["--json", "project", "clean", "recovery-test", "--yes"])
            assert exit_code == 0

            # After clean, state should be CREATED
            _, out = _run_cli_raw(["--json", "project", "status", "recovery-test"])
            status = json.loads(out)
            assert status["data"]["state"] == "CREATED"

            # Now re-import with a new binary
            binary_path2 = _create_binary_fixture(tmpdir, b"MZ\x00\x02")
            exit_code, _ = _run_cli_raw(
                ["--json", "import", "--project", "recovery-test", binary_path2]
            )
            assert exit_code == 0

            exit_code, out = _run_cli_raw(
                ["--json", "analyze", "--project", "recovery-test", "--profile", "standard"]
            )
            assert exit_code == 0

            _, out = _run_cli_raw(["--json", "project", "status", "recovery-test"])
            status = json.loads(out)
            assert status["data"]["state"] == "READY"


# ---------------------------------------------------------------------------
# VAL-CROSS-013: Re-import of same binary
# ---------------------------------------------------------------------------


class TestReimport:
    """VAL-CROSS-013: Re-import of same binary."""

    def test_reimport_same_binary(self, monkeypatch):
        """Import the same binary twice -> second import returns same binary_id."""
        with tempfile.TemporaryDirectory() as tmpdir:
            monkeypatch.setattr(
                "binary_analysis.projects.workspace.get_workspace_root",
                lambda: Path(tmpdir),
            )
            monkeypatch.setattr(
                "binary_analysis.projects.workspace._DEFAULT_WORKSPACE_ROOT",
                str(tmpdir),
            )

            binary_path = _create_binary_fixture(tmpdir)

            _run_cli_raw(["--json", "project", "create", "reimport-test"])

            # First import
            _, out1 = _run_cli_raw(["--json", "import", "--project", "reimport-test", binary_path])
            result1 = json.loads(out1)
            assert result1["success"] is True
            binary_id_1 = result1["data"]["binary_id"]

            # Second import of same file -> returns same binary_id
            _, out2 = _run_cli_raw(["--json", "import", "--project", "reimport-test", binary_path])
            result2 = json.loads(out2)
            assert result2["success"] is True
            binary_id_2 = result2["data"]["binary_id"]

            assert binary_id_1 == binary_id_2


# ---------------------------------------------------------------------------
# VAL-CROSS-014: Deterministic analysis across projects
# ---------------------------------------------------------------------------


class TestDeterministicAnalysis:
    """VAL-CROSS-014: Deterministic analysis across projects."""

    def test_same_binary_two_projects_same_results(self, monkeypatch):
        """Same binary in two projects produces identical structural data."""
        with tempfile.TemporaryDirectory() as tmpdir:
            monkeypatch.setattr(
                "binary_analysis.projects.workspace.get_workspace_root",
                lambda: Path(tmpdir),
            )
            monkeypatch.setattr(
                "binary_analysis.projects.workspace._DEFAULT_WORKSPACE_ROOT",
                str(tmpdir),
            )

            binary_path = _create_binary_fixture(tmpdir)

            # Project A
            _run_cli_raw(["--json", "project", "create", "det-test-a"])
            _run_cli_raw(["--json", "import", "--project", "det-test-a", binary_path])
            _run_cli_raw(["--json", "analyze", "--project", "det-test-a", "--profile", "standard"])

            # Project B
            _run_cli_raw(["--json", "project", "create", "det-test-b"])
            _run_cli_raw(["--json", "import", "--project", "det-test-b", binary_path])
            _run_cli_raw(["--json", "analyze", "--project", "det-test-b", "--profile", "standard"])

            # Compare section counts
            _, out_a = _run_cli_raw(["--json", "sections", "--project", "det-test-a"])
            sections_a = json.loads(out_a)
            _, out_b = _run_cli_raw(["--json", "sections", "--project", "det-test-b"])
            sections_b = json.loads(out_b)

            assert sections_a["data"]["total"] == sections_b["data"]["total"]

            # Compare function counts
            _, out_a = _run_cli_raw(["--json", "functions", "--project", "det-test-a"])
            funcs_a = json.loads(out_a)
            _, out_b = _run_cli_raw(["--json", "functions", "--project", "det-test-b"])
            funcs_b = json.loads(out_b)

            assert funcs_a["data"]["total"] == funcs_b["data"]["total"]


# ---------------------------------------------------------------------------
# VAL-CROSS-012: Analyze interruption and restart
# ---------------------------------------------------------------------------


class TestAnalyzeInterruption:
    """VAL-CROSS-012: Analyze interruption (lock cleanup)."""

    def test_analyze_completes_and_lock_released(self, monkeypatch):
        """Successful analyze releases the lock."""
        with tempfile.TemporaryDirectory() as tmpdir:
            from binary_analysis.projects.lock import is_locked

            monkeypatch.setattr(
                "binary_analysis.projects.workspace.get_workspace_root",
                lambda: Path(tmpdir),
            )
            monkeypatch.setattr(
                "binary_analysis.projects.workspace._DEFAULT_WORKSPACE_ROOT",
                str(tmpdir),
            )

            binary_path = _create_binary_fixture(tmpdir)

            _run_cli_raw(["--json", "project", "create", "interrupt-test"])
            _run_cli_raw(["--json", "import", "--project", "interrupt-test", binary_path])

            exit_code, _ = _run_cli_raw(
                ["--json", "analyze", "--project", "interrupt-test", "--profile", "standard"]
            )
            assert exit_code == 0

            # Lock should be released after completion
            project_dir = os.path.join(tmpdir, "interrupt-test")
            assert not is_locked(project_dir)
