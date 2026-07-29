"""Unit tests for all canonical enumerations."""

from __future__ import annotations

import json

from binary_analysis.domain.enums import (
    AuditResult,
    Confidence,
    DiagnosticSeverity,
    Endianness,
    FunctionNameSource,
    ImportResolution,
    ProjectState,
    ReferenceKind,
    ReportType,
)


class TestProjectState:
    """Tests for ProjectState enum."""

    def test_all_six_states_defined(self) -> None:
        assert len(ProjectState) == 6

    def test_values_are_upper_case(self) -> None:
        for state in ProjectState:
            assert state.value == state.value.upper()

    def test_expected_values(self) -> None:
        assert ProjectState.CREATED.value == "CREATED"
        assert ProjectState.IMPORTED.value == "IMPORTED"
        assert ProjectState.ANALYZING.value == "ANALYZING"
        assert ProjectState.READY.value == "READY"
        assert ProjectState.STALE.value == "STALE"
        assert ProjectState.FAILED.value == "FAILED"

    def test_serializes_as_string(self) -> None:
        raw = json.dumps(ProjectState.CREATED.value)
        assert raw == '"CREATED"'

    def test_is_string_enum(self) -> None:
        assert isinstance(ProjectState.CREATED, str)


class TestConfidence:
    """Tests for Confidence enum."""

    def test_all_four_levels_defined(self) -> None:
        assert len(Confidence) == 4

    def test_values_are_upper_case(self) -> None:
        for level in Confidence:
            assert level.value == level.value.upper()

    def test_serializes_as_string(self) -> None:
        assert json.dumps(Confidence.HIGH.value) == '"HIGH"'
        assert json.dumps(Confidence.LOW.value) == '"LOW"'


class TestDiagnosticSeverity:
    """Tests for DiagnosticSeverity enum."""

    def test_all_three_levels_defined(self) -> None:
        assert len(DiagnosticSeverity) == 3

    def test_values_match_expected(self) -> None:
        assert DiagnosticSeverity.INFO.value == "INFO"
        assert DiagnosticSeverity.WARNING.value == "WARNING"
        assert DiagnosticSeverity.ERROR.value == "ERROR"


class TestReferenceKind:
    """Tests for ReferenceKind enum."""

    def test_all_nine_kinds_defined(self) -> None:
        assert len(ReferenceKind) == 9

    def test_expected_values(self) -> None:
        assert ReferenceKind.CALL.value == "CALL"
        assert ReferenceKind.JUMP.value == "JUMP"
        assert ReferenceKind.READ.value == "READ"
        assert ReferenceKind.WRITE.value == "WRITE"
        assert ReferenceKind.DATA.value == "DATA"
        assert ReferenceKind.IMPORT.value == "IMPORT"
        assert ReferenceKind.EXPORT.value == "EXPORT"
        assert ReferenceKind.INDIRECT.value == "INDIRECT"
        assert ReferenceKind.UNKNOWN.value == "UNKNOWN"


class TestEndianness:
    """Tests for Endianness enum."""

    def test_all_four_values_defined(self) -> None:
        assert len(Endianness) == 4

    def test_expected_values(self) -> None:
        assert Endianness.LITTLE.value == "LITTLE"
        assert Endianness.BIG.value == "BIG"
        assert Endianness.MIXED.value == "MIXED"
        assert Endianness.UNKNOWN.value == "UNKNOWN"


class TestFunctionNameSource:
    """Tests for FunctionNameSource enum."""

    def test_all_seven_sources_defined(self) -> None:
        assert len(FunctionNameSource) == 7

    def test_expected_values(self) -> None:
        assert FunctionNameSource.ORIGINAL.value == "ORIGINAL"
        assert FunctionNameSource.IMPORTED.value == "IMPORTED"
        assert FunctionNameSource.DEBUG.value == "DEBUG"
        assert FunctionNameSource.BACKEND_GENERATED.value == "BACKEND_GENERATED"
        assert FunctionNameSource.USER_ANNOTATION.value == "USER_ANNOTATION"
        assert FunctionNameSource.AGENT_SUGGESTION.value == "AGENT_SUGGESTION"
        assert FunctionNameSource.UNKNOWN.value == "UNKNOWN"


class TestImportResolution:
    """Tests for ImportResolution enum."""

    def test_all_three_states_defined(self) -> None:
        assert len(ImportResolution) == 3

    def test_expected_values(self) -> None:
        assert ImportResolution.RESOLVED.value == "RESOLVED"
        assert ImportResolution.PARTIAL.value == "PARTIAL"
        assert ImportResolution.UNRESOLVED.value == "UNRESOLVED"


class TestReportType:
    """Tests for ReportType enum."""

    def test_all_three_types_defined(self) -> None:
        assert len(ReportType) == 3

    def test_expected_values(self) -> None:
        assert ReportType.TRIAGE.value == "TRIAGE"
        assert ReportType.FOCUSED.value == "FOCUSED"
        assert ReportType.PROJECT.value == "PROJECT"


class TestAuditResult:
    """Tests for AuditResult enum."""

    def test_all_five_results_defined(self) -> None:
        assert len(AuditResult) == 5

    def test_expected_values(self) -> None:
        assert AuditResult.SUCCESS.value == "SUCCESS"
        assert AuditResult.PARTIAL.value == "PARTIAL"
        assert AuditResult.FAILED.value == "FAILED"
        assert AuditResult.CANCELLED.value == "CANCELLED"
        assert AuditResult.REFUSED.value == "REFUSED"


class TestEnumSerialization:
    """Ensure all enums serialize as UPPER_CASE strings (VAL-JSON-013)."""

    def test_no_enum_serializes_as_integer(self) -> None:
        """No enum value should be an integer ordinal."""
        all_enums = [
            ProjectState,
            Confidence,
            DiagnosticSeverity,
            ReferenceKind,
            Endianness,
            FunctionNameSource,
            ImportResolution,
            ReportType,
            AuditResult,
        ]
        for enum_class in all_enums:
            for member in enum_class:
                serialized = json.dumps(member.value)
                assert serialized.startswith('"'), (
                    f"{enum_class.__name__}.{member.name} serialized as integer: {serialized}"
                )

    def test_no_enum_serializes_as_lowercase(self) -> None:
        """No enum value should be lowercase."""
        all_enums = [
            ProjectState,
            Confidence,
            DiagnosticSeverity,
            ReferenceKind,
            Endianness,
            FunctionNameSource,
            ImportResolution,
            ReportType,
            AuditResult,
        ]
        for enum_class in all_enums:
            for member in enum_class:
                assert member.value == member.value.upper(), (
                    f"{enum_class.__name__}.{member.name} is not UPPER_CASE: {member.value}"
                )
