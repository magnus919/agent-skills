# vLLM Benchmark Run Record

One record per sweep level, cache cohort, and repetition. Link a sweep summary.
This template is a collection plan, not evidence that a benchmark ran.

## Objective and safe limits

- Run ID / date / operator / authorized target and load-test scope: _[fill]_
- Hypothesis / compared variable / baseline record: _[fill]_
- Workload and user/task acceptance criteria: _[fill]_
- Primary metric and threshold: _[fill]_
- Latency SLOs / error and quality guardrails: _[fill]_
- Stop constraints, measurement window, and abort method: _[fill: memory
  headroom, preemption, p99 latency, timeouts, temperature, duration, budget]_
- Sweep plan: _[fill: default 1, 2, 4, 8, 10; customize and extend when safe]_
- Tested / untested levels and why escalation stopped: _[fill]_

## Frozen conditions

- vLLM version / image tag / digest / plugin versions: _[fill]_
- Model revision / quantization / dtype / backend / kernel configuration: _[fill]_
- Tokenizer revision / chat template hash: _[fill]_
- Tensor / pipeline / data parallel sizes: _[fill]_
- Max model length / request output cap: _[fill: admission limits, not actual use]_
- GPU memory utilization / explicit KV budget / KV dtype: _[fill]_
- Allocated KV bytes/blocks or tokens / startup concurrency estimate and its
  assumed request length: _[fill: memory estimate, not measured SLO capacity]_
- Resolved max sequences / batched tokens / chunked prefill / prefix caching /
  performance settings, and where verified: _[fill]_
- GPU model / count / driver / interconnect / host memory: _[fill]_
- Host / thermal state / competing load: _[fill]_
- Serving configuration record: _[fill: reference; no secrets]_

## Workload and cache controls

- Tool/version/command and endpoint: _[fill]_
- Dataset or task-set hash / mix / tokenizer: _[fill]_
- Actual input/context-token distribution p50/p95/max: _[fill]_
- Actual generated-token distribution p50/p95/max: _[fill]_
- Sampling / seed / stop policy / EOS / truncation policy: _[fill]_
- Cache cohort: _[fill: cold or warm; shared or non-shared prefixes]_
- Shared prefix lengths / reuse order / cache preparation or reset evidence:
  _[fill: approved scratch procedure, distinct from process warmup]_
- Compile/model warmup / repetitions / duration / cooldown: _[fill]_
- Offered request rate / arrival burstiness / requested concurrency: _[fill]_
- Active agents / task fanout / tool-wait intervals: _[fill or inference-only]_
- Timeout / cancellation / retry policy: _[fill]_
- Task acceptance rubric revision and linked eval artifact: _[fill: use
  agent-evals-and-observability; HTTP success is not task acceptance]_

## Observed load and results

- Client in-flight and queued requests over time / peak: _[fill]_
- Server waiting and running requests over time / peak: _[fill]_
- Achieved arrival rate versus requested rate: _[fill]_
- Raw client/server records and redaction/access policy: _[fill]_
- Attempted / completed / failed / pending distinct tasks: _[fill]_
- Accepted tasks / measured wall-clock hours / accepted tasks per hour: _[fill
  or not measured; deduplicate by task ID; retries/tool waits remain in boundary]_
- HTTP/model errors / timeouts / cancellations / retry counts: _[fill]_
- Finish reasons / truncation counts / task quality regressions: _[fill]_
- Request throughput / output tok/s / total tok/s with denominators: _[fill]_
- Per-request TTFT / TPOT / ITL p50/p95/p99 and sample counts: _[fill]_
- Queue wait / end-to-end latency p50/p95/p99: _[fill]_
- Per-request decode-rate distribution: _[fill if useful]_
- Failed or censored requests excluded from percentiles and why: _[fill]_
- GPU/host memory peaks and headroom / KV occupancy: _[fill]_
- Preemptions / recomputation / evictions / metrics names and sampling interval:
  _[fill; unsupported data marked unavailable]_
- Cache hits/queries or reused input tokens with definitions: _[fill]_
- Temperature / throttling / utilization / competing load during run: _[fill]_

## Matched comparison and decision

- Single changed variable and baseline/candidate values: _[fill]_
- All other differences or missing observations: _[fill]_
- Results by cache cohort, actual token lengths, and concurrency: _[fill]_
- Variance / tail-percentile uncertainty / sample-size limits: _[fill]_
- Outcome: _[fill: met / not met / inconclusive; separate SLO and task quality]_
- Supported operating point / measured headroom / tested range: _[fill]_
- Next experiment or rollback recommendation: _[fill]_

Do not infer decode acceleration from a prefix-cache TTFT gain, useful task
throughput from aggregate tok/s, or a hardware ranking from unmatched runs.
