# ML Model Quantization & Inference Serving — Reference Manual

> **Purpose:** Engineering methodology reference for production ML serving. Covers quantization approaches, calibration strategies, quality assessment, mixed precision, KV cache optimization, and inference serving architectures.
>
> **Serving methodology reviewed:** 2026-11-08. Quantization background is not a current compatibility matrix; verify the pinned implementation before use.

---

## Table of Contents

1. [Quantization Fundamentals](#1-quantization-fundamentals)
2. [Quantization Approaches Compared](#2-quantization-approaches-compared)
   - 2.1 GGUF
   - 2.2 GPTQ
   - 2.3 AWQ
   - 2.4 bitsandbytes NF4
   - 2.5 EXL2
   - 2.6 HQQ
   - 2.7 Comparison Table
3. [Calibration Data Strategies](#3-calibration-data-strategies)
4. [Quality Impact Assessment](#4-quality-impact-assessment)
5. [Mixed Precision Patterns](#5-mixed-precision-patterns)
6. [KV Cache Quantization](#6-kv-cache-quantization)
7. [Quantization Workflow](#7-quantization-workflow)
8. [Inference Serving Architecture](#8-inference-serving-architecture)
9. [Production Considerations](#9-production-considerations)
10. [References & Further Reading](#10-references--further-reading)

---

## 1. Quantization Fundamentals

**Quantization** reduces the numerical precision of model weights (and optionally activations / KV cache) from full-precision (FP32, BF16) to lower-bit representations (INT8, INT4, FP8, NF4). This shrinks memory footprint, reduces memory bandwidth pressure, and accelerates inference — especially on bandwidth-bound decode steps.

### Key concepts

| Concept | Description |
|---|---|
| **Weight quantization** | Map each weight tensor's values from a high-precision range into a low-bit grid. Reduces model size by 2-4x at common bit widths. |
| **Activation quantization** | Quantize intermediate activations at runtime. Harder than weight quantization due to dynamic range variation. Common in INT8 pipelines (e.g., TensorRT). |
| **KV cache quantization** | Quantize the key-value cache during autoregressive generation. Critical for long-context serving where KV cache dominates GPU memory. |
| **Symmetric vs. asymmetric** | Symmetric: zero point = 0, range is [-max, max]. Asymmetric: zero point can shift. Asymmetric generally preserves more info for non-normalized distributions. |
| **Per-tensor vs. per-channel (per-group)** | Finer granularity (per-channel or per-group) captures outlier distributions better at the cost of storing more scale/zero-point metadata. |
| **Post-training quantization (PTQ)** | Quantize after training. Dominant paradigm for LLMs given cost of training. |
| **Quantization-aware training (QAT)** | Simulate quantization during training (e.g., FakeQuant ops). More accurate but expensive. Used in some production pipelines (e.g., NVIDIA TensorRT). |

### Why quantize LLMs?

- **Memory:** Nominal weights for 70 billion parameters occupy ~140 GB at FP16 or ~35 GB at INT4, before metadata and other tensors. Deployment fit also requires the cache, buffers and overhead budget below.
- **Throughput:** Lower-precision weights reduce memory bandwidth consumption, which is the primary bottleneck for autoregressive token generation (memory-bound, not compute-bound).
- **Cost:** Enables deployment on cheaper/consumer hardware (RTX 4090, Apple Silicon unified memory, CPU-only).

---

## 2. Quantization Approaches Compared

### 2.1 GGUF

**Type:** File format + quantization scheme  
**Ecosystem:** llama.cpp, Ollama, LM Studio  
**Bit widths:** Q2_K through Q8_0, plus Q4_K_M, Q5_K_M, Q6_K, etc.

GGUF is a model container format used by ggml-based runtimes, not an executable program or a synonym for every quantization method. It stores tensor data and metadata, including tokenizer information; models may also be split across files. Some variants use **k-quant** mixed tensor precision:

- **Q4_K_M** — recommended sweet spot. Mixture of 4-bit and 6-bit quantization across layers. ~4.5 bits/weight effective.
- **Q5_K_M** — higher quality, ~5.5 bits/weight effective.
- **Q8_0** — near-lossless 8-bit, ~8.5 GB for a 7B model.
- **Q2_K** — aggressive 2-3 bit mix, significant quality loss.

**Key features:**
- Supports CPU inference natively (no GPU required for modest models).
- Can offload layers to GPU via `--n-gpu-layers`.
- Single-file distribution simplifies deployment.
- Supports a wide range of architectures (Llama, Mistral, Falcon, Gemma, etc.).
- **Imatrix** (importance matrix) quantization: weights are quantized with per-layer importance scores, improving quality at a given bit rate.

**Strengths:** A common distribution format for local/offline inference with llama.cpp across CPU and supported GPU backends.

**Compatibility:** Check the exact loader, model architecture and version. The [current vLLM GGUF documentation](https://docs.vllm.ai/en/latest/features/quantization/gguf/) describes experimental, under-optimized support through an out-of-tree plugin. This is not proof that every older vLLM version lacks GGUF, nor a universal speed ranking against AWQ/GPTQ. See the [source record](local-serving-sources.md).

---

### 2.2 GPTQ

**Type:** Post-training quantization (weight only)  
**Ecosystem:** AutoGPTQ, HuggingFace optimum, vLLM, TGI  
**Bit widths:** 2-8 bits (most common: 4-bit), supports group size 32/64/128

GPTQ (GPT Post-Training Quantization) uses approximate second-order optimization (Hessian-based) to find weight quantizations that minimize output error. It was the first widely adopted 4-bit LLM quantization method.

**How it works:**
1. Sample a calibration dataset (typically 128 sequences from the training distribution).
2. Compute the approximate Hessian (Fisher information) for each weight column.
3. Quantize weights column-by-column, using the Hessian to prioritize preserving important weights.
4. Update remaining unquantized weights to compensate for quantization error (optimal brain quantization / OBC family).

**Key parameters:**
- **Group size** (g128, g64, g32): Smaller groups = higher accuracy but more scale storage overhead. g128 is common. g64 preferred for quality.
- **Desc_act / act_order** (activation order): When True, reorders columns by activation magnitude. Increases accuracy significantly but reduces speed in older implementations. vLLM's Marlin kernel makes desc_act fast.

**Strengths:** Strong quality at 4-bit, mature ecosystem, widely supported in serving frameworks.

**Weaknesses:** Calibration dataset required (cannot quantize a model from scratch without data). Quantization is slower than AWQ or NF4 due to Hessian computation.

---

### 2.3 AWQ

**Type:** Post-training quantization (weight only)  
**Ecosystem:** AutoAWQ, vLLM, TGI, TensorRT-LLM  
**Bit widths:** 4-bit (most common), also 2-bit, 3-bit variants

AWQ (Activation-Aware Weight Quantization) observes that a small fraction (~1%) of weight channels are "salient" — they handle large activations and are disproportionately important. AWQ protects these channels by scaling them up before quantization, then scaling the output down.

**How it works:**
1. Run a few calibration samples to collect activation statistics.
2. Identify salient channels (those with large activation magnitudes).
3. Apply per-channel scaling factors to redistribute quantization error from salient → non-salient channels.
4. Quantize with simple round-to-nearest.

**Key advantages:**
- **No group size dependency:** AWQ INT4 often matches GPTQ g128 quality without requiring groups, simplifying kernel implementation.
- **Very fast quantization:** Minutes instead of hours. No Hessian computation needed.
- **Excellent GPU kernel support:** Marlin kernel (for GPTQ-compatible AWQ) and AWQ-specific kernels in vLLM achieve near-peak hardware utilization.
- **Good hardware compatibility:** Works well on NVIDIA, AMD, and Apple Silicon via MLX.

**Strengths:** Best quality-to-speed tradeoff at 4-bit, fastest quantize time, strong production support in vLLM.

**Weaknesses:** Primarily designed for 4-bit (less flexible than GGUF's range of bit widths). Requires activation statistics → needs calibration data.

---

### 2.4 bitsandbytes NF4

**Type:** Post-training quantization (weight only)  
**Ecosystem:** HuggingFace `bitsandbytes`, `transformers`, PEFT/LoRA  
**Bit widths:** 4-bit (NF4), 8-bit (INT8)

Bitsandbytes (BnB) is a library from Tim Dettmers that implements efficient GPU quantization kernels. Its 4-bit variant uses **NormalFloat (NF4)** — a non-uniform quantization grid that assumes normally distributed weights.

**Key concepts:**
- **NF4:** A 4-bit data type with 16 levels, non-uniformly spaced to match the cumulative distribution function (CDF) of a normal distribution. This gives higher resolution near zero where most weight values cluster.
- **Double quantization:** Quantizes the quantization constants (scale/offset) themselves to save additional memory. Reduces the 4-bit overhead from ~0.5 bits/weight to ~0.127 bits/weight.
- **QLoRA:** Fine-tune quantized models with LoRA adapters. The base model stays in NF4; only the LoRA parameters are updated in FP16.

**Key features:**
- Native `transformers` integration via `BitsAndBytesConfig` — load any model in 4-bit with a single config object.
- Best for fine-tuning (QLoRA) and rapid prototyping.
- No calibration data needed — quantization is "on the fly" at load time.

**Strengths:** Simplest API, no calibration required, excellent for fine-tuning, HuggingFace-native.

**Weaknesses:** Slower inference than AWQ/GPTQ (dequantization at every forward pass). Kernels are less optimized for serving throughput. Not suitable for high-throughput production serving on its own.

---

### 2.5 EXL2

**Type:** Post-training quantization  
**Ecosystem:** ExLlamaV2  
**Bit widths:** Mixed 2-8 bits per layer

EXL2 is the quantization format for ExLlamaV2, a high-throughput inference engine. It supports mixed-precision within a single model — different layers can use different bit widths.

**Key features:**
- Fine-grained per-layer bit allocation for optimal quality/size tradeoffs.
- GPU kernels intended for local inference; measure single-request and concurrent performance on the target workload.
- Less widely supported than GGUF/GPTQ/AWQ but excellent for local GPU use.

**Strengths:** Flexible per-layer bit allocation and a local-GPU-oriented runtime; speed requires matched measurement.

**Weaknesses:** Smaller ecosystem, primarily desktop/local use. Not widely supported in production serving frameworks.

---

### 2.6 HQQ

**Type:** Post-training quantization  
**Ecosystem:** HuggingFace, independent  
**Bit widths:** 1-8 bits

HQQ (Half-Quadratic Quantization) uses a half-quadratic splitting approach to compute optimal quantization. It's notable for being extremely fast to quantize (no calibration data, no Hessian) and supporting very low bit widths (2-bit, 3-bit).

**Strengths:** Fastest PTQ (no data needed), supports 1-3 bits, good quality at lower bits.

**Weaknesses:** Needs `torch.compile` for reasonable inference speed; otherwise dequantization overhead is high. Less mature ecosystem.

---

### 2.7 Quantization Method Comparison Table

| Property | GGUF (Q4_K_M) | GPTQ (g128) | AWQ | BnB NF4 | EXL2 | HQQ |
|---|---|---|---|---|---|---|
| **Effective bits/weight** | ~4.5 | ~4.125 | ~4.0 | ~4.127 | Variable | 1-8 |
| **File format** | Single .gguf | HF safetensors | HF safetensors | HF safetensors | Custom | HF safetensors |
| **Calibration data req.** | No* | Yes (128 seq) | Yes (128 seq) | No | Yes | No |
| **Quantize speed** | Fast** | Slow (hrs) | Fast (min) | Instant (load) | Moderate | Very fast |
| **GPU inference speed** | Measure pinned backend | Measure pinned kernel | Measure pinned kernel | Measure pinned kernel | Measure pinned kernel | Measure pinned kernel |
| **CPU inference** | llama.cpp CPU | Verify runtime | Verify runtime | Verify runtime | Verify runtime | Verify runtime |
| **Apple Silicon** | llama.cpp Metal | Verify conversion/runtime | Verify conversion/runtime | Verify runtime | Verify runtime | Verify runtime |
| **Serving support** | llama.cpp; vLLM version/plugin dependent | vLLM, TGI | vLLM, TGI, TRT-LLM | Limited | ExLlamaV2 | Limited |
| **Fine-tuning support** | No | No | No | Yes (QLoRA) | No | Possible |
| **Ecosystem maturity** | Very high | High | High | Very high | Moderate | Low |
| **Typical PPL increase (7B)** | +0.15 | +0.10 | +0.10 | +0.20 | +0.10 | +0.12 |

\* GGUF quantization typically does not use calibration data; imatrix quantization does.  
\** Quantization is an explicit step via `llama-quantize` or similar tools (not on-the-fly).

---

## 3. Calibration Data Strategies

Some quantization methods (GPTQ, AWQ, EXL2, imatrix) require a **calibration dataset** — a small set of representative text samples used to compute activation statistics or Hessian information.

### Recommended calibration datasets

| Dataset | Typical Size | Use Case |
|---|---|---|
| **Wikitext-2** | 128 seq × 2048 tokens | Standard benchmark, general text |
| **C4 (Colossal Clean Crawled Corpus)** | 128-256 seq | General web text, diverse |
| **Pile** | 128-256 seq | General, diverse (books, code, academic) |
| **Custom task-specific** | 128-512 seq | Domain adaptation (medical, legal, code) |
| **Random from training data** | 128 seq | Best if available (closest to training distribution) |

### Best practices

1. **Size:** 128-256 sequences of 2048 tokens is typically sufficient. More calibration data has diminishing returns and can even harm quality (overfitting the calibration set).
2. **Diversity:** Calibration data should broadly match the model's training distribution. A model trained on code + text benefits from a calibration mix of both.
3. **Sequences vs. random tokens:** Always use natural text sequences, not random tokens. Random tokens produce meaningless activation statistics.
4. **Avoid duplication:** Deduplicate calibration data. Repeated samples can skew Hessian estimates.
5. **Prompt-like structure:** For instruction-tuned models, including representative prompts in calibration data can improve downstream quality.
6. **Multiple calibration runs:** Some advanced pipelines run calibration on multiple small datasets and average the quantized parameters.

### When calibration data matters most

- **GPTQ** — critically important. Poor calibration data leads to significantly higher perplexity.
- **AWQ** — important but more robust than GPTQ. The scaling factor approach is less sensitive to calibration data quality.
- **GGUF imatrix** — uses importance matrices computed from calibration data. Worth the effort for best-quality GGUF quants.
- **NF4 / HQQ** — no calibration data needed.

---

## 4. Quality Impact Assessment

### Quantization degradation patterns

| Bit Width | Quality Impact |
|---|---|
| **FP16 / BF16** | Baseline (lossless reference) |
| **INT8 (Q8_0, BnB INT8)** | Near-lossless. Negligible PPL increase (<0.01). Output-level differences often undetectable. |
| **6-bit (Q6_K)** | Very minor PPL increase (~0.02). Safe for production. |
| **5-bit (Q5_K_M, Q5_0)** | Small PPL increase (~0.05-0.15). Generally safe. |
| **4-bit (Q4_K_M, GPTQ, AWQ, NF4)** | Moderate PPL increase (~0.10-0.35). Noticeable on complex reasoning tasks. AWS/GPTQ typically best, NF4 worst at same bit width. |
| **3-bit (Q3_K_S, HQQ int3)** | Significant degradation. PPL +0.5-1.5. Tasks requiring multi-step reasoning (CoT) degrade notably. |
| **2-bit (Q2_K)** | Heavy degradation. Only usable for very tolerant tasks. |

### Task-level sensitivity

Not all tasks degrade equally:

| Task Type | Sensitivity | Notes |
|---|---|---|
| **Perplexity / next-token prediction** | Low | Relatively robust to quantization. |
| **Single-token classification (MMLU)** | Low-Moderate | 4-bit typically loses 1-2% accuracy. |
| **Multi-step reasoning (CoT, MATH)** | High | 4-bit can lose 3-5%+ on math reasoning. 3-bit often fails entirely. |
| **Code generation** | Moderate | Functional correctness degrades at aggressive quantization. |
| **Creative writing** | Low | Quality differences are subtle at 4-bit; 3-bit may produce incoherence. |
| **Instruction following** | Moderate | Longer, multi-step instructions become harder at lower precision. |
| **Few-shot learning** | Moderate | Degrades faster than zero-shot performance. |

### Empirical data (Llama 3 8B, from LessWrong benchmarks)

| Method | MMLU (0-shot) | WMDP | The Pile PPL |
|---|---|---|---|
| BF16 (baseline) | 63.87% | 54.99% | 8.283 |
| BnB INT8 | 63.05% | 54.96% | 8.305 |
| HQQ INT8 | 63.87% | 54.66% | 8.298 |
| AWQ INT4 | 61.84% | 54.55% | 8.483 |
| HQQ INT4 | 62.29% | 54.23% | 8.482 |
| GPTQ INT4 | 61.58% | 53.30% | 8.575 |
| BnB NF4 | 61.44% | 54.42% | 8.499 |
| BnB INT4 | 60.80% | 52.73% | 8.633 |
| HQQ INT3 | 62.26% | 51.23% | 8.872 |

> **Scope:** These are historical, secondary-source measurements for one checkpoint and task mix, not a universal quality or serving-speed ordering. Retain their provenance and validate a candidate on the actual task; small average differences do not establish equivalence or protect critical subsets.

### Recommended evaluation framework

1. **Perplexity** — quick sanity check. Compute on withheld validation split (100k tokens minimum).
2. **Task-specific accuracy** — MMLU, HumanEval, GSM8K, or domain-specific benchmarks.
3. **A/B comparison** — Run paired generations from FP16 and quantized model. Human eval or LLM-as-judge for quality differences.
4. **Downstream metric** — For RAG systems, measure retrieval precision. For chatbots, measure response acceptability.

---

## 5. Mixed Precision Patterns

Mixed precision assigns different numerical precisions to different parts of the model or computation graph. This is distinct from per-layer variable-width quantization.

### Common mixed precision patterns

#### 5.1 Weight quantization + high-precision compute

```
Weights: INT4 / NF4
Activations: FP16 / BF16
Gradients (training): FP32
```

- Most common pattern for LLM inference.
- Weights are dequantized on-the-fly to FP16 for computation.
- Offered by AWQ, GPTQ, BnB, GGUF.
- **Tradeoff:** Dequantization overhead. AWQ/GPTQ minimize this via fused kernels (Marlin).

#### 5.2 Low-precision compute (FP8 matmul)

```
Weights: FP8
Activations: FP8
Accumulation: FP16/FP32
```

- NVIDIA H100/H200 supports native FP8 tensor cores (2x throughput vs. FP16).
- TensorRT-LLM and vLLM (FP8 support) use this for high-throughput serving.
- Activation ranges are calibrated (per-tensor or per-channel) at export time.
- Quantization-aware scaling (QTS) ensures accuracy.

#### 5.3 INT8 compute with INT4 weights (W4A8)

```
Weights: INT4
Activations: INT8
Compute: INT8 tensor cores
```

- Emerging pattern for maximum throughput on hardware with INT8 tensor cores (all NVIDIA GPUs since Volta).
- Requires activation quantization at inference time — more complex.
- Used by TensorRT-LLM and some custom serving stacks.

#### 5.4 Per-layer variable precision

```
Layer 1: Q4_K
Layer 5: Q6_K
Layer 14: Q5_K
...
```

- GGUF k-quant and EXL2 use this pattern.
- Sensitive layers (e.g., embedding, lm_head, early/late transformer layers) get higher precision.
- Reduces average bit width without sacrificing critical layers.

#### 5.5 High-precision weights + lower-precision KV cache

```
Weights: FP16
KV Cache: INT8/FP8
Compute: FP16/BF16
```

- KV cache can dominate memory for long contexts or many resident sequences.
- Reducing element width from 16 to 8 bits halves raw cache payload before metadata/alignment; it does not halve total memory.
- Cache dtype and kernel support are engine/model/version-specific; verify them independently of weight precision. See section 6.

### Precision selection

Budget the whole serving process, not only model weights. Compare supported
precision candidates under the same task/context/latency requirements; a smaller
representation does not guarantee faster kernels or unchanged quality. Choose
only from measured candidates meeting all registered guardrails, or retain the
baseline and report insufficient evidence.

---

## 6. KV Cache Quantization

### The KV cache problem

For ordinary decoder self-attention with equal-sized K and V, estimate the
logical cache payload using **KV heads**, not query heads:

```text
KV bytes = 2 × batch_size × n_layers × n_kv_heads × head_dim × cached_tokens × bytes_per_element
```

Here `batch_size` counts simultaneously resident sequences, including separate
samples/beams where applicable. `cached_tokens` includes retained prompt and
generated tokens; for unequal sequence lengths sum their token counts instead of
multiplying one length by the batch. This is payload arithmetic, not an allocated
memory or supported-context guarantee.

**Worked example:** one sequence, Llama 3 70B-style GQA dimensions (80 layers,
8 KV heads, head dimension 128), 32K = 32,768 cached tokens, FP16 = 2 bytes:

```text
2 × 1 × 80 × 8 × 128 × 32768 × 2 = 10,737,418,240 bytes
                                     = 10 GiB ≈ 10.74 GB
```

The former 320 GB result was incorrect. With equal independent sequences and no
sharing, batch 8 needs **80 GiB** and batch 10 **100 GiB** of KV payload alone.
GB means 10^9 bytes; GiB means 2^30 bytes. Original Llama 3 70B's configured context
is 8,192 tokens: the 32K calculation illustrates memory scaling, **not** permission
to extend its supported context. Validate the actual checkpoint and any context
extension separately. At 8,192 tokens the same one-sequence cache is 2.5 GiB.

### Architecture and allocation limits

| Architecture / feature | What changes |
|---|---|
| MHA | KV heads equal query heads; read the model config rather than assuming eight. |
| MQA | One KV head per attention layer; cache size scales with that head, not query count. |
| GQA | Use the checkpoint's KV head count, which need not equal the query head count. |
| MLA / unequal K and V dimensions | Derive stored latent and positional components from the implementation; the simple GQA formula is not applicable unchanged. |
| Hybrid recurrent / sliding-window models | Account per layer for attention windows and recurrent state; do not multiply all layers by a full-context GQA cache. |
| Prefix sharing, paged allocation, sharding | Sharing can reduce duplicate payload; block rounding, retained prefixes, replication and metadata change allocation. Verify per-device placement and measured peaks. |

### KV precision is a separate experiment

Halving element width halves raw KV payload, not total process memory. Scale
metadata, alignment, supported attention kernels and quality matter. Verify the
[versioned KV cache support](https://docs.vllm.ai/en/latest/features/quantization/quantized_kvcache/)
for the engine, hardware and model before proposing FP8/INT8/INT4. Do not call
FP8 lossless, assume FP8 requires only one GPU generation, or infer INT8 support
from an FP8 flag. Evaluate long-context recall, reasoning and task quality at the
same retained context and output budget before accepting reduced KV precision.

See [local serving selection](local-serving-selection.md) for the full memory
budget and bounded workload comparison; provenance is in
[local serving sources](local-serving-sources.md).

---

## 7. Quantization Workflow

The canonical workflow for applying and validating quantization in production:

### Step 1: Establish Baseline

- Load the model in FP16/BF16.
- Run evaluation benchmark (MMLU, perplexity, domain-specific tasks).
- Record latency and throughput at relevant batch sizes.
- Record VRAM usage.
- This is the reference against which all quantized variants are compared.

### Step 2: Select Quantization Method

Use the comparison table (Section 2.7) to choose based on:
- **Target hardware** (CPU? GPU? Apple Silicon? Cloud instance type?)
- **Deployment framework** (vLLM? llama.cpp? TGI? TensorRT-LLM?)
- **Quality constraints** (must match FP16 within X%?)
- **Compute budget** (time available for quantization)

### Step 3: Quantize

Record the calibration corpus (or why the method needs none), quantizer version,
configuration and exported artifact hash. Use the [llama-cpp](../../llama-cpp/SKILL.md)
conversion runbook for GGUF and the [vllm](../../vllm/SKILL.md) skill for supported
serving formats. Do not copy historical conversion commands without checking the
installed quantizer; this reference owns selection and evaluation, not a tool CLI.

### Step 4: Evaluate Quality

- **Primary metric:** Same evaluation benchmark as baseline (Step 1).
- **Secondary metric:** Perplexity on a held-out validation set (e.g., The Pile test split).
- **Tertiary metric:** A/B test with LLM-as-judge for generative tasks.
- **Threshold:** Define acceptable degradation (e.g., < 0.5% MMLU drop, < 0.3 PPL increase).

### Step 5: Benchmark Performance

- Follow the [workload-first serving comparison](local-serving-selection.md): separate single-stream decode, aggregate throughput and accepted tasks/hour.
- Use a configurable concurrency sweep starting with 1, 2, 4, 8 and 10, extending when relevant and safe; ten is not a hard limit.
- Preserve matched context, output/reasoning settings, quality, failures, memory peaks and bounded stop criteria.

### Step 6: Select the Winner

| Criteria | Decision |
|---|---|
| All registered quality, latency, reliability and memory guardrails met | Choose the candidate best meeting the workload objective |
| Quality outside threshold | Try higher-precision variant (Q4_K_M → Q5_K_M; g128 → g64) |
| All methods fail threshold | Consider FP16 with tensor parallelism, or switch to a different architecture |
| Throughput insufficient | Compare supported precision/kernel candidates on the target workload; do not assume lower precision wins |

### Step 7: Production Deployment

- Store quantized model in model registry.
- Configure inference server with appropriate settings.
- Monitor quality metrics continuously (drift detection).
- Set up A/B test vs. previous version.

---

## 8. Inference Serving Architecture

Choose an engine from the workload and supported model/backend, not a universal
throughput table. Start with [local serving selection](local-serving-selection.md)
and its [study template](../templates/local-serving-study.md).

| Candidate | Reason to investigate | Evidence needed before choosing |
|---|---|---|
| llama.cpp | GGUF, CPU/GPU offload, Metal and local deployments | Actual backend, context allocation and concurrency results; it is not restricted to four or fewer users. |
| vLLM | GPU serving with continuous batching and configurable scheduling | Pinned model/kernel support, memory headroom, preemption and task-level tail latency. |
| SGLang | Another candidate for GPU serving, request scheduling and prefix reuse | Pinned compatibility and matched workload measurements; no separate SGLang runbook is provided here. |
| TGI | Existing Hugging Face serving integration | Current maintenance/support status and compatibility with the required checkpoint and platform. |
| Triton with an LLM backend | Existing multi-model deployment requirements | Name and pin the actual backend; Triton is not one universal LLM execution engine or a guaranteed throughput winner. |

Continuous batching, chunked prefill, prefix reuse and speculative decoding are
hypotheses to measure under the chosen workload. Prefix caching saves repeated
prefill work, not generation of new tokens; benchmark cold and warm conditions
separately. Speculation can incur draft-model memory and verification overhead.

Use the [llama-cpp](../../llama-cpp/SKILL.md) and [vllm](../../vllm/SKILL.md)
tool skills for operational commands. This methodology intentionally replaces
stale launch snippets, absolute feature matrices and unqualified engine rankings.

---

## 9. Production Considerations

### Model registry & versioning

- Store quantized models alongside their FP16 originals in a model registry (e.g., MLflow, HuggingFace Hub, S3).
- Tag each quantized model with: base model version, quantization method, bit width, calibration dataset, validation metrics.
- Never overwrite a quantized model — always create a new version.

### A/B testing in production

- Serve both FP16 and quantized variants simultaneously.
- Route a fraction of traffic to each variant.
- Compare quality (user feedback, downstream metrics), latency (p50, p95, p99), and throughput.
- Gradual rollout: 5% → 25% → 50% → 100%.

### Monitoring

The numbers below are illustrative starting points, not universal release gates.
Register workload-specific limits before comparing candidates; cache occupancy
alone does not establish useful throughput or safe memory headroom.

| Metric | What to Watch | Alert Threshold |
|---|---|---|
| **p50/p99 TTFT** | Time to first token | +30% from baseline |
| **p50/p99 TPOT** | Time per output token | +20% from baseline |
| **Throughput** | Tokens/second | <80% of expected |
| **GPU memory utilization** | VRAM usage | >95% persistent |
| **KV cache utilization** | vs. allocated | >90% (good) |
| **Error rate** | 4xx/5xx responses | >1% |
| **Perplexity (eval)** | Quality drift | +0.5 from baseline |
| **Generation quality** | LLM-as-judge or human eval | Periodic |

### Hardware and memory budget

Choose hardware only after the required model, context distribution, quality,
latency and actual simultaneous inference load are known. A parameter count or
short-prompt demo does not establish capacity for long-context agents.

```text
Peak resident memory = loaded weights + active/retained KV or recurrent state
                     + activations and workspace + graph/batching buffers
                     + runtime/allocator/device overhead + safety headroom
```

For 70 billion parameters at nominal 4 bits, weights alone are approximately
35 GB = 32.60 GiB **before** quantization metadata, unquantized tensors and loader
allocations. Add the per-sequence cache estimate from section 6, then measure the
remaining terms on each device. A one-sequence 8K GQA cache contributes 2.5 GiB;
a ten-sequence 32K cache contributes 100 GiB without sharing. Neither arithmetic
sum proves the model loads or meets an SLO. Do not use fixed percentages of
weight size or a universal 1–2 GB allowance for activations/overhead.

Report reserved versus used device memory, host/unified memory, peak prefill and
decode usage, swap/offload and background workloads. On unified memory systems,
account for OS and application pressure rather than treating RAM as dedicated VRAM.

### Cold start and throughput/latency tradeoffs

Record load/compile time and warm-up separately from steady state. Warm-up is not
a remedy for invalid outputs: investigate output corruption before admitting
traffic. Measure TTFT, per-token latency and completed-task time across the sweep;
bigger batches, chunked prefill and speculation do not guarantee lower tail latency.
Use the [study record](../templates/local-serving-study.md) to keep cold/warm
prefix states, failures and saturation stops visible.

### Security considerations

- **GGUF is tensor/metadata data, not an executable file format.** Malformed inputs can still exploit parser/runtime vulnerabilities; use trusted artifacts, maintained loaders and isolation.
- Safetensors likewise does not make a whole model repository, loader or remote-code dependency safe. Review executable code separately; do not enable remote code merely because weights use a data-only container.
- Validate model provenance:
  - Check SHA256 hashes against published values.
  - Only load from trusted registries (HuggingFace verified orgs, internal registry).
- Harden the inference server:
  - Run as non-root user.
  - Use network isolation (no external access for the server).
  - Rate-limit API endpoints.

---

## 10. References & Further Reading

For the reviewed serving claims and their limits, use the [primary-source record](local-serving-sources.md). The historical reading below is background, not a compatibility or capacity guarantee.

### Foundational papers

- **GPTQ:** Frantar et al., "GPTQ: Accurate Post-Training Quantization for Generative Pre-trained Transformers" (2023) — [arXiv:2210.17323](https://arxiv.org/abs/2210.17323)
- **AWQ:** Lin et al., "AWQ: Activation-aware Weight Quantization for LLM Compression and Acceleration" (2024) — [arXiv:2306.00978](https://arxiv.org/abs/2306.00978)
- **Bitsandbytes / NF4 / QLoRA:** Dettmers et al., "QLoRA: Efficient Finetuning of Quantized Language Models" (2023) — [arXiv:2305.14314](https://arxiv.org/abs/2305.14314)
- **PagedAttention:** Kwon et al., "Efficient Memory Management for Large Language Model Serving with PagedAttention" (2023) — [arXiv:2309.06180](https://arxiv.org/abs/2309.06180)
- **vLLM performance analysis:** "Anatomy of a High-Throughput LLM Inference System" (2025) — [vLLM Blog](https://vllm.ai/blog/2025-09-05-anatomy-of-vllm)
- **KV cache quantization (KVTuner):** Liu et al., "KVTuner: Sensitivity-Aware Layer-Wise Mixed-Precision KV Cache Quantization" (2025) — [OpenReview](https://openreview.net/forum?id=zDwipF6h06)
- **MLA:** "TransMLA: Multi-head Latent Attention Is All You Need" (2025) — [arXiv:2502.07864](https://arxiv.org/abs/2502.07864)

### Guides & benchmarks

- "Which Quantization Method is Right for You (GPTQ vs. GGUF vs. AWQ)" — [Maarten Grootendorst](https://newsletter.maartengrootendorst.com/p/which-quantization-method-is-right)
- "Comparing Quantized Performance in Llama Models" (2024) — [LessWrong](https://www.lesswrong.com/posts/qmPXQbyYA66DuJbht/comparing-quantized-performance-in-llama-models)
- "The Complete Guide to LLM Quantization with vLLM" (2026) — [Jarvis Labs](https://jarvislabs.ai/blog/vllm-quantization-complete-guide-benchmarks)
- "An Empirical Study of Qwen3 Quantization" (2025) — [arXiv:2505.02214](https://arxiv.org/abs/2505.02214)
- "LLM Inference at scale with TGI" (2024) — [HuggingFace Blog](https://huggingface.co/blog/martinigoyanes/llm-inference-at-scale-with-tgi)
- "Continuous Batching: The Single Biggest GPU Utilization Unlock" (2026) — [Tian Pan](https://tianpan.co/blog/2026-04-09-continuous-batching-llm-inference)

### Tools & repositories

- **vLLM** — [github.com/vllm-project/vllm](https://github.com/vllm-project/vllm)
- **llama.cpp** — [github.com/ggml-org/llama.cpp](https://github.com/ggml-org/llama.cpp)
- **TGI** — [github.com/huggingface/text-generation-inference](https://github.com/huggingface/text-generation-inference)
- **TensorRT-LLM** — [github.com/NVIDIA/TensorRT-LLM](https://github.com/NVIDIA/TensorRT-LLM)
- **Triton Inference Server** — [github.com/triton-inference-server/server](https://github.com/triton-inference-server/server)
- **AutoGPTQ** — [github.com/PanQiWei/AutoGPTQ](https://github.com/PanQiWei/AutoGPTQ)
- **AutoAWQ** — [github.com/casper-hansen/AutoAWQ](https://github.com/casper-hansen/AutoAWQ)
- **bitsandbytes** — [github.com/bitsandbytes-foundation/bitsandbytes](https://github.com/bitsandbytes-foundation/bitsandbytes)
- **ExLlamaV2** — [github.com/turboderp/exllamav2](https://github.com/turboderp/exllamav2)
- **Awesome LLM Quantization** — [github.com/pprp/awesome-llm-quantization](https://github.com/pprp/awesome-llm-quantization)

---

> **End of reference document.** This is a living document — update benchmarks and framework versions as the ecosystem evolves.
