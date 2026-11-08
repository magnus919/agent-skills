# vLLM Continuous Batching and Tuning

> **Last Updated:** 2026-11-08
> Sources: https://docs.vllm.ai/en/latest/configuration/optimization/,
> https://docs.vllm.ai/en/latest/features/automatic_prefix_caching/,
> https://docs.vllm.ai/en/v0.26.0/configuration/engine_args/, and
> https://docs.vllm.ai/en/v0.26.0/api/vllm/config/cache/, and
> https://docs.vllm.ai/en/v0.26.0/api/vllm/engine/arg_utils/

## Inspect defaults before changing them

vLLM continuously schedules new requests as capacity becomes available. KV
blocks track resident tokens rather than reserving one full context window
per request. Actual behavior depends on engine version, model, and backend.
Record the supplied flags **and resolved startup configuration**. CLI help or
a config-class default alone may omit model-specific resolution or overrides.
For example, v0.26.0 EngineArgs keeps hybrid-model prefix caching opt-in,
despite CacheConfig defaulting to true, and disables both features on RISC-V
CPU. Do not generalize either an enabled or disabled default to every model.

| Flag | Observed default/behavior | What to measure |
|---|---|---|
| `--max-num-seqs` | Runtime-selected; caps sequences per scheduling iteration | Running/queued requests, throughput, latency, and KV pressure |
| `--max-num-batched-tokens` | Runtime-selected token budget per iteration | Prefill/decode contention, TTFT and ITL/TPOT |
| `--enable-chunked-prefill` | V1 enables it where supported; not generally off | Resolved setting, then latency versus token-budget choices |
| `--enable-prefix-caching` | v0.26.0 CacheConfig defaults to enabled; inspect runtime eligibility | Shared-prefix reuse, TTFT, cache occupancy and eviction |
| `--performance-mode` | Version-sensitive (`balanced`, `interactivity`, `throughput` where supported) | Task latency versus aggregate throughput under the same load |
| `--optimization-level` | Version-sensitive compilation configuration; inspect installed help | Startup cost and measured steady-state performance, not a universal best level |

Chunked prefill splits long prefills into the remaining token budget while
prioritizing decode in V1. It can reduce prefill/decode interference; tune the
budget instead of assuming an already-enabled feature needs enabling. Prefix
caching reuses matching prefixes to reduce prefill work, not new-token decoding
work. Check these claims against the installed release before using old advice.
Where supported, `--long-prefill-token-threshold` and partial-prefill limits
control how long prefills share scheduler capacity; record their resolved values
when they are part of the experiment.

## Tuning discipline

1. **Baseline first**: freeze the serving configuration and benchmark record;
   capture cache usage, running/waiting requests, preemption/recomputation,
   memory headroom, actual token distributions, and latency tails.
2. **Change one knob at a time**. More sequences may improve aggregate
   throughput, but can increase queueing, contention, or preemption. A lower
   limit may stabilize latency or merely move waiting to the client; measure
   both boundaries.
3. **Diagnose pressure**: high KV occupancy plus waiting requests is a reason to
   investigate, not proof that every request is memory-bound. Correlate
   preemption, scheduler limits, utilization, and TTFT/TPOT. Consider bounding
   inference overlap, reducing actual prompt/output demand, or scaling out.
4. **Match the experiment**: mixed long/short prefills call for checking the
   resolved chunked-prefill setting and token budget. Reused system prompts
   call for cold/warm and shared/non-shared prefix cohorts, not a promise of
   faster decoding. Do not quietly truncate useful work to improve a benchmark.
5. **Verify useful capacity**: repeat the [benchmark sweep](04-benchmarking.md),
   including 1, 2, 4, 8, 10 as configurable starting
   levels, with declared stop constraints. Check per-request SLOs, failures,
   and task outcomes alongside throughput before recommending a change.

## Interpret startup capacity without overclaiming

Startup can report a KV token capacity and a maximum concurrency at a specified
request length. In a simple homogeneous full-attention case, dividing the token
pool by that length gives an approximate full-length residency count. Record
the engine's estimate and assumptions: block rounding, sharing, hybrid/sliding
attention, and other layouts can change the accounting.

It is not a universal ceiling for client requests (some can wait), a measured
latency SLO, or a reason to benchmark at a fixed 80–90% of the estimate. Shorter
actual requests or prefix sharing change residency; queueing and compute can
bind well before memory does. Use the measured workload sweep to select an
operating point with justified headroom.

`max-model-len` limits admitted prompt plus output length. The allocated KV pool
instead follows its memory budget and profiling; live occupancy follows actual
resident tokens and sharing. Lowering a configured 32K limit to 16K with the
same 4K prompts and 1K outputs does not itself halve their KV use or double SLO
capacity. If lower limits reject or truncate long tasks, record those outcome
changes. Re-profile and re-benchmark instead of assuming freed memory.
