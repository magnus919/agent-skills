"""Read-only eSCRIBE public-meetings adapter."""

from __future__ import annotations

import html
import json
import re
import urllib.parse
from collections.abc import Iterator
from datetime import date, datetime
from pathlib import Path
from typing import Any

from raleighlib import core


BASE_URL = "https://pub-raleighnc.escribemeetings.com"
MEETING_VIEW = f"{BASE_URL}/?MeetingViewId=2"
PAST_MEETINGS_URL = f"{BASE_URL}/MeetingsCalendarView.aspx/PastMeetings"
MAX_PAST_PAGES_PER_TYPE = 50
MAX_PAST_MEETING_TYPES = 25
MAX_PAST_REQUESTS = 100


class CompatibilityError(Exception):
    """Raised when the eSCRIBE page structure has changed and cannot be parsed."""


def _absolute_url(path: str) -> str:
    if path.startswith("http://") or path.startswith("https://"):
        return path
    return urllib.parse.urljoin(BASE_URL, path)


def _fetch_html(url: str) -> str:
    if not core.is_allowed_host(url):
        raise core.SecurityError(f"URL host is not allowlisted: {url}")
    data = core.raw_request(url)
    return data.decode("utf-8", errors="replace")


def _extract_meeting_rows(html_text: str) -> list[dict[str, Any]]:
    """Extract meeting rows from listing HTML.

    eSCRIBE lists meetings with links like:
      Meeting.aspx?Id=<UUID>&lang=English
    The surrounding aria-label contains the meeting title and date.
    """
    rows: dict[str, dict[str, Any]] = {}
    for match in re.finditer(
        r"Meeting\.aspx\?Id=([0-9a-fA-F-]+)&lang=English",
        html_text,
    ):
        meeting_id = match.group(1).lower()
        if meeting_id in rows:
            continue
        # Read the label from this link's opening tag, not an earlier nearby
        # link. Historical pages contain many adjacent meeting anchors.
        start = html_text.rfind("<a", max(0, match.start() - 1000), match.start())
        end = html_text.find(">", match.end())
        opening_tag = html_text[start : end + 1] if start >= 0 and end >= 0 else ""
        label_match = re.search(r'aria-label="([^"]+)"', opening_tag)
        label = html.unescape(label_match.group(1)) if label_match else ""

        # Labels are like "Share <Title> <Weekday>, <Month> <Day>, <Year> @ <Time>"
        # or "Public Comment for <Title> <Weekday>, ...".
        title = label
        date_text = ""
        date_match = re.search(
            r"(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday),\s+[^@]+@\s+\d{1,2}:\d{2}\s+(?:AM|PM)",
            label,
        )
        if date_match:
            date_text = date_match.group(0)
            title = label[: date_match.start()].strip()
            # Strip common prefixes.
            for prefix in ("Share ", "Public Comment for "):
                if title.startswith(prefix):
                    title = title[len(prefix) :].strip()

        body = ""
        body_match = re.search(
            r"(City Council|Board of Commissioners|Planning Commission|City Council Meeting|Boards and Commissions)",
            title,
            re.IGNORECASE,
        )
        if body_match:
            body = body_match.group(1)

        rows[meeting_id] = {
            "id": meeting_id,
            "title": title,
            "date": date_text,
            "body": body,
            "url": f"{BASE_URL}/Meeting.aspx?Id={meeting_id}&lang=English",
        }
    if "Meeting.aspx" in html_text and not any(
        r.get("title") or r.get("date") for r in rows.values()
    ):
        raise CompatibilityError(
            "eSCRIBE meeting page contains Meeting.aspx links but no semantic meetings could be parsed"
        )
    return list(rows.values())


def _date_from_row(row: dict[str, Any]) -> date | None:
    value = row.get("date", "")
    try:
        return datetime.strptime(value, "%A, %B %d, %Y @ %I:%M %p").date()
    except (TypeError, ValueError):
        return None


def _meeting_types(html_text: str) -> list[str]:
    """Extract unique public meeting-type names from the listing page."""
    found: list[str] = []
    for encoded in re.findall(r'MeetingType="([^"]+)"', html_text):
        meeting_type = html.unescape(encoded).strip()
        if meeting_type and meeting_type not in found:
            found.append(meeting_type)
    return found


def _normalize_past_meeting(item: dict[str, Any]) -> dict[str, Any]:
    meeting_id = str(item.get("Id") or "")
    return {
        "id": meeting_id,
        "title": item.get("MeetingType") or "",
        "date": item.get("FormattedStart") or "",
        "body": item.get("MeetingType") or "",
        "location": item.get("LocationName") or "",
        "cancelled": bool(item.get("Cancelled")),
        "url": f"{BASE_URL}/Meeting.aspx?Id={meeting_id}&lang=English",
    }


def _past_meeting_items(
    year: int,
    body: str | None = None,
) -> Iterator[dict[str, Any]]:
    """Yield raw historical meeting records from the public page method."""
    listing = _fetch_html(MEETING_VIEW)
    meeting_types = _meeting_types(listing)
    if not meeting_types:
        raise CompatibilityError("eSCRIBE listing exposed no historical meeting types")
    if len(meeting_types) != len(set(meeting_types)):
        raise CompatibilityError("eSCRIBE returned duplicate meeting types")
    if len(meeting_types) > MAX_PAST_MEETING_TYPES:
        raise CompatibilityError(f"eSCRIBE returned more than {MAX_PAST_MEETING_TYPES} meeting types")
    if body:
        needle = body.casefold()
        meeting_types = [item for item in meeting_types if needle in item.casefold()]
    requests_remaining = MAX_PAST_REQUESTS
    seen_meeting_ids: set[str] = set()
    url = f"{PAST_MEETINGS_URL}?MeetingViewId=2&Year={year}"
    for meeting_type in meeting_types:
        page_number = 1
        loaded_for_type = 0
        expected_total: int | None = None
        while page_number <= MAX_PAST_PAGES_PER_TYPE:
            if requests_remaining <= 0:
                raise CompatibilityError("eSCRIBE historical request budget exhausted")
            requests_remaining -= 1
            response = core.json_request(
                url,
                method="POST",
                data=json.dumps({"type": meeting_type, "pageNumber": page_number}).encode("utf-8"),
                headers={"Content-Type": "application/json; charset=utf-8"},
            )
            response = core.require_object(response, "eSCRIBE historical meetings")
            result = response.get("d", response)
            page = result.get("Meetings", []) if isinstance(result, dict) else []
            if not isinstance(result, dict) or "TotalCount" not in result:
                raise CompatibilityError("eSCRIBE historical response omitted TotalCount")
            total_value = result["TotalCount"]
            if isinstance(total_value, bool) or not isinstance(total_value, int) or total_value < 0:
                raise CompatibilityError("eSCRIBE historical response has invalid TotalCount")
            total = total_value
            if expected_total is None:
                expected_total = total
            elif total != expected_total:
                raise CompatibilityError("eSCRIBE historical TotalCount changed during pagination")
            if not isinstance(page, list):
                raise CompatibilityError("eSCRIBE historical response has invalid Meetings")
            if not page:
                if loaded_for_type < total:
                    raise CompatibilityError("eSCRIBE historical pagination ended before TotalCount")
                break
            if loaded_for_type + len(page) > total:
                raise CompatibilityError("eSCRIBE historical Meetings exceed TotalCount")
            for item in page:
                if not isinstance(item, dict):
                    raise CompatibilityError("eSCRIBE historical response contains a non-object meeting")
                meeting_id = str(item.get("Id") or "").strip().casefold()
                if not meeting_id:
                    raise CompatibilityError("eSCRIBE historical meeting omitted Id")
                if meeting_id in seen_meeting_ids:
                    raise CompatibilityError("eSCRIBE historical response repeated a meeting Id")
                seen_meeting_ids.add(meeting_id)
                yield item
            loaded_for_type += len(page)
            if loaded_for_type >= total:
                break
            page_number += 1
        else:
            raise CompatibilityError(
                f"eSCRIBE pagination exceeded {MAX_PAST_PAGES_PER_TYPE} pages for {meeting_type}"
            )


def _fetch_past_meetings(
    year: int,
    body: str | None = None,
    limit: int | None = None,
) -> list[dict[str, Any]]:
    """Fetch normalized historical meetings from eSCRIBE's public page method."""
    rows: list[dict[str, Any]] = []
    for item in _past_meeting_items(year, body=body):
        rows.append(_normalize_past_meeting(item))
        if limit is not None and len(rows) >= limit:
            break
    return rows


def _find_past_meeting_record(meeting_id: str, year: int) -> dict[str, Any] | None:
    for item in _past_meeting_items(year):
        if str(item.get("Id") or "").casefold() == meeting_id.casefold():
            return item
    return None


def list_upcoming(
    limit: int | None = None,
    today: date | None = None,
) -> list[dict[str, Any]]:
    """List upcoming meetings, optionally limited to the first N."""
    core.require_positive_limit(limit, allow_none=True)
    html_text = _fetch_html(MEETING_VIEW)
    rows = _extract_meeting_rows(html_text)
    if not rows:
        page_is_escribe = "eSCRIBE Published Meetings" in html_text
        explicit_empty = re.search(
            r"\b(no upcoming meetings|no meetings (?:found|available|scheduled))\b",
            html_text,
            re.IGNORECASE,
        )
        if not page_is_escribe:
            raise CompatibilityError(
                "eSCRIBE upcoming page identity was not recognized"
            )
        if not explicit_empty:
            raise CompatibilityError(
                "eSCRIBE upcoming page contained no meetings or recognized empty state"
            )
    cutoff = today or date.today()
    rows = [row for row in rows if (_date_from_row(row) or date.min) >= cutoff]
    if limit is not None:
        rows = rows[:limit]
    return rows


def list_meetings(body: str | None = None, year: int | None = None, limit: int | None = None) -> list[dict[str, Any]]:
    """List meetings, optionally filtered by body and year.

    When ``year`` is supplied, fetch the historical archive for that year
    instead of the upcoming-meetings view.
    """
    core.require_positive_limit(limit, allow_none=True)
    if year is not None:
        rows = _fetch_past_meetings(year, body=body, limit=limit)
    else:
        rows = list_upcoming(limit=limit)
    if body:
        body_lower = body.lower()
        rows = [r for r in rows if body_lower in r.get("body", "").lower() or body_lower in r.get("title", "").lower()]
    if limit is not None:
        rows = rows[:limit]
    return rows


def search_meetings(
    query: str,
    body: str | None = None,
    year: int | None = None,
    limit: int | None = None,
) -> list[dict[str, Any]]:
    """Search upcoming or historical meetings by keyword."""
    core.require_positive_limit(limit, allow_none=True)
    rows = list_meetings(body=body, year=year)
    query_lower = query.lower()
    rows = [
        row for row in rows
        if query_lower in " ".join(
            str(row.get(field, "")) for field in ("title", "body", "date")
        ).lower()
    ]
    if limit is not None:
        rows = rows[:limit]
    return rows


def meeting_detail(meeting_id: str) -> dict[str, Any]:
    """Fetch meeting details including documents and links."""
    url = f"{BASE_URL}/Meeting.aspx?Id={meeting_id}&lang=English"
    html_text = _fetch_html(url)

    def extract_text(pattern: str) -> str:
        match = re.search(pattern, html_text, re.DOTALL | re.IGNORECASE)
        if match:
            return re.sub(r"<[^>]+>", "", html.unescape(match.group(1))).strip()
        return ""

    title = extract_text(r'<[^>]+class="[^"]*AgendaMeetingName[^"]*"[^>]*>(.*?)</[^>]+>')
    title = title or extract_text(r'<h1[^>]*>(.*?)</h1>') or extract_text(r'<title[^>]*>(.*?)</title>')
    meeting_date = extract_text(r'<div[^>]*class="[^"]*(?:meeting-date|date)[^"]*"[^>]*>(.*?)</div>')
    location = extract_text(r'<div[^>]*class="[^"]*(?:meeting-location|location)[^"]*"[^>]*>(.*?)</div>')

    def link_by_label(label: str) -> str | None:
        match = re.search(
            rf"<a[^>]+href=\"([^\"]+)\"[^>]*>\s*{re.escape(label)}\s*</a>",
            html_text,
            re.DOTALL | re.IGNORECASE,
        )
        return _absolute_url(match.group(1)) if match else None

    agenda = link_by_label("Agenda")
    minutes = link_by_label("Minutes")
    agenda_package = link_by_label("Agenda Packet")

    # Video/stream links.
    video_match = re.search(
        r"<a[^>]+href=\"([^\"]+)\"[^>]*>\s*(?:Video|Watch|Stream|Live)\s*</a>",
        html_text,
        re.DOTALL | re.IGNORECASE,
    )
    video = _absolute_url(video_match.group(1)) if video_match else None

    # Attachments: links to files near the agenda section.
    attachments: list[dict[str, str]] = []
    for att_match in re.finditer(
        r"<a[^>]+href=\"([^\"]+\.(?:pdf|doc|docx|xlsx|pptx|zip))\"[^>]*>(.*?)</a>",
        html_text,
        re.DOTALL | re.IGNORECASE,
    ):
        href = _absolute_url(att_match.group(1))
        text = re.sub(r"<[^>]+>", "", html.unescape(att_match.group(2))).strip()
        attachments.append({"url": href, "title": text})

    # Historical meeting metadata and document links are exposed by the same
    # read-only page method used by the site's past-meetings accordion.
    year_match = re.search(
        r'datetime=["\'][^"\']*?(20\d{2})-\d{2}-\d{2}', html_text, re.IGNORECASE
    ) or re.search(r"\b(20\d{2})\b", meeting_date)
    if not year_match:
        raise CompatibilityError("eSCRIBE meeting detail exposed no semantic meeting year")
    record = _find_past_meeting_record(meeting_id, int(year_match.group(1)))
    if record:
        title = str(record.get("MeetingType") or title)
        meeting_date = str(record.get("FormattedStart") or meeting_date)
        location = str(record.get("LocationName") or location)
        links = record.get("MeetingLinks", [])
        if isinstance(links, list):
            for link in links:
                if not isinstance(link, dict) or not link.get("Url"):
                    continue
                href = _absolute_url(str(link["Url"]))
                label = str(link.get("Title") or link.get("AriaLabel") or "Document")
                link_type = str(link.get("Type") or "").casefold()
                link_format = str(link.get("Format") or "").casefold()
                if link_type == "agendacover" and not agenda:
                    agenda = href
                elif link_type == "agenda":
                    if not agenda_package or link_format == ".pdf":
                        agenda_package = href
                elif "minute" in link_type or "minute" in label.casefold():
                    if not minutes:
                        minutes = href
                if link.get("HasVideo") and not video:
                    video = href
                if not any(item["url"] == href for item in attachments):
                    attachments.append({"url": href, "title": label})
        video = str(record.get("VideoUrl") or video or "") or None

    return {
        "id": meeting_id,
        "title": title,
        "date": meeting_date,
        "location": location,
        "cancelled": bool(record.get("Cancelled")) if record else False,
        "url": url,
        "agenda": agenda,
        "minutes": minutes,
        "agenda_package": agenda_package,
        "video": video,
        "attachments": attachments,
    }


def download_document(url: str, dest: str, force: bool = False) -> str:
    """Download a meeting document to a local path."""
    if not core.is_allowed_host(url):
        raise core.SecurityError(f"URL host is not allowlisted: {url}")
    data = core.raw_request(url)
    core.safe_write(Path(dest), data, force=force)
    return str(dest)
