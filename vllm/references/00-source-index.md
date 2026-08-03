# vLLM Operations — Source Index

> **Last Updated:** 2026-08-03

This index tracks the authoritative upstream sources behind the vLLM operational
skill and the refresh procedure for keeping it current. vLLM moves fast — flags,
defaults, and endpoint behavior change between releases; treat any claim here as
version-sensitive and re-verify against the installed release.

## Canonical sources

| Topic | Source |
|---|---|
| vLLM documentation (latest) | https://docs.vllm.ai/en/latest/ |
| vLLM documentation (stable release) | https://docs.vllm.ai/en/stable/ |
| Releases and release notes | https://github.com/vllm-project/vllm/releases |
| Docker deployment | https://docs.vllm.ai/en/latest/deployment/docker/ |
| Kubernetes deployment | https://docs.vllm.ai/en/latest/deployment/k8s/ |
| Online serving (OpenAI-compatible API) | https://docs.vllm.ai/en/latest/serving/online_serving/ |
| Engine arguments | https://docs.vllm.ai/en/latest/configuration/engine_args/ |
| Quantization | https://docs.vllm.ai/en/latest/features/quantization/index.html |
| Benchmark CLI (`vllm bench`) | https://docs.vllm.ai/en/latest/benchmarking/cli/ |
| vLLM paper (PagedAttention, SOSP 2023) | https://arxiv.org/abs/2309.06180 |
| Continuous batching explainer (Anyscale, by Cade Daniel et al.) | https://www.anyscale.com/blog/continuous-batching-llm-inference |

## Version observations (as of this refresh)

- Latest release: **v0.26.0** (published 2026-07-27). Release cadence is roughly
  monthly; docs publish `stable` and `latest` streams plus per-version archives.
- The official Docker image is `vllm/vllm-openai` on Docker Hub, with
  `vllm/vllm-openai-rocm` (AMD) and `vllm/vllm-openai-xpu` (Intel) variants;
  the XPU image is official starting with v0.26.0.
- Engine argument documentation moved to `configuration/engine_args`; engine
  args are also available as JSON-style CLI arguments (`--json-arg.key value`).
- Benchmarking is now a first-class CLI: `vllm bench serve` (online serving),
  `vllm bench throughput` (offline), plus latency-focused and multimodal
  variants, replacing the older `benchmark_serving.py`/`benchmark_throughput.py`
  scripts. The docs recommend the external GuideLLM framework for production
  capacity testing.
- `--prefix-caching` and `--performance-mode` (balanced/interactivity/throughput)
  are current flags on the `vllm serve` command line; older doc pages may still
  show earlier spellings.
- Default `--gpu-memory-utilization` is 0.92 (per instance). `--kv-cache-dtype`
  accepts `auto`, `bfloat16`, `float16`, `fp8` (`fp8_e4m3`), `int8_per_token_head`,
  `nvfp4`, and other hardware-specific values on CUDA 11.8+.
- vLLM 0.26.0 dependencies include Transformers 5.13, FlashInfer 0.6.14, and
  NIXL 1.3.1; GPU support spans NVIDIA (Ampere+ for most quantized kernels),
  AMD ROCm, and Intel XPU, with a CPU backend for testing.

## Refresh procedure

1. Re-check the sources above for a new release and read its release notes for
   changed or removed engine arguments and changed defaults.
2. Update the version observations that changed (defaults, flag names, endpoint
   behavior, hardware support).
3. Re-verify the SKILL.md scope keyword sweep and the routing links to
   `ml-engineering` and `llama-cpp` still resolve.
4. Re-run the bundled probe against a test server and confirm every check still
   parses: `scripts/vllm-health --url http://127.0.0.1:8000 --json`.

## Related skill sources

- `ml-engineering` owns serving methodology: engine selection, quantization
  decisions, deployment plans, and regression triage. Its references are the
  source for engine-spanning decisions; this skill covers vLLM operation itself.
- `llama-cpp` owns the llama.cpp stack (GGUF, llama-server). Do not duplicate
  its content here.
