# Local serving rubric changes and challenges

Added 2026-11-08. Existing case IDs are preserved. New cases exercise serving
methodology; these authored examples are reviewer aids, not executed model
responses, labeled quality evidence or release approval. Assertion numbers below
are one-based within each case. Assess each independently as met / not met /
not shown. A response can satisfy one row while contradicting another.

The existing `quantization-decision` assertion 2 now accepts method-appropriate
calibration or documented calibration-free methods, rather than demanding the
same calibration procedure for every format. Its expected outcome was updated
to match. All other existing assertions remain unchanged.

| Case / assertion | Satisfying evidence | Contradictory near miss | Evidence omitted |
|---|---|---|---|
| quantization-decision / 2 | Uses one frozen eval set and records GPTQ/AWQ calibration and a calibration-free BnB candidate | Claims every candidate must use the same calibration procedure | Lists formats without eval or calibration information |
| local-serving-workload-metrics / 1 | Reports request decode interval separately from all-output tokens per cohort window | Adds rates measured over unrelated windows as aggregate throughput | Gives only tok/s with no denominator |
| local-serving-workload-metrics / 2 | Thirty unique accepted tasks in ten cohort minutes means 180/hour | Divides by summed overlapping request latencies or counts attempts as tasks | Reports accepted count without elapsed time |
| local-serving-workload-metrics / 3 | Cohort clock includes queue, tools and retries | Resets the clock after each retry or drops tool time | No timing boundary for these stages |
| local-serving-workload-metrics / 4 | Logs active prefill/decode overlap separately from ten agent lifetimes | Calls ten mostly idle agents ten simultaneous inference streams | Mentions concurrency without evidence source |
| local-serving-workload-metrics / 5 | Retains errors/timeouts/unresolved tasks in the expected roster | Removes failed attempts before reporting reliability | Gives only completed token counts |
| local-serving-workload-metrics / 6 | Requires frozen task acceptance and critical-error limits | Chooses higher tok/s despite worse task acceptance | Reports speed with no acceptance criterion |
| local-serving-workload-metrics / 7 | Delivers a plan marked execution not run | Claims a successful benchmark without running one | Gives recommendations without execution status |
| local-serving-concurrency-sweep / 1 | Starts 1, 2, 4, 8, 10 with configurable levels | Stops by design at four | Does not specify test levels |
| local-serving-concurrency-sweep / 2 | Adds 12/16 if relevant and safe within budget | Calls ten the mandatory maximum regardless of evidence | No statement about demand beyond ten |
| local-serving-concurrency-sweep / 3 | Records client in-flight and measured active inference separately | Equates a max-sequences setting with realized concurrency | No overlap measurement |
| local-serving-concurrency-sweep / 4 | Covers median/long contexts and matched output/thinking budgets | Tests only tiny prompts then claims long-agent capacity | No length or reasoning protocol |
| local-serving-concurrency-sweep / 5 | Registers OOM/pressure and timeout/latency stop thresholds | Continues increasing after OOM to chase tok/s | No memory or reliability stop |
| local-serving-concurrency-sweep / 6 | Sets a time/sample cap and repeat-based plateau rule | Reruns without bound until a winner appears | No budget or saturation criterion |
| local-serving-concurrency-sweep / 7 | Saves failed C8 evidence, marks unattempted C10/C12 not run | Labels unattempted C10 as passed, or deletes failed C8 evidence | Omits higher-level execution status |
| local-serving-concurrency-sweep / 8 | Includes compatible SGLang with the same measurement protocol | Recommends SGLang unconditionally as fastest | Leaves SGLang unexplained |
| kv-cache-capacity-arithmetic / 1 | Shows 10,737,418,240 bytes = 10 GiB ≈ 10.74 GB | Repeats 320 GB for the stated single sequence | Describes cache growth with no calculation |
| kv-cache-capacity-arithmetic / 2 | Gives 80 GiB for eight and 100 GiB for ten independent sequences | Says ten sequences still use 10 GiB without sharing evidence | Omits batch scaling |
| kv-cache-capacity-arithmetic / 3 | Uses 8 KV heads and explicit resident-sequence multiplier | Uses query heads instead of KV heads | Does not identify which heads or batch count |
| kv-cache-capacity-arithmetic / 4 | States GB = 10^9 and GiB = 2^30 bytes | Labels 10 GiB exactly 10 GB | Uses only an ambiguous memory number |
| kv-cache-capacity-arithmetic / 5 | Adds weights, cache, workspace/buffers and runtime overhead | Treats cache payload or weight file as total memory | No full memory budget |
| kv-cache-capacity-arithmetic / 6 | Requires implementation-specific latent/recurrent accounting | Applies the ordinary GQA formula unchanged to all hybrids | No architecture limit |
| kv-cache-capacity-arithmetic / 7 | Calls 32K hypothetical and identifies original Llama 3's 8K context | Claims the arithmetic enables 32K on that checkpoint | No supported-context distinction |
| kv-cache-capacity-arithmetic / 8 | Requires actual allocation/quality tests and does not assert 24 GB fit | Declares fit from nominal INT4 size or a short demo | No deployment-capacity conclusion |
| serving-comparison-evidence / 1 | Declines long-context capacity proof from short-prompt/video rates | Promises ten long agents on 24 GB from the headline | No discussion of transfer limits |
| serving-comparison-evidence / 2 | Matches thinking, sampling, context and output before attribution | Calls thinking-off versus thinking-on an engine-only speedup | No settings comparison |
| serving-comparison-evidence / 3 | Compares warm/cold separately and attributes reuse to prefill | Calls prefix reuse elimination of new-token decode cost | No cache state discussion |
| serving-comparison-evidence / 4 | Keeps project source and disclosed denominator differences | Presents the author's result as independently replicated locally | No source or limitations |
| serving-comparison-evidence / 5 | Keeps timed-out and missing expected tasks with explicit statuses | Drops timed-out tasks from the roster | No coverage or failure handling |
| serving-comparison-evidence / 6 | Uses agent task/trajectory contracts and helper only for matched single-attempt receipts | Invents new grading semantics or hides retries in single-attempt receipts | No evidence-contract route |
| serving-comparison-evidence / 7 | Supplies separate cohort window and acceptance evidence | Says helper exit zero proves accepted tasks/hour or correctness | Does not explain the helper's scope |
| serving-comparison-evidence / 8 | Labels fixtures structural and runtime/quality not run | Calls synthetic/schema success production readiness | No separation of evidence types |
| gguf-version-security-boundary / 1 | Calls GGUF a tensor/metadata container | Calls the format an executable program | Says only to trust models |
| gguf-version-security-boundary / 2 | Separates parser bugs and executable dependencies from data format | Calls every GGUF automatically safe | No parser/runtime/code risk |
| gguf-version-security-boundary / 3 | Cites current experimental/under-optimized plugin-based support | Says vLLM has no GGUF path or always uses llama.cpp | No current support evidence |
| gguf-version-security-boundary / 4 | Checks release-specific support before applying plugin instructions | Claims the current path governed every historical release | Omits version boundary |
| gguf-version-security-boundary / 5 | Requires matched GPU workload data before speed ranking | Says AWQ is always faster | No performance comparison boundary |

Actual-output review requires real responses/artifacts. The manifest remains v1
and semantic assertions remain reviewable prose; no keyword hit, helper exit or
schema pass stands in for task acceptance. Use the repository's existing graders
and evidence contracts rather than adding a serving-specific grading system.
