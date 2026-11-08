# vLLM GPU Operation, Upgrade, and Rollback

> **Last Updated:** 2026-11-08 (memory-pressure interpretation)
> Sources: https://docs.vllm.ai/en/latest/configuration/engine_args/,
> https://docs.vllm.ai/en/latest/deployment/docker/,
> https://github.com/vllm-project/vllm/releases

## GPU operation

- **Inventory first**: `nvidia-smi` (NVIDIA) or `rocm-smi` (AMD) shows device
  list, per-GPU memory, utilization, temperature, power, and ECC/error state.
  Record it before and after changes; a thermal or ECC change invalidates
  benchmark comparisons.
- **Device selection**: `CUDA_VISIBLE_DEVICES="0,1" vllm serve ...` restricts
  which GPUs the process sees; `--tensor-parallel-size` counts the *visible*
  devices in order. Device names are the container's view, not the host's —
  verify with `nvidia-smi -L` inside the container.
- **Per-GPU memory matters**: tensor parallelism assumes equal per-GPU memory.
  Mixed-capacity GPUs or other workloads sharing a GPU break the memory
  profile; pin the serving process to dedicated devices.
- **Observability**: `/metrics` exposes `vllm:gpu_cache_usage_perc` (KV cache
  pressure), `vllm:num_requests_running`, `vllm:num_requests_waiting`, and
  token counters. Prometheus scraping of `/metrics` is the standard wiring;
  correlate cache usage and waiting with preemption, actual lengths, and SLO
  tails. Inspect emitted metric names for the installed version. Occupancy
  alone is not evidence of measured capacity.
- **OOM diagnosis**: identify whether failure occurs loading weights, profiling
  activations, capturing graphs, allocating KV, or running a particular batch.
  Check competing processes and per-GPU headroom. Reducing a request-length
  bound is not a guaranteed way to shrink the allocated pool or resident KV
  at unchanged actual token lengths. Match a bounded scratch experiment to
  the allocation that failed; weights that cannot fit may need quantization,
  additional GPUs, or weight offload. Mid-run OOM is not necessarily KV alone.

## Upgrade

1. **Pin before you start**: image tag (or `pip install vllm==<version>`),
   model revision, and the full serving command from the serving config record.
   Without pins, upgrades are unreproducible and rollback is guesswork.
2. **Read the release notes for the full span** (for example v0.25.1 → v0.26.0):
   vLLM deprecates and renames flags, changes defaults (memory allocation,
   `max-model-len` derivation, CUDA graph capture), and adjusts kernel/hardware
   support between releases. A config that ran on one minor may not behave the
   same on the next.
3. **Rehearse on a scratch instance** with the real model and workload: install
   the new version, apply the config, confirm the model loads, and run the
   frozen benchmark.
4. **Swap with a rollback plan**: deploy the new pinned image, verify at the
   delivery boundary (`/health`, `/v1/models`, a representative request,
   re-benchmark), and keep the previous image + config ready to reapply.

## Rollback

- **Rollback is a redeploy of the previous pinned image + serving config.**
  Because the config record is versioned and the image tag is pinned, the old
  state is reproducible by construction.
- Verify the rollback the same way as an upgrade: `/health`, `/v1/models`, one
  representative request, and the frozen benchmark. Do not assume the old
  behavior returned because the old image is back.
- Watch for **config drift across versions**: KV cache layout, defaults, and
  flag names change between releases. A rollback must restore the *recorded*
  config, not the current one.

## Troubleshooting table

| Symptom | First evidence to collect | Likely causes and next step |
|---|---|---|
| Server crashes at startup (OOM) | Allocation phase, side-by-side logs, `nvidia-smi`, image digests | Compare weights, activation/graph and KV budgets plus competing load; validate a targeted scratch change or roll back |
| `/health` 200 but requests fail | `/v1/models`, one bounded request | Model not loaded, served-name mismatch, missing chat template; check `/load` and startup log |
| 404 on `/v1/chat/completions` | `/v1/models`, model type | Pooling/embedding model or missing chat template; see `references/03-openai-api.md` |
| High p99 latency | TTFT vs TPOT split, resolved defaults, cache/preemption metrics | Tune the already-resolved chunked-prefill budget if contention is shown; bound overlap when pressure is shown |
| Requests waiting, cache ~100% | Cache usage, waiting/running, preemption, actual lengths and latency | Investigate pressure; use the SLO sweep before scaling or reducing actual demand/concurrency |
| Container killed at startup | `kubectl get events`, log `KeyboardInterrupt: terminated` | Probe `failureThreshold` too low for model load time; raise it |
| Slow restart every time | Startup duration, `VLLM_CACHE_ROOT` | Compile cache not persisted; mount `~/.cache/vllm` volume |

## Hard boundaries

- No restart, redeploy, scale, or upgrade without an explicit human directive
  naming the target and a stated rollback path. Read-only discovery may proceed
  without confirmation.
- Never compare performance across versions, models, quants, parallelism,
  contexts, batches, or workloads as if one variable changed.
- Never expose development-only endpoints, request logs with prompt content, or
  credentials to chat or logs.
