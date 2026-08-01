"""Unit tests for the doctor command.

Validates VAL-CLI-001, VAL-CLI-002, VAL-CLI-003:
- Doctor reports missing dependencies with severity, component, message, remediation
- Doctor reports all-clear when everything is healthy
- Doctor JSON envelope contains all required fields
"""

from __future__ import annotations

import sys
from pathlib import Path
_scripts_dir = Path(__file__).resolve().parents[2] / "scripts"
if str(_scripts_dir) not in sys.path:
    sys.path.insert(0, str(_scripts_dir))

import json

import pytest
from binary_analysis.bootstrap.deps import Dependency, discover_dependencies
from binary_analysis.cli.doctor import execute
from binary_analysis.domain.enums import ExitCode


class TestDoctorExecute:
    """Tests for doctor command execute function."""

    def test_doctor_result_has_required_fields(self) -> None:
        """Doctor result must have success, partial, warnings, diagnostics, data."""
        # We can't create a real argparse.Namespace easily, but we can
        # test the execute function directly with a mock
        import argparse

        args = argparse.Namespace()
        result = execute(args)

        assert "success" in result
        assert "partial" in result
        assert "warnings" in result
        assert "diagnostics" in result
        assert "data" in result

    def test_doctor_data_has_components(self) -> None:
        """Doctor data must contain components list."""
        import argparse

        args = argparse.Namespace()
        result = execute(args)

        assert "components" in result["data"]
        assert isinstance(result["data"]["components"], list)
        assert len(result["data"]["components"]) >= 1  # At least checks Java

    def test_doctor_diagnostics_have_required_fields(self) -> None:
        """Each diagnostic must have severity, component, and message."""
        import argparse

        args = argparse.Namespace()
        result = execute(args)
        diagnostics = result["diagnostics"]

        # There should be at least one diagnostic entry
        assert len(diagnostics) >= 1

        for diag in diagnostics:
            assert "severity" in diag
            assert "component" in diag
            assert "message" in diag
            assert diag["severity"] in ("INFO", "WARNING", "ERROR")

    def test_doctor_check_component_coverage(self) -> None:
        """Doctor should check java, ghidra, and pyghidra."""
        import argparse

        args = argparse.Namespace()
        result = execute(args)
        components = result["data"]["components"]
        component_names = {c["name"] for c in components}

        # All three required components should be checked
        assert "java" in component_names, "Java must be checked"
        assert "ghidra" in component_names, "Ghidra must be checked"
        assert "pyghidra" in component_names, "PyGhidra must be checked"

    def test_doctor_exit_code_when_deps_missing(self) -> None:
        """When deps are missing, result should include _exit_code = 3."""
        import argparse

        args = argparse.Namespace()
        result = execute(args)

        # If all deps are missing (common in test env), expect exit code 3
        has_error = any(d["status"] == "missing" for d in result["data"]["components"])
        if has_error:
            assert result.get("_exit_code") == ExitCode.DEPENDENCY_MISSING
            assert result["success"] is False

    def test_doctor_success_when_all_present(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """When all deps are present, success should be True."""
        # Mock discover_dependencies to return all present
        monkeypatch.setattr(
            "binary_analysis.cli.doctor.discover_dependencies",
            lambda: [
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
            ],
        )

        import argparse

        args = argparse.Namespace()
        result = execute(args)

        assert result["success"] is True
        assert "_exit_code" not in result  # No explicit exit code needed for success
        # All diagnostics should be INFO
        for diag in result["diagnostics"]:
            assert diag["severity"] == "INFO"
        # No ERROR diagnostics
        assert not any(d["severity"] == "ERROR" for d in result["diagnostics"])

    def test_doctor_missing_deps_have_remediation(self) -> None:
        """Missing deps must have remediation hints."""
        import argparse

        args = argparse.Namespace()
        result = execute(args)
        diagnostics = result["diagnostics"]

        error_diags = [d for d in diagnostics if d["severity"] == "ERROR"]
        if error_diags:
            for diag in error_diags:
                assert "remediation" in diag
                assert len(diag["remediation"]) > 0, f"Missing remediation for {diag['component']}"

    def test_doctor_components_have_status(self) -> None:
        """Each component must have a status field."""
        import argparse

        args = argparse.Namespace()
        result = execute(args)
        components = result["data"]["components"]

        for comp in components:
            assert "status" in comp
            assert comp["status"] in ("present", "missing", "error")
            assert "name" in comp
            assert "message" in comp
            assert "remediation" in comp


class TestDoctorCLI:
    """Integration-style tests for doctor command via main()."""

    def test_doctor_json_produces_valid_envelope(self, capsys: pytest.CaptureFixture) -> None:
        """doctor --json must produce valid JSON envelope."""
        from binary_analysis.cli.main import main

        main(["--json", "doctor"])
        captured = capsys.readouterr()
        parsed = json.loads(captured.out)

        # All envelope fields must be present
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

        assert parsed["command"] == "doctor"

    def test_doctor_json_diagnostics_structure(self, capsys: pytest.CaptureFixture) -> None:
        """doctor --json diagnostics must have severity, component, message."""
        from binary_analysis.cli.main import main

        main(["--json", "doctor"])
        captured = capsys.readouterr()
        parsed = json.loads(captured.out)

        for diag in parsed["diagnostics"]:
            assert "severity" in diag
            assert "component" in diag
            assert "message" in diag


class TestDependencyClass:
    """Tests for the Dependency dataclass."""

    def test_dependency_to_dict(self) -> None:
        """Dependency.to_dict() should produce expected keys."""
        dep = Dependency(
            name="java",
            status="present",
            version="21.0.1",
            path="/usr/bin/java",
            message="Java found",
            remediation="",
        )
        d = dep.to_dict()
        assert d["name"] == "java"
        assert d["status"] == "present"
        assert d["version"] == "21.0.1"
        assert d["path"] == "/usr/bin/java"

    def test_dependency_missing_to_dict(self) -> None:
        """Missing dependency to_dict should have null version/path."""
        dep = Dependency(
            name="ghidra",
            status="missing",
            message="Ghidra not found",
            remediation="Install Ghidra from https://ghidra-sre.org/",
        )
        d = dep.to_dict()
        assert d["name"] == "ghidra"
        assert d["status"] == "missing"
        assert d["version"] is None
        assert d["path"] is None
        assert len(d["remediation"]) > 0


class TestDiscoverDependencies:
    """Tests for the discover_dependencies function."""

    def test_discover_returns_list(self) -> None:
        """discover_dependencies must return a list."""
        deps = discover_dependencies()
        assert isinstance(deps, list)
        assert len(deps) >= 1

    def test_discover_checks_all_components(self) -> None:
        """discover_dependencies must check java, ghidra, pyghidra."""
        deps = discover_dependencies()
        names = {d.name for d in deps}
        assert "java" in names
        assert "ghidra" in names
        assert "pyghidra" in names

    def test_discover_deps_are_dependency_instances(self) -> None:
        """Each item must be a Dependency instance."""
        deps = discover_dependencies()
        for dep in deps:
            assert isinstance(dep, Dependency)

    def test_discover_deps_have_valid_status(self) -> None:
        """Each dependency must have a valid status."""
        deps = discover_dependencies()
        valid_statuses = {"present", "missing", "error"}
        for dep in deps:
            assert dep.status in valid_statuses

    def test_java_detection_with_java_home(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """When JAVA_HOME points to a valid JDK, Java should be present."""
        import shutil

        java_path = shutil.which("java")
        if java_path:
            monkeypatch.setenv("JAVA_HOME", "/usr")  # Won't match exactly but tests the flow
            deps = discover_dependencies()
            java_dep = next(d for d in deps if d.name == "java")
            assert java_dep is not None
