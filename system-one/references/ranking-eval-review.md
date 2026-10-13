# Pairwise ranking eval review

These are author-reviewed rubric challenges, not executed agent outputs or
validated behavioral passes. Stable new IDs: `pairwise-ranking-method-choice`,
`pairwise-ranking-graph-boundaries`, `pairwise-ranking-evidence-readout`.
All assertions are semantic and require visible reasoning/artifacts; Jev triage
does not turn them into a release gate.

| Case / assertion | Satisfying response | Contradictory near miss | Missing evidence |
|---|---|---|---|
| method-choice / strong control | Uses independently meaningful relevance levels for Score | Uses numeric-only levels and declares Choice superior | No control rubric shown |
| method-choice / same candidates | Pairs arms on the same frozen shortlists | Gives Choice better candidate recall | Candidate construction unspecified |
| method-choice / resource boundary | Counts pairs, tokens and complete-ranking time separately | Calls eight pair questions equivalent to eight Scores in cost | Only request count shown |
| method-choice / rejection | Separates absolute usability from relative preference | Auto-accepts the winner of an all-irrelevant shortlist | No treatment of unsuitable winners |
| method-choice / independent labels | Uses labels independent of tested Jev outputs | Jev grades its own ranking | Label provenance absent |
| graph-boundaries / connectivity | Rejects a comparison graph with disconnected components | Uses ridge to make disconnected candidates comparable | Connectivity not checked |
| graph-boundaries / unequal opponents | Uses an opponent-aware fit or declares the limitation | Sorts raw wins from unequal comparison schedules as fair | Schedule omitted |
| graph-boundaries / fitting | Declares identifiability, regularization and convergence checks | Treats a finite parameter vector as validated model fit | Fitting choices absent |
| graph-boundaries / symmetry | Maps reversed positions back to original candidate IDs | Counts an A-label agreement after swapping passages as stability | Candidate mapping omitted |
| graph-boundaries / diagnostics | Compares final ranking with independent labels despite stable pair verdicts | Treats no cycles as correctness | Only repeat agreement reported |
| evidence-readout / scoped recommendation | Retains cheaper, better Score for the observed workload | Promotes pairwise after it loses quality and cost | No adoption decision |
| evidence-readout / uncertainty | States effect interval and holds broad claims under exploratory design | Calls an insignificant result equivalent | Interval or design classification absent |
| evidence-readout / aggregation attribution | Does not credit Bradley–Terry when win totals have identical ranking | Claims Bradley–Terry caused gains solely from all-pairs results | Aggregation ablation absent |
| evidence-readout / terminal accounting | Preserves the failed pilot and identifies a fresh amended study | Regrades old failure under the relaxed validator and merges runs | Protocol history omitted |
| evidence-readout / evidence scope | Separates ranking experiment evidence from skill behavior evidence | Treats valid portable eval JSON as proof enrichment helps agents | Skill behavioral evidence unspecified |

Material rubric change: introduces a distinct ranking-method comparison,
incomplete-graph/fitting review, and negative-evidence adoption decision. Existing
case IDs and assertions are preserved. Equivalent implementations are allowed;
incidental wording, solver package and exact model parameters are not asserted.
