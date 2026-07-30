"""Unit tests for the version command.

Validates VAL-CLI-008, VAL-CLI-009:
- Version reports cli_version, schema_version, workspace_version, adapter, backend, platform
- Version JSON envelope has command=version and all standard envelope fields
"""

from __future__ import annotations

import sys
from pathlib import Path
_scripts_dir = Path(__file__).resolve().parents[2] / "scripts"
if str(_scripts_dir) not in sys.path:
    sys.path.insert(0, str(_scripts_dir))

import json

import pytest
from binary_analysis.cli.version import execute


class TestVersionExecute:
    """Tests for version command execute function."""

    def test_version_data_has_required_fields(self) -> None:
        """Version data must contain cli_version, schema_version, workspace_version,
        adapter, backend, and platform."""
        import argparse

        args = argparse.Namespace()
        result = execute(args)

        data = result["data"]
        assert "cli_version" in data
        assert "schema_version" in data
        assert "workspace_version" in data
        assert "adapter" in data
        assert "backend" in data
        assert "platform" in data

    def test_version_adapter_has_name_and_version(self) -> None:
        """Adapter must have name and version."""
        import argparse

        args = argparse.Namespace()
        result = execute(args)

        adapter = result["data"]["adapter"]
        assert isinstance(adapter, dict)
        assert "name" in adapter
        assert "version" in adapter

    def test_version_backend_has_name_and_version(self) -> None:
        """Backend must have name and version."""
        import argparse

        args = argparse.Namespace()
        result = execute(args)

        backend = result["data"]["backend"]
        assert isinstance(backend, dict)
        assert "name" in backend
        assert "version" in backend

    def test_version_platform_has_details(self) -> None:
        """Platform must have system, machine, python_version."""
        import argparse

        args = argparse.Namespace()
        result = execute(args)

        platform_data = result["data"]["platform"]
        assert isinstance(platform_data, dict)
        assert "system" in platform_data
        assert "machine" in platform_data
        assert "python_version" in platform_data

    def test_version_cli_version_is_string(self) -> None:
        """cli_version must be a string."""
        import argparse

        args = argparse.Namespace()
        result = execute(args)

        assert isinstance(result["data"]["cli_version"], str)
        assert len(result["data"]["cli_version"]) > 0

    def test_version_schema_version_is_string(self) -> None:
        """schema_version must be a string."""
        import argparse

        args = argparse.Namespace()
        result = execute(args)

        assert isinstance(result["data"]["schema_version"], str)

    def test_version_workspace_version_is_string(self) -> None:
        """workspace_version must be a string."""
        import argparse

        args = argparse.Namespace()
        result = execute(args)

        assert isinstance(result["data"]["workspace_version"], str)

    def test_version_success_is_true(self) -> None:
        """Version should always return success=true."""
        import argparse

        args = argparse.Namespace()
        result = execute(args)

        assert result["success"] is True
        assert result["partial"] is False


class TestVersionCLI:
    """Integration-style tests for version command via main()."""

    def test_version_json_envelope(self, capsys: pytest.CaptureFixture) -> None:
        """version --json must produce valid JSON with command=version."""
        from binary_analysis.cli.main import main

        main(["--json", "version"])
        captured = capsys.readouterr()
        parsed = json.loads(captured.out)

        assert parsed["command"] == "version"
        assert parsed["success"] is True

        # All envelope fields present
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

    def test_version_json_data_fields(self, capsys: pytest.CaptureFixture) -> None:
        """version --json data must contain all required version info."""
        from binary_analysis.cli.main import main

        main(["--json", "version"])
        captured = capsys.readouterr()
        parsed = json.loads(captured.out)

        data = parsed["data"]
        assert "cli_version" in data
        assert "schema_version" in data
        assert "workspace_version" in data

        adapter = data["adapter"]
        assert isinstance(adapter, dict)
        assert "name" in adapter
        assert "version" in adapter

        backend = data["backend"]
        assert isinstance(backend, dict)
        assert "name" in backend
        assert "version" in backend

        platform_data = data["platform"]
        assert isinstance(platform_data, dict)
        assert "system" in platform_data
        assert "machine" in platform_data
        assert "python_version" in platform_data

    def test_version_json_no_null_required_fields(self, capsys: pytest.CaptureFixture) -> None:
        """All six required fields must be non-null."""
        from binary_analysis.cli.main import main

        main(["--json", "version"])
        captured = capsys.readouterr()
        parsed = json.loads(captured.out)

        data = parsed["data"]
        assert data["cli_version"] is not None
        assert data["schema_version"] is not None
        assert data["workspace_version"] is not None
        assert data["adapter"] is not None
        assert data["adapter"]["name"] is not None
        assert data["adapter"]["version"] is not None
        assert data["backend"] is not None
        assert data["backend"]["name"] is not None
        assert data["backend"]["version"] is not None
        assert data["platform"] is not None

    def test_version_exit_code_0(self) -> None:
        """version should always exit 0."""
        from binary_analysis.cli.main import main

        exit_code = main(["--json", "version"])
        assert exit_code == 0, f"Expected exit code 0, got {exit_code}"
