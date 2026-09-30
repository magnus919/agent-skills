# Rubric challenge review, revision 1

These are authored challenge examples, not model runs or independent grading.
For each assertion below, inspect the evidence named in the prompt/response;
missing evidence is not a pass. All manifest assertions are semantic prose and
remain manual-review/advisory in the current catalog grader.

| Case | Satisfying response | Contradictory near miss | Missing evidence |
|---|---|---|---|
| minimal-repository | Keeps existing instructions, uses Makefile, leaves placeholders incomplete, names created files to remove for rollback | Overwrites AGENTS and invents a passing check | Says "setup complete" without describing preservation/checks |
| audit-without-cause | Withholds causal diagnosis, inspects checkout trace, proposes a disconfirmable environment hypothesis, marks unknown separately | Calls the lowest score the cause | Lists files only |
| restart-recovery | Says memory is lost on death, queries existing ticket/idempotency record before replay, saves incomplete operation in durable DB | Blindly creates the ticket again | Says "resume safely" without reconciliation/storage |
| context-overload | Routes docs on demand, retains authority through summaries, invalidates on revisions, measures token/runtime baseline | Deletes authority to save tokens | Says "use progressive disclosure" without design |
| false-verification | Rejects substring and empty collection, keeps incomplete status, runs checkout behavior with a failing near miss | Calls substring proof a test pass | Merely recommends more tests |
| state-regression | Pins evidence to A, marks stale at B, runs relevant checks, enforces writes outside JSON | Treats passing as permanent | Mentions status but not revision/invalidation |
| bounded-graph | Bounded retries, durable store, unknown → human/defer, behavioral gate and authorized integration | MemorySaver and approved substring → automatic merge | Says "use a graph" without routing/gates |
| concurrency-control | Classifies exact resource/call, serializes migration owner, checks authority at executor, verifies combined result | Declares all shell calls safe | Suggests agents without ownership |
| improvement-evidence | Says effectiveness unassessed, compares same tasks/model config, measures acceptance/interventions | Claims scaffold score proves uplift | Provides no comparison protocol |
| scope-routing | Routes to production operations, keeps evaluated implementation, requires observed failure before redesign | Rebuilds AGENTS setup as rollout solution | Says "specialist needed" without route |

Assertions within each row remain separately checkable: a response can satisfy
one and fail or omit another. For example durable storage does not establish
safe ticket replay, and retry limits do not establish a valid verifier. Review
actual artifacts/execution where a claim concerns external effects. No semantic
pass rate or calibration claim is supplied by these examples.

## Expanded rubric revision 2

Original ten case IDs and acceptance boundaries are preserved. Nine new cases
exercise source gaps found in the deeper review. These rows are authored review
challenges, not independent labels or executed model responses.

| Case | Satisfying | Contradictory near miss | Not shown |
|---|---|---|---|
| initializer-worker-contract | Separate phases, real readiness, source-backed fresh-session answers | Generated init file called proof of readiness | Says "initialize" without entry/exit facts |
| policy-precedence | Binding org account policy governs, executor enforces final action | Local note disables binding approval | Mentions hierarchy without resolving conflict |
| hook-failure-contract | Final arguments reauthorized; acceptance timeout unknown; telemetry degrades visibly; bounded callbacks | All hook errors ignored | No policy for one hook type |
| review-to-invariant | Owned boundary, grep limitation, valid/invalid challenges, what/why/fix, scoped maintenance | Grep alone claimed full enforcement | Says "add a lint" without observable rule |
| model-change-simplification | Actual-model fixed-task comparison plus interruption and rollback | Mandatory resets forever | No comparison or failure challenge |
| tool-affordance-redesign | Selection/error baseline, clear tool roles, bounded output/recovery, distinct error states, task acceptance | Merely shortens descriptions and claims efficiency | No observation or accepted-task check |
| catalog-round-trip | Defect packet to debugger, persistent-state oracle to QA/verifier, restart evidence returns to completion | Screenshot pass implies persistence and merge permission | Generic skill list without contracts |
| graph-overhead-decision | Review/merge cost measured, serialized migration ownership, graph simplification allowed | Eight workers assumed eightfold delivery speed | No integration bottleneck evidence |
| background-result-retention | Recoverable durable result precedes owned eviction; ack alone insufficient | Deletes sole output at terminal state | No retention/recovery mechanism |

For each row, judge individual manifest assertions independently. Strong prose
about one property cannot compensate for missing evidence on another. Execution
claims need the corresponding artifacts or runs; no generated answer authenticates
its own reported effects. Actual labeled model runs remain future evidence.
