# Troubleshooting

Use this reference after preserving the failing command, exact version, model identity, host/device inventory, startup logs, error response, and recent change. Diagnose one layer at a time: artifact, model, backend/placement, memory, prompt/template, then API/client.

## First evidence

```sh
llama-cli --version
llama-cli --list-devices
llama-cli --help
llama-server --version
llama-server --help
```

Also capture vendor device status, free RAM/disk, the model hash and metadata, and the last known-good command. Redact API/Hugging Face tokens and sensitive prompts.

## Symptom routing

| Symptom | Check first | Safe next action |
|---|---|---|
| Unknown flag or changed response | Installed `--help`, version, REST changelog | Translate configuration to current interface; do not retry obsolete flags blindly |
| Unsupported architecture/tensor/GGUF | Model metadata, complete shards, llama.cpp revision | Confirm current architecture support or use a supported build/model conversion |
| GPU absent | Build configure log, `--list-devices`, driver/runtime visibility | Fix build/runtime visibility before tuning offload |
| GPU listed but CPU inference | Resolved device, offloaded layer/buffer logs, environment device filters | Select the intended device and verify load placement |
| OOM at startup | Weight placement, context, slots, KV type/offload, batch buffers, sidecars | Reduce context/parallel slots or buffers, then offload; preserve safety margin |
| OOM during requests | Actual prompt depth, concurrency, cache growth, multimodal inputs | Reproduce with one slot and bounded context, then scale deliberately |
| Slow generation | Backend fallback, generation threads, partial offload, memory pressure, thermals | Establish `llama-bench` tg baseline and sweep one setting |
| Slow prompt/TTFT | Prompt length, batch/ubatch, prompt threads, model load/cache misses | Separate pp from tokenization, queueing, and first-request warmup |
| More threads are slower | Physical cores, SMT, NUMA, oversubscription | Sweep from one thread upward and retain measured optimum |
| Multi-GPU slower | Split mode, interconnect, collective library, device balance | Compare `layer` with single GPU; use experimental tensor mode only when supported |
| Garbled or role-leaking chat | Embedded/source template, conversation mode, special tokens | Test a minimal rendered chat before overriding template |
| Broken tool calls/JSON | Tool-aware template, parser format, schema, cache quantization | Test one deterministic tool/schema and inspect logs/response shape |
| Context exhausted/truncated | Trained context, configured context, prompt tokens, slots, finish reason | Reduce prompt/output or use supported scaling with quality evaluation |
| Health stays 503 | Model load progress, file access, OOM, startup error | Fix load failure; do not put traffic on the instance |
| API client fails after upgrade | Exact route/fields, model identifier, auth, stream framing, changelog | Reproduce with `curl` against the documented current contract |

## Backend fallback

An accelerator appearing in a vendor tool is not enough. Check that the binary was compiled with the backend, the device appears to llama.cpp, the runtime did not hide it, and model buffers/layers were actually assigned. Use a CPU-only control and vendor utilization only after confirming identical workload. Avoid changing backend, offload, threads, and batch simultaneously.

## OOM triage

Account separately for weights, KV cache, parallel sequences, context, batch/compute buffers, sidecars/draft models, and runtime margin. Read resolved allocations from startup logs. For a server, reproduce with one parallel slot and a bounded prompt. Reduce the largest workload-driven allocation first; moving model layers to CPU can restore fit but may sharply reduce speed.

On current multi-GPU tensor mode, upstream documents additional constraints around automatic fitting, cache quantization, Flash Attention, and architecture support. Fall back to `layer` rather than forcing unsupported combinations.

## Output and template triage

Determine whether the model is base, instruct, chat, reasoning, or tool-tuned. Compare the original model card template, GGUF metadata, selected llama.cpp format, and response parser. Look for leaked role markers, duplicated BOS/EOS, wrong stops, missing tool delimiters, and reasoning content in unexpected fields. Use a minimal deterministic conversation before testing long prompts.

## Performance triage

Separate:

1. startup/model load;
2. tokenization and queueing;
3. prompt processing;
4. first-token latency;
5. token generation;
6. sampling/stream rendering;
7. end-to-end request latency.

`llama-bench` isolates model prompt/generation performance but excludes tokenization and sampling. If its numbers are stable while the API is slow, investigate queueing, templates, prompt length, streaming/client rendering, network, and concurrency.

## API compatibility triage

Reproduce with the smallest direct `curl` request, query current model/capability endpoints, and inspect server logs. Compare the installed build with the REST changelog. Do not assume that OpenAI-compatible means every OpenAI route, field, stream event, model-name behavior, or error shape is implemented identically.

## Stop conditions

Stop after two materially different fixes fail, when the model/license or target hardware is unknown, when only an unsupported architecture/backend combination would satisfy the request, or when external exposure lacks an approved security boundary. Report evidence, the exact blocker, and the smallest decision needed next.
