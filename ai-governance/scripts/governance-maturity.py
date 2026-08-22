#!/usr/bin/env python3
"""Governance-maturity self-assessment scorer for the ai-governance skill.

Reads a JSON answers file describing an organization's current state across the
canonical governance dimensions (each scored 1-5), computes an overall maturity
level and a list of gaps (dimensions below the target), and reports the result.

Behavior contract:

* ``--json`` emits a single JSON object to stdout containing the keys
  ``maturity_level`` (string) and ``gaps`` (array).
* Exit code 0 on healthy input; exit code 1 when every dimension is at minimum
  (critical gaps); exit code 1 on missing, malformed, or semantically-invalid
  input (with an explanatory message on stderr).
* ``--dry-run`` is a true preview: the tool is read-only and never writes files,
  so a dry-run's ``--json`` output is byte-identical to the real run's.
* Output is deterministic: no timestamps, stable ordering, and sorted keys.

Standard library only. No third-party runtime dependencies.
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
from typing import Any

# The canonical governance dimensions scored by the self-assessment. Scores are
# 1 (ad hoc / absent) to 5 (systematically optimized).
DIMENSIONS: tuple[str, ...] = (
    "roles_and_decision_rights",
    "risk_register",
    "lifecycle_gates",
    "incident_response",
    "fairness_reviews",
    "transparency_reporting",
    "model_inventory",
    "third_party_due_diligence",
)

MIN_SCORE = 1
MAX_SCORE = 5
DEFAULT_TARGET = 3  # "Defined" is the minimum for a baseline governance posture

# Maturity level names, keyed to a lower-bound on the average score.
LEVEL_THRESHOLDS: tuple[tuple[float, str], ...] = (
    (4.5, "Optimized"),
    (3.5, "Managed"),
    (2.5, "Defined"),
    (1.5, "Developing"),
    (0.0, "Initial"),
)


def validate_answers(data: Any) -> dict[str, Any]:
    """Validate the parsed JSON payload and return its ``answers`` mapping.

    Raises ``ValueError`` with a human-readable message when the payload is not
    the expected shape: a top-level object with an ``answers`` object whose keys
    are exactly the canonical dimensions and whose values are integers 1-5.
    """
    if not isinstance(data, dict):
        raise ValueError("top-level JSON must be an object")
    answers = data.get("answers")
    if not isinstance(answers, dict):
        raise ValueError("'answers' must be an object of dimension scores")
    unknown = sorted(set(answers) - set(DIMENSIONS))
    if unknown:
        raise ValueError("unexpected dimension(s): " + ", ".join(unknown))
    missing = [d for d in DIMENSIONS if d not in answers]
    if missing:
        raise ValueError("missing required dimension(s): " + ", ".join(missing))
    for dimension in DIMENSIONS:
        value = answers[dimension]
        if isinstance(value, bool) or not isinstance(value, int):
            raise ValueError(f"dimension '{dimension}' must be an integer score, got {value!r}")
        if not MIN_SCORE <= value <= MAX_SCORE:
            raise ValueError(
                f"dimension '{dimension}' score {value} out of range {MIN_SCORE}-{MAX_SCORE}"
            )
    return answers


def compute_maturity(answers: dict[str, int], target: int = DEFAULT_TARGET) -> dict[str, Any]:
    """Compute the maturity result for validated dimension scores.

    Returns a dict with ``maturity_level`` (string), ``average_score`` (float),
    ``min_score`` (int), ``critical`` (bool), ``target`` (int), and ``gaps``
    (a list of gap entries for dimensions scoring below ``target``, sorted by
    dimension name for deterministic output).
    """
    scores = [answers[d] for d in DIMENSIONS]
    average = statistics.fmean(scores)
    minimum = min(scores)
    level = next(name for bound, name in LEVEL_THRESHOLDS if average >= bound)
    # "Critical gaps" means every dimension is at its minimum (all scored 1),
    # indicating the organization has no governance controls in place at all.
    critical = max(scores) == MIN_SCORE
    gaps: list[dict[str, Any]] = [
        {
            "dimension": dimension,
            "score": answers[dimension],
            "target": target,
            "deficit": max(target - answers[dimension], 0),
        }
        for dimension in sorted(DIMENSIONS, key=str.lower)
        if answers[dimension] < target
    ]
    return {
        "maturity_level": level,
        "average_score": round(average, 3),
        "min_score": minimum,
        "critical": critical,
        "target": target,
        "gaps": gaps,
    }


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Score an organization's AI-governance maturity from a JSON "
            "answers file of dimension scores (1-5)."
        )
    )
    parser.add_argument(
        "answers_file",
        help="path to a JSON file with an 'answers' object of dimension scores",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="emit the result as a single JSON object on stdout",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="preview the result without writing anything (this tool is read-only)",
    )
    parser.add_argument(
        "--target",
        type=int,
        default=DEFAULT_TARGET,
        metavar="SCORE",
        help=(f"minimum dimension score considered non-gap (default: {DEFAULT_TARGET})"),
    )
    return parser.parse_args(argv)


def _fail(message: str) -> int:
    print(f"error: {message}", file=sys.stderr)
    return 1


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)

    if not MIN_SCORE <= args.target <= MAX_SCORE:
        return _fail(f"--target must be between {MIN_SCORE} and {MAX_SCORE}")

    try:
        with open(args.answers_file, encoding="utf-8") as handle:
            raw = handle.read()
    except OSError as exc:
        return _fail(f"cannot read answers file '{args.answers_file}': {exc}")

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        return _fail(f"invalid JSON in '{args.answers_file}': {exc}")

    try:
        answers = validate_answers(data)
    except ValueError as exc:
        return _fail(str(exc))

    result = compute_maturity(answers, target=args.target)

    if args.json:
        print(
            json.dumps(
                result,
                sort_keys=True,
                ensure_ascii=False,
                separators=(",", ":"),
            )
        )
    else:
        _render_human(result)

    return 1 if result["critical"] else 0


def _render_human(result: dict[str, Any]) -> None:
    header = (
        f"Governance maturity: {result['maturity_level']} "
        f"(avg {result['average_score']}, min {result['min_score']}, "
        f"target {result['target']})"
    )
    print(header)
    if result["gaps"]:
        print("Gaps:")
        for gap in result["gaps"]:
            print(f"  - {gap['dimension']}: score {gap['score']} (deficit {gap['deficit']})")
    else:
        print("No gaps: every dimension is at or above the target.")
    if result["critical"]:
        print("Critical: every dimension is at minimum; governance is not established.")


if __name__ == "__main__":
    raise SystemExit(main())
