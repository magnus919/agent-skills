#!/usr/bin/env python3
"""Query the generated CNCF Landscape JSON API with bounded local filters."""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Callable, Mapping, Sequence
from datetime import datetime, timezone
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

DEFAULT_BASE_URL = "https://landscape.cncf.io/api"
SOURCE_PATHS = {
    "projects": "/projects/all.json",
    "members": "/members/all.json",
    "end-users": "/members/end-users.json",
}
SORT_FIELDS = ("name", "stars", "contributors", "latest-release")


class LandscapeError(RuntimeError):
    """A user-actionable failure while retrieving or interpreting the API."""


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Query the public CNCF Landscape JSON API and apply local filters. "
            "Output is a bounded JSON envelope."
        )
    )
    parser.add_argument(
        "--source",
        choices=tuple(SOURCE_PATHS),
        default="projects",
        help="Collection to query (default: projects).",
    )
    parser.add_argument(
        "--base-url",
        default=DEFAULT_BASE_URL,
        help="API base URL, useful for a compatible mirror or offline test server.",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=20.0,
        help="HTTP timeout in seconds (default: 20).",
    )
    parser.add_argument(
        "--search",
        help="Case-insensitive text search across name, summary, description, and taxonomy.",
    )
    parser.add_argument("--category", help="Case-insensitive category match.")
    parser.add_argument("--subcategory", help="Case-insensitive subcategory match.")
    parser.add_argument(
        "--maturity",
        action="append",
        help="Project maturity to include; repeat for multiple values.",
    )
    parser.add_argument("--license", dest="license_name", help="Substring match in repository license fields.")
    parser.add_argument("--country", help="Case-insensitive country match.")
    parser.add_argument(
        "--oss-only",
        action="store_true",
        help="Keep records whose API record has oss=true.",
    )
    parser.add_argument(
        "--has-license",
        action="store_true",
        help="Keep records with at least one non-empty repository license.",
    )
    parser.add_argument(
        "--has-release",
        action="store_true",
        help="Keep records with at least one non-empty repository latest_release.",
    )
    parser.add_argument(
        "--min-stars",
        type=int,
        metavar="N",
        help="Keep records with at least N stars in any listed repository.",
    )
    parser.add_argument(
        "--min-contributors",
        type=int,
        metavar="N",
        help="Keep records with at least N contributors in any listed repository.",
    )
    parser.add_argument(
        "--sort",
        choices=SORT_FIELDS,
        default="name",
        help="Sort field; numeric/release fields descend by default (default: name).",
    )
    parser.add_argument(
        "--ascending",
        action="store_true",
        help="Sort ascending, including for numeric fields.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=20,
        help="Maximum records to return; 0 means no limit (default: 20).",
    )
    return parser


def _fold(value: Any) -> str:
    return str(value or "").strip().casefold()


def _repositories(record: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    repositories = record.get("repositories")
    if not isinstance(repositories, list):
        return []
    return [item for item in repositories if isinstance(item, dict)]


def _numeric_values(record: Mapping[str, Any], field: str) -> list[int]:
    values: list[int] = []
    for repository in _repositories(record):
        value = repository.get(field)
        if isinstance(value, bool):
            continue
        if isinstance(value, (int, float)):
            values.append(int(value))
    return values


def _licenses(record: Mapping[str, Any]) -> list[str]:
    return [str(value) for value in (repo.get("license") for repo in _repositories(record)) if value]


def _latest_releases(record: Mapping[str, Any]) -> list[str]:
    return [str(value) for value in (repo.get("latest_release") for repo in _repositories(record)) if value]


def _search_text(record: Mapping[str, Any]) -> str:
    fields = (
        record.get("name"),
        record.get("summary"),
        record.get("description"),
        record.get("category"),
        record.get("subcategory"),
    )
    return " ".join(str(value) for value in fields if value).casefold()


def matches(record: Mapping[str, Any], args: argparse.Namespace) -> bool:
    if args.search and _fold(args.search) not in _search_text(record):
        return False
    if args.category and _fold(record.get("category")) != _fold(args.category):
        return False
    if args.subcategory and _fold(record.get("subcategory")) != _fold(args.subcategory):
        return False
    if args.maturity and _fold(record.get("maturity")) not in {_fold(item) for item in args.maturity}:
        return False
    if args.license_name and not any(_fold(args.license_name) in _fold(item) for item in _licenses(record)):
        return False
    if args.country and _fold(record.get("country")) != _fold(args.country):
        return False
    if args.oss_only and record.get("oss") is not True:
        return False
    if args.has_license and not _licenses(record):
        return False
    if args.has_release and not _latest_releases(record):
        return False
    if args.min_stars is not None and max(_numeric_values(record, "stars"), default=0) < args.min_stars:
        return False
    return args.min_contributors is None or max(_numeric_values(record, "contributors"), default=0) >= args.min_contributors


def _sort_key(record: Mapping[str, Any], field: str) -> Any:
    if field == "name":
        return _fold(record.get("name"))
    if field == "stars":
        return max(_numeric_values(record, "stars"), default=0)
    if field == "contributors":
        return max(_numeric_values(record, "contributors"), default=0)
    if field == "latest-release":
        return max(_latest_releases(record), default="")
    raise LandscapeError(f"Unsupported sort field: {field}")


def select_records(
    records: Sequence[Mapping[str, Any]],
    args: argparse.Namespace,
) -> list[Mapping[str, Any]]:
    selected = [record for record in records if matches(record, args)]
    descending = not args.ascending and args.sort != "name"
    selected.sort(key=lambda record: _sort_key(record, args.sort), reverse=descending)
    if args.limit < 0:
        raise LandscapeError("--limit must be zero or greater")
    if args.limit:
        return selected[: args.limit]
    return selected


def fetch_records(
    url: str,
    timeout: float,
    opener: Callable[..., Any] | None = None,
) -> tuple[list[Mapping[str, Any]], Mapping[str, Any]]:
    request = Request(
        url,
        headers={
            "Accept": "application/json",
            "User-Agent": "cncf-landscape-agent-skill/1.0",
        },
    )
    open_url = opener or urlopen
    try:
        with open_url(request, timeout=timeout) as response:
            status = getattr(response, "status", 200)
            headers = getattr(response, "headers", {})
            content_type = str(headers.get("Content-Type", ""))
            payload = response.read()
    except HTTPError as exc:
        raise LandscapeError(f"Landscape API returned HTTP {exc.code} for {url}") from exc
    except URLError as exc:
        raise LandscapeError(f"Could not reach Landscape API at {url}: {exc.reason}") from exc
    except OSError as exc:
        raise LandscapeError(f"Could not read Landscape API at {url}: {exc}") from exc

    if status < 200 or status >= 300:
        raise LandscapeError(f"Landscape API returned HTTP {status} for {url}")
    if "json" not in content_type.casefold():
        raise LandscapeError(
            f"Expected JSON from {url} but received Content-Type {(content_type or '(missing)')!r}; "
            "an SPA fallback may have returned HTML."
        )
    try:
        decoded = json.loads(payload.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise LandscapeError(f"Landscape API response from {url} was not valid UTF-8 JSON") from exc
    if not isinstance(decoded, list):
        raise LandscapeError(f"Expected a JSON array from {url}")
    records: list[Mapping[str, Any]] = []
    for item in decoded:
        if not isinstance(item, dict):
            raise LandscapeError(f"Landscape API response from {url} contained a non-object record")
        records.append(item)
    return records, headers


def _filters(args: argparse.Namespace) -> dict[str, Any]:
    return {
        key: value
        for key, value in {
            "search": args.search,
            "category": args.category,
            "subcategory": args.subcategory,
            "maturity": args.maturity,
            "license": args.license_name,
            "country": args.country,
            "oss_only": args.oss_only,
            "has_license": args.has_license,
            "has_release": args.has_release,
            "min_stars": args.min_stars,
            "min_contributors": args.min_contributors,
        }.items()
        if value not in (None, False, [], "")
    }


def run(args: argparse.Namespace, opener: Callable[..., Any] | None = None) -> dict[str, Any]:
    url = args.base_url.rstrip("/") + SOURCE_PATHS[args.source]
    records, headers = fetch_records(url, args.timeout, opener=opener)
    selected = select_records(records, args)
    return {
        "source": args.source,
        "endpoint": url,
        "retrieved_at": datetime.now(timezone.utc).isoformat(),
        "last_modified": headers.get("Last-Modified"),
        "total_records": len(records),
        "returned_records": len(selected),
        "filters": _filters(args),
        "sort": {"field": args.sort, "ascending": args.ascending},
        "items": selected,
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        result = run(args)
    except LandscapeError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2
    json.dump(result, sys.stdout, indent=2)
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
