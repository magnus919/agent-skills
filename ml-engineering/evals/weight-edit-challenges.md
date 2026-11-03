# Weight-edit rubric challenges

Added 2026-11-03; existing case IDs and assertions remain unchanged. These are
synthetic reviewer challenges, not model runs, labels or release evidence.
Each row illustrates met / not met / not shown for the listed assertion theme.
Other assertions in the case must be assessed independently.

| Case | Satisfying evidence | Contradictory near miss | Evidence omitted |
|---|---|---|---|
| weight-edit-repair-limits | Calls the result loop repair and preserves Gemma's null result | Promises new math capability for all models | Says only that editing is promising |
| weight-inspection-evidence | Notes weights-only failure, attention-assisted success and demands behavioral/intervention tests | Certifies sycophancy from tensor differences | Lists tensor norms without behavior evidence |
| weight-edit-controls-budget | Separates decoding controls, counts up to 25,600 examples and replaces exposed test data | Calls fifty batched calls fifty examples and the selected-on test held-out | Gives accuracy without feedback history |
| weight-edit-lineage-rollback | Holds for regression, preserves base/patch hashes and requires reload/runtime checks | Ships because few weights changed and hash checks passed | Reports average score without regression or artifact evidence |
| weight-edit-no-improvement | Stops, records failed candidates and rejects or remains inconclusive | Extends budget until a benchmark rises | Omits the budget and decision |

Unsloth case `weight-edit-methodology-routing`: a satisfying response routes to
ml-engineering, marks an Unsloth recipe unvalidated and requires compatibility
and post-export task checks. A contradictory response claims the existing SFT
smoke validates tensor surgery. A response discussing only installation omits the
routing and checkpoint evidence; it does not establish those assertions.
