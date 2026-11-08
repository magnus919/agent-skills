# Local serving study record

A planning and evidence record, not a benchmark result or new grading contract.
Use with [workload-first selection](../references/local-serving-selection.md) and
existing agent-evaluation/task-receipt contracts. Leave unknown fields unknown.

## Decision and frozen workload

- Decision / date / owner:
- Task and trajectory acceptance criteria / critical failure conditions:
- Dataset, expected case IDs, slice/group definitions and immutable revision:
- Task/trajectory grader specification and independent evidence source:
- Required accepted tasks/hour, quality floor and per-request/task latency SLOs:
- Input/context distribution, longest retained context, output distribution:
- Reasoning/thinking mode, output/reasoning budget, token accounting convention:
- Agent roster, tool duty cycle, observed inference overlap and burst pattern:
- Authorized runtime, data/telemetry boundaries and rollback target:

## Candidates and pinned conditions

| Candidate | Engine / backend / plugin revision | Model and quantized artifact hashes | Compatibility evidence / exclusions |
|---|---|---|---|
| llama.cpp, vLLM, SGLang or another relevant stack | | | |

- Tokenizer/chat template/parser versions and tool/output contract:
- Hardware, OS, drivers/build, power limits, co-tenants/background load:
- Hardware memory totals with explicit GB/GiB units:
- Harness, sampling/stop policy, seeds and repeat protocol:
- Retry/timeout/selection budget and identical acceptance rubric:
- Controlled comparison versus whole-stack comparison; differing variables:
- Tuning budget per candidate; held-out comparison after settings freeze:
- Cold-start/warm-up policy, prefix-cache state and reset/reuse policy:
- Primary-source URL, access date, version/commit and claim limitations:

## Capacity estimate and measured allocation

| Term | Estimate + assumptions | Observed peak + evidence | Units / device |
|---|---|---|---|
| Loaded weights including metadata / unquantized tensors | | | |
| Active and retained KV / recurrent state | | | |
| Activations and temporary workspace | | | |
| Graph/batch/draft buffers | | | |
| Runtime and allocator overhead | | | |
| Headroom / host or unified memory pressure | | | |

- Attention architecture, layers, KV heads (not query heads), head dimension:
- Simultaneously resident sequences, cached tokens including generation, KV dtype:
- Sharing/window/sharding/replication assumptions and supported context evidence:
- Logical payload versus reserved pool versus measured used memory:
- Separate prefill/decode peaks, swap/offload and allocation failure evidence:

## Bounded load protocol

- Initial configurable concurrency ladder: **1, 2, 4, 8, 10**.
- Additional workload-relevant levels beyond ten, or reason none is needed:
- Client in-flight setting versus server sequence/token limits:
- Actual active inference overlap measurement and proof client sustains load:
- Closed-loop request cohorts / open-loop arrival distribution and drain policy:
- Context/output/reasoning slices and prefix-cache conditions at each level:
- Requests per slice, repetitions, tail-sample requirement, total elapsed budget:
- Immediate OOM/unsafe-pressure/critical-quality stop:
- Error/timeout/tail-latency/queue-growth limits and observation windows:
- Preemption/retraction limit, throughput plateau definition and repeat count:
- Optional refinement between last acceptable and failing level within budget:

## Results, including failures

One row per candidate × concurrency × context/output slice × cache state × repeat.
Link raw minimized telemetry; do not populate with illustrative performance claims.

| Run ID | Requested / observed concurrency | Context / output / thinking | Cache state | Execution status / stop reason |
|---|---|---|---|---|
| | | | | not run / complete / failed / incomplete |

- Cold load/compile time and excluded warm-up interval:
- Single-request decode rate, token counts and exact decode-window convention:
- Aggregate generation/prefill throughput over a shared elapsed window:
- Queue, TTFT, TPOT/inter-token and full task latency p50/p95/p99 + sample count:
- Cohort window start/end and elapsed seconds, or arrival/drain/censoring rules:
- Unique expected / accepted / failed / timed-out / unresolved tasks:
- Errors, request retries, task retries and attempt ledger, including failures:
- Accepted tasks/hour = accepted unique tasks × 3600 / cohort elapsed seconds:
- Task-quality slices, critical regressions and acceptance evidence:
- Peak memory, preemptions/retractions, rejects and queue growth:
- Between-run spread, paired task/groups and evidence gaps:
- Higher levels not run and reason; no extrapolated performance results:

## Existing contracts and decision

- Matched single-attempt receipt pair and `compare_task_runs.py` report:
- Matching dataset/harness/decoding/budget pins (or explicit incomparable result):
- Retry-enabled study: existing agent-evaluation run report/trajectory evidence:
- Separate telemetry/window ledger for accepted tasks/hour (not helper output):
- Chosen operating point, workload boundaries and residual risks:
- Rejected or inconclusive candidates and reasons:
- Registered quality/reliability/SLO guardrails, evidence and decision authority:
- Rollback, retest triggers, owner and unresolved validation:

A complete helper report or green schema check is not model execution, task
acceptance, a capacity measurement or release approval. An empty result table
means not run, never zero errors or a successful benchmark.
