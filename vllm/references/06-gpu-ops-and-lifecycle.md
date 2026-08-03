# vLLM GPU Operation, Upgrade, and Rollback

> **Last Updated:** 2026-08-03
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
  alert on cache usage near 1.0 with requests waiting (capacity), repeated OOM,
  and probe failures.
- **OOM at startup** usually means weights + KV cache do not fit: reduce
  `--max-model-len`, switch to a quantized checkpoint, add GPUs, or (as a
  stopgap) `--cpu-offload-gb`. Lowering `--gpu-memory-utilization` does not
  help if the weights alone exceed memory.
- **OOM mid-run** means KV cache pressure at peak concurrency: shorten context,
  lower `--max-num-seqs`, or scale out replicas.

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
| Server crashes at startup (OOM) | Side-by-side startup logs, `nvidia-smi`, image digests | Weights+KV don't fit; changed defaults after upgrade. Reduce `max-model-len`/memory utilization on scratch, or roll back the pinned image |
| `/health` 200 but requests fail | `/v1/models`, one bounded request | Model not loaded, served-name mismatch, missing chat template; check `/load` and startup log |
| 404 on `/v1/chat/completions` | `/v1/models`, model type | Pooling/embedding model or missing chat template; see `references/03-openai-api.md` |
| High p99 latency | TTFT vs TPOT split, cache-usage metrics | Prefill blocking decode → chunked prefill; KV pressure → bound concurrency |
| Requests waiting, cache ~100% | `vllm:gpu_cache_usage_perc`, waiting gauge | At capacity: scale out or reduce context/concurrency; do not raise batch limits |
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
