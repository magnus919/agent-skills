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

Use a client driving the actual `llama-server` route, template, streaming mode,
and task mix. `llama-bench` is a component comparison, and the bounded
`llama-completion` helper is an offline completion/containment workflow. Neither
proves concurrent serving, agent capacity, or accepted task throughput.

### Declare the sweep and stop rules

Start with configurable client-outstanding-request levels **1, 2, 4, 8, 10**.
This is a useful default sweep, not a ceiling or a claim that every host can
reach ten. Add higher levels when the target workload and safe measured headroom
justify them. Do not stop at four merely because an example does. State whether
the client uses fixed outstanding requests, a synchronized burst, or a timed
arrival rate; queueing behavior differs. Check load-generator headroom too.

For each level, test representative **short, normal, and long context** cohorts.
Define their actual token ranges from the intended workload, including rendered
system/tool instructions, conversation history, input, and reserved output.
Freeze fixture/task IDs, sampling, output budgets, quality acceptance criteria,
latency/error thresholds, timeout/retry policy, repetitions, and measurement
window before comparisons. Keep long-context quality in the contract rather
than substituting short prompts to make the highest level fit.

Record configured slots, resolved per-slot context/shared KV behavior, cache,
batch, offload, and memory from the installed build's help and startup evidence.
Client load and server slot count are separate experiment variables. First
sweep load against one frozen server configuration. If slots or context must
change, record a new configuration and rerun matched baseline cells; do not
attribute that combined change to concurrency alone. Do not assume a portable
context-per-slot formula across revisions or KV modes.

Predeclare the minimum host/device memory margin, maximum memory pressure or
swap, thermal limits, latency/timeout/error limits, run duration, and resource
budget. Check headroom before each increase. On OOM, sustained overload, a
breached safety limit, or unusable output, stop the affected sweep and retain
sanitized evidence; do not keep raising load to complete a table. Name the
trigger, last measured safe cell, and next permitted diagnostic step. A higher
cell skipped after a stop is **not run / unknown**, not a measured failure or
proven capacity. The highest passing tested cell is not the system's maximum.

### Measure each concurrency layer

| Layer | Record | What it does not prove |
|---|---|---|
| Active agents | Task-active agents and agents waiting on tools, I/O, or humans | All agents are issuing inference now |
| Client requests | Target and observed outstanding requests, client-side queue, submissions and completions over time | Every submitted request is executing |
| Server | Configured slots, occupied/running slots, requests processing and deferred, with timestamps | Configured slots equal realized overlap |
| Inference overlap | Correlated request/slot timeline or available decode/batch trace showing overlapping processing | A single peak or queue snapshot proves sustained parallel decode |

Record the sampling interval and source for each count. Use documented
`/slots` and `/metrics` when available and already authorized; otherwise state
the observation gap. At the focused reviewed revision, metrics include
`llamacpp:requests_processing`, `llamacpp:requests_deferred`, and
`llamacpp:n_busy_slots_per_decode`. These are server observations, not an agent
count; an average busy-slot gauge alone does not reconstruct a timeline or prove
simultaneous hardware execution. Recheck names and enablement on the installed
build. Keep monitoring private and sanitize prompt-bearing slot/log data.

### Separate speed from useful work

For every context/load/cache cell preserve raw per-request records and report:

- Aggregate prompt and generated tokens per measured wall second separately,
  completed requests/s, and elapsed window. Do not sum or average per-request
  token rates and label the result aggregate throughput.
- Per-request client TTFT and full latency distributions (at least p50/p95,
  sample counts and repeated-run variance), plus decode rate/time per token
  when measurable. Define the first token event for reasoning/tool streams;
  first byte or an empty role event is not necessarily a usable token. Record
  client queue delay separately and server queue time if observable. Preserve
  failures/timeouts as outcomes rather than silently excluding them from an
  otherwise successful-only latency distribution.
- Unique logical tasks attempted and accepted, total request attempts, retries,
  failures, timeouts, quality rejects, cancellations, and unfinished tasks.
  **Accepted tasks/hour = 3600 × unique tasks passing the frozen acceptance
  criteria / total measured wall seconds.** Count a retried task at most once;
  keep failed-attempt, retry, queue, and timeout time inside the window. Declare
  warmup and drain/cutoff handling; do not shrink the denominator to successful
  request time. For agent workflows keep tool-wait time in the agent-task
  window and label a separate inference-only rate if useful.
- Server usage prompt/completion tokens, finish reasons, truncation and empty
  or malformed outputs, quality results, errors/OOMs, peak RAM and per-device
  memory, and remaining margin. Missing fields are unknown, not zero errors or
  successful completion. A `length` finish is not automatically accepted work.

The upstream k6 benchmark uses a simple whitespace tokenizer for input
selection; actual model token counts differ. Prefer server usage for request
accounting when present. Its `llamacpp_tokens_second` is
`usage.total_tokens / request duration`, so it mixes prompt and completion
counts and is not pure decode speed or aggregate generated-token throughput.
Extend the harness as needed to measure TTFT, timelines, and task acceptance;
its default token/finish metrics do not establish them. An aggregate throughput
increase can coexist with slower individual responses and fewer accepted tasks.

### Test prefix reuse without hiding diversity

Keep model warmup separate from prompt-cache state. Compare a cache-cold common
prefix, a cache-warm common prefix with changed task suffixes, and diverse
prefixes representative of independent agents. Record shared-prefix lengths,
request ordering/slot assignment, cache reset or isolation method, and observed
reused/evaluated token evidence where the exact route exposes it. If verifying
cold state needs a restart or cache mutation, confirm that scope first; otherwise
mark cold state unverified. Repeat cohorts without carrying warm shared-prefix
results into the diverse-prefix estimate.

Prompt cache reuse avoids reprocessing a matching prefix and can reduce
**prefill/TTFT**; it does not automatically accelerate **decode**. Measure both
phases and retain the same quality criteria. Cache reuse is conditional on the
build, model, request shape, and cache/slot state; matching text alone does not
prove a hit. Verify request fields and response/metric support against pinned
server docs plus installed help, rather than copying cache switches between
frontends or API routes. The focused source review is recorded in
`references/source-index.md` from the skill root.

## Quality guardrail

Performance changes can alter output through quantization, cache precision, templates, context scaling, batching, or backend numerical behavior. Keep a fixed representative prompt/eval set. For quant comparisons, pair task-specific outcomes with perplexity or KL divergence where meaningful. Perplexity from different tokenizers/models is not directly comparable.

## Verdict

Accept a change only when the primary metric improves beyond observed variance, guardrails remain within thresholds, memory has safe margin, and the target workload passes. Otherwise retain the baseline and document whether the candidate was slower, unstable, too large, or outside the quality budget.
