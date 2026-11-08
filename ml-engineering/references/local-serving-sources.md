# Local serving source record

Reviewed 2026-11-08 through public primary documentation. These URLs track live
branches or `latest`; no versioned deployment or model run was validated here.
For a real study, record the fetched revision/content hash and match it to the
installed release. Distinguish source claims, arithmetic, local measurements and
recommendations; a project-authored benchmark is not independent replication.

| Primary source | Supported observation | Limits / use in this skill |
|---|---|---|
| [vLLM optimization and tuning](https://docs.vllm.ai/en/latest/configuration/optimization/) | KV pressure can cause preemption/recomputation; scheduler and memory settings trade throughput against latency. | Version-specific guidance, not a fixed batch size or universal engine ranking. The workload sweep and stop criteria here are study recommendations. |
| [vLLM automatic prefix caching](https://docs.vllm.ai/en/latest/features/automatic_prefix_caching/) | Matching prefixes can reuse prefill work; new-token decoding is still required. | Warm-prefix wins are not cold/non-shared-prefix wins. Check hybrid-model support and actual reuse. |
| [vLLM GGUF](https://docs.vllm.ai/en/latest/features/quantization/gguf/) | Current documentation warns that GGUF is experimental/under-optimized and directs users to an out-of-tree plugin. | Do not retroactively apply this installation path to every older release or promise compatibility with every feature. |
| [vLLM quantized KV cache](https://docs.vllm.ai/en/latest/features/quantization/quantized_kvcache/) | Documents supported cache precision and backend/model constraints. | Verify the deployed version; weight precision does not determine cache precision or guarantee unchanged quality. |
| [SGLang hyperparameter tuning](https://docs.sglang.io/docs/advanced_features/hyperparameter_tuning) | Separates queued/running work and KV pressure; accounts for weights, cache, graph buffers and activations. | Offline saturation advice is not an interactive SLO. SGLang is a comparison candidate here, not a new operational skill. |
| [GGUF specification](https://github.com/ggml-org/ggml/blob/master/docs/gguf.md) | Defines tensor/metadata container structure. | A data format is not executable code; parser vulnerabilities and separately loaded code remain security risks. |
| [Meta Llama 3 model card](https://github.com/meta-llama/llama3/blob/main/MODEL_CARD.md) | Original Llama 3 models use GQA and an 8K context. | The 32K example is hypothetical memory arithmetic, not validated context extension. Read the actual checkpoint config for dimensions. |
| [HyperQwen benchmark report](https://github.com/syv-ai/HyperQwen/blob/main/docs/benchmarks.md) | Author-run single/cohort benchmarks include short prompts; the report discloses mismatched reasoning/sampling, decode versus end-to-end definitions and cache-residency effects. | Useful for hypotheses and comparison pitfalls, not transferable capacity proof for ten long-context agents on a 24 GB card. |

## HyperQwen and video-claim boundary

The report compares some 29–34-token prompts with a different chat workload; its
64-request row uses 128 input / 512 output tokens. It also records that thinking
settings differ and that an earlier table mixed decode and end-to-end rates.
Those qualifications prevent treating the headline as a matched engine trial.
Preserve hardware, precision, context/output length, cache/speculation state,
reasoning mode, measurement denominator and quality evidence with any quoted
number. A demonstration or video summary cannot fill missing task acceptance,
long-context residency, errors or repeat-run evidence. No local capacity or model
quality was measured as part of this documentation change.

## Arithmetic provenance

The cache calculation is a dimensional derivation for standard equal-shaped
K/V self-attention, not an empirical benchmark: `2 × 80 × 8 × 128 × 32768 × 2`
bytes is 10 GiB for one sequence before allocation overhead. Eight or ten
independent sequences scale the payload to 80 or 100 GiB. The dimensions are the
explicit assumptions of the example; MLA, hybrid recurrent state, sliding windows,
prefix sharing and per-device sharding require an implementation-specific budget.
