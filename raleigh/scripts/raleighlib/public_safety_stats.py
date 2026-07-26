"""Official RPD and RFD aggregate statistics published on RaleighNC.gov."""

from __future__ import annotations

import re
import urllib.error
import urllib.parse
from datetime import datetime, timezone
from html.parser import HTMLParser
from typing import Any

from raleighlib import core


SOURCES = {
    "police": {
        "id": "40ebbee4-2477-4f7d-9623-257685345e3d",
        "title": "Raleigh's Crime Data",
        "page_url": "https://raleighnc.gov/police/services/raleighs-crime-data",
    },
    "fire": {
        "id": "f95a0f43-3dbf-4378-b7c7-b1bdda20eb24",
        "title": "View Raleigh Fire Statistics",
        "page_url": "https://raleighnc.gov/fire/services/view-raleigh-fire-statistics",
    },
}


class PublishedStatisticsError(ValueError):
    """Raised when an official statistics page no longer matches its contract."""


_TERMINAL_CONTROLS_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]")


class _FragmentParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.links: list[dict[str, Any]] = []
        self.tables: list[list[list[str]]] = []
        self.text: list[str] = []
        self._year: int | None = None
        self._heading: list[str] | None = None
        self._link: dict[str, Any] | None = None
        self._table: list[list[str]] | None = None
        self._row: list[str] | None = None
        self._cell: list[str] | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.casefold()
        if tag == "h5":
            self._heading = []
        elif tag == "a":
            self._link = {"href": dict(attrs).get("href"), "text": [], "year": self._year}
        elif tag == "table":
            self._table = []
        elif tag == "tr" and self._table is not None:
            self._row = []
        elif tag in {"th", "td"} and self._row is not None:
            self._cell = []

    def handle_data(self, data: str) -> None:
        self.text.append(data)
        if self._heading is not None:
            self._heading.append(data)
        if self._link is not None:
            self._link["text"].append(data)
        if self._cell is not None:
            self._cell.append(data)

    def handle_endtag(self, tag: str) -> None:
        tag = tag.casefold()
        if tag == "h5" and self._heading is not None:
            value = _clean(" ".join(self._heading))
            self._year = int(value) if re.fullmatch(r"20\d{2}", value) else None
            self._heading = None
        elif tag == "a" and self._link is not None:
            self._link["text"] = _clean(" ".join(self._link["text"]))
            self.links.append(self._link)
            self._link = None
        elif tag in {"th", "td"} and self._cell is not None and self._row is not None:
            self._row.append(_clean(" ".join(self._cell)))
            self._cell = None
        elif tag == "tr" and self._row is not None and self._table is not None:
            if self._row:
                self._table.append(self._row)
            self._row = None
        elif tag == "table" and self._table is not None:
            self.tables.append(self._table)
            self._table = None


def _clean(value: str) -> str:
    return " ".join(_TERMINAL_CONTROLS_RE.sub("", value).split())


def _source(agency: str) -> dict[str, str]:
    try:
        return SOURCES[agency]
    except KeyError as exc:
        raise PublishedStatisticsError(f"unknown public-safety agency: {agency}") from exc


def _document_url(href: Any, page_url: str, agency: str) -> str:
    if not isinstance(href, str) or not href.strip():
        raise PublishedStatisticsError("published report link is missing")
    if _TERMINAL_CONTROLS_RE.search(href):
        raise PublishedStatisticsError("published report link contains control characters")
    url = urllib.parse.urljoin(page_url, href)
    parsed = urllib.parse.urlparse(url)
    try:
        port = parsed.port
    except ValueError as exc:
        raise PublishedStatisticsError("published report link has an invalid port") from exc
    if (
        parsed.scheme != "https"
        or parsed.username is not None
        or parsed.password is not None
        or port not in (None, 443)
        or parsed.params
        or parsed.query
        or parsed.fragment
    ):
        raise PublishedStatisticsError("published report link left the approved HTTPS contract")
    host = (parsed.hostname or "").casefold()
    decoded_segments = urllib.parse.unquote(parsed.path).split("/")
    if any(segment in {".", ".."} for segment in decoded_segments):
        raise PublishedStatisticsError("published report link contains a path traversal segment")
    if agency == "fire" and host == "raleighnc.gov" and parsed.path.startswith("/fire/news/"):
        return url
    if (
        host == "cityofraleigh0drupal.blob.core.usgovcloudapi.net"
        and re.fullmatch(
            rf"/drupal-prod/{'COR23' if agency == 'police' else 'COR18'}/[^/]+\.[Pp][Dd][Ff]",
            parsed.path,
        )
    ):
        return url
    raise PublishedStatisticsError("published report link left the approved document origins")


def _fetch_page(agency: str) -> tuple[dict[str, Any], dict[str, str]]:
    source = _source(agency)
    url = (
        f"https://raleighnc.gov/jsonapi/node/service/{source['id']}"
        "?include=field_content_primary"
    )
    payload = core.require_object(core.json_request(url), "published statistics request")
    data = payload.get("data")
    included = payload.get("included")
    if not isinstance(data, dict) or not isinstance(included, list):
        raise PublishedStatisticsError("published statistics source returned invalid JSON:API data")
    attrs = data.get("attributes")
    path = attrs.get("path") if isinstance(attrs, dict) else None
    if (
        data.get("type") != "node--service"
        or data.get("id") != source["id"]
        or not isinstance(attrs, dict)
        or not isinstance(path, dict)
        or attrs.get("status") is not True
        or attrs.get("title") != source["title"]
        or path.get("alias") != urllib.parse.urlparse(source["page_url"]).path
    ):
        raise PublishedStatisticsError("published statistics page identity changed")

    relationships = data.get("relationships")
    if not isinstance(relationships, dict):
        raise PublishedStatisticsError("published statistics content relationships are invalid")
    relationship = relationships.get("field_content_primary", {})
    related = relationship.get("data") if isinstance(relationship, dict) else None
    if not isinstance(related, list):
        raise PublishedStatisticsError("published statistics content relationship is missing")
    referenced: set[tuple[str, str]] = set()
    for item in related:
        if (
            not isinstance(item, dict)
            or not isinstance(item.get("type"), str)
            or not isinstance(item.get("id"), str)
        ):
            raise PublishedStatisticsError("published statistics relationship identifiers are invalid")
        referenced.add((item["type"], item["id"]))
    fragments: dict[str, str] = {}
    for item in included:
        if not isinstance(item, dict) or item.get("type") != "paragraph--stories_text":
            continue
        if (item.get("type"), item.get("id")) not in referenced:
            raise PublishedStatisticsError("published statistics included an unreferenced content section")
        item_attrs = item.get("attributes")
        if not isinstance(item_attrs, dict) or item_attrs.get("status") is not True:
            continue
        heading = item_attrs.get("field_heading")
        formatted = item_attrs.get("field_stories_text_formatted")
        html = formatted.get("value") if isinstance(formatted, dict) else None
        if isinstance(heading, str) and isinstance(html, str):
            if heading in fragments:
                raise PublishedStatisticsError(f"published statistics section is duplicated: {heading}")
            fragments[heading] = html
    metadata = {
        "url": source["page_url"],
        "retrieved_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "published_changed_at": str(attrs.get("changed") or ""),
    }
    return {"fragments": fragments}, metadata


def _parse_police(fragments: dict[str, str], page_url: str) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    html = fragments.get("Summary of Crime Statistics by Year")
    if html is None:
        raise PublishedStatisticsError("police report index section is missing")
    parser = _FragmentParser()
    parser.feed(html)
    reports = []
    for link in parser.links:
        label = link["text"]
        year = link["year"]
        quarter_match = re.search(r"\bQ([1-4])\b", label, re.IGNORECASE)
        if not isinstance(year, int):
            raise PublishedStatisticsError("police report is not grouped under a year")
        if "annual" in label.casefold():
            period, quarter = "annual", None
        elif quarter_match:
            period, quarter = "quarterly", int(quarter_match.group(1))
        else:
            raise PublishedStatisticsError(f"unrecognized police publication label: {label}")
        reports.append({
            "agency": "police",
            "year": year,
            "period": period,
            "quarter": quarter,
            "label": label,
            "document_url": _document_url(link["href"], page_url, "police"),
        })
    if not reports:
        raise PublishedStatisticsError("police report index returned no publications")
    return [], reports


def _parse_fire(fragments: dict[str, str], page_url: str) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    annual_html = fragments.get("Previous Years Statistics")
    quarterly_html = fragments.get("Quarterly Report")
    if annual_html is None or quarterly_html is None:
        raise PublishedStatisticsError("fire report index section is missing")

    reports: list[dict[str, Any]] = []
    annual_parser = _FragmentParser()
    annual_parser.feed(annual_html)
    for link in annual_parser.links:
        if not re.fullmatch(r"20\d{2}", link["text"]):
            raise PublishedStatisticsError(f"unrecognized fire annual publication label: {link['text']}")
        year = int(link["text"])
        reports.append({
            "agency": "fire", "year": year, "period": "annual", "quarter": None,
            "label": link["text"], "document_url": _document_url(link["href"], page_url, "fire"),
        })

    quarterly_parser = _FragmentParser()
    quarterly_parser.feed(quarterly_html)
    for link in quarterly_parser.links:
        url = _document_url(link["href"], page_url, "fire")
        period = re.search(r"(?:^|[-_/])q([1-4])-(20\d{2})(?:[-_/]|$)", url, re.IGNORECASE)
        if period is None:
            raise PublishedStatisticsError("fire quarterly report URL has no stable quarter and year")
        reports.append({
            "agency": "fire", "year": int(period.group(2)), "period": "quarterly",
            "quarter": int(period.group(1)), "label": link["text"], "document_url": url,
        })

    statistic_headings = [
        heading for heading in fragments
        if re.fullmatch(r"20\d{2} Statistics", heading)
    ]
    if not statistic_headings:
        raise PublishedStatisticsError("fire incident statistics section is missing")

    datasets: list[dict[str, Any]] = []
    for heading, html in fragments.items():
        match = re.fullmatch(r"(20\d{2}) Statistics", heading)
        if match is None:
            continue
        parser = _FragmentParser()
        parser.feed(html)
        if len(parser.tables) != 1 or len(parser.tables[0]) < 2:
            raise PublishedStatisticsError(f"fire statistics table is missing for {match.group(1)}")
        rows = parser.tables[0]
        if rows[0] != ["Incident Type", "Totals"]:
            raise PublishedStatisticsError("fire statistics table headers changed")
        values = []
        for row in rows[1:]:
            if len(row) != 2 or not row[0] or not re.fullmatch(r"\d[\d,]*", row[1]):
                raise PublishedStatisticsError("fire statistics table contains a malformed row")
            values.append({"label": row[0], "value": int(row[1].replace(",", "")), "published_value": row[1]})
        datasets.append({"year": int(match.group(1)), "kind": "incident_totals", "values": values})

    sprinkler_html = fragments.get("Sprinkler Saves Stats")
    if sprinkler_html is None:
        raise PublishedStatisticsError("fire sprinkler statistics section is missing")
    parser = _FragmentParser()
    parser.feed(sprinkler_html)
    year_match = re.search(r"\b(20\d{2}) Sprinkler Saves Statistics\b", _clean(" ".join(parser.text)))
    if year_match is None or len(parser.tables) != 1 or len(parser.tables[0]) < 2:
        raise PublishedStatisticsError("fire sprinkler statistics contract changed")
    rows = parser.tables[0]
    if rows[0] != ["Type", "Description", "Statistic", "Percentage"]:
        raise PublishedStatisticsError("fire sprinkler statistics table headers changed")
    values = []
    for row in rows[1:]:
        if len(row) != 4 or not row[1] or not row[2]:
            raise PublishedStatisticsError("fire sprinkler statistics table contains a malformed row")
        values.append({"type": row[0] or None, "label": row[1], "published_value": row[2], "published_percentage": row[3]})
    datasets.append({"year": int(year_match.group(1)), "kind": "sprinkler_saves", "values": values})

    if not reports or not datasets:
        raise PublishedStatisticsError("fire statistics source returned no publications or structured totals")
    return datasets, reports


def _published(agency: str) -> dict[str, Any]:
    page, metadata = _fetch_page(agency)
    fragments = page["fragments"]
    if agency == "police":
        datasets, reports = _parse_police(fragments, metadata["url"])
    else:
        datasets, reports = _parse_fire(fragments, metadata["url"])
    return {"datasets": datasets, "reports": reports, "source": metadata}


def _assert_available(items: list[dict[str, Any]]) -> None:
    unique = {(item["document_url"], item["agency"]) for item in items}
    for url, agency in unique:
        try:
            final_url = core.probe_url(url)
            _document_url(final_url, url, agency)
        except (core.SecurityError, urllib.error.HTTPError, urllib.error.URLError) as exc:
            raise PublishedStatisticsError(f"published document is unavailable: {url}: {exc}") from exc


def statistics(agency: str, year: int | None = None) -> dict[str, Any]:
    published = _published(agency)
    years = sorted({item["year"] for item in published["datasets"] + published["reports"]}, reverse=True)
    if year is not None and year not in years:
        raise PublishedStatisticsError(f"no published {agency} statistics found for {year}")
    datasets = [item for item in published["datasets"] if year is None or item["year"] == year]
    reports = [item for item in published["reports"] if year is None or item["year"] == year]
    _assert_available(reports)
    warnings = []
    if year is not None and not datasets:
        warnings.append("Published totals are document-only for this year; PDF contents were not parsed.")
    if agency == "fire":
        warnings.append(
            "Published medical totals are aggregate-only and must not be joined to or used to infer excluded incident records."
        )
    return {
        "agency": agency,
        "classification": "official_published_statistics",
        "year": year,
        "available_years": years,
        "datasets": datasets,
        "reports": reports,
        "source": published["source"],
        "warnings": warnings,
    }


def reports(agency: str, year: int | None = None, quarter: int | None = None) -> dict[str, Any]:
    if quarter is not None and year is None:
        raise PublishedStatisticsError("--quarter requires --year")
    published = _published(agency)
    available_years = sorted({item["year"] for item in published["reports"]}, reverse=True)
    if year is not None and year not in available_years:
        raise PublishedStatisticsError(f"no published {agency} reports found for {year}")
    selected = [
        item for item in published["reports"]
        if (year is None or item["year"] == year) and (quarter is None or item["quarter"] == quarter)
    ]
    if not selected:
        period = f" Q{quarter}" if quarter is not None else ""
        raise PublishedStatisticsError(f"no published {agency} report found for {year}{period}")
    _assert_available(selected)
    return {
        "agency": agency,
        "classification": "official_published_reports",
        "year": year,
        "quarter": quarter,
        "available_years": available_years,
        "reports": selected,
        "source": published["source"],
        "warnings": ["Document links are preserved from the official index; PDF contents were not parsed."],
    }
