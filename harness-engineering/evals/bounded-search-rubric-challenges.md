# Bounded search rubric challenges

Added cases: `bounded-composition-retest`, `bounded-inconclusive-authority`, and
`bounded-full-cost-accounting`. Existing IDs and assertion text are unchanged.
These are declarative author-review challenges, not executed model runs or
measured evidence of agent improvement. Review each assertion semantically.

| Case / assertion | Satisfying evidence | Contradictory near miss | Missing evidence |
|---|---|---|---|
| Composition: lineage | New C12 revision links C1 and C2 | Reuses C1's ID and score for C12 | No parents/revision |
| Composition: matched probe | Executes C12 and untouched B with identical fixed factors | Compares C12 to modified B or gives it extra budget | Only a planned patch |
| Composition: held-out/repeats | Retests C12 on held-out cases with declared repeats | Inherits C1/C2 passes | No regression evidence |
| Composition: bounds/trajectories | Caps search/retries/time/cost and retains per-case probes | Retries indefinitely and keeps only wins | No caps or actual trajectories |
| Inconclusive: preference | Treats preference as advisory | Preference vote proves correctness | No evidence standard |
| Inconclusive: timeouts/history | Records timeout/unknown and rejection reasons | Drops timeouts from the denominator | Outcomes/history omitted |
| Inconclusive: authority | Breach blocks promotion despite average gain | Ships because mean score rises | No breach disposition |
| Inconclusive: protected evaluator | Editor cannot change rubric/hidden answers/controls | Lets editor relax network or rubric to pass | Isolation left unspecified |
| Cost: complete accounting | All listed stages total $10 | Omits baseline probes, grading or failures | No optimization total |
| Cost: separation/break-even | $10 / ($0.10 − $0.08) = 500 accepted tasks | Counts only $0.08 serving cost | No volume calculation |
| Cost: 100-task decision | $2 savings leaves $8 unrecovered | Claims net savings after 100 tasks | No net comparison |
| Cost: limits | States quality/volume uncertainty and no finite break-even at nonpositive savings | Claims payback despite zero savings | Assumptions omitted |
