#!/usr/bin/env python3
"""Deterministic synthetic lookup workload for the optimization walkthrough."""

import argparse
import hashlib
import json
import os
import statistics
import subprocess
import sys
import time

EXPECTED_DIGEST = "1f723a23379b4b20"


def workload(size: int = 6_000, query_count: int = 1_200) -> tuple[list[str], list[str]]:
    """Build a repeatable corpus and a mix of present/absent query keys."""
    corpus = [f"item-{index:06d}" for index in range(size)]
    queries = [
        f"item-{(index * 37) % size:06d}" if index % 5 else f"missing-{index:06d}"
        for index in range(query_count)
    ]
    return corpus, queries


def scan(corpus: list[str], queries: list[str]) -> list[bool]:
    """Baseline: scan the full corpus for every query."""
    return [any(candidate == query for candidate in corpus) for query in queries]


def indexed(corpus: list[str], queries: list[str]) -> list[bool]:
    """Candidate: build an index once, then perform constant-time lookups."""
    index = set(corpus)
    return [query in index for query in queries]


def digest(results: list[bool]) -> str:
    return hashlib.sha256(bytes(results)).hexdigest()[:16]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("scan", "indexed", "measure"))
    parser.add_argument("--repeat", type=int, default=1)
    parser.add_argument("--runs", type=int, default=9)
    args = parser.parse_args()
    if args.repeat < 1:
        parser.error("--repeat must be at least 1")
    if args.runs < 1:
        parser.error("--runs must be at least 1")

    if args.mode == "measure":
        timings: dict[str, list[float]] = {"scan": [], "indexed": []}
        digests: dict[str, str] = {}
        # Alternate order to reduce bias from host drift during the comparison.
        for run in range(args.runs):
            modes = ("scan", "indexed") if run % 2 == 0 else ("indexed", "scan")
            for mode in modes:
                command = [sys.executable, os.path.abspath(__file__), mode]
                started = time.perf_counter()
                completed = subprocess.run(command, capture_output=True, text=True, check=True)
                fields = dict(line.split("=", 1) for line in completed.stdout.splitlines() if "=" in line)
                if fields.get("correctness") != "pass" or fields.get("sha256-prefix") != EXPECTED_DIGEST:
                    raise SystemExit(f"CLI did not return usable correct output: {completed.stdout!r}")
                elapsed = time.perf_counter() - started
                timings[mode].append(elapsed)
                digests[mode] = fields["sha256-prefix"]
        if digests["scan"] != digests["indexed"]:
            raise SystemExit(f"end-to-end outputs differ: {digests}")
        print(f"boundary=process invocation to validated usable stdout; pairs={args.runs}")
        print(f"correctness=pass sha256-prefix={digests['scan']}")
        for mode in ("scan", "indexed"):
            print(f"{mode}_seconds=" + ",".join(f"{value:.6f}" for value in timings[mode]))
            print(f"{mode}_median_seconds={statistics.median(timings[mode]):.6f}")
        return

    corpus, queries = workload()
    function = scan if args.mode == "scan" else indexed
    actual = function(corpus, queries)
    if digest(actual) != EXPECTED_DIGEST:
        raise SystemExit("correctness check failed: output differs from fixed fixture")

    durations = []
    for _ in range(args.repeat):
        started = time.perf_counter()
        result = function(corpus, queries)
        durations.append(time.perf_counter() - started)
        if digest(result) != EXPECTED_DIGEST:
            raise SystemExit("correctness check failed during timed run")

    median = statistics.median(durations)
    print(f"mode={args.mode} corpus={len(corpus)} queries={len(queries)} repeats={len(durations)}")
    print("correctness=pass")
    print(f"sha256-prefix={digest(actual)}")
    print("seconds=" + ",".join(f"{value:.6f}" for value in durations))
    print(f"median_seconds={median:.6f}")


if __name__ == "__main__":
    main()
