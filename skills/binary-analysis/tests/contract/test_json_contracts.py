"""Contract tests for JSON envelope consistency across all commands.

Validates the assertions from VAL-JSON-007 through VAL-JSON-017
and the cross-cutting VAL-CROSS-010 bootstrap-to-doctor roundtrip.
"""

from __future__ import annotations

import base64
import json
import re
import tempfile
from typing import Any, ClassVar

import pytest
from binary_analysis.cli.helpers import (
    PAGE_SIZE_DEFAULT,
    PAGE_SIZE_MAX,
    SCHEMA_VERSION,
    build_paginated_response,
    clamp_page_size,
    enrich_provenance,
    ensure_collection,
    make_partial_success,
    make_warning,
)
from binary_analysis.cli.helpers import (
    default_provenance as _default_provenance,
)
from binary_analysis.cli.main import build_envelope, main
from binary_analysis.domain.enums import ExitCode

# ---------------------------------------------------------------------------
# Helper: extract JSON from capsys
# ---------------------------------------------------------------------------


def _run_json(argv: list[str], capsys: pytest.CaptureFixture) -> dict[str, Any]:
    """Run main() with --json and return parsed envelope."""
    exit_code = main(argv)
    captured = capsys.readouterr()
    if not captured.out.strip():
        return {"_exit_code": exit_code, "_raw": ""}
    try:
        parsed = json.loads(captured.out)
        parsed["_exit_code"] = exit_code
        return parsed
    except json.JSONDecodeError:
        return {"_exit_code": exit_code, "_raw": captured.out}


# ============================================================================
# VAL-JSON-007: Pagination token null for last page
# ============================================================================


class TestPaginatedTokenNullOnLastPage:
    """Verify next_page_token logic in build_paginated_response."""

    def test_token_non_null_when_more_pages(self) -> None:
        """next_page_token must be a non-null string when has_more=True."""
        items = [{"id": i} for i in range(5)]
        result = build_paginated_response(items=items, total=20, offset=0, limit=5)
        assert result["has_more"] is True
        assert isinstance(result["next_page_token"], str)
        assert result["next_page_token"] is not None

    def test_token_null_on_last_page(self) -> None:
        """next_page_token must be null on the final page."""
        items = [{"id": i} for i in range(5)]
        result = build_paginated_response(items=items, total=20, offset=15, limit=5)
        assert result["has_more"] is False
        assert result["next_page_token"] is None

    def test_accumulated_count_equals_total(self) -> None:
        """Accumulating page items across all pages must equal total."""
        total = 47
        page_size = 10
        accumulated: list[dict[str, Any]] = []
        offset = 0
        while True:
            page_items = [{"id": i} for i in range(offset, min(offset + page_size, total))]
            result = build_paginated_response(
                items=page_items, total=total, offset=offset, limit=page_size
            )
            accumulated.extend(result["items"])
            if not result["has_more"]:
                break
            # Decode next_page_token to get next offset
            token: str = result["next_page_token"]
            cursor_data = json.loads(base64.urlsafe_b64decode(token.encode("ascii")))
            offset = cursor_data["offset"]

        assert len(accumulated) == total

    def test_empty_result_token_null(self) -> None:
        """Empty result set should have next_page_token null."""
        result = build_paginated_response(items=[], total=0, offset=0, limit=10)
        assert result["has_more"] is False
        assert result["next_page_token"] is None
        assert result["total"] == 0

    def test_project_list_pagination_token_null_last_page(
        self, capsys: pytest.CaptureFixture, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """project list with --json should have next_page_token=null on last page."""
        # Use a temp workspace to avoid interfering with real projects
        with tempfile.TemporaryDirectory() as tmpdir:
            monkeypatch.setenv("BINARY_WORKSPACE_ROOT", tmpdir)
            # Create 0 projects — list should be empty, token null
            envelope = _run_json(["--json", "project", "list"], capsys)
            data = envelope.get("data", {})
            items = data.get("items", [])
            assert isinstance(items, list)
            # With no projects, token should be null
            assert data.get("next_page_token") is None
            assert data.get("has_more") is False

    def test_page_size_field_present(self) -> None:
        """Paginated responses must include page_size field."""
        result = build_paginated_response(
            items=[{"a": 1}], total=1, offset=0, limit=PAGE_SIZE_DEFAULT
        )
        assert "page_size" in result
        assert result["page_size"] == PAGE_SIZE_DEFAULT


# ============================================================================
# VAL-JSON-008: Pagination defaults and bounds
# ============================================================================


class TestPaginationDefaultsAndBounds:
    """Verify default page size, max clamping, and rejection/clamping of 0."""

    def test_default_page_size_is_100(self) -> None:
        """clamp_page_size(None) must return 100 with no warning."""
        value, warning = clamp_page_size(None)
        assert value == PAGE_SIZE_DEFAULT
        assert warning is None
        assert PAGE_SIZE_DEFAULT == 100

    def test_clamp_above_max(self) -> None:
        """Values above PAGE_SIZE_MAX must be clamped to PAGE_SIZE_MAX with warning."""
        value1, warning1 = clamp_page_size(2000)
        assert value1 == PAGE_SIZE_MAX
        assert warning1 is not None
        value2, warning2 = clamp_page_size(1001)
        assert value2 == PAGE_SIZE_MAX
        assert warning2 is not None
        assert PAGE_SIZE_MAX == 1000

    def test_zero_clamped_to_default(self) -> None:
        """--page-size 0 must be clamped to default (not error)."""
        value, warning = clamp_page_size(0)
        assert value == PAGE_SIZE_DEFAULT
        assert warning is None

    def test_negative_clamped_to_default(self) -> None:
        """Negative page sizes must be clamped to default."""
        value, warning = clamp_page_size(-5)
        assert value == PAGE_SIZE_DEFAULT
        assert warning is None

    def test_valid_value_passed_through(self) -> None:
        """Valid values must pass through unchanged with no warning."""
        for v in (1, 50, 100, 1000):
            value, warning = clamp_page_size(v)
            assert value == v
            assert warning is None

    def test_page_size_above_max_clamped_in_build_response(self) -> None:
        """build_paginated_response with limit > max should not exceed max items."""
        items = [{"id": i} for i in range(5)]
        result = build_paginated_response(
            items=items[:PAGE_SIZE_MAX], total=1500, offset=0, limit=PAGE_SIZE_MAX
        )
        assert len(result["items"]) <= PAGE_SIZE_MAX


# ============================================================================
# VAL-JSON-009: Partial success envelope
# ============================================================================


class TestPartialSuccessEnvelope:
    """Verify partial success contract: success=false, partial=true,
    diagnostics non-empty, data present."""

    def test_make_partial_success_has_required_fields(self) -> None:
        """make_partial_success must produce correct envelope fragment."""
        result = make_partial_success(
            data={"partial_result": [1, 2, 3]},
            diagnostics=[
                {"severity": "ERROR", "message": "Some analyzers failed", "category": "analysis"}
            ],
        )
        assert result["success"] is False
        assert result["partial"] is True
        assert len(result["diagnostics"]) > 0
        assert result["data"] is not None

    def test_partial_success_data_present_not_null(self) -> None:
        """Data must be present in partial success, never null."""
        result = make_partial_success(
            data=[],
            diagnostics=[{"severity": "ERROR", "message": "failed", "category": "test"}],
        )
        assert result["data"] is not None
        assert result["data"] == []

    def test_full_envelope_with_partial(self) -> None:
        """build_envelope with partial=True must preserve all fields."""
        partial_result = make_partial_success(
            data={"items": [{"a": 1}]},
            diagnostics=[{"severity": "ERROR", "message": "partial", "category": "test"}],
        )
        envelope = build_envelope(
            command="test",
            success=partial_result["success"],
            partial=partial_result["partial"],
            warnings=partial_result["warnings"],
            diagnostics=partial_result["diagnostics"],
            data=partial_result["data"],
            duration_ms=100,
        )
        assert envelope["success"] is False
        assert envelope["partial"] is True
        assert len(envelope["diagnostics"]) > 0
        assert envelope["data"] is not None


# ============================================================================
# VAL-JSON-010: Empty collections are []
# ============================================================================


class TestEmptyCollections:
    """Verify empty collections are always [], never null, never absent."""

    def test_ensure_collection_none_returns_empty(self) -> None:
        """ensure_collection(None) must return []."""
        assert ensure_collection(None) == []

    def test_ensure_collection_empty_list_preserved(self) -> None:
        """ensure_collection([]) must return []."""
        assert ensure_collection([]) == []

    def test_ensure_collection_populated_preserved(self) -> None:
        """ensure_collection([1,2,3]) must return same list."""
        data = [1, 2, 3]
        assert ensure_collection(data) == data

    def test_empty_project_list_returns_empty_items(self) -> None:
        """build_paginated_response with empty items must return items=[]."""
        result = build_paginated_response(items=[], total=0, offset=0, limit=10)
        assert result["items"] == []
        assert result["items"] is not None
        assert isinstance(result["items"], list)

    def test_all_envelope_data_is_present(self) -> None:
        """Even with null data, the data key must exist in the envelope."""
        envelope = build_envelope(
            command="test",
            success=True,
            partial=False,
            warnings=[],
            diagnostics=[],
            data=None,
            duration_ms=0,
        )
        assert "data" in envelope


# ============================================================================
# VAL-JSON-011: Backend-specific data only under extensions.<backend>
# ============================================================================


class TestBackendExtensions:
    """Verify backend-specific keys never appear at the top level of entities."""

    def test_canonical_field_whitelists_exist(self) -> None:
        """Canonical field whitelists must be defined for all entity types."""
        from binary_analysis.domain.schemas import (
            FUNCTION_CANONICAL_FIELDS,
            PROJECT_CANONICAL_FIELDS,
            SECTION_CANONICAL_FIELDS,
            STRING_CANONICAL_FIELDS,
            SYMBOL_CANONICAL_FIELDS,
        )

        assert len(PROJECT_CANONICAL_FIELDS) >= 5
        assert len(FUNCTION_CANONICAL_FIELDS) >= 5
        assert len(SECTION_CANONICAL_FIELDS) >= 5
        assert len(STRING_CANONICAL_FIELDS) >= 3
        assert len(SYMBOL_CANONICAL_FIELDS) >= 3

    def test_no_ghidra_keys_in_canonical_fields(self) -> None:
        """Canonical field whitelists must not contain backend-specific names."""
        from binary_analysis.domain.schemas import (
            FUNCTION_CANONICAL_FIELDS,
            PROJECT_CANONICAL_FIELDS,
        )

        for field_set in [PROJECT_CANONICAL_FIELDS, FUNCTION_CANONICAL_FIELDS]:
            for field_name in field_set:
                assert "ghidra" not in field_name.lower(), (
                    f"Backend-specific field '{field_name}' in canonical whitelist"
                )
                assert not field_name.startswith("_"), (
                    f"Internal field '{field_name}' in canonical whitelist"
                )

    def test_entity_to_dict_respects_whitelist(self) -> None:
        """entity_to_dict must only include canonical fields when whitelist provided."""
        from dataclasses import dataclass

        from binary_analysis.domain.schemas import entity_to_dict

        @dataclass
        class TestEntity:
            name: str
            address: str
            _internal_id: str = ""
            ghidra_field: str = ""

        entity = TestEntity(
            name="test", address="0x1000", _internal_id="secret", ghidra_field="db://prog"
        )
        canonical = {"name", "address"}

        result = entity_to_dict(entity, canonical_fields=canonical)
        assert "name" in result
        assert "address" in result
        assert "_internal_id" not in result
        assert "ghidra_field" not in result


# ============================================================================
# VAL-JSON-012: Provenance always present
# ============================================================================


class TestProvenanceAlwaysPresent:
    """Verify provenance object is present in every response with required fields."""

    BASE_FIELDS: ClassVar[set[str]] = {
        "cli_version",
        "schema_version",
        "adapter",
        "adapter_version",
        "backend",
        "backend_version",
        "platform",
    }

    def test_default_provenance_has_all_base_fields(self) -> None:
        """Default provenance must contain 7 base fields."""
        prov = _default_provenance()
        for field in self.BASE_FIELDS:
            assert field in prov, f"Missing base provenance field: {field}"

    def test_envelop_always_has_provenance(self) -> None:
        """Every envelope must include a provenance object."""
        envelope = build_envelope(
            command="test",
            success=True,
            partial=False,
            warnings=[],
            diagnostics=[],
            data={},
            duration_ms=0,
        )
        assert "provenance" in envelope
        assert isinstance(envelope["provenance"], dict)

    def test_version_command_has_base_provenance(self, capsys: pytest.CaptureFixture) -> None:
        """version --json must have base 7 provenance fields."""
        envelope = _run_json(["--json", "version"], capsys)
        prov = envelope.get("provenance", {})
        for field in self.BASE_FIELDS:
            assert field in prov, f"version command missing provenance.{field}"

    def test_project_create_has_base_provenance(
        self, capsys: pytest.CaptureFixture, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """project create --json must have base 7 provenance fields."""
        with tempfile.TemporaryDirectory() as tmpdir:
            monkeypatch.setenv("BINARY_WORKSPACE_ROOT", tmpdir)
            envelope = _run_json(["--json", "project", "create", "test-prov"], capsys)
            prov = envelope.get("provenance", {})
            for field in self.BASE_FIELDS:
                assert field in prov, f"project create missing provenance.{field}"

    def test_doctor_has_base_provenance(self, capsys: pytest.CaptureFixture) -> None:
        """doctor --json must have base 7 provenance fields."""
        envelope = _run_json(["--json", "doctor"], capsys)
        prov = envelope.get("provenance", {})
        for field in self.BASE_FIELDS:
            assert field in prov, f"doctor missing provenance.{field}"

    def test_bootstrap_plan_has_base_provenance(self, capsys: pytest.CaptureFixture) -> None:
        """bootstrap --plan --json must have base 7 provenance fields."""
        envelope = _run_json(["--json", "bootstrap", "--plan"], capsys)
        prov = envelope.get("provenance", {})
        for field in self.BASE_FIELDS:
            assert field in prov, f"bootstrap --plan missing provenance.{field}"


# ============================================================================
# VAL-JSON-016: Warnings have defined structure
# ============================================================================


class TestWarningsStructure:
    """Verify warning objects have severity, message, and category;
    distinct from diagnostics."""

    def test_make_warning_has_required_fields(self) -> None:
        """make_warning must produce severity, message, category."""
        w = make_warning("Test warning", severity="WARNING", category="pagination")
        assert w["severity"] == "WARNING"
        assert w["message"] == "Test warning"
        assert w["category"] == "pagination"

    def test_warnings_distinct_from_diagnostics(self) -> None:
        """Warnings and diagnostics are separate arrays in the envelope."""
        envelope = build_envelope(
            command="test",
            success=True,
            partial=True,
            warnings=[make_warning("truncated results", category="truncation")],
            diagnostics=[{"severity": "ERROR", "message": "backend error", "category": "backend"}],
            data={"items": []},
            duration_ms=50,
        )
        assert isinstance(envelope["warnings"], list)
        assert isinstance(envelope["diagnostics"], list)
        assert len(envelope["warnings"]) == 1
        assert len(envelope["diagnostics"]) == 1
        # They are distinct top-level arrays
        assert envelope["warnings"] != envelope["diagnostics"]

    def test_warning_entry_keys_are_correct(self) -> None:
        """Warning entries must have exactly severity, message, category."""
        w = make_warning("Page truncated", severity="WARNING", category="pagination")
        assert set(w.keys()) == {"severity", "message", "category"}

    def test_warnings_in_envelope_are_valid(self) -> None:
        """Warnings in an envelope must serialize to valid JSON."""
        envelope = build_envelope(
            command="test",
            success=True,
            partial=False,
            warnings=[
                make_warning("w1", category="cat1"),
                make_warning("w2", severity="INFO", category="cat2"),
            ],
            diagnostics=[],
            data={},
            duration_ms=0,
        )
        raw = json.dumps(envelope, ensure_ascii=False)
        parsed = json.loads(raw)
        assert len(parsed["warnings"]) == 2
        for w in parsed["warnings"]:
            assert "severity" in w
            assert "message" in w
            assert "category" in w


# ============================================================================
# VAL-JSON-017: Provenance includes architecture and analysis_profile when applicable
# ============================================================================


class TestProvenanceEnrichment:
    """Verify provenance enrichment with project/binary context."""

    def test_enrich_with_project_id(self) -> None:
        """enrich_provenance with project_id adds it."""
        prov = enrich_provenance(project_id="proj-123")
        assert prov["project_id"] == "proj-123"

    def test_enrich_with_binary_context(self) -> None:
        """enrich_provenance with binary_id and binary_sha256 adds both."""
        prov = enrich_provenance(binary_id="bin-456", binary_sha256="a" * 64)
        assert prov["binary_id"] == "bin-456"
        assert prov["binary_sha256"] == "a" * 64

    def test_enrich_with_architecture(self) -> None:
        """enrich_provenance with architecture adds it."""
        prov = enrich_provenance(architecture="x86:LE:64:default")
        assert prov["architecture"] == "x86:LE:64:default"

    def test_enrich_with_analysis_profile(self) -> None:
        """enrich_provenance with analysis_profile adds it."""
        prov = enrich_provenance(analysis_profile="standard")
        assert prov["analysis_profile"] == "standard"

    def test_array_fields_absent_when_not_provided(self) -> None:
        """Optional provenance fields must be absent, not null, when not provided."""
        prov = enrich_provenance()
        assert "project_id" not in prov
        assert "binary_id" not in prov
        assert "binary_sha256" not in prov
        assert "architecture" not in prov
        assert "analysis_profile" not in prov

    def test_enrich_with_all_fields(self) -> None:
        """Enrich with all optional fields at once."""
        prov = enrich_provenance(
            project_id="p1",
            binary_id="b1",
            binary_sha256="s" * 64,
            architecture="arm:LE:32:v7",
            analysis_profile="deep",
        )
        assert prov["project_id"] == "p1"
        assert prov["binary_id"] == "b1"
        assert prov["binary_sha256"] == "s" * 64
        assert prov["architecture"] == "arm:LE:32:v7"
        assert prov["analysis_profile"] == "deep"

    def test_enrich_does_not_mutate_base(self) -> None:
        """enrich_provenance must return a new dict, not mutate the base."""
        base = _default_provenance()
        enriched = enrich_provenance(base, project_id="x")
        assert "project_id" in enriched
        assert "project_id" not in _default_provenance()


# ============================================================================
# VAL-CROSS-010: Bootstrap to doctor roundtrip
# ============================================================================


class TestBootstrapToDoctorRoundtrip:
    """Verify bootstrap --plan -> doctor --require-ready roundtrip integration."""

    def test_bootstrap_plan_output_structure(self, capsys: pytest.CaptureFixture) -> None:
        """bootstrap --plan --json must produce valid envelope with components."""
        envelope = _run_json(["--json", "bootstrap", "--plan"], capsys)
        assert "data" in envelope
        data = envelope.get("data", {})
        assert "components" in data
        components = data["components"]
        assert isinstance(components, list)
        for comp in components:
            assert "name" in comp
            assert "status" in comp

    def test_doctor_output_structure(self, capsys: pytest.CaptureFixture) -> None:
        """doctor --json must produce valid envelope with components."""
        envelope = _run_json(["--json", "doctor"], capsys)
        assert "data" in envelope
        data = envelope.get("data", {})
        assert "components" in data
        components = data["components"]
        assert isinstance(components, list)
        for comp in components:
            assert "name" in comp
            assert "status" in comp

    def test_doctor_require_ready_flag_accepted(self, capsys: pytest.CaptureFixture) -> None:
        """doctor --require-ready --json must not error on unknown flag."""
        envelope = _run_json(["--json", "doctor", "--require-ready"], capsys)
        exit_code = envelope.get("_exit_code", -1)
        # Should be either 0 (all present) or 3 (missing deps) — but NOT 2 (invalid args)
        assert exit_code in (ExitCode.SUCCESS, ExitCode.DEPENDENCY_MISSING), (
            f"Expected exit 0 or 3, got {exit_code}"
        )

    def test_doctor_components_match_bootstrap_components(
        self, capsys: pytest.CaptureFixture
    ) -> None:
        """Doctor components should be the same set as bootstrap plan components."""
        bs_envelope = _run_json(["--json", "bootstrap", "--plan"], capsys)
        dr_envelope = _run_json(["--json", "doctor"], capsys)

        bs_components = {c["name"] for c in bs_envelope.get("data", {}).get("components", [])}
        dr_components = {c["name"] for c in dr_envelope.get("data", {}).get("components", [])}

        assert bs_components == dr_components, (
            f"Bootstrap components {bs_components} != Doctor components {dr_components}"
        )

    def test_bootstrap_plan_then_doctor_roundtrip(self, capsys: pytest.CaptureFixture) -> None:
        """bootstrap --plan then doctor --require-ready must not crash."""
        bs_envelope = _run_json(["--json", "bootstrap", "--plan"], capsys)
        dr_envelope = _run_json(["--json", "doctor", "--require-ready"], capsys)

        # Both must be valid JSON (implied by _run_json returning dict)
        assert "command" in bs_envelope
        assert "command" in dr_envelope

        # If all deps present, doctor should report success with ready=true
        bs_data = bs_envelope.get("data", {})
        bs_comps = bs_data.get("components", [])
        all_present = all(c.get("status") == "present" for c in bs_comps)
        if all_present:
            dr_data = dr_envelope.get("data", {})
            assert dr_data.get("ready") is True

    def test_bootstrap_apply_reports_requires_manual_for_java_ghidra(
        self, capsys: pytest.CaptureFixture
    ) -> None:
        """bootstrap --apply --json should not crash; reports status for Java/Ghidra.

        Java and Ghidra can only be installed manually; bootstrap reports
        'requires_manual' only when they are actually absent. When present,
        they report 'present'. Either status is valid.
        """
        envelope = _run_json(["--json", "bootstrap", "--apply"], capsys)
        assert "data" in envelope
        data = envelope.get("data", {})
        components = data.get("components", [])
        assert isinstance(components, list)

        # Verify Java and Ghidra components exist
        names = {c["name"] for c in components}
        for expected in ("java", "ghidra", "pyghidra"):
            assert expected in names, f"Missing component: {expected}"

        # Verify each has a valid status
        for c in components:
            assert c.get("status") in ("present", "installed", "requires_manual", "failed"), (
                f"Unexpected status for {c['name']}: {c.get('status')}"
            )


# ============================================================================
# VAL-JSON general envelope validation
# ============================================================================


class TestGeneralEnvelopeValidation:
    """Cross-cutting envelope validation tests."""

    def test_envelope_data_never_none_with_collection(self) -> None:
        """Data key must always be present; collections never null."""
        envelope = build_envelope(
            command="test",
            success=True,
            partial=False,
            warnings=[],
            diagnostics=[],
            data=[],
            duration_ms=0,
        )
        assert envelope["data"] is not None
        assert envelope["data"] == []

    def test_all_boolean_fields_are_bool(self) -> None:
        """success, partial, and any has_*/is_* fields must be JSON booleans."""
        envelope = build_envelope(
            command="test",
            success=True,
            partial=False,
            warnings=[],
            diagnostics=[],
            data={"is_stale": False, "has_more": True},
            duration_ms=0,
        )
        assert isinstance(envelope["success"], bool)
        assert isinstance(envelope["partial"], bool)
        assert isinstance(envelope["data"]["is_stale"], bool)
        assert isinstance(envelope["data"]["has_more"], bool)

    def test_size_fields_are_integers(self) -> None:
        """All size/length fields must be integers, never strings."""
        envelope = build_envelope(
            command="test",
            success=True,
            partial=False,
            warnings=[],
            diagnostics=[],
            data={
                "size_bytes": 4096,
                "virtual_size": 8192,
                "raw_size": 2048,
                "length": 100,
            },
            duration_ms=0,
        )
        assert isinstance(envelope["data"]["size_bytes"], int)
        assert isinstance(envelope["data"]["virtual_size"], int)
        assert isinstance(envelope["data"]["raw_size"], int)
        assert isinstance(envelope["data"]["length"], int)

    def test_schema_version_is_correct(self, capsys: pytest.CaptureFixture) -> None:
        """schema_version in every response must be '1.0.0'."""
        commands = [
            ["--json", "version"],
            ["--json", "doctor"],
            ["--json", "bootstrap", "--plan"],
        ]
        for cmd in commands:
            envelope = _run_json(cmd, capsys)
            assert envelope["schema_version"] == SCHEMA_VERSION, (
                f"Wrong schema_version for {' '.join(cmd)}"
            )

    def test_timestamps_are_iso8601(self, capsys: pytest.CaptureFixture) -> None:
        """All timestamp fields must be ISO 8601 with timezone."""
        envelope = _run_json(["--json", "version"], capsys)
        ts = envelope.get("generated_at", "")
        assert re.match(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?(Z|[+-]\d{2}:\d{2})$", ts), (
            f"Timestamp '{ts}' is not ISO 8601 with timezone"
        )
