#!/usr/bin/env python3
"""Journal writing sessions and report progress.

Appends one session record per call to a JSONL file (default
~/.writing-habits.jsonl) and reports day/week/month totals, averages,
streaks, and best days. Non-interactive; --dry-run previews an append.

Examples:
    habit-log.py --log 2026-08-08 850 45 7 "finished act two"
    habit-log.py --report week
    habit-log.py --report month --json
"""

import argparse
import json
import os
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

DEFAULT_FILE = os.path.join(Path.home(), ".writing-habits.jsonl")
FIELDS = ["date", "words", "minutes", "energy", "notes"]


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


def add_record(path, words, minutes, energy, notes, log_date):
    records = load_records(path)
    record = {
        "date": log_date,
        "words": words,
        "minutes": minutes,
        "energy": energy,
        "notes": notes,
    }
    records.append(record)
    save_records(path, records)
    return record


def parse_date(value):
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError as error:
        raise ValueError(f"invalid date {value!r}, expected YYYY-MM-DD") from error


def summarize(records, start_date, label):
    window = [r for r in records if r.get("date", "") >= start_date.isoformat()]
    words = sum(int(r.get("words", 0)) for r in window)
    minutes = sum(int(r.get("minutes", 0)) for r in window)
    sessions = len(window)
    days = {r.get("date", "") for r in window}

    # Streak of consecutive writing days ending today or yesterday.
    streak = 0
    cursor = date.today()
    if cursor.isoformat() not in days:
        cursor = cursor - timedelta(days=1)
    while cursor.isoformat() in days:
        streak += 1
        cursor = cursor - timedelta(days=1)

    energy_values = [int(r["energy"]) for r in window if r.get("energy") is not None]
    best = None
    if window:
        best = max(window, key=lambda r: int(r.get("words", 0)))
        best = {"date": best.get("date", ""), "words": int(best.get("words", 0))}

    return {
        "period": label,
        "sessions": sessions,
        "writing_days": len(days),
        "words": words,
        "minutes": minutes,
        "avg_words_per_session": round(words / sessions, 0) if sessions else 0,
        "avg_minutes_per_session": round(minutes / sessions, 1) if sessions else 0,
        "avg_energy": round(sum(energy_values) / len(energy_values), 1) if energy_values else None,
        "current_streak_days": streak,
        "best_day": best,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description="Journal writing sessions and report progress.")
    parser.add_argument("--file", default=DEFAULT_FILE, help="Path to the JSONL log.")
    parser.add_argument(
        "--log",
        nargs="+",
        metavar="VALUE",
        help="Append a session: DATE WORDS MINUTES ENERGY [NOTES...]",
    )
    parser.add_argument("--report", choices=["day", "week", "month"], help="Report period.")
    parser.add_argument("--json", action="store_true", help="Emit JSON.")
    parser.add_argument("--dry-run", action="store_true", help="Preview an append without writing.")
    args = parser.parse_args(argv)

    path = Path(args.file).expanduser()

    if args.log:
        if len(args.log) < 4:
            parser.error("--log needs DATE WORDS MINUTES ENERGY [NOTES...]")
        try:
            log_date = parse_date(args.log[0]).isoformat()
        except ValueError as error:
            parser.error(str(error))
        try:
            words = int(args.log[1])
            minutes = int(args.log[2])
            energy = int(args.log[3])
        except ValueError:
            parser.error("WORDS, MINUTES, and ENERGY must be integers")
        if words < 0 or minutes < 0:
            parser.error("WORDS and MINUTES must be >= 0")
        if not 1 <= energy <= 10:
            parser.error("ENERGY must be 1-10")
        notes = " ".join(args.log[4:])
        if args.dry_run:
            print(
                f"would append to {path}: {log_date}, {words} words, "
                f"{minutes} min, energy {energy}, notes {notes!r}"
            )
            return 0
        try:
            record = add_record(path, words, minutes, energy, notes, log_date)
        except OSError as error:
            print(f"error: cannot write {path}: {error}", file=sys.stderr)
            return 1
        if args.json:
            print(json.dumps(record, indent=2))
        else:
            print(f"logged {log_date}: {words} words in {minutes} min, energy {energy}")
        return 0

    if args.report:
        try:
            records = load_records(path)
        except OSError as error:
            print(f"error: cannot read {path}: {error}", file=sys.stderr)
            return 1
        today = date.today()
        if args.report == "day":
            result = summarize(records, today, "day")
        elif args.report == "week":
            result = summarize(records, today - timedelta(days=6), "week")
        else:
            result = summarize(records, today - timedelta(days=29), "month")
        if args.json:
            print(json.dumps(result, indent=2))
            return 0
        print(
            f"{result['period'].title()} report: {result['sessions']} sessions over "
            f"{result['writing_days']} days, {result['words']} words, {result['minutes']} minutes"
        )
        print(
            f"Avg {int(result['avg_words_per_session'])} words/session, "
            f"{result['avg_minutes_per_session']} min/session, energy {result['avg_energy']}"
        )
        print(
            f"Streak: {result['current_streak_days']} days  Best day: "
            f"{result['best_day']['date']} ({result['best_day']['words']} words)"
        )
        return 0

    parser.error("either --log or --report is required")
    return 1


if __name__ == "__main__":
    sys.exit(main())
