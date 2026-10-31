#!/usr/bin/env python3
"""Read-only declaration screening for a factory snapshot; never dispatches work."""

import argparse
import json
import math
import sys
from pathlib import Path


class InvalidSnapshot(ValueError):
    """The supplied declaration cannot be interpreted safely."""


def require(condition, message):
    if not condition:
        raise InvalidSnapshot(message)


def number(value):
    try:
        return type(value) in (int, float) and math.isfinite(value) and value >= 0
    except OverflowError:
        return False


def text(value):
    return isinstance(value, str) and bool(value.strip())


def validate(data):
    require(isinstance(data, dict), "snapshot must be an object")
    require(
        type(data.get("schema_version")) is int and data["schema_version"] == 1,
        "schema_version must be integer 1",
    )
    require(text(data.get("job_id")), "job_id must be nonempty")
    require(number(data.get("as_of")), "as_of must be a nonnegative finite timestamp")
    budget = data.get("budget")
    require(isinstance(budget, dict), "budget must be an object")
    for key in ("limit", "spent", "reserved"):
        require(number(budget.get(key)), f"budget.{key} must be nonnegative and finite")
    tasks = data.get("tasks")
    require(isinstance(tasks, list) and bool(tasks), "tasks must be a nonempty list")
    indexed = {}
    for task in tasks:
        require(isinstance(task, dict), "each task must be an object")
        for key in ("id", "required_revision", "worker_revision"):
            require(text(task.get(key)), f"task.{key} must be nonempty")
        task_id = task["id"]
        require(task_id not in indexed, f"duplicate task: {task_id}")
        require(
            task.get("status") in ("queued", "running", "complete", "cancelled"),
            f"{task_id}: unsupported status",
        )
        for key in ("ack_revision", "artifact_revision"):
            require(task.get(key) is None or text(task[key]), f"{task_id}: invalid {key}")
        require(number(task.get("lease_expires_at")), f"{task_id}: invalid lease expiry")
        versions = task.get("dependency_versions")
        require(isinstance(versions, dict), f"{task_id}: dependency_versions must be an object")
        require(
            all(text(k) and text(v) for k, v in versions.items()),
            f"{task_id}: dependency IDs/revisions must be nonempty",
        )
        indexed[task_id] = task
    for task_id, task in indexed.items():
        for dependency in task["dependency_versions"]:
            require(dependency in indexed, f"{task_id}: unknown dependency {dependency}")
    # Kahn traversal also rejects self-dependency without recursion depth assumptions.
    remaining = set(indexed)
    ordered = []
    while remaining:
        ready = sorted(
            t for t in remaining if not set(indexed[t]["dependency_versions"]) & remaining
        )
        require(bool(ready), "dependency cycle")
        ordered.extend(ready)
        remaining.difference_update(ready)
    changed = data.get("changed_tasks")
    require(
        isinstance(changed, list) and all(text(t) for t in changed),
        "changed_tasks must be a list of IDs",
    )
    require(len(set(changed)) == len(changed), "duplicate changed_tasks ID")
    require(set(changed) <= set(indexed), "changed_tasks contains an unknown ID")
    return indexed, ordered


def reconcile(data):
    indexed, ordered = validate(data)
    affected = set(data["changed_tasks"])
    reasons = {t: [] for t in indexed}
    for task_id in ordered:
        task = indexed[task_id]
        deps = task["dependency_versions"]
        if task_id in affected or any(d in affected for d in deps):
            affected.add(task_id)
            reasons[task_id].append("change_impact_requires_disposition")
        if task["worker_revision"] != task["required_revision"]:
            reasons[task_id].append("worker_revision_mismatch")
        if (
            task["status"] in ("running", "complete")
            and task.get("ack_revision") != task["required_revision"]
        ):
            reasons[task_id].append("current_revision_not_acknowledged")
        if task["status"] == "running" and task["lease_expires_at"] <= data["as_of"]:
            reasons[task_id].append("lease_expired_reconcile_effects_before_reassignment")
        if (
            task["status"] == "complete"
            and task.get("artifact_revision") != task["required_revision"]
        ):
            reasons[task_id].append("artifact_revision_mismatch")
        if task["status"] == "cancelled":
            reasons[task_id].append("cancelled_reconcile_pending_effects")
        for dependency, revision in deps.items():
            upstream = indexed[dependency]
            if revision != upstream["required_revision"]:
                reasons[task_id].append(f"dependency_revision_mismatch:{dependency}")
            if upstream["status"] != "complete" or reasons[dependency]:
                reasons[task_id].append(f"dependency_unresolved:{dependency}")
    budget = data["budget"]
    available = budget["limit"] - budget["spent"] - budget["reserved"]
    require(math.isfinite(available), "budget arithmetic must remain finite")
    return {
        "schema_version": 1,
        "job_id": data["job_id"],
        "scope": "supplied_declarations_only",
        "behavior": "not_assessed",
        "release_acceptance": "not_assessed",
        "affected_tasks": sorted(affected),
        "tasks_requiring_disposition": {t: reasons[t] for t in sorted(reasons) if reasons[t]},
        "completed_candidates_for_review": sorted(
            t for t in indexed if indexed[t]["status"] == "complete" and not reasons[t]
        ),
        "declared_available_budget": available,
        "new_dispatch_budget_available": available > 0,
        "budget_reconciliation_required": available < 0,
        "limitations": "No authority, lease, acknowledgement, artifact, cost or external effect is authenticated; no work is started or accepted.",
    }


def main():
    parser = argparse.ArgumentParser(
        description=__doc__,
        epilog="Exit 0: report produced (not acceptance); 2: invalid input. Writes JSON to stdout only.",
    )
    parser.add_argument(
        "--snapshot",
        required=True,
        type=Path,
        help="Version 1 JSON snapshot; see templates/factory-snapshot.json",
    )
    args = parser.parse_args()
    try:
        data = json.loads(args.snapshot.read_text())
        report = reconcile(data)
    except (OSError, ValueError, TypeError) as exc:
        print(json.dumps({"error": str(exc), "behavior": "not_assessed"}), file=sys.stderr)
        return 2
    print(json.dumps(report, indent=2, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
