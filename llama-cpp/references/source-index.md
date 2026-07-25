# Source index

Research checked 2026-07-25 against llama.cpp commit [`555881ebc8b0fc0402b30e09258a32a7bfd13c52`](https://github.com/ggml-org/llama.cpp/commit/555881ebc8b0fc0402b30e09258a32a7bfd13c52), immediately after release [`b10107`](https://github.com/ggml-org/llama.cpp/releases/tag/b10107). Links to `master`, generated command help, changelog issues, package repositories, and Hugging Face remain live sources and must be rechecked before relying on current flags, defaults, routes, or artifacts.

## Coverage matrix

| Requested dimension | Primary evidence | Skill reference | Status |
|---|---|---|---|
| Packages, releases, Docker, source builds | Install, build, Docker docs and releases | `installation-and-backends.md` | Covered with host-specific discovery |
| CPU, Metal, CUDA, HIP, Vulkan, SYCL | README backend table, build/backend guides, generated help | `installation-and-backends.md` | Covered; exact device support remains a task input |
| GGUF, provenance, conversion, quantization, imatrix | GGUF specification, quantize and imatrix docs, HF model cards | `models-gguf-and-memory.md` | Covered without a universal quant recommendation |
| Memory, context, cache, offload | Generated CLI/server help, model metadata, load logs, multi-GPU guide | `models-gguf-and-memory.md`, `performance-and-benchmarking.md` | Covered by measured procedure, not a fixed formula |
| CLI inference and chat templates | README quick start, generated CLI help, template and function docs | `inference-and-serving.md` | Covered with installed-help refresh gate |
| Server and OpenAI-compatible routes | Server README, tests, REST changelog | `inference-and-serving.md` | Covered; exact client contract must be tested |
| Structured output, embeddings, reranking, tools | Server README and function-calling docs | `inference-and-serving.md` | Covered with model/capability checks |
| Benchmarking and quality | llama-bench, server bench, perplexity docs | `performance-and-benchmarking.md` | Covered with matched-comparison contract |
| Multi-GPU | Current multi-GPU guide and generated help | `performance-and-benchmarking.md`, `troubleshooting.md` | Covered; experimental tensor support must be refreshed |
| Failure diagnosis | Build/server/multi-GPU docs, changelog, startup evidence | `troubleshooting.md` | Covered by symptom routing |

## Primary llama.cpp sources

| Area | Source | Claims used |
|---|---|---|
| Project scope, quick start, backends, tools | [README at reviewed commit](https://github.com/ggml-org/llama.cpp/blob/555881ebc8b0fc0402b30e09258a32a7bfd13c52/README.md) | Supported operating surfaces, model acquisition, primary binaries |
| Pre-built installation | [Install guide](https://github.com/ggml-org/llama.cpp/blob/555881ebc8b0fc0402b30e09258a32a7bfd13c52/docs/install.md) | Package-manager matrix and distributor boundaries |
| Source build and backends | [Build guide](https://github.com/ggml-org/llama.cpp/blob/555881ebc8b0fc0402b30e09258a32a7bfd13c52/docs/build.md) | CMake paths, backend selection, multi-backend/device discovery |
| Containers | [Docker guide](https://github.com/ggml-org/llama.cpp/blob/555881ebc8b0fc0402b30e09258a32a7bfd13c52/docs/docker.md) | Image families, host driver and passthrough requirements |
| CLI interface | [Generated CLI documentation](https://github.com/ggml-org/llama.cpp/blob/555881ebc8b0fc0402b30e09258a32a7bfd13c52/tools/cli/README.md) | Current flags and defaults; generated and volatile |
| Server interface | [Server documentation](https://github.com/ggml-org/llama.cpp/blob/555881ebc8b0fc0402b30e09258a32a7bfd13c52/tools/server/README.md) | Readiness, APIs, auth/TLS, capabilities, generated flags |
| REST changes | [REST API changelog](https://github.com/ggml-org/llama.cpp/issues/9291) | Upgrade-sensitive route, response, default, and environment changes |
| Multi-GPU | [Multi-GPU guide](https://github.com/ggml-org/llama.cpp/blob/555881ebc8b0fc0402b30e09258a32a7bfd13c52/docs/multi-gpu.md) | Split-mode status, fit/cache constraints, troubleshooting |
| Quantization | [Quantize guide](https://github.com/ggml-org/llama.cpp/blob/555881ebc8b0fc0402b30e09258a32a7bfd13c52/tools/quantize/README.md) | Conversion/quantization phases, requantization warning, example data |
| Importance matrices | [Imatrix guide](https://github.com/ggml-org/llama.cpp/blob/555881ebc8b0fc0402b30e09258a32a7bfd13c52/tools/imatrix/README.md) | Calibration inputs, outputs, statistics, quantization use |
| Model performance | [llama-bench guide](https://github.com/ggml-org/llama.cpp/blob/555881ebc8b0fc0402b30e09258a32a7bfd13c52/tools/llama-bench/README.md) | pp/tg/pg methodology, repetitions, structured outputs, exclusions |
| Service performance | [Server benchmark guide](https://github.com/ggml-org/llama.cpp/blob/555881ebc8b0fc0402b30e09258a32a7bfd13c52/tools/server/bench/README.md) | Concurrent request benchmark and client/server metrics |
| Quant quality | [Perplexity guide](https://github.com/ggml-org/llama.cpp/blob/555881ebc8b0fc0402b30e09258a32a7bfd13c52/tools/perplexity/README.md) | Same-model comparison, uncertainty, KL, cross-model limits |
| Templates and tools | [Function-calling guide](https://github.com/ggml-org/llama.cpp/blob/555881ebc8b0fc0402b30e09258a32a7bfd13c52/docs/function-calling.md) | Template/handler coupling, props/log verification, cache-quality warning |
| Template provenance | [Template maintenance](https://github.com/ggml-org/llama.cpp/blob/555881ebc8b0fc0402b30e09258a32a7bfd13c52/models/templates/README.md) | Model-source template acquisition |

## Format and model provenance sources

| Area | Source | Claims used |
|---|---|---|
| GGUF format and metadata | [GGUF specification](https://github.com/ggml-org/ggml/blob/master/docs/gguf.md) | Extensibility, mmap, architecture, context, license/source/base-model and template metadata |
| Model cards | [Hugging Face model cards](https://huggingface.co/docs/hub/model-cards) | License, base-model lineage, intended use, limitations, datasets, evaluation |
| Reproducible downloads | [Hugging Face download guide](https://huggingface.co/docs/huggingface_hub/guides/download) | Exact revisions, file filtering, caching, CLI dry runs |

## Source evaluation

The operational claims above are primarily Tier 1 official documentation, generated help, specifications, tests, and project changelogs. Upstream examples establish supported command shapes, not performance guarantees for other hardware or models. No local llama.cpp binary or model was available during skill authoring, so commands were source-verified but not represented as locally executed runtime evidence.

## Refresh rules

Recheck the installed help and upstream sources when any of these change:

- llama.cpp build/release, binary name, package, or container image;
- backend SDK, driver, GPU architecture, build target, or device topology;
- model revision, GGUF metadata/version, quantization, sidecar, template, or license;
- REST route, stream/error schema, environment variable, authentication, CORS, or default bind behavior;
- context, cache, fit, batch, offload, split-mode, or speculative-decoding default;
- benchmark tool output/schema or measurement boundary.

Always recheck external-exposure and built-in-tool security options immediately before enabling them.
