#!/usr/bin/env python3
"""Read-only declaration audit; never a runtime acceptance or dispatch tool."""

import argparse
import json
import math
import sys
from collections import deque
from datetime import datetime
from pathlib import Path
from typing import Any, NoReturn

MAX_BYTES = 1_000_000
ACTIVE = {"claimed", "working", "blocked", "delivered"}
STATUSES = ACTIVE | {"queued", "accepted", "canceled", "denied", "failed"}


class InputError(ValueError):
    """Invalid snapshot rather than a coordination finding."""


def record(value: Any, keys: set[str], where: str) -> None:
    if not isinstance(value, dict) or set(value) != set(keys):
        raise InputError(f"{where}: expected exactly {', '.join(sorted(keys))}")


def label(value: Any, where: str) -> str:
    if not isinstance(value, str) or not value.strip() or len(value) > 256:
        raise InputError(f"{where}: expected nonempty string of at most 256 characters")
    return value


def sequence(value: Any, where: str) -> list[Any]:
    if not isinstance(value, list) or len(value) > 5000:
        raise InputError(f"{where}: expected array with at most 5000 entries")
    return value


def timestamp(value: Any, where: str) -> datetime:
    try:
        dt = datetime.fromisoformat(label(value, where).replace("Z", "+00:00"))
    except ValueError as exc:
        raise InputError(f"{where}: expected ISO-8601 timestamp") from exc
    if dt.tzinfo is None or dt.utcoffset() is None:
        raise InputError(f"{where}: timezone is required")
    return dt


def unique(rows: Any, keys: set[str], where: str) -> dict[str, dict[str, Any]]:
    result = {}
    for i, row in enumerate(sequence(rows, where)):
        record(row, keys, f"{where}[{i}]")
        key = label(row["id"], f"{where}[{i}].id")
        if key in result:
            raise InputError(f"{where}: duplicate id {key}")
        result[key] = row
    return result


def ref(value: Any, index: dict[str, Any], where: str) -> None:
    if label(value, where) not in index:
        raise InputError(f"{where}: unknown reference {value}")


def validate(data: Any) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    record(
        data,
        {
            "schema_version",
            "run_id",
            "as_of",
            "intent_version",
            "seats",
            "tasks",
            "knowledge",
            "edges",
        },
        "snapshot",
    )
    if type(data["schema_version"]) is not int or data["schema_version"] != 1:
        raise InputError("schema_version: expected integer 1")
    label(data["run_id"], "run_id")
    label(data["intent_version"], "intent_version")
    timestamp(data["as_of"], "as_of")
    seats = unique(data["seats"], {"id", "execution"}, "seats")
    for row in seats.values():
        label(row["execution"], "seat.execution")
    tasks = unique(
        data["tasks"],
        {"id", "owner", "status", "intent_version", "depends_on", "claims", "continuation"},
        "tasks",
    )
    if len(tasks) > 1000:
        raise InputError("tasks: maximum 1000")
    total_dependencies = 0
    for row in tasks.values():
        ref(row["owner"], seats, "task.owner")
        if row["status"] not in STATUSES:
            raise InputError("task.status: unsupported state")
        label(row["intent_version"], "task.intent_version")
        deps = sequence(row["depends_on"], "task.depends_on")
        for dep in deps:
            ref(dep, tasks, "task.depends_on")
        if len(set(deps)) != len(deps):
            raise InputError("task.depends_on: duplicate reference")
        total_dependencies += len(deps)
        for claim in sequence(row["claims"], "task.claims"):
            record(claim, {"seat", "execution", "epoch", "expires_at"}, "claim")
            ref(claim["seat"], seats, "claim.seat")
            label(claim["execution"], "claim.execution")
            if type(claim["epoch"]) is not int or claim["epoch"] < 0:
                raise InputError("claim.epoch: expected nonnegative integer")
            timestamp(claim["expires_at"], "claim.expires_at")
        if row["continuation"] is not None:
            record(row["continuation"], {"blocker", "wake", "owner"}, "continuation")
            for field in ("blocker", "wake"):
                label(row["continuation"][field], "continuation." + field)
            ref(row["continuation"]["owner"], seats, "continuation.owner")
    if total_dependencies > 5000:
        raise InputError("depends_on: maximum 5000 total edges")
    nodes = unique(data["knowledge"], {"id", "kind", "status"}, "knowledge")
    for row in nodes.values():
        if row["kind"] not in {"source", "artifact", "consumer"}:
            raise InputError("knowledge.kind: expected source, artifact or consumer")
        if row["status"] not in {"current", "suspect", "invalidated", "unknown"}:
            raise InputError("knowledge.status: unsupported status")
    pairs = set()
    for edge in sequence(data["edges"], "edges"):
        record(edge, {"source", "target"}, "edge")
        for field in ("source", "target"):
            ref(edge[field], nodes, "edge." + field)
        pair = (edge["source"], edge["target"])
        if pair in pairs:
            raise InputError("edges: duplicate edge")
        pairs.add(pair)
    return seats, tasks, nodes


def cycle_affected(tasks: dict[str, Any]) -> list[str]:
    """Kahn remainder includes cycle members AND downstream blocked tasks."""
    degree = {key: len(row["depends_on"]) for key, row in tasks.items()}
    children: dict[str, list[str]] = {key: [] for key in tasks}
    for key, row in tasks.items():
        for dep in row["depends_on"]:
            children[dep].append(key)
    ready = deque(key for key, count in degree.items() if not count)
    while ready:
        for child in children[ready.popleft()]:
            degree[child] -= 1
            if not degree[child]:
                ready.append(child)
    return sorted(key for key, count in degree.items() if count)


def audit(data: Any) -> dict[str, Any]:
    seats, tasks, _ = validate(data)
    findings: list[dict[str, Any]] = []

    def add(code: str, task: str) -> None:
        findings.append({"code": code, "task": task})

    affected = cycle_affected(tasks)
    if affected:
        findings.append({"code": "dependency_cycle_or_downstream", "tasks": affected})
    now = timestamp(data["as_of"], "as_of")
    for key, row in sorted(tasks.items()):
        if row["status"] not in ACTIVE:
            continue
        if row["intent_version"] != data["intent_version"]:
            add("stale_intent", key)
        claims = row["claims"]
        if not claims:
            add("missing_claim", key)
        if len(claims) > 1:
            add("multiple_claims", key)
        for claim in claims:
            if claim["seat"] != row["owner"]:
                add("claim_owner_mismatch", key)
            if claim["execution"] != seats[claim["seat"]]["execution"]:
                add("obsolete_occupant", key)
            if timestamp(claim["expires_at"], "expires_at") <= now:
                add("expired_claim", key)
        if row["status"] == "blocked" and row["continuation"] is None:
            add("missing_continuation", key)
        for dep in row["depends_on"]:
            if row["status"] != "blocked" and tasks[dep]["status"] != "accepted":
                add("unaccepted_prerequisite", key)
    return {
        "schema_version": 1,
        "run_id": data["run_id"],
        "basis": "supplied_declarations",
        "runtime_acceptance": "not_assessed",
        "findings": findings,
    }


def exposure(data: Any, source: str) -> dict[str, Any]:
    _, _, nodes = validate(data)
    ref(source, nodes, "source")
    children: dict[str, list[str]] = {key: [] for key in nodes}
    for edge in data["edges"]:
        children[edge["source"]].append(edge["target"])
    seen, pending = {source}, deque([source])
    while pending:
        for child in children[pending.popleft()]:
            if child not in seen:
                seen.add(child)
                pending.append(child)
    reached = sorted(seen - {source})
    return {
        "schema_version": 1,
        "source": source,
        "reachable": reached,
        "consumers": [key for key in reached if nodes[key]["kind"] == "consumer"],
        "basis": "supplied_edges",
        "coverage": "unknown",
        "runtime_acceptance": "not_assessed",
    }


def no_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    obj = {}
    for key, value in pairs:
        if key in obj:
            raise InputError(f"duplicate JSON key: {key}")
        obj[key] = value
    return obj


def reject_constant(value: str) -> NoReturn:
    raise InputError(f"nonfinite JSON constant: {value}")


def finite_float(value: str) -> float:
    number = float(value)
    if not math.isfinite(number):
        raise InputError("nonfinite JSON number")
    return number


def load(path: str) -> Any:
    with Path(path).open("rb") as stream:
        payload = stream.read(MAX_BYTES + 1)
    if len(payload) > MAX_BYTES:
        raise InputError("input exceeds 1000000 bytes")
    return json.loads(
        payload.decode("utf-8"),
        object_pairs_hook=no_duplicate_keys,
        parse_constant=reject_constant,
        parse_float=finite_float,
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=__doc__,
        epilog="Exit 0: completed/no findings; 1: audit findings; 2: invalid input. No writes or network calls.",
    )
    parser.add_argument("command", choices=["audit", "exposure"])
    parser.add_argument("--file", required=True, help="UTF-8 JSON snapshot, at most 1 MB")
    parser.add_argument("--source", help="Knowledge node ID; required for exposure")
    parser.add_argument("--json", action="store_true", help="Emit one JSON result")
    parser.add_argument("--dry-run", action="store_true", help="No-op: every command is read-only")
    args = parser.parse_args(argv)
    try:
        if (args.command == "exposure") != (args.source is not None):
            raise InputError("--source is required only for exposure")
        data = load(args.file)
        result = audit(data) if args.command == "audit" else exposure(data, args.source)
        code = int(bool(result.get("findings")))
    except (OSError, UnicodeError, ValueError, TypeError, RecursionError) as exc:
        result, code = {"error": str(exc), "runtime_acceptance": "not_assessed"}, 2
    if args.json:
        print(json.dumps(result, sort_keys=True, allow_nan=False))
    else:
        print(json.dumps(result, indent=2, sort_keys=True, allow_nan=False))
    return code


if __name__ == "__main__":
    sys.exit(main())
