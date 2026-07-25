---
name: llama-cpp
description: >-
  Operate, configure, benchmark, and troubleshoot llama.cpp across CPU, Metal, CUDA, HIP/ROCm, Vulkan, SYCL, and hybrid or multi-GPU systems. Use when installing or building llama.cpp, selecting or inspecting GGUF models, running llama-cli, serving an OpenAI-compatible API with llama-server, tuning memory and performance, or diagnosing backend, context, template, and API failures. Do not use for model training or fine-tuning, general inference-framework selection, llama-cpp-python or other bindings, LlamaIndex, Ollama, or LM Studio operation.
license: MIT
compatibility: Requires a supported llama.cpp binary or a build environment. Model use requires a compatible GGUF file and sufficient disk and memory; accelerator paths require the matching driver and SDK.
metadata:
  source: https://github.com/ggml-org/llama.cpp
  source_index: references/source-index.md
  research_checked: "2026-07-25"
---

# llama.cpp Operations

Treat every launch recipe as a hypothesis about a specific build, model, host, and workload. Discover capabilities from the installed binary, inspect the model and startup logs, then measure the requested boundary.

## Operating contract

1. Record the exact llama.cpp version or commit, installation method, OS and architecture, CPU and RAM, accelerator and memory, driver/toolkit, available devices, model provenance and quantization, intended context, concurrency, and workload.
2. Read the installed command's `--help` before using a flag from documentation. llama.cpp flags, defaults, binary names, and REST behavior change frequently.
3. Confirm the target, scope, and rollback path before acting. Read-only discovery may proceed without confirmation.
4. Verify the backend from `--list-devices` and model-load logs. A successful build or an accepted GPU flag does not prove acceleration is active.
5. Start with a bounded CLI smoke test on loopback or local input. Establish a measured baseline before changing threads, batches, context, cache types, offload, or split mode.
6. Call work complete only at the requested boundary: binary, model load, generated output, API response, benchmark comparison, or diagnosed failure with evidence.

## When not to use

Use `ml-engineering` for model training, fine-tuning, broad quantization methodology, evaluation design, or choosing among llama.cpp, vLLM, TGI, and other engines. Use the relevant product skill for Ollama, LM Studio, or LlamaIndex. Use binding-specific documentation for `llama-cpp-python`, node-llama-cpp, or other language wrappers.

## Read-only preflight

Run only commands that exist in the installed build:

```sh
llama-cli --version
llama-cli --help
llama-cli --list-devices
llama-server --version
llama-server --help
llama-bench --help
```

Also inspect host memory and accelerator state with native OS/vendor tools. Record results in [the operation record](templates/operation-record.md). If no binary exists, choose an installation path only after reading [installation and backends](references/installation-and-backends.md).

## Route the task

| Need | Read first |
|---|---|
| Install, build, choose CPU/Metal/CUDA/HIP/Vulkan/SYCL, Docker, or prove backend use | [installation and backends](references/installation-and-backends.md) |
| Acquire, convert, inspect, license-check, quantize, or fit a GGUF model | [models, GGUF, and memory](references/models-gguf-and-memory.md) |
| Run `llama-cli`, expose `llama-server`, call compatible APIs, use templates, structured output, embeddings, reranking, or tools | [inference and serving](references/inference-and-serving.md) |
| Tune threads, batches, context, cache, offload, concurrency, or multi-GPU and compare results | [performance and benchmarking](references/performance-and-benchmarking.md) |
| Diagnose load, backend, OOM, speed, context, template, output, or API failures | [troubleshooting](references/troubleshooting.md) |
| Check the evidence, research date, upstream revision, or refresh rule behind a claim | [source index](references/source-index.md) |

## Safe workflow

### 1. Select and verify the installation

Prefer a supported package or release binary when its compiled backend matches the target. Build from a pinned revision when backend options, portability, or reproducibility require it. Use Docker when host isolation is useful and device passthrough is understood. After installation, capture version, help, device listing, and a model-load log before claiming success.

### 2. Select and inspect the model

Accept a user-specified local GGUF path or Hugging Face repository. Before downloading, record the repository, revision, file, size, model card, license, base-model lineage, and quantizer when available. Inspect GGUF metadata and model-load output for architecture, quantization, context, tokenizer, chat template, and sidecars. Plan capacity from actual file size plus KV cache, context, batch/concurrency, compute buffers, and backend overhead; parameter count alone is insufficient.

Do not call one quantization universally best. Start from workload quality and capacity constraints, avoid requantizing an already quantized model when a higher-precision source is available, and compare candidate quants with the same task-quality and performance workload.

### 3. Prove local inference

Use a short, fixed prompt and bounded token count. Record the exact command, seed or sampling settings, startup log, output, timings, and whether the expected backend loaded. If the model has a chat template, test the template path required by the intended workload rather than treating plain completion as chat proof.

### 4. Prove serving

Bind to `127.0.0.1` for the first launch. Wait for `/health` to report ready, query `/v1/models`, then make a representative request using a reported model identifier. A listening process or HTTP 200 from a shallow endpoint is not inference proof. External exposure requires an explicit decision about bind address, API keys, TLS or reverse proxy, firewall, CORS, rate limits, logging, and whether experimental built-in tools are disabled.

### 5. Tune one dimension at a time

Preserve a baseline before changing context size, generation and batch threads, logical or physical batch size, GPU layers, KV cache type/offload, Flash Attention, parallel slots, or multi-GPU split. Use `llama-bench` for prompt-processing and token-generation comparisons, and an end-to-end client or server benchmark for TTFT and request latency. Record each comparison in [the benchmark template](templates/benchmark-comparison.md).

## Hard boundaries

- Do not infer accelerator use from the command line alone; require device and load-log evidence.
- Do not expose an unauthenticated server beyond loopback by accident. Authentication is not a substitute for network and TLS controls.
- Do not enable `llama-server` built-in filesystem or shell tools in an untrusted environment.
- Do not override a chat template until model metadata, the original model card, and rendered behavior have been inspected.
- Do not compare benchmark numbers from different models, quants, commits, backends, contexts, batches, thermal states, or workloads as if only one variable changed.
- Do not treat `llama-bench` tokens per second as TTFT; its measurements exclude tokenization and sampling.
- Do not claim a larger configured context preserves quality unless the model and scaling behavior support it and the workload was evaluated.

## Exit criteria

The task is complete when the requested boundary is evidenced: the expected binary and backend are observed; the selected model's provenance and fit are recorded; a bounded prompt returns usable output; a server reaches readiness and completes a representative API request; a tuning change beats or preserves the declared metrics under matched conditions; or a failure is reduced to a supported cause with a safe next action. List any stronger boundary that was not tested.
