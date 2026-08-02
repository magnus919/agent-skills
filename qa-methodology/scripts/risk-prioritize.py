#!/usr/bin/env python3
"""Risk prioritization CLI for qa-methodology.

Reads a JSON array of risk items, computes score = probability x impact,
ranks descending (deterministic tie-break by id), and outputs a
human-readable table by default or machine-parseable JSON with --json.

Input format (JSON array):
  [{"id": "auth-bypass", "probability": 4, "impact": 5}, ...]

Each item requires:
  - id: non-empty string
  - probability: integer 1-5
  - impact: integer 1-5

Exit codes:
  0  success
  1  malformed input (bad JSON, missing/invalid fields, wrong types)
  2  usage error (argparse)
"""

import argparse
import json
import sys


def parse_args(argv=None):
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        prog="risk-prioritize.py",
        description=(
            "Compute risk priority scores (probability x impact) and rank "
            "risk items for test allocation."
        ),
        epilog="Exit codes: 0 success, 1 malformed input, 2 usage error.",
    )
    parser.add_argument(
        "input",
        nargs="?",
        default="-",
        metavar="INPUT_JSON",
        help=(
            "Path to a JSON file containing an array of risk items "
            "(default: stdin). Each item: {\"id\": str, \"probability\": 1-5, "
            "\"impact\": 1-5}."
        ),
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="json_output",
        help="Output results as machine-parseable JSON instead of a table.",
    )
    return parser.parse_args(argv)


def validate_item(item, index):
    """Validate a single risk item. Returns (item, error_message)."""
    if not isinstance(item, dict):
        return None, "item {} is not an object".format(index)
    item_id = item.get("id")
    if item_id is None:
        return None, "item {} missing required field 'id'".format(index)
    if not isinstance(item_id, str) or not item_id.strip():
        return None, "item {} field 'id' must be a non-empty string".format(index)
    prob = item.get("probability")
    if prob is None:
        return None, "item '{}' missing required field 'probability'".format(item_id)
    impact = item.get("impact")
    if impact is None:
        return None, "item '{}' missing required field 'impact'".format(item_id)
    # Accept int only (not bool, not float)
    if isinstance(prob, bool) or not isinstance(prob, int):
        return None, "item '{}' field 'probability' must be an integer".format(item_id)
    if isinstance(impact, bool) or not isinstance(impact, int):
        return None, "item '{}' field 'impact' must be an integer".format(item_id)
    if not (1 <= prob <= 5):
        return None, "item '{}' field 'probability' must be 1-5".format(item_id)
    if not (1 <= impact <= 5):
        return None, "item '{}' field 'impact' must be 1-5".format(item_id)
    return item, None


def load_and_validate(source_text):
    """Parse JSON text and validate the risk items array.

    Returns (items, None) on success or (None, error_message) on failure.
    """
    try:
        data = json.loads(source_text)
    except (json.JSONDecodeError, ValueError) as exc:
        return None, "invalid JSON: {}".format(exc)

    if not isinstance(data, list):
        return None, "input must be a JSON array of risk items"
    if len(data) == 0:
        return None, "input array must contain at least one risk item"

    items = []
    for i, raw in enumerate(data):
        item, err = validate_item(raw, i)
        if err:
            return None, err
        items.append(item)
    return items, None


def compute_rankings(items):
    """Compute score and rank items descending by score, then by id ascending.

    Returns a new list of dicts with 'score' and 'rank' added.
    Does not mutate the input.
    """
    scored = []
    for item in items:
        scored.append({
            "id": item["id"],
            "probability": item["probability"],
            "impact": item["impact"],
            "score": item["probability"] * item["impact"],
        })
    # Sort descending by score, then ascending by id for deterministic tie-break
    scored.sort(key=lambda x: (-x["score"], x["id"]))
    for rank, entry in enumerate(scored, start=1):
        entry["rank"] = rank
    return scored


def format_table(rankings):
    """Format rankings as a human-readable table."""
    lines = []
    header = "{:<4} {:<30} {:>5} {:>5} {:>5}".format(
        "Rank", "ID", "Prob", "Imp", "Score"
    )
    lines.append(header)
    lines.append("-" * len(header))
    for entry in rankings:
        lines.append(
            "{:<4} {:<30} {:>5} {:>5} {:>5}".format(
                entry["rank"],
                entry["id"],
                entry["probability"],
                entry["impact"],
                entry["score"],
            )
        )
    return "\n".join(lines)


def main(argv=None):
    """Entry point."""
    args = parse_args(argv)

    # Read input
    try:
        if args.input == "-":
            source_text = sys.stdin.read()
        else:
            with open(args.input, "r", encoding="utf-8") as fh:
                source_text = fh.read()
    except OSError as exc:
        print("error: cannot read input: {}".format(exc), file=sys.stderr)
        return 1

    if not source_text.strip():
        print("error: input is empty", file=sys.stderr)
        return 1

    items, err = load_and_validate(source_text)
    if err:
        print("error: {}".format(err), file=sys.stderr)
        return 1

    rankings = compute_rankings(items)

    if args.json_output:
        print(json.dumps(rankings, indent=2))
    else:
        print(format_table(rankings))

    return 0


if __name__ == "__main__":
    sys.exit(main())
