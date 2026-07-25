"""Read-only adapter for the Raleigh-Wake Emergency Communications Center active incident feed.

This is an UNDOCUMENTED public application endpoint, not a versioned API.
The adapter is isolated and can be disabled independently via
RALEIGH_DISABLE_INCIDENTS=1.
"""

from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Any

from raleighlib import core


FEED_URL = "https://incidents.rwecc.com/getdata"

CACHE_KEY = "incidents-rwecc-active.json"
CACHE_TTL_SECONDS = 90

SOURCE_LABEL = (
    "Filtered active public incident feed from incidents.rwecc.com "
    "(undocumented endpoint). This is NOT all 911 calls and NOT "
    "authoritative emergency status."
)

KNOWN_AGENCIES = frozenset({
    "raleigh police department",
    "raleigh fire department",
    "raleigh police",
    "raleigh fire",
})


class IncidentFeedError(ValueError):
    """Raised when the incident feed is unavailable, malformed, or drifted."""


def _ensure_enabled() -> None:
    value = os.environ.get("RALEIGH_DISABLE_INCIDENTS", "").strip().casefold()
    if value in {"1", "true", "yes", "on"}:
        raise IncidentFeedError(
            "Incident feed adapter is disabled by RALEIGH_DISABLE_INCIDENTS"
        )


def _validate_record(record: Any, index: int) -> dict[str, Any] | None:
    if not isinstance(record, dict):
        return None
    jurisdiction = record.get("jurisdiction")
    problem = record.get("problem")
    address = record.get("address")
    timestamp = record.get("timestamp")
    if not isinstance(jurisdiction, str) or not jurisdiction.strip():
        return None
    if not isinstance(problem, str) or not problem.strip():
        return None
    lat = record.get("lat")
    lon = record.get("long")
    if not isinstance(lat, (int, float)) or isinstance(lat, bool):
        lat = None
    if not isinstance(lon, (int, float)) or isinstance(lon, bool):
        lon = None
    if lat is not None and not (-90 <= lat <= 90):
        lat = None
    if lon is not None and not (-180 <= lon <= 180):
        lon = None
    return {
        "jurisdiction": jurisdiction.strip(),
        "problem": problem.strip(),
        "address": address.strip() if isinstance(address, str) else None,
        "lat": lat,
        "long": lon,
        "timestamp": timestamp if isinstance(timestamp, str) else None,
    }


def fetch_active(
    agency: str | None = None,
    incident_type: str | None = None,
    limit: int = 50,
    use_cache: bool = True,
) -> dict[str, Any]:
    """Fetch currently active incidents from the RWECC public feed.

    Returns a dict with ``incidents``, ``retrieved_at``, ``source``, and
    ``warnings`` keys.
    """
    _ensure_enabled()
    core.require_positive_limit(limit)

    warnings: list[str] = []

    if use_cache:
        cached = core.read_cache(CACHE_KEY, max_age_seconds=CACHE_TTL_SECONDS)
        if cached is not None and isinstance(cached, list):
            raw = cached
        else:
            raw = _fetch_raw()
    else:
        raw = _fetch_raw()

    if not isinstance(raw, list):
        raise IncidentFeedError(
            "Feed schema drift: expected a JSON list of incident records"
        )

    if len(raw) == 0:
        warnings.append(
            "Feed returned zero records. This does not prove no incidents "
            "are active; the feed may be stale or filtered upstream."
        )

    incidents: list[dict[str, Any]] = []
    skipped = 0
    seen_keys: set[str] = set()
    for i, record in enumerate(raw):
        validated = _validate_record(record, i)
        if validated is None:
            skipped += 1
            continue
        dedup_key = "|".join([
            validated["jurisdiction"].casefold(),
            validated["problem"].casefold(),
            str(validated.get("address") or "").casefold(),
            str(validated.get("timestamp") or ""),
        ])
        if dedup_key in seen_keys:
            continue
        seen_keys.add(dedup_key)
        incidents.append(validated)

    if skipped > 0:
        warnings.append(
            f"{skipped} record(s) skipped due to schema drift or missing required fields."
        )

    if agency:
        agency_lower = agency.strip().casefold().replace("-", " ")
        if agency_lower not in KNOWN_AGENCIES:
            warnings.append(
                f"Agency '{agency}' is not a known agency. "
                f"Known agencies: {', '.join(sorted(KNOWN_AGENCIES))}. "
                "Filtering by substring match anyway."
            )
        incidents = [
            r for r in incidents
            if agency_lower in r["jurisdiction"].casefold()
        ]

    if incident_type:
        type_lower = incident_type.strip().casefold()
        incidents = [
            r for r in incidents
            if type_lower in r["problem"].casefold()
        ]

    incidents = incidents[:limit]

    return {
        "incidents": incidents,
        "retrieved_at": datetime.now(timezone.utc).isoformat(),
        "source": SOURCE_LABEL,
        "warnings": warnings,
    }


def _fetch_raw() -> list[Any]:
    import json as _json
    try:
        body = core.raw_request(FEED_URL, max_bytes=2 * 1024 * 1024)
    except core.SecurityError:
        raise
    except Exception as exc:
        raise IncidentFeedError(
            f"Incident feed unavailable: {exc}"
        ) from exc
    if not body:
        return []
    try:
        data = _json.loads(body.decode("utf-8"))
    except (UnicodeDecodeError, _json.JSONDecodeError) as exc:
        raise IncidentFeedError(
            f"Incident feed returned malformed JSON: {exc}"
        ) from exc
    if isinstance(data, dict) and not data:
        return []
    if isinstance(data, dict):
        raise IncidentFeedError(
            "Feed schema drift: expected a JSON list, got an object. "
            "The undocumented endpoint contract may have changed."
        )
    if isinstance(data, list):
        core.write_cache(CACHE_KEY, data)
        return data
    raise IncidentFeedError(
        "Feed schema drift: unexpected response type"
    )
