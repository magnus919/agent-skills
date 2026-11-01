# Performance optimization audit — #768

**Recommendation: no skill change for the inspected scope.** The current skill
supplies the decision mechanisms for all seven inspected fixture tasks. The local
example still executes correctly. This is source/task inspection plus synthetic
execution, not a new behavioral comparison or evidence that real users always
receive good outcomes. No skill implementation or production change is included.

## Revision, sources, and prior work

Source revision: `6eeef1dfbe2348191b0866acdfb7a8b470186e63` (2026-11-01).
`execution.json` records hashes for every skill file and environment/command/exit
receipts. `protocol.md` records the bounded decision rule before execution.
The seven task prompts, expected outcomes and stable IDs are preserved in the
[pinned manifest](https://github.com/magnus919/agent-skills/blob/6eeef1dfbe2348191b0866acdfb7a8b470186e63/performance-optimization/evals/evals.json).
They are authored reproducible fixtures, not participant reports. The findings below
are analyst inspection, except where an execution receipt is explicitly named.

Reviewed SKILL.md, README, all four references, the optimization-record template,
example source, and all seven eval cases. No scripts/ directory exists; the runnable
example lives under examples/. No missing script is inferred from that layout.

Completed prior work:

- [#572](https://github.com/magnus919/agent-skills/pull/572), merged as
  `fc5805d72f62e318983f241eaf0068a348f22c71`: added diagnosis, executable
  walkthrough, repeated full-CLI timings, A/A, failure/timeout and field rules.
- [#594](https://github.com/magnus919/agent-skills/pull/594), merged as
  `0f30a0c5f245569fd49e710e3e5ffd8c490f71d9`: split compound rubric claims.
- [#596](https://github.com/magnus919/agent-skills/pull/596), merged as
  `659722072328178152b33f38af07a8593f254877`: clarified environment parity,
  warmup, and representative-workload prerequisite. Advisory pseudo-label evidence
  was explicitly limited; it is not human calibration or a gate.

Also inspected `docs/performance-optimization-execution-evidence.md`. Its earlier
single-run model comparison and temporary raw-trace paths were not re-executed or
verified here; they are historical context, not current behavioral proof.

Primary comparisons checked 2026-11-01:

- [Google Benchmark user guide](https://github.com/google/benchmark/blob/main/docs/user_guide.md): repetition, warmup, and random interleaving support the skill's benchmark design. It does not establish a universal run count or threshold for this fixture.
- [Go diagnostics](https://go.dev/doc/diagnostics): profiling and tracing answer different questions, and diagnostic interference matters. The skill already separates CPU, waits, and journey boundaries.
- [web.dev field/lab workflow](https://web.dev/articles/vitals-tools): lab diagnostics and actual user measurements differ. The skill already withholds field claims from synthetic results.

## Task matrix and observed inspection outcomes

All rows inspect the complete pinned case against the cited source sections. The
supported disposition is this audit's application of the instructions; no fresh
agent session was run and no semantic grader pass is asserted.

| Case ID / decision | Relevant current coverage | Supported disposition from inspection | Gap or limit |
|---|---|---|---|
| unmeasured-user-journey: optimize without agreed loaded event | SKILL loop 1–3; measurement-and-benchmarks “Measure the boundary users feel”; record “Journey and decision” | Define dashboard interaction-to-usable-result boundary, build/workload slices, countermetrics, then baseline; no speculative fix | No telemetry fixture supplied, so actual event correctness remains untested |
| noisy-benchmark-comparison: 82 ms → 77 ms on busy host | SKILL loop 4–5; measurement-and-benchmarks “Build a faithful laboratory proxy”; experiment-and-rollout 1–6,9 | Inconclusive; freeze representative payload/environment/warmup, repeat comparable runs, retain spread; no 6% user-win or gate claim | No repeated parser data available; cannot quantify its uncertainty |
| profile-guided-service-optimization: repeated permission checks | SKILL loop 3–5; diagnostic-guide CPU/wait rows and triage 3–5 | Reproduce large-account slice; verify critical-path/profile boundaries; one reversible caching/indexing hypothesis only if permission semantics preserved | No target code or authorization lifetime supplied; do not prescribe caching as proven fix |
| proxy-metric-validation: fewer DOM nodes | measurement-and-benchmarks proxy calibration and A/A paragraphs; experiment-and-rollout 9 | Keep node count diagnostic until rendering outcome and harmful counterexamples calibrate its domain; no immediate strict ratchet | No field correlation data; no gate validation |
| production-rollout-and-field-read: 18% staging query gain | SKILL loop 6; experiment-and-rollout 7–8; record “Review and field check” | Lab-supported claim only; named owner, bounded rollout, abort/rollback plan, matched segments; deployment remains unauthorized | No deployment performed and no field outcome available |
| bounded-stop-and-routing: three noisy hypotheses | SKILL loop 7 and “When not to use”; experiment-and-rollout stop rule | Stop tuning, preserve inconclusive evidence, ask owner whether measurement improvement is worth cost; route SLO/capacity/tool work outward | No evidence justifies another week of micro-optimization |
| failed-attempts-and-field-slices: faster median with timeouts | measurement-and-benchmarks attempted-run and field paragraphs; experiment-and-rollout 4,8 | Retain failed attempts, completion rate, explicit timeout rule, and matched build/platform/workload/cohort windows; successful median alone insufficient | No timeout counts supplied; cannot produce aggregate success rate |

No repeated missing decision mechanism or severe boundary defect was demonstrated.
These are source coverage findings, not seven observed behavioral passes.

## Executed example

The existing command `python3 performance-optimization/examples/membership_workload.py
measure --runs 9` completed nine alternating pairs (18 child invocations), returned
exit 0, and matched the fixed digest `1f723a23379b4b20` in both modes. Scan median
was **0.138513 s**, indexed median **0.042513 s**: a local median difference of
96.000 ms for the declared process-start-to-validated-stdout boundary. Raw samples
are in `execution.json`. No new performance gate, causal population estimate, memory
claim, or field improvement follows from this result.

Both documented profile operations ran after correcting an audit-author quoting
error in the first invocation. The invalid invocation and its SyntaxError are
preserved; it never executed the fixture and is not a skill failure. Corrected
profiles returned exit 0: scan 4,226,165 calls / 0.318 s; indexed 5 calls / 0.001 s.
Profile durations are diagnostic and are not compared as unbiased wall time.
`measure --runs 0` rejected the input with exit 2 as expected. No fixture source
was changed to obtain these results.

## Coverage map and remaining uncertainty

| Concern from issue | Coverage and limit |
|---|---|
| Measurement before optimization and reproducible baseline | Explicit loop 1–4, record fields, same workload/build/environment, preserved raw runs |
| Latency / throughput / tail / I/O / concurrency | Journey definitions, latency distributions, diagnostic CPU/wait/queue/I/O and throughput rows; no live multi-threaded system was exercised |
| Memory / cost / energy | Named primary outcomes and countermetrics in loop 1; heap/RSS diagnosis present; energy/cost instrumentation not demonstrated in this audit |
| Local versus architecture/database/network/capacity/reliability | Critical-path partition and explicit owner routes; a database problem may be optimized here but named-tool operation and capacity policy retain their owners |
| Regression budgets / validity / warmup / variance / overhead | Baseline and experiment rules plus record fields; strict CI ratchet requires A/A, representative calibration, practical threshold and noise evidence |
| Statistical uncertainty | No universal threshold or run count; repeated/interleaved distributions and inconclusive disposition; this synthetic run is not a population study |
| Language/runtime examples | Python executable plus Go diagnostics references; insufficient evidence for adding per-language manuals |
| Discoverability versus capability | Current description explicitly covers slow apps/services/workflows/hot paths and measurement-first work. No client activation was executed, so no routing defect or improvement rate is claimed |

## Rejected ideas and smallest next step

- A new performance skill or generic checklist duplicates #572's loop and owner routes.
- More language-specific walkthroughs are speculative without recurring task failures;
  named-tool operations belong in the named tool skill.
- A strict median-speed threshold from this run would repeat the proxy/noise mistake
  the skill already warns against.
- Turning the illustrative runner into a production benchmark platform would widen
  scope. It exits on child failure and does not aggregate partial failed-run samples;
  that is a documented audit limitation, not evidence that it is safe for arbitrary
  production benchmarking. No failing child occurred in this bounded execution.
- Raw install growth is a prioritization signal only. No install total was used as a
  unique-user count, demand measure, successful activation, or user-value result.

**Smallest useful next increment: no catalog implementation now.** Preserve this
report and seek a maintainer-approved real investigation where the agent fails to
retain full-command baseline/candidate evidence, mishandles timeouts, or misroutes a
bottleneck despite these instructions. Compare identical tasks against this pinned
skill with independent evidence review before changing it. Expected value: test the
remaining behavioral uncertainty. Effort: bounded by the selected real task and its
privacy constraints; no participant or cost estimate is fabricated. Verification:
actual invocation traces, raw attempts including failures, correctness checks,
user-boundary measures, and explicit lab/field status. A recurring demonstrated
failure would justify a separately approved implementation issue.
