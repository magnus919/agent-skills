"""ArcGIS Hub catalog discovery and normalization."""

from __future__ import annotations

import urllib.parse
from typing import Any

from raleighlib import core


HUB_SEARCH_URL = "https://data.raleighnc.gov/api/search/v1/collections/{collection}/items"


class CatalogError(Exception):
    """Raised for catalog discovery or resolution failures."""


def fetch_collection(collection: str, start_index: int = 1, num: int = 100) -> dict[str, Any]:
    """Fetch a page from a Hub search collection."""
    if start_index < 1:
        raise ValueError("start_index must be positive")
    core.require_positive_limit(num)
    url = HUB_SEARCH_URL.format(collection=collection)
    params = {"limit": num, "startindex": start_index}
    url = f"{url}?{urllib.parse.urlencode(params)}"
    return core.json_request(url)


def fetch_all_records(
    collection: str,
    max_records: int | None = None,
    max_pages: int = 100,
) -> list[dict[str, Any]]:
    """Paginate through a Hub collection and return all records."""
    if max_pages < 1:
        raise ValueError("max_pages must be at least 1")
    core.require_positive_limit(max_records, allow_none=True)
    records: list[dict[str, Any]] = []
    start_index = 1
    page_size = 100
    seen_pages: set[tuple[str, ...]] = set()
    expected_total: int | None = None
    for _page_number in range(max_pages):
        page = fetch_collection(collection, start_index=start_index, num=page_size)
        if not isinstance(page, dict):
            raise CatalogError(f"Hub collection {collection!r} returned a non-object page")
        matched = page.get("numberMatched")
        if matched is not None:
            if isinstance(matched, bool) or not isinstance(matched, int) or matched < 0:
                raise CatalogError(f"Hub collection {collection!r} returned invalid numberMatched")
            if expected_total is None:
                expected_total = matched
            elif matched != expected_total:
                raise CatalogError(f"Hub collection {collection!r} changed numberMatched")
        features = page.get("features", [])
        if not isinstance(features, list):
            raise CatalogError(f"Hub collection {collection!r} returned invalid features")
        if not features:
            if expected_total is not None and len(records) < expected_total:
                raise CatalogError(f"Hub collection {collection!r} ended before numberMatched")
            return records
        if any(not isinstance(feature, dict) for feature in features):
            raise CatalogError(f"Hub collection {collection!r} returned a non-object feature")
        page_ids: list[str] = []
        for feature in features:
            properties = feature.get("properties", {})
            if not isinstance(properties, dict):
                raise CatalogError(
                    f"Hub collection {collection!r} returned invalid feature properties"
                )
            page_ids.append(str(feature.get("id") or properties.get("id") or ""))
        page_key = tuple(page_ids)
        if any(not item for item in page_key):
            raise CatalogError(f"Hub collection {collection!r} returned a feature without an id")
        if page_key in seen_pages:
            raise CatalogError(f"Hub collection {collection!r} repeated a page")
        seen_pages.add(page_key)
        records.extend(features)
        if expected_total is not None and len(records) > expected_total:
            raise CatalogError(f"Hub collection {collection!r} exceeded numberMatched")
        start_index += len(features)
        if matched is not None and start_index > matched:
            return records
        if max_records is not None and len(records) >= max_records:
            return records[:max_records]
        # Only break on partial page when the server did not report a total.
        if matched is None and len(features) < page_size:
            return records
    raise CatalogError(f"Hub collection {collection!r} exceeded {max_pages} pages")


def _first(props: dict[str, Any], *keys: str) -> Any:
    for key in keys:
        if key in props and props[key] not in (None, ""):
            return props[key]
    return None


def _normalize_type(record_type: str | None) -> str:
    if not record_type:
        return "Unknown"
    record_type = record_type.strip()
    mapping = {
        "Feature Service": "FeatureServer",
        "Map Service": "MapServer",
        "Image Service": "ImageServer",
        "Table": "Table",
    }
    return mapping.get(record_type, record_type)


def normalize_record(record: dict[str, Any]) -> dict[str, Any]:
    """Normalize a Hub search record into a stable catalog item."""
    props = record.get("properties", {})
    record_type = _normalize_type(props.get("type") or record.get("type"))
    raw_url = props.get("url") or props.get("serviceUrl") or ""

    # ImageServer URLs are root services; never append a layer suffix.
    url = raw_url
    if record_type == "ImageServer" and url.endswith("/0"):
        url = url[:-2]

    tags = props.get("tags") or []
    categories = props.get("categories") or []
    if isinstance(categories, str):
        categories = [categories]
    category = categories[0] if categories else "Other"

    return {
        "id": record.get("id", ""),
        "title": _first(props, "title", "name") or "",
        "description": props.get("description") or "",
        "type": record_type,
        "url": url,
        "tags": tags,
        "categories": categories,
        "category": category,
        "owner": props.get("owner") or props.get("source") or "",
        "access": str(props.get("access") or "").lower(),
        "license": props.get("license") or "",
        "extent": props.get("extent"),
        "has_geometry": None,  # Resolved from layer metadata at query time.
        "created": props.get("created"),
        "modified": props.get("modified"),
    }


def fetch_catalog(max_records: int | None = None) -> list[dict[str, Any]]:
    """Return the live catalog across all curated collections."""
    core.require_positive_limit(max_records, allow_none=True)
    collections = ["dataset", "document", "appAndMap"]
    catalog: list[dict[str, Any]] = []
    for collection in collections:
        records = fetch_all_records(collection, max_records=max_records)
        normalized = (normalize_record(r) for r in records)
        catalog.extend(item for item in normalized if item.get("access") == "public")
    return catalog


def catalog_from_cache_or_live(
    max_age_seconds: int = 3600,
    allow_stale: bool = True,
) -> list[dict[str, Any]]:
    """Return cached catalog if fresh; otherwise fetch live and cache.

    On transient failure, fall back to a stale cache entry and label it.
    """
    cached = core.read_cache("hub-catalog.json", max_age_seconds=max_age_seconds)
    if cached is not None:
        return [item for item in cached if item.get("access") == "public"]

    try:
        catalog = fetch_catalog()
    except Exception as exc:
        if not allow_stale:
            raise CatalogError(f"Catalog refresh failed and stale cache is disabled: {exc}") from exc
        stale = core.read_cache("hub-catalog.json", max_age_seconds=None)
        if stale is None:
            raise CatalogError(f"Catalog refresh failed and no stale cache is available: {exc}") from exc
        for item in stale:
            item["_stale"] = True
            item["_stale_reason"] = str(exc)
        return [item for item in stale if item.get("access") == "public"]

    core.write_cache("hub-catalog.json", catalog)
    return catalog


def search_catalog(
    query: str,
    catalog: list[dict[str, Any]] | None = None,
    limit: int = 20,
) -> list[dict[str, Any]]:
    """Search catalog records by title, description, tags, and categories."""
    core.require_positive_limit(limit)
    if catalog is None:
        catalog = catalog_from_cache_or_live()
    terms = query.lower().split()
    scored: list[tuple[int, dict[str, Any]]] = []
    for item in catalog:
        if item.get("access") != "public":
            continue
        text = " ".join(
            str(x)
            for x in [
                item.get("title", ""),
                item.get("description", ""),
                " ".join(item.get("tags", [])),
                " ".join(item.get("categories", [])),
            ]
        ).lower()
        if all(term in text for term in terms):
            score = 0
            title_lower = item.get("title", "").lower()
            if query.lower() in title_lower:
                score += 10
            if any(term in title_lower for term in terms):
                score += 5
            scored.append((score, item))
    scored.sort(key=lambda x: (x[0], x[1].get("title", "").lower()), reverse=True)
    return [item for _, item in scored[:limit]]


def resolve_item(
    identifier: str,
    catalog: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Resolve a catalog item by stable ID or exact title."""
    if catalog is None:
        catalog = catalog_from_cache_or_live()
    catalog = [item for item in catalog if item.get("access") == "public"]
    by_id: dict[str, dict[str, Any]] = {}
    by_title: dict[str, dict[str, Any]] = {}
    for item in catalog:
        by_id[item.get("id", "")] = item
        by_title[item.get("title", "").lower()] = item

    if identifier in by_id:
        return by_id[identifier]

    key = identifier.lower()
    exact_matches = [item for item in catalog if item.get("title", "").lower() == key]
    if len(exact_matches) == 1:
        return exact_matches[0]
    if len(exact_matches) > 1:
        raise CatalogError(
            f"'{identifier}' matches multiple catalog items; supply the stable item ID"
        )

    # Fuzzy title match as fallback.
    matches = [item for item in catalog if key in item.get("title", "").lower()]
    if len(matches) == 1:
        return matches[0]
    if len(matches) > 1:
        titles = [m.get("title", "") for m in matches]
        raise CatalogError(
            f"'{identifier}' is ambiguous; matches: {', '.join(titles[:5])}"
        )
    raise CatalogError(f"'{identifier}' was not found in the catalog")
