"""Guarded adapter for the fragile plain-HTTP RFD Report System."""

from __future__ import annotations

import html
import re
import urllib.error
import urllib.parse
import urllib.request
from datetime import date, datetime, timezone
from html.parser import HTMLParser
from typing import Any

from raleighlib import core

BASE_URL = "http://rfdreports.net"
DATE_PATH = "/fd_date.php"
NARRATIVE_PATH = "/fd_incidentreport.php"
BUSINESS_PATH = "/fd_inspection_business_name.php"
ADDRESS_PATH = "/fd_inspection_business_address.php"
MAX_HTML_BYTES = 2 * 1024 * 1024
INSECURE_WARNING = (
    "RFD Report System uses unencrypted HTTP; search terms and returned data "
    "can be observed or altered in transit."
)

_REPORT_HEADERS = [
    "Incident Data", "Incident Type", "Incident #", "Dispatch Time",
    "Arrive Time", "Clear Time", "Address", "Unit", "Cross Street", "View Report",
]
_INSPECTION_HEADERS = [
    "Occupancy Name", "Address", "Inspection Type", "Data Completed",
    "View Report", "View Invoice",
]
_TERMINAL_CONTROLS_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]")


class RFDReportError(ValueError):
    """Raised when an RFD request or HTML contract is unsafe or incompatible."""


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise RFDReportError("RFD redirects are not allowed")


_OPENER = urllib.request.build_opener(_NoRedirect)


class _TableParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.rows: list[list[dict[str, Any]]] = []
        self._row: list[dict[str, Any]] | None = None
        self._cell: dict[str, Any] | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.casefold()
        if tag == "tr":
            if self._row:
                self.rows.append(self._row)
            self._row = []
        elif tag in {"th", "td"} and self._row is not None:
            self._cell = {"text": [], "links": []}
        elif tag == "a" and self._cell is not None:
            href = dict(attrs).get("href")
            if href:
                self._cell["links"].append(href)

    def handle_data(self, data: str) -> None:
        if self._cell is not None:
            self._cell["text"].append(data)

    def handle_endtag(self, tag: str) -> None:
        tag = tag.casefold()
        if tag in {"th", "td"} and self._cell is not None and self._row is not None:
            text = _safe_text(" ".join(self._cell["text"]))
            self._row.append({"text": html.unescape(text), "links": self._cell["links"]})
            self._cell = None
        elif tag == "tr" and self._row is not None:
            if self._row:
                self.rows.append(self._row)
            self._row = None


def _require_text(value: str, label: str) -> str:
    value = value.strip()
    if not value:
        raise RFDReportError(f"{label} must not be empty")
    if len(value) > 200 or any(ord(char) < 32 for char in value):
        raise RFDReportError(f"{label} is invalid")
    return value


def _safe_text(value: str) -> str:
    """Remove terminal controls from untrusted HTTP text and normalize whitespace."""
    return " ".join(_TERMINAL_CONTROLS_RE.sub("", value).split())


def _validate_contract(path: str, params: dict[str, str], method: str) -> str:
    contracts = {
        DATE_PATH: ("POST", {"date"}),
        NARRATIVE_PATH: ("GET", {"incidentnumber", "incidentdate"}),
        BUSINESS_PATH: ("POST", {"fd_business"}),
        ADDRESS_PATH: ("POST", {"fd_address"}),
    }
    expected = contracts.get(path)
    if expected != (method, set(params)):
        raise RFDReportError("unsupported RFD request contract")
    return BASE_URL + path


def _request(path: str, params: dict[str, str], method: str, *, acknowledged: bool) -> str:
    if not acknowledged:
        raise RFDReportError("RFD access requires --acknowledge-insecure-rfd")
    url = _validate_contract(path, params, method)
    encoded = urllib.parse.urlencode(params)
    data = encoded.encode("utf-8") if method == "POST" else None
    if method == "GET":
        url = f"{url}?{encoded}"
    headers = {"User-Agent": core.USER_AGENT, "Accept": "text/html"}
    if data is not None:
        headers["Content-Type"] = "application/x-www-form-urlencoded"
    request = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with _OPENER.open(request, timeout=core._get_timeout()) as response:
            final = urllib.parse.urlparse(response.geturl())
            if final.scheme != "http" or final.hostname != "rfdreports.net" or final.port not in (None, 80):
                raise RFDReportError("RFD response left the fixed insecure origin")
            body = core._read_limited(response, MAX_HTML_BYTES)
    except urllib.error.HTTPError as exc:
        raise RFDReportError(f"RFD returned HTTP {exc.code}") from exc
    text = body.decode("utf-8", errors="replace")
    lowered = text.casefold()
    if "internal server error" in lowered or "service unavailable" in lowered:
        raise RFDReportError("RFD returned an error page")
    return text


def _table_rows(html_text: str, expected_headers: list[str]) -> list[list[dict[str, Any]]]:
    parser = _TableParser()
    parser.feed(html_text)
    if not parser.rows:
        if re.search(r"\b(no (?:records|results|reports|inspections) (?:found|available))\b", html_text, re.I):
            return []
        raise RFDReportError("RFD HTML contract drift: no result table")
    headers = [cell["text"] for cell in parser.rows[0]]
    if headers != expected_headers:
        raise RFDReportError("RFD HTML contract drift: unexpected table headers")
    rows = parser.rows[1:]
    for row in rows:
        if len(row) != len(expected_headers):
            raise RFDReportError("RFD HTML contract drift: malformed result row")
    return rows


def _canonical_link(href: str, path: str, required: set[str]) -> str:
    parsed = urllib.parse.urlparse(urllib.parse.urljoin(BASE_URL + "/", href))
    params = urllib.parse.parse_qs(parsed.query, keep_blank_values=True)
    if parsed.scheme != "http" or parsed.hostname != "rfdreports.net" or parsed.path != path:
        raise RFDReportError("RFD HTML contract drift: unexpected result link")
    if set(params) != required or any(len(values) != 1 for values in params.values()):
        raise RFDReportError("RFD HTML contract drift: malformed result link")
    return urllib.parse.urlunparse(("http", "rfdreports.net", path, "", urllib.parse.urlencode({k: v[0] for k, v in params.items()}), ""))


def _inspection_link(href: str, number: str, address: str, name: str) -> str:
    """Validate the fixed report link, then repair upstream's unescaped # values."""
    parsed = urllib.parse.urlparse(urllib.parse.urljoin(BASE_URL + "/", href))
    params = urllib.parse.parse_qs(parsed.query, keep_blank_values=True)
    if parsed.scheme != "http" or parsed.hostname != "rfdreports.net" or parsed.path != "/fd_report.php":
        raise RFDReportError("RFD HTML contract drift: unexpected inspection link")
    if params.get("inspection_number") != [number]:
        raise RFDReportError("RFD HTML contract drift: inspection link identifier mismatch")
    return BASE_URL + "/fd_report.php?" + urllib.parse.urlencode({
        "inspection_number": number,
        "address": address,
        "name": name,
    })


def search_date(report_date: str, *, acknowledged: bool) -> list[dict[str, Any]]:
    report_date = _require_text(report_date, "date")
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", report_date):
        raise RFDReportError("date must use YYYY-MM-DD")
    try:
        requested_date = date.fromisoformat(report_date)
    except ValueError as exc:
        raise RFDReportError("date must use YYYY-MM-DD") from exc
    html_text = _request(DATE_PATH, {"date": report_date}, "POST", acknowledged=acknowledged)
    reports: list[dict[str, Any]] = []
    for row in _table_rows(html_text, _REPORT_HEADERS):
        values = [cell["text"] for cell in row]
        links = row[9]["links"]
        if not values[2] or len(links) != 1:
            raise RFDReportError("RFD HTML contract drift: report identifier or link missing")
        source_url = _canonical_link(
            links[0], NARRATIVE_PATH, {"incidentnumber", "incidentdate"}
        )
        try:
            row_date = datetime.strptime(values[0], "%m/%d/%Y").date()
        except ValueError as exc:
            raise RFDReportError("RFD HTML contract drift: invalid incident date") from exc
        source_params = urllib.parse.parse_qs(urllib.parse.urlparse(source_url).query)
        if row_date != requested_date:
            raise RFDReportError("RFD response included a report outside the requested date")
        if source_params.get("incidentnumber") != [values[2]] or source_params.get("incidentdate") != [report_date]:
            raise RFDReportError("RFD report row and source link do not match")
        reports.append({
            "source": "rfd-html",
            "source_fragility": "fragile-html-over-http",
            "incident_date": values[0],
            "incident_type_name": values[1],
            "incident_number": values[2],
            "dispatch_time": values[3],
            "arrive_time": values[4],
            "clear_time": values[5],
            "address": values[6],
            "unit": values[7],
            "cross_street": values[8],
            "source_url": source_url,
        })
    return reports


def search_inspections(*, business: str | None = None, address: str | None = None, acknowledged: bool) -> dict[str, Any]:
    if bool(business) == bool(address):
        raise RFDReportError("provide exactly one business name or address")
    if business is not None:
        query = _require_text(business, "business name")
        path, params = BUSINESS_PATH, {"fd_business": query}
        mode = "business"
    else:
        query = _require_text(address or "", "address")
        path, params = ADDRESS_PATH, {"fd_address": query}
        mode = "address"
    html_text = _request(path, params, "POST", acknowledged=acknowledged)
    inspections: list[dict[str, Any]] = []
    for row in _table_rows(html_text, _INSPECTION_HEADERS):
        values = [cell["text"] for cell in row]
        report_links = row[4]["links"]
        if not values[4] or len(report_links) != 1:
            raise RFDReportError("RFD HTML contract drift: inspection identifier or link missing")
        source_url = _inspection_link(
            report_links[0], values[4], values[1], values[0]
        )
        inspections.append({
            "source": "rfd-html",
            "source_fragility": "fragile-html-over-http",
            "business_name": values[0],
            "address": values[1],
            "inspection_type": values[2],
            "completed_date": values[3],
            "inspection_number": values[4],
            "source_url": source_url,
        })
    return {
        "query": {mode: query},
        "inspections": inspections,
        "source": {
            "source": "rfd-html",
            "url": BASE_URL + path,
            "retrieved_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        },
        "warnings": [INSECURE_WARNING],
    }


def fetch_narrative(incident_number: str, incident_date: str, *, acknowledged: bool) -> dict[str, Any]:
    incident_number = _require_text(incident_number, "incident number")
    incident_date = _require_text(incident_date, "incident date")
    html_text = _request(
        NARRATIVE_PATH,
        {"incidentnumber": incident_number, "incidentdate": incident_date},
        "GET",
        acknowledged=acknowledged,
    )
    if "City of Raleigh Fire Department Basic Fire Report" not in html_text:
        raise RFDReportError("RFD narrative page identity was not recognized")
    number_match = re.search(r"Incident Number:</b>\s*([^<]+)", html_text, re.I)
    date_match = re.search(r"Alarm Date:</b>\s*([^<]+)", html_text, re.I)
    narrative_match = re.search(
        r"<b>\s*narrative(?:\&quot;|\")?\s*:\s*(.*?)</b>", html_text, re.I | re.S
    )
    if not number_match or not date_match or not narrative_match:
        raise RFDReportError("RFD HTML contract drift: narrative fields missing")
    returned_number = " ".join(html.unescape(number_match.group(1)).split())
    returned_date = " ".join(html.unescape(date_match.group(1)).split())
    if returned_number != incident_number or returned_date != incident_date:
        raise RFDReportError("RFD narrative response did not match the requested incident")
    narrative = _safe_text(re.sub(
        r'"?\s*}\]\s*$',
        "",
        html.unescape(narrative_match.group(1)).strip().lstrip('"').strip(),
    ))
    if not narrative:
        raise RFDReportError("RFD narrative was empty")
    return {
        "source": "rfd-html",
        "source_fragility": "fragile-html-over-http",
        "incident_number": returned_number,
        "incident_date": returned_date,
        "narrative": narrative,
        "source_url": BASE_URL + NARRATIVE_PATH + "?" + urllib.parse.urlencode({
            "incidentnumber": incident_number,
            "incidentdate": incident_date,
        }),
    }
