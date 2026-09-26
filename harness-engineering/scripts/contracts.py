#!/usr/bin/env python3
"""Validate declared harness contracts and compare compatible recorded task runs."""

import argparse
import json
import math
import re
import sys
from pathlib import Path

HEX = re.compile(r"^[a-f0-9]{64}$")
STATUSES = {"pending", "active", "blocked", "verified", "stale"}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def text(value):
    return isinstance(value, str) and bool(value.strip())


def positive(value):
    return (
        isinstance(value, (float, int))
        and not isinstance(value, bool)
        and math.isfinite(value)
        and value > 0
    )


def nonnegative(value):
    return (value == 0 and not isinstance(value, bool)) or positive(value)


def object_list(data, name):
    value = data.get(name)
    require(isinstance(value, list) and bool(value), f"{name} must be a nonempty list")
    require(all(isinstance(v, dict) for v in value), f"{name} entries must be objects")
    require(all(text(v.get("id")) for v in value), f"{name} entries require stable id")
    require(len({v["id"] for v in value}) == len(value), f"{name} IDs must be unique")
    return value


def acyclic(nodes, edges):
    active, visited = set(), set()

    def visit(node):
        require(node not in active, "task dependencies contain a cycle")
        if node in visited:
            return
        active.add(node)
        for child in edges[node]:
            visit(child)
        active.remove(node)
        visited.add(node)

    for node in nodes:
        visit(node)


def state(data):
    require(text(data.get("objective")), "objective required")
    tasks = object_list(data, "tasks")
    by_id = {t["id"]: t for t in tasks}
    edges = {}
    for task in tasks:
        require(task.get("status") in STATUSES, "invalid task status")
        require(text(task.get("behavior")), "task behavior required")
        deps = task.get("dependencies")
        require(
            isinstance(deps, list) and all(text(d) for d in deps), "dependencies must be string IDs"
        )
        require(len(set(deps)) == len(deps), "duplicate dependency")
        require(all(d in by_id and d != task["id"] for d in deps), "unknown/self dependency")
        edges[task["id"]] = deps
        checks = task.get("verification")
        evidence = task.get("evidence")
        require(
            isinstance(checks, list) and all(isinstance(c, dict) for c in checks),
            "verification must be objects",
        )
        require(
            all(text(c.get("id")) and text(c.get("claim")) for c in checks),
            "criterion needs id and claim",
        )
        require(len({c["id"] for c in checks}) == len(checks), "duplicate criterion ID")
        require(
            isinstance(evidence, list) and all(isinstance(e, dict) for e in evidence),
            "evidence must be objects",
        )
        require(
            all(
                text(e.get("criterion_id"))
                and text(e.get("revision"))
                and text(e.get("reference"))
                and e.get("outcome") in {"pass", "fail", "unknown"}
                for e in evidence
            ),
            "invalid evidence record",
        )
        require(
            all(e["criterion_id"] in {c["id"] for c in checks} for e in evidence),
            "evidence references unknown criterion",
        )
        pairs = [(e["criterion_id"], e["revision"]) for e in evidence]
        require(len(pairs) == len(set(pairs)), "conflicting/duplicate current criterion evidence")
        if task["status"] == "active":
            require(text(task.get("owner")), "active task needs owner")
        if task["status"] == "verified":
            require(checks, "verified task needs acceptance criteria")
            rev = task.get("revision")
            require(
                text(rev) and rev == data.get("candidate_revision"),
                "verified task must match candidate revision",
            )
            current = {e["criterion_id"]: e for e in evidence if e["revision"] == rev}
            require(
                all(c["id"] in current and current[c["id"]]["outcome"] == "pass" for c in checks),
                "verified task needs passing evidence for every criterion on candidate revision",
            )
            require(
                all(
                    by_id[d]["status"] == "verified" and by_id[d].get("revision") == rev
                    for d in deps
                ),
                "verified task has unverified/stale dependency",
            )
    acyclic(by_id, edges)
    limit = data.get("max_active_tasks", 1)
    require(
        isinstance(limit, int) and not isinstance(limit, bool) and limit > 0,
        "max_active_tasks must be positive integer",
    )
    require(
        sum(t["status"] == "active" for t in tasks) <= limit,
        "active task count exceeds declared WIP limit",
    )
    return {
        "tasks": len(tasks),
        "verified_claims": sum(t["status"] == "verified" for t in tasks),
        "limits": "Evidence references and revision declarations are validated, not independently executed or authenticated.",
    }


def graph(data):
    nodes = object_list(data, "nodes")
    by_id = {n["id"]: n for n in nodes}
    terminal = data.get("terminal_nodes")
    require(
        isinstance(terminal, list) and terminal and all(text(n) and n in by_id for n in terminal),
        "terminal_nodes must name real nodes",
    )
    require(len(terminal) == len(set(terminal)), "duplicate terminal node")
    require(text(data.get("start")) and data["start"] in by_id, "start must name a real node")
    limits = data.get("limits")
    require(isinstance(limits, dict), "limits required")
    for name in ["max_attempts", "max_elapsed_seconds", "max_no_progress_cycles"]:
        require(positive(limits.get(name)), f"positive {name} required")
    for name in ["max_attempts", "max_no_progress_cycles"]:
        require(isinstance(limits[name], int), f"{name} must be integer")
    require(
        text(data.get("checkpoint_store")) and data["checkpoint_store"] != "in_memory",
        "durable checkpoint store required",
    )
    adjacency = {n: set() for n in by_id}
    for node in nodes:
        require(text(node.get("owner")), "node owner required")
        require(
            node.get("kind") in {"maker", "verifier", "action", "terminal"}, "invalid node kind"
        )
        routes = node.get("routes")
        require(
            isinstance(routes, dict)
            and all(text(k) and text(v) and v in by_id for k, v in routes.items()),
            "routes must name real destinations",
        )
        require(
            (node["id"] in terminal) == (node["kind"] == "terminal"),
            "terminal kind and terminal list disagree",
        )
        require(node["id"] not in terminal or not routes, "terminal node must have no routes")
        require(node["id"] in terminal or routes, "nonterminal node needs routes")
        adjacency[node["id"]].update(routes.values())
        if node["kind"] == "verifier":
            require(
                {"pass", "fail", "unknown"} <= routes.keys(),
                "verifier needs pass/fail/unknown routes",
            )
            require(routes["unknown"] != routes["pass"], "unknown may not take the pass route")
            require(text(node.get("criteria_reference")), "verifier criteria reference required")
        if node.get("side_effects"):
            require(
                node.get("requires_authorization") is True, "side effect requires authorization"
            )
            require(text(node.get("reconciliation")), "side effect needs reconciliation policy")

    def reachable(start):
        seen, pending = set(), [start]
        while pending:
            node = pending.pop()
            if node in seen:
                continue
            seen.add(node)
            pending.extend(adjacency[node] - seen)
        return seen

    require(reachable(data["start"]) == set(by_id), "graph contains unreachable nodes")
    require(all(set(terminal) & reachable(n) for n in by_id), "node has no terminal path")
    return {
        "nodes": len(nodes),
        "limits": "Declared routes/limits checked; runtime enforcement, persistence and authority not exercised.",
    }


def run(data):
    require(text(data.get("harness_revision")), "harness_revision required")
    fingerprints = data.get("fingerprints")
    require(isinstance(fingerprints, dict), "fingerprints required")
    for key in ["model_config", "environment", "taskset", "authority", "verifier"]:
        require(
            isinstance(fingerprints.get(key), str) and HEX.fullmatch(fingerprints[key]),
            f"{key} requires SHA256 fingerprint",
        )
    cases = object_list(data, "cases")
    for case in cases:
        require(
            isinstance(case.get("input_sha256"), str) and HEX.fullmatch(case["input_sha256"]),
            "case input_sha256 required",
        )
        require(case.get("outcome") in {"accepted", "rejected", "unknown"}, "invalid outcome")
        for key in ["elapsed_seconds", "cost", "human_interventions"]:
            require(nonnegative(case.get(key)), f"case {key} must be finite nonnegative number")
        require(isinstance(case["human_interventions"], int), "human_interventions must be integer")
        require(
            text(case.get("evidence_reference")),
            "case evidence reference required even for failed/unknown runs",
        )
    return {
        "cases": len(cases),
        "limits": "Recorded observations not independently executed or authenticated.",
    }


def validate(kind, data):
    require(isinstance(data, dict), "contract must be an object")
    require(
        type(data.get("schema_version")) is int and data["schema_version"] == 1,
        "schema_version must be 1",
    )
    return {
        "schema_version": 1,
        "kind": kind,
        "contract_valid": True,
        "behavior": "not_assessed",
        "details": {"state": state, "graph": graph, "run": run}[kind](data),
    }


def compare(baseline, candidate):
    validate("run", baseline)
    validate("run", candidate)
    differing = sorted(
        key
        for key in set(baseline["fingerprints"]) | set(candidate["fingerprints"])
        if baseline["fingerprints"].get(key) != candidate["fingerprints"].get(key)
    )
    require(
        not differing,
        "incompatible run fingerprints (" + ", ".join(differing) + "); comparison refused",
    )
    base = {c["id"]: c for c in baseline["cases"]}
    new = {c["id"]: c for c in candidate["cases"]}
    require(base.keys() == new.keys(), "case IDs differ; comparison refused")
    require(
        all(base[k]["input_sha256"] == new[k]["input_sha256"] for k in base),
        "case inputs differ; comparison refused",
    )
    rows = []
    for key in sorted(base):
        a, b = base[key], new[key]
        rows.append(
            {
                "id": key,
                "baseline": a["outcome"],
                "candidate": b["outcome"],
                "acceptance_regression": a["outcome"] == "accepted" and b["outcome"] != "accepted",
                "elapsed_delta_seconds": b["elapsed_seconds"] - a["elapsed_seconds"],
                "cost_delta": b["cost"] - a["cost"],
                "intervention_delta": b["human_interventions"] - a["human_interventions"],
            }
        )
    return {
        "schema_version": 1,
        "kind": "paired_record_comparison",
        "paired_cases": len(rows),
        "baseline_harness": baseline["harness_revision"],
        "candidate_harness": candidate["harness_revision"],
        "observed_baseline_accepted": sum(c["outcome"] == "accepted" for c in base.values()),
        "observed_candidate_accepted": sum(c["outcome"] == "accepted" for c in new.values()),
        "rows": rows,
        "release_approval": "not_assessed",
        "limits": "Descriptive comparison of supplied records; no causality, significance, authenticity or field effectiveness claim.",
    }


def load(path):
    # Strict JSON: Python otherwise accepts NaN/Infinity.
    def reject_constant(value):
        raise ValueError(f"nonstandard JSON constant {value}")

    def unique_pairs(pairs):
        result = {}
        for key, value in pairs:
            require(key not in result, f"duplicate JSON key: {key}")
            result[key] = value
        return result

    return json.loads(
        path.read_text(), parse_constant=reject_constant, object_pairs_hook=unique_pairs
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="mode", required=True)
    v = sub.add_parser("validate")
    v.add_argument("--kind", choices=["state", "graph", "run"], required=True)
    v.add_argument("--file", type=Path, required=True)
    c = sub.add_parser("compare")
    c.add_argument("--baseline", type=Path, required=True)
    c.add_argument("--candidate", type=Path, required=True)
    args = parser.parse_args()
    try:
        result = (
            validate(args.kind, load(args.file))
            if args.mode == "validate"
            else compare(load(args.baseline), load(args.candidate))
        )
        print(json.dumps(result, indent=2))
        return 0
    except (OSError, ValueError, TypeError, KeyError, RecursionError) as error:
        print(json.dumps({"contract_valid": False, "error": str(error)}))
        return 2


if __name__ == "__main__":
    sys.exit(main())
