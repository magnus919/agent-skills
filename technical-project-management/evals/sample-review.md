# Initial sampled behavioral review

Date: 2026-09-05. Reviewer: authoring assistant. These are actual captured responses,
not golden answers. Configuration: two fresh Codex subagent contexts, one with the
skill and one without; each answered the same three prompts. No model override was
requested. Model version, token use, and exact timing were not captured.

Candidate: precommit working tree on `codex/technical-project-management`, based on
`de968df`. Exact per-run content hashes were not captured. This is informal evidence,
not the repository's versioned runtime provenance or release-gate contract.

## Assertion review

| Case | Baseline | With skill | Evidence in captured outputs |
|---|---|---|---|
| expert-tpm-vendor-slip | 5/5 | 5/5 | Both expert responses calculate day 28 and 8-day variance, identify the old day-12-plus-10 inconsistency, keep vendor dates conditional, and give decision options without a primer |
| no-pm-small-team | 4/4 | 4/4 | Both team responses retain sales date as a target, seek accepted scope/authority, use actual part-time capacity, and propose a lightweight written decision system |
| shared-resource-network | 5/5 | 5/5 | Both schedule responses distinguish unconstrained day 6 from a feasible serial day 7, show the shared resource, and explain why a second specialist alone does not meet day 5 |

Outputs are retained in `samples/baseline-expert.md`, `samples/with-skill-expert.md`,
`samples/baseline-team.md`, `samples/with-skill-team.md`,
`samples/baseline-schedule.md`, and `samples/with-skill-schedule.md`.

## What changed after review

Both variants passed the original assertions. The expert response's baseline
consistency check and the resource response's day-7 reasoning were valuable but
not required by the initial manifest. Added those assertions without changing IDs.
The captured answers satisfy the strengthened checks too.

The with-skill team response supplied board columns and one-active-item-per-engineer
advice without diagnosing flow. The engagement reference now explicitly preserves
existing boards and routes WIP design to kanban-guru. The forecasting reference now
includes the small resource-feasible example. The script also gained bounded
resource-conflict output and a test during the review period. These refinements
were mechanically checked; the sample is not a rerun of the final revision.

## Limits and conclusion

These three scenarios did not distinguish skill-assisted from baseline quality.
Both scored 14/14 on the final reviewed assertions. Do not infer general improvement
or reliability from that result. Each variant used one context across three prompts,
so prompts were not individually isolated. Grading was not blind or independent,
and only three of twelve cases were exercised. The remaining cases are authored
contracts, not demonstrated behavioral passes. CI's fake-adapter run is a harness
smoke test, not additional model evidence.

Further evaluation should use individually isolated cases, a blinded reviewer,
and difficult multi-artifact project records, including contradictory status and
changing scope across several management cycles. The initial evidence supports
usable sample outputs and concrete refinements, not a "world-class" certification.
