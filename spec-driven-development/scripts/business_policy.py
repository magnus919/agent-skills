"""Read-only synthetic equipment-loan policy. Python 3.10+, no dependencies."""

import argparse
import json
from dataclasses import asdict, dataclass
from datetime import date
from typing import Literal


@dataclass(frozen=True)
class Policy:
    version: str
    start: date
    end: date | None
    max_days: int


@dataclass(frozen=True)
class Decision:
    status: Literal["eligible", "ineligible", "review"]
    reason: str
    rule_ids: tuple[str, ...]
    policy_version: str | None


POLICIES = (
    Policy("loan-v1", date(2026, 1, 1), date(2026, 7, 1), 7),
    Policy("loan-v2", date(2026, 7, 1), None, 5),
)


def evaluate(facts: dict, policies: tuple[Policy, ...] = POLICIES) -> Decision:
    """Validate facts, select policy, then evaluate approved precedence."""
    try:
        pickup = date.fromisoformat(facts["pickup_date"])
    except (KeyError, TypeError, ValueError):
        return Decision("review", "invalid_input", (), None)
    if (
        type(facts.get("days")) is not int
        or facts["days"] <= 0
        or type(facts.get("available")) is not bool
        or type(facts.get("exception")) is not bool
    ):
        return Decision("review", "invalid_input", (), None)
    matches = [p for p in policies if p.start <= pickup and (p.end is None or pickup < p.end)]
    if len(matches) != 1:
        return Decision("review", "policy_selection", (), None)
    policy = matches[0]
    if not facts["available"]:
        return Decision("ineligible", "unavailable", ("L1",), policy.version)
    if facts["exception"]:
        return Decision("review", "exception", ("L2",), policy.version)
    if facts["days"] > policy.max_days:
        return Decision("ineligible", "duration", ("L3",), policy.version)
    return Decision("eligible", "within_limit", ("L4",), policy.version)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, help="Path to a JSON facts object")
    args = parser.parse_args()
    try:
        with open(args.input, encoding="utf-8") as stream:
            facts = json.load(stream)
        if not isinstance(facts, dict):
            raise ValueError("input must be an object")
        print(json.dumps(asdict(evaluate(facts))))
    except (OSError, ValueError) as exc:
        parser.exit(2, f"Invalid input: {exc}\n")
