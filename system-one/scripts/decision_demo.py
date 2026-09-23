#!/usr/bin/env python3
"""Read-only ticket-routing demonstration with synthetic or opt-in live answers."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from systemone_probe import live_call, load_json, validate_request, validate_response


ROOT = Path(__file__).resolve().parents[1]


def policy(request: dict, response: dict) -> dict:
    """Example policy only; thresholds must be fit to the target workload."""
    validate_response(request, response)
    route = response["answers"]["queue"]
    refund = response["answers"]["refund_requested"]
    if route["choice"] == "other" or route["confidence"] < 0.70:
        return {"lane": "human_review", "reason": "uncertain_or_other_route"}
    if route["probabilities"][route["choice"]] < 0.75:
        return {"lane": "human_review", "reason": "insufficient_route_probability"}
    return {
        "lane": "route_only",
        "queue": route["choice"],
        "refund_flag": refund["noul"] >= 0.80,
        "reason": "example_policy_passed",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--request", type=Path, default=ROOT / "examples/request.json")
    parser.add_argument("--response", type=Path, default=ROOT / "examples/response.synthetic.json")
    parser.add_argument("--live", action="store_true", help="send request to Jev; may transmit data and incur cost")
    parser.add_argument("--url", default="https://api.typesafe.ai/v1/systemone")
    args = parser.parse_args(argv)
    request = validate_request(load_json(args.request))
    if args.live:
        key = os.environ.get("TYPESAFE_API_KEY")
        if not key:
            parser.error("--live requires TYPESAFE_API_KEY")
        _, response, _ = live_call(args.url, request, key, 10.0)
    else:
        response = load_json(args.response)
    print(json.dumps({"mode": "live" if args.live else "synthetic_fixture", **policy(request, response)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
