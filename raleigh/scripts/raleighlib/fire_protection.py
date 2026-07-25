"""Wake County MAR Fire Protection proximity data access.

Resolves the Wake County MAR Fire Protection Data table (item
8ab8c4f1a8eb473bacfcc1a1c1980b6c) and provides read-only lookups of
source-provided station rankings, road-network distances, ISO ratings,
and nearest-hydrant distances by canonical site-address identifier (CSAID).

Address input is composed through the official Raleigh locator and the
Wake County MAR Addresses layer to resolve a CSAID. The CLI never
calculates its own station routing, hydrant distance, or ISO rating.
"""

from __future__ import annotations

import json
import urllib.parse
from datetime import datetime, timezone
from typing import Any

from raleighlib import arcgis
from raleighlib import core
from raleighlib import geocode

FIRE_PROTECTION_ITEM_ID = "8ab8c4f1a8eb473bacfcc1a1c1980b6c"
FIRE_PROTECTION_ITEM_URL = (
    "https://ral.maps.arcgis.com/sharing/rest/content/items/" + FIRE_PROTECTION_ITEM_ID
)

MAR_ADDRESSES_LAYER_URL = (
    "https://services1.arcgis.com/a7CWfuGP5ZnLYE7I/arcgis/rest/services/"
    "Wake_County_MAR_Address_Data_Public/FeatureServer/0"
)

MIN_GEOCODE_SCORE = 90.0
MAR_ENVELOPE_DELTA = 0.0001
REQUIRED_PROTECTION_FIELDS = frozenset(
    {
        "CSAID",
        "STATION_RANK",
        "STATION_DISTANCE",
        "STATIONID",
        "STATION_ISO",
        "Hydrant_Distance",
    }
)

PROTECTION_CAVERAT = (
    "Source-provided fire protection proximity data. Distances are "
    "road-network values from the Wake County MAR table; the source does "
    "not advertise distance units. This is not live emergency response "
    "data and must not be used for emergency dispatch."
)


class FireProtectionError(Exception):
    """Raised for fire-protection resolution or query failures."""


def _resolve_fire_protection_layer() -> str:
    """Resolve the fire-protection item ID to a queryable layer URL."""
    params = {"f": "json"}
    url = f"{FIRE_PROTECTION_ITEM_URL}?{urllib.parse.urlencode(params)}"
    meta = core.json_request(url)
    service_url = meta.get("url")
    if not service_url:
        raise FireProtectionError(f"Item {FIRE_PROTECTION_ITEM_ID} has no service URL")
    return arcgis.resolve_queryable_layer(service_url)


def resolve_csaid_from_address(address: str) -> dict[str, Any]:
    """Geocode an address and resolve it to a Wake County MAR CSAID.

    Returns a dict with keys: csaid, match_address, score, lat, lon.
    Raises FireProtectionError on no match, ambiguous match, or when
    the geocoded location cannot be mapped to a MAR record.
    """
    candidates = geocode.find_address_candidates(
        address,
        out_fields="StAddr,SubAddr,Match_addr",
        min_score=MIN_GEOCODE_SCORE,
        max_locations=5,
    )
    if not candidates:
        raise FireProtectionError(
            f"No geocode match for '{address}' at score >= {MIN_GEOCODE_SCORE:.0f}"
        )

    top_score = max(candidate.get("score", 0) or 0 for candidate in candidates)
    top_candidates = [
        candidate
        for candidate in candidates
        if (candidate.get("score", 0) or 0) == top_score
    ]
    identities = {
        (
            candidate.get("address"),
            candidate.get("location", {}).get("x"),
            candidate.get("location", {}).get("y"),
        )
        for candidate in top_candidates
    }
    if len(identities) != 1:
        raise FireProtectionError(
            f"Address '{address}' has {len(identities)} equally ranked geocode "
            "matches; refine the address or supply --csaid directly"
        )

    best = top_candidates[0]
    location = best.get("location", {})
    lat = location.get("y")
    lon = location.get("x")
    if lat is None or lon is None:
        raise FireProtectionError(f"Geocode match for '{address}' has no coordinates")

    match_address = best.get("address", "")
    score = best.get("score")
    attributes = best.get("attributes", {})
    if not isinstance(attributes, dict):
        attributes = {}
    street_address = attributes.get("StAddr")
    subaddress = attributes.get("SubAddr")
    if isinstance(street_address, str) and street_address.strip():
        mar_match_address = " ".join(
            value.strip()
            for value in (street_address, subaddress)
            if isinstance(value, str) and value.strip()
        )
    else:
        mar_match_address = match_address.split(",", 1)[0]

    csaid = _spatial_resolve_csaid(lon, lat, mar_match_address)
    if csaid is None:
        raise FireProtectionError(
            f"Address '{match_address}' geocoded but no unique Wake County "
            "MAR record found nearby; supply --csaid directly"
        )

    return {
        "csaid": csaid,
        "match_address": match_address,
        "score": score,
        "lat": lat,
        "lon": lon,
    }


def _spatial_resolve_csaid(lon: float, lat: float, match_address: str) -> int | None:
    """Query the MAR Addresses layer near a point and return a unique CSAID.

    Uses a small envelope around the geocoded point and prefers an exact
    matched-address record. If none exists, it prefers base addresses over
    unit-level records. Returns None when zero or multiple distinct CSAIDs
    remain after filtering.
    """
    delta = MAR_ENVELOPE_DELTA
    geometry = json.dumps(
        {
            "xmin": lon - delta,
            "ymin": lat - delta,
            "xmax": lon + delta,
            "ymax": lat + delta,
            "spatialReference": {"wkid": 4326},
        }
    )
    params: dict[str, Any] = {
        "geometry": geometry,
        "geometryType": "esriGeometryEnvelope",
        "inSR": 4326,
        "spatialRel": "esriSpatialRelIntersects",
        "outFields": "CSAID,ADDRESS,SUBADDR_TYPE",
        "returnGeometry": "false",
        "f": "json",
    }
    url = f"{MAR_ADDRESSES_LAYER_URL}/query?{urllib.parse.urlencode(params)}"
    data = core.json_request(url)
    core.raise_for_arcgis_error(data, "MAR address lookup")
    features = data.get("features", [])
    if not isinstance(features, list):
        return None

    base_csaids: set[int] = set()
    all_csaids: set[int] = set()
    exact_csaids: set[int] = set()
    normalized_match = match_address.strip().casefold()
    for feature in features:
        attrs = feature.get("attributes", {})
        csaid = attrs.get("CSAID")
        if not isinstance(csaid, int) or isinstance(csaid, bool):
            continue
        all_csaids.add(csaid)
        mar_address = attrs.get("ADDRESS")
        if (
            isinstance(mar_address, str)
            and mar_address.strip().casefold() == normalized_match
        ):
            exact_csaids.add(csaid)
        subaddr = attrs.get("SUBADDR_TYPE")
        if subaddr is None or (isinstance(subaddr, str) and not subaddr.strip()):
            base_csaids.add(csaid)

    candidates = exact_csaids or base_csaids or all_csaids
    if len(candidates) == 1:
        return candidates.pop()
    return None


def query_fire_protection(csaid: int) -> dict[str, Any]:
    """Query the MAR Fire Protection table for a given CSAID.

    Returns a dict with source metadata and the ranked station records.
    """
    layer_url = _resolve_fire_protection_layer()
    fields = arcgis.layer_fields(layer_url)
    field_names = {field.get("name") for field in fields if isinstance(field, dict)}
    missing_fields = REQUIRED_PROTECTION_FIELDS - field_names
    if missing_fields:
        missing = ", ".join(sorted(missing_fields))
        raise FireProtectionError(
            f"Fire protection source schema drift: missing fields: {missing}"
        )

    where = f"CSAID = {int(csaid)}"
    records = arcgis.query_all_pages(
        layer_url,
        where=where,
        return_geometry=False,
        max_records=10,
        order_by_fields="STATION_RANK ASC",
    )

    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    stations: list[dict[str, Any]] = []
    hydrant_distances: set[Any] = set()

    for record in records:
        attrs = record.get("attributes", {})
        rank = attrs.get("STATION_RANK")
        station: dict[str, Any] = {
            "rank": rank,
            "station_id": attrs.get("STATIONID"),
            "distance": attrs.get("STATION_DISTANCE"),
            "iso": attrs.get("STATION_ISO"),
        }
        stations.append(station)
        if attrs.get("Hydrant_Distance") is not None:
            hydrant_distances.add(attrs.get("Hydrant_Distance"))

    if len(hydrant_distances) > 1:
        raise FireProtectionError(
            f"Fire protection source returned inconsistent hydrant distances "
            f"for CSAID {csaid}"
        )
    hydrant_distance = next(iter(hydrant_distances), None)

    return {
        "csaid": csaid,
        "item_id": FIRE_PROTECTION_ITEM_ID,
        "retrieved_at": now,
        "stations": stations,
        "hydrant_distance": hydrant_distance,
        "distance_units": None,
        "caveats": PROTECTION_CAVERAT,
    }
