# Performance optimization — measure, improve, verify

## Why Install This Skill

“Make it faster” often starts with a profiler screenshot and ends with a benchmark that users never notice. This skill turns that request into a repeatable investigation: choose the journey, define what users wait for, establish a trustworthy baseline, and find the actual bottleneck.

An agent using it can add missing measurements, design a representative benchmark, run focused experiments, check correctness and tradeoffs, and verify the result after rollout. It also knows when a promising local result is still unproven and when to stop spending effort on a tiny gain.

## What You Get

| File | Purpose |
|---|---|
| `SKILL.md` | The seven-step optimization loop and routing to specialist skills |
| `references/measurement-and-benchmarks.md` | Field, trace, profile, and benchmark design |
| `references/experiment-and-rollout.md` | Comparison, decision, and rollout rules |
| `templates/optimization-record.md` | A record for one journey or bottleneck |
| `evals/evals.json` | Representative output-quality scenarios |

## Quick Start

Install or load `performance-optimization`, then ask: “Our conversation list feels slow. Find the user-visible bottleneck, establish a baseline, and propose one measurable experiment.” Give the agent access to relevant code, telemetry, and a safe benchmark environment. If measurements are missing, its first output should be an instrumentation and baseline plan.

## Triggers

- Make an app, endpoint, workflow, or hot path faster or less resource intensive.
- Identify what to measure and instrument an unmeasured slow journey.
- Design or run a profiling, benchmark, and iteration loop.
- Decide whether a measured optimization actually helped users.

## Requirements

No runtime or API key is required by the skill. Actual measurements require the target system, an appropriate profiler or benchmark tool, and access to relevant telemetry. Production changes follow the target project's review and deployment permissions.
