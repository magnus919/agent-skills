"""Shared CLI helpers for pagination, warnings, diagnostics, and provenance.

These helpers are used across CLI modules without creating circular imports.
"""

from __future__ import annotations

import json
import platform as _platform
import sys
from typing import Any

from binary_analysis import __version__ as _cli_version

# ---------------------------------------------------------------------------
# Constants (matching main.py)
# ---------------------------------------------------------------------------

SCHEMA_VERSION = "1.0.0"
PAGE_SIZE_DEFAULT = 100
PAGE_SIZE_MAX = 1000

# ---------------------------------------------------------------------------
# Provenance helpers
# ---------------------------------------------------------------------------


def default_provenance() -> dict[str, Any]:
    """Return default provenance metadata (base 7 fields) for all commands.

    Every response must include: cli_version, schema_version, adapter,
    adapter_version, backend, backend_version, platform.
    """
    return {
        "cli_version": _cli_version,
        "schema_version": SCHEMA_VERSION,
        "adapter": "none",
        "adapter_version": "0.1.0",
        "backend": "none",
        "backend_version": "0.1.0",
        "platform": f"{_platform.system()}-{_platform.machine()}-python{_platform.python_version()}",
    }


def enrich_provenance(
    provenance: dict[str, Any] | None = None,
    *,
    project_id: str | None = None,
    binary_id: str | None = None,
    binary_sha256: str | None = None,
    architecture: str | None = None,
    analysis_profile: str | None = None,
) -> dict[str, Any]:
    """Enrich provenance with optional context fields.

    Args:
        provenance: Base provenance dict (uses default if None).
        project_id: UUID of the project, added for project-context commands.
        binary_id: UUID of the binary, added for binary-context commands.
        binary_sha256: SHA-256 of the binary, added for binary-context commands.
        architecture: Language/processor spec (e.g., "x86:LE:64:default").
        analysis_profile: Profile name (e.g., "standard", "quick", "deep").

    Returns:
        The enriched provenance dict.
    """
    if provenance is None:
        provenance = default_provenance()

    if project_id is not None:
        provenance["project_id"] = project_id
    if binary_id is not None:
        provenance["binary_id"] = binary_id
    if binary_sha256 is not None:
        provenance["binary_sha256"] = binary_sha256
    if architecture is not None:
        provenance["architecture"] = architecture
    if analysis_profile is not None:
        provenance["analysis_profile"] = analysis_profile

    return provenance


# ---------------------------------------------------------------------------
# Pagination helpers
# ---------------------------------------------------------------------------


def clamp_page_size(limit: int | None) -> int:
    """Clamp a page size to the valid range [1, PAGE_SIZE_MAX].

    None or values <= 0 default to PAGE_SIZE_DEFAULT.
    Values above PAGE_SIZE_MAX are clamped to PAGE_SIZE_MAX.

    Args:
        limit: Requested page size, or None for default.

    Returns:
        Clamped page size as a positive integer in [1, PAGE_SIZE_MAX].
    """
    if limit is None or limit < 1:
        return PAGE_SIZE_DEFAULT
    if limit > PAGE_SIZE_MAX:
        print(
            f"Warning: Requested page size {limit} exceeds maximum {PAGE_SIZE_MAX}. "
            f"Clamping to {PAGE_SIZE_MAX}.",
            file=sys.stderr,
        )
        return PAGE_SIZE_MAX
    return limit


def build_paginated_response(
    items: list[dict[str, Any]],
    total: int,
    offset: int,
    limit: int,
    *,
    cursor_encoder: Any | None = None,
) -> dict[str, Any]:
    """Build a paginated response with opaque next_page_token.

    Args:
        items: The sliced page of items.
        total: Total number of items across all pages.
        offset: Starting offset of this page within the total set.
        limit: Page size used for this slice.
        cursor_encoder: Optional callable(dict) -> str for cursor encoding.

    Returns:
        A dict with items, total, page_size, has_more, and next_page_token.
    """
    import base64 as _base64

    has_more = (offset + limit) < total
    next_page_token: str | None = None
    if has_more:
        if cursor_encoder is not None:
            next_page_token = cursor_encoder({"offset": offset + limit})
        else:
            cursor_data = json.dumps({"offset": offset + limit}).encode("utf-8")
            next_page_token = _base64.urlsafe_b64encode(cursor_data).decode("ascii")

    return {
        "items": items,
        "total": total,
        "page_size": limit,
        "has_more": has_more,
        "next_page_token": next_page_token,
    }


# ---------------------------------------------------------------------------
# Warning and diagnostics helpers
# ---------------------------------------------------------------------------


def make_warning(
    message: str,
    severity: str = "WARNING",
    category: str = "general",
) -> dict[str, Any]:
    """Create a structured warning entry with severity, message, and category.

    Warnings are structurally distinct from diagnostics. They appear in
    the `warnings` array, not `diagnostics`.

    Args:
        message: Human-readable warning description.
        severity: Severity from DiagnosticSeverity enum (INFO, WARNING, ERROR).
        category: Classification domain (e.g., "pagination", "staleness", "truncation").

    Returns:
        A dict with severity, message, and category keys.
    """
    return {
        "severity": severity,
        "message": message,
        "category": category,
    }


def make_diagnostic(
    message: str,
    severity: str = "ERROR",
    category: str = "general",
    *,
    component: str | None = None,
    remediation: str | None = None,
    recoverable: bool | None = None,
) -> dict[str, Any]:
    """Create a structured diagnostic entry.

    Args:
        message: Human-readable diagnostic description.
        severity: Severity from DiagnosticSeverity enum.
        category: Classification domain.
        component: Optional component name (e.g., "Java", "Ghidra").
        remediation: Optional remediation hint.
        recoverable: Whether retrying could resolve this.

    Returns:
        A dict with standard diagnostic fields; None-valued optional fields omitted.
    """
    diag: dict[str, Any] = {
        "severity": severity,
        "message": message,
        "category": category,
    }
    if component is not None:
        diag["component"] = component
    if remediation is not None:
        diag["remediation"] = remediation
    if recoverable is not None:
        diag["recoverable"] = recoverable
    return diag


def ensure_collection(data: Any) -> list[Any]:
    """Guarantee that a collection value is a list, never None.

    Empty collection results must be [], never null and never absent.

    Args:
        data: A list or None.

    Returns:
        The original list, or an empty list if data is None.
    """
    if data is None:
        return []
    if isinstance(data, list):
        return data
    return list(data)


def make_partial_success(
    data: Any,
    diagnostics: list[dict[str, Any]],
    warnings: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Build a partial success result envelope fragment.

    Partial success means: success=false, partial=true, non-empty diagnostics,
    and data containing whatever partial results are available.

    Args:
        data: The partial result payload.
        diagnostics: Non-empty list of diagnostic entries.
        warnings: Optional warning entries.

    Returns:
        A dict with success, partial, warnings, diagnostics, data keys.
    """
    return {
        "success": False,
        "partial": True,
        "warnings": warnings or [],
        "diagnostics": diagnostics,
        "data": data,
    }
