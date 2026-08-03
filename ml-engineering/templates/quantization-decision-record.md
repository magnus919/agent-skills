# Quantization Decision Record

Fill this record before shipping a quantized model. Quantization is a trade-off,
not a default: the record captures what was measured, what was compared, and why
the chosen variant is safe for the workloads it serves.

## Context

- Model: `[fill: model id and version/commit]`
- Serving engine: `[fill: e.g. llama.cpp, vLLM, TGI, Triton]`
- Hardware: `[fill: GPU model(s) and count, VRAM per GPU]`
- Workload: `[fill: concurrency, max context, latency and throughput targets]`
- Decision date: `[fill: YYYY-MM-DD]`

## Baseline (Unquantized)

- Eval set version: `[fill: eval set revision/hash]`
- Baseline quality: `[fill: metric and value, per capability if applicable]`
- Baseline VRAM / throughput / latency: `[fill: measured numbers, not model-card arithmetic]`

## Candidates Compared

| Candidate | Calibration data | Quality delta | VRAM | Tokens/sec | Latency | Notes |
|---|---|---|---|---|---|---|
| `[fill: e.g. GGUF q8_0]` | `[fill: source and size of calibration set]` | `[fill: delta vs baseline]` | `[fill: GB]` | `[fill: value]` | `[fill: value]` | `[fill: notes]` |
| `[fill: e.g. GGUF q4_k_m]` | `[fill: ...]` | `[fill: ...]` | `[fill: ...]` | `[fill: ...]` | `[fill: ...]` | `[fill: ...]` |
| `[fill: e.g. AWQ 4-bit]` | `[fill: ...]` | `[fill: ...]` | `[fill: ...]` | `[fill: ...]` | `[fill: ...]` | `[fill: ...]` |
| `[fill: e.g. GPTQ 4-bit]` | `[fill: ...]` | `[fill: ...]` | `[fill: ...]` | `[fill: ...]` | `[fill: ...]` | `[fill: ...]` |

All candidates measured on the same eval set version and the same hardware under
production-like concurrency.

## Quality Threshold

- Required threshold: `[fill: the minimum quality per critical capability that must hold]`
- Regression check: `[fill: which capabilities were re-checked and the results]`
- Capabilities where regression is acceptable: `[fill: list or none]`

## Decision

- Selected variant: `[fill: quantization scheme and size, e.g. GGUF q5_k_m]`
- Rationale: `[fill: why this variant meets the quality threshold within the VRAM/latency budget]`
- Rejected variants and reasons: `[fill: e.g. "q4_k_m dropped code-gen subset by 12%"]`
- Rollback path: `[fill: e.g. "serve the fp16/bf16 weights; keep serving config unchanged"]`

## Follow-Ups

- Re-evaluate when: `[fill: e.g. "new engine version or model release, or after 2 weeks of production traffic"]`
- Production monitoring: `[fill: how quality will be sampled in production]`
- Open questions: `[fill: anything unresolved]`
