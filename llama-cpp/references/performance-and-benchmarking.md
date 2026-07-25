# Performance and benchmarking

Use this reference when tuning llama.cpp or comparing builds, models, quants, backends, cache settings, or server configurations.

## Define the objective

Choose explicit primary and guardrail metrics:

| Concern | Useful evidence |
|---|---|
| Interactive latency | TTFT, time per output token, end-to-end latency percentiles |
| Offline throughput | prompt tokens/s, generated tokens/s, requests/s, total completion time |
| Capacity | peak/resident RAM, VRAM per device, KV/cache use, maximum stable context/concurrency |
| Quality | task success, schema/tool-call success, paired output review, perplexity/KL where appropriate |
| Stability | error/OOM rate, variance, throttling, thermal behavior, long-run memory trend |

Tokens per second alone is not an objective. State the workload: prompt/output lengths, context depth, number of slots/users, streaming, structured output, and expected hardware contention.

## Freeze the comparison contract

Keep constant:

- llama.cpp commit/build options and backend unless that is the tested variable;
- model file hash, quant, sidecars, template, and sampling;
- host, driver, power mode, device visibility, and interconnect;
- context, prompt and generated token counts, batches, cache types, offload, and concurrency;
- warmup, repetitions, delays, background load, and thermal state.

Change one dimension at a time. Record raw machine-readable output and observed startup configuration in `templates/benchmark-comparison.md`.

## Use `llama-bench` correctly

At the reviewed revision, `llama-bench` distinguishes:

- prompt processing (`pp`);
- text generation (`tg`);
- combined prompt plus generation (`pg`);
- context depth and repeated runs.

Use its current `--help` to construct tests and prefer JSON/JSONL/CSV for durable comparisons. A representative shape is:

```sh
llama-bench -m /path/to/model.gguf \
  -p 512 -n 128 -r 5 -o json
```

The upstream tool states that measurements exclude tokenization and sampling. Therefore use an end-to-end client or server benchmark for TTFT and user-visible latency. Preserve individual repetitions and standard deviation; do not report only the best run.

## Tuning order

Start from the working baseline and test in this order when relevant:

1. **Backend and placement:** verify expected device, full or partial offload, and CPU fallback.
2. **Context and concurrency:** set only what the workload needs; both can drive KV/cache memory.
3. **Generation threads:** sweep from a small value upward; oversubscription can reduce decode speed.
4. **Prompt/batch threads and sizes:** tune prompt processing separately from generation.
5. **Logical/physical batch:** compare speed against compute-buffer memory and latency.
6. **KV cache type/offload and Flash Attention:** measure memory, speed, and task quality together.
7. **GPU layers/device split:** compare full offload, partial offload, and stable margin.
8. **Advanced or experimental paths:** multi-GPU tensor mode, speculative decoding, and backend-specific knobs require a new baseline and quality/stability checks.

## Multi-GPU

Run `--list-devices` first and record device order and memory. At the reviewed revision:

- `layer` is the default and most compatible split, useful for capacity and batch throughput;
- `row` is deprecated;
- `tensor` is experimental, communication-sensitive, architecture-limited, incompatible with automatic fitting in documented cases, and requires supported Flash Attention/cache combinations.

Use automatic splitting as a baseline, then explicit device and tensor proportions only when measured imbalance justifies them. Compare against the best single-GPU or partial-offload baseline. More GPUs can be slower when interconnect communication dominates. Record NCCL/RCCL or peer-access availability and any warnings; revert peer-access experiments if instability or corrupted output appears.

## Server benchmark

Test the actual request shape and concurrency. Capture at least request success/error rate, TTFT, completion latency, prompt/completion tokens, truncation/finish reasons, throughput, and memory. The upstream server benchmark uses k6 and distinguishes client metrics from server metrics; its simple local tokenizer can differ from actual token counts, so rely on server usage for authoritative request accounting when available.

## Quality guardrail

Performance changes can alter output through quantization, cache precision, templates, context scaling, batching, or backend numerical behavior. Keep a fixed representative prompt/eval set. For quant comparisons, pair task-specific outcomes with perplexity or KL divergence where meaningful. Perplexity from different tokenizers/models is not directly comparable.

## Verdict

Accept a change only when the primary metric improves beyond observed variance, guardrails remain within thresholds, memory has safe margin, and the target workload passes. Otherwise retain the baseline and document whether the candidate was slower, unstable, too large, or outside the quality budget.
