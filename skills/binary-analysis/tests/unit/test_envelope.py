"""Unit tests for the CLI JSON envelope builder."""

from __future__ import annotations

import json
import re

from binary_analysis.cli.main import SCHEMA_VERSION, build_envelope


class TestBuildEnvelope:
    """Tests for the build_envelope function."""

    def test_envelope_has_all_required_fields(self) -> None:
        """Envelope must contain all 10 required top-level keys."""
        envelope = build_envelope(
            command="test-cmd",
            success=True,
            partial=False,
            warnings=[],
            diagnostics=[],
            data={"key": "value"},
            duration_ms=42,
        )
        required_keys = {
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
        }
        assert set(envelope.keys()) == required_keys

    def test_schema_version_is_string(self) -> None:
        """schema_version must be a string matching '1.0.0'."""
        envelope = build_envelope(
            command="test",
            success=True,
            partial=False,
            warnings=[],
            diagnostics=[],
            data={},
            duration_ms=0,
        )
        assert isinstance(envelope["schema_version"], str)
        assert envelope["schema_version"] == SCHEMA_VERSION

    def test_command_matches_input(self) -> None:
        """command field must match the provided command name."""
        envelope = build_envelope(
            command="doctor",
            success=True,
            partial=False,
            warnings=[],
            diagnostics=[],
            data={},
            duration_ms=5,
        )
        assert envelope["command"] == "doctor"

    def test_generated_at_is_iso8601_with_timezone(self) -> None:
        """generated_at must be ISO 8601 with timezone offset."""
        envelope = build_envelope(
            command="test",
            success=True,
            partial=False,
            warnings=[],
            diagnostics=[],
            data={},
            duration_ms=10,
        )
        ts = envelope["generated_at"]
        assert re.match(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?(Z|[+-]\d{2}:\d{2})$", ts), (
            f"Timestamp '{ts}' is not ISO 8601 with timezone"
        )

    def test_duration_ms_is_non_negative_integer(self) -> None:
        """duration_ms must be a non-negative integer (int, not float or string)."""
        for val in [0, 1, 42, 99999]:
            envelope = build_envelope(
                command="test",
                success=True,
                partial=False,
                warnings=[],
                diagnostics=[],
                data={},
                duration_ms=val,
            )
            assert isinstance(envelope["duration_ms"], int)
            assert envelope["duration_ms"] >= 0
            assert envelope["duration_ms"] == val

    def test_success_and_partial_are_json_booleans(self) -> None:
        """success and partial must be Python bool (serializes as JSON true/false)."""
        for success_val, partial_val in [
            (True, False),
            (False, True),
            (True, True),
            (False, False),
        ]:
            envelope = build_envelope(
                command="test",
                success=success_val,
                partial=partial_val,
                warnings=[],
                diagnostics=[],
                data={},
                duration_ms=0,
            )
            assert isinstance(envelope["success"], bool)
            assert isinstance(envelope["partial"], bool)
            assert envelope["success"] is success_val
            assert envelope["partial"] is partial_val

            # Verify they serialize as JSON true/false, not strings
            raw = json.dumps(envelope)
            assert '"success": true' in raw or '"success": false' in raw
            assert '"partial": true' in raw or '"partial": false' in raw
            assert '"success": "true"' not in raw
            assert '"success": "false"' not in raw

    def test_warnings_and_diagnostics_are_arrays(self) -> None:
        """warnings and diagnostics must be arrays (may be empty)."""
        envelope = build_envelope(
            command="test",
            success=True,
            partial=False,
            warnings=[{"msg": "warn1"}],
            diagnostics=[{"severity": "ERROR", "message": "err1"}],
            data={},
            duration_ms=0,
        )
        assert isinstance(envelope["warnings"], list)
        assert isinstance(envelope["diagnostics"], list)
        assert len(envelope["warnings"]) == 1
        assert len(envelope["diagnostics"]) == 1

    def test_warnings_and_diagnostics_can_be_empty(self) -> None:
        """warnings and diagnostics can be empty lists."""
        envelope = build_envelope(
            command="test",
            success=True,
            partial=False,
            warnings=[],
            diagnostics=[],
            data={},
            duration_ms=0,
        )
        assert envelope["warnings"] == []
        assert envelope["diagnostics"] == []

    def test_provenance_is_object(self) -> None:
        """provenance must be a dict."""
        envelope = build_envelope(
            command="test",
            success=True,
            partial=False,
            warnings=[],
            diagnostics=[],
            data={},
            duration_ms=0,
        )
        assert isinstance(envelope["provenance"], dict)

    def test_data_can_be_null_or_empty(self) -> None:
        """data may be None, empty dict, empty list, or populated."""
        for data_val in [None, {}, [], {"items": [1, 2, 3]}]:
            envelope = build_envelope(
                command="test",
                success=True,
                partial=False,
                warnings=[],
                diagnostics=[],
                data=data_val,
                duration_ms=0,
            )
            assert envelope["data"] == data_val

    def test_json_serializable(self) -> None:
        """The full envelope must be JSON-serializable."""
        envelope = build_envelope(
            command="test-cmd",
            success=True,
            partial=True,
            warnings=[{"code": "W001", "message": "test warning"}],
            diagnostics=[{"severity": "INFO", "message": "test diag"}],
            data={"items": [{"id": 1, "name": "test"}]},
            duration_ms=153,
        )
        raw = json.dumps(envelope, ensure_ascii=False)
        parsed = json.loads(raw)
        assert parsed == envelope

    def test_default_provenance_included(self) -> None:
        """Envelope built without provenance should include default provenance."""
        envelope = build_envelope(
            command="test",
            success=True,
            partial=False,
            warnings=[],
            diagnostics=[],
            data={},
            duration_ms=0,
        )
        prov = envelope["provenance"]
        assert "cli_version" in prov
        assert "schema_version" in prov
