# vLLM Model Configuration: Quantization, Tensor Parallelism, KV Cache

> **Last Updated:** 2026-11-08 (context/KV distinction and GGUF caveats)
> Sources: https://docs.vllm.ai/en/latest/configuration/engine_args/ and
> https://docs.vllm.ai/en/latest/features/quantization/index.html,
> https://docs.vllm.ai/en/v0.26.0/configuration/engine_args/, and
> https://docs.vllm.ai/en/latest/features/quantization/gguf/

## Model identity and context

- `--model` is the Hugging Face repo or a local path; `--revision` pins a branch,
  tag, or commit so weight provenance is reproducible. `--tokenizer` overrides
  the tokenizer; `--chat-template` supplies a Jinja2 chat template when the
  model card lacks one (without one, chat requests error).
- `--max-model-len` bounds prompt + output per request and accepts human-readable
  values (`32k` = 32,000; `32K` = 32,768). Unset, it derives from the model
  config. `-1`/`auto` picks the largest length that fits GPU memory, capped by
  the model's supported context on that release. This is a request/admission
  bound, not the allocated KV pool size. Actual resident prompt and generated
  lengths consume KV blocks; halving only the configured bound at unchanged
  actual lengths does not automatically free half the memory or double capacity.
  A stricter bound may reject workloads rather than make them faster.
- `--dtype` selects weight/activation precision (`auto`, `bfloat16`, `float16`,
  `float32`, `half`). `auto` uses FP16 for FP32/FP16 models and BF16 for BF16
  models; some quantized formats are recommended at a specific dtype (for
  example `half` for AWQ).

## Quantization-aware serving

- **Let the checkpoint declare its scheme.** vLLM first checks the model's
  `quantization_config`; `--quantization`/`-q` is for cases where the config is
  missing or needs overriding. Serving a checkpoint with the wrong method fails
  to load or silently degrades.
- **Supported methods (as of v0.26.0)**: GPTQ, AWQ, bitsandbytes (load-time
  quantization), GGUF, LLM Compressor FP8/INT8/INT4, NVIDIA Model Optimizer
  (NVFP4/MXFP4/FP8), TorchAO, and online quantization. The current index lives
  at https://docs.vllm.ai/en/latest/features/quantization/index.html.
- **Hardware coupling**: kernel support varies by GPU generation — for example
  Marlin (GPTQ/AWQ/FP8/FP4) requires Turing+ and is NVIDIA-only; FP8 W8A8 needs
  Ada/Hopper; GGUF and bitsandbytes span more platforms. Check the compatibility
  table before choosing a quantized checkpoint for a GPU fleet.
- **KV cache quantization**: `--kv-cache-dtype` (`auto`, `bfloat16`, `float16`,
  `fp8` = `fp8_e4m3`, `int8_per_token_head`, `nvfp4`, ...) shrinks the attention
  cache for long-context workloads on CUDA 11.8+. This is a quality-vs-capacity
  decision; spot-check outputs before trusting it at scale.
- **Dated-source rule**: quantization support changes every release. Never
  assume a method that worked on one version works on the next; the source
  index records the refresh date.

### GGUF is a separate compatibility experiment

The official GGUF page describes support as experimental and under-optimized,
with possible incompatibilities with other features. Current docs require the
out-of-tree `vllm-gguf-plugin` and recommend explicitly selecting the base-model
tokenizer to avoid GGUF tokenizer-conversion problems. Older releases may use
a different integration path: pin and check both engine and plugin versions,
model architecture, quant type, tokenizer revision, and required features.
Do not infer serving performance from file size or assume GGUF is equivalent
to a native supported checkpoint. Test feature correctness and task quality
alongside the matched benchmark before choosing it. See `llama-cpp` for that
engine's GGUF operations, not as proof of vLLM compatibility.

## Tensor, pipeline, and data parallelism

- `--tensor-parallel-size N` (`-tp`) shards each layer's weights and attention
  across N GPUs in one node. It requires fast interconnect (NVLink or high-speed
  NIC) and equal per-GPU memory. Startup runs a memory-profiling pass and logs
  the resulting KV cache size — that log line is the evidence the model fits.
- `--pipeline-parallel-size N` (`-pp`) splits layers across ranks/nodes for
  models too large for one node's aggregate memory; it adds inter-stage
  communication latency.
- `--data-parallel-size N` (`-dp`) replicates the model across groups for
  throughput scaling of small models. `--expert-parallel-size` shards MoE
  experts. The product of TP × PP × DP (× EP for MoE) must equal the world size.
- **Gotchas**: tensor-parallel workers must all see the same visible GPU set
  (`CUDA_VISIBLE_DEVICES` applies to the whole process group); mixed GPU models
  or different per-GPU memory cause the memory profile to fail; multi-node TP
  needs `--distributed-executor-backend mp` with `--master-addr`/`--master-port`
  reachable across nodes.

## Memory budgeting

- `--gpu-memory-utilization` (0.92 in v0.26.0; inspect the installed config)
  caps the fraction of GPU memory the
  model executor may use — weights plus KV cache plus activation buffers. It is
  per-instance and does not account for other processes on the GPU.
- Weights dominate first: a bf16 70B needs ~140 GB before any KV cache, so it
  needs two 80 GB GPUs (TP=2) or quantization. Only after weights fit does the
  KV cache constrain resident requests: the engine logs `GPU KV cache size: N tokens`
  and `Maximum concurrency for M tokens per request: K`; record both along with
  the assumed length. This estimate does not include queueing/latency SLOs.
- The allocated pool follows memory profiling and its budget; v0.26.0 supports
  `--kv-cache-memory-bytes` as an explicit per-GPU pool budget that overrides
  memory-utilization-based KV sizing. Separate allocated bytes/blocks from
  live occupancy and cached reusable blocks. Attention layout, KV dtype,
  sharing, and actual token lengths affect residency. Re-profile any change.
- `--cpu-offload-gb` moves model weights to CPU per GPU (a virtual memory increase
  at the cost of PCIe-bound performance) — a stopgap for fitting a model, not a
  performance feature.
- `--load-format` (auto, safetensors, npcache, bitsandbytes, sharded_state, ...)
  controls how weights are read; `--safetensors-load-strategy eager` avoids
  random reads on network filesystems (NFS/Lustre) at the cost of CPU RAM.

## Configuration record

Every non-default choice goes into `templates/serving-config.md`. The record is
what makes a deployment reproducible and rollback a redeploy of the previous
pinned image plus record.
