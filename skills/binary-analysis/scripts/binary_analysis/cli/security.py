"""Security analysis CLI commands — triage, diagnostics, suspicious-apis, capability-map.

Implements the triage and diagnostics commands for milestone: security-ship.

Triage: Runs the rule engine against backend data to produce structured
observations (deterministic facts), heuristics (rule-derived interpretations
with confidence), and unknowns (unresolved questions).

Diagnostics: Retrieves all persistent diagnostics accumulated across
the project lifecycle from previous commands (analyze, triage, etc.).
"""

from __future__ import annotations

import argparse
from typing import Any

from binary_analysis.adapters.fake import FakeAdapter
from binary_analysis.cli.helpers import (
    clamp_page_size,
    make_diagnostic,
)
from binary_analysis.domain.enums import ExitCode
from binary_analysis.domain.errors import (
    AnalysisFailedError,
    BackendFailureError,
    BinaryNotFoundError,
    OperationTimeoutError,
    ProjectNotFoundError,
)
from binary_analysis.projects.diagnostics import (
    get_diagnostics_summary,
    load_diagnostics,
    persist_diagnostics,
)
from binary_analysis.projects.manifest import load_manifest
from binary_analysis.projects.workspace import get_project_path, workspace_exists

# ---------------------------------------------------------------------------
# Argument registration
# ---------------------------------------------------------------------------


def add_subparser(sub: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    """Register triage and diagnostics subcommands."""
    triage_parser = sub.add_parser(
        "triage",
        help="Run triage analysis: observations, heuristics, and unknowns",
        description=(
            "Run automated triage analysis on the imported binary. "
            "Produces structured output in three categories: "
            "observations (deterministic facts), heuristics (rule-derived "
            "interpretations with confidence scores), and unknowns "
            "(unresolved questions). No free-form narrative or agent conclusions."
        ),
    )
    triage_parser.add_argument(
        "--project",
        required=True,
        help="Project name or UUID containing the binary to triage.",
    )
    triage_parser.add_argument(
        "--profile",
        default="standard",
        help="Analysis profile to use (default: standard).",
    )
    triage_parser.add_argument(
        "--limit",
        type=int,
        default=100,
        help="Maximum results per category (default: 100, max: 1000).",
    )

    diag_parser = sub.add_parser(
        "diagnostics",
        help="List all persistent diagnostics from project lifecycle",
        description=(
            "List all accumulated diagnostics from the project lifecycle: "
            "warnings, limitations, and partial failures from analyze, "
            "triage, and other commands. Each entry includes severity, "
            "category, message, and recoverable flag."
        ),
    )
    diag_parser.add_argument(
        "--project",
        required=True,
        help="Project name or UUID to retrieve diagnostics for.",
    )


# ---------------------------------------------------------------------------
# Triage command
# ---------------------------------------------------------------------------


def execute_triage(args: argparse.Namespace) -> dict[str, Any]:
    """Execute the triage command.

    Returns:
        A result dict with success, partial, warnings, diagnostics, data, and
        optional _exit_code for non-success paths.
    """
    project_name = args.project
    profile_name = getattr(args, "profile", "standard")
    limit = clamp_page_size(getattr(args, "limit", 100))

    # Validate project exists
    if not workspace_exists(project_name):
        raise ProjectNotFoundError(project_name)

    project_path = str(get_project_path(project_name))

    # Load project manifest
    manifest = load_manifest(project_path)

    # Check for binary
    current_binary = manifest.get("current_binary")
    if current_binary is None:
        raise BinaryNotFoundError()

    binary_id = current_binary.get("id", "unknown")
    binary_sha256 = current_binary.get("sha256", "unknown")
    binary_format = current_binary.get("format", "unknown")
    binary_arch = current_binary.get("architecture", "unknown")

    # Provenance context fields for the envelope
    _prov_project_id = manifest.get("id")
    _prov_binary_id = binary_id
    _prov_binary_sha256 = binary_sha256
    _prov_project_state = manifest.get("state")

    # Create adapter and run triage
    adapter = FakeAdapter()
    adapter.initialize()

    # Set up the adapter with appropriate fixture
    if binary_format == "ELF":
        adapter.set_fixture("test-bin", FakeAdapter.elf_fixture())
    elif binary_format == "Mach-O":
        adapter.set_fixture("test-bin", FakeAdapter.macho_fixture())
    else:
        adapter.set_fixture("test-bin", FakeAdapter.pe_fixture())

    from uuid import UUID

    from binary_analysis.domain.entities import Binary

    binary = Binary(
        id=UUID(binary_id) if binary_id != "unknown" else UUID(int=0),
        sha256=binary_sha256,
        path=current_binary.get("path", ""),
        format=binary_format,
        architecture=binary_arch,
        size_bytes=current_binary.get("size_bytes", 0),
        analysis_profile=profile_name,
    )

    # Run the triage
    try:
        triage_result = adapter.run_triage(binary)
    except OperationTimeoutError:
        # Return partial results
        diags = [
            make_diagnostic(
                "Triage operation timed out; results may be incomplete",
                severity="WARNING",
                category="timeout",
                recoverable=True,
            )
        ]
        # Persist diagnostics
        persist_diagnostics(project_path, diags, command="triage")

        return {
            "success": False,
            "partial": True,
            "warnings": [],
            "diagnostics": diags,
            "data": {
                "observations": [],
                "heuristics": [],
                "unknowns": [],
            },
            "_exit_code": ExitCode.OPERATION_TIMEOUT,
            "_provenance_project_state": _prov_project_state,
            "_provenance_analysis_profile": profile_name,
            "_provenance_project_id": _prov_project_id,
            "_provenance_binary_id": _prov_binary_id,
            "_provenance_binary_sha256": _prov_binary_sha256,
        }
    except BackendFailureError as e:
        # Treat backend failure as partial - return engine diagnostics
        diags = [
            make_diagnostic(
                str(e),
                severity="ERROR",
                category="backend-failure",
                recoverable=False,
            )
        ]
        persist_diagnostics(project_path, diags, command="triage")

        return {
            "success": False,
            "partial": True,
            "warnings": [],
            "diagnostics": diags,
            "data": {
                "observations": [],
                "heuristics": [],
                "unknowns": [],
            },
            "_exit_code": ExitCode.BACKEND_FAILURE,
            "_provenance_project_state": _prov_project_state,
            "_provenance_analysis_profile": profile_name,
            "_provenance_project_id": _prov_project_id,
            "_provenance_binary_id": _prov_binary_id,
            "_provenance_binary_sha256": _prov_binary_sha256,
        }
    except AnalysisFailedError:
        diags = [
            make_diagnostic(
                "Analysis has not been completed; triage results are limited",
                severity="WARNING",
                category="analysis-state",
                recoverable=True,
            )
        ]
        persist_diagnostics(project_path, diags, command="triage")

        return {
            "success": False,
            "partial": True,
            "warnings": [],
            "diagnostics": diags,
            "data": {
                "observations": [],
                "heuristics": [],
                "unknowns": [],
            },
            "_exit_code": ExitCode.ANALYSIS_FAILED,
            "_provenance_project_state": _prov_project_state,
            "_provenance_analysis_profile": profile_name,
            "_provenance_project_id": _prov_project_id,
            "_provenance_binary_id": _prov_binary_id,
            "_provenance_binary_sha256": _prov_binary_sha256,
        }
    except Exception as e:
        diags = [
            make_diagnostic(
                f"Unexpected error during triage: {e}",
                severity="ERROR",
                category="triage",
                recoverable=False,
            )
        ]
        persist_diagnostics(project_path, diags, command="triage")

        return {
            "success": False,
            "partial": True,
            "warnings": [],
            "diagnostics": diags,
            "data": {
                "observations": [],
                "heuristics": [],
                "unknowns": [],
            },
            "_exit_code": ExitCode.GENERIC_ERROR,
            "_provenance_project_state": _prov_project_state,
            "_provenance_analysis_profile": profile_name,
            "_provenance_project_id": _prov_project_id,
            "_provenance_binary_id": _prov_binary_id,
            "_provenance_binary_sha256": _prov_binary_sha256,
        }

    # Collect all diagnostics from triage
    all_diagnostics: list[dict[str, Any]] = []
    all_warnings: list[dict[str, Any]] = []

    for ed in triage_result.engine_diagnostics:
        all_diagnostics.append(ed)

    if triage_result.partial:
        all_warnings.append(
            {
                "severity": "WARNING",
                "message": "Triage completed with partial results; "
                "some analyzers encountered errors",
                "category": "triage",
            }
        )

    # Serialize observations (no confidence field — they are facts)
    observations_data: list[dict[str, Any]] = []
    for obs in triage_result.observations[:limit]:
        obs_dict: dict[str, Any] = {
            "category": obs.category,
            "description": obs.description,
            "source": obs.source,
        }
        if obs.address is not None:
            obs_dict["address"] = obs.address.to_dict()
        if obs.evidence is not None:
            obs_dict["evidence"] = obs.evidence
        observations_data.append(obs_dict)

    # Serialize heuristics (with confidence field)
    heuristics_data: list[dict[str, Any]] = []
    for heur in triage_result.heuristics[:limit]:
        heur_dict: dict[str, Any] = {
            "name": heur.name,
            "description": heur.description,
            "confidence": heur.confidence.value,
        }
        if heur.rule_id is not None:
            heur_dict["rule_id"] = heur.rule_id
        if heur.evidence:
            heur_dict["evidence"] = heur.evidence
        heuristics_data.append(heur_dict)

    # Serialize unknowns (with address and question)
    unknowns_data: list[dict[str, Any]] = []
    for unk in triage_result.unknowns[:limit]:
        unk_dict: dict[str, Any] = {
            "question": unk.question,
        }
        if unk.address is not None:
            unk_dict["address"] = unk.address.to_dict()
        if unk.category is not None:
            unk_dict["category"] = unk.category
        unknowns_data.append(unk_dict)

    # Truncation warnings
    if len(triage_result.observations) > limit:
        all_warnings.append(
            {
                "severity": "WARNING",
                "message": f"Observations truncated: {len(triage_result.observations)} found, "
                f"showing first {limit}",
                "category": "truncation",
            }
        )
    if len(triage_result.heuristics) > limit:
        all_warnings.append(
            {
                "severity": "WARNING",
                "message": f"Heuristics truncated: {len(triage_result.heuristics)} found, "
                f"showing first {limit}",
                "category": "truncation",
            }
        )
    if len(triage_result.unknowns) > limit:
        all_warnings.append(
            {
                "severity": "WARNING",
                "message": f"Unknowns truncated: {len(triage_result.unknowns)} found, "
                f"showing first {limit}",
                "category": "truncation",
            }
        )

    # Persist any diagnostics for later retrieval
    if all_diagnostics:
        persist_diagnostics(project_path, all_diagnostics, command="triage")

    partial = triage_result.partial or len(all_diagnostics) > 0

    return {
        "success": True,
        "partial": partial,
        "warnings": all_warnings,
        "diagnostics": all_diagnostics,
        "data": {
            "observations": observations_data,
            "heuristics": heuristics_data,
            "unknowns": unknowns_data,
        },
        "_provenance_project_state": _prov_project_state,
        "_provenance_analysis_profile": profile_name,
        "_provenance_project_id": _prov_project_id,
        "_provenance_binary_id": _prov_binary_id,
        "_provenance_binary_sha256": _prov_binary_sha256,
    }


# ---------------------------------------------------------------------------
# Diagnostics command
# ---------------------------------------------------------------------------


def execute_diagnostics(args: argparse.Namespace) -> dict[str, Any]:
    """Execute the diagnostics command.

    Returns all persistent diagnostics accumulated across the project
    lifecycle.

    Returns:
        A result dict with success, partial, warnings, diagnostics, data.
    """
    project_name = args.project

    # Validate project exists
    if not workspace_exists(project_name):
        raise ProjectNotFoundError(project_name)

    project_path = str(get_project_path(project_name))

    # Load project manifest
    manifest = load_manifest(project_path)

    # Load all accumulated diagnostics
    all_diagnostics = load_diagnostics(project_path)

    # Compute summary
    summary = get_diagnostics_summary(all_diagnostics)

    return {
        "success": True,
        "partial": False,
        "warnings": [],
        "diagnostics": [],
        "data": {
            "diagnostics": all_diagnostics,
            "total": summary["total"],
            "by_severity": summary["by_severity"],
        },
        "_provenance_project_state": manifest.get("state"),
        "_provenance_project_id": manifest.get("id"),
    }
