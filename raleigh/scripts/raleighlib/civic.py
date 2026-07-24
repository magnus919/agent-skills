"""RaleighNC.gov public civic-content adapter (JSON:API + RSS)."""

from __future__ import annotations

import urllib.parse
import xml.etree.ElementTree as ET
from datetime import date, datetime
from typing import Any

from raleighlib import core


JSONAPI_ROOT = "https://raleighnc.gov/jsonapi"
RSS_FEED = "https://raleighnc.gov/rss.xml"

# Explicit allowlist of public content resource types.
ALLOWED_RESOURCE_TYPES = frozenset({
    "node--news",
    "node--event",
    "node--event_series",
    "node--project",
    "node--place",
    "node--service",
    "node--service_core",
    "node--directory_entry",
    "node--organizational_unit",
    "node--alert",
    "node--alert_update",
    "node--status_alert",
})


class ResourceError(Exception):
    """Raised when a disallowed resource type is requested."""


def _resource_type_to_parts(resource_type: str) -> tuple[str, str]:
    """Split a resource type into entity_type and bundle."""
    if resource_type not in ALLOWED_RESOURCE_TYPES:
        raise ResourceError(f"Resource type is not allowlisted: {resource_type}")
    parts = resource_type.split("--")
    if len(parts) != 2:
        raise ResourceError(f"Unsupported resource type format: {resource_type}")
    return parts[0], parts[1]


def _discover_resource_paths() -> dict[str, str]:
    """Discover canonical JSON:API paths from the index and cache them."""
    cached = core.read_cache("jsonapi-paths.json", max_age_seconds=86400)
    if isinstance(cached, dict) and all(
        isinstance(key, str) and isinstance(value, str)
        for key, value in cached.items()
    ):
        return cached
    try:
        index = core.json_request(JSONAPI_ROOT)
    except Exception:
        return {}
    if not isinstance(index, dict) or not isinstance(index.get("links"), dict):
        return {}
    paths: dict[str, str] = {}
    for key, value in index["links"].items():
        if "--" not in key:
            continue
        href = _extract_href(value)
        if href:
            paths[key] = href
    core.write_cache("jsonapi-paths.json", paths)
    return paths


def _resource_type_to_path(resource_type: str) -> str:
    """Map a resource type to its canonical JSON:API collection URL."""
    entity_type, bundle = _resource_type_to_parts(resource_type)
    discovered = _discover_resource_paths()
    if resource_type in discovered:
        url = urllib.parse.urljoin(JSONAPI_ROOT + "/", discovered[resource_type])
        parsed = urllib.parse.urlparse(url)
        expected_path = f"/jsonapi/{entity_type}/{bundle}"
        try:
            port = parsed.port
        except ValueError as exc:
            raise ResourceError("Raleigh JSON:API resource path has an invalid port") from exc
        if (
            parsed.scheme != "https"
            or parsed.hostname != "raleighnc.gov"
            or parsed.username is not None
            or parsed.password is not None
            or port not in (None, 443)
            or parsed.path.rstrip("/") != expected_path
        ):
            raise ResourceError(
                f"Raleigh JSON:API index returned an invalid path for {resource_type}"
            )
        return url
    # Fallback to conventional Drupal path.
    return f"{JSONAPI_ROOT}/{entity_type}/{bundle}"


def _extract_href(value: Any) -> str | None:
    """Return the href string from a JSON:API link object or string."""
    if isinstance(value, str):
        return value
    if isinstance(value, dict):
        return value.get("href")
    return None


def _validated_jsonapi_next(value: Any, current_url: str = JSONAPI_ROOT + "/") -> str | None:
    """Return a pagination URL only when it stays on the JSON:API origin/path."""
    href = _extract_href(value)
    if href is None:
        return None
    url = urllib.parse.urljoin(current_url, href)
    parsed = urllib.parse.urlparse(url)
    current = urllib.parse.urlparse(current_url)
    if (
        parsed.scheme != "https"
        or parsed.hostname != "raleighnc.gov"
        or parsed.username is not None
        or parsed.password is not None
        or parsed.port not in (None, 443)
        or parsed.path.rstrip("/") != current.path.rstrip("/")
    ):
        raise ResourceError("Raleigh JSON:API pagination link left the expected origin or path")
    return url


def list_resource_types() -> list[str]:
    """Return the allowlisted public resource types."""
    return sorted(ALLOWED_RESOURCE_TYPES)


def _canonical_url(item: dict[str, Any]) -> str | None:
    """Return the canonical public page URL for a JSON:API item."""
    attrs = item.get("attributes", {})
    path_alias = attrs.get("path", {}).get("alias")
    if path_alias:
        return f"https://raleighnc.gov{path_alias}"
    links = item.get("links", {})
    return _extract_href(links.get("canonical")) or _extract_href(links.get("self"))


def _normalize_jsonapi_item(item: dict[str, Any]) -> dict[str, Any]:
    attrs = item.get("attributes", {})
    relationships: dict[str, Any] = {}
    for name, relationship in item.get("relationships", {}).items():
        if isinstance(relationship, dict):
            relationships[name] = relationship.get("data")
    return {
        "id": item.get("id"),
        "type": item.get("type"),
        "title": attrs.get("title") or attrs.get("label") or attrs.get("name"),
        "created": attrs.get("created"),
        "changed": attrs.get("changed"),
        "status": attrs.get("status"),
        "url": _canonical_url(item),
        "attributes": attrs,
        "relationships": relationships,
    }


def _matches_search(record: dict[str, Any], search: str | None) -> bool:
    if not search:
        return True
    term = search.lower()
    text = " ".join(
        str(record.get(k, "")) for k in ("title", "attributes")
    ).lower()
    return term in text


def _matches_date_range(
    record: dict[str, Any],
    date_from: str | None,
    date_to: str | None,
    date_field: str | None,
) -> bool:
    if not date_from and not date_to:
        return True
    attrs = record.get("attributes", {})
    value = attrs.get(date_field) if date_field else None
    if isinstance(value, dict):
        value = value.get("value")
    if not value and "created" in attrs:
        value = attrs["created"]
    if not value:
        return False
    value_str = str(value).strip()
    try:
        if "T" in value_str or " " in value_str:
            normalized = value_str.replace("Z", "+00:00")
            value_date = datetime.fromisoformat(normalized).date()
        else:
            value_date = date.fromisoformat(value_str)
    except ValueError as exc:
        raise ResourceError(f"Raleigh JSON:API returned an invalid date: {value_str}") from exc
    if date_from and value_date < date.fromisoformat(date_from):
        return False
    if date_to and value_date > date.fromisoformat(date_to):
        return False
    return True


def _matches_relationship(record: dict[str, Any], relationship: str | None) -> bool:
    """Match a client-side JSON:API relationship expression, FIELD=ID."""
    if not relationship:
        return True
    if "=" not in relationship:
        raise ValueError("relationship must use FIELD=ID")
    field, target_id = (part.strip() for part in relationship.split("=", 1))
    if not field or not target_id:
        raise ValueError("relationship must use FIELD=ID")
    data = record.get("relationships", {}).get(field)
    related = data if isinstance(data, list) else [data]
    return any(
        isinstance(item, dict) and str(item.get("id") or "") == target_id
        for item in related
    )


def _build_collection_url(base: str, page_limit: int) -> str:
    query = {"filter[status]": "1", "page[limit]": page_limit}
    return f"{base}?{urllib.parse.urlencode(query)}"


def fetch_jsonapi(
    resource_type: str,
    limit: int = 20,
    search: str | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
    date_field: str | None = None,
    relationship: str | None = None,
) -> list[dict[str, Any]]:
    """Fetch paginated JSON:API records for an allowlisted resource type.

    Only ``filter[status]=1`` is sent to the server. Search and date filters are
    applied client-side because the Raleigh JSON:API implementation does not
    expose a verified server-side fulltext or date filter.
    """
    core.require_positive_limit(limit)
    if relationship:
        if "=" not in relationship or not all(
            part.strip() for part in relationship.split("=", 1)
        ):
            raise ValueError("relationship must use FIELD=ID")
    base = _resource_type_to_path(resource_type)
    # Client-side filters may need to inspect many upstream records before
    # finding ``limit`` matches. Use a bounded service page size independent of
    # the requested output count so selective date/search filters remain usable.
    url = _build_collection_url(base, page_limit=max(50, min(limit, 100)))
    records: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    pages = 0
    max_pages = 100
    while url and pages < max_pages:
        pages += 1
        data = core.json_request(url)
        if not isinstance(data, dict):
            raise ResourceError("Raleigh JSON:API returned a non-object document")
        items = data.get("data", [])
        if not isinstance(items, list):
            raise ResourceError("Raleigh JSON:API returned invalid data")
        for item in items:
            if not isinstance(item, dict):
                raise ResourceError("Raleigh JSON:API returned a non-object resource")
            attributes = item.get("attributes")
            if not isinstance(attributes, dict) or attributes.get("status") is not True:
                continue
            record = _normalize_jsonapi_item(item)
            rid = record.get("id")
            if rid in seen_ids:
                continue
            seen_ids.add(rid)
            if (
                _matches_search(record, search)
                and _matches_date_range(record, date_from, date_to, date_field)
                and _matches_relationship(record, relationship)
            ):
                records.append(record)
                if len(records) >= limit:
                    return records
        links = data.get("links", {})
        if not isinstance(links, dict):
            raise ResourceError("Raleigh JSON:API returned invalid links")
        url = _validated_jsonapi_next(links.get("next"), url)
    if url:
        raise ResourceError(f"Raleigh JSON:API exceeded {max_pages} pages")
    return records


def fetch_news(
    limit: int = 20,
    search: str | None = None,
    relationship: str | None = None,
) -> list[dict[str, Any]]:
    """Fetch news items."""
    return fetch_jsonapi("node--news", limit=limit, search=search, relationship=relationship)


def fetch_events(
    limit: int = 20,
    date_from: str | None = None,
    date_to: str | None = None,
    search: str | None = None,
    relationship: str | None = None,
) -> list[dict[str, Any]]:
    """Fetch events filtered by date range."""
    return fetch_jsonapi(
        "node--event",
        limit=limit,
        search=search,
        date_from=date_from,
        date_to=date_to,
        date_field="field_event_date",
        relationship=relationship,
    )


def fetch_projects(
    limit: int = 20,
    search: str | None = None,
    relationship: str | None = None,
) -> list[dict[str, Any]]:
    """Fetch projects."""
    return fetch_jsonapi("node--project", limit=limit, search=search, relationship=relationship)


def fetch_places(
    limit: int = 20,
    search: str | None = None,
    relationship: str | None = None,
) -> list[dict[str, Any]]:
    """Fetch places."""
    return fetch_jsonapi("node--place", limit=limit, search=search, relationship=relationship)


def fetch_services(
    limit: int = 20,
    search: str | None = None,
    relationship: str | None = None,
) -> list[dict[str, Any]]:
    """Fetch services."""
    return fetch_jsonapi("node--service", limit=limit, search=search, relationship=relationship)


def fetch_directory(
    limit: int = 20,
    search: str | None = None,
    relationship: str | None = None,
) -> list[dict[str, Any]]:
    """Fetch directory entries."""
    return fetch_jsonapi(
        "node--directory_entry", limit=limit, search=search, relationship=relationship
    )


def fetch_alerts(
    limit: int = 20,
    relationship: str | None = None,
) -> list[dict[str, Any]]:
    """Fetch public alerts."""
    return fetch_jsonapi("node--alert", limit=limit, relationship=relationship)


def fetch_rss(limit: int = 20, new_only: bool = False) -> list[dict[str, Any]]:
    """Fetch and parse the RSS feed."""
    core.require_positive_limit(limit)
    data = core.raw_request(RSS_FEED)
    root = ET.fromstring(data)
    items: list[dict[str, Any]] = []
    previous = set(core.read_cache("rss-seen.json") or []) if new_only else set()
    seen: set[str] = set()
    for channel in root.findall("channel"):
        for item in channel.findall("item"):
            title = item.findtext("title", default="").strip()
            link = item.findtext("link", default="").strip()
            pub_date = item.findtext("pubDate", default="").strip()
            description = item.findtext("description", default="").strip()
            guid = item.findtext("guid", default="").strip()
            identity = guid or link or f"{title}\0{pub_date}"
            if identity in seen or identity in previous:
                continue
            seen.add(identity)
            items.append(
                {
                    "title": title,
                    "url": link,
                    "pub_date": pub_date,
                    "description": description,
                }
            )
            if len(items) >= limit:
                break
        if len(items) >= limit:
            break
    if new_only:
        core.write_cache("rss-seen.json", sorted(previous | seen))
    return items
