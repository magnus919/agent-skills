"""Read-only guest-public EnerGov Permit and Development Portal adapter."""

from __future__ import annotations

import json
import os
from typing import Any

from raleighlib import core


BASE_URL = "https://raleighnc-energovpub.tylerhost.net/apps/selfservice"
SEARCH_URL = f"{BASE_URL}/api/energov/search/search"
CRITERIA_URL = f"{BASE_URL}/api/energov/search/criteria"
PERMIT_URL = f"{BASE_URL}/api/energov/permits"
INSPECTION_SEARCH_URL = f"{BASE_URL}/api/energov/entity/inspections/search/search"


class UnsupportedEndpointError(ValueError):
    """Raised for operations that have no verified guest-public endpoint."""


def _ensure_enabled() -> None:
    value = os.environ.get("RALEIGH_DISABLE_DEVELOPMENT", "").strip().casefold()
    if value in {"1", "true", "yes", "on"}:
        raise UnsupportedEndpointError(
            "Permit and Development Portal adapter is disabled by RALEIGH_DISABLE_DEVELOPMENT"
        )


def _energov_headers(extra: dict[str, str] | None = None) -> dict[str, str]:
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "tenantId": "1",
        "tenantName": "RaleighNCProd",
        "Tyler-TenantUrl": "RaleighNCProd",
        "Tyler-Tenant-Culture": "en-US",
    }
    if extra:
        headers.update(extra)
    return headers


def fetch_criteria() -> dict[str, Any]:
    """Fetch the guest-public search criteria contract."""
    _ensure_enabled()
    data = core.json_request(CRITERIA_URL, headers=_energov_headers())
    if not isinstance(data, dict) or data.get("Success") is False:
        raise UnsupportedEndpointError("EnerGov criteria endpoint returned an error")
    if not isinstance(data.get("Result"), dict):
        raise UnsupportedEndpointError("EnerGov criteria schema is incompatible: Result is not an object")
    return data


def _criteria_field(record_type: str) -> str:
    mapping = {
        "permit": "PermitCriteria",
        "plan": "PlanCriteria",
        "inspection": "InspectionCriteria",
        "code-case": "CodeCaseCriteria",
        "request": "RequestCriteria",
        "license": "LicenseCriteria",
        "project": "ProjectCriteria",
    }
    return mapping.get(record_type.lower(), "PermitCriteria")


def supported_record_types(criteria: dict[str, Any]) -> set[str]:
    """Discover guest-public record types advertised by the criteria contract."""
    result = criteria.get("Result")
    if not isinstance(result, dict):
        raise UnsupportedEndpointError("EnerGov criteria schema is incompatible: Result is not an object")
    candidates = {"permit", "plan", "inspection", "code-case", "request", "license", "project"}
    return {kind for kind in candidates if isinstance(result.get(_criteria_field(kind)), dict)}


def _filter_module(record_type: str) -> int:
    # EnerGov FilterModule enum values used by the public search controller.
    mapping = {
        "permit": 2,
        "plan": 3,
        "inspection": 4,
        "code-case": 5,
        "request": 6,
        "license": 10,
        "project": 11,
    }
    return mapping.get(record_type.lower(), 1)


def _public_scalar(value: Any, *nested_keys: str) -> Any:
    """Return a guest-display scalar, never an upstream container."""
    if isinstance(value, dict):
        for key in nested_keys:
            candidate = value.get(key)
            if candidate is None or isinstance(candidate, (dict, list, tuple, set)):
                continue
            return candidate
        return None
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    return None


def _first_public(record: dict[str, Any], keys: tuple[str, ...], *nested_keys: str) -> Any:
    for key in keys:
        value = _public_scalar(record.get(key), *nested_keys)
        if value not in (None, ""):
            return value
    return None


def _normalize_search_record(record: dict[str, Any]) -> dict[str, Any]:
    """Return only fields represented by the guest-public search cards."""
    address = _first_public(record, ("Address",), "FullAddress", "AddressLine", "DisplayText")
    return {
        "RecordId": _first_public(record, ("CaseId", "Id", "id"), "Id", "Value"),
        "RecordNumber": _first_public(record, ("CaseNumber", "RecordNumber", "PermitNumber"), "Number", "Value"),
        "RecordType": _first_public(record, ("CaseType", "RecordType"), "Name", "DisplayText", "Value"),
        "WorkClass": _first_public(record, ("CaseWorkclass", "WorkClass"), "Name", "DisplayText", "Value"),
        "Status": _first_public(record, ("CaseStatus", "Status"), "Name", "DisplayText", "Value"),
        "ProjectName": _first_public(record, ("ProjectName",), "Name", "DisplayText"),
        "IssueDate": _public_scalar(record.get("IssueDate")),
        "ApplyDate": _public_scalar(record.get("ApplyDate")),
        "ExpireDate": _public_scalar(record.get("ExpireDate")),
        "FinalDate": _public_scalar(record.get("FinalDate")),
        "Address": address or _public_scalar(record.get("AddressDisplay")),
        "ParcelNumber": _first_public(record, ("MainParcel",), "ParcelNumber", "Number", "Value"),
        "Description": _public_scalar(record.get("Description")),
    }


def public_search(
    record_type: str,
    query: str | None = None,
    limit: int = 20,
) -> dict[str, Any]:
    """Search guest-visible records by type using the verified POST contract.

    Returns a dict with ``results`` and ``total`` so callers can paginate or
    report counts.
    """
    core.require_positive_limit(limit)
    criteria = fetch_criteria()
    normalized_type = record_type.lower()
    supported = supported_record_types(criteria)
    if normalized_type not in supported:
        raise UnsupportedEndpointError(
            f"EnerGov does not advertise guest-public {normalized_type} search criteria"
        )
    result = dict(criteria["Result"])
    result["Keyword"] = query or ""
    result["ExactMatch"] = bool(query)
    result["SearchModule"] = 1  # Global public search
    result["FilterModule"] = _filter_module(record_type)
    result["SearchMainAddress"] = False
    result["PageNumber"] = 1
    result["PageSize"] = limit
    result["SortBy"] = None
    result["SortAscending"] = True
    data = core.json_request(
        SEARCH_URL,
        method="POST",
        data=json.dumps(result).encode("utf-8"),
        headers=_energov_headers(),
    )
    data = core.require_object(data, "EnerGov search")
    search_result = data.get("Result")
    if not isinstance(search_result, dict):
        message = (
            data.get("ErrorMessage")
            or data.get("ValidationErrorMessage")
            or "EnerGov search returned no result"
        )
        raise UnsupportedEndpointError(message)
    entity_results = search_result.get("EntityResults")
    total_found = search_result.get("TotalFound")
    if not isinstance(entity_results, list) or any(not isinstance(item, dict) for item in entity_results):
        raise UnsupportedEndpointError("EnerGov search schema is incompatible: EntityResults is not an object list")
    if not isinstance(total_found, int) or isinstance(total_found, bool) or total_found < 0:
        raise UnsupportedEndpointError("EnerGov search schema is incompatible: TotalFound is invalid")
    if len(entity_results) > total_found:
        raise UnsupportedEndpointError(
            "EnerGov search schema is incompatible: EntityResults exceeds TotalFound"
        )
    return {
        "results": [
            _normalize_search_record(record)
            for record in entity_results[:limit]
        ],
        "total": total_found,
    }


def _is_uuid(value: str) -> bool:
    """Return True if value looks like an EnerGov record UUID."""
    import uuid
    try:
        uuid.UUID(value)
        return True
    except ValueError:
        return False


def _resolve_uuid(record: str) -> str:
    """Resolve a record identifier to a UUID, searching by record number if needed."""
    record = record.strip()
    if _is_uuid(record):
        return record
    results = public_search("permit", query=record, limit=20)
    record_folded = record.casefold()
    matches = [
        r for r in results.get("results", [])
        if str(r.get("RecordNumber") or r.get("PermitNumber") or r.get("CaseNumber") or "").casefold()
        == record_folded
    ]
    if not matches:
        raise ValueError(f"No permit found for record number: {record}")
    if len(matches) > 1:
        raise ValueError(f"Ambiguous record number '{record}'; supply the UUID")
    resolved = (
        matches[0].get("RecordId")
        or matches[0].get("Id")
        or matches[0].get("id")
        or matches[0].get("CaseId")
    )
    if not resolved:
        raise ValueError("Resolved record has no UUID")
    return resolved


def permit_detail(record: str) -> dict[str, Any]:
    """Fetch guest-public permit details by UUID or record number."""
    _ensure_enabled()
    uuid = _resolve_uuid(record)
    url = f"{PERMIT_URL}/{uuid}"
    data = core.json_request(url, headers=_energov_headers())
    if not isinstance(data, dict):
        raise UnsupportedEndpointError("EnerGov permit detail schema is incompatible")
    if data.get("Success") is False:
        raise ValueError(data.get("ErrorMessage") or "EnerGov permit detail failed")
    result = data.get("Result", data)
    if not isinstance(result, dict):
        raise UnsupportedEndpointError("EnerGov permit detail Result must be an object")
    projected = {
        "PermitId": _first_public(result, ("PermitId",), "Id", "Value"),
        "PermitNumber": _first_public(result, ("PermitNumber",), "Number", "Value"),
        "PermitType": _first_public(result, ("PermitType",), "Name", "DisplayText", "Value"),
        "PermitStatus": _first_public(result, ("PermitStatus",), "Name", "DisplayText", "Value"),
        "IssueDate": _public_scalar(result.get("IssueDate")),
        "ExpireDate": _public_scalar(result.get("ExpireDate")),
        "FinalizeDate": _public_scalar(result.get("FinalizeDate")),
        "ApplyDate": _public_scalar(result.get("ApplyDate")),
        "WorkClassName": _first_public(result, ("WorkClassName",), "Name", "DisplayText", "Value"),
        "Description": _public_scalar(result.get("Description")),
        "IVRNumber": _public_scalar(result.get("IVRNumber")),
        "MainAddress": _first_public(result, ("MainAddress",), "FullAddress", "AddressLine", "DisplayText"),
        "MainParcelNumber": _first_public(result, ("MainParcelNumber",), "ParcelNumber", "Number", "Value"),
        "ProjectName": _first_public(result, ("ProjectName",), "Name", "DisplayText"),
        "DistrictName": _first_public(result, ("DistrictName",), "Name", "DisplayText"),
        "SquareFeet": _public_scalar(result.get("SquareFeet")),
        "Value": _public_scalar(result.get("Value")),
    }
    if not projected["PermitId"] and not projected["PermitNumber"]:
        raise UnsupportedEndpointError(
            "EnerGov permit detail Result has no permit identifier"
        )
    return projected


def inspections_for_record(record: str, limit: int = 10) -> list[dict[str, Any]]:
    """Fetch guest-visible inspections for a permit UUID or record number."""
    if limit < 1:
        raise ValueError("limit must be at least 1")
    _ensure_enabled()
    uuid = _resolve_uuid(record)
    payload = {
        "PageNumber": 1,
        "PageSize": limit,
        "SortField": "",
        "IsSortedInAscendingOrder": True,
        "ModuleId": 1,
        "EntityId": uuid,
        "IsExistingInspection": True,
        "IsOptionalInspection": False,
        "IsFailed": False,
    }
    data = core.json_request(
        INSPECTION_SEARCH_URL,
        method="POST",
        data=json.dumps(payload).encode("utf-8"),
        headers=_energov_headers(),
    )
    if not isinstance(data, dict):
        raise UnsupportedEndpointError("EnerGov inspection schema is incompatible")
    if data.get("Success") is False:
        raise ValueError(data.get("ErrorMessage") or "EnerGov inspection search failed")
    result = data.get("Result", data)
    if isinstance(result, dict):
        if "results" in result:
            result = result["results"]
        elif "Results" in result:
            result = result["Results"]
        else:
            raise UnsupportedEndpointError(
                "EnerGov inspection Result has no recognized result list"
            )
    if not isinstance(result, list):
        raise UnsupportedEndpointError("EnerGov inspection Result must be a list")
    rows: list[dict[str, Any]] = []
    for inspection in result[:limit]:
        if not isinstance(inspection, dict):
            raise UnsupportedEndpointError(
                "EnerGov inspection Result contains a non-object item"
            )
        rows.append({
            "InspectionId": _first_public(inspection, ("InspectionId",), "Id", "Value"),
            "InspectionNumber": _first_public(inspection, ("InspectionNumber",), "Number", "Value"),
            "InspectionType": _first_public(inspection, ("InspectionType",), "Name", "DisplayText", "Value"),
            "InspectionStatus": _first_public(inspection, ("InspectionStatus",), "Name", "DisplayText", "Value"),
            "RequestedDate": _public_scalar(inspection.get("RequestedDate")),
            "ScheduledStartDate": _public_scalar(inspection.get("ScheduledStartDate")),
            "ActualDate": _public_scalar(inspection.get("ActualDate")),
            "PrimaryInspector": _first_public(inspection, ("PrimaryInspector",), "Name", "DisplayName"),
            "IsReinspectionDisplayText": _public_scalar(inspection.get("IsReinspectionDisplayText")),
        })
    return rows


def code_cases(query: str | None = None, limit: int = 20) -> list[dict[str, Any]]:
    """Search guest-visible code cases."""
    return public_search("code-case", query=query, limit=limit)


def licenses(query: str | None = None, limit: int = 20) -> list[dict[str, Any]]:
    """Search guest-visible licenses."""
    return public_search("license", query=query, limit=limit)
