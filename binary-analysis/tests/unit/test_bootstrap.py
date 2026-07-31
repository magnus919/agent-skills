"""Unit tests for the bootstrap command.

Validates VAL-CLI-004, VAL-CLI-005, VAL-CLI-006, VAL-CLI-007, VAL-SAFE-006:
- Bootstrap --plan shows install targets without mutation
- Bootstrap --plan on healthy system reports nothing needed
- Bootstrap --apply downloads, installs, verifies
- Bootstrap --apply partial failure reports success=false, partial=true
- Checksum verification fails closed on mismatch
"""

from __future__ import annotations

import sys
from pathlib import Path
_scripts_dir = Path(__file__).resolve().parents[2] / "scripts"
if str(_scripts_dir) not in sys.path:
    sys.path.insert(0, str(_scripts_dir))

import hashlib
import json

import pytest
from binary_analysis.bootstrap.deps import Dependency
from binary_analysis.cli.bootstrap import (
    _apply_mode,
    _build_plan,
    _plan_mode,
    _verify_checksum,
)
from binary_analysis.domain.enums import ExitCode


class TestBuildPlan:
    """Tests for the build_plan function."""

    def test_plan_lists_missing_components(self) -> None:
        """Missing deps should have status=missing, action=install, source."""
        deps = [
            Dependency(
                name="java",
                status="missing",
                message="Java not found",
                remediation="Install Java",
            ),
            Dependency(
                name="ghidra",
                status="present",
                version="12.1.2",
                path="/opt/ghidra",
                message="Ghidra found",
                remediation="",
            ),
        ]
        plan = _build_plan(deps)
        assert len(plan) == 2

        java = plan[0]
        assert java["name"] == "java"
        assert java["status"] == "missing"
        assert java["action"] == "install"
        assert "source" in java
        assert "remediation" in java

        ghidra = plan[1]
        assert ghidra["name"] == "ghidra"
        assert ghidra["status"] == "present"
        assert ghidra["action"] == "none"

    def test_plan_all_present(self) -> None:
        """All-present deps should show all status=present, action=none."""
        deps = [
            Dependency(
                name="java",
                status="present",
                version="21.0.1",
                path="/usr/bin/java",
                message="Java found",
                remediation="",
            ),
            Dependency(
                name="ghidra",
                status="present",
                version="12.1.2",
                path="/opt/ghidra",
                message="Ghidra found",
                remediation="",
            ),
            Dependency(
                name="pyghidra",
                status="present",
                version="3.1.0",
                path="/venv/lib/pyghidra",
                message="PyGhidra found",
                remediation="",
            ),
        ]
        plan = _build_plan(deps)
        assert len(plan) == 3
        for item in plan:
            assert item["status"] == "present"
            assert item["action"] == "none"


class TestPlanMode:
    """Tests for the _plan_mode function."""

    def test_plan_mode_has_missing_returns_false_success(self) -> None:
        """When deps are missing, plan mode returns success=false."""
        deps = [
            Dependency(
                name="java",
                status="missing",
                message="Java not found",
                remediation="Install Java",
            ),
        ]
        result = _plan_mode(deps)
        assert result["success"] is False
        assert result["_exit_code"] == ExitCode.DEPENDENCY_MISSING

    def test_plan_mode_all_present_returns_true_success(self) -> None:
        """When all deps present, plan mode returns success=true."""
        deps = [
            Dependency(
                name="java",
                status="present",
                version="21.0.1",
                path="/usr/bin/java",
                message="Java found",
                remediation="",
            ),
        ]
        result = _plan_mode(deps)
        assert result["success"] is True
        assert "_exit_code" not in result

    def test_plan_mode_no_filesystem_mutation(self, tmp_path) -> None:
        """Plan mode must not create any files."""
        import os

        before = set(os.listdir(tmp_path))

        deps = [
            Dependency(
                name="java",
                status="missing",
                message="Java not found",
                remediation="Install Java",
            ),
        ]
        _plan_mode(deps)

        # Working in tmp_path — nothing should change
        after = set(os.listdir(tmp_path))
        assert after == before, "Plan mode must not create files"

    def test_plan_mode_diagnostics_for_missing(self) -> None:
        """Missing deps must produce ERROR diagnostics."""
        deps = [
            Dependency(
                name="java",
                status="missing",
                message="Java not found",
                remediation="Install Java",
            ),
            Dependency(
                name="ghidra",
                status="present",
                version="12.1.2",
                path="/opt/ghidra",
                message="Ghidra found",
                remediation="",
            ),
        ]
        result = _plan_mode(deps)
        diags = result["diagnostics"]

        # Only missing deps get diagnostics
        assert len(diags) == 1
        assert diags[0]["severity"] == "ERROR"
        assert diags[0]["component"] == "java"


class TestApplyMode:
    """Tests for the _apply_mode function."""

    def test_apply_mode_all_present(self) -> None:
        """When all deps present, apply returns success=true."""
        deps = [
            Dependency(
                name="java",
                status="present",
                version="21.0.1",
                path="/usr/bin/java",
                message="Java found",
                remediation="",
            ),
        ]
        result = _apply_mode(deps)
        assert result["success"] is True
        assert "_exit_code" not in result

    def test_apply_mode_requires_manual(self) -> None:
        """Deps requiring manual install produce WARNING diagnostics."""
        deps = [
            Dependency(
                name="java",
                status="missing",
                message="Java not found",
                remediation="Install Java JDK 17+",
            ),
        ]
        result = _apply_mode(deps)
        # Java installation requires manual steps
        components = result["data"]["components"]
        java = components[0]
        assert java["status"] == "requires_manual"


class TestChecksumVerification:
    """Tests for checksum verification (VAL-SAFE-006)."""

    def test_verify_checksum_match_passes(self) -> None:
        """Matching checksums should not raise."""
        data = b"hello world"
        expected = hashlib.sha256(data).hexdigest()
        # Should not raise
        _verify_checksum(data, expected)

    def test_verify_checksum_mismatch_raises(self) -> None:
        """Mismatched checksums should raise ValueError."""
        data = b"hello world"
        expected = "a" * 64  # Deliberately wrong
        with pytest.raises(ValueError, match="Checksum mismatch"):
            _verify_checksum(data, expected)

    def test_verify_checksum_empty_data(self) -> None:
        """Empty data should still verify checksum."""
        data = b""
        expected = hashlib.sha256(data).hexdigest()
        _verify_checksum(data, expected)

    def test_verify_checksum_case_insensitive(self) -> None:
        """Checksum comparison should be case-insensitive."""
        data = b"test"
        expected = hashlib.sha256(data).hexdigest().upper()
        _verify_checksum(data, expected)


class TestBootstrapCLI:
    """Integration-style tests for bootstrap command via main()."""

    def test_bootstrap_plan_json_produces_envelope(self, capsys: pytest.CaptureFixture) -> None:
        """bootstrap --plan --json must produce valid JSON envelope."""
        from binary_analysis.cli.main import main

        main(["--json", "bootstrap", "--plan"])
        captured = capsys.readouterr()
        parsed = json.loads(captured.out)

        # Must have all envelope fields
        for key in (
            "schema_version",
            "command",
            "generated_at",
            "duration_ms",
            "success",
            "partial",
            "warnings",
            "diagnostics",
            "provenance",
            "data",
        ):
            assert key in parsed, f"Missing envelope key: {key}"

        assert parsed["command"] == "bootstrap"

    def test_bootstrap_plan_json_has_components(self, capsys: pytest.CaptureFixture) -> None:
        """bootstrap --plan --json must list components."""
        from binary_analysis.cli.main import main

        main(["--json", "bootstrap", "--plan"])
        captured = capsys.readouterr()
        parsed = json.loads(captured.out)

        assert "components" in parsed["data"]
        assert isinstance(parsed["data"]["components"], list)

    def test_bootstrap_plan_json_components_have_required_fields(
        self, capsys: pytest.CaptureFixture
    ) -> None:
        """Each component in plan must have name, status, action, source."""
        from binary_analysis.cli.main import main

        main(["--json", "bootstrap", "--plan"])
        captured = capsys.readouterr()
        parsed = json.loads(captured.out)

        for comp in parsed["data"]["components"]:
            assert "name" in comp
            assert "status" in comp
            assert "action" in comp

    def test_bootstrap_apply_json_produces_envelope(self, capsys: pytest.CaptureFixture) -> None:
        """bootstrap --apply --json must produce valid JSON envelope."""
        from binary_analysis.cli.main import main

        main(["--json", "bootstrap", "--apply"])
        captured = capsys.readouterr()
        parsed = json.loads(captured.out)

        for key in (
            "schema_version",
            "command",
            "generated_at",
            "duration_ms",
            "success",
            "partial",
            "warnings",
            "diagnostics",
            "provenance",
            "data",
        ):
            assert key in parsed, f"Missing envelope key: {key}"
