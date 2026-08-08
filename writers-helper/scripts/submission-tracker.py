#!/usr/bin/env python3
"""Track submissions to agents and publishers.

Maintains a JSONL ledger (default ~/.writing-submissions.jsonl) of queries,
proposals, and manuscript submissions. Reports the pipeline by status and
flags follow-ups due. Non-interactive; --dry-run previews mutations.

Examples:
    submission-tracker.py --add "The Glass Orchard" "Agent Name" query 2026-08-08 sent
    submission-tracker.py --update 1 status partial-request
    submission-tracker.py --list
    submission-tracker.py --status --follow-up-days 21
"""

import argparse
import json
import os
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

DEFAULT_FILE = os.path.join(Path.home(), ".writing-submissions.jsonl")
VALID_STATUSES = {
    "sent",
    "no-response",
    "partial-request",
    "full-request",
    "rejection",
    "offer",
    "accepted",
    "withdrawn",
}
SORT_ORDER = {
    "offer": 0,
    "accepted": 0,
    "full-request": 1,
    "partial-request": 2,
    "sent": 3,
    "no-response": 3,
    "rejection": 4,
    "withdrawn": 5,
}


def load_records(path):
    records = []
    if not path.is_file():
        return records
    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError as error:
                print(
                    f"warning: skipping malformed line {line_number} in {path}: {error}",
                    file=sys.stderr,
                )
                continue
            records.append(record)
    return records


def save_records(path, records):
    with path.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, sort_keys=True) + "\n")


def add_record(path, title, target, submission_type, sent_date, status, notes):
    records = load_records(path)
    next_id = max((int(r["id"]) for r in records), default=0) + 1
    record = {
        "id": next_id,
        "title": title,
        "target": target,
        "type": submission_type,
        "sent_date": sent_date,
        "status": status,
        "notes": notes,
    }
    records.append(record)
    save_records(path, records)
    return record


def update_record(path, record_id, field, value):
    records = load_records(path)
    for record in records:
        if int(record["id"]) == record_id:
            record[field] = value
            save_records(path, records)
            return record
    return None


def parse_date(value):
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError as error:
        raise ValueError(f"invalid date {value!r}, expected YYYY-MM-DD") from error


def status_report(records, follow_up_days):
    counts = {}
    for record in records:
        status = record.get("status", "sent")
        counts[status] = counts.get(status, 0) + 1

    cutoff = date.today() - timedelta(days=follow_up_days)
    follow_ups = []
    for record in records:
        status = record.get("status", "sent")
        if status not in {"sent", "no-response"}:
            continue
        try:
            sent = parse_date(record.get("sent_date", ""))
        except ValueError:
            continue
        if sent <= cutoff:
            follow_ups.append(
                {
                    "id": record["id"],
                    "title": record.get("title", ""),
                    "target": record.get("target", ""),
                    "sent_date": record.get("sent_date", ""),
                    "days_outstanding": (date.today() - sent).days,
                }
            )

    total = len(records)
    active = sum(
        counts.get(s, 0) for s in ("sent", "no-response", "partial-request", "full-request")
    )
    return {
        "total": total,
        "active": active,
        "by_status": counts,
        "follow_ups_due": follow_ups,
        "follow_up_window_days": follow_up_days,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description="Track submissions to agents and publishers.")
    parser.add_argument("--file", default=DEFAULT_FILE, help="Path to the JSONL ledger.")
    parser.add_argument(
        "--add",
        nargs="+",
        metavar="VALUE",
        help="Add a submission: TITLE TARGET TYPE SENT-DATE STATUS [NOTES...]",
    )
    parser.add_argument(
        "--update",
        nargs=3,
        metavar=("ID", "FIELD", "VALUE"),
        help="Update a field on a submission.",
    )
    parser.add_argument("--list", action="store_true", help="List all submissions.")
    parser.add_argument("--status", action="store_true", help="Report the pipeline.")
    parser.add_argument("--follow-up-days", type=int, default=21, help="Follow-up window in days.")
    parser.add_argument("--json", action="store_true", help="Emit JSON.")
    parser.add_argument(
        "--dry-run", action="store_true", help="Preview a mutation without writing."
    )
    args = parser.parse_args(argv)

    path = Path(args.file).expanduser()

    if args.add:
        if len(args.add) < 4:
            parser.error("--add needs TITLE TARGET TYPE SENT-DATE STATUS [NOTES...]")
        title, target, submission_type = args.add[0], args.add[1], args.add[2]
        try:
            sent_date = parse_date(args.add[3]).isoformat()
        except ValueError as error:
            parser.error(str(error))
        status = args.add[4]
        if status not in VALID_STATUSES:
            parser.error(f"invalid status {status!r}; valid: {', '.join(sorted(VALID_STATUSES))}")
        notes = " ".join(args.add[5:])
        if args.dry_run:
            print(
                f"would add to {path}: {title!r} -> {target} ({submission_type}) "
                f"sent {sent_date}, status {status}"
            )
            return 0
        try:
            record = add_record(path, title, target, submission_type, sent_date, status, notes)
        except OSError as error:
            print(f"error: cannot write {path}: {error}", file=sys.stderr)
            return 1
        if args.json:
            print(json.dumps(record, indent=2))
        else:
            print(
                f"added #{record['id']}: {record['title']} -> {record['target']} ({record['status']})"
            )
        return 0

    if args.update:
        try:
            record_id = int(args.update[0])
        except ValueError:
            parser.error("ID must be an integer")
        field, value = args.update[1], args.update[2]
        if field == "status" and value not in VALID_STATUSES:
            parser.error(f"invalid status {value!r}; valid: {', '.join(sorted(VALID_STATUSES))}")
        if field == "sent_date":
            try:
                value = parse_date(value).isoformat()
            except ValueError as error:
                parser.error(str(error))
        if args.dry_run:
            print(f"would update #{record_id} in {path}: {field} = {value!r}")
            return 0
        try:
            record = update_record(path, record_id, field, value)
        except OSError as error:
            print(f"error: cannot write {path}: {error}", file=sys.stderr)
            return 1
        if record is None:
            print(f"error: no submission with id {record_id}", file=sys.stderr)
            return 1
        if args.json:
            print(json.dumps(record, indent=2))
        else:
            print(f"updated #{record['id']}: {field} = {value!r}")
        return 0

    try:
        records = load_records(path)
    except OSError as error:
        print(f"error: cannot read {path}: {error}", file=sys.stderr)
        return 1

    if args.list:
        records = sorted(records, key=lambda r: SORT_ORDER.get(r.get("status", "sent"), 5))
        if args.json:
            print(json.dumps(records, indent=2))
            return 0
        if not records:
            print("no submissions recorded")
            return 0
        for record in records:
            print(
                f"#{record['id']} [{record.get('status', 'sent')}] {record.get('title', '')} "
                f"-> {record.get('target', '')} ({record.get('type', '')}, sent {record.get('sent_date', '')})"
            )
        return 0

    if args.status:
        if args.follow_up_days < 1:
            parser.error("--follow-up-days must be >= 1")
        report = status_report(records, args.follow_up_days)
        if args.json:
            print(json.dumps(report, indent=2))
            return 0
        print(f"Pipeline: {report['total']} total, {report['active']} active")
        for status, count in sorted(report["by_status"].items()):
            print(f"  {status}: {count}")
        if report["follow_ups_due"]:
            print(f"Follow-ups due (>{args.follow_up_days} days):")
            for item in report["follow_ups_due"]:
                print(
                    f"  #{item['id']} {item['title']} -> {item['target']} "
                    f"({item['days_outstanding']} days)"
                )
        else:
            print("No follow-ups due")
        return 0

    parser.error("one of --add, --update, --list, or --status is required")
    return 1


if __name__ == "__main__":
    sys.exit(main())
