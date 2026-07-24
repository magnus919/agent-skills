"""Raleigh public geocoding adapter."""

from __future__ import annotations

import json
import urllib.parse
from typing import Any

from raleighlib import core


GEOCODE_URL = "https://maps.raleighnc.gov/arcgis/rest/services/Locators/Locator/GeocodeServer"


def find_address_candidates(
    address: str,
    out_fields: str | None = None,
    out_sr: int = 4326,
    max_locations: int = 10,
    min_score: float | None = None,
) -> list[dict[str, Any]]:
    """Forward geocode a single-line address."""
    core.require_positive_limit(max_locations)
    params: dict[str, Any] = {
        "SingleLine": address,
        "outSR": out_sr,
        "maxLocations": max_locations,
        "f": "json",
    }
    if out_fields:
        params["outFields"] = out_fields
    url = f"{GEOCODE_URL}/findAddressCandidates?{urllib.parse.urlencode(params)}"
    data = core.json_request(url)
    core.raise_for_arcgis_error(data, "Forward geocoding")
    candidates = core.require_object_list(data.get("candidates", []), "Forward geocoding")
    return filter_candidates(candidates, min_score=min_score)


def reverse_geocode(
    lat: float,
    lon: float,
    out_sr: int = 4326,
    distance: int | None = None,
) -> dict[str, Any]:
    """Reverse geocode a coordinate."""
    params: dict[str, Any] = {
        "location": json.dumps({
            "x": lon,
            "y": lat,
            "spatialReference": {"wkid": 4326},
        }),
        "outSR": out_sr,
        "f": "json",
    }
    if distance is not None:
        params["distance"] = distance
    url = f"{GEOCODE_URL}/reverseGeocode?{urllib.parse.urlencode(params)}"
    result = core.json_request(url)
    core.raise_for_arcgis_error(result, "Reverse geocoding")
    return result


def suggest(
    text: str,
    out_sr: int = 4326,
    max_suggestions: int = 10,
) -> list[dict[str, Any]]:
    """Return address suggestions for a partial string."""
    core.require_positive_limit(max_suggestions)
    params: dict[str, Any] = {
        "text": text,
        "outSR": out_sr,
        "maxSuggestions": max_suggestions,
        "f": "json",
    }
    url = f"{GEOCODE_URL}/suggest?{urllib.parse.urlencode(params)}"
    data = core.json_request(url)
    core.raise_for_arcgis_error(data, "Address suggestion")
    return core.require_object_list(data.get("suggestions", []), "Address suggestion")


MAX_BATCH_SIZE = 1000


def geocode_addresses(
    records: list[dict[str, Any]],
    out_sr: int = 4326,
    out_fields: str | None = None,
    max_batch: int = MAX_BATCH_SIZE,
) -> list[dict[str, Any]]:
    """Batch geocode address records using POST form data.

    Every input row is preserved in the output with a status of ``matched``,
    ``unmatched``, or ``error``. The batch size is capped to avoid oversized
    requests.
    """
    if not records:
        return []
    core.require_positive_limit(max_batch)
    if len(records) > max_batch:
        raise ValueError(f"Batch geocoding limit is {max_batch} addresses")
    prepared: list[tuple[Any, int, dict[str, Any]]] = []
    used_request_ids: set[int] = set()
    for ordinal, record in enumerate(records, start=1):
        source = dict(record)
        source_id = source.get("OBJECTID", ordinal)
        request_id = source_id if isinstance(source_id, int) and not isinstance(source_id, bool) else ordinal
        if request_id in used_request_ids:
            request_id = ordinal
            while request_id in used_request_ids:
                request_id += len(records)
        used_request_ids.add(request_id)
        prepared.append((source_id, request_id, source))
    wrapped_records = [{"attributes": {**source, "OBJECTID": request_id}} for _, request_id, source in prepared]
    params: dict[str, Any] = {
        "addresses": json.dumps({"records": wrapped_records}),
        "outSR": out_sr,
        "f": "json",
    }
    if out_fields:
        params["outFields"] = out_fields
    data = core.json_request(
        f"{GEOCODE_URL}/geocodeAddresses",
        method="POST",
        data=urllib.parse.urlencode(params).encode("utf-8"),
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    core.raise_for_arcgis_error(data, "Batch geocoding")
    results: dict[str, dict[str, Any]] = {}
    locations = core.require_object_list(data.get("locations", []), "Batch geocoding")
    for loc in locations:
        attrs = loc.get("attributes", {})
        rid = attrs.get("ResultID")
        score = attrs.get("Score")
        matched = score is not None and score > 0
        results[str(rid)] = {
            "score": score,
            "address": attrs.get("Match_addr") or attrs.get("MatchAddress"),
            "lat": loc.get("location", {}).get("y"),
            "lon": loc.get("location", {}).get("x"),
            "status": "matched" if matched else "unmatched",
            "attributes": attrs,
        }
    outputs: list[dict[str, Any]] = []
    for source_id, request_id, source in prepared:
        result = results.get(str(request_id)) or results.get(str(source_id))
        if result:
            outputs.append({"input_id": source_id, "source": source, **result})
        else:
            outputs.append(
                {
                    "input_id": source_id,
                    "source": source,
                    "score": None,
                    "address": None,
                    "lat": None,
                    "lon": None,
                    "status": "unmatched",
                    "attributes": {},
                }
            )
    return outputs


def geocode_with_magic_key(
    text: str,
    magic_key: str,
    out_sr: int = 4326,
    max_locations: int = 1,
) -> list[dict[str, Any]]:
    """Geocode a suggestion using its magicKey."""
    core.require_positive_limit(max_locations)
    params: dict[str, Any] = {
        "SingleLine": text,
        "magicKey": magic_key,
        "outSR": out_sr,
        "maxLocations": max_locations,
        "f": "json",
    }
    url = f"{GEOCODE_URL}/findAddressCandidates?{urllib.parse.urlencode(params)}"
    data = core.json_request(url)
    core.raise_for_arcgis_error(data, "Magic-key geocoding")
    return core.require_object_list(data.get("candidates", []), "Magic-key geocoding")


def filter_candidates(
    candidates: list[dict[str, Any]],
    min_score: float | None = None,
) -> list[dict[str, Any]]:
    """Filter candidates by minimum score."""
    if min_score is None:
        return candidates
    return [c for c in candidates if (c.get("score") or 0) >= min_score]
