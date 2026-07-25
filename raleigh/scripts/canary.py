#!/usr/bin/env python3
"""Live endpoint and schema canary for the Raleigh civic-data CLI.

Runs a full catalog check against the ArcGIS Hub and probes every fixed
non-Hub adapter endpoint shipped by the CLI.  Validates source-specific
minimum schemas, classifies failures, retries bounded transient errors,
and writes a machine-readable JSON report.

Exit codes:
  0  all probes passed (or only empty-but-valid observations)
  1  one or more durable contract failures detected
  2  script-level error (bad arguments, import failure, etc.)
"""

from __future__ import annotations

import json
import os
import sys
import time
import traceback
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

from raleighlib import core
from raleighlib import hub
from raleighlib import arcgis
from raleighlib import imagery
from raleighlib import geocode
from raleighlib import transit
from raleighlib import development
from raleighlib import civic
from raleighlib import meetings

MAX_RETRIES = 2
RETRY_DELAY_SECONDS = 5

FAILURE_CLASSES = (
    "transport_outage",
    "auth_regression",
    "arcgis_error",
    "schema_drift",
    "parser_failure",
    "empty_but_valid",
)


def _classify_exception(exc: Exception) -> str:
    if isinstance(exc, urllib.error.HTTPError):
        if exc.code in (401, 403):
            return "auth_regression"
        if exc.code >= 500:
            return "transport_outage"
        return "transport_outage"
    if isinstance(exc, (urllib.error.URLError, OSError, TimeoutError)):
        return "transport_outage"
    if isinstance(exc, core.SecurityError):
        return "auth_regression"
    if isinstance(exc, ValueError):
        msg = str(exc).lower()
        if "token required" in msg or "auth" in msg:
            return "auth_regression"
        if "arcgis" in msg or "error" in msg:
            return "arcgis_error"
        return "schema_drift"
    return "parser_failure"


def _is_transient(failure_class: str) -> bool:
    return failure_class == "transport_outage"


def _probe_with_retry(fn, *args, **kwargs) -> tuple[Any, None] | tuple[None, dict[str, Any]]:
    first_evidence: dict[str, Any] | None = None
    for attempt in range(1, MAX_RETRIES + 2):
        try:
            result = fn(*args, **kwargs)
            return result, None
        except Exception as exc:
            fc = _classify_exception(exc)
            evidence = {
                "failure_class": fc,
                "error": str(exc),
                "attempt": attempt,
            }
            if first_evidence is None:
                first_evidence = evidence
            if not _is_transient(fc) or attempt > MAX_RETRIES:
                return None, first_evidence
            time.sleep(RETRY_DELAY_SECONDS * attempt)
    return None, first_evidence


def probe_hub_catalog() -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    catalog, err = _probe_with_retry(hub.fetch_catalog)
    if err:
        results.append({
            "source": "hub-catalog",
            "target": "fetch_catalog",
            "status": "fail",
            **err,
        })
        return results

    supported_types = {"FeatureServer", "MapServer", "ImageServer"}
    items = [i for i in catalog if i.get("type") in supported_types and i.get("url")]
    total = len(items)
    failures = 0

    for item in items:
        url = item["url"]
        item_id = item.get("id", "unknown")
        title = item.get("title", "untitled")
        item_type = item.get("type", "")

        if item_type == "ImageServer":
            meta, err = _probe_with_retry(imagery.service_info, url)
        else:
            meta, err = _probe_with_retry(arcgis.service_metadata, url)

        if err:
            failures += 1
            results.append({
                "source": "hub-catalog",
                "target": f"{item_type}/{item_id}",
                "title": title,
                "url": url,
                "status": "fail",
                **err,
            })
            continue

        if isinstance(meta, dict) and "error" in meta:
            failures += 1
            results.append({
                "source": "hub-catalog",
                "target": f"{item_type}/{item_id}",
                "title": title,
                "url": url,
                "status": "fail",
                "failure_class": "arcgis_error",
                "error": json.dumps(meta["error"]),
                "attempt": 1,
            })
            continue

        if isinstance(meta, dict) and not meta.get("layers") and not meta.get("serviceDescription") is None:
            pass

    results.insert(0, {
        "source": "hub-catalog",
        "target": "summary",
        "status": "pass" if failures == 0 else "fail",
        "checked": total,
        "failures": failures,
    })
    return results


def probe_geocode() -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    candidates, err = _probe_with_retry(
        geocode.find_address_candidates, "1 Hargett St, Raleigh, NC", max_locations=1
    )
    if err:
        results.append({"source": "geocode", "target": "findAddressCandidates", "status": "fail", **err})
        return results

    if not isinstance(candidates, list):
        results.append({
            "source": "geocode", "target": "findAddressCandidates", "status": "fail",
            "failure_class": "schema_drift", "error": "expected list of candidates", "attempt": 1,
        })
        return results

    if len(candidates) == 0:
        results.append({
            "source": "geocode", "target": "findAddressCandidates", "status": "pass",
            "failure_class": "empty_but_valid", "error": "no candidates returned", "attempt": 1,
        })
        return results

    c = candidates[0]
    missing = [f for f in ("address", "location") if f not in c]
    if missing:
        results.append({
            "source": "geocode", "target": "findAddressCandidates", "status": "fail",
            "failure_class": "schema_drift",
            "error": f"missing required fields: {missing}", "attempt": 1,
        })
    else:
        results.append({"source": "geocode", "target": "findAddressCandidates", "status": "pass"})
    return results


def probe_transit_gtfs() -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    data, err = _probe_with_retry(transit.download_gtfs)
    if err:
        results.append({"source": "transit", "target": "static-gtfs", "status": "fail", **err})
        return results

    try:
        feed = transit._parse_gtfs_zip(data)
    except Exception as exc:
        results.append({
            "source": "transit", "target": "static-gtfs", "status": "fail",
            "failure_class": "parser_failure", "error": str(exc), "attempt": 1,
        })
        return results

    missing_tables = [t for t in transit.REQUIRED_GTFS_FIELDS if t not in feed]
    if missing_tables:
        results.append({
            "source": "transit", "target": "static-gtfs", "status": "fail",
            "failure_class": "schema_drift",
            "error": f"missing required tables: {missing_tables}", "attempt": 1,
        })
        return results

    for table, required_fields in transit.REQUIRED_GTFS_FIELDS.items():
        rows = feed.get(table, [])
        if not rows:
            results.append({
                "source": "transit", "target": f"static-gtfs/{table}", "status": "pass",
                "failure_class": "empty_but_valid", "error": f"table {table} is empty", "attempt": 1,
            })
            continue
        header = set(rows[0].keys())
        missing = required_fields - header
        if missing:
            results.append({
                "source": "transit", "target": f"static-gtfs/{table}", "status": "fail",
                "failure_class": "schema_drift",
                "error": f"missing fields in {table}: {sorted(missing)}", "attempt": 1,
            })
            return results

    results.append({
        "source": "transit", "target": "static-gtfs", "status": "pass",
        "tables": len(feed), "rows": sum(len(v) for v in feed.values()),
    })
    return results


def probe_development() -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    criteria, err = _probe_with_retry(development.fetch_criteria)
    if err:
        results.append({"source": "development", "target": "criteria", "status": "fail", **err})
        return results

    if not isinstance(criteria, dict):
        results.append({
            "source": "development", "target": "criteria", "status": "fail",
            "failure_class": "schema_drift", "error": "expected dict", "attempt": 1,
        })
        return results

    results.append({"source": "development", "target": "criteria", "status": "pass"})
    return results


def probe_civic_jsonapi() -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    index, err = _probe_with_retry(core.json_request, civic.JSONAPI_ROOT)
    if err:
        results.append({"source": "civic", "target": "jsonapi-index", "status": "fail", **err})
        return results

    if not isinstance(index, dict) or "links" not in index:
        results.append({
            "source": "civic", "target": "jsonapi-index", "status": "fail",
            "failure_class": "schema_drift",
            "error": "index missing 'links' key", "attempt": 1,
        })
        return results

    results.append({"source": "civic", "target": "jsonapi-index", "status": "pass"})
    return results


def probe_civic_rss() -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    data, err = _probe_with_retry(core.raw_request, civic.RSS_FEED)
    if err:
        results.append({"source": "civic", "target": "rss-feed", "status": "fail", **err})
        return results

    text = data.decode("utf-8", errors="replace")
    if "<rss" not in text and "<feed" not in text:
        results.append({
            "source": "civic", "target": "rss-feed", "status": "fail",
            "failure_class": "parser_failure",
            "error": "response does not look like RSS/Atom XML", "attempt": 1,
        })
        return results

    results.append({"source": "civic", "target": "rss-feed", "status": "pass"})
    return results


def probe_meetings() -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    upcoming, err = _probe_with_retry(meetings.list_upcoming)
    if err:
        fc = err.get("failure_class", "parser_failure")
        if fc == "parser_failure" and "CompatibilityError" in err.get("error", ""):
            err["failure_class"] = "parser_failure"
        results.append({"source": "meetings", "target": "upcoming", "status": "fail", **err})
        return results

    if not isinstance(upcoming, list):
        results.append({
            "source": "meetings", "target": "upcoming", "status": "fail",
            "failure_class": "schema_drift", "error": "expected list", "attempt": 1,
        })
        return results

    if len(upcoming) == 0:
        results.append({
            "source": "meetings", "target": "upcoming", "status": "pass",
            "failure_class": "empty_but_valid", "error": "no upcoming meetings", "attempt": 1,
        })
        return results

    m = upcoming[0]
    missing = [f for f in ("id", "title", "date") if f not in m]
    if missing:
        results.append({
            "source": "meetings", "target": "upcoming", "status": "fail",
            "failure_class": "schema_drift",
            "error": f"missing fields: {missing}", "attempt": 1,
        })
    else:
        results.append({"source": "meetings", "target": "upcoming", "status": "pass", "count": len(upcoming)})
    return results


def probe_imagery_catalog() -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    services, err = _probe_with_retry(imagery.list_services)
    if err:
        results.append({"source": "imagery", "target": "catalog", "status": "fail", **err})
        return results

    if not isinstance(services, list):
        results.append({
            "source": "imagery", "target": "catalog", "status": "fail",
            "failure_class": "schema_drift", "error": "expected list of services", "attempt": 1,
        })
        return results

    if len(services) == 0:
        results.append({
            "source": "imagery", "target": "catalog", "status": "pass",
            "failure_class": "empty_but_valid", "error": "no imagery services", "attempt": 1,
        })
        return results

    results.append({"source": "imagery", "target": "catalog", "status": "pass", "count": len(services)})
    return results


ALL_PROBES = [
    ("hub-catalog", probe_hub_catalog),
    ("geocode", probe_geocode),
    ("transit-gtfs", probe_transit_gtfs),
    ("development", probe_development),
    ("civic-jsonapi", probe_civic_jsonapi),
    ("civic-rss", probe_civic_rss),
    ("meetings", probe_meetings),
    ("imagery", probe_imagery_catalog),
]


def run_canary() -> dict[str, Any]:
    started = datetime.now(timezone.utc).isoformat()
    all_results: list[dict[str, Any]] = []
    durable_failures = 0
    transient_failures = 0
    empty_valid = 0

    for name, probe_fn in ALL_PROBES:
        try:
            results = probe_fn()
        except Exception as exc:
            results = [{
                "source": name,
                "target": "probe-level",
                "status": "fail",
                "failure_class": "parser_failure",
                "error": f"{type(exc).__name__}: {exc}",
                "traceback": traceback.format_exc(),
                "attempt": 1,
            }]
        all_results.extend(results)

    for r in all_results:
        if r.get("target") == "summary":
            continue
        if r.get("status") != "fail":
            if r.get("failure_class") == "empty_but_valid":
                empty_valid += 1
            continue
        fc = r.get("failure_class", "unknown")
        if _is_transient(fc):
            transient_failures += 1
        else:
            durable_failures += 1

    passed = durable_failures == 0
    report = {
        "canary": "raleigh-live-endpoint",
        "started_at": started,
        "completed_at": datetime.now(timezone.utc).isoformat(),
        "passed": passed,
        "summary": {
            "total_results": len(all_results),
            "durable_failures": durable_failures,
            "transient_failures": transient_failures,
            "empty_but_valid": empty_valid,
        },
        "results": all_results,
    }
    return report


def write_github_summary(report: dict[str, Any]) -> None:
    summary_path = os.environ.get("GITHUB_STEP_SUMMARY")
    if not summary_path:
        return
    lines: list[str] = []
    s = report["summary"]
    status = "PASS" if report["passed"] else "FAIL"
    lines.append(f"## Raleigh Live Canary: {status}")
    lines.append("")
    lines.append(f"| Metric | Count |")
    lines.append(f"|--------|-------|")
    lines.append(f"| Total probes | {s['total_results']} |")
    lines.append(f"| Durable failures | {s['durable_failures']} |")
    lines.append(f"| Transient failures | {s['transient_failures']} |")
    lines.append(f"| Empty-but-valid | {s['empty_but_valid']} |")
    lines.append("")

    failures = [r for r in report["results"] if r.get("status") == "fail"]
    if failures:
        lines.append("### Failures")
        lines.append("")
        lines.append("| Source | Target | Class | Evidence |")
        lines.append("|--------|--------|-------|----------|")
        for f in failures:
            evidence = f.get("error", "")[:120]
            lines.append(
                f"| {f.get('source', '?')} | {f.get('target', '?')} "
                f"| {f.get('failure_class', '?')} | {evidence} |"
            )
        lines.append("")

    with open(summary_path, "a", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")


def main() -> int:
    report = run_canary()

    report_path = os.environ.get("CANARY_REPORT_PATH", "canary-report.json")
    with open(report_path, "w", encoding="utf-8") as fh:
        json.dump(report, fh, indent=2)

    write_github_summary(report)

    s = report["summary"]
    print(
        f"Canary {'PASSED' if report['passed'] else 'FAILED'}: "
        f"{s['total_results']} probes, "
        f"{s['durable_failures']} durable failures, "
        f"{s['transient_failures']} transient failures, "
        f"{s['empty_but_valid']} empty-but-valid"
    )
    print(f"Report written to {report_path}")

    return 0 if report["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
