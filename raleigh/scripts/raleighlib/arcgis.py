"""ArcGIS FeatureServer and MapServer query helpers."""

from __future__ import annotations

import csv
import io
import urllib.parse
from typing import Any

from raleighlib import core


def service_metadata(url: str) -> dict[str, Any]:
    """Fetch service or layer metadata from an ArcGIS REST endpoint."""
    sep = "&" if "?" in url else "?"
    return core.json_request(f"{url}{sep}f=json")


def _looks_like_layer_url(url: str) -> bool:
    """Return True if url already ends with a layer id."""
    import re

    return bool(re.search(r"/(FeatureServer|MapServer)/\d+/?$", url.rstrip("/")))


def _looks_like_service_root(url: str) -> bool:
    import re

    return bool(re.search(r"/(FeatureServer|MapServer)/?$", url.rstrip("/")))


def resolve_queryable_layer(url: str) -> str:
    """Return a queryable layer URL, resolving service roots to their first layer."""
    if _looks_like_layer_url(url):
        return url.rstrip("/")
    if not _looks_like_service_root(url):
        # Not a recognized service root or layer; return as-is and let the caller fail clearly.
        return url
    meta = service_metadata(url)
    layers = meta.get("layers", []) or meta.get("tables", []) or []
    for candidate in layers:
        if candidate.get("subLayerIds") is None:
            return f"{url.rstrip('/')}/{candidate['id']}"
    # Fallback to first layer if all are group layers.
    if layers:
        return f"{url.rstrip('/')}/{layers[0]['id']}"
    raise ValueError(f"No queryable layers found at {url}")


def layer_has_geometry(url: str) -> bool:
    """Return True if the layer advertises a geometry type."""
    meta = service_metadata(url)
    if meta.get("type") == "Table":
        return False
    return meta.get("geometryType") is not None


def layer_fields(url: str) -> list[dict[str, Any]]:
    """Return the field definitions advertised by a layer or table."""
    meta = service_metadata(url)
    return meta.get("fields", [])


def sample_features(url: str, limit: int = 3) -> list[dict[str, Any]]:
    """Query a small sample of features from a layer."""
    return query_all_pages(url, max_records=limit, return_geometry=True)


def query_layer(
    url: str,
    where: str = "1=1",
    out_fields: str = "*",
    return_geometry: bool = True,
    result_record_count: int | None = None,
    result_offset: int = 0,
    order_by_fields: str | None = None,
    f: str = "json",
    out_sr: int | None = 4326,
) -> dict[str, Any]:
    """Query a single page from an ArcGIS layer."""
    core.require_positive_limit(result_record_count, allow_none=True)
    if result_offset < 0:
        raise ValueError("result_offset must be nonnegative")
    base = url.rstrip("/") + "/query"
    params: dict[str, Any] = {
        "where": where,
        "outFields": out_fields,
        "returnGeometry": "true" if return_geometry else "false",
        "f": f,
        "outSR": out_sr,
    }
    if result_record_count is not None:
        params["resultRecordCount"] = result_record_count
    if result_offset:
        params["resultOffset"] = result_offset
    if order_by_fields:
        params["orderByFields"] = order_by_fields
    if out_sr is not None:
        params["outSR"] = out_sr
    full_url = f"{base}?{urllib.parse.urlencode(params)}"
    response = core.json_request(full_url)
    core.raise_for_arcgis_error(response, "ArcGIS query")
    return response


def query_all_pages(
    url: str,
    where: str = "1=1",
    out_fields: str = "*",
    return_geometry: bool = True,
    max_records: int | None = None,
    offset: int = 0,
    order_by_fields: str | None = None,
    f: str = "json",
    out_sr: int | None = 4326,
    page_size: int = 1000,
    max_pages: int = 100,
) -> list[dict[str, Any]]:
    """Paginate through an ArcGIS query and return all feature records."""
    if page_size < 1 or max_pages < 1:
        raise ValueError("page_size and max_pages must be positive")
    core.require_positive_limit(max_records, allow_none=True)
    if offset < 0:
        raise ValueError("offset must be nonnegative")
    records: list[dict[str, Any]] = []
    total_offset = offset
    remaining = max_records
    seen_pages: set[str] = set()
    for _page_number in range(max_pages):
        limit = min(page_size, remaining) if remaining is not None else page_size
        page = query_layer(
            url,
            where=where,
            out_fields=out_fields,
            return_geometry=return_geometry,
            result_record_count=limit,
            result_offset=total_offset,
            order_by_fields=order_by_fields,
            f=f,
            out_sr=out_sr,
        )
        features = page.get("features", [])
        if not isinstance(features, list):
            raise ValueError("ArcGIS query returned invalid features")
        if not features:
            return records
        signature = repr(features)
        if signature in seen_pages:
            raise ValueError("ArcGIS query repeated a page")
        seen_pages.add(signature)
        raw_count = len(features)
        accepted = features[:remaining] if remaining is not None else features
        records.extend(accepted)
        total_offset += raw_count
        if remaining is not None:
            remaining -= len(accepted)
            if remaining <= 0:
                return records
        if raw_count < limit:
            return records
        # Some servers signal pagination via exceededTransferLimit.
        if not page.get("exceededTransferLimit", True):
            return records
    raise ValueError(f"ArcGIS query exceeded {max_pages} pages")


def _signed_area(ring: list[list[float]]) -> float:
    """Return the signed area of a linear ring using the shoelace formula."""
    area = 0.0
    n = len(ring)
    for i in range(n):
        if len(ring[i]) < 2 or len(ring[(i + 1) % n]) < 2:
            raise ValueError("ArcGIS polygon coordinate must contain x and y")
        x1, y1 = ring[i][0], ring[i][1]
        x2, y2 = ring[(i + 1) % n][0], ring[(i + 1) % n][1]
        area += (x1 * y2) - (x2 * y1)
    return area / 2.0


def _normalize_ring(ring: list[list[float]]) -> list[list[float]]:
    """Return a closed ring (append first point if missing)."""
    if not ring:
        return ring
    if ring[0] != ring[-1]:
        return ring + [ring[0]]
    return ring


def _rings_to_geojson(rings: list[list[list[float]]]) -> dict[str, Any]:
    """Convert ArcGIS rings to a GeoJSON Polygon or MultiPolygon."""
    if not rings:
        return {"type": "Polygon", "coordinates": []}
    normalized = [_normalize_ring(ring) for ring in rings]
    # ArcGIS uses clockwise exterior rings and counterclockwise holes. GeoJSON
    # recommends the opposite winding, so reverse both while converting.
    exteriors = [ring for ring in normalized if _signed_area(ring) < 0]
    holes = [ring for ring in normalized if _signed_area(ring) >= 0]
    if not exteriors:
        raise ValueError("ArcGIS polygon has no clockwise exterior ring")

    def contains(ring: list[list[float]], point: list[float]) -> bool:
        if len(point) < 2:
            raise ValueError("ArcGIS polygon coordinate must contain x and y")
        x, y = point[0], point[1]
        inside = False
        for first, second in zip(ring, ring[1:]):
            if len(first) < 2 or len(second) < 2:
                raise ValueError("ArcGIS polygon coordinate must contain x and y")
            x1, y1 = first[0], first[1]
            x2, y2 = second[0], second[1]
            if (y1 > y) != (y2 > y):
                crossing = (x2 - x1) * (y - y1) / (y2 - y1) + x1
                if x < crossing:
                    inside = not inside
        return inside

    polygons: list[list[list[list[float]]]] = [[list(reversed(ring))] for ring in exteriors]
    for hole in holes:
        containing = [
            (abs(_signed_area(exterior)), index)
            for index, exterior in enumerate(exteriors)
            if contains(exterior, hole[0])
        ]
        if not containing:
            raise ValueError("ArcGIS polygon contains a hole outside every exterior ring")
        _, index = min(containing)
        polygons[index].append(list(reversed(hole)))

    if len(polygons) == 1:
        return {"type": "Polygon", "coordinates": polygons[0]}
    return {"type": "MultiPolygon", "coordinates": polygons}


def _paths_to_geojson(paths: list[list[list[float]]]) -> dict[str, Any]:
    """Convert ArcGIS paths to a GeoJSON LineString or MultiLineString."""
    if not paths:
        return {"type": "LineString", "coordinates": []}
    if len(paths) == 1:
        return {"type": "LineString", "coordinates": paths[0]}
    return {"type": "MultiLineString", "coordinates": paths}


def geometry_from_record(record: dict[str, Any]) -> dict[str, Any] | None:
    """Extract and normalize geometry from a feature record."""
    geom = record.get("geometry")
    if not geom:
        return None
    if "x" in geom and "y" in geom:
        return {"type": "Point", "coordinates": [geom["x"], geom["y"]]}
    if "points" in geom:
        return {"type": "MultiPoint", "coordinates": geom["points"]}
    if "rings" in geom:
        return _rings_to_geojson(geom["rings"])
    if "paths" in geom:
        return _paths_to_geojson(geom["paths"])
    return geom


def _attribute_rows(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [r.get("attributes", {}) for r in records]


def csv_safe_value(value: Any) -> str:
    """Return a CSV-safe string, prefixing formula triggers to prevent injection."""
    if value is None:
        return ""
    text = str(value)
    stripped = text.lstrip().lstrip("\ufeff").lstrip()
    if text.startswith(("\t", "\r", "\n", "\v", "\f")) or (
        stripped and stripped[0] in "=+-@"
    ):
        return "'" + text
    return text


def csv_from_records(records: list[dict[str, Any]]) -> str:
    """Convert feature records to a CSV string with unioned keys and formula injection protection."""
    rows = _attribute_rows(records)
    if not rows:
        return ""
    # Preserve key order of the first row while unioning keys from all rows.
    fieldnames: list[str] = []
    seen: set[str] = set()
    for row in rows:
        for key in row.keys():
            if key not in seen:
                seen.add(key)
                fieldnames.append(key)
    safe_rows = [
        {key: csv_safe_value(row.get(key, "")) for key in fieldnames}
        for row in rows
    ]
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow([csv_safe_value(field) for field in fieldnames])
    for row in safe_rows:
        writer.writerow([row.get(field, "") for field in fieldnames])
    return buf.getvalue()


def geojson_from_records(records: list[dict[str, Any]]) -> dict[str, Any]:
    """Convert feature records to a GeoJSON FeatureCollection."""
    features: list[dict[str, Any]] = []
    for record in records:
        geom = geometry_from_record(record)
        features.append(
            {
                "type": "Feature",
                "properties": record.get("attributes", {}),
                "geometry": geom,
            }
        )
    return {"type": "FeatureCollection", "features": features}
