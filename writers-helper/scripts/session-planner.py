#!/usr/bin/env python3
"""Plan a timed writing session with blocks, breaks, and word targets.

Converts session minutes and a target word count into a concrete plan:
block/break schedule, per-block word targets, and a flow-sprint check
based on a words-per-hour estimate. Pure computation, non-interactive.

Examples:
    session-planner.py --minutes 60 --target-words 1000
    session-planner.py --minutes 90 --blocks 3 --break-minutes 10 --json
    session-planner.py --minutes 30 --words-per-hour 1800
"""

import argparse
import json
import math
import sys
from datetime import datetime, timedelta

# Low-water mark from fast-drafting practice: below this speed the inner
# critic is likely interfering, so the plan flags it rather than worrying.
FLOW_FLOOR_WPH = 1200
STANDARD_WPH = 1500
DEFAULT_BLOCK_MINUTES = 25
DEFAULT_BREAK_MINUTES = 5


def plan(minutes, blocks, break_minutes, target_words, words_per_hour, start_time):
    if blocks is None:
        blocks = max(1, math.ceil(minutes / (DEFAULT_BLOCK_MINUTES + DEFAULT_BREAK_MINUTES)))
    if blocks < 1:
        raise ValueError("blocks must be >= 1")
    if minutes < blocks:
        raise ValueError("minutes must be >= the number of blocks")

    writing_minutes = minutes - (blocks - 1) * break_minutes
    if writing_minutes <= 0:
        raise ValueError("break time exceeds session minutes; reduce blocks or breaks")

    minutes_per_block = writing_minutes / blocks
    wph = words_per_hour or STANDARD_WPH
    words_per_minute = wph / 60.0
    projected_words = int(writing_minutes * words_per_minute)
    per_block_words = [int(minutes_per_block * words_per_minute)] * blocks
    # Distribute the remainder of the projection across the first blocks.
    remainder = projected_words - sum(per_block_words)
    for index in range(remainder):
        per_block_words[index] += 1

    schedule = []
    cursor = start_time
    for index in range(blocks):
        block_end = cursor + timedelta(minutes=minutes_per_block)
        schedule.append(
            {
                "block": index + 1,
                "start": cursor.strftime("%H:%M"),
                "end": block_end.strftime("%H:%M"),
                "minutes": round(minutes_per_block, 1),
                "word_target": per_block_words[index],
            }
        )
        cursor = block_end
        if index < blocks - 1:
            cursor += timedelta(minutes=break_minutes)

    return {
        "session_minutes": minutes,
        "writing_minutes": round(writing_minutes, 1),
        "break_minutes_total": (blocks - 1) * break_minutes,
        "blocks": blocks,
        "minutes_per_block": round(minutes_per_block, 1),
        "assumed_words_per_hour": wph,
        "projected_words": projected_words,
        "per_block_word_targets": per_block_words,
        "target_words": target_words,
        "target_feasible": target_words is None or target_words <= projected_words,
        "flow_floor_check": (
            "ok" if wph >= FLOW_FLOOR_WPH else "below the ~1200 wph floor; re-relax before writing"
        ),
        "schedule": schedule,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description="Plan a timed writing session.")
    parser.add_argument("--minutes", type=int, required=True, help="Total session minutes.")
    parser.add_argument("--target-words", type=int, default=None, help="Desired word count.")
    parser.add_argument("--blocks", type=int, default=None, help="Number of writing blocks.")
    parser.add_argument(
        "--break-minutes", type=int, default=DEFAULT_BREAK_MINUTES, help="Minutes per break."
    )
    parser.add_argument("--words-per-hour", type=int, default=None, help="Assumed writing speed.")
    parser.add_argument("--start-time", default=None, help="Start time as HH:MM (default: now).")
    parser.add_argument("--json", action="store_true", help="Emit JSON.")
    parser.add_argument(
        "--dry-run", action="store_true", help="Compute the plan without side effects (no-op)."
    )
    args = parser.parse_args(argv)

    if args.minutes < 1:
        parser.error("--minutes must be >= 1")
    if args.break_minutes < 0:
        parser.error("--break-minutes must be >= 0")
    if args.words_per_hour and args.words_per_hour < 1:
        parser.error("--words-per-hour must be >= 1")

    if args.start_time:
        try:
            start = datetime.strptime(args.start_time, "%H:%M").replace(
                year=datetime.now().year,
                month=datetime.now().month,
                day=datetime.now().day,
            )
        except ValueError as error:
            parser.error(f"invalid --start-time: {error}")
    else:
        start = datetime.now()

    try:
        result = plan(
            args.minutes,
            args.blocks,
            args.break_minutes,
            args.target_words,
            args.words_per_hour,
            start,
        )
    except ValueError as error:
        print(f"error: {error}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(result, indent=2))
        return 0

    print(
        f"Session plan: {result['session_minutes']} minutes, "
        f"{result['writing_minutes']} writing, {result['break_minutes_total']} on breaks"
    )
    print(
        f"Blocks: {result['blocks']} x ~{result['minutes_per_block']} min "
        f"at {result['assumed_words_per_hour']} words/hour"
    )
    print(f"Projected words: {result['projected_words']}")
    if result["target_words"] is not None:
        status = (
            "feasible"
            if result["target_feasible"]
            else "over the projection; extend time or lower the target"
        )
        print(f"Target: {result['target_words']} words -> {status}")
    print(f"Flow check: {result['flow_floor_check']}")
    print("Schedule:")
    for item in result["schedule"]:
        print(
            f"  Block {item['block']}: {item['start']}-{item['end']} "
            f"(~{item['minutes']} min, ~{item['word_target']} words)"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
