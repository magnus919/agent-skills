# Quantization selection and measured tradeoffs

Research checked 2026-10-12. Low-bit GGUF/NVFP4 execution **not run**. Our existing
GPU parity result is F16 GGUF only. Sources:
[Dynamic GGUF](https://unsloth.ai/docs/basics/dynamic-3.0-ggufs),
[NVFP4](https://unsloth.ai/docs/basics/dynamic-3.0-ggufs/nvfp4) and the selected
model card/runtime documentation. Vendor benchmark gains are not local results.

## Keep the formats separate

| Path | Meaning | Verify |
|---|---|---|
| BF16/FP16 | Unquantized weight baseline; can run locally if it fits | Model/backend and memory |
| bitsandbytes 4-bit QLoRA | Adapter training on a quantized backbone | Training kernels and all training-state memory |
| GGUF Q4/Q8 or Unsloth UD variants | Quantized inference artifact with model-specific tensor treatment | Exact GGUF file, runtime/build and architecture support |
| Dynamic NVFP4 | Separate Blackwell-oriented W4A4 inference path, retaining selected tensors at higher precision | Exact checkpoint, supported vLLM/SGLang stack and GPU kernels |

`UD-*` is an artifact variant, not a generic on/off flag in `FastLanguageModel`.
Do not treat a standard Q4_K_M export as an Unsloth Dynamic artifact. Mixed tensor
precision/calibration and architecture matter, not just a filename's bit count.
Quantization is optional for local inference; it is not required when a higher
precision model fits. GGUF and NVFP4 are not interchangeable files or loaders.

The RTX 5070 Ti is Blackwell, making NVFP4 a documented research candidate, not a
validated path. Published throughput figures involve larger hardware/concurrency;
check per-request decode latency and complete memory usage before extrapolating.
The documented 27B NVFP4 example asks for more VRAM than this host has. Do not
choose it from a Blackwell support label alone or install a second stack globally.

## Compare candidates against an immutable baseline

Pin the parent model and each quantized artifact revision/file hash, tokenizer,
chat template, runtime, prompts, seed and decoding settings. Hold task semantics,
context budget and output allowance constant. Reserve memory for context/KV,
workspace and auxiliary components; download size is not peak VRAM.

Measure load/cold/warm latency, generation throughput, peak VRAM/RAM, actual layer
placement, termination/repetition, task score and tool-call success. For lossy
quants, use predeclared allowed score degradation and critical-failure thresholds;
exact token equality may no longer be appropriate. Keep the F16 conversion-parity
check separate from the quantization quality comparison. For numeric decision
outputs compare probabilities/calibration and preserve the learned head.

The Dynamic guide distinguishes next-token top-1 agreement from longer generation
behavior and warns that very low-bit variants can fail tool use or loop. Such
agreement is not task accuracy. Test complete bounded tool tasks and long prompts
on an independent evaluation set, disjoint from quantization calibration data.
Do not generalize a reported percentage to all models or all workloads.

Deliver a comparison table and candidate artifacts only after real target-runtime
loads. When execution is unavailable, deliver the pinned plan with each stage
marked not run. No automatic CPU fallback, endpoint exposure or upload is part
of quantization selection.
