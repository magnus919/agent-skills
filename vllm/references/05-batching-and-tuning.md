# vLLM Continuous Batching and Tuning

> **Last Updated:** 2026-08-03
> Sources: https://docs.vllm.ai/en/latest/configuration/engine_args/ and
> https://www.anyscale.com/blog/continuous-batching-llm-inference

## How continuous batching works

vLLM batches requests **continuously** (iteration-level scheduling): the
scheduler admits new sequences whenever capacity frees up, mixing prefill and
decode in the same iteration instead of waiting for a whole batch to finish.
PagedAttention stores KV blocks in a paged table so memory is allocated per
token-block rather than per whole sequence, which is what makes high occupancy
and large effective concurrency possible. The practical consequences:

- A single model replica serves many concurrent requests; throughput rises with
  concurrency until the KV cache or the batch limits bind.
- Long prefill requests can block decode of other requests unless chunked
  prefill is enabled, which is exactly what spikes p99 latency under mixed
  workloads.

## The knobs

| Flag | Default behavior | What it does |
|---|---|---|
| `--max-num-seqs` | convenience default (set per deployment) | Max sequences per scheduling iteration. Higher = more batching and throughput, higher per-request latency and KV pressure. |
| `--max-num-batched-tokens` | convenience default (set per deployment) | Max tokens per iteration. Together with chunked prefill it bounds how much prefill work can run between decode steps. |
| `--enable-chunked-prefill` | disabled by default on most configs | Lets a prefill request be chunked across iterations so it shares time with decode; the fix for prefill-blocking-decode latency spikes. |
| `--enable-prefix-caching` | disabled | Reuses KV blocks for shared request prefixes (chat system prompts, RAG contexts); hit rate shows up in `/metrics` and lower effective input tokens. |
| `--performance-mode` | `balanced` | Kernel-level trade: `interactivity` favors low end-to-end latency at small batch sizes; `throughput` favors aggregate tok/s at high concurrency. |
| `--optimization-level` | `-O2` | Startup-time vs performance trade for `torch.compile` (`-O0` fastest start, `-O3` best performance). |

Both `--max-num-seqs` and `--max-num-batched-tokens` accept human-readable
sizes (`1k`, `2M`, ...). `--long-prefill-token-threshold` sets when a prefill is
treated as long for chunked-prefill scheduling.

## Tuning discipline

1. **Establish the baseline first**: freeze the serving config record, run the
   benchmark, and record `vllm:gpu_cache_usage_perc`,
   `vllm:num_requests_running`, and `vllm:num_requests_waiting` at the peak.
2. **Change one knob at a time** and re-run the frozen benchmark. Two changes
   in one iteration make the delta unassignable.
3. **Read the signals**: cache usage near 1.0 with requests waiting means the
   KV cache is the binding constraint — lower `--max-num-seqs`, shorten
   `--max-model-len` or cap output tokens, or scale out. It does not mean
   raise the batch limits further.
4. **Match the knob to the symptom**: latency spikes under mixed load →
   chunked prefill + a deliberate `--max-num-batched-tokens`; low utilization
   at steady state → raise `--max-num-seqs` within the cache budget;
   shared-prefix workloads → `--enable-prefix-caching`.
5. **Verify at the boundary**: re-run the benchmark and confirm the declared
   metric moved and the guardrail metrics (p99 TTFT/TPOT) did not regress,
   with variance reported across repetitions.

## Capacity math from the startup log

At startup the engine reports something like:

```
GPU KV cache size: 15,728,640 tokens
Maximum concurrency for 8,192 tokens per request: 1920
```

`max_concurrency = kv_cache_size / max_model_len`. Use 80-90% of that figure as
the `--max-concurrency` for capacity-planning benchmarks, and treat the size as
the ceiling when deciding whether to raise concurrency or shorten context.
