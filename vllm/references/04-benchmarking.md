# vLLM Benchmarking: Throughput, Latency, and Useful Capacity

> **Last Updated:** 2026-11-08
> Sources: https://docs.vllm.ai/en/latest/benchmarking/cli/,
> https://docs.vllm.ai/en/latest/cli/bench/serve/,
> https://docs.vllm.ai/en/latest/configuration/optimization/, and
> https://docs.vllm.ai/en/latest/features/automatic_prefix_caching/

## Define the claim before generating load

Capacity is the load a specific deployment sustains within declared latency,
error, memory, and task-quality constraints. A startup memory estimate or peak
tok/s is not measured SLO capacity. Declare the representative workload,
measurement interval, acceptance criteria, and stop conditions first. A test
server and a bounded load-test scope must be authorized before sending traffic.

Keep these counts separate, with timestamps or aligned sampling windows:

- **Active agents/tasks**: orchestration activity, including time spent waiting
  on tools, humans, or other agents. Ten active agents need not mean ten model
  requests overlap; a single agent may fan out several requests.
- **Requested concurrency and arrival rate**: the load generator's settings.
  Record actual in-flight requests, including client/gateway queues, because
  the configured cap is not proof it was reached.
- **Queued and running inference**: server waiting/running gauges or traces.
  Correlate these with client timestamps and scheduler limits; neither count
  equals the number of active agents or a static slot reservation.

For tool-using workflows, replay realistic think/tool-wait intervals as well as
an inference-only stress test. Label both: stress overlap is not an observed
agent workflow. Keep the same task mix across candidate deployments.

## Configurable concurrency sweep

Start with **1, 2, 4, 8, 10** outstanding-request levels. This is a configurable
experiment plan, not a hardware limit or a requirement to reach ten unsafely.
Extend beyond ten when useful and within the authorized budget; add points near
the throughput plateau or SLO boundary. Do not stop at four merely because an
example did, or select a universal 80–90% of startup-estimated concurrency.

1. Freeze the conditions below and set numeric stop constraints for memory
   headroom, preemption/error rate, tail latency, thermal state, test duration,
   and cost/compute budget. Decide how sustained violations are detected.
2. Warm up compilation/model execution consistently, then establish the
   intended prefix-cache state separately. Cold prefix cache does not have to
   mean a cold process. Use isolated scratch runs or an approved reset method;
   never clear a production cache just to make a benchmark comparable.
3. Run one level at a time, repeat it, and save client plus server evidence.
   Stop escalating when a predefined constraint is hit. Record untested levels
   and the reason rather than extrapolating a pass.
4. Repeat across realistic short/long context and output-length distributions,
   not just a fixed maximum. Include cold/warm cache and shared/non-shared
   prefix cohorts, with the same prefix lengths, reuse order, and mix on both
   sides of a comparison.
5. Select a supported operating point using SLO attainment, error/quality
   results, and measured headroom. Report the tested range and uncertainty;
   a higher-throughput point that breaks an SLO is not extra usable capacity.

## Online benchmark invocation

Check `vllm bench serve --help` for the pinned release. This illustrative command
runs one level, not an automatically safe full sweep:

```bash
vllm bench serve \
  --backend vllm \
  --model <model-name> \
  --endpoint /v1/completions \
  --dataset-name sharegpt \
  --dataset-path <path>/ShareGPT_V3_unfiltered_cleaned_split.json \
  --num-prompts <sample-count> \
  --request-rate inf \
  --max-concurrency <sweep-level> \
  --save-result --result-dir ./log
```

- `--request-rate inf` offers requests without arrival pacing, but the client
  concurrency cap still limits overlap. A finite rate controls offered arrivals;
  `--burstiness 1` uses Poisson arrivals, values below one are burstier, and
  values above one are more regular. Record achieved as well as offered rate.
- `--max-concurrency` limits client requests, not engine running sequences.
  `--max-num-seqs` is a separate server scheduling constraint.
- Representative chat needs the matching chat backend/endpoint and chat
  template. Validate the dataset schema for the installed release; a random
  token test does not establish tool-calling or application quality.
- Where supported, `--save-detailed` includes per-request information, potentially
  response text. Use only approved benchmark data, restrict access, and redact
  private text before sharing. Supplement missing fields with client traces;
  do not assume aggregate CLI output contains every observation below.

## Results to retain

TTFT is time to the first token; TPOT measures time per generated token after
the first; ITL captures gaps between streamed tokens. Define the timestamp
boundary so client queuing is not silently omitted from end-to-end latency.

- Aggregate request throughput, output tok/s, and total tok/s, with sample
  count, measurement interval, repetitions, and variance. State the denominator
  and whether failures are excluded from each metric.
- Per-request TTFT, TPOT, ITL, queue wait, and end-to-end latency: p50/p95/p99
  plus distributions/raw observations, grouped by workload/cohort. Keep a
  per-request decode rate where useful; aggregate output tok/s is not each
  request's speed. Small samples make extreme percentiles unstable; report that
  limitation. Mark unsupported measurements rather than inventing them.
- Actual prompt/context and generated-token distributions, not only configured
  limits. Record output caps, EOS/stopping behavior, truncation and finish
  reasons. Faster short/truncated answers can be worse work.
- Attempted, completed, and accepted tasks; HTTP/model errors, timeouts,
  cancellations, retries, and failed or still-pending tasks. Keep terminal
  outcomes by task ID so retries cannot become extra successes. Do not hide
  failures by reporting only successful-request latency.
- **Accepted tasks/hour** = distinct tasks meeting a fixed acceptance rubric /
  measured end-to-end wall-clock hours. Count retries, tool waits, and required
  review in the declared boundary. Bind task IDs to eval results and rubric
  revision, using `agent-evals-and-observability` for task-level evaluation and
  `ml-engineering` for serving acceptance design. HTTP 200 and generated tokens
  prove neither task correctness nor acceptance. If acceptance was not
  evaluated, report accepted tasks/hour as not measured.
- GPU and host memory peaks/headroom, allocated KV bytes/blocks and occupied
  fraction, running/waiting time series, preemptions/recomputations, utilization,
  temperature/throttling, and competing load. Inspect emitted metric names for
  the installed release; logs and traces may be needed for missing counters.

## Prefix caching is a controlled variable

Prefix reuse skips repeated prefill work; it does not directly accelerate
new-token decoding. Record cached/recomputed input tokens or hit/query counters
with their definitions, TTFT and TPOT separately, and eviction/preemption under
load. Warm shared-prefix gains can disappear for unrelated or cold requests.
Do not report a change in prompt mix or cache warmth as an engine speedup.

## Comparable evidence

The [benchmark run record](../templates/benchmark-run-record.md) freezes:

- engine version/image digest; model, tokenizer, and template revisions;
- quantization, dtype, kernels/backend, parallelism, KV budget/dtype, and
  request-length limits;
- resolved scheduling, chunked-prefill, prefix-cache and performance settings;
- GPU count/model/driver/interconnect; host, thermal state, and background load;
- dataset hash/task mix, actual context/output distributions, seeds/sampling,
  stop policy, offered rate, achieved overlap, tool waits, and retry policy;
- cache cohorts/order, warmup, test duration, repetitions, and acceptance rubric.

Change one declared variable at a time and disclose other drift. An upgrade
compares two pinned versions while holding other conditions fixed as far as
possible. Never turn a synthetic throughput test into a universal engine,
quantization, or hardware ranking.

## Offline tests and production tools

`vllm bench throughput --model <model-name> --input-len 512 --output-len 128
--num-prompts 1000` measures engine-only throughput. `vllm bench latency` is a
latency-oriented offline test. Neither includes the client/network/agent path.
The upstream benchmark guide also recommends GuideLLM for production capacity
testing; tool choice does not replace the workload, SLO, and evidence contract.
Documentation and structural eval checks are not performance measurements.
