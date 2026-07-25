"""Raleigh Police Department incident data access.

Resolves stable ArcGIS item IDs to live FeatureServer URLs and provides
source-aware queries across four RPD datasets: NIBRS, SRS, previous-day,
and CrimeMapper past-90-days.
"""

from __future__ import annotations

import sys
import urllib.parse
from datetime import datetime, timezone
from typing import Any

from raleighlib import arcgis
from raleighlib import core

ITEM_RESOLUTION_URL = "https://ral.maps.arcgis.com/sharing/rest/content/items/{item_id}"

RPD_SOURCES: dict[str, dict[str, str]] = {
    "nibrs": {
        "item_id": "24c0b37fa9bb4e16ba8bcaa7e806c615",
        "label": "NIBRS (June 2014–present)",
        "caveats": "Block-level locations; may be randomized or redacted.",
    },
    "srs": {
        "item_id": "09af62a32ae8436bae6eda74aa7f172b",
        "label": "SRS (2005–May 2014)",
        "caveats": "Legacy reporting system; schema differs from NIBRS.",
    },
    "previous-day": {
        "item_id": "693811eb361f4da286891eca1fae5943",
        "label": "Previous-day incidents",
        "caveats": "May lag by more than one day; empty on some days.",
    },
    "crimemapper-90d": {
        "item_id": "a1f2d9204a184404b5a4c7e0fdceb6d0",
        "label": "CrimeMapper past 90 days",
        "caveats": "Not in the curated Hub catalog; field schema may differ.",
    },
}

_FIELD_MAPS: dict[str, dict[str, str]] = {
    "nibrs": {"category": "crime_description", "district": "district", "date": "reported_date"},
    "crimemapper-90d": {"category": "crime_description", "district": "district", "date": "reported_date"},
    "previous-day": {"category": "crime_description", "district": "district", "date": "reported_date"},
    "srs": {"category": "LCR_DESC", "district": "DISTRICT", "date": "INC_DATETIME"},
}

RALEIGH_BBOX = (-78.8, 35.6, -78.4, 36.0)

NIBRS_EPOCH_MS = 1401580800000

LOCATION_CAVERAT = (
    "Locations are block-level and may be randomized or redacted. "
    "This data does not include arrests, convictions, or dispositions."
)


class PoliceError(Exception):
    """Raised for RPD data resolution or query failures."""


def resolve_item_url(item_id: str) -> str:
    """Resolve an ArcGIS item ID to its FeatureServer/MapServer URL."""
    url = ITEM_RESOLUTION_URL.format(item_id=item_id)
    params = {"f": "json"}
    full_url = f"{url}?{urllib.parse.urlencode(params)}"
    meta = core.json_request(full_url)
    service_url = meta.get("url")
    if not service_url:
        raise PoliceError(f"Item {item_id} has no service URL")
    return service_url


def resolve_layer_url(source_key: str) -> str:
    """Resolve a source key to a queryable layer URL."""
    source = RPD_SOURCES.get(source_key)
    if not source:
        raise PoliceError(f"Unknown source: {source_key}")
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


def build_where_clause(
    source_key: str,
    available_fields: set[str],
    since_ms: int | None = None,
    category: str | None = None,
    district: str | None = None,
) -> str:
    """Build an ArcGIS WHERE clause from durable filters.

    Field names are validated against the supplied field set. If a filter
    field is missing, the filter is skipped with a stderr warning.
    """
    field_map = _FIELD_MAPS.get(source_key)
    if not field_map:
        raise PoliceError(f"No field map for source: {source_key}")

    clauses: list[str] = ["1=1"]

    if since_ms is not None:
        date_field = field_map["date"]
        if date_field in available_fields:
            clauses.append(f"{date_field} >= {since_ms}")
        else:
            print(
                f"Warning: date field '{date_field}' not found in {source_key}; skipping date filter",
                file=sys.stderr,
            )

    if category:
        cat_field = field_map["category"]
        if cat_field in available_fields:
            escaped = _escape_like_value(category.upper())
            clauses.append(f"UPPER({cat_field}) LIKE '%{escaped}%'")
        else:
            print(
                f"Warning: category field '{cat_field}' not found in {source_key}; skipping category filter",
                file=sys.stderr,
            )

    if district:
        dist_field = field_map["district"]
        if dist_field in available_fields:
            escaped = _escape_like_value(district.upper())
            clauses.append(f"UPPER({dist_field}) LIKE '%{escaped}%'")
        else:
            print(
                f"Warning: district field '{dist_field}' not found in {source_key}; skipping district filter",
                file=sys.stderr,
            )

    return " AND ".join(clauses)


def _is_placeholder_point(geom: dict[str, Any]) -> bool:
    """Return True if the geometry is a null-island placeholder (0,0)."""
    return geom.get("x") == 0 and geom.get("y") == 0


def _location_status(record: dict[str, Any]) -> str:
    """Classify a record's location quality."""
    geom = record.get("geometry")
    if not geom:
        return "redacted"
    if "x" in geom and "y" in geom:
        if _is_placeholder_point(geom):
            return "redacted"
        x, y = geom["x"], geom["y"]
        if not (RALEIGH_BBOX[0] <= x <= RALEIGH_BBOX[2] and RALEIGH_BBOX[1] <= y <= RALEIGH_BBOX[3]):
            return "out_of_area"
        return "block_level"
    return "unknown"


def _normalize_geometry(record: dict[str, Any]) -> dict[str, Any] | None:
    """Return GeoJSON geometry, suppressing redacted/placeholder points."""
    geom = record.get("geometry")
    if not geom:
        return None
    if "x" in geom and "y" in geom:
        if _is_placeholder_point(geom):
            return None
        return {"type": "Point", "coordinates": [geom["x"], geom["y"]]}
    return arcgis.geometry_from_record(record)


def query_incidents(
    source_key: str,
    since_ms: int | None = None,
    category: str | None = None,
    district: str | None = None,
    limit: int = 20,
    offset: int = 0,
) -> dict[str, Any]:
    """Query a single RPD source and return an enriched GeoJSON FeatureCollection."""
    source = RPD_SOURCES.get(source_key)
    if not source:
        raise PoliceError(f"Unknown source: {source_key}")

    layer_url = resolve_layer_url(source_key)
    available_fields = _discover_fields(layer_url)
    where = build_where_clause(
        source_key, available_fields, since_ms=since_ms, category=category, district=district
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
        geom = _normalize_geometry(record)
        attrs = dict(record.get("attributes", {}))
        attrs["_source"] = source_key
        attrs["_item_id"] = source["item_id"]
        attrs["_retrieved_at"] = now
        attrs["_location_status"] = _location_status(record)
        features.append({
            "type": "Feature",
            "properties": attrs,
            "geometry": geom,
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
