#!/usr/bin/env python3
"""Read-only finish-to-start schedule analysis; not resource leveling."""

import argparse
import heapq
import json
import math
import sys
from pathlib import Path

MAX_BYTES = 1_000_000
MAX_TASKS = 500
MAX_DURATION = 1_000_000
MAX_CONFLICTS = 100


def number(value, label):
    if type(value) not in (int, float) or not 0 <= value <= MAX_DURATION:
        raise ValueError(f"{label} must be a finite number from 0 to {MAX_DURATION}")
    return value


def identifier(value, label):
    if (
        not isinstance(value, str)
        or not value.strip()
        or len(value) > 100
        or any(ord(c) < 32 or ord(c) == 127 for c in value)
    ):
        raise ValueError(
            f"{label} must be nonblank text of at most 100 characters without controls"
        )
    return value


def fields(value, required, optional, label):
    if not isinstance(value, dict):
        raise ValueError(f"{label} must be an object")
    if not required <= value.keys() or value.keys() - required - optional:
        raise ValueError(
            f"{label}: required fields {sorted(required)}; optional {sorted(optional)}"
        )


def validate(data):
    fields(data, {"schema_version", "unit", "tasks"}, {"deadline"}, "schedule")
    if type(data["schema_version"]) is not int or data["schema_version"] != 1:
        raise ValueError("schema_version must be integer 1")
    if data["unit"] != "working_days":
        raise ValueError("unit must be working_days (elapsed duration, not person-days)")
    if "deadline" in data:
        number(data["deadline"], "deadline")
    tasks = data["tasks"]
    if not isinstance(tasks, list) or not 1 <= len(tasks) <= MAX_TASKS:
        raise ValueError(f"tasks must contain 1 to {MAX_TASKS} tasks")
    by_id = {}
    for task in tasks:
        fields(task, {"id", "duration", "depends_on"}, {"resource"}, "task")
        key = identifier(task["id"], "task id")
        if key in by_id:
            raise ValueError(f"duplicate task id: {key}")
        number(task["duration"], f"duration for {key}")
        deps = task["depends_on"]
        if not isinstance(deps, list):
            raise ValueError(f"depends_on for {key} must be a list")
        for dep in deps:
            identifier(dep, "dependency id")
        if len(deps) != len(set(deps)):
            raise ValueError(f"duplicate dependency for {key}")
        if "resource" in task:
            identifier(task["resource"], "resource")
        by_id[key] = task
    if sum(t["duration"] for t in tasks) > MAX_DURATION:
        raise ValueError(f"aggregate duration exceeds {MAX_DURATION} working days")
    for key, task in by_id.items():
        for dep in task["depends_on"]:
            if dep not in by_id:
                raise ValueError(f"unknown dependency {dep} for {key}")
            if dep == key:
                raise ValueError(f"self dependency for {key}")
    return by_id


def analyze(data):
    tasks = validate(data)
    successors = {key: [] for key in tasks}
    indegree = {key: len(t["depends_on"]) for key, t in tasks.items()}
    for key, task in tasks.items():
        for dep in task["depends_on"]:
            successors[dep].append(key)
    ready = [key for key in tasks if indegree[key] == 0]
    heapq.heapify(ready)
    order = []
    timing = {}
    while ready:
        key = heapq.heappop(ready)
        start = max((timing[d]["early_finish"] for d in tasks[key]["depends_on"]), default=0)
        timing[key] = {"early_start": start, "early_finish": start + tasks[key]["duration"]}
        order.append(key)
        for child in successors[key]:
            indegree[child] -= 1
            if indegree[child] == 0:
                heapq.heappush(ready, child)
    if len(order) != len(tasks):
        raise ValueError("dependency cycle: remove circular dependencies before scheduling")
    finish = max(t["early_finish"] for t in timing.values())
    for key in reversed(order):
        late_finish = min((timing[c]["late_start"] for c in successors[key]), default=finish)
        late_start = late_finish - tasks[key]["duration"]
        slack = late_start - timing[key]["early_start"]
        # Decimal working-day inputs may accumulate binary floating-point noise.
        if math.isclose(slack, 0, abs_tol=1e-9):
            slack = 0
        timing[key].update(late_start=late_start, late_finish=late_finish, total_float=slack)
    conflicts = []
    conflict_count = 0
    resource_tasks = {}
    for key in sorted(tasks):
        resource = tasks[key].get("resource")
        if resource and tasks[key]["duration"] > 0:
            for other in resource_tasks.get(resource, []):
                start = max(timing[key]["early_start"], timing[other]["early_start"])
                end = min(timing[key]["early_finish"], timing[other]["early_finish"])
                if start < end:
                    conflict_count += 1
                    if len(conflicts) < MAX_CONFLICTS:
                        conflicts.append(
                            {
                                "resource": resource,
                                "tasks": [other, key],
                                "overlap_start": start,
                                "overlap_finish": end,
                            }
                        )
            resource_tasks.setdefault(resource, []).append(key)
    return {
        "schema_version": 1,
        "unit": "working_days",
        "model": "unconstrained_finish_to_start",
        "finish": finish,
        "deadline_gap": finish - data["deadline"] if "deadline" in data else None,
        "critical_tasks": sorted(key for key in tasks if timing[key]["total_float"] == 0),
        "tasks": [{"id": key, **timing[key]} for key in sorted(tasks)],
        "resource_conflicts": conflicts,
        "resource_conflict_count": conflict_count,
        "resource_conflicts_truncated": conflict_count > MAX_CONFLICTS,
        "warnings": [
            "Earliest times are not resource-leveled or commitments; validate capacity, calendars and uncertainty."
        ],
    }


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON field: {key}")
        result[key] = value
    return result


def reject_constant(value):
    raise ValueError(f"non-finite JSON number: {value}")


def read_input(path):
    with Path(path).open("rb") as handle:
        raw = handle.read(MAX_BYTES + 1)
    if len(raw) > MAX_BYTES:
        raise ValueError(f"input exceeds {MAX_BYTES} bytes")
    return json.loads(
        raw.decode("utf-8"), object_pairs_hook=unique_object, parse_constant=reject_constant
    )


def main(argv=None):
    parser = argparse.ArgumentParser(
        description=__doc__,
        epilog="Exit 0: calculation complete (even if late). Exit 2: invalid input. No files are changed.",
    )
    parser.add_argument(
        "--input", required=True, help="JSON schedule file; see templates/schedule-example.json"
    )
    parser.add_argument("--json", action="store_true", help="Structured output (also the default)")
    args = parser.parse_args(argv)
    try:
        result = analyze(read_input(args.input))
    except (ValueError, OSError, RecursionError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2, allow_nan=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
