# Serving evidence assertion challenges

## Rubric changes (2026-11-08)

All six original case IDs are retained. `serving-config-review` corrects direct
context-to-KV sizing and unconditional fit; `quantization-and-parallelism-sizing`
requires measured capacity; `benchmark-run-review` adds cache/length controls;
`continuous-batching-tuning` checks resolved defaults and pressure evidence;
`upgrade-rollback-troubleshooting` distinguishes allocation phase from a
guaranteed context-limit fix. `openai-api-integration` is unchanged. Four new
cases cover V1 defaults/cache evidence, GGUF, agent/load sweeps, and context/KV.

These authored challenge examples are for assertion review, not observed model
outputs, execution evidence, independent human labels, or benchmark results.
Each row maps to the current one-based assertion index in `evals.json`.
Use the assertion text as the contract; omission means not shown, not a pass.

## serving-config-review

| Assertion | Satisfying example | Contradictory near miss | Omitted evidence |
|---|---|---|---|
| 1. The command pins model, revision, served-model-name, tensor-parallel-size 2, max-model-len, and gpu-memory-utilization | Pinned model/revision/name, TP=2, length and budget in draft. | Deploys an unpinned model with no budget. | Only gives prose; no serving plan. |
| 2. Uses roughly 140 GB of bf16 weights to assess the two-GPU plan without guaranteeing the target workload fits | ~140 GB weights makes TP=2 plausible; runtime overhead still needs profiling. | Two 80 GB GPUs guarantee all 32K workloads fit. | No weight-budget reasoning. |
| 3. Distinguishes the max-model-len admission limit from the allocated KV pool and actual resident token demand | 32K is admission; pool is profiled; live tokens occupy blocks. | 32K directly allocates one 32K cache per request. | Only lists the context flag. |
| 4. Verification includes startup memory profiling, /v1/models, and a representative chat request | Check startup profile, served name and generated response. | HTTP health alone proves model readiness. | No verification steps. |
| 5. The serving config template is used so the deployment is reproducible and rollback is a pinned-image redeploy | Save pinned config record as rollback unit. | Rollback by reinstalling latest with new flags. | No config record or rollback treatment. |

## quantization-and-parallelism-sizing

| Assertion | Satisfying example | Contradictory near miss | Omitted evidence |
|---|---|---|---|
| 1. Requires a measured baseline before claiming the requested concurrency is supportable | Measure workload/SLO baseline before promising 256. | 80 GB proves 256 long requests are safe. | Only recommends a quant type. |
| 2. Tensor parallelism is correctly deemed not applicable on a single GPU | TP=1 on the single H100; more shards need more GPUs. | Set TP=2 on one H100. | Does not address TP. |
| 3. Quantization (FP8/INT4 weights) and kv-cache-dtype fp8 are evaluated as the memory levers, with quality trade-offs stated | Compare supported weight quants and FP8 KV with quality checks. | KV FP8 cannot affect quality. | No quantization trade-offs. |
| 4. Correlates KV occupancy with waiting requests and preemption before diagnosing capacity | Correlate occupied KV, waiting and preemption. | Occupancy alone proves the bottleneck. | No capacity signals. |
| 5. Verification re-runs the frozen benchmark and a quality spot-check under matched conditions | Repeat matched benchmark and quality check. | Accept a smaller checkpoint without testing. | No post-change verification. |

## benchmark-run-review

| Assertion | Satisfying example | Contradictory near miss | Omitted evidence |
|---|---|---|---|
| 1. The review demands matched conditions (version, model, quant, parallelism, context, batching, GPU, workload) on both sides | Freeze everything except declared engine version. | Different model/hardware runs prove an upgrade win. | No conditions listed. |
| 2. Raw vllm bench serve output with throughput, TTFT/TPOT/ITL percentiles, and variance is required, not a single number | Request raw latency/throughput records and repeat variance. | One aggregate throughput value suffices. | No raw results or repetitions. |
| 3. A suspicious doubling is probed for a mismatch in concurrency, dataset, or precision | Investigate concurrency, dataset and precision drift. | Assume both numbers necessarily represent the same load. | No confounder investigation. |
| 4. Throughput and latency (TTFT/TPOT under load) are treated as separate metrics | Check TTFT/TPOT SLOs separately from total tok/s. | Double tok/s proves each response is twice as fast. | Only discusses throughput. |
| 5. The benchmark run record template is required on both sides before the upgrade ships | Require both run records before a rollout claim. | Approve rollout from the two numbers alone. | No evidence-record requirement. |
| 6. Checks cache state and actual output lengths or truncation as possible comparison confounders | Check cache warmth and actual outputs/truncation. | Warm shortened outputs are interchangeable with cold full answers. | No cache/length controls. |

## continuous-batching-tuning

| Assertion | Satisfying example | Contradictory near miss | Omitted evidence |
|---|---|---|---|
| 1. Correlates high KV occupancy and waiting with preemption or latency evidence before declaring the capacity bottleneck | Inspect preemption and latency alongside occupancy/waiting. | 0.95 occupancy alone proves KV is the only bottleneck. | No pressure diagnosis. |
| 2. Inspects resolved chunked-prefill and prefix-cache settings before recommending enablement | Read resolved V1 settings before adding enable flags. | Both are off; enabling them must improve throughput. | No default verification. |
| 3. Proposes a bounded experiment using concurrency, a prefill token budget, actual token demand, or scale-out | Test one bounded token-budget or concurrency change. | Raise every limit at once without a scope. | No concrete experiment. |
| 4. Does not claim lowering max-model-len alone frees KV memory at unchanged actual token lengths | A smaller cap with the same actual tokens need not free KV. | Half the cap always halves resident KV. | No distinction about the cap. |
| 5. Evaluates prefix reuse with cache-state controls rather than promising faster decoding | Compare prefix cohorts; prefill savings do not speed new-token work. | Warm TTFT improvement proves decode acceleration. | No cache interpretation. |
| 6. Changes one variable at a time under matched benchmark conditions | Vary one knob with workload/config fixed. | Change precision, model and concurrency and attribute to batching. | No matched-comparison plan. |
| 7. Requires repeated per-request tail-latency evidence rather than one aggregate or median result | Repeat per-request p95/p99 analysis with sample limits. | Good p50 means the p99 spike is solved. | No tail evidence. |

## upgrade-rollback-troubleshooting

| Assertion | Satisfying example | Contradictory near miss | Omitted evidence |
|---|---|---|---|
| 1. Diagnosis uses exact image digests, serving args, model revision, nvidia-smi, and side-by-side startup logs | Compare both image digests, arguments, model, GPUs and logs. | Same model means no other evidence is needed. | No read-only evidence plan. |
| 2. Investigates changed memory defaults or flag semantics together with the allocation phase rather than assuming the context limit directly sizes KV memory | Locate allocation failure and compare resolved defaults. | max-model-len directly sizes all memory; halve it. | No phase/default investigation. |
| 3. The fix-forward path validates on a scratch instance with release notes and the frozen benchmark before redeploying | Validate candidate on scratch with release notes and matched benchmark. | Try changed memory flags directly on production. | No forward validation. |
| 4. The rollback path redeploys the pinned previous image plus recorded config and verifies at the delivery boundary | Restore old pinned image/config, then verify inference. | Restoring the tag proves old behavior returned. | No rollback verification. |
| 5. No production mutation happens without a human directive naming target, scope, and rollback path | Require target/scope/rollback directive before mutating production. | Restart production based only on this diagnostic question. | No mutation boundary. |

## v1-defaults-and-prefix-evidence

| Assertion | Satisfying example | Contradictory near miss | Omitted evidence |
|---|---|---|---|
| 1. Explains that V1 chunked prefill is enabled where supported rather than generally off | V1 enables chunking where supported. | Chunking is off on most V1 configurations. | No chunking default statement. |
| 2. Identifies the v0.26.0 CacheConfig prefix-caching default without treating it as a universal resolved engine setting | CacheConfig is true; EngineArgs has model/backend exceptions. | All v0.26.0 models must enable prefix caching by default. | No prefix default or resolution statement. |
| 3. Requires inspection of the installed release and resolved startup settings before deciding whether enablement changes behavior | Inspect release, model/backend and resolved startup values. | CLI absence proves the feature is off. | Only repeats a documentation default. |
| 4. Distinguishes prefix-cache prefill or TTFT savings from direct new-token decoding acceleration | Reuse avoids prefill; measure TPOT independently. | A warm TTFT win proves direct decode acceleration. | No prefill/decode distinction. |
| 5. Proposes matched cold/warm and shared/non-shared prefix cohorts | Cross cold/warm with shared/non-shared prefixes in matched runs. | Use only repeated warm system prompts for all claims. | No cache-state experiment. |
| 6. Links official versioned or current vLLM documentation supporting the default correction | Link official optimization and versioned cache docs. | Cite only an undated third-party claim. | No supporting source. |

## gguf-serving-compatibility

| Assertion | Satisfying example | Contradictory near miss | Omitted evidence |
|---|---|---|---|
| 1. Describes vLLM GGUF support as experimental and under-optimized | Warn experimental and under-optimized. | GGUF is a fully optimized native path. | No maturity warning. |
| 2. Warns that GGUF may be incompatible with required serving features | Check compatibility with required serving features. | All features have native-checkpoint parity. | No feature warning. |
| 3. Identifies the current out-of-tree vllm-gguf-plugin integration path | Current docs point to vllm-gguf-plugin. | Current docs require no separate integration. | No current integration path. |
| 4. Checks the pinned engine version instead of applying the current plugin requirement universally to older releases | Check pinned older engine before applying plugin advice. | Every old release necessarily requires the latest plugin. | No version qualification. |
| 5. Recommends the matching base-model tokenizer | Use matching base-model tokenizer/revision. | Always convert the tokenizer from GGUF instead. | No tokenizer guidance. |
| 6. Requires measured serving evidence instead of inferring speed or parity from smaller file size | Measure matched serving throughput/latency. | Smaller file proves faster serving. | No performance verification. |
| 7. Requires task-quality validation before treating the GGUF checkpoint as an equivalent replacement | Evaluate representative task quality before replacement. | Load success proves equivalent task outcomes. | No quality check. |

## measured-agent-serving-capacity

| Assertion | Satisfying example | Contradictory near miss | Omitted evidence |
|---|---|---|---|
| 1. Includes eight and ten in a configurable sweep rather than stopping at four | Plan 1,2,4,8,10 unless a safety stop intervenes. | Four is always enough to establish capacity. | No sweep points above four. |
| 2. Allows extending the sweep beyond ten when safe and useful | Extend beyond ten if headroom and budget justify it. | Ten is a hard maximum for every deployment. | No statement about further levels. |
| 3. Defines explicit stop constraints before escalating load | Set measurable latency, memory/error and budget stops before running. | Reach ten even if OOM/timeouts start at eight. | No stopping criteria. |
| 4. Rejects a fixed percentage of startup concurrency as proof of production SLO capacity | Measure SLO capacity; 18 is not proven by 90% of 20. | Startup 20 authorizes production concurrency 18. | No assessment of the startup estimate. |
| 5. Separates active agents from requested, queued and running inference overlap | Record agents/tool waits, requested in-flight, server queue and running. | Ten active agents means ten simultaneous generations. | Only gives an agent count. |
| 6. Requires per-request latency tails rather than relying solely on aggregate token throughput | Retain TTFT/TPOT/E2E tails for each request cohort. | Total tok/s alone establishes interactive capacity. | No per-request latency evidence. |
| 7. Retains request errors in the benchmark outcome evidence | Keep HTTP/model errors by attempt and task. | Drop errors from the report. | No error data. |
| 8. Retains timeouts in the benchmark outcome evidence | Count timed-out requests in outcomes. | Exclude timeouts as if they never occurred. | No timeout accounting. |
| 9. Records retry counts rather than treating every attempt as distinct completed work | Retain retry counts and deduplicate completed tasks. | Every successful retry is another completed task. | No retry data. |
| 10. Records finish reasons or truncation so shortened answers are not silently counted as equivalent work | Record finish reasons/truncation. | Treat capped short answers as equivalent completed tasks. | No stopping/outcome detail. |
| 11. Defines accepted tasks/hour using distinct tasks and linked task-acceptance evaluation | Accepted distinct task count per hour links rubric/eval IDs. | HTTP 200 count is accepted tasks/hour. | Only gives tokens/second. |
| 12. Keeps retry and tool-wait time inside the declared end-to-end task measurement boundary | End-to-end task wall time includes retries and tool waits. | Subtract all retry/tool time from task throughput. | No timing boundary. |
| 13. Matches actual context/output distributions and cache cohorts across compared runs | Match actual length mix and cold/warm prefix cohorts. | Compare warm short answers with cold long answers. | No length/cache controls. |
| 14. Collects preemption and memory evidence during the sweep | Capture memory/headroom and preemption across sweep. | Infer memory safety from aggregate throughput. | No memory or preemption evidence. |

## context-limit-versus-kv-pool

| Assertion | Satisfying example | Contradictory near miss | Omitted evidence |
|---|---|---|---|
| 1. Distinguishes the request admission limit, allocated KV pool and actual resident token demand | Separate 16K cap, allocated pool, and live 4K+1K tokens. | A configured cap is a per-request fixed allocation. | Only repeats the flag name. |
| 2. Rejects automatic memory halving or concurrency doubling at unchanged actual token lengths | Fixed actual lengths imply no automatic half-memory/double-capacity claim. | 32768 to 16384 guarantees a 2x capacity increase. | Does not evaluate the claimed improvement. |
| 3. Requires memory profiling and a matched workload/SLO measurement before claiming improved capacity | Re-profile memory and compare matched SLO sweeps. | A changed startup ratio alone proves capacity gain. | No verification plan. |
| 4. Checks whether the lower limit rejects or truncates tasks rather than assuming quality is unchanged | Check newly rejected or truncated long tasks. | Discard rejected tasks and call the test faster. | No task-outcome check. |
