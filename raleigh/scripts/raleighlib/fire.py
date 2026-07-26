"""Raleigh Fire Department incident data access.

Resolves stable ArcGIS item IDs to live FeatureServer URLs and provides
source-aware queries across two RFD datasets: the full public history
(2007–present) and the past-month feed. Normalizes the 2026 classification
schema transition into stable output keys without fabricating cross-era
mappings, and computes response durations only from valid timestamps.
"""

from __future__ import annotations

import math
import re
import sys
import urllib.parse
from datetime import date, datetime, timedelta, timezone
from typing import Any

from raleighlib import arcgis
from raleighlib import core

ITEM_RESOLUTION_URL = "https://ral.maps.arcgis.com/sharing/rest/content/items/{item_id}"

RFD_SOURCES: dict[str, dict[str, str]] = {
    "full-history": {
        "item_id": "ea466e39e9ca4448b645c33a0d6c60ad",
        "label": "Fire Incidents (full public history, 2007–present)",
        "caveats": (
            "Legacy classification fields are null for 2026+ records; "
            "station is unpopulated for many records."
        ),
    },
    "past-month": {
        "item_id": "c983765e304a41d19087c8d95aa46d54",
        "label": "Fire Incidents (past month)",
        "caveats": (
            "Rolling past-month feed; carries station_name and the current "
            "classification fields only."
        ),
    },
}

_FIELD_MAPS: dict[str, dict[str, str]] = {
    "full-history": {
        "date": "dispatch_date_time",
        "station": "station",
        "platoon": "platoon",
        "group": "incident_group_name",
        "type_name": "incident_type_name",
        "type_legacy": "incident_type_description",
        "type_code": "incident_type",
    },
    "past-month": {
        "date": "dispatch_date_time",
        "station": "station_name",
        "platoon": "platoon",
        "group": "incident_group_name",
        "type_name": "incident_type_name",
    },
}

SCHEMA_TRANSITION_EPOCH_MS = 1767225600000

PRIVACY_CAVERAT = (
    "RFD excludes incident types 300–399 and 661 from this public feed for "
    "EMS/privacy reasons. This is not a complete record of all fire department "
    "responses and must not be used for emergency response."
)

REPORT_FIELDS = (
    "incident_number",
    "dispatch_date_time",
    "arrive_date_time",
    "cleared_date_time",
    "address",
    "station_name",
    "platoon",
    "incident_group_name",
    "incident_subgroup_code",
    "incident_type_name",
)
REPORT_LIMIT = 200

_STATION_NAME_RE = re.compile(r"^station\s*0*(\d+)\s*$", re.IGNORECASE)


class FireError(Exception):
    """Raised for RFD data resolution or query failures."""


def resolve_item_url(item_id: str) -> str:
    """Resolve an ArcGIS item ID to its FeatureServer/MapServer URL."""
    url = ITEM_RESOLUTION_URL.format(item_id=item_id)
    params = {"f": "json"}
    full_url = f"{url}?{urllib.parse.urlencode(params)}"
    meta = core.json_request(full_url)
    service_url = meta.get("url")
    if not service_url:
        raise FireError(f"Item {item_id} has no service URL")
    return service_url


def resolve_layer_url(source_key: str) -> str:
    """Resolve a source key to a queryable layer URL."""
    source = RFD_SOURCES.get(source_key)
    if not source:
        raise FireError(f"Unknown source: {source_key}")
    service_url = resolve_item_url(source["item_id"])
    return arcgis.resolve_queryable_layer(service_url)


def _escape_sql_value(value: str) -> str:
    """Escape a string value for use inside single quotes in an ArcGIS WHERE clause."""
    return value.replace("'", "''")


def _escape_like_value(value: str) -> str:
    """Escape LIKE wildcards and quotes for use in a LIKE pattern."""
    return value.replace("'", "''").replace("%", "\\%").replace("_", "\\_")


def _discover_fields(layer_url: str) -> set[str]:
    """Return the set of field names advertised by a layer."""
    fields = arcgis.layer_fields(layer_url)
    return {f.get("name", "") for f in fields if isinstance(f, dict)}


def _ms_to_timestamp_literal(ms: int) -> str:
    """Format Unix milliseconds as an ArcGIS TIMESTAMP literal in UTC.

    The RFD layers reject bare epoch-millisecond literals in date comparisons
    and require TIMESTAMP 'YYYY-MM-DD HH:MM:SS'.
    """
    try:
        dt = datetime.fromtimestamp(ms / 1000, timezone.utc)
    except (OverflowError, OSError, ValueError) as exc:
        raise FireError(f"date range out of bounds: {ms}") from exc
    return "TIMESTAMP '" + dt.strftime("%Y-%m-%d %H:%M:%S") + "'"


def _station_patterns(station: int) -> list[str]:
    """Return case-insensitive station_name match patterns for a station number."""
    padded = f"STATION {station:02d}"
    bare = f"STATION {station}"
    return [padded, bare] if padded != bare else [padded]


def build_where_clause(
    source_key: str,
    available_fields: set[str],
    since_ms: int | None = None,
    station: int | None = None,
    platoon: str | None = None,
    group: str | None = None,
    incident_type: str | None = None,
) -> str:
    """Build an ArcGIS WHERE clause from durable filters.

    Field names are validated against the supplied field set. If a filter
    field is missing, the filter is skipped with a stderr warning.
    """
    field_map = _FIELD_MAPS.get(source_key)
    if not field_map:
        raise FireError(f"No field map for source: {source_key}")

    clauses: list[str] = ["1=1"]

    if since_ms is not None:
        date_field = field_map["date"]
        if date_field in available_fields:
            clauses.append(f"{date_field} >= {_ms_to_timestamp_literal(since_ms)}")
        else:
            print(
                f"Warning: date field '{date_field}' not found in {source_key}; skipping date filter",
                file=sys.stderr,
            )

    if station is not None:
        station_field = field_map["station"]
        if station_field in available_fields:
            if source_key == "past-month":
                patterns = " OR ".join(
                    f"UPPER({station_field}) LIKE '{pattern}'"
                    for pattern in _station_patterns(station)
                )
                clauses.append(f"({patterns})")
            else:
                clauses.append(f"{station_field} = {int(station)}")
        else:
            print(
                f"Warning: station field '{station_field}' not found in {source_key}; skipping station filter",
                file=sys.stderr,
            )

    if platoon:
        platoon_field = field_map["platoon"]
        if platoon_field in available_fields:
            escaped = _escape_sql_value(platoon.strip().upper())
            clauses.append(f"UPPER({platoon_field}) = '{escaped}'")
        else:
            print(
                f"Warning: platoon field '{platoon_field}' not found in {source_key}; skipping platoon filter",
                file=sys.stderr,
            )

    if group:
        group_field = field_map["group"]
        if group_field in available_fields:
            escaped = _escape_like_value(group.upper())
            clauses.append(f"UPPER({group_field}) LIKE '%{escaped}%'")
        else:
            print(
                f"Warning: group field '{group_field}' not found in {source_key}; skipping group filter",
                file=sys.stderr,
            )

    if incident_type:
        type_fields = [
            field_map["type_name"],
            field_map.get("type_legacy"),
        ]
        present = [f for f in type_fields if f and f in available_fields]
        if present:
            escaped = _escape_like_value(incident_type.upper())
            like_terms = [f"UPPER({field}) LIKE '%{escaped}%'" for field in present]
            code_field = field_map.get("type_code")
            if code_field and code_field in available_fields and incident_type.strip().isdigit():
                like_terms.append(f"{code_field} = {int(incident_type.strip())}")
            clauses.append(f"({' OR '.join(like_terms)})")
        else:
            print(
                f"Warning: incident type fields not found in {source_key}; skipping type filter",
                file=sys.stderr,
            )

    return " AND ".join(clauses)


def _present(value: Any) -> Any:
    """Return the value if it carries content, else None. Empty strings are missing."""
    if value is None:
        return None
    if isinstance(value, str) and not value.strip():
        return None
    return value


def normalize_classification(attrs: dict[str, Any]) -> dict[str, Any]:
    """Map legacy and current RFD classification fields to stable keys.

    RFD deprecated incident_type and incident_type_description for records
    after 2026-01-01, replacing them with incident_group_name,
    incident_subgroup_code, and incident_type_name. This never fabricates
    cross-era mappings: legacy NFIRS codes are not translated into current
    group names. If both field sets are populated, the replacement fields
    win and the era is reported as 'current'.
    """
    group = _present(attrs.get("incident_group_name"))
    subgroup = _present(attrs.get("incident_subgroup_code"))
    type_name = _present(attrs.get("incident_type_name"))
    legacy_desc = _present(attrs.get("incident_type_description"))
    legacy_code = _present(attrs.get("incident_type"))

    has_current = any(v is not None for v in (group, subgroup, type_name))
    has_legacy = any(v is not None for v in (legacy_desc, legacy_code))

    if has_current:
        era = "current"
    elif has_legacy:
        era = "legacy"
    else:
        era = "unknown"

    return {
        "_classification_era": era,
        "_incident_group": group,
        "_incident_subgroup": subgroup,
        "_incident_type": type_name if type_name is not None else legacy_desc,
        "_incident_code": legacy_code,
    }


def normalize_station(attrs: dict[str, Any]) -> int | None:
    """Return a station number from either source's station field.

    The full-history feed carries an integer 'station'; the past-month feed
    carries a 'station_name' string such as 'Station 09'. Returns None when
    neither carries a usable value; never guesses.
    """
    raw = attrs.get("station")
    if isinstance(raw, (int, float)) and not isinstance(raw, bool):
        if math.isfinite(raw) and raw == int(raw) and int(raw) > 0:
            return int(raw)
    name = _present(attrs.get("station_name"))
    if isinstance(name, str):
        match = _STATION_NAME_RE.match(name)
        if match:
            return int(match.group(1))
    return None


def _valid_timestamp_ms(value: Any) -> int | None:
    """Return the timestamp as integer milliseconds if it is a finite non-negative number."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    if not math.isfinite(value):
        return None
    if value < 0:
        return None
    return int(value)


def _duration_seconds(start: Any, end: Any) -> tuple[float | None, str]:
    """Compute a duration in seconds between two timestamps with a status.

    Statuses: ok, missing_timestamp, malformed_timestamp, reversed_timestamps.
    """
    if start is None or end is None:
        return None, "missing_timestamp"
    start_ms = _valid_timestamp_ms(start)
    end_ms = _valid_timestamp_ms(end)
    if start_ms is None or end_ms is None:
        return None, "malformed_timestamp"
    if end_ms < start_ms:
        return None, "reversed_timestamps"
    return (end_ms - start_ms) / 1000.0, "ok"


def compute_response_times(attrs: dict[str, Any]) -> dict[str, Any]:
    """Compute incident durations in seconds from dispatch/arrival/cleared timestamps.

    Each pair is validated independently; invalid pairs yield None with a
    status explaining why. No duration is invented.
    """
    dispatch = attrs.get("dispatch_date_time")
    arrive = attrs.get("arrive_date_time")
    cleared = attrs.get("cleared_date_time")

    pairs = [
        ("_dispatch_to_arrive_seconds", "_dispatch_to_arrive_status", dispatch, arrive),
        ("_arrive_to_clear_seconds", "_arrive_to_clear_status", arrive, cleared),
        ("_dispatch_to_clear_seconds", "_dispatch_to_clear_status", dispatch, cleared),
    ]
    out: dict[str, Any] = {}
    for value_key, status_key, start, end in pairs:
        seconds, status = _duration_seconds(start, end)
        out[value_key] = seconds
        out[status_key] = status
    return out


def _normalize_geometry(record: dict[str, Any]) -> dict[str, Any] | None:
    """Return GeoJSON geometry, suppressing missing and null-island placeholder points."""
    geom = record.get("geometry")
    if not geom:
        return None
    if geom.get("x") == 0 and geom.get("y") == 0:
        return None
    return arcgis.geometry_from_record(record)


def query_incidents(
    source_key: str,
    since_ms: int | None = None,
    station: int | None = None,
    platoon: str | None = None,
    group: str | None = None,
    incident_type: str | None = None,
    limit: int = 20,
    offset: int = 0,
    include_response_times: bool = False,
) -> dict[str, Any]:
    """Query a single RFD source and return an enriched GeoJSON FeatureCollection."""
    source = RFD_SOURCES.get(source_key)
    if not source:
        raise FireError(f"Unknown source: {source_key}")

    layer_url = resolve_layer_url(source_key)
    available_fields = _discover_fields(layer_url)
    where = build_where_clause(
        source_key,
        available_fields,
        since_ms=since_ms,
        station=station,
        platoon=platoon,
        group=group,
        incident_type=incident_type,
    )

    records = arcgis.query_all_pages(
        layer_url,
        where=where,
        return_geometry=True,
        max_records=limit,
        offset=offset,
    )

    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    features: list[dict[str, Any]] = []
    for record in records:
        attrs = dict(record.get("attributes", {}))
        attrs["_source"] = source_key
        attrs["_item_id"] = source["item_id"]
        attrs["_retrieved_at"] = now
        attrs.update(normalize_classification(attrs))
        attrs["_station"] = normalize_station(attrs)
        if include_response_times:
            attrs.update(compute_response_times(attrs))
        features.append({
            "type": "Feature",
            "properties": attrs,
            "geometry": _normalize_geometry(record),
        })

    return {
        "type": "FeatureCollection",
        "_sources": [
            {
                "item_id": source["item_id"],
                "label": source["label"],
                "caveats": source["caveats"],
            }
        ],
        "features": features,
    }


def query_reports(
    *,
    report_date: str | None = None,
    incident_number: str | None = None,
) -> dict[str, Any]:
    """Query the authoritative past-month layer by one exact bounded selector."""
    if bool(report_date) == bool(incident_number):
        raise FireError("provide exactly one report date or incident number")

    layer_url = resolve_layer_url("past-month")
    available_fields = _discover_fields(layer_url)
    missing = set(REPORT_FIELDS) - available_fields
    if missing:
        raise FireError(
            "Fire report source schema drift; missing fields: "
            + ", ".join(sorted(missing))
        )

    query: dict[str, str | None] = {
        "date": report_date,
        "incident_number": incident_number,
    }
    if report_date:
        try:
            start = date.fromisoformat(report_date)
        except ValueError as exc:
            raise FireError("report date must use YYYY-MM-DD") from exc
        end = start + timedelta(days=1)
        where = (
            f"dispatch_date_time >= TIMESTAMP '{start.isoformat()} 00:00:00' AND "
            f"dispatch_date_time < TIMESTAMP '{end.isoformat()} 00:00:00'"
        )
    else:
        number = (incident_number or "").strip()
        if not number:
            raise FireError("incident number must not be empty")
        where = f"incident_number = '{_escape_sql_value(number)}'"

    response = arcgis.query_layer(
        layer_url,
        where=where,
        out_fields=",".join(REPORT_FIELDS),
        return_geometry=False,
        result_record_count=REPORT_LIMIT,
        order_by_fields="dispatch_date_time ASC,incident_number ASC",
    )
    records = response.get("features")
    if not isinstance(records, list):
        raise FireError("Fire report source returned invalid features")
    if response.get("exceededTransferLimit"):
        raise FireError(f"Fire report query exceeded the {REPORT_LIMIT}-record safety limit")

    retrieved_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    reports: list[dict[str, Any]] = []
    for record in records:
        if not isinstance(record, dict) or not isinstance(record.get("attributes"), dict):
            raise FireError("Fire report source returned a malformed record")
        attrs = record["attributes"]
        if not _present(attrs.get("incident_number")):
            raise FireError("Fire report source returned a record without incident_number")
        reports.append({
            "source": "arcgis",
            "source_fragility": "authoritative-structured",
            **{field: attrs.get(field) for field in REPORT_FIELDS},
        })

    return {
        "query": query,
        "reports": reports,
        "sources": [{
            "source": "arcgis",
            "item_id": RFD_SOURCES["past-month"]["item_id"],
            "url": layer_url,
            "retrieved_at": retrieved_at,
        }],
        "warnings": [
            "The rolling ArcGIS feed may lag the RFD Report System and is not proof of completeness."
        ],
    }
