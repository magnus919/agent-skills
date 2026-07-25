# Models, GGUF, and memory

Use this reference when acquiring, converting, inspecting, quantizing, or deciding whether a model fits the target workload.

## Model acquisition contract

Before download or conversion, record:

- original model repository and exact revision;
- GGUF repository, file, shard set, quantization, and quantizer identity;
- base-model and fine-tune lineage;
- model card, intended use, known limitations, and license terms;
- file sizes, available disk, cache location, and expected sidecars such as multimodal projectors;
- whether the repository is gated and how credentials will be supplied without logging them.

GGUF metadata can carry license, source repository, base-model lineage, quantizer, architecture, context, tokenizer, and chat-template data, but these fields are not guaranteed to be complete. Reconcile metadata with the model card and original source. Missing license or provenance is a decision blocker, not permission to guess.

For reproducible Hugging Face acquisition, prefer an exact revision and file. Use the current Hugging Face CLI dry run to inspect download size before fetching:

```sh
hf download <repo> <file> --revision <full-commit> --dry-run
hf download <repo> <file> --revision <full-commit>
```

The llama.cpp `-hf` path is useful for interactive acquisition and shared cache use, but record the resolved repository revision and file if the result must be reproducible. Keep access tokens in the supported environment/credential mechanism, never in committed commands.

## Inspect before launch

Use a current GGUF inspection tool from the upstream `gguf-py` package or a bounded llama.cpp model load. Capture at least:

- GGUF version and tensor types;
- architecture, parameter/size label, block count, and expert topology;
- trained context and RoPE/scaling metadata;
- tokenizer and special-token metadata;
- embedded chat template and tool-use template, if present;
- quantization type/version and quantizer/source fields;
- shard and sidecar requirements;
- model file hash for a locally controlled artifact.

Do not edit metadata to hide incompatibility. An override is an experiment that must preserve the original file and prove output behavior.

## Capacity planning

Model file size is the weight-floor estimate, not total runtime memory. Budget separately for:

1. mapped or loaded model weights and any duplicated host/device placement;
2. KV cache, driven by architecture, context, parallel sequences, cache types, and offload;
3. prompt and micro-batch compute buffers;
4. backend/runtime, driver, graph, and allocator overhead;
5. multimodal projectors, adapters, draft models, or multiple loaded models;
6. safety margin for the OS and other workloads.

Use GGUF metadata and startup allocation logs for the exact model. Parameter-count formulas are rough screening tools because MoE topology, tensor mixtures, metadata, cache architecture, and backend placement differ. For `llama-server`, concurrency can multiply context/cache pressure. Reduce context or parallel slots before sacrificing full accelerator offload when that matches the service objective, then measure the effect.

Current llama.cpp may auto-fit unset arguments and report resolved settings. Treat that as a starting proposal, not a guarantee that sustained workload, latency, or quality targets are met.

## Choose a quantization

Start with constraints, not a universal recommendation:

- minimum task-quality threshold;
- model and cache capacity on the target host;
- prompt-processing and generation performance;
- architecture/backend kernel support;
- context and concurrency needs;
- whether an importance matrix exists for representative data.

Compare candidate quants against a higher-precision baseline using the same task-specific prompts and, where useful, perplexity or KL-divergence tooling. Perplexity is most meaningful for comparing variants of the same model/tokenizer; it is not a universal cross-model quality score.

## Conversion and quantization

Upstream defines two separate phases:

1. convert a supported source model to a high-quality GGUF;
2. quantize that GGUF with `llama-quantize`.

Use the conversion script and requirements from the same pinned llama.cpp revision. Validate representative outputs against the source model before quantization. Preserve the high-precision GGUF and conversion record.

Avoid requantizing an already quantized input when a higher-precision source exists; upstream warns this can severely reduce quality. For importance-matrix use, select representative calibration text, record its provenance, generate the matrix with `llama-imatrix`, inspect its statistics, and compare output quality with and without it. An importance matrix is evidence for a particular model and data distribution, not a universal quality certificate.

## Model acceptance gate

Accept a model for the requested use only when:

- provenance and license are understood;
- all required shards and sidecars are present;
- architecture and tensor types load in the chosen llama.cpp revision;
- capacity includes context, concurrency, and margin;
- the intended chat/template or completion behavior passes a representative smoke test;
- the selected quantization meets the declared quality and performance thresholds.
