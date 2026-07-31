"""Unit tests for CLI argument parsing and exit codes."""

from __future__ import annotations

import sys
from pathlib import Path
_scripts_dir = Path(__file__).resolve().parents[2] / "scripts"
if str(_scripts_dir) not in sys.path:
    sys.path.insert(0, str(_scripts_dir))

import argparse
import json

import pytest
from binary_analysis.cli.main import (
    _extract_globals,
    _positive_duration,
    _positive_int,
    build_parser,
    main,
)
from binary_analysis.domain.enums import ExitCode


class TestArgumentValidators:
    """Tests for custom argparse type validators."""

    def test_positive_int_accepts_positive(self) -> None:
        """_positive_int should accept positive values."""
        for val in ["1", "10", "100", "99999"]:
            assert _positive_int(val) == int(val)

    def test_positive_int_rejects_zero(self) -> None:
        """_positive_int should reject zero."""
        with pytest.raises(argparse.ArgumentTypeError, match="limit must be a positive integer"):
            _positive_int("0")

    def test_positive_int_rejects_negative(self) -> None:
        """_positive_int should reject negative values."""
        with pytest.raises(argparse.ArgumentTypeError, match="limit must be a positive integer"):
            _positive_int("-5")

    def test_positive_int_rejects_non_numeric(self) -> None:
        """_positive_int should reject non-numeric input."""
        with pytest.raises(argparse.ArgumentTypeError, match="limit must be a positive integer"):
            _positive_int("abc")

    def test_positive_duration_accepts_positive(self) -> None:
        """_positive_duration should accept positive values."""
        for val in ["1", "30", "300", "3600"]:
            assert _positive_duration(val) == int(val)

    def test_positive_duration_rejects_zero(self) -> None:
        """_positive_duration should reject zero."""
        with pytest.raises(argparse.ArgumentTypeError, match="timeout must be a positive duration"):
            _positive_duration("0")

    def test_positive_duration_rejects_negative(self) -> None:
        """_positive_duration should reject negative values."""
        with pytest.raises(argparse.ArgumentTypeError, match="timeout must be a positive duration"):
            _positive_duration("-1")


class TestExtractGlobals:
    """Tests for global flag extraction/reordering."""

    def test_extract_json_before_subcommand(self) -> None:
        """--json should be moved before the subcommand."""
        result = _extract_globals(["doctor", "--json"])
        assert result == ["--json", "doctor"]

    def test_extract_quiet_before_subcommand(self) -> None:
        """--quiet should be moved before the subcommand."""
        result = _extract_globals(["version", "--quiet"])
        assert result == ["--quiet", "version"]

    def test_extract_limit_with_value(self) -> None:
        """--limit with its value should be moved before the subcommand."""
        result = _extract_globals(["doctor", "--limit", "50"])
        assert result == ["--limit", "50", "doctor"]

    def test_extract_timeout_with_value(self) -> None:
        """--timeout with its value should be moved before the subcommand."""
        result = _extract_globals(["doctor", "--timeout", "120"])
        assert result == ["--timeout", "120", "doctor"]

    def test_preserve_equals_form(self) -> None:
        """--limit=50 should be preserved as-is."""
        result = _extract_globals(["doctor", "--limit=50"])
        assert result == ["--limit=50", "doctor"]

    def test_non_global_flags_unchanged(self) -> None:
        """Non-global flags remain after the subcommand."""
        # None of these are global flags, so all remain in the tail after "project"
        result = _extract_globals(["project", "create", "--dry-run", "my-proj"])
        assert result == ["project", "create", "--dry-run", "my-proj"]


class TestParser:
    """Tests for the argparse parser structure."""

    def test_parser_has_global_flags(self) -> None:
        """Parser should define --json, --quiet, --limit, --timeout as global flags."""
        parser = build_parser()
        # Use parse_known_args to test flag presence
        args, _ = parser.parse_known_args(["--json", "--quiet", "--limit", "50", "doctor"])
        assert args.json is True
        assert args.quiet is True
        assert args.limit == 50

    def test_parser_help_lists_subcommands(self) -> None:
        """--help should list doctor, bootstrap, version, project."""
        parser = build_parser()
        help_text = parser.format_help()
        assert "doctor" in help_text
        assert "bootstrap" in help_text
        assert "version" in help_text
        assert "project" in help_text

    def test_parser_accepts_doctor_command(self) -> None:
        """Parser should accept 'doctor' as a command."""
        parser = build_parser()
        args = parser.parse_args(["doctor"])
        assert args.command == "doctor"

    def test_parser_accepts_bootstrap_command(self) -> None:
        """Parser should accept 'bootstrap' as a command."""
        parser = build_parser()
        args = parser.parse_args(["bootstrap"])
        assert args.command == "bootstrap"

    def test_parser_accepts_version_command(self) -> None:
        """Parser should accept 'version' as a command."""
        parser = build_parser()
        args = parser.parse_args(["version"])
        assert args.command == "version"

    def test_parser_accepts_project_command(self) -> None:
        """Parser should accept 'project' as a command."""
        parser = build_parser()
        args = parser.parse_args(["project", "create", "my-proj"])
        assert args.command == "project"
        assert args.project_command == "create"

    def test_parser_project_subcommands(self) -> None:
        """Parser should support all project subcommands."""
        parser = build_parser()
        # subcommands that take a positional project name arg
        positional_subcmds = ["create", "status", "clean", "remove", "migrate"]
        for subcmd in positional_subcmds:
            args = parser.parse_args(["project", subcmd, "test-project"])
            assert args.project_command == subcmd
        # 'list' takes no positional project name arg
        args = parser.parse_args(["project", "list"])
        assert args.project_command == "list"


class TestMainExitCodes:
    """Tests for main() exit codes."""

    def test_version_json_exit_0(self) -> None:
        """version --json should exit with code 0."""
        exit_code = main(["--json", "version"])
        assert exit_code == ExitCode.SUCCESS

    def test_doctor_json_exit_3_when_missing(self) -> None:
        """doctor --json should exit with code 3 when dependencies are missing."""
        exit_code = main(["--json", "doctor"])
        # If deps are all present (rare in test env), exit 0; otherwise exit 3
        assert exit_code in (ExitCode.SUCCESS, ExitCode.DEPENDENCY_MISSING), (
            f"Expected exit 0 or 3, got {exit_code}"
        )

    def test_invalid_flag_exit_2(self) -> None:
        """--nonexistent-flag should exit with code 2."""
        exit_code = main(["--nonexistent-flag", "doctor"])
        assert exit_code == ExitCode.INVALID_ARGS

    def test_project_no_subcommand_exit_2(self) -> None:
        """project without subcommand should exit with code 2."""
        exit_code = main(["project"])
        assert exit_code == ExitCode.INVALID_ARGS

    def test_negative_limit_exit_2(self) -> None:
        """Negative --limit should exit with code 2."""
        exit_code = main(["--limit", "-5", "doctor"])
        assert exit_code == ExitCode.INVALID_ARGS

    def test_negative_timeout_exit_2(self) -> None:
        """Negative --timeout should exit with code 2."""
        exit_code = main(["--timeout", "-1", "doctor"])
        assert exit_code == ExitCode.INVALID_ARGS

    def test_no_command_exit_2(self) -> None:
        """No command specified should exit with code 2."""
        exit_code = main([])
        assert exit_code == ExitCode.INVALID_ARGS

    def test_unknown_command_exit_2(self) -> None:
        """Unknown command should exit with code 2."""
        exit_code = main(["nonexistent-cmd"])
        assert exit_code == ExitCode.INVALID_ARGS


class TestJsonEnvelopeOutput:
    """Tests for JSON envelope output from main()."""

    def test_version_json_output_is_valid_json(self, capsys: pytest.CaptureFixture) -> None:
        """version --json stdout must be valid parseable JSON."""
        main(["--json", "version"])
        captured = capsys.readouterr()
        parsed = json.loads(captured.out)
        assert parsed["command"] == "version"
        assert "schema_version" in parsed

    def test_version_json_envelope_fields(self, capsys: pytest.CaptureFixture) -> None:
        """version --json must contain all envelope fields."""
        main(["--json", "version"])
        captured = capsys.readouterr()
        parsed = json.loads(captured.out)

        required = [
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
        ]
        for key in required:
            assert key in parsed, f"Missing key: {key}"

    def test_command_field_matches_invoked(self, capsys: pytest.CaptureFixture) -> None:
        """response.command must match the invoked command name."""
        main(["--json", "doctor"])
        captured = capsys.readouterr()
        parsed = json.loads(captured.out)
        assert parsed["command"] == "doctor"

    def test_project_command_includes_subcommand_name(self, capsys: pytest.CaptureFixture) -> None:
        """project create --json should report 'project create' as command."""
        main(["--json", "project", "create", "my-proj"])
        captured = capsys.readouterr()
        parsed = json.loads(captured.out)
        assert parsed["command"] == "project create"

    def test_duration_ms_is_non_negative_integer(self, capsys: pytest.CaptureFixture) -> None:
        """duration_ms must be non-negative integer."""
        main(["--json", "version"])
        captured = capsys.readouterr()
        parsed = json.loads(captured.out)
        assert isinstance(parsed["duration_ms"], int)
        assert parsed["duration_ms"] >= 0

    def test_success_and_partial_are_booleans(self, capsys: pytest.CaptureFixture) -> None:
        """success and partial must be JSON booleans."""
        main(["--json", "version"])
        captured = capsys.readouterr()
        parsed = json.loads(captured.out)
        assert isinstance(parsed["success"], bool)
        assert isinstance(parsed["partial"], bool)

    def test_timestamp_is_iso8601(self, capsys: pytest.CaptureFixture) -> None:
        """generated_at must be ISO 8601 with timezone."""
        import re

        main(["--json", "version"])
        captured = capsys.readouterr()
        parsed = json.loads(captured.out)
        ts = parsed["generated_at"]
        assert re.match(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?(Z|[+-]\d{2}:\d{2})$", ts), (
            f"Timestamp '{ts}' is not ISO 8601 with timezone"
        )

    def test_no_extraneous_text_on_stdout(self, capsys: pytest.CaptureFixture) -> None:
        """--json output should not have extraneous text on stdout."""
        main(["--json", "version"])
        captured = capsys.readouterr()
        # Must be parseable as JSON from the very first character
        assert captured.out.strip().startswith("{")

    def test_error_exit_2_produces_json_envelope(self, capsys: pytest.CaptureFixture) -> None:
        """Error exit code 2 should still produce JSON envelope when --json is used."""
        # Use an invalid flag scenario AFTER a valid command (to trigger our handler, not argparse's)
        exit_code = main(["--json", "project"])
        captured = capsys.readouterr()
        parsed = json.loads(captured.out)
        assert exit_code == 2
        assert parsed["success"] is False
        assert parsed["command"] == "project"
        assert len(parsed["diagnostics"]) > 0
