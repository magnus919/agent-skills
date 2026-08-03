# vLLM Benchmarking: Throughput and Latency

> **Last Updated:** 2026-08-03
> Source: https://docs.vllm.ai/en/latest/benchmarking/cli/

## Metrics that matter

- **Throughput**: request throughput (req/s), output token throughput (tok/s),
  and total token throughput (input + output tok/s). Output token throughput is
  the number users feel; total token throughput includes prompt processing.
- **Latency**: TTFT (time to first token — what users perceive as the start of
  a response), TPOT (time per output token, excluding the first), and ITL
  (inter-token latency, including scheduling jitter). Report mean, median, and
  p99 — p99 under load is the SLO-relevant number.
- Throughput and latency are different axes: raising concurrency raises
  throughput until the KV cache saturates, then latency degrades. State which
  axis a change optimizes before measuring it.

## `vllm bench serve` (online serving benchmark)

Run against a live server with a representative dataset:

```bash
vllm bench serve \
  --backend vllm \
  --model <model-name> \
  --endpoint /v1/completions \
  --dataset-name sharegpt \
  --dataset-path <path>/ShareGPT_V3_unfiltered_cleaned_split.json \
  --num-prompts 100 \
  --request-rate inf \
  --max-concurrency 64 \
  --save-result --result-dir ./log
```

Output includes: `Successful requests`, `Benchmark duration (s)`, `Total input
tokens`, `Total generated tokens`, `Request throughput (req/s)`, `Output token
throughput (tok/s)`, `Total token throughput (tok/s)`, and mean/median/p99 of
TTFT, TPOT, and ITL.

### Load pattern control

- `--request-rate`: `inf` sends all requests immediately (maximum throughput
  test); a finite rate (requests/second) simulates arrival traffic with a
  Poisson process (`--burstiness 1.0`), bursty Gamma traffic (`0.1-0.5`), or
  uniform spacing (`2.0-5.0`).
- `--max-concurrency`: caps outstanding requests, simulating a load balancer or
  gateway limit. The most common production pattern is `--request-rate=inf
  --max-concurrency=<limit>`.
- Datasets: `sharegpt` (realistic chat), `custom` (a JSONL of `{"prompt": ...}`
  entries), synthetic random lengths, and HF-hosted sets. For capacity planning
  use the KV-cache-derived maximum concurrency the server logs at startup as
  the ceiling (80-90% of it for realistic tests).

## `vllm bench throughput` (offline benchmark)

Measures raw engine throughput without the HTTP path:

```bash
vllm bench throughput \
  --model <model-name> \
  --input-len 512 --output-len 128 \
  --num-prompts 1000
```

Use it for engine-only comparisons (kernel, quantization, parallelism); it is
not a user-facing latency measurement. `vllm bench latency` is the
latency-oriented offline variant.

## Comparable evidence (the skill's core rule)

Benchmark numbers are only comparable under **matched conditions**. The
[benchmark run record template](../templates/benchmark-run-record.md) freezes:

- vLLM version/image tag/digest, model + revision, quantization + dtype;
- parallelism (TP/PP/DP), `max-model-len`, KV cache dtype, memory utilization;
- batching knobs (`max-num-seqs`, `max-num-batched-tokens`, chunked prefill,
  prefix caching), performance mode;
- GPU model/count/driver/interconnect, host, thermal, background load;
- dataset, prompt/output lengths, request rate, concurrency, sampling params;
- repetitions and variance.

Never compare numbers from different versions, models, quants, parallelism,
contexts, batches, or workloads as if one variable changed. Re-run the frozen
benchmark after every serving-arg change and record both sides in the template.

## Production capacity testing

For SLA validation and capacity planning the upstream docs recommend the
external GuideLLM framework (live progress, automatic reports). This skill's
scope is the bundled `vllm bench` tools plus the run-record discipline; route
a GuideLLM setup as its own tooling decision.
