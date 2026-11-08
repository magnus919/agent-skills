# Workload-first local serving selection

Use this methodology when choosing or comparing a local inference stack. Engine
operation belongs in [llama-cpp](../../llama-cpp/SKILL.md) or
[vllm](../../vllm/SKILL.md). Include SGLang as a candidate when compatible; this
reference is not a SGLang installation guide. Record the plan in
[local-serving-study](../templates/local-serving-study.md), with the
[primary-source record](local-serving-sources.md) for compatibility claims.

## 1. Define the decision before benchmarking

Describe the actual task, model family and quality floor, hardware/OS, device and
host memory, input-length distribution, maximum retained context, output-length
distribution, latency targets, offered load and privacy constraints. Separate:

- One interactive user who values first-token and per-token responsiveness.
- A stream of independent jobs where throughput within deadlines matters.
- Tool-using agents whose inference bursts alternate with tool execution/waiting.

Short-prompt decode tests help diagnose a kernel; they do not establish capacity
for long-context work or prove useful agent productivity. Select candidates that
can meet the model, tokenizer, tool parser, structured-output and hardware
requirements before tuning them. Treat unsupported combinations as exclusions
with evidence, not poor benchmark results. Do not rank engines universally.

## 2. Keep the denominators separate

| Measure | Definition and boundary |
|---|---|
| Single-stream decode rate | Tokens from one request divided by that request's decode interval; report the interval convention and token count, not only tok/s. Excludes prefill if labeled decode-only. |
| Aggregate generation throughput | Total output tokens across requests divided by one shared elapsed measurement window. Never add per-request rates with different windows. Report input/prefill throughput separately. |
| Request latency | Queue delay, TTFT, inter-token/TPOT, and end-to-end completion latency, with p50/p95/p99 and sample count. For one-token outputs TPOT may be undefined; report it as such. |
| Accepted tasks/hour | Unique tasks meeting the frozen task/trajectory acceptance criteria divided by elapsed hours over the whole cohort. Include retries, queueing and tool waits in that window; never divide by summed concurrent task times. |
| Reliability and quality | Full expected roster, accepted/failed/incomplete counts, errors, retries, timeouts, truncations and critical regressions. Show denominators and unresolved judgments, not only surviving successes. |

For a finite cohort, predefine start at first dispatch and end after all tasks
reach a terminal state or the registered deadline; a timeout still consumes its
wall time. In a fixed-duration stream, freeze arrival and drain/censoring rules
before running and report unfinished tasks. Do not count attempts as unique
accepted tasks. Failed attempts can consume throughput without useful output.
A synthetic example: 30 accepted tasks in a ten-minute cohort is 180 accepted
tasks/hour, regardless of how many tokens failed attempts generated. This is
arithmetic, not a measured system result.

## 3. Measure inference overlap, not just agent count

An agent roster of ten is not evidence of ten simultaneous model requests. Use
minimized timestamped events to distinguish agent lifetime, ready work, client
in-flight requests, server queueing, active prefill/decode sequences and tool wait.
Report the distribution and peaks of actual inference overlap and whether the
client held the requested concurrency. Keep client outstanding requests separate
from scheduler batch size, maximum resident sequences and token budgets.

Test both sustained inference pressure and a representative agent trace with
realistic tool duty cycles. A tool-heavy workflow may underfill the accelerator;
a synchronized return from tools may create a burst. Do not extrapolate sustained
capacity from idle agent count, or hide tool latency in an engine speed claim.

## 4. Freeze comparable conditions

Pin model/base/adapter and quantized artifact hashes, tokenizer and chat-template
revisions, engine version/commit, backend/plugins, build, driver, hardware, memory,
power settings, background load, harness revision and the task roster. Keep prompt
content, retained context, output limits, stop rules, sampling, seed/repeat policy,
thinking/reasoning mode and budget, tool schema, retry/timeout/selection budgets
and acceptance rubric matched.

If one engine needs a different quantization, template or reasoning setting,
label the result a **whole-stack comparison**, not an isolated engine effect.
Keep a controlled comparison distinct from separately tuned candidates, each
with an equal, declared tuning budget. Do not silently shorten prompts or disable
thinking to make a candidate fit. Reasoning tokens consume resources even when
not displayed; state whether each metric includes them.

Run separate cold-prefix, warm shared-prefix and non-shared-prefix conditions
when production uses them. Prefix reuse can avoid repeated prefill; it does not
remove the cost of generating new tokens. Record cache state and observed reuse
rather than assuming a cache flag guarantees hits. Repeats must use comparable
cache reset/warm-up policies and realistic shared prefixes, not privileged reuse
available only to one candidate.

## 5. Size memory before increasing load

Use [quantization-inference, section 6](quantization-inference.md#6-kv-cache-quantization)
for the architecture-specific KV calculation and corrected 10 GiB example. Budget
loaded weights, retained KV/recurrent state, activations/workspace, graph/batch
buffers, runtime/allocator overhead and headroom separately. Include quantization
metadata and nonquantized tensors. Distinguish GB from GiB, logical payload from
allocated pools, and device memory from host/unified memory. Prefix reuse does
not make all sequence storage free. Read actual allocation and peak-use evidence.

Memory fit at one request does not imply fit at eight, ten or a longer context.
Validate the checkpoint's supported context separately from cache arithmetic.
Account for page rounding, sliding windows, hybrid state, draft models and
sharding/replication rather than applying one formula to every architecture.

## 6. Run a configurable, bounded sweep

Use **1, 2, 4, 8, 10** simultaneous inference requests as an initial ladder,
not a four-request test or a hard limit of ten. Customize it for the workload and
extend beyond ten when demand, headroom and the question warrant it, for example
12 or 16. Record whether each setting controls client in-flight requests or a
server limit; neither alone proves active inference overlap.

Before running, choose representative short/median/long contexts, output and
reasoning budgets, enough requests and repeated runs for the target tails, an
elapsed-time/sample budget, and explicit safety/SLO limits. Distinguish closed-loop
concurrency from open-loop arrivals: at a fixed arrival rate, record backlog
growth, admission/rejections and drain time. A short closed-loop run does not
prove an open-loop service remains stable.

At each level collect all metrics above and memory peaks. Do not prescribe
untested numeric engine settings from a different GPU. The official vLLM tuning
guide describes scheduler/memory and preemption tradeoffs; SGLang's guide similarly
links queued/running requests to KV pressure. Their offline throughput advice is
not automatically an interactive latency target.

Stop increasing load on an OOM, unsafe memory pressure, repeated preemption or
request retraction, unbounded queue growth, timeout/error/SLO violations, a
critical quality failure, or the preregistered sample/time budget. Define what
counts as repeated or unacceptable before the run. Also stop on a predeclared
throughput plateau across repeated levels when more load answers no useful
question. Preserve the failing level as **measured/failed** or **aborted**, with
its observed results and stop reason. Mark only unexecuted higher levels **not
run**; do not erase failed measurements or infer untested results. If safe, refine between the last acceptable
and failing levels inside the remaining budget. Do not rerun indefinitely until
a winner appears. Ten passing requests is a measured point, not a capacity cap.

## 7. Reuse task evidence; do not invent a second grader

Use the task, trajectory, dataset and grader contracts from
[agent-evals-and-observability](../../agent-evals-and-observability/SKILL.md).
Use execution evidence for task artifacts/side effects and independent rubric
judgment where needed. Model-judge opinions are not ground truth, and faster
incorrect or unauthorized outcomes are not accepted tasks.

For matched **single-attempt** paired outcomes, retain the existing
[task-run examples](../templates/task-run-baseline.json) and
`ml-engineering/scripts/compare_task_runs.py`. Its contract pins dataset, harness,
decoding and budget hashes plus the complete expected roster. Timeouts remain
outcomes; absent, not-run or infrastructure-failed cases make the comparison
inconclusive. Do not fabricate matching hashes to bypass a mismatch.

The helper describes solve-rate changes, paired gains/losses, latency and grouped
uncertainty. It does **not** calculate accepted tasks/hour, account for overlapping
wall time, validate retries, run inference or grade task semantics. Attach the
cohort start/end window, retry/attempt ledger, resource telemetry and independent
acceptance evidence separately. Compare matched concurrency levels; varying a
concurrency/load budget is its own explicitly labeled study, not a controlled
paired model effect. Retry-enabled agent studies use the existing agent-evaluation
run report and budget contracts, not a renamed single-attempt receipt.

## Completion and decision

Finish with a supported operating point, rejected/inconclusive candidates,
quality and latency guardrail results, observed uncertainty, measured capacity
limits, untested conditions, rollback and an owner. Choose the simplest supported
stack meeting the workload; no winner is required. Structural/schema checks and
synthetic fixtures cannot establish real throughput, capacity, quality or release
approval. If runtime evidence is unavailable, deliver the plan and evidence gaps,
mark execution **not run**, and stop.
