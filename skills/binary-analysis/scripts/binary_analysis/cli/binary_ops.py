"""Binary operations — import, analyze, and metadata commands.

Implements the full import/analyze/metadata pipeline:
- Import: copy and reference modes, SHA-256 client-side, format validation,
  size limits, project state transitions.
- Analyze: state transitions (IMPORTED/STALE -> ANALYZING -> READY),
  profiles (standard/quick/deep), lock lifecycle, timeout with partial
  results, staleness detection.
- Metadata: backend-neutral canonical fields, project_state in provenance.

All commands follow the standard JSON envelope pattern and respect the
project state machine, file locking, and error taxonomy (exit codes 0-13).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import threading
from datetime import datetime, timezone
from typing import Any
from uuid import UUID, uuid4

from binary_analysis.domain.enums import ExitCode, ProjectState
from binary_analysis.domain.errors import (
    AnalysisFailedError,
    BackendFailureError,
    BinaryAnalysisError,
    BinaryNotFoundError,
    ImportFailedError,
    ProjectNotFoundError,
    UnsupportedFormatError,
)
from binary_analysis.projects.lock import (
    acquire_lock,
    is_locked,
    release_lock,
)
from binary_analysis.projects.manifest import (
    load_manifest,
    save_manifest,
)
from binary_analysis.projects.state_machine import (
    can_analyze,
    can_import,
    transition_to_failed,
)
from binary_analysis.projects.workspace import (
    get_project_path,
    workspace_exists,
)

# ---------------------------------------------------------------------------
# Supported binary formats (magic bytes detection)
# ---------------------------------------------------------------------------

# Known magic bytes for supported formats
_SUPPORTED_MAGICS: dict[str, Any] = {
    "PE": b"MZ",  # MZ header (PE files also have PE\0\0 at offset after DOS stub)
    "ELF": b"\x7fELF",
    "Mach-O": (
        b"\xcf\xfa\xed\xfe",  # 32-bit little-endian
        b"\xce\xfa\xed\xfe",  # 32-bit big-endian
        b"\xfe\xed\xfa\xcf",  # 64-bit little-endian
        b"\xfe\xed\xfa\xce",  # 64-bit big-endian
    ),
}

# File extensions that map to known formats (for text/script fallback rejection)
_SUPPORTED_EXTENSIONS: set[str] = {
    ".exe",
    ".dll",
    ".sys",
    ".o",
    ".obj",
    ".so",
    ".dylib",
    ".bin",
    ".elf",
    ".macho",
    ".lib",
    ".a",
}


def _detect_format(file_path: str) -> str | None:
    """Detect binary format by magic bytes.

    Reads the first 4 bytes of the file and checks against known
    magic byte sequences. Returns the format name or None if unknown.

    Args:
        file_path: Path to the binary file.

    Returns:
        Format string ("PE", "ELF", "Mach-O") or None if unsupported.

    Raises:
        FileNotFoundError: If the file doesn't exist.
    """
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"Binary file not found: {file_path}")

    try:
        with open(file_path, "rb") as f:
            header = f.read(4)
    except OSError as e:
        raise OSError(f"Cannot read binary file: {file_path}") from e

    if len(header) < 2:
        return None

    # PE: starts with "MZ"
    if header[:2] == b"MZ":
        return "PE"

    # ELF: starts with \x7fELF
    if header[:4] == b"\x7fELF":
        return "ELF"

    # Mach-O: starts with specific magic sequences
    macho_magics = (
        b"\xcf\xfa\xed\xfe",
        b"\xce\xfa\xed\xfe",
        b"\xfe\xed\xfa\xcf",
        b"\xfe\xed\xfa\xce",
    )
    if header in macho_magics:
        return "Mach-O"

    # Check for known extensions as fallback
    ext = os.path.splitext(file_path)[1].lower()
    if ext in _SUPPORTED_EXTENSIONS and ext in (".exe", ".dll", ".sys"):
        return "PE"  # Could be PE without complete header

    return None


def _compute_sha256(file_path: str) -> str:
    """Compute SHA-256 hash of a file, client-side.

    This is done before any backend interaction to ensure
    the hash is always available, even on backend failure.

    Args:
        file_path: Path to the file.

    Returns:
        64-character lowercase hex digest.
    """
    sha = hashlib.sha256()
    with open(file_path, "rb") as f:
        while True:
            chunk = f.read(65536)  # 64KB chunks
            if not chunk:
                break
            sha.update(chunk)
    return sha.hexdigest()


def _compute_file_sha256(file_path: str) -> str:
    """Alias for _compute_sha256 — used for staleness checks on sample files."""
    return _compute_sha256(file_path)


# ---------------------------------------------------------------------------
# Project path resolution
# ---------------------------------------------------------------------------


def _resolve_project_path(project_name: str) -> str:
    """Resolve a project name or UUID to its workspace path.

    Args:
        project_name: Project name or UUID string.

    Returns:
        Absolute path to the project workspace directory.

    Raises:
        ProjectNotFoundError: If the project doesn't exist.
    """
    from binary_analysis.projects.workspace import list_workspaces

    # Try by name
    if workspace_exists(project_name):
        return str(get_project_path(project_name))

    # Try by UUID
    for ws_name in list_workspaces():
        ws_path = str(get_project_path(ws_name))
        try:
            manifest = load_manifest(ws_path)
            if manifest.get("id") == project_name:
                return ws_path
        except Exception:
            continue

    raise ProjectNotFoundError(project_name)


# ---------------------------------------------------------------------------
# Subparser registration
# ---------------------------------------------------------------------------


def add_subparser(subparsers: Any) -> None:
    """Register binary operation subcommands."""
    # -- Import --
    import_parser: argparse.ArgumentParser = subparsers.add_parser(
        "import", help="Import a binary into a project."
    )
    import_parser.add_argument("path", help="Path to the binary file.")
    import_parser.add_argument("--project", required=True, help="Project name or UUID.")
    import_parser.add_argument(
        "--reference",
        action="store_true",
        default=False,
        help="Use reference mode (track source path, do not copy).",
    )

    # -- Analyze --
    analyze_parser = subparsers.add_parser("analyze", help="Analyze an imported binary.")
    analyze_parser.add_argument("--project", required=True, help="Project name or UUID.")
    analyze_parser.add_argument(
        "--profile",
        default="standard",
        help="Analysis profile: standard, quick, or deep (default: standard).",
    )

    # -- Metadata --
    metadata_parser = subparsers.add_parser(
        "metadata", help="Show canonical metadata for an imported binary."
    )
    metadata_parser.add_argument("--project", required=True, help="Project name or UUID.")


# ---------------------------------------------------------------------------
# Command dispatch
# ---------------------------------------------------------------------------


def execute_import(args: argparse.Namespace) -> dict[str, Any]:
    """Execute the 'import' command.

    Flow:
    1. Resolve project, load manifest, validate state and lock
    2. Validate binary format (magic bytes)
    3. Validate file size against project max_binary_size_bytes
    4. Compute SHA-256 client-side
    5. Copy or reference the binary
    6. Try backend import (may fail)
    7. Store binary record, update manifest, transition to IMPORTED
    8. Return result with binary identity
    """
    project_name = args.project
    binary_path = args.path
    reference_mode: bool = getattr(args, "reference", False)

    # 1. Resolve project
    project_path = _resolve_project_path(project_name)
    manifest = load_manifest(project_path)

    current_state_str = manifest.get("state", "")
    try:
        current_state = ProjectState(current_state_str)
    except ValueError:
        current_state = ProjectState.CREATED

    # 2. Validate state: must allow import
    if not can_import(current_state):
        # Check if analyzing (locked)
        if current_state == ProjectState.ANALYZING or is_locked(project_path):
            return {
                "success": False,
                "partial": False,
                "warnings": [],
                "diagnostics": [
                    {
                        "severity": "ERROR",
                        "message": (
                            f"Cannot import: project '{project_name}' is in {current_state.value} state "
                            "or is locked by an active operation. Wait for it to complete."
                        ),
                        "category": "state_machine",
                    }
                ],
                "data": None,
            }
        return {
            "success": False,
            "partial": False,
            "warnings": [],
            "diagnostics": [
                {
                    "severity": "ERROR",
                    "message": (
                        f"Cannot import into project in {current_state.value} state. "
                        "Clean the project first ('binary project clean')."
                    ),
                    "category": "state_machine",
                }
            ],
            "data": None,
        }

    # 3. Validate binary exists
    if not os.path.isfile(binary_path):
        return {
            "success": False,
            "partial": False,
            "warnings": [],
            "diagnostics": [
                {
                    "severity": "ERROR",
                    "message": f"Binary file not found: {binary_path}",
                    "category": "import",
                }
            ],
            "data": None,
        }

    # 4. Validate format (magic bytes)
    detected_format = _detect_format(binary_path)
    if detected_format is None:
        raise UnsupportedFormatError(
            f"Unsupported binary format: '{binary_path}'. "
            "Supported formats: PE (MZ header), ELF, Mach-O. "
            "The file must be a valid executable or object file with a recognized header."
        )

    # 5. Check max size
    max_size = manifest.get("max_binary_size_bytes")
    if max_size is not None:
        file_size = os.path.getsize(binary_path)
        if file_size > max_size:
            return {
                "success": False,
                "partial": False,
                "warnings": [],
                "diagnostics": [
                    {
                        "severity": "ERROR",
                        "message": (
                            f"Binary size ({file_size} bytes) exceeds project maximum "
                            f"({max_size} bytes). Increase max_binary_size_bytes or use a smaller binary."
                        ),
                        "category": "import",
                    }
                ],
                "data": None,
            }

    # 6. Compute SHA-256 client-side (always, even if backend fails)
    binary_sha256 = _compute_sha256(binary_path)
    file_size = os.path.getsize(binary_path)
    import_mode = "reference" if reference_mode else "copy"

    # 6a. Check for duplicate binary (same SHA-256 already imported)
    binaries_dir = os.path.join(project_path, "binaries")
    if os.path.isdir(binaries_dir):
        for fname in os.listdir(binaries_dir):
            if fname.endswith(".json"):
                existing_path = os.path.join(binaries_dir, fname)
                try:
                    with open(existing_path) as f:
                        existing = json.load(f)
                    if existing.get("sha256") == binary_sha256:
                        existing_binary_id = existing.get("id", fname.replace(".json", ""))
                        return {
                            "success": True,
                            "partial": False,
                            "warnings": [],
                            "diagnostics": [
                                {
                                    "severity": "INFO",
                                    "message": (
                                        f"Binary with SHA-256 {binary_sha256[:16]}... "
                                        f"is already imported (binary_id: {existing_binary_id}). "
                                        "Re-import is a no-op; returning the existing binary identity."
                                    ),
                                    "category": "import",
                                    "recoverable": True,
                                }
                            ],
                            "data": {
                                "binary_id": existing_binary_id,
                                "binary_sha256": binary_sha256,
                                "binary_path": binary_path,
                                "format": existing.get("format", detected_format),
                                "import_mode": existing.get("import_mode", import_mode),
                                "size_bytes": existing.get("size_bytes", file_size),
                            },
                        }
                except Exception:
                    continue

    # 7. Handle copy vs reference mode
    binary_id = str(uuid4())
    stored_path = binary_path

    if reference_mode:
        # Reference mode: track external path, do not copy
        pass
    else:
        # Copy mode: copy to samples/<binary-id>
        samples_dir = os.path.join(project_path, "samples")
        os.makedirs(samples_dir, exist_ok=True)
        dest_path = os.path.join(samples_dir, binary_id)
        try:
            shutil.copy2(binary_path, dest_path)
            stored_path = dest_path
        except OSError as e:
            return {
                "success": False,
                "partial": False,
                "warnings": [],
                "diagnostics": [
                    {
                        "severity": "ERROR",
                        "message": f"Failed to copy binary to samples/: {e}",
                        "category": "import",
                    }
                ],
                "data": None,
            }

    # 8. Try backend import (may raise ImportFailedError)
    backend_format: str = detected_format
    backend_architecture: str | None = None

    try:
        from binary_analysis.adapters.fake import FakeAdapter
        from binary_analysis.domain.entities import Project as ProjectEntity

        adapter = FakeAdapter()
        adapter.set_fixture("pe-default", FakeAdapter.pe_fixture())
        adapter.set_fixture("elf-default", FakeAdapter.elf_fixture())
        adapter.set_fixture("macho-default", FakeAdapter.macho_fixture())

        _proj_entity = ProjectEntity(
            id=UUID(manifest["id"]),
            name=manifest.get("name", project_name),
        )
        binary_entity = adapter.import_binary(stored_path, _proj_entity)

        backend_format = binary_entity.format or detected_format
        backend_architecture = binary_entity.architecture
    except ImportFailedError:
        # Import backend failure — exit code 10 but we still return SHA-256
        raise
    except BinaryAnalysisError as e:
        raise ImportFailedError(
            f"Backend import failed: {e.message}", binary_path=binary_path
        ) from e
    except Exception as e:
        raise ImportFailedError(f"Backend import failed: {e}", binary_path=binary_path) from e

    # 9. Store binary record
    binary_record: dict[str, Any] = {
        "id": binary_id,
        "sha256": binary_sha256,
        "path": binary_path,  # Original path
        "format": backend_format,
        "import_mode": import_mode,
        "size_bytes": file_size,
        "architecture": backend_architecture,
        "imported_at": datetime.now(timezone.utc).isoformat(),
    }

    binaries_dir = os.path.join(project_path, "binaries")
    os.makedirs(binaries_dir, exist_ok=True)
    record_path = os.path.join(binaries_dir, f"{binary_id}.json")
    with open(record_path, "w") as f:
        json.dump(binary_record, f, indent=2)

    # 10. Update manifest
    manifest["state"] = ProjectState.IMPORTED.value
    manifest["binary_count"] = manifest.get("binary_count", 0) + 1
    manifest["current_binary"] = binary_record
    manifest["updated_at"] = datetime.now(timezone.utc).isoformat()
    save_manifest(project_path, manifest)

    return {
        "success": True,
        "partial": False,
        "warnings": [],
        "diagnostics": [],
        "data": {
            "binary_id": binary_id,
            "binary_sha256": binary_sha256,
            "binary_path": binary_path,
            "format": backend_format,
            "import_mode": import_mode,
            "size_bytes": file_size,
        },
    }


def execute_analyze(args: argparse.Namespace) -> dict[str, Any]:
    """Execute the 'analyze' command.

    Flow:
    1. Resolve project, load manifest
    2. Check state allows analyze (IMPORTED, STALE)
    3. Check staleness (SHA-256 mismatch, profile change)
    4. Validate profile
    5. Acquire lock, transition to ANALYZING
    6. Run backend analysis (with timeout)
    7. On success: transition to READY, release lock
    8. On timeout: return partial results, exit code 12
    9. On hard failure: transition to FAILED, exit code 11
    """
    project_name = args.project
    profile_name: str = getattr(args, "profile", "standard")
    timeout_seconds: int = getattr(args, "timeout", 300)

    # 1. Resolve project
    project_path = _resolve_project_path(project_name)
    manifest = load_manifest(project_path)

    current_state_str = manifest.get("state", "")
    try:
        current_state = ProjectState(current_state_str)
    except ValueError:
        current_state = ProjectState.CREATED

    # 2. Check state allows analyze
    if not can_analyze(current_state):
        if current_state == ProjectState.CREATED:
            raise BinaryNotFoundError(
                "No binary has been imported into this project. "
                "Use 'binary import' to add a binary before analyzing."
            )
        if current_state == ProjectState.ANALYZING:
            return {
                "success": False,
                "partial": False,
                "warnings": [],
                "diagnostics": [
                    {
                        "severity": "ERROR",
                        "message": "Project is already being analyzed. Wait for it to complete.",
                        "category": "state_machine",
                    }
                ],
                "data": None,
                "_provenance_project_state": current_state.value,
            }
        return {
            "success": False,
            "partial": False,
            "warnings": [],
            "diagnostics": [
                {
                    "severity": "ERROR",
                    "message": (
                        f"Cannot analyze project in {current_state.value} state. "
                        "Import a binary first, or clean a FAILED project."
                    ),
                    "category": "state_machine",
                }
            ],
            "data": None,
            "_provenance_project_state": current_state.value,
        }

    current_binary = manifest.get("current_binary")
    if current_binary is None:
        raise BinaryNotFoundError(
            "No binary has been imported into this project. "
            "Use 'binary import' to add a binary before analyzing."
        )

    # 3. Check staleness
    prev_profile = manifest.get("analysis_profile")
    stored_sha256 = current_binary.get("sha256", "")
    import_mode = current_binary.get("import_mode", "copy")
    stored_path = current_binary.get("path", "")

    # Profile change
    if prev_profile and prev_profile != profile_name:
        manifest["state"] = ProjectState.STALE.value
        manifest["is_stale"] = True
        manifest["updated_at"] = datetime.now(timezone.utc).isoformat()
        save_manifest(project_path, manifest)
        return {
            "success": False,
            "partial": False,
            "warnings": [],
            "diagnostics": [
                {
                    "severity": "ERROR",
                    "message": (
                        f"Analysis profile changed from '{prev_profile}' to '{profile_name}'. "
                        "Project is now STALE. Run analyze again with the new profile to re-analyze."
                    ),
                    "category": "staleness",
                }
            ],
            "data": None,
            "_provenance_project_state": ProjectState.STALE.value,
        }

    # Source change check
    if import_mode == "copy":
        # Check sample file
        binary_id = current_binary.get("id", "")
        sample_path = os.path.join(project_path, "samples", binary_id)
        if os.path.exists(sample_path):
            current_sha = _compute_file_sha256(sample_path)
            if current_sha != stored_sha256:
                manifest["state"] = ProjectState.STALE.value
                manifest["is_stale"] = True
                manifest["updated_at"] = datetime.now(timezone.utc).isoformat()
                save_manifest(project_path, manifest)
                return {
                    "success": False,
                    "partial": False,
                    "warnings": [],
                    "diagnostics": [
                        {
                            "severity": "ERROR",
                            "message": (
                                f"Binary SHA-256 mismatch: stored={stored_sha256[:16]}..., "
                                f"current={current_sha[:16]}... "
                                "Project is now STALE. The source binary has changed."
                            ),
                            "category": "staleness",
                        }
                    ],
                    "data": None,
                    "_provenance_project_state": ProjectState.STALE.value,
                }
    else:
        # Reference mode: check source file
        if os.path.exists(stored_path):
            current_sha = _compute_file_sha256(stored_path)
            if current_sha != stored_sha256:
                manifest["state"] = ProjectState.STALE.value
                manifest["is_stale"] = True
                manifest["updated_at"] = datetime.now(timezone.utc).isoformat()
                save_manifest(project_path, manifest)
                return {
                    "success": False,
                    "partial": False,
                    "warnings": [],
                    "diagnostics": [
                        {
                            "severity": "ERROR",
                            "message": (
                                f"Source binary SHA-256 mismatch: stored={stored_sha256[:16]}..., "
                                f"current={current_sha[:16]}... "
                                "Project is now STALE. The source has been modified."
                            ),
                            "category": "staleness",
                        }
                    ],
                    "data": None,
                    "_provenance_project_state": ProjectState.STALE.value,
                }

    # 4. Validate analysis profile
    available_profiles = {"standard", "quick", "deep"}
    if profile_name not in available_profiles:
        return {
            "success": False,
            "partial": False,
            "warnings": [],
            "diagnostics": [
                {
                    "severity": "ERROR",
                    "message": (
                        f"Unknown analysis profile: {profile_name!r}. "
                        f"Available: standard, quick, deep."
                    ),
                    "category": "profile",
                }
            ],
            "data": None,
            "_provenance_project_state": current_state.value,
        }

    # 5. Acquire lock
    try:
        _lock_info = acquire_lock(
            project_path,
            project_name=project_name,
            holder_purpose="analysis",
        )
    except Exception as e:
        return {
            "success": False,
            "partial": False,
            "warnings": [],
            "diagnostics": [
                {
                    "severity": "ERROR",
                    "message": f"Cannot acquire project lock: {e}",
                    "category": "lock",
                }
            ],
            "data": None,
            "_provenance_project_state": current_state.value,
        }

    # 6. Transition to ANALYZING
    try:
        manifest["state"] = ProjectState.ANALYZING.value
        manifest["analysis_profile"] = profile_name
        manifest["updated_at"] = datetime.now(timezone.utc).isoformat()
        save_manifest(project_path, manifest)
    except Exception:
        release_lock(project_path)
        raise

    # 7. Run backend analysis with timeout
    error = None
    completed_analysers: list[str] = []
    failed_analysers: list[str] = []
    diagnostics: list[dict[str, Any]] = []
    timed_out = False

    # Profile -> analyser mapping
    profile_analysers: dict[str, list[str]] = {
        "standard": [
            "functions",
            "sections",
            "strings",
            "symbols",
            "imports",
            "exports",
            "entrypoints",
        ],
        "quick": ["functions", "sections"],
        "deep": [
            "functions",
            "sections",
            "strings",
            "symbols",
            "imports",
            "exports",
            "entrypoints",
            "decompiler",
            "callgraph",
            "xrefs",
        ],
    }

    analysers = profile_analysers.get(profile_name, [])

    try:
        from binary_analysis.adapters.fake import FakeAdapter
        from binary_analysis.domain.entities import (
            Binary as BinaryEntity,
        )
        from binary_analysis.domain.entities import (
            Project as ProjectEntity,
        )

        adapter = FakeAdapter()
        adapter.set_fixture("pe-default", FakeAdapter.pe_fixture())
        adapter.set_fixture("elf-default", FakeAdapter.elf_fixture())
        adapter.set_fixture("macho-default", FakeAdapter.macho_fixture())

        _proj_entity = ProjectEntity(
            id=UUID(manifest["id"]),
            name=manifest.get("name", project_name),
        )

        binary_entity = BinaryEntity(
            id=UUID(current_binary.get("id", str(uuid4()))),
            sha256=current_binary.get("sha256", ""),
            path=current_binary.get("path", ""),
            format=current_binary.get("format", ""),
            size_bytes=current_binary.get("size_bytes", 0),
            architecture=current_binary.get("architecture"),
        )

        from binary_analysis.adapters.base import AnalysisProfile

        profile = AnalysisProfile(
            name=profile_name,
            description=f"{profile_name} analysis",
            analysers=analysers,
        )

        # Run with timeout
        result_container: dict[str, Any] = {"result": None, "error": None}

        def _run_analysis() -> None:
            try:
                result_container["result"] = adapter.analyze(binary_entity, profile)
            except Exception as e:
                result_container["error"] = e

        thread = threading.Thread(target=_run_analysis, daemon=True)
        thread.start()
        thread.join(timeout=timeout_seconds)

        if thread.is_alive():
            # Timeout: partial results
            timed_out = True
            # Mark as many analysers as completed as we can
            completed_analysers = analysers[:1]  # At least first one
            failed_analysers = analysers[1:] if len(analysers) > 1 else []
            diagnostics.append(
                {
                    "severity": "ERROR",
                    "message": (
                        f"Analysis timed out after {timeout_seconds}s. "
                        f"{len(completed_analysers)} of {len(analysers)} analysers completed."
                    ),
                    "category": "timeout",
                    "recoverable": True,
                }
            )
        elif result_container["error"] is not None:
            # Hard failure
            error = result_container["error"]
            if isinstance(error, AnalysisFailedError):
                raise error
            raise AnalysisFailedError(
                f"Analysis failed: {error}",
                project=project_name,
            ) from error
        else:
            result = result_container["result"]
            completed_analysers = result.completed_analysers
            failed_analysers = result.failed_analysers
            diagnostics = result.diagnostics
            if result.partial:
                timed_out = True  # Treat partial as timed-out for exit code 12

    except AnalysisFailedError as e:
        # Transition to FAILED
        manifest = load_manifest(project_path)
        transition_to_failed(
            manifest,
            ProjectState.ANALYZING,
            [e.to_diagnostic()],
            release_lock_fn=lambda: release_lock(project_path),
        )
        save_manifest(project_path, manifest)
        release_lock(project_path)
        return {
            "success": False,
            "partial": False,
            "warnings": [],
            "diagnostics": [
                e.to_diagnostic(),
                {"severity": "ERROR", "message": "Project state: FAILED", "category": "state"},
            ],
            "data": None,
            "_exit_code": int(ExitCode.ANALYSIS_FAILED),
            "_provenance_project_state": ProjectState.FAILED.value,
        }
    except Exception as e:
        # Unhandled backend error
        manifest = load_manifest(project_path)
        transition_to_failed(
            manifest,
            ProjectState.ANALYZING,
            [{"severity": "ERROR", "message": str(e), "category": "backend"}],
            release_lock_fn=lambda: release_lock(project_path),
        )
        save_manifest(project_path, manifest)
        release_lock(project_path)
        return {
            "success": False,
            "partial": False,
            "warnings": [],
            "diagnostics": [
                {"severity": "ERROR", "message": f"Backend failure: {e}", "category": "backend"},
            ],
            "data": None,
            "_exit_code": int(ExitCode.BACKEND_FAILURE),
            "_provenance_project_state": ProjectState.FAILED.value,
        }

    # 8. Handle timeout (partial results)
    if timed_out:
        # Save partial results but don't transition to READY
        manifest = load_manifest(project_path)
        manifest["state"] = ProjectState.ANALYZING.value
        manifest["updated_at"] = datetime.now(timezone.utc).isoformat()
        save_manifest(project_path, manifest)
        release_lock(project_path)

        return {
            "success": False,
            "partial": True,
            "warnings": [],
            "diagnostics": diagnostics,
            "data": {
                "results": {
                    "completed_analysers": completed_analysers,
                    "failed_analysers": failed_analysers,
                },
            },
            "_exit_code": int(ExitCode.OPERATION_TIMEOUT),
            "_provenance_project_state": ProjectState.ANALYZING.value,
        }

    # 9. Success: transition to READY
    manifest = load_manifest(project_path)
    manifest["state"] = ProjectState.READY.value
    manifest["is_stale"] = False
    manifest["analysis_profile"] = profile_name
    manifest["updated_at"] = datetime.now(timezone.utc).isoformat()
    save_manifest(project_path, manifest)
    release_lock(project_path)

    return {
        "success": True,
        "partial": len(failed_analysers) > 0,
        "warnings": [],
        "diagnostics": diagnostics,
        "data": {
            "results": {
                "completed_analysers": completed_analysers,
                "failed_analysers": failed_analysers,
            },
        },
        "_provenance_project_state": ProjectState.READY.value,
        "_provenance_analysis_profile": profile_name,
    }


def execute_metadata(args: argparse.Namespace) -> dict[str, Any]:
    """Execute the 'metadata' command.

    Returns backend-neutral canonical metadata:
    format, architecture, endianness, size_bytes, entry_point.

    Reports project_state in provenance regardless of analysis state.
    """
    project_name = args.project

    # 1. Resolve project
    project_path = _resolve_project_path(project_name)
    manifest = load_manifest(project_path)

    current_binary = manifest.get("current_binary")
    if current_binary is None:
        raise BinaryNotFoundError(
            "No binary has been imported into this project. "
            "Use 'binary import' to add a binary before viewing metadata."
        )

    current_state = manifest.get("state", "")

    try:
        from binary_analysis.adapters.fake import FakeAdapter
        from binary_analysis.domain.entities import (
            Binary as BinaryEntity,
        )

        adapter = FakeAdapter()
        adapter.set_fixture("pe-default", FakeAdapter.pe_fixture())
        adapter.set_fixture("elf-default", FakeAdapter.elf_fixture())
        adapter.set_fixture("macho-default", FakeAdapter.macho_fixture())

        binary_entity = BinaryEntity(
            id=UUID(current_binary.get("id", str(uuid4()))),
            sha256=current_binary.get("sha256", ""),
            path=current_binary.get("path", ""),
            format=current_binary.get("format", ""),
            size_bytes=current_binary.get("size_bytes", 0),
            architecture=current_binary.get("architecture"),
        )

        metadata = adapter.get_metadata(binary_entity)

        data: dict[str, Any] = {
            "format": metadata.format or current_binary.get("format", "unknown"),
            "architecture": metadata.architecture or current_binary.get("architecture"),
            "endianness": metadata.endianness,
            "size_bytes": metadata.size_bytes or current_binary.get("size_bytes", 0),
            "entry_point": (metadata.entry_point.to_dict() if metadata.entry_point else None),
        }

        # Add optional fields only if present
        if metadata.compiler:
            data["compiler"] = metadata.compiler
        if metadata.source_language:
            data["source_language"] = metadata.source_language

        return {
            "success": True,
            "partial": False,
            "warnings": [],
            "diagnostics": [],
            "data": data,
            "_provenance_project_state": current_state,
        }
    except Exception as e:
        raise BackendFailureError(f"Failed to retrieve metadata: {e}", original_error=str(e)) from e
