# Worked investigation: synthetic support CLI delay

This reproducible, non-production exercise models a support CLI that checks whether reported item IDs exist in a local corpus. The scenario is synthetic: it does not claim that a real user reported this delay. There is no field telemetry in the fixture or deployment, so the reported boundary cannot be audited against real users. The example makes that evidence gap explicit and measures only a local proxy.

## Boundary, hypothesis, and rollback

The CLI's user-visible boundary is **process invocation** (operator runs the command) to **usable output** (the process exits, the operator can read `correctness=pass` and the result digest, and the measurement harness validates them). The end-to-end clock includes interpreter/process startup, workload construction, the lookup, stdout capture, and output validation. The primary measure is wall-clock seconds for that boundary. This fixture emits no event, trace, or field metric; field telemetry is absent.

The baseline scans a corpus of 6,000 strings for each of 1,200 queries, one fifth absent. The profile hypothesis is that repeated string comparisons dominate CPU time. The candidate builds a set once per invocation. The change is reversible by selecting `scan` instead of `indexed`; both modes remain available in the fixture. Correctness requires exact equality of the result booleans and matching result digest. Set memory use is a countermetric to inspect in a real system, but this small fixture does not measure it.

## Run the CLI and compare its end-to-end boundary

From the repository root, the comparison command alternates the order of nine baseline/candidate pairs. It starts a fresh process for every sample and validates stdout before stopping the timer:

```sh
python3 performance-optimization/examples/membership_workload.py measure --runs 9
```

Observed in two local nine-pair runs on Darwin arm64 (Python 3.14.7). The harness validates each process output against a fixed fixture digest before stopping its timer:

```text
run 1 scan_seconds=0.139774,0.136325,0.135088,0.135800,0.139046,0.138737,0.135809,0.136704,0.134552
run 1 indexed_seconds=0.041950,0.041900,0.041650,0.040586,0.044297,0.046487,0.042216,0.041635,0.041400
run 1 medians: scan=0.136325s indexed=0.041900s
run 2 scan_seconds=0.146184,0.136078,0.140537,0.141676,0.143390,0.139389,0.139005,0.140875,0.144856
run 2 indexed_seconds=0.044456,0.042375,0.043244,0.042853,0.048913,0.043563,0.044145,0.043178,0.045527
run 2 medians: scan=0.140875s indexed=0.043563s
correctness=pass sha256-prefix=1f723a23379b4b20
```

The median difference was 94.425 ms (69.26% lower) in the first run and 97.312 ms (69.08% lower) in the second. Every indexed sample was faster than every scan sample in these local runs. The result supports a local end-to-end improvement for this fixed synthetic CLI. It does not establish a gain on other hosts or a real support workflow. Process startup remains part of the indexed boundary; the larger function-only change below does not transfer directly to the full CLI.

To inspect the lookup's own repeated timings without process startup:

```sh
python3 performance-optimization/examples/membership_workload.py scan --repeat 7
python3 performance-optimization/examples/membership_workload.py indexed --repeat 7
```

These function timings help isolate the mechanism; they are not the user-visible boundary.

## Profile the bottleneck

Profile the lookup function directly, excluding the CLI startup and comparison harness. These commands use Python's standard library:

```sh
python3 -c 'import cProfile,runpy; m=runpy.run_path("performance-optimization/examples/membership_workload.py"); cProfile.runctx("m[\"scan\"](*m[\"workload\"]())", {"m":m}, {}, sort="cumtime")'
python3 -c 'import cProfile,runpy; m=runpy.run_path("performance-optimization/examples/membership_workload.py"); cProfile.runctx("m[\"indexed\"](*m[\"workload\"]())", {"m":m}, {}, sort="cumtime")'
```

The baseline profile reported 4,226,165 calls in 0.329 seconds; `scan` used 0.328 seconds cumulative, including 4,226,160 generator comparisons (0.151 seconds self time). The candidate profile reported five calls in 0.001 seconds, below useful display precision for the lookup. The profile locates the repeated scan mechanism; it is not used for the wall-clock comparison because profiling overhead overwhelms candidate runtime.

## Decision and evidence boundary

The correctness check passes for the fixed synthetic input. The profile supports the mechanism hypothesis, and repeated local end-to-end samples support the synthetic CLI improvement despite one outlier. No production deployment or user field data exists here; **field verification is pending**. A real investigation must first find or add the missing invocation-to-usable-output field measure, then compare matched builds and workloads, include memory and error/correctness countermetrics, and use the normal review and rollout path.
