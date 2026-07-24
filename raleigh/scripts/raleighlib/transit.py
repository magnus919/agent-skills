"""GoRaleigh GTFS and GTFS-Realtime adapter."""

from __future__ import annotations

import csv
import copy
import hashlib
import io
import zipfile
from datetime import date, datetime, timezone
from typing import Any

from raleighlib import core


STATIC_FEED = "https://goraleigh.org/gr_gtfs"
REALTIME_BASE = "https://www.goraleighlive.org/gtfsrt"

# GTFS ZIP safety caps.
MAX_GTFS_ZIP_BYTES = 50 * 1024 * 1024
MAX_GTFS_MEMBERS = 100
MAX_GTFS_MEMBER_SIZE = 64 * 1024 * 1024
MAX_GTFS_TOTAL_UNCOMPRESSED = 200 * 1024 * 1024

REQUIRED_GTFS_FIELDS = {
    "agency": {"agency_name", "agency_url", "agency_timezone"},
    "stops": {"stop_id", "stop_name", "stop_lat", "stop_lon"},
    "routes": {"route_id", "route_type"},
    "trips": {"route_id", "service_id", "trip_id"},
    "stop_times": {"trip_id", "arrival_time", "departure_time", "stop_id", "stop_sequence"},
}
CALENDAR_FIELDS = {
    "service_id", "monday", "tuesday", "wednesday", "thursday", "friday",
    "saturday", "sunday", "start_date", "end_date",
}
CALENDAR_DATES_FIELDS = {"service_id", "date", "exception_type"}


def download_gtfs(url: str = STATIC_FEED, max_bytes: int = MAX_GTFS_ZIP_BYTES) -> bytes:
    """Download the static GTFS ZIP archive."""
    return core.raw_request(url, max_bytes=max_bytes)


def _parse_gtfs_zip(data: bytes) -> dict[str, list[dict[str, str]]]:
    """Parse required GTFS tables from a ZIP archive with bounded size checks."""
    if len(data) > MAX_GTFS_ZIP_BYTES:
        raise ValueError(f"GTFS ZIP archive exceeds {MAX_GTFS_ZIP_BYTES} bytes")
    feed: dict[str, list[dict[str, str]]] = {}
    total_uncompressed = 0
    with zipfile.ZipFile(io.BytesIO(data)) as zf:
        members = zf.infolist()
        if len(members) > MAX_GTFS_MEMBERS:
            raise ValueError(f"GTFS ZIP contains more than {MAX_GTFS_MEMBERS} members")
        for info in members:
            if info.file_size > MAX_GTFS_MEMBER_SIZE:
                raise ValueError(f"GTFS ZIP member {info.filename} exceeds {MAX_GTFS_MEMBER_SIZE} bytes")
            total_uncompressed += info.file_size
            if total_uncompressed > MAX_GTFS_TOTAL_UNCOMPRESSED:
                raise ValueError(f"GTFS ZIP uncompressed total exceeds {MAX_GTFS_TOTAL_UNCOMPRESSED} bytes")
        for name in zf.namelist():
            if not name.endswith(".txt"):
                continue
            table = name.replace(".txt", "")
            with zf.open(name) as f:
                reader = csv.DictReader(io.TextIOWrapper(f, encoding="utf-8-sig"))
                feed[table] = list(reader)
    return feed


def parse_gtfs_zip(data: bytes) -> dict[str, list[dict[str, str]]]:
    """Validate and parse a GTFS archive, normalizing malformed ZIP errors."""
    try:
        feed = _parse_gtfs_zip(data)
        _validate_gtfs_feed(feed)
        return feed
    except (zipfile.BadZipFile, csv.Error, UnicodeError) as exc:
        raise ValueError("GTFS ZIP archive is malformed") from exc


def _validate_table(
    feed: dict[str, list[dict[str, str]]],
    table: str,
    required_fields: set[str],
) -> None:
    rows = feed.get(table)
    if not isinstance(rows, list) or not rows:
        raise ValueError(f"GTFS archive is missing non-empty {table}.txt")
    for index, row in enumerate(rows, start=2):
        if not isinstance(row, dict) or None in row:
            raise ValueError(f"GTFS {table}.txt row {index} is malformed")
        missing = [field for field in required_fields if not str(row.get(field, "")).strip()]
        if missing:
            raise ValueError(
                f"GTFS {table}.txt row {index} is missing required values: {', '.join(sorted(missing))}"
            )


def _validate_gtfs_feed(feed: dict[str, list[dict[str, str]]]) -> None:
    """Require the semantic core of a usable GTFS Schedule dataset."""
    for table, fields in REQUIRED_GTFS_FIELDS.items():
        _validate_table(feed, table, fields)
    for index, row in enumerate(feed["routes"], start=2):
        if not (str(row.get("route_short_name", "")).strip() or str(row.get("route_long_name", "")).strip()):
            raise ValueError(
                f"GTFS routes.txt row {index} requires route_short_name or route_long_name"
            )
    if feed.get("calendar"):
        _validate_table(feed, "calendar", CALENDAR_FIELDS)
    if feed.get("calendar_dates"):
        _validate_table(feed, "calendar_dates", CALENDAR_DATES_FIELDS)
    if not feed.get("calendar") and not feed.get("calendar_dates"):
        raise ValueError("GTFS archive requires calendar.txt or calendar_dates.txt")


def _load_feed_with_cache() -> dict[str, list[dict[str, str]]]:
    archive = core.read_cache_bytes(
        "gtfs-feed.zip", max_age_seconds=86400, max_bytes=MAX_GTFS_ZIP_BYTES
    )
    metadata = core.read_cache("gtfs-feed-metadata.json", max_age_seconds=86400)
    if archive is not None and isinstance(metadata, dict):
        digest = hashlib.sha256(archive).hexdigest()
        if (
            metadata.get("source_url") == STATIC_FEED
            and metadata.get("validated") is True
            and metadata.get("sha256") == digest
            and metadata.get("archive_bytes") == len(archive)
        ):
            try:
                return parse_gtfs_zip(archive)
            except (ValueError, zipfile.BadZipFile):
                pass
    data = download_gtfs()
    feed = parse_gtfs_zip(data)
    core.write_cache_bytes("gtfs-feed.zip", data)
    core.write_cache("gtfs-feed-metadata.json", {
        "source_url": STATIC_FEED,
        "retrieved_at": datetime.now(timezone.utc).isoformat(),
        "archive_bytes": len(data),
        "sha256": hashlib.sha256(data).hexdigest(),
        "validated": True,
        "tables": sorted(feed),
        "feed_info": feed.get("feed_info", [])[:1],
    })
    return feed


def get_routes(feed: dict[str, list[dict[str, str]]] | None = None) -> list[dict[str, str]]:
    """List all routes from the static feed."""
    if feed is None:
        feed = _load_feed_with_cache()
    return feed.get("routes", [])


def get_stops(feed: dict[str, list[dict[str, str]]] | None = None) -> list[dict[str, str]]:
    """List all stops from the static feed."""
    if feed is None:
        feed = _load_feed_with_cache()
    return feed.get("stops", [])


def _today_date() -> str:
    return date.today().strftime("%Y%m%d")


def _service_ids_for_date(feed: dict[str, list[dict[str, str]]], target_date: str) -> set[str]:
    """Return active service IDs for a date (YYYYMMDD)."""
    weekday = datetime.strptime(target_date, "%Y%m%d").strftime("%A").lower()
    calendar = feed.get("calendar", [])
    services: set[str] = set()
    for row in calendar:
        if row.get("start_date", "") <= target_date <= row.get("end_date", ""):
            if row.get(weekday, "0") == "1":
                services.add(row["service_id"])
    for row in feed.get("calendar_dates", []):
        if row.get("date") == target_date:
            if row.get("exception_type") == "1":
                services.add(row["service_id"])
            elif row.get("exception_type") == "2":
                services.discard(row["service_id"])
    return services


def get_schedule_for_route(
    route_id: str,
    target_date: str | None = None,
    feed: dict[str, list[dict[str, str]]] | None = None,
) -> list[dict[str, Any]]:
    """Return scheduled trips and stop times for a route on a date."""
    if feed is None:
        feed = _load_feed_with_cache()
    if target_date is None:
        target_date = _today_date()
    services = _service_ids_for_date(feed, target_date)
    trips = [t for t in feed.get("trips", []) if t.get("route_id") == route_id and t.get("service_id") in services]
    trip_ids = {t["trip_id"] for t in trips}
    times = [s for s in feed.get("stop_times", []) if s.get("trip_id") in trip_ids]
    times.sort(key=lambda s: (s.get("trip_id", ""), int(s.get("stop_sequence", 0) or 0)))
    return [
        {
            "trip_id": t.get("trip_id"),
            "stop_id": t.get("stop_id"),
            "stop_sequence": t.get("stop_sequence"),
            "arrival_time": t.get("arrival_time"),
            "departure_time": t.get("departure_time"),
        }
        for t in times
    ]


def get_arrivals_for_stop(
    stop_id: str,
    feed: dict[str, list[dict[str, str]]] | None = None,
) -> list[dict[str, Any]]:
    """Return scheduled arrivals for a stop."""
    if feed is None:
        feed = _load_feed_with_cache()
    target_date = _today_date()
    services = _service_ids_for_date(feed, target_date)
    trip_ids = {t["trip_id"] for t in feed.get("trips", []) if t.get("service_id") in services}
    times = [
        s
        for s in feed.get("stop_times", [])
        if s.get("stop_id") == stop_id and s.get("trip_id") in trip_ids
    ]
    times.sort(key=lambda s: s.get("arrival_time", ""))
    return [
        {
            "trip_id": t.get("trip_id"),
            "arrival_time": t.get("arrival_time"),
            "departure_time": t.get("departure_time"),
        }
        for t in times
    ]


def _decode_realtime(data: bytes) -> dict[str, Any]:
    """Decode GTFS-Realtime protobuf using vendored gtfs_realtime_pb2.

    Requires the optional ``google.protobuf`` runtime (>= 6.31.1, < 7).
    The vendored descriptor provides message definitions but does not replace
    the runtime.
    """
    try:
        from raleighlib import gtfs_realtime_pb2
        from google.protobuf.message import DecodeError
    except Exception as exc:
        raise ValueError(
            "GTFS-Realtime decoding requires google.protobuf>=6.31.1,<7"
        ) from exc

    msg = gtfs_realtime_pb2.FeedMessage()
    try:
        msg.ParseFromString(data)
    except DecodeError as exc:
        raise ValueError("GTFS-Realtime feed is malformed") from exc
    if not msg.IsInitialized() or not msg.HasField("header"):
        raise ValueError("GTFS-Realtime feed is missing required fields")
    if not msg.header.IsInitialized() or not msg.header.gtfs_realtime_version.strip():
        raise ValueError("GTFS-Realtime feed has an invalid required header")
    for entity in msg.entity:
        payloads = [
            field.name
            for field in entity.DESCRIPTOR.fields
            if field.message_type is not None
            and not field.is_repeated
            and entity.HasField(field.name)
        ]
        if entity.is_deleted:
            if payloads:
                raise ValueError(
                    "GTFS-Realtime deleted entity must not include a payload"
                )
        elif len(payloads) != 1:
            raise ValueError(
                "GTFS-Realtime entity must include exactly one payload"
            )
    return _protobuf_to_dict(msg)


def _protobuf_to_dict(msg) -> dict[str, Any]:
    """Minimal recursive converter for protobuf messages."""
    from google.protobuf.descriptor import FieldDescriptor

    result: dict[str, Any] = {}
    for field in msg.DESCRIPTOR.fields:
        value = getattr(msg, field.name)
        is_repeated = field.is_repeated
        if not is_repeated and not msg.HasField(field.name):
            continue
        if field.type == FieldDescriptor.TYPE_MESSAGE:
            if is_repeated:
                result[field.name] = [_protobuf_to_dict(v) for v in value]
            else:
                result[field.name] = _protobuf_to_dict(value)
        else:
            if is_repeated:
                result[field.name] = list(value)
            else:
                result[field.name] = value
    return result


def fetch_realtime(kind: str) -> dict[str, Any]:
    """Fetch and decode a GTFS-Realtime feed (alerts, trips, or vehicles)."""
    if kind not in {"alerts", "trips", "vehicles"}:
        raise ValueError(f"Invalid realtime kind: {kind}")
    url = f"{REALTIME_BASE}/{kind}"
    data = core.raw_request(url)
    return _decode_realtime(data)


def _entity_staleness(entity: dict[str, Any]) -> float | None:
    """Return seconds since the entity's timestamp if available."""
    ts = None
    for key in ("vehicle", "trip_update", "alert"):
        if key in entity:
            ts = entity[key].get("timestamp")
            break
    if ts:
        return datetime.now(timezone.utc).timestamp() - ts
    return None


def enrich_realtime_with_static(
    entities: list[dict[str, Any]],
    feed: dict[str, list[dict[str, str]]],
    header_timestamp: int | None = None,
) -> list[dict[str, Any]]:
    """Add static route/trip/stop names, feed timestamp, and staleness to realtime entities."""
    routes = {r.get("route_id"): r for r in feed.get("routes", [])}
    trips = {t.get("trip_id"): t for t in feed.get("trips", [])}
    stops = {s.get("stop_id"): s for s in feed.get("stops", [])}
    now = datetime.now(timezone.utc).timestamp()
    enriched: list[dict[str, Any]] = []
    for entity in entities:
        item = copy.deepcopy(entity)
        trip_id = None
        route_id = None
        if "vehicle" in entity:
            trip_id = entity["vehicle"].get("trip", {}).get("trip_id")
            route_id = entity["vehicle"].get("trip", {}).get("route_id")
        elif "trip_update" in entity:
            trip_id = entity["trip_update"].get("trip", {}).get("trip_id")
            route_id = entity["trip_update"].get("trip", {}).get("route_id")
        if trip_id and trip_id in trips:
            item["trip_id"] = trip_id
            route_id = route_id or trips[trip_id].get("route_id")
            item["route_id"] = route_id
        if route_id and route_id in routes:
            item["route_short_name"] = routes[route_id].get("route_short_name")
            item["route_long_name"] = routes[route_id].get("route_long_name")
        if "trip_update" in entity:
            for update in item["trip_update"].get("stop_time_update", []):
                sid = update.get("stop_id")
                if sid and sid in stops:
                    update["stop_name"] = stops[sid].get("stop_name")
        if "alert" in item:
            for informed in item["alert"].get("informed_entity", []):
                route_id = informed.get("route_id")
                trip_id = informed.get("trip", {}).get("trip_id")
                stop_id = informed.get("stop_id")
                if route_id and route_id in routes:
                    informed["route_short_name"] = routes[route_id].get("route_short_name")
                    informed["route_long_name"] = routes[route_id].get("route_long_name")
                if trip_id and trip_id in trips:
                    informed["trip_headsign"] = trips[trip_id].get("trip_headsign")
                    informed["trip_route_id"] = trips[trip_id].get("route_id")
                if stop_id and stop_id in stops:
                    informed["stop_name"] = stops[stop_id].get("stop_name")
        item["feed_header_timestamp"] = header_timestamp
        entity_ts = _entity_staleness(entity)
        if header_timestamp is not None:
            item["staleness_seconds"] = now - header_timestamp
        elif entity_ts is not None:
            item["staleness_seconds"] = entity_ts
        else:
            item["staleness_seconds"] = None
        enriched.append(item)
    return enriched


def _realtime_envelope(
    feed: dict[str, Any], entities: list[dict[str, Any]]
) -> dict[str, Any]:
    header_ts = feed.get("header", {}).get("timestamp")
    now = datetime.now(timezone.utc).timestamp()
    return {
        "feed_timestamp": header_ts,
        "staleness_seconds": now - header_ts if header_ts else None,
        "entities": entities,
    }


def get_alerts(limit: int = 20) -> dict[str, Any]:
    """Fetch and return service alerts."""
    core.require_positive_limit(limit)
    feed = fetch_realtime("alerts")
    static = _load_feed_with_cache()
    header_ts = feed.get("header", {}).get("timestamp")
    entities = enrich_realtime_with_static(feed.get("entity", [])[:limit], static, header_ts)
    return _realtime_envelope(feed, entities)


def get_trip_updates(route: str | None = None, limit: int = 20) -> dict[str, Any]:
    """Fetch and return trip updates, optionally filtered by route."""
    core.require_positive_limit(limit)
    feed = fetch_realtime("trips")
    entities = feed.get("entity", [])
    if route:
        static = _load_feed_with_cache()
        trips = {t.get("trip_id"): t for t in static.get("trips", [])}
        entities = [
            e for e in entities
            if trips.get(e.get("trip_update", {}).get("trip", {}).get("trip_id"), {}).get("route_id") == route
        ]
    static = _load_feed_with_cache()
    header_ts = feed.get("header", {}).get("timestamp")
    enriched = enrich_realtime_with_static(entities[:limit], static, header_ts)
    return _realtime_envelope(feed, enriched)


def filter_vehicle_positions(
    entities: list[dict[str, Any]],
    feed: dict[str, list[dict[str, str]]],
    route: str | None = None,
    stop: str | None = None,
    limit: int = 20,
) -> list[dict[str, Any]]:
    """Filter and limit vehicle positions by route/stop."""
    core.require_positive_limit(limit)
    trips = {t.get("trip_id"): t for t in feed.get("trips", [])}
    routes = {r.get("route_id"): r for r in feed.get("routes", [])}
    filtered: list[dict[str, Any]] = []
    for entity in entities:
        vehicle = entity.get("vehicle", {})
        trip_id = vehicle.get("trip", {}).get("trip_id")
        stop_id = vehicle.get("stop_id")
        trip = trips.get(trip_id) if trip_id else None
        route_id = trip.get("route_id") if trip else vehicle.get("trip", {}).get("route_id")
        if route and route_id != route:
            continue
        if stop and stop_id != stop:
            continue
        if trip_id:
            entity["trip_id"] = trip_id
        if route_id:
            entity["route_id"] = route_id
        if route_id and route_id in routes:
            entity["route_short_name"] = routes[route_id].get("route_short_name")
            entity["route_long_name"] = routes[route_id].get("route_long_name")
        filtered.append(entity)
        if len(filtered) >= limit:
            break
    return filtered


def get_vehicle_positions(route: str | None = None, limit: int = 20) -> dict[str, Any]:
    """Fetch and return vehicle positions, optionally filtered by route."""
    core.require_positive_limit(limit)
    feed = fetch_realtime("vehicles")
    entities = feed.get("entity", [])
    static = _load_feed_with_cache()
    filtered = filter_vehicle_positions(entities, static, route=route, limit=limit)
    header_ts = feed.get("header", {}).get("timestamp")
    enriched = enrich_realtime_with_static(filtered, static, header_ts)
    return _realtime_envelope(feed, enriched)
