# Server benchmark rubric challenges

Added 2026-11-08: `server-concurrency-context-sweep`,
`server-agent-throughput-accounting`, and `server-prefix-cache-measurement`.
Existing IDs and assertions are unchanged. These author-written challenge
examples clarify the new semantic assertions; they are not generated runs,
independent adjudication, a new grading system, or release evidence. Numbers in
the accounting case are illustrative inputs, not observed hardware results.
Each row maps to the corresponding case's 1-based assertion index. A missing
piece of evidence is not shown, not a measured negative result. Equivalent
wording or valid measurement implementations are acceptable.

## server-concurrency-context-sweep

| Assertion | Satisfying evidence | Contradictory near miss | Missing evidence |
|---|---|---|---|
| 1 | Editable outstanding-request levels 1, 2, 4, 8, 10 | Stops at 4 because the example does | No explicit load levels |
| 2 | Extend beyond 10 for demonstrated demand/headroom under the same stops | Calls 10 a universal maximum | No higher-load policy |
| 3 | Workload-derived short/normal/long token ranges include reserved output | Only short prompts, or fills the entire context with input | No context cohorts or token ranges |
| 4 | Fixture IDs and task acceptance thresholds are fixed before comparisons | Loosens quality at higher load | No fixture/quality contract |
| 5 | Freeze slots/context during load sweep; changed server setup gets a matched baseline | Increases slots and reduces context while attributing all improvement to load alone | No server/client variable control |
| 6 | Predeclared memory margin plus latency/timeout or overload stop limits | Pushes until repeated OOM without limits | No stop criteria |
| 7 | Eight/long stopped for margin breach; ten/long not run, capacity unknown | Marks ten failed or ten supported without running it | Omits disposition of the ten cell |
| 8 | Highest passing measured cell applies only to its tested conditions | Highest tested result is called the system maximum | No bound on capacity conclusion |

## server-agent-throughput-accounting

| Assertion | Satisfying evidence | Contradictory near miss | Missing evidence |
|---|---|---|---|
| 1 | Ten active = seven tool waits + three outstanding; two running, one deferred | All ten active agents counted as executing inference | No layer breakdown |
| 2 | Ten configured is not observed overlap; correlate request/slot times for sustained claim | Ten slots or a single occupancy snapshot proves ten concurrent decodes | No overlap-evidence assessment |
| 3 | 3600 × 18 / 120 = 540 accepted tasks/hour; retries do not duplicate accepted tasks | Counts 24 attempts as 24 accepted tasks or changes the denominator | No rate or derivation |
| 4 | Full 120-second window retains failed/retry/queue/timeout work | Removes timeout and retry time to raise the rate | No denominator policy |
| 5 | Aggregate 720 tokens/s can coexist with slower per-request decode | Declares every request 20% faster from aggregate alone | No aggregate/per-request distinction |
| 6 | Candidate misses fixed limit: p95 TTFT 9 s > 5 s | Accepts because aggregate token throughput rose | No guardrail verdict |
| 7 | Finish/truncation data missing; completeness of serving validation unknown | Assumes no truncation from missing fields | No mention of missing outcomes |
| 8 | Offline smoke validates only that completion path, not concurrent serving | Passing llama-completion proves ten-server-slot capacity | No scope assigned to the smoke |

## server-prefix-cache-measurement

| Assertion | Satisfying evidence | Contradictory near miss | Missing evidence |
|---|---|---|---|
| 1 | Cold common, warm common with varied suffixes, and diverse independent prefixes | Warm identical prefix is the only workload and is generalized to all agents | No cache/workload cohorts |
| 2 | Model warmed separately; cache coldness verified via isolated state or authorized reset | Calls a reused prefix cache-cold because the process was warmed | No cache-state preparation evidence |
| 3 | Cache-hit claim requires supported reused/evaluated-token evidence; absent data marked unverified | Matching text is treated as guaranteed hit | No cache-hit verification plan |
| 4 | Measures prefill/TTFT and decode separately; no automatic decode gain | Prefix cache guarantees faster token generation | No phase distinction |
| 5 | Capture installed revision/help; check matching server/benchmark source before fields/controls | Copies unverified cache options into an unknown endpoint | No version/source verification |
| 6 | k6 trend mixes prompt+completion per request duration | Calls that trend pure decode speed | No metric interpretation |
| 7 | Available server usage counts actual request tokens | Treats whitespace-split input estimates as exact model tokens | No token accounting source |
| 8 | TTFT and full-latency p50/p95 and sample counts | Average throughput is substituted for request latency distributions | No latency measurement plan |
| 9 | Aggregate prompt/generated rates use counts per wall window, separately from per-request rates | Sums request token rates and calls that aggregate throughput | No aggregate measurement plan |
| 10 | Same fixture acceptance checks for each prefix cohort | Replaces hard diverse tasks with easy repeated questions | No quality control |
| 11 | Record finish reasons and length/truncation outcomes | Counts every HTTP 200 as complete output | No completion-outcome plan |
| 12 | Counts errors and timeouts, including failed attempts | Omits failed attempts to make the benchmark look faster | No error accounting |
| 13 | Peak host/device memory and remaining margin are measured | Calls weight fit alone sufficient memory evidence | No memory observation plan |

Runtime claims need real measured artifacts in a separately authorized run.
These plan/assessment cases cannot prove a server was started, cache reuse
occurred, or any concurrent hardware capacity was reached.
