# Performance optimization skill: focused execution evidence

## Scope and method

This revision was based on a bounded screen of the merged skill, followed by one focused revision and a held-out executable task. The screen ran two evidence-reasoning fixtures in clean ephemeral Codex CLI sessions (`gpt-5.5`, CLI 0.145.0), with and without the frozen skill. The prompts matched within each pair; traces confirmed skill activation in the skill condition. Each condition met all applicable manual rubric checks. The fixture prompts supplied much of the desired method, and one run per condition cannot establish repeatability or uplift. The screen therefore found no repeatable reasoning failure.

The held-out task supplied a synthetic support CLI that was slow for accounts with many sessions. The same task prompt and fixture were given to three clean sessions: no skill, frozen merged skill, and the revised skill. Each session made a focused owner-index change and preserved the golden outputs, including missing-owner behavior. The comparison is about the agent's *evidence quality*, not about which implementation ran fastest: hosts and run conditions were not controlled across sessions.

| Condition | Full CLI before and after? | Diagnostic profile? | Output and edge checks? | Field claim boundary? |
|---|---|---|---|---|
| No skill | After only | Yes | Golden fixtures | No deployment; field plan limited |
| Frozen merged skill | Seven before samples, but after only in final evidence | Yes | Golden fixtures and duplicate/missing-owner checks | Field verification pending |
| Revised skill | 40 before and 40 after samples for small and large fixtures | Yes | Golden fixtures and duplicate/missing-owner checks | Field verification pending; proposed build/slice check |

The revised-skill session reported `large.json` full-CLI medians of 209.385 ms before and 28.720 ms after (40 runs each), and `small.json` medians of 30.525 ms before and 23.166 ms after (40 each). Those numbers describe the synthetic fixture on that run's host. They do not establish production benefit. This is a single held-out run per condition; it supports keeping the revised guidance, not a general claim that the skill always changes agent behavior.

The updated worked example is separately executable with `python3 performance-optimization/examples/membership_workload.py measure --runs 9`. Two nine-pair local runs, after correcting the harness so validation is inside the timed boundary and neither mode runs the baseline lookup as hidden setup, recorded scan medians of 136.325 and 140.875 ms versus indexed medians of 41.900 and 43.563 ms. Correctness matched the fixed fixture digest. Field telemetry and memory impact remain unmeasured.

## Decision

Keep the focused diagnostic guide, corrected executable example, and experiment rules for variance, failed attempts, proxy calibration, and matched field slices. Do not claim the reasoning-fixture screen proved uplift. Do not make Jev or a strict performance threshold a release gate from this evidence. Trigger probes were authored (three positive, two near miss) but not executed in the phase-one screen. A future release-gate decision needs repeated held-out tasks, independent review, and an explicit grader/provenance contract.

Local raw event traces, prompts, and rubrics are retained in `/private/tmp/performance-optimization-v2/` and `/private/tmp/perf-opt-heldout-runs/` on the evaluation host. These temporary paths are not durable release artifacts. The durable evidence here is deliberately limited to the task design, observed outcomes, and boundaries above.
