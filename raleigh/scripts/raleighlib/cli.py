"""Command-line interface for the Raleigh civic-data skill."""

from __future__ import annotations

import argparse
import csv
import io
import json
import math
import os
import re
import sys
import urllib.error
import urllib.parse
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

from raleighlib import core
from raleighlib import hub
from raleighlib import arcgis
from raleighlib import imagery
from raleighlib import geocode
from raleighlib import transit
from raleighlib import development
from raleighlib import civic
from raleighlib import meetings
from raleighlib import police
from raleighlib import fire
from raleighlib import fire_protection
from raleighlib import rfd_reports
from raleighlib import incidents


def _output_json(data: Any) -> None:
    json.dump(data, sys.stdout, indent=2)
    sys.stdout.write("\n")


def _output_table(headers: list[str], rows: list[list[str]]) -> None:
    if not rows:
        return
    widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            widths[i] = max(widths[i], len(str(cell)))
    fmt = "  ".join(f"{{:{w}}}" for w in widths)
    print(fmt.format(*headers))
    print(fmt.format(*["-" * w for w in widths]))
    for row in rows:
        print(fmt.format(*(str(c) for c in row)))


def cli_error(message: str) -> SystemExit:
    """Return a SystemExit with concise stderr message."""
    return SystemExit(f"Error: {message}")


def _positive_int(value: str) -> int:
    number = int(value)
    if not 1 <= number <= 100_000:
        raise argparse.ArgumentTypeError("value must be between 1 and 100000")
    return number


def _csaid_value(value: str) -> int:
    number = int(value)
    if not 1 <= number <= 99_999_999:
        raise argparse.ArgumentTypeError("CSAID must be between 1 and 99999999")
    return number


def _nonnegative_int(value: str) -> int:
    number = int(value)
    if not 0 <= number <= 100_000_000:
        raise argparse.ArgumentTypeError("value must be between 0 and 100000000")
    return number


def _timeout_seconds(value: str) -> int:
    number = int(value)
    if not 1 <= number <= 600:
        raise argparse.ArgumentTypeError("timeout must be between 1 and 600 seconds")
    return number


def _year(value: str) -> int:
    number = int(value)
    if not 1900 <= number <= 2100:
        raise argparse.ArgumentTypeError("year must be between 1900 and 2100")
    return number


def _score(value: str) -> float:
    number = float(value)
    if not math.isfinite(number) or not 0 <= number <= 100:
        raise argparse.ArgumentTypeError("score must be finite and between 0 and 100")
    return number


def _latitude(value: str) -> float:
    number = float(value)
    if not math.isfinite(number) or not -90 <= number <= 90:
        raise argparse.ArgumentTypeError("latitude must be finite and between -90 and 90")
    return number


def _longitude(value: str) -> float:
    number = float(value)
    if not math.isfinite(number) or not -180 <= number <= 180:
        raise argparse.ArgumentTypeError("longitude must be finite and between -180 and 180")
    return number


def _iso_date(value: str) -> str:
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        raise argparse.ArgumentTypeError("date must use YYYY-MM-DD")
    try:
        parsed = date.fromisoformat(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("date must use YYYY-MM-DD") from exc
    return parsed.isoformat()


def _nonempty_text(value: str) -> str:
    value = value.strip()
    if not value:
        raise argparse.ArgumentTypeError("value must not be empty")
    if len(value) > 200 or any(ord(char) < 32 for char in value):
        raise argparse.ArgumentTypeError("value is invalid")
    return value


def _service_date(value: str) -> str:
    try:
        datetime.strptime(value, "%Y%m%d")
    except ValueError as exc:
        raise argparse.ArgumentTypeError("date must use YYYYMMDD") from exc
    return value


def _bbox_value(value: str) -> str:
    _parse_bbox(value)
    return value


def _point_value(value: str) -> str:
    _parse_point(value)
    return value


def _latlon_value(value: str) -> str:
    parts = value.split(",")
    if len(parts) != 2:
        raise argparse.ArgumentTypeError("coordinate must be lat,lon")
    _latitude(parts[0].strip())
    _longitude(parts[1].strip())
    return value


def _size_value(value: str) -> str:
    try:
        _parse_size(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(str(exc)) from exc
    return value


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="raleigh",
        description="CLI for the City of Raleigh civic data and services.",
    )
    parser.add_argument(
        "--json", action="store_true", help="Emit machine-readable JSON output."
    )
    parser.add_argument(
        "--cache-dir", help="Override the default cache directory."
    )
    parser.add_argument(
        "--refresh", action="store_true", help="Bypass cache for catalog operations."
    )
    parser.add_argument(
        "--timeout", type=_timeout_seconds, default=30, help="HTTP timeout in seconds."
    )
    sub = parser.add_subparsers(dest="command", help="Available commands")

    # Legacy / core dataset commands.
    cat_p = sub.add_parser("catalog", help="List datasets from the live catalog.")
    cat_p.add_argument("--limit", type=_positive_int, default=100, help="Maximum datasets to display.")
    cat_p.add_argument("--category", help="Filter by category substring.")
    cat_p.add_argument("--search", help="Filter by search term.")
    search_p = sub.add_parser("search", help="Search the live catalog.")
    search_p.add_argument("query", help="Search terms.")
    search_p.add_argument("--limit", type=_positive_int, default=20, help="Maximum results.")

    info_p = sub.add_parser("info", help="Show dataset info.")
    info_p.add_argument("dataset", help="Dataset title or ID.")

    query_p = sub.add_parser("query", help="Query records from a dataset.")
    query_p.add_argument("dataset", help="Dataset title or ID.")
    query_p.add_argument("--where", default="1=1", help="SQL WHERE clause.")
    query_p.add_argument("--limit", type=_positive_int, default=10, help="Maximum records.")
    query_p.add_argument("--offset", type=_nonnegative_int, default=0, help="Records to skip.")
    query_p.add_argument("--out-fields", default="*", help="Comma-separated fields.")
    query_p.add_argument("--no-geometry", action="store_true", help="Omit geometry.")
    query_p.add_argument("--order-by", help="ORDER BY fields.")
    query_p.add_argument("--csv", action="store_true", help="Emit CSV output.")

    download_p = sub.add_parser("download", help="Download records from a dataset.")
    download_p.add_argument("dataset", help="Dataset title or ID.")
    download_p.add_argument("--where", default="1=1", help="SQL WHERE clause.")
    download_p.add_argument("--limit", type=_positive_int, default=1000, help="Maximum records.")
    download_p.add_argument("--all", action="store_true", help="Fetch all records; overrides --limit.")
    download_p.add_argument("--out-fields", default="*", help="Comma-separated fields.")
    download_p.add_argument("--no-geometry", action="store_true", help="Omit geometry.")
    download_p.add_argument("-f", "--format", default="csv", choices=["csv", "geojson", "json"])
    download_p.add_argument("-o", "--output", required=True, help="Output file path.")
    download_p.add_argument("--force", action="store_true", help="Overwrite an existing output file.")

    sub.add_parser("categories", help="List catalog categories.")

    # Imagery commands.
    img = sub.add_parser("imagery", help="ArcGIS ImageServer imagery operations.")
    img_sub = img.add_subparsers(dest="imagery_command")
    img_cat = img_sub.add_parser("catalog", help="List imagery services.")
    img_cat.add_argument("--limit", type=_positive_int, default=100, help="Maximum services to display.")
    img_info = img_sub.add_parser("info", help="Show imagery service metadata.")
    img_info.add_argument("service", help="Service name or URL.")
    img_export = img_sub.add_parser("export", help="Export a bounded image.")
    img_export.add_argument("service", help="Service name or URL.")
    img_export.add_argument("--bbox", required=True, type=_bbox_value, help="xmin,ymin,xmax,ymax")
    img_export.add_argument("--size", type=_size_value, help="width,height")
    img_export.add_argument("--format", default="jpgpng", dest="format_")
    img_export.add_argument("--in-sr", type=_positive_int, default=4326)
    img_export.add_argument("--out-sr", type=_positive_int, default=4326)
    img_export.add_argument("-o", "--output", required=True)
    img_export.add_argument("--force", action="store_true")
    img_identify = img_sub.add_parser("identify", help="Identify pixel at a point.")
    img_identify.add_argument("service", help="Service name or URL.")
    img_identify.add_argument("--point", required=True, type=_point_value, help="lon,lat")
    img_stats = img_sub.add_parser("statistics", help="Compute statistics for an extent.")
    img_stats.add_argument("service", help="Service name or URL.")
    img_stats.add_argument("--bbox", required=True, type=_bbox_value, help="xmin,ymin,xmax,ymax")

    # Geocoding commands.
    geo = sub.add_parser("geocode", help="Forward geocode an address.")
    geo.add_argument("address", help="Address string.")
    geo.add_argument("--min-score", type=_score, default=None)
    geo.add_argument("--max", type=_positive_int, default=10, dest="max_locations")

    rev_geo = sub.add_parser("reverse-geocode", help="Reverse geocode a coordinate.")
    rev_geo.add_argument("--lat", required=True, type=_latitude)
    rev_geo.add_argument("--lon", required=True, type=_longitude)

    suggest_p = sub.add_parser("suggest", help="Address autocomplete.")
    suggest_p.add_argument("text", help="Partial address.")
    suggest_p.add_argument("--max", "--limit", type=_positive_int, default=10, dest="max_suggestions")

    batch_geo = sub.add_parser("geocode-batch", help="Batch geocode addresses from CSV.")
    batch_geo.add_argument("input", help="Input CSV path.")
    batch_geo.add_argument("--address-field", default="address")
    batch_geo.add_argument("-o", "--output", required=True)
    batch_geo.add_argument("--force", action="store_true")

    # Transit commands.
    transit_p = sub.add_parser("transit", help="GoRaleigh transit feeds.")
    transit_sub = transit_p.add_subparsers(dest="transit_command")
    transit_routes = transit_sub.add_parser("routes", help="List routes.")
    transit_routes.add_argument("--limit", type=_positive_int, default=100)
    transit_stops = transit_sub.add_parser("stops", help="List stops.")
    transit_stops.add_argument("--near", type=_latlon_value, help="lat,lon")
    transit_stops.add_argument("--limit", type=_positive_int, default=20)
    transit_sched = transit_sub.add_parser("schedule", help="Schedule for a route.")
    transit_sched.add_argument("--route", required=True)
    transit_sched.add_argument("--date", type=_service_date, help="YYYYMMDD")
    transit_sched.add_argument("--limit", type=_positive_int, default=100)
    transit_arr = transit_sub.add_parser("arrivals", help="Arrivals for a stop.")
    transit_arr.add_argument("--stop", required=True)
    transit_arr.add_argument("--limit", type=_positive_int, default=100)
    transit_veh = transit_sub.add_parser("vehicles", help="Live vehicle positions.")
    transit_veh.add_argument("--route")
    transit_veh.add_argument("--limit", type=_positive_int, default=20)
    transit_alerts = transit_sub.add_parser("alerts", help="Service alerts.")
    transit_alerts.add_argument("--limit", type=_positive_int, default=20)
    transit_trips = transit_sub.add_parser("trip-updates", help="Live trip updates.")
    transit_trips.add_argument("--route")
    transit_trips.add_argument("--limit", type=_positive_int, default=20)
    transit_download = transit_sub.add_parser("download-gtfs", help="Download static GTFS.")
    transit_download.add_argument("-o", "--output", default="goraleigh_gtfs.zip")
    transit_download.add_argument("--force", action="store_true")

    # Development / EnerGov commands.
    dev = sub.add_parser("development", help="Permit and Development Portal (guest read-only).")
    dev_sub = dev.add_subparsers(dest="development_command")
    dev_search = dev_sub.add_parser("search", help="Search public records.")
    dev_search.add_argument("type", nargs="?", default=None, help="Record type")
    dev_search.add_argument("--type", dest="type_opt", default=None, help=argparse.SUPPRESS)
    dev_search.add_argument("--query")
    dev_search.add_argument("--limit", type=_positive_int, default=20)
    dev_permit = dev_sub.add_parser("permit", help="Show permit details.")
    dev_permit.add_argument("record")
    dev_insp = dev_sub.add_parser("inspections", help="Inspections for a record.")
    dev_insp.add_argument("--record", required=True)
    dev_insp.add_argument("--limit", type=_positive_int, default=10)
    dev_cc = dev_sub.add_parser("code-cases", help="Search code cases.")
    dev_cc.add_argument("--query")
    dev_cc.add_argument("--limit", type=_positive_int, default=20)
    dev_lic = dev_sub.add_parser("licenses", help="Search licenses.")
    dev_lic.add_argument("--query")
    dev_lic.add_argument("--limit", type=_positive_int, default=20)

    # Civic content commands (top-level aliases).
    news_p = sub.add_parser("news", help="RaleighNC.gov news.")
    news_p.add_argument("--limit", type=_positive_int, default=20)
    news_p.add_argument("--search")

    events_p = sub.add_parser("events", help="RaleighNC.gov events.")
    events_p.add_argument("--limit", type=_positive_int, default=20)
    events_p.add_argument("--from", dest="date_from", type=_iso_date)
    events_p.add_argument("--to", dest="date_to", type=_iso_date)
    events_p.add_argument("--search")

    projects_p = sub.add_parser("projects", help="RaleighNC.gov projects.")
    projects_p.add_argument("--limit", type=_positive_int, default=20)
    projects_p.add_argument("--search")

    places_p = sub.add_parser("places", help="RaleighNC.gov places.")
    places_p.add_argument("--limit", type=_positive_int, default=20)
    places_p.add_argument("--search")

    services_p = sub.add_parser("services", help="RaleighNC.gov services.")
    services_p.add_argument("--limit", type=_positive_int, default=20)
    services_p.add_argument("--search")

    directory_p = sub.add_parser("directory", help="RaleighNC.gov directory entries.")
    directory_p.add_argument("--limit", type=_positive_int, default=20)
    directory_p.add_argument("--search")

    alerts_p = sub.add_parser("alerts", help="RaleighNC.gov public alerts.")
    alerts_p.add_argument("--limit", type=_positive_int, default=20)

    for civic_parser in (
        news_p, events_p, projects_p, places_p, services_p, directory_p, alerts_p
    ):
        civic_parser.add_argument(
            "--relationship",
            metavar="FIELD=ID",
            help="Filter by a JSON:API relationship identifier.",
        )

    rss_p = sub.add_parser("rss", help="RaleighNC.gov RSS feed.")
    rss_p.add_argument("--limit", type=_positive_int, default=20)
    rss_p.add_argument(
        "--new-only", action="store_true", help="Return only entries not seen by prior --new-only runs."
    )

    # Meetings commands.
    mtg = sub.add_parser("meetings", help="eSCRIBE public meetings.")
    mtg_sub = mtg.add_subparsers(dest="meetings_command")
    mtg_upcoming = mtg_sub.add_parser("upcoming", help="Upcoming meetings.")
    mtg_upcoming.add_argument("--limit", type=_positive_int, default=20)
    mtg_list = mtg_sub.add_parser("list", help="List meetings.")
    mtg_list.add_argument("--body")
    mtg_list.add_argument("--year", type=_year)
    mtg_list.add_argument("--limit", type=_positive_int, default=20)
    mtg_search = mtg_sub.add_parser("search", help="Search upcoming or historical meetings.")
    mtg_search.add_argument("query")
    mtg_search.add_argument("--body")
    mtg_search.add_argument("--year", type=_year)
    mtg_search.add_argument("--limit", type=_positive_int, default=20)
    mtg_show = mtg_sub.add_parser("show", help="Show meeting details.")
    mtg_show.add_argument("id")
    mtg_agenda = mtg_sub.add_parser("download-agenda", help="Download agenda.")
    mtg_agenda.add_argument("id")
    mtg_agenda.add_argument("-o", "--output", required=True)
    mtg_agenda.add_argument("--force", action="store_true")
    mtg_minutes = mtg_sub.add_parser("download-minutes", help="Download minutes.")
    mtg_minutes.add_argument("id")
    mtg_minutes.add_argument("-o", "--output", required=True)
    mtg_minutes.add_argument("--force", action="store_true")

    # Catalog-check command for CI/validation.
    check_p = sub.add_parser("catalog-check", help="Validate catalog endpoints.")
    check_p.add_argument("--sample", type=_positive_int, default=10, help="Number of items to sample (default 10).")
    check_p.add_argument("--snapshot", action="store_true", help="Use the cached/live catalog snapshot instead of fetching fresh.")
    check_p.add_argument("--type", help="Check only datasets of this type (FeatureServer, MapServer, ImageServer).")
    check_p.add_argument("--full", action="store_true", help="Check every catalog item (overrides --sample).")

    # Police incident commands.
    police_p = sub.add_parser("police", help="Raleigh Police Department incident data.")
    police_sub = police_p.add_subparsers(dest="police_command")

    police_incidents = police_sub.add_parser("incidents", help="Query NIBRS incidents (June 2014–present).")
    police_incidents.add_argument("--since", type=_duration_value, help="Time range, e.g. 7d, 24h, 2w.")
    police_incidents.add_argument("--category", help="Filter by crime description substring.")
    police_incidents.add_argument("--district", help="Filter by police district substring.")
    police_incidents.add_argument("--limit", type=_positive_int, default=20)
    police_incidents.add_argument("--offset", type=_nonnegative_int, default=0)

    police_recent = police_sub.add_parser("recent", help="Query CrimeMapper past-90-day incidents.")
    police_recent.add_argument("--days", type=_positive_int, default=90, help="Days back (max 90).")
    police_recent.add_argument("--category", help="Filter by crime description substring.")
    police_recent.add_argument("--district", help="Filter by police district substring.")
    police_recent.add_argument("--limit", type=_positive_int, default=20)
    police_recent.add_argument("--offset", type=_nonnegative_int, default=0)

    police_prev = police_sub.add_parser("previous-day", help="Query previous-day incidents.")
    police_prev.add_argument("--category", help="Filter by crime description substring.")
    police_prev.add_argument("--district", help="Filter by police district substring.")
    police_prev.add_argument("--limit", type=_positive_int, default=20)
    police_prev.add_argument("--offset", type=_nonnegative_int, default=0)

    police_history = police_sub.add_parser("history", help="Query historical incidents (SRS or NIBRS).")
    police_history.add_argument("--reporting-system", choices=["srs", "nibrs"], default="nibrs",
                                help="Reporting system (default: nibrs).")
    police_history.add_argument("--since", type=_duration_value, help="Time range, e.g. 30d, 4w.")
    police_history.add_argument("--category", help="Filter by crime description substring.")
    police_history.add_argument("--district", help="Filter by police district substring.")
    police_history.add_argument("--limit", type=_positive_int, default=20)
    police_history.add_argument("--offset", type=_nonnegative_int, default=0)

    # Fire incident commands.
    fire_p = sub.add_parser("fire", help="Raleigh Fire Department incident data.")
    fire_sub = fire_p.add_subparsers(dest="fire_command")

    fire_incidents = fire_sub.add_parser("incidents", help="Query RFD incidents (full history 2007–present or past month).")
    fire_incidents.add_argument("--source", choices=["full-history", "past-month"], default="full-history",
                                help="Dataset to query (default: full-history).")
    fire_incidents.add_argument("--since", type=_duration_value, help="Time range, e.g. 30d, 24h, 2w, 1y.")
    fire_incidents.add_argument("--station", type=_positive_int, help="Filter by station number.")
    fire_incidents.add_argument("--platoon", help="Filter by platoon (e.g. A, B, C).")
    fire_incidents.add_argument("--group", help="Filter by incident group substring (populated only for 2026+ records).")
    fire_incidents.add_argument("--type", dest="incident_type", help="Filter by incident type name/description substring or legacy NFIRS code.")
    fire_incidents.add_argument("--limit", type=_positive_int, default=20)
    fire_incidents.add_argument("--offset", type=_nonnegative_int, default=0)

    fire_rt = fire_sub.add_parser("response-times", help="Compute response durations from dispatch/arrival/cleared timestamps.")
    fire_rt.add_argument("--source", choices=["full-history", "past-month"], default="full-history",
                         help="Dataset to query (default: full-history).")
    fire_rt.add_argument("--since", type=_duration_value, help="Time range, e.g. 30d, 24h, 2w, 1y.")
    fire_rt.add_argument("--station", type=_positive_int, help="Filter by station number.")
    fire_rt.add_argument("--platoon", help="Filter by platoon (e.g. A, B, C).")
    fire_rt.add_argument("--group", help="Filter by incident group substring (populated only for 2026+ records).")
    fire_rt.add_argument("--type", dest="incident_type", help="Filter by incident type name/description substring or legacy NFIRS code.")
    fire_rt.add_argument("--limit", type=_positive_int, default=20)
    fire_rt.add_argument("--offset", type=_nonnegative_int, default=0)

    fire_prot = fire_sub.add_parser("protection", help="Wake County MAR fire-protection proximity lookup.")
    fire_prot_group = fire_prot.add_mutually_exclusive_group(required=True)
    fire_prot_group.add_argument("--address", help="Address to geocode and resolve to a CSAID.")
    fire_prot_group.add_argument("--csaid", type=_csaid_value, help="Canonical site-address identifier (CSAID).")

    fire_reports = fire_sub.add_parser("reports", help="Exact ArcGIS fire-report lookup with guarded RFD fallback.")
    fire_reports_group = fire_reports.add_mutually_exclusive_group(required=True)
    fire_reports_group.add_argument("--date", type=_iso_date, help="Exact dispatch date (YYYY-MM-DD).")
    fire_reports_group.add_argument("--incident-number", type=_nonempty_text, help="Exact incident number.")
    fire_reports.add_argument("--allow-rfd-fallback", action="store_true", help="Use the RFD date form only when ArcGIS returns no records.")
    fire_reports.add_argument("--include-narrative", action="store_true", help="Fetch one exact incident narrative (requires --incident-number).")
    fire_reports.add_argument("--acknowledge-insecure-rfd", action="store_true", help="Acknowledge that RFD data crosses unencrypted HTTP for this invocation.")

    fire_inspections = fire_sub.add_parser("inspections", help="Search fragile RFD inspection records over acknowledged HTTP.")
    fire_inspections_group = fire_inspections.add_mutually_exclusive_group(required=True)
    fire_inspections_group.add_argument("--business", type=_nonempty_text, help="Nonempty business-name search.")
    fire_inspections_group.add_argument("--address", type=_nonempty_text, help="Nonempty address search.")
    fire_inspections.add_argument("--acknowledge-insecure-rfd", action="store_true", help="Acknowledge that the search crosses unencrypted HTTP for this invocation.")

    incidents_p = sub.add_parser("incidents", help="Raleigh-Wake ECC active incident feed (undocumented).")
    incidents_sub = incidents_p.add_subparsers(dest="incidents_command")
    incidents_active = incidents_sub.add_parser("active", help="Currently active incidents.")
    incidents_active.add_argument("--agency", help="Filter by agency substring (e.g. raleigh-fire, raleigh-police).")
    incidents_active.add_argument("--type", dest="incident_type", help="Filter by incident type substring.")
    incidents_active.add_argument("--limit", type=_positive_int, default=50)
    incidents_active.add_argument("--no-cache", action="store_true", help="Bypass the short-lived cache.")

    return parser


def _resolve_imagery_url(service: str) -> str:
    if service.startswith("http"):
        return service
    encoded_service = urllib.parse.quote(service.strip("/"), safe="/")
    return f"{imagery.IMAGE_ROOT}/{encoded_service}/ImageServer"


def _parse_bbox(value: str) -> tuple[float, float, float, float]:
    try:
        parts = [float(x.strip()) for x in value.split(",")]
    except ValueError as exc:
        raise argparse.ArgumentTypeError("bbox must be xmin,ymin,xmax,ymax") from exc
    if len(parts) != 4:
        raise argparse.ArgumentTypeError("bbox must be xmin,ymin,xmax,ymax")
    if not all(math.isfinite(value) for value in parts):
        raise argparse.ArgumentTypeError("bbox coordinates must be finite")
    if parts[0] >= parts[2] or parts[1] >= parts[3]:
        raise argparse.ArgumentTypeError("bbox minimums must be less than maximums")
    return tuple(parts)  # type: ignore[return-value]


def _parse_point(value: str) -> tuple[float, float]:
    try:
        parts = [float(x.strip()) for x in value.split(",")]
    except ValueError as exc:
        raise argparse.ArgumentTypeError("point must be lon,lat") from exc
    if len(parts) != 2:
        raise argparse.ArgumentTypeError("point must be lon,lat")
    _longitude(str(parts[0]))
    _latitude(str(parts[1]))
    return tuple(parts)  # type: ignore[return-value]


def _parse_latlon(value: str) -> tuple[float, float]:
    parts = value.split(",")
    if len(parts) != 2:
        raise argparse.ArgumentTypeError("coordinate must be lat,lon")
    return _latitude(parts[0].strip()), _longitude(parts[1].strip())


def _parse_size(value: str) -> tuple[int, int]:
    try:
        parts = [int(item.strip()) for item in value.split(",")]
    except ValueError as exc:
        raise ValueError("size must be width,height using positive integers") from exc
    if len(parts) != 2 or any(part <= 0 for part in parts):
        raise ValueError("size must be width,height using positive integers")
    return parts[0], parts[1]


def _ensure_catalog(args: argparse.Namespace) -> list[dict[str, Any]]:
    if args.refresh:
        return hub.fetch_catalog()
    return hub.catalog_from_cache_or_live()


def cmd_catalog(args: argparse.Namespace) -> int:
    catalog = _ensure_catalog(args)
    if args.category:
        catalog = [i for i in catalog if args.category.lower() in i.get("category", "").lower()]
    if args.search:
        catalog = [i for i in catalog if args.search.lower() in " ".join([i.get("title", ""), i.get("description", ""), " ".join(i.get("tags", []))]).lower()]
    limit = args.limit
    if args.json:
        _output_json([{"id": i["id"], "title": i["title"], "type": i["type"], "url": i.get("url")} for i in catalog[:limit]])
    else:
        _output_table(["TYPE", "TITLE"], [[i["type"], i["title"]] for i in catalog[:limit]])
        if len(catalog) > limit:
            print(
                f"... and {len(catalog) - limit} more "
                f"(use --limit {len(catalog)} --json for the full list)"
            )
    return 0


def cmd_search(args: argparse.Namespace) -> int:
    catalog = _ensure_catalog(args)
    results = hub.search_catalog(args.query, catalog=catalog, limit=args.limit)
    if args.json:
        _output_json(results)
    else:
        _output_table(["TYPE", "TITLE", "CATEGORY"], [[r["type"], r["title"], r["category"]] for r in results])
    return 0


def cmd_info(args: argparse.Namespace) -> int:
    catalog = _ensure_catalog(args)
    item = hub.resolve_item(args.dataset, catalog=catalog)
    url = item.get("url", "")
    resolved_url: str | None = None
    fields: list[dict[str, Any]] = []
    sample: dict[str, Any] = {"type": "FeatureCollection", "features": []}
    sample_error: str | None = None
    if url and item.get("type") in ("FeatureServer", "MapServer"):
        try:
            resolved_url = arcgis.resolve_queryable_layer(url)
            fields = arcgis.layer_fields(resolved_url)
            sample_records = arcgis.sample_features(resolved_url, limit=3)
            sample = arcgis.geojson_from_records(sample_records)
        except Exception as exc:
            sample_error = str(exc)
    output = {
        "dataset": item,
        "fields": fields,
        "sample": sample,
    }
    if sample_error:
        output["sample_error"] = sample_error
    if args.json:
        _output_json(output)
        return 1 if sample_error else 0
    else:
        print(f"Title: {item['title']}")
        print(f"Type: {item['type']}")
        print(f"Category: {item['category']}")
        print(f"URL: {item['url']}")
        if resolved_url:
            print(f"Resolved layer: {resolved_url}")
        print(f"Fields: {len(fields)}")
        print(f"Sample features: {len(sample['features'])}")
        if sample_error:
            print(f"Sample error: {sample_error}", file=sys.stderr)
            return 1
        print(f"Tags: {', '.join(item['tags'])}")
    return 0


def _query_dataset(
    args: argparse.Namespace,
    max_records: int | None = None,
    offset: int = 0,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    catalog = _ensure_catalog(args)
    item = hub.resolve_item(args.dataset, catalog=catalog)
    url = item.get("url")
    if not url:
        raise cli_error("Dataset has no queryable URL.")
    resolved = arcgis.resolve_queryable_layer(url)
    item["resolved_url"] = resolved
    has_geometry = arcgis.layer_has_geometry(resolved)
    item["has_geometry"] = has_geometry
    return_geometry = not args.no_geometry and has_geometry
    records = arcgis.query_all_pages(
        resolved,
        where=args.where,
        out_fields=args.out_fields,
        return_geometry=return_geometry,
        max_records=max_records,
        offset=offset,
        order_by_fields=getattr(args, "order_by", None),
    )
    return records, item


def cmd_query(args: argparse.Namespace) -> int:
    records, _ = _query_dataset(args, max_records=args.limit, offset=args.offset)
    if args.json:
        _output_json(arcgis.geojson_from_records(records))
    elif args.csv:
        sys.stdout.write(arcgis.csv_from_records(records))
    elif records:
        headers = list(records[0].get("attributes", {}).keys())[:8]
        rows = [[str(r.get("attributes", {}).get(h, "")) for h in headers] for r in records]
        _output_table(headers, rows)
    return 0


def cmd_download(args: argparse.Namespace) -> int:
    max_records = None if args.all else args.limit
    records, _ = _query_dataset(args, max_records=max_records)
    fmt = args.format
    if fmt == "csv":
        output = arcgis.csv_from_records(records)
    elif fmt == "geojson" or fmt == "json":
        output = json.dumps(arcgis.geojson_from_records(records), indent=2)
    core.safe_write(Path(args.output), output, force=getattr(args, "force", False))
    if not args.json:
        print(f"Wrote {len(records)} records to {args.output}")
    return 0


def cmd_categories(args: argparse.Namespace) -> int:
    catalog = _ensure_catalog(args)
    counts: dict[str, int] = {}
    for item in catalog:
        counts[item.get("category", "Other")] = counts.get(item.get("category", "Other"), 0) + 1
    categories = sorted(counts.items(), key=lambda x: x[0])
    if args.json:
        _output_json([{"category": c, "count": n} for c, n in categories])
    else:
        _output_table(["CATEGORY", "COUNT"], [[c, str(n)] for c, n in categories])
    return 0


def cmd_imagery_catalog(args: argparse.Namespace) -> int:
    services = imagery.list_services()
    limit = args.limit
    if args.json:
        _output_json(services[:limit])
    else:
        _output_table(["NAME", "TYPE"], [[s.get("name", ""), s.get("type", "")] for s in services[:limit]])
    return 0


def cmd_imagery_info(args: argparse.Namespace) -> int:
    url = _resolve_imagery_url(args.service)
    info = imagery.service_info(url)
    if args.json:
        _output_json(info)
    else:
        print(f"Service: {info.get('serviceDescription') or args.service}")
        print(f"Capabilities: {info.get('capabilities')}")
        print(f"Band count: {info.get('bandCount')}")
    return 0


def cmd_imagery_export(args: argparse.Namespace) -> int:
    url = _resolve_imagery_url(args.service)
    bbox = _parse_bbox(args.bbox)
    size = _parse_size(args.size) if args.size else None
    data = imagery.export_image(url, bbox=bbox, size=size, format_=args.format_, in_sr=args.in_sr, out_sr=args.out_sr)
    core.safe_write(Path(args.output), data, force=args.force)
    if not args.json:
        print(f"Wrote {len(data)} bytes to {args.output}")
    return 0


def cmd_imagery_identify(args: argparse.Namespace) -> int:
    url = _resolve_imagery_url(args.service)
    point = _parse_point(args.point)
    result = imagery.identify(url, point=point)
    if args.json:
        _output_json(result)
    else:
        print(json.dumps(result, indent=2))
    return 0


def cmd_imagery_statistics(args: argparse.Namespace) -> int:
    url = _resolve_imagery_url(args.service)
    bbox = _parse_bbox(args.bbox)
    result = imagery.compute_statistics(url, bbox=bbox)
    if args.json:
        _output_json(result)
    else:
        print(json.dumps(result, indent=2))
    return 0


def cmd_geocode(args: argparse.Namespace) -> int:
    candidates = geocode.find_address_candidates(
        args.address,
        max_locations=args.max_locations,
        min_score=args.min_score,
    )
    if args.json:
        _output_json(candidates)
    else:
        if not candidates:
            print("No match.")
            return 0
        _output_table(
            ["SCORE", "ADDRESS", "LON", "LAT"],
            [
                [str(c.get("score", "")), c.get("address", ""), str(c.get("location", {}).get("x", "")), str(c.get("location", {}).get("y", ""))]
                for c in candidates
            ],
        )
    return 0


def cmd_reverse_geocode(args: argparse.Namespace) -> int:
    result = geocode.reverse_geocode(args.lat, args.lon)
    if args.json:
        _output_json(result)
    else:
        print(json.dumps(result, indent=2))
    return 0


def cmd_suggest(args: argparse.Namespace) -> int:
    suggestions = geocode.suggest(args.text, max_suggestions=args.max_suggestions)
    if args.json:
        _output_json(suggestions)
    else:
        _output_table(["SUGGESTION"], [[s.get("text", "")] for s in suggestions])
    return 0


def cmd_geocode_batch(args: argparse.Namespace) -> int:
    records: list[dict[str, Any]] = []
    with open(args.input, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        source_fields = list(reader.fieldnames or [])
        for row in reader:
            source = dict(row)
            source.setdefault("SingleLine", row.get(args.address_field, ""))
            records.append(source)
    results = geocode.geocode_addresses(records)
    result_fields = ["input_id", "match_address", "score", "lat", "lon", "status"]
    result_columns = {
        field: field if field not in source_fields else f"geocode_{field}"
        for field in result_fields
    }
    output_rows = []
    for result in results:
        source = dict(result.get("source") or {})
        source.update({
            result_columns["input_id"]: result.get("input_id"),
            result_columns["match_address"]: result.get("address"),
            result_columns["score"]: result.get("score"),
            result_columns["lat"]: result.get("lat"),
            result_columns["lon"]: result.get("lon"),
            result_columns["status"]: result.get("status"),
        })
        output_rows.append({key: arcgis.csv_safe_value(value) for key, value in source.items()})
    output = io.StringIO()
    fieldnames = source_fields + list(result_columns.values())
    writer = csv.writer(output)
    writer.writerow([arcgis.csv_safe_value(field) for field in fieldnames])
    for row in output_rows:
        writer.writerow([row.get(field, "") for field in fieldnames])
    core.safe_write(Path(args.output), output.getvalue(), force=args.force)
    if not args.json:
        print(f"Geocoded {len(results)} addresses to {args.output}")
    return 0


def cmd_transit_routes(args: argparse.Namespace) -> int:
    routes = transit.get_routes()
    routes = routes[: args.limit]
    if args.json:
        _output_json(routes)
    else:
        _output_table(
            ["SHORT", "LONG NAME"],
            [[r.get("route_short_name", ""), r.get("route_long_name", "")] for r in routes],
        )
    return 0


def cmd_transit_stops(args: argparse.Namespace) -> int:
    stops = transit.get_stops()
    if args.near:
        lat, lon = _parse_latlon(args.near)
        # Simple Euclidean sort for nearest; sufficient for CLI filtering.
        stops = sorted(
            stops,
            key=lambda s: ((float(s.get("stop_lat", 0)) - lat) ** 2 + (float(s.get("stop_lon", 0)) - lon) ** 2),
        )
    stops = stops[: args.limit]
    if args.json:
        _output_json(stops)
    else:
        _output_table(
            ["STOP", "NAME", "LAT", "LON"],
            [
                [s.get("stop_id", ""), s.get("stop_name", ""), s.get("stop_lat", ""), s.get("stop_lon", "")]
                for s in stops
            ],
        )
    return 0


def cmd_transit_schedule(args: argparse.Namespace) -> int:
    schedule = transit.get_schedule_for_route(args.route, target_date=args.date)
    schedule = schedule[: args.limit]
    if args.json:
        _output_json(schedule)
    else:
        _output_table(
            ["TRIP", "STOP", "ARRIVAL"],
            [[s["trip_id"], s["stop_id"], s["arrival_time"]] for s in schedule],
        )
    return 0


def cmd_transit_arrivals(args: argparse.Namespace) -> int:
    arrivals = transit.get_arrivals_for_stop(args.stop)
    arrivals = arrivals[: args.limit]
    if args.json:
        _output_json(arrivals)
    else:
        _output_table(
            ["TRIP", "ARRIVAL"],
            [[a["trip_id"], a["arrival_time"]] for a in arrivals],
        )
    return 0


def cmd_transit_vehicles(args: argparse.Namespace) -> int:
    entities = transit.get_vehicle_positions(route=args.route, limit=args.limit)
    if args.json:
        _output_json(entities)
    else:
        print(json.dumps(entities, indent=2))
    return 0


def cmd_transit_alerts(args: argparse.Namespace) -> int:
    entities = transit.get_alerts(limit=args.limit)
    if args.json:
        _output_json(entities)
    else:
        print(json.dumps(entities, indent=2))
    return 0


def cmd_transit_trip_updates(args: argparse.Namespace) -> int:
    entities = transit.get_trip_updates(route=args.route, limit=args.limit)
    if args.json:
        _output_json(entities)
    else:
        print(json.dumps(entities, indent=2))
    return 0


def cmd_transit_download_gtfs(args: argparse.Namespace) -> int:
    data = transit.download_gtfs()
    transit.parse_gtfs_zip(data)
    core.safe_write(Path(args.output), data, force=args.force)
    if not args.json:
        print(f"Downloaded {len(data)} bytes to {args.output}")
    return 0


def cmd_development_search(args: argparse.Namespace) -> int:
    record_type = args.type or args.type_opt
    if not record_type:
        print("Error: record type is required (e.g. permit, plan, inspection)", file=sys.stderr)
        return 2
    type_map = {
        "permit": "permit",
        "permits": "permit",
        "plan": "plan",
        "plans": "plan",
        "inspection": "inspection",
        "inspections": "inspection",
        "code-case": "code-case",
        "code-cases": "code-case",
        "request": "request",
        "requests": "request",
        "license": "license",
        "licenses": "license",
        "project": "project",
        "projects": "project",
    }
    if record_type not in type_map:
        print(f"Error: invalid record type '{record_type}'", file=sys.stderr)
        return 2
    result = development.public_search(type_map[record_type], query=args.query, limit=args.limit)
    if args.json:
        _output_json(result)
    else:
        print(json.dumps(result, indent=2))
    return 0


def cmd_development_permit(args: argparse.Namespace) -> int:
    try:
        result = development.permit_detail(args.record)
    except development.UnsupportedEndpointError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    if args.json:
        _output_json(result)
    else:
        print(json.dumps(result, indent=2))
    return 0


def cmd_development_inspections(args: argparse.Namespace) -> int:
    try:
        results = development.inspections_for_record(args.record, limit=args.limit)
    except development.UnsupportedEndpointError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    if args.json:
        _output_json(results)
    else:
        print(json.dumps(results, indent=2))
    return 0


def cmd_development_code_cases(args: argparse.Namespace) -> int:
    results = development.code_cases(query=args.query, limit=args.limit)
    if args.json:
        _output_json(results)
    else:
        print(json.dumps(results, indent=2))
    return 0


def cmd_development_licenses(args: argparse.Namespace) -> int:
    results = development.licenses(query=args.query, limit=args.limit)
    if args.json:
        _output_json(results)
    else:
        print(json.dumps(results, indent=2))
    return 0


def cmd_news(args: argparse.Namespace) -> int:
    results = civic.fetch_news(
        limit=args.limit, search=args.search, relationship=args.relationship
    )
    if args.json:
        _output_json(results)
    else:
        _output_table(["TITLE", "URL"], [[r["title"], r["url"]] for r in results])
    return 0


def cmd_events(args: argparse.Namespace) -> int:
    if args.date_from and args.date_to and args.date_from > args.date_to:
        raise cli_error("--from must not be later than --to")
    results = civic.fetch_events(
        limit=args.limit,
        date_from=args.date_from,
        date_to=args.date_to,
        search=args.search,
        relationship=args.relationship,
    )
    if args.json:
        _output_json(results)
    else:
        _output_table(["TITLE", "URL"], [[r["title"], r["url"]] for r in results])
    return 0


def cmd_projects(args: argparse.Namespace) -> int:
    results = civic.fetch_projects(
        limit=args.limit, search=args.search, relationship=args.relationship
    )
    if args.json:
        _output_json(results)
    else:
        _output_table(["TITLE", "URL"], [[r["title"], r["url"]] for r in results])
    return 0


def cmd_places(args: argparse.Namespace) -> int:
    results = civic.fetch_places(
        limit=args.limit, search=args.search, relationship=args.relationship
    )
    if args.json:
        _output_json(results)
    else:
        _output_table(["TITLE", "URL"], [[r["title"], r["url"]] for r in results])
    return 0


def cmd_services(args: argparse.Namespace) -> int:
    results = civic.fetch_services(
        limit=args.limit, search=args.search, relationship=args.relationship
    )
    if args.json:
        _output_json(results)
    else:
        _output_table(["TITLE", "URL"], [[r["title"], r["url"]] for r in results])
    return 0


def cmd_directory(args: argparse.Namespace) -> int:
    results = civic.fetch_directory(
        limit=args.limit, search=args.search, relationship=args.relationship
    )
    if args.json:
        _output_json(results)
    else:
        _output_table(["TITLE", "URL"], [[r["title"], r["url"]] for r in results])
    return 0


def cmd_alerts(args: argparse.Namespace) -> int:
    results = civic.fetch_alerts(limit=args.limit, relationship=args.relationship)
    if args.json:
        _output_json(results)
    else:
        _output_table(["TITLE", "URL"], [[r["title"], r["url"]] for r in results])
    return 0


def cmd_rss(args: argparse.Namespace) -> int:
    results = civic.fetch_rss(limit=args.limit, new_only=args.new_only)
    if args.json:
        _output_json(results)
    else:
        _output_table(["TITLE", "URL"], [[r["title"], r["url"]] for r in results])
    return 0


def cmd_meetings_upcoming(args: argparse.Namespace) -> int:
    results = meetings.list_upcoming(limit=args.limit)
    if args.json:
        _output_json(results)
    else:
        _output_table(["DATE", "BODY", "TITLE"], [[r["date"], r["body"], r["title"]] for r in results])
    return 0


def cmd_meetings_list(args: argparse.Namespace) -> int:
    results = meetings.list_meetings(body=args.body, year=args.year, limit=args.limit)
    if args.json:
        _output_json(results)
    else:
        _output_table(["DATE", "BODY", "TITLE"], [[r["date"], r["body"], r["title"]] for r in results])
    return 0


def cmd_meetings_search(args: argparse.Namespace) -> int:
    results = meetings.search_meetings(
        args.query,
        body=args.body,
        year=args.year,
        limit=args.limit,
    )
    if args.json:
        _output_json(results)
    else:
        _output_table(
            ["ID", "Title", "Date", "Body"],
            [[str(r.get("id", "")), str(r.get("title", "")), str(r.get("date", "")), str(r.get("body", ""))] for r in results],
        )
    return 0


def cmd_meetings_show(args: argparse.Namespace) -> int:
    result = meetings.meeting_detail(args.id)
    if args.json:
        _output_json(result)
    else:
        print(json.dumps(result, indent=2))
    return 0


def cmd_meetings_download_agenda(args: argparse.Namespace) -> int:
    detail = meetings.meeting_detail(args.id)
    url = detail.get("agenda")
    if not url:
        print("No agenda available.", file=sys.stderr)
        return 1
    meetings.download_document(url, args.output, force=args.force)
    if not args.json:
        print(f"Downloaded agenda to {args.output}")
    return 0


def cmd_meetings_download_minutes(args: argparse.Namespace) -> int:
    detail = meetings.meeting_detail(args.id)
    url = detail.get("minutes")
    if not url:
        print("No minutes available.", file=sys.stderr)
        return 1
    meetings.download_document(url, args.output, force=args.force)
    if not args.json:
        print(f"Downloaded minutes to {args.output}")
    return 0


def cmd_catalog_check(args: argparse.Namespace) -> int:
    if args.snapshot:
        catalog = hub.catalog_from_cache_or_live()
    else:
        catalog = hub.fetch_catalog()
    if args.type:
        catalog = [i for i in catalog if i.get("type") == args.type]
    # Only ArcGIS service records have a metadata contract this command can
    # validate. Documents, web applications, and external links remain visible
    # in catalog output but are intentionally not dereferenced here.
    supported_types = {"FeatureServer", "MapServer", "ImageServer"}
    catalog = [i for i in catalog if i.get("type") in supported_types]
    if args.full:
        sample = catalog
    else:
        sample = catalog[: args.sample]
    failures: list[dict[str, Any]] = []
    for item in sample:
        url = item.get("url", "")
        if not url:
            continue
        try:
            if item.get("type") == "ImageServer":
                meta = imagery.service_info(url)
            else:
                meta = arcgis.service_metadata(url)
            if "error" in meta:
                failures.append({"id": item["id"], "title": item["title"], "error": meta["error"]})
        except Exception as exc:
            failures.append({"id": item["id"], "title": item["title"], "error": str(exc)})
    if args.json:
        _output_json({"checked": len(sample), "failures": failures})
    else:
        print(f"Checked {len(sample)} endpoints; {len(failures)} failures")
        for f in failures:
            print(f"  {f['title']}: {f['error']}")
    return 0 if not failures else 1


def _duration_value(value: str) -> str:
    """Validate a duration string like '7d', '24h', '2w', '1y'."""
    if not re.fullmatch(r"\d+[dhwy]", value.strip()):
        raise argparse.ArgumentTypeError("duration must be a positive integer followed by d (days), h (hours), w (weeks), or y (years)")
    amount = int(value.strip()[:-1])
    if amount < 1:
        raise argparse.ArgumentTypeError("duration must be positive")
    return value.strip()


def _duration_to_ms(value: str) -> int:
    """Convert a validated duration string to a Unix-milliseconds timestamp in the past."""
    amount = int(value[:-1])
    unit = value[-1]
    multiplier = {"h": 3600, "d": 86400, "w": 604800, "y": 31536000}
    seconds_ago = amount * multiplier[unit]
    now_ms = int(datetime.now(timezone.utc).timestamp() * 1000)
    return now_ms - (seconds_ago * 1000)


def _police_output(result: dict[str, Any], args: argparse.Namespace) -> int:
    """Shared output logic for police commands."""
    if args.json:
        _output_json(result)
    else:
        features = result.get("features", [])
        if features:
            rows = []
            for f in features:
                props = f.get("properties", {})
                rows.append([
                    str(props.get("_source", "")),
                    str(props.get("crime_description") or props.get("LCR_DESC") or ""),
                    str(props.get("district") or props.get("DISTRICT") or ""),
                    str(props.get("reported_block_address") or ""),
                    str(props.get("_location_status", "")),
                ])
            _output_table(["SOURCE", "DESCRIPTION", "DISTRICT", "BLOCK ADDRESS", "LOC STATUS"], rows)
        else:
            print("No records returned.")
        print(police.LOCATION_CAVERAT, file=sys.stderr)
    return 0


def cmd_police_incidents(args: argparse.Namespace) -> int:
    since_ms = _duration_to_ms(args.since) if args.since else None
    if since_ms is not None and since_ms < police.NIBRS_EPOCH_MS:
        print(
            "Warning: --since predates NIBRS availability (June 2014); "
            "results will only include June 2014 onward. Use 'police history --reporting-system srs' for older data.",
            file=sys.stderr,
        )
    result = police.query_incidents(
        "nibrs", since_ms=since_ms, category=args.category, district=args.district,
        limit=args.limit, offset=args.offset,
    )
    return _police_output(result, args)


def cmd_police_recent(args: argparse.Namespace) -> int:
    if args.days > 90:
        raise cli_error("--days cannot exceed 90 (the CrimeMapper feed covers at most 90 days)")
    since_ms = int(datetime.now(timezone.utc).timestamp() * 1000) - (args.days * 86400 * 1000)
    result = police.query_incidents(
        "crimemapper-90d", since_ms=since_ms, category=args.category, district=args.district,
        limit=args.limit, offset=args.offset,
    )
    return _police_output(result, args)


def cmd_police_previous_day(args: argparse.Namespace) -> int:
    result = police.query_incidents(
        "previous-day", category=args.category, district=args.district,
        limit=args.limit, offset=args.offset,
    )
    return _police_output(result, args)


def cmd_police_history(args: argparse.Namespace) -> int:
    source_key = args.reporting_system
    if source_key == "nibrs":
        print("Note: defaulting to NIBRS; use --reporting-system srs for pre-2014 data.", file=sys.stderr)
    since_ms = _duration_to_ms(args.since) if args.since else None
    result = police.query_incidents(
        source_key, since_ms=since_ms, category=args.category, district=args.district,
        limit=args.limit, offset=args.offset,
    )
    return _police_output(result, args)


def _format_ms_datetime(value: Any) -> str:
    """Format a Unix-milliseconds timestamp for table output, or '' if unusable."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return ""
    try:
        return datetime.fromtimestamp(value / 1000, timezone.utc).strftime("%Y-%m-%d %H:%MZ")
    except (OverflowError, OSError, ValueError):
        return ""


def _fire_query_args(args: argparse.Namespace) -> tuple[int | None, dict[str, Any]]:
    """Shared filter extraction for fire commands, with source-specific notes."""
    since_ms = _duration_to_ms(args.since) if args.since else None
    if args.group and since_ms is not None and since_ms < fire.SCHEMA_TRANSITION_EPOCH_MS:
        print(
            "Note: incident_group_name is populated only for 2026+ records; "
            "older records will be excluded by the group filter.",
            file=sys.stderr,
        )
    if args.station and args.source == "full-history":
        print(
            "Note: station is unpopulated for most full-history records after "
            "early 2021; use --source past-month for current station data.",
            file=sys.stderr,
        )
    filters = {
        "station": args.station,
        "platoon": args.platoon,
        "group": args.group,
        "incident_type": args.incident_type,
        "limit": args.limit,
        "offset": args.offset,
    }
    return since_ms, filters


def _fire_output(result: dict[str, Any], args: argparse.Namespace) -> int:
    """Shared output logic for fire incidents."""
    if args.json:
        _output_json(result)
    else:
        features = result.get("features", [])
        if features:
            rows = []
            for f in features:
                props = f.get("properties", {})
                station = props.get("_station")
                rows.append([
                    str(props.get("incident_number") or ""),
                    str(props.get("_classification_era") or ""),
                    str(props.get("_incident_group") or ""),
                    str(props.get("_incident_type") or ""),
                    str(station if station is not None else ""),
                    str(props.get("platoon") or ""),
                    _format_ms_datetime(props.get("dispatch_date_time")),
                ])
            _output_table(["INCIDENT", "ERA", "GROUP", "TYPE", "STATION", "PLATOON", "DISPATCHED"], rows)
        else:
            print("No records returned.")
        print(fire.PRIVACY_CAVERAT, file=sys.stderr)
    return 0


def _fire_duration_cell(props: dict[str, Any], key: str, status_key: str) -> str:
    """Format a duration value for table output, blank unless the pair validated."""
    if props.get(status_key) != "ok":
        return ""
    value = props.get(key)
    return f"{value:.0f}" if isinstance(value, (int, float)) else ""


def _fire_response_times_output(result: dict[str, Any], args: argparse.Namespace) -> int:
    """Shared output logic for fire response-times."""
    features = result.get("features", [])
    valid = 0
    rejected = 0
    for f in features:
        status = f.get("properties", {}).get("_dispatch_to_arrive_status")
        if status == "ok":
            valid += 1
        elif status is not None:
            rejected += 1

    if args.json:
        _output_json(result)
    else:
        if features:
            rows = []
            for f in features:
                props = f.get("properties", {})
                rows.append([
                    str(props.get("incident_number") or ""),
                    str(props.get("_incident_group") or ""),
                    _fire_duration_cell(props, "_dispatch_to_arrive_seconds", "_dispatch_to_arrive_status"),
                    _fire_duration_cell(props, "_arrive_to_clear_seconds", "_arrive_to_clear_status"),
                    _fire_duration_cell(props, "_dispatch_to_clear_seconds", "_dispatch_to_clear_status"),
                    str(props.get("_dispatch_to_arrive_status") or ""),
                ])
            _output_table(
                ["INCIDENT", "GROUP", "DISPATCH->ARRIVE (S)", "ARRIVE->CLEAR (S)", "DISPATCH->CLEAR (S)", "STATUS"],
                rows,
            )
        else:
            print("No records returned.")
        print(
            f"{len(features)} records: {valid} with a valid dispatch-to-arrival "
            f"duration, {rejected} rejected (missing, malformed, or reversed timestamps).",
            file=sys.stderr,
        )
        print(fire.PRIVACY_CAVERAT, file=sys.stderr)
    return 0


def cmd_fire_incidents(args: argparse.Namespace) -> int:
    since_ms, filters = _fire_query_args(args)
    result = fire.query_incidents(args.source, since_ms=since_ms, **filters)
    return _fire_output(result, args)


def cmd_fire_response_times(args: argparse.Namespace) -> int:
    since_ms, filters = _fire_query_args(args)
    result = fire.query_incidents(args.source, since_ms=since_ms, include_response_times=True, **filters)
    return _fire_response_times_output(result, args)


def cmd_fire_protection(args: argparse.Namespace) -> int:
    if args.csaid is not None:
        csaid = args.csaid
        resolution = None
    else:
        resolution = fire_protection.resolve_csaid_from_address(args.address)
        csaid = resolution["csaid"]

    result = fire_protection.query_fire_protection(csaid)
    if resolution:
        result["address_resolution"] = resolution

    if args.json:
        _output_json(result)
    else:
        if resolution:
            print(f"Address: {resolution['match_address']} (score: {resolution['score']})")
        print(f"CSAID: {result['csaid']}")
        print(f"Retrieved: {result['retrieved_at']}")
        print()
        stations = result.get("stations", [])
        if stations:
            rows = []
            for s in stations:
                rank = s.get("rank")
                distance = s.get("distance")
                rows.append([
                    str(rank if rank is not None else ""),
                    str(s.get("station_id") or ""),
                    str(distance if distance is not None else ""),
                    str(s.get("iso") or ""),
                ])
            _output_table(["RANK", "STATION", "DISTANCE", "ISO"], rows)
        else:
            print("No station records for this CSAID.")
        hd = result.get("hydrant_distance")
        if hd is not None:
            print(f"\nNearest hydrant distance: {hd}")
        print(fire_protection.PROTECTION_CAVERAT, file=sys.stderr)
    return 0


def _fire_reports_output(result: dict[str, Any], args: argparse.Namespace) -> int:
    if args.json:
        _output_json(result)
        return 0
    reports = result.get("reports", [])
    if reports:
        rows = []
        for report in reports:
            dispatched = report.get("dispatch_date_time")
            rows.append([
                str(report.get("source") or ""),
                str(report.get("incident_number") or ""),
                _format_ms_datetime(dispatched) if dispatched is not None else str(report.get("incident_date") or ""),
                str(report.get("incident_type_name") or ""),
                str(report.get("address") or ""),
            ])
        _output_table(["SOURCE", "INCIDENT", "DATE", "TYPE", "ADDRESS"], rows)
    else:
        print("No records returned; this does not prove no report exists.")
    narrative = result.get("narrative")
    if isinstance(narrative, dict) and narrative.get("narrative"):
        print(f"\nNarrative ({narrative.get('incident_number', '')}):")
        print(narrative["narrative"])
    for warning in result.get("warnings", []):
        print(f"Warning: {warning}", file=sys.stderr)
    return 0


def cmd_fire_reports(args: argparse.Namespace) -> int:
    if args.include_narrative and not args.incident_number:
        raise cli_error("--include-narrative requires --incident-number")
    if (args.allow_rfd_fallback or args.include_narrative) and not args.acknowledge_insecure_rfd:
        raise cli_error("RFD access requires --acknowledge-insecure-rfd")

    result = fire.query_reports(
        report_date=args.date,
        incident_number=args.incident_number,
    )
    if not result["reports"] and args.allow_rfd_fallback:
        if not args.date:
            raise cli_error("--allow-rfd-fallback requires --date")
        print(f"Warning: {rfd_reports.INSECURE_WARNING}", file=sys.stderr)
        result["reports"] = rfd_reports.search_date(
            args.date, acknowledged=args.acknowledge_insecure_rfd
        )
        result["sources"].append({
            "source": "rfd-html",
            "url": rfd_reports.BASE_URL + rfd_reports.DATE_PATH,
            "source_fragility": "fragile-html-over-http",
        })
        result["warnings"].append(rfd_reports.INSECURE_WARNING)

    if args.include_narrative:
        if len(result["reports"]) != 1:
            raise cli_error("exactly one ArcGIS report is required to fetch a narrative")
        report = result["reports"][0]
        dispatched = report.get("dispatch_date_time")
        if isinstance(dispatched, bool) or not isinstance(dispatched, (int, float)):
            raise cli_error("the ArcGIS report has no usable dispatch date for narrative lookup")
        incident_date = datetime.fromtimestamp(
            dispatched / 1000, timezone.utc
        ).date().isoformat()
        print(f"Warning: {rfd_reports.INSECURE_WARNING}", file=sys.stderr)
        result["narrative"] = rfd_reports.fetch_narrative(
            report["incident_number"],
            incident_date,
            acknowledged=args.acknowledge_insecure_rfd,
        )
        result["warnings"].append(rfd_reports.INSECURE_WARNING)
    return _fire_reports_output(result, args)


def cmd_fire_inspections(args: argparse.Namespace) -> int:
    if not args.acknowledge_insecure_rfd:
        raise cli_error("RFD access requires --acknowledge-insecure-rfd")
    print(f"Warning: {rfd_reports.INSECURE_WARNING}", file=sys.stderr)
    result = rfd_reports.search_inspections(
        business=args.business,
        address=args.address,
        acknowledged=True,
    )
    if args.json:
        _output_json(result)
    else:
        rows = [[
            str(item.get("source") or ""),
            str(item.get("inspection_number") or ""),
            str(item.get("completed_date") or ""),
            str(item.get("business_name") or ""),
            str(item.get("address") or ""),
        ] for item in result["inspections"]]
        if rows:
            _output_table(["SOURCE", "INSPECTION", "COMPLETED", "BUSINESS", "ADDRESS"], rows)
        else:
            print("No inspection records returned.")
    return 0


def cmd_incidents_active(args: argparse.Namespace) -> int:
    result = incidents.fetch_active(
        agency=args.agency,
        incident_type=args.incident_type,
        limit=args.limit,
        use_cache=not args.no_cache,
    )
    if args.json:
        _output_json(result)
    else:
        rows = []
        for inc in result["incidents"]:
            rows.append([
                inc["jurisdiction"],
                inc["problem"],
                inc.get("address") or "",
                inc.get("timestamp") or "",
            ])
        if rows:
            _output_table(["AGENCY", "PROBLEM", "ADDRESS", "TIMESTAMP"], rows)
        else:
            print("No active incidents returned.")
        for warning in result.get("warnings", []):
            print(f"Warning: {warning}", file=sys.stderr)
        print(f"\n{result['source']}", file=sys.stderr)
        print(f"Retrieved: {result['retrieved_at']}", file=sys.stderr)
    return 0


_COMMANDS: dict[str, Any] = {
    "catalog": cmd_catalog,
    "search": cmd_search,
    "info": cmd_info,
    "query": cmd_query,
    "download": cmd_download,
    "categories": cmd_categories,
    "catalog-check": cmd_catalog_check,
}


_IMAGERY_COMMANDS: dict[str, Any] = {
    "catalog": cmd_imagery_catalog,
    "info": cmd_imagery_info,
    "export": cmd_imagery_export,
    "identify": cmd_imagery_identify,
    "statistics": cmd_imagery_statistics,
}


_TRANSIT_COMMANDS: dict[str, Any] = {
    "routes": cmd_transit_routes,
    "stops": cmd_transit_stops,
    "schedule": cmd_transit_schedule,
    "arrivals": cmd_transit_arrivals,
    "vehicles": cmd_transit_vehicles,
    "alerts": cmd_transit_alerts,
    "trip-updates": cmd_transit_trip_updates,
    "download-gtfs": cmd_transit_download_gtfs,
}


_DEVELOPMENT_COMMANDS: dict[str, Any] = {
    "search": cmd_development_search,
    "permit": cmd_development_permit,
    "inspections": cmd_development_inspections,
    "code-cases": cmd_development_code_cases,
    "licenses": cmd_development_licenses,
}


_MEETINGS_COMMANDS: dict[str, Any] = {
    "upcoming": cmd_meetings_upcoming,
    "list": cmd_meetings_list,
    "search": cmd_meetings_search,
    "show": cmd_meetings_show,
    "download-agenda": cmd_meetings_download_agenda,
    "download-minutes": cmd_meetings_download_minutes,
}

_POLICE_COMMANDS: dict[str, Any] = {
    "incidents": cmd_police_incidents,
    "recent": cmd_police_recent,
    "previous-day": cmd_police_previous_day,
    "history": cmd_police_history,
}

_FIRE_COMMANDS: dict[str, Any] = {
    "incidents": cmd_fire_incidents,
    "response-times": cmd_fire_response_times,
    "protection": cmd_fire_protection,
    "reports": cmd_fire_reports,
    "inspections": cmd_fire_inspections,
}

_INCIDENTS_COMMANDS: dict[str, Any] = {
    "active": cmd_incidents_active,
}


_GLOBAL_FLAG_SPEC: dict[str, int] = {
    "--json": 0,
    "--refresh": 0,
    "--cache-dir": 1,
    "--timeout": 1,
}


def extract_globals(argv: list[str]) -> list[str]:
    """Move global flags so they appear before the subcommand for argparse.

    Boolean flags consume no value; valued flags consume exactly one.
    """
    head: list[str] = []
    tail: list[str] = []
    i = 0
    while i < len(argv):
        arg = argv[i]
        if arg in _GLOBAL_FLAG_SPEC:
            head.append(arg)
            count = _GLOBAL_FLAG_SPEC[arg]
            for _ in range(count):
                i += 1
                if i < len(argv):
                    head.append(argv[i])
            i += 1
        else:
            tail.append(arg)
            i += 1
    return head + tail


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    if argv is None:
        argv = sys.argv[1:]
    args = parser.parse_args(extract_globals(argv))

    if args.cache_dir:
        os.environ["RALEIGH_CACHE"] = args.cache_dir

    os.environ[core.ENV_TIMEOUT] = str(args.timeout)

    if not args.command:
        parser.print_help()
        return 2

    try:
        if args.command in _COMMANDS:
            return _COMMANDS[args.command](args)

        if args.command == "imagery":
            if args.imagery_command in _IMAGERY_COMMANDS:
                return _IMAGERY_COMMANDS[args.imagery_command](args)
            parser.parse_args([args.command, "--help"])
            return 2

        if args.command == "transit":
            if args.transit_command in _TRANSIT_COMMANDS:
                return _TRANSIT_COMMANDS[args.transit_command](args)
            parser.parse_args([args.command, "--help"])
            return 2

        if args.command == "development":
            if args.development_command in _DEVELOPMENT_COMMANDS:
                return _DEVELOPMENT_COMMANDS[args.development_command](args)
            parser.parse_args([args.command, "--help"])
            return 2

        if args.command == "meetings":
            if args.meetings_command in _MEETINGS_COMMANDS:
                return _MEETINGS_COMMANDS[args.meetings_command](args)
            parser.parse_args([args.command, "--help"])
            return 2

        if args.command == "police":
            if args.police_command in _POLICE_COMMANDS:
                return _POLICE_COMMANDS[args.police_command](args)
            parser.parse_args([args.command, "--help"])
            return 2

        if args.command == "fire":
            if args.fire_command in _FIRE_COMMANDS:
                return _FIRE_COMMANDS[args.fire_command](args)
            parser.parse_args([args.command, "--help"])
            return 2

        if args.command == "incidents":
            if args.incidents_command in _INCIDENTS_COMMANDS:
                return _INCIDENTS_COMMANDS[args.incidents_command](args)
            parser.parse_args([args.command, "--help"])
            return 2

        if args.command == "geocode":
            return cmd_geocode(args)
        if args.command == "reverse-geocode":
            return cmd_reverse_geocode(args)
        if args.command == "suggest":
            return cmd_suggest(args)
        if args.command == "geocode-batch":
            return cmd_geocode_batch(args)

        if args.command == "news":
            return cmd_news(args)
        if args.command == "events":
            return cmd_events(args)
        if args.command == "projects":
            return cmd_projects(args)
        if args.command == "places":
            return cmd_places(args)
        if args.command == "services":
            return cmd_services(args)
        if args.command == "directory":
            return cmd_directory(args)
        if args.command == "alerts":
            return cmd_alerts(args)
        if args.command == "rss":
            return cmd_rss(args)

        parser.print_help()
        return 2
    except (core.SecurityError, core.RequestPolicyError, core.ResponseTooLargeError, hub.CatalogError, civic.ResourceError, development.UnsupportedEndpointError, imagery.CapabilityError, police.PoliceError, fire.FireError, fire_protection.FireProtectionError, rfd_reports.RFDReportError, incidents.IncidentFeedError, FileExistsError, ValueError, KeyError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    except urllib.error.HTTPError as exc:
        print(f"Error: HTTP {exc.code} from {exc.url}", file=sys.stderr)
        return 1
    except urllib.error.URLError as exc:
        print(f"Error: network failure: {exc.reason}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
