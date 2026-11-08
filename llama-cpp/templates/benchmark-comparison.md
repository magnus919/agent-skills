# llama.cpp Benchmark Comparison

## Objective

- Hypothesis:
- Primary metric and threshold:
- Guardrail metrics and thresholds:
- Workload represented:
- Evidence boundary: component benchmark / offline completion / concurrent server / agent-task workflow:

## Frozen conditions

- Host / power / thermal / background load:
- llama.cpp commit and build options:
- Driver / backend / devices / interconnect:
- Model file hash / quant / template / sidecars:
- Fixture/task IDs and acceptance criteria revision:
- Prompt and output lengths / context depth (including rendered system/tool/history tokens):
- Context / batch / ubatch / threads / slots:
- Cache / Flash Attention / offload / split:
- Warmup / repetitions / delay:

## Compared variable

- Baseline value:
- Candidate value:
- All other known differences:

## Commands and raw artifacts

- Baseline command/output path:
- Candidate command/output path:
- End-to-end or server command/output path:
- Quality fixture/results:

## Results

| Metric | Baseline | Candidate | Delta | Variance / confidence | Threshold |
|---|---:|---:|---:|---:|---:|
| Prompt processing | | | | | |
| Token generation | | | | | |
| TTFT | | | | | |
| End-to-end latency | | | | | |
| Throughput | | | | | |
| Peak RAM | | | | | |
| Peak device memory | | | | | |
| Task quality / success | | | | | |
| Error rate | | | | | |

## Server sweep contract (when measuring serving)

- Client-outstanding-request levels: 1, 2, 4, 8, 10; edit/extend for the target workload:
- Reason for any omitted or higher levels (ten is not a ceiling):
- Client load model: fixed outstanding / burst / arrival rate; rate and queue limits:
- Server configured slots and resolved per-slot context/shared KV behavior:
- Frozen server configuration ID; new configuration/baseline if slots or context change:
- Load-generator capacity and observation sampling interval:
- Fixed quality threshold, latency limits, finish/truncation acceptance policy:
- Timeout/retry budget, repetition count, warmup, measurement window and drain/cutoff policy:
- Predeclared stops: memory margin/pressure/swap, thermal, latency/timeouts/errors, unusable output, wall/resource budget:
- Stop/cleanup scope and last measured safe cell:

Use token ranges representative of the workload, not nominal context flags.
Run each planned load level across these contexts and cache cohorts. Record every
planned cell, including ones not run; use the compact register below and link
complete raw records. Do not force unsafe cells to run to fill the table.

| Context cohort | Input/history token range | Reserved output | Fixture/task IDs | Quality threshold |
|---|---|---|---|---|
| Short | | | | |
| Normal | | | | |
| Long | | | | |

| Cache cohort | Reset/isolation or warmup method | Shared prefix tokens | Ordering/slot assignment | Observed reuse evidence |
|---|---|---|---|---|
| Cold common prefix | | | | |
| Warm common prefix, varied suffixes | | | | |
| Diverse independent prefixes | | | | |

Warm model state and warm prompt-cache state are separate. Cache hits can reduce
prefill; measure decode independently. Unsupported or missing cache observations
remain unknown.

### Cell register

Repeat rows for every context/cache/configuration combination and added level.
Status is measured (with guardrail result), aborted (with observed reason), or
not run (unknown). A skipped level is neither a measured failure nor capacity.

| Config / context / cache | Target client outstanding | Observed outstanding / client queue | Server running / deferred | Status / stop or skip reason | Raw results |
|---|---:|---|---|---|---|
| | 1 | | | | |
| | 2 | | | | |
| | 4 | | | | |
| | 8 | | | | |
| | 10 | | | | |
| Higher level if relevant | | | | | |

### Per-cell observations

- Cell/configuration ID, start/end and total measured wall seconds:
- Active agents / tool-or-I/O-waiting agents (or not applicable):
- Client target and observed outstanding requests / queued requests over time:
- Configured slots / observed running slots / processing and deferred requests:
- Correlated request/slot timeline or decode/batch trace showing overlap, sample interval and limits:
- Aggregate prompt tokens/s and generated tokens/s; tokens and wall-time denominator:
- Completed requests/s; per-request decode rate/time per token if measurable:
- TTFT first-event definition, p50/p95, sample count and repeated-run variance:
- End-to-end latency p50/p95; client queue delay; observable server queue delay:
- Failure/timeout latency inclusion or censoring policy and counts:
- Unique tasks attempted / accepted / quality-rejected / failed / unfinished:
- Request attempts / retries / errors / timeouts / cancellations (identify overlapping categories):
- Accepted tasks/hour = 3600 × unique accepted tasks / total measured wall seconds:
- Retry/failed/queued/timeout time retained; tool waits retained for agent-task rate:
- Usage prompt/completion tokens; missing usage fields:
- Finish-reason counts / truncations / empty or malformed outputs:
- Fixed-fixture task quality and acceptance results:
- Peak/resident RAM / peak per-device memory / KV-cache use / remaining margin:
- Memory pressure/swap / thermal observations / OOM or other stop trigger:
- Cache-reused/evaluated tokens or other route-supported evidence; unavailable fields:

Do not call aggregate throughput per-request decode speed, or equate configured
slots with observed inference overlap. Count accepted logical tasks once despite
retries; keep failure and retry time in the denominator. Label successful-only
latency summaries and report their omitted outcomes. Missing metrics are unknown.

## Verdict

- Accept / reject / inconclusive:
- Evidence:
- Confounders or unverified boundaries:
- Highest passing tested cell and its exact context/cache/configuration, not claimed maximum capacity:
- Not-run/aborted cells and remaining evidence needed for the target workload:
- Rollback or next experiment:
