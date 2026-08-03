# vLLM — Inference-Serving Skill

Operate, configure, benchmark, and troubleshoot vLLM inference servers: Docker and Kubernetes deployment, quantization-aware model configuration (tensor parallelism, KV cache), the OpenAI-compatible API surface, throughput/latency benchmarking, continuous batching tuning, GPU operation, and upgrade/rollback.

## Why Install This Skill

Your agent can run a vLLM deployment instead of guessing. Teams that self-serve open models in production need someone (or something) that knows how to start a `vllm serve` with the right flags, size the model and its KV cache for the GPUs at hand, confirm the OpenAI-compatible endpoints actually work, measure throughput and latency with evidence that comparisons mean something, tune continuous batching one knob at a time, and upgrade or roll back without burning the deployment.

This skill ships that operating knowledge plus two fillable templates — a serving configuration record (so every deployment is reproducible) and a benchmark run record (so every performance claim is comparable) — and a read-only `vllm-health` probe that checks a running server's health, version, models, load, and metrics over HTTP without changing anything. The references are distilled from the official vLLM documentation with dated sources. Serving strategy and engine-selection methodology deliberately route up to `ml-engineering`; the llama.cpp stack routes to `llama-cpp`; this skill owns the day-to-day operation of vLLM itself.

## What You Get

| Directory | Purpose |
|---|---|
| `SKILL.md` | Agent-facing operating loop, mutation gates, and verification boundaries |
| `references/` | Seven dated, source-indexed references: source index, deployment, model configuration, OpenAI API, benchmarking, batching/tuning, GPU ops and lifecycle |
| `templates/serving-config.md` | Fillable record of every serving argument, model revision, and environment — the rollback unit |
| `templates/benchmark-run-record.md` | Fillable record that makes throughput/latency evidence comparable across runs |
| `scripts/vllm-health` | Read-only probe: health, version, models, load, and metrics; stdlib-only, `--json`, `--help` without a server |
| `tests/` | Deterministic tests against a local stub HTTP server, including the read-only contract |
| `evals/evals.json` | Six output-quality evaluation cases for agent runs |

## Quick Start

```bash
# Help works with no vLLM server
scripts/vllm-health --help

# Probe a running server, machine-readable
scripts/vllm-health --url http://127.0.0.1:8000 --json

# Targeted checks
scripts/vllm-health --check health --check models --json

# Record what you are about to run before you run it
# (fill in vllm/templates/serving-config.md), then:
docker run --runtime nvidia --gpus all \
  -v ~/.cache/huggingface:/root/.cache/huggingface \
  --env "HF_TOKEN=$HF_TOKEN" \
  -p 8000:8000 --ipc=host \
  vllm/vllm-openai:v0.26.0 \
  --model <model-name> --served-model-name <api-name> --max-model-len <len>

# Benchmark serving throughput/latency once the server is ready
vllm bench serve --backend vllm --model <model-name> \
  --endpoint /v1/completions --dataset-name custom \
  --dataset-path prompts.jsonl --num-prompts 100 --request-rate inf
```

The `vllm-health` script uses only Python's standard library and issues GET requests only. Exit codes: 0 all checks passed, 1 issues found or a fatal error, 2 usage error, 124 timeout. Benchmark output includes request throughput (req/s), output token throughput (tok/s), and TTFT/TPOT/ITL percentiles — record them in `templates/benchmark-run-record.md`.

## Triggers

Load this skill for vLLM operations: deploying or updating a `vllm serve` server (bare, Docker, or Kubernetes), choosing serving flags (`--quantization`, `--tensor-parallel-size`, `--max-model-len`, `--kv-cache-dtype`, `--gpu-memory-utilization`), wiring or debugging the OpenAI-compatible API surface (`/v1/chat/completions`, `/v1/completions`, `/v1/models`, `/health`, tool calling, chat templates), measuring serving throughput or latency (`vllm bench serve`/`bench throughput`), tuning continuous batching, running or diagnosing GPUs under a vLLM workload, or planning a vLLM upgrade or rollback. Do not load it for model training or fine-tuning (that's `ml-engineering`), for the llama.cpp stack (that's `llama-cpp`), or for generic Kubernetes/Docker administration (that's `kubernetes`/`docker-compose`).

## Requirements

- A vLLM release: the `vllm/vllm-openai` Docker image (NVIDIA CUDA, AMD ROCm, or Intel XPU variants) or `pip install vllm==<pinned-version>`.
- An accelerator with the matching driver (NVIDIA with the NVIDIA Container Toolkit for Docker, or the platform equivalent), or a supported CPU build for testing.
- Hugging Face access to the model: a mounted `~/.cache/huggingface` and an `HF_TOKEN` for gated models.
- Python 3.9+ for the `vllm-health` script (`--help` needs nothing else); live probes need HTTP(S) access to the running server.
