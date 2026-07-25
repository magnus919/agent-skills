# llama.cpp Skill

Operate llama.cpp from hardware discovery through verified local inference, API serving, benchmarking, and failure diagnosis.

## Why Install This Skill

llama.cpp can run on laptops, CPU servers, and heterogeneous accelerator systems, but a command that starts is not necessarily using the intended backend or fitting the intended workload safely. Build options, GPU offload, GGUF quantization, context sizing, chat templates, and server behavior interact in ways that generic local-LLM advice does not capture.

This skill gives your agent a discovery-first operating procedure. It checks the actual binary, host, model metadata, startup logs, and workload before selecting a launch configuration, then verifies inference or serving at the requested boundary. It also keeps fast-moving flags and API details tied to dated upstream sources instead of presenting one launch command as timeless.

## What You Get

| Resource | Purpose |
|---|---|
| `SKILL.md` | Core operating contract, task routing, safety boundaries, and completion criteria |
| `references/installation-and-backends.md` | Package, release, Docker, source-build, and backend verification workflows |
| `references/models-gguf-and-memory.md` | Model provenance, GGUF inspection, quantization, context, and capacity planning |
| `references/inference-and-serving.md` | CLI smoke tests, server readiness, APIs, templates, structured output, embeddings, and reranking |
| `references/performance-and-benchmarking.md` | Reproducible tuning and matched benchmark comparisons |
| `references/troubleshooting.md` | Evidence-led diagnosis by symptom |
| `references/source-index.md` | Dated primary sources and refresh rules |
| `templates/` | Reusable operation and benchmark evidence records |
| `evals/evals.json` | Output-quality cases for installation, fit, serving, performance, templates, and multi-GPU diagnosis |
| `EVIDENCE-LEDGER.md` | Auditable implementation, verification, and known-gap record for this skill release |

## Quick Start

With a current llama.cpp installation and a compatible local GGUF model:

```sh
llama-cli --version
llama-cli --list-devices
llama-cli -m /path/to/model.gguf -p "Reply with exactly: llama.cpp ready" -n 16
```

Inspect the startup log and generated response. Before relying on a GPU, server, long context, or downloaded model, follow the corresponding workflow in `SKILL.md`.

## Triggers

Use this skill for llama.cpp installation and builds, CMake backend selection, GGUF acquisition and inspection, `llama-cli`, `llama-server`, OpenAI-compatible endpoints, chat templates, GPU offload, KV cache and context sizing, `llama-bench`, multi-GPU operation, or llama.cpp-specific troubleshooting.

Do not use it for training or fine-tuning models, comparing inference frameworks generally, operating LlamaIndex/Ollama/LM Studio, or configuring language bindings such as `llama-cpp-python`.

## Requirements

Operations require a llama.cpp binary or a CMake/C++ build environment. Model runs require a supported GGUF model, adequate disk and RAM, and optional accelerator drivers/toolkits. Hugging Face acquisition requires network access and possibly an access token for gated repositories. Server verification uses an HTTP client such as `curl`.
