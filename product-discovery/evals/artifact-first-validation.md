# Artifact-first interview validation — 2026-10-08

Issue: #674. Evidence: `artifact-first-run.json`; rubric challenges: `artifact-first-rubric-review.md`; routing prompts: `trigger-queries.json`.

## Hypothesis and method

Hypothesis: an explicit artifact-first entry reduces question batching and preserves a traceable small patch without restarting full discovery. This is not a claim that the previous skill cannot find hidden assumptions.

Compared the baseline at `96fbe0780a2fc2b7d063b613bfc1a5767e11b5d7` with the candidate in separate subagent contexts. Three synthetic artifacts each received two assistant interview turns, the same scripted answer facts across conditions, and the same explicit stop request. Full user-facing responses and answer facts are retained. The root model inspected the outputs unblinded (`reviewer_kind: model_teacher`). Source hashes and run limitations are recorded in the JSON. No elapsed-time, calibrated-accuracy, or human-acceptance claim is supported.

## Observed results

| Artifact | Consequential finding revealed by scripted exchange | Baseline | Candidate |
|---|---|---|---|
| Archive/restore | A1 excludes the proposed search path and introduces confidentiality; A2 leaves discovery unresolved and restoration permissions assumed. | Found recovery/access gaps; asked compound questions. Final text selects search exclusion while deferring discovery. | One question per turn. Retains conflicting search statements as unresolved rather than silently selecting one; marks admin-only restoration unvalidated. |
| Dashboard/email | A1 reveals requests for Monday staffing slides, no measured retention, and a founder-originated dashboard; A2 defers format. | Found the weak retention claim; asked three numbered questions per turn, some compound. Returned a useful targeted replacement. | One question per turn; follows up on the staffing decision. Patch cites facts/decisions and keeps the new preparation-time hypothesis unvalidated. |
| Account-access chatbot | A1 reveals that automation would remove manual ownership verification; A2 retains human approval and defers interface. | Already noticed that closures can hide bad recovery; asked multiple questions. Returned a constrained patch after stop. | One question per turn; adapts from resolution evidence to MFA authority. Preserves history-page constraint, human approval, and unknown success evidence. |

Both conditions identified material issues and stopped when instructed. The candidate's observed advantage was interaction shape and explicit provenance, not uniquely finding the problems. Candidate summaries can still be lengthy. Each synthetic exchange revealed a consequential issue absent from the initial draft, but scripted answers do not prove real interviewer effectiveness or customer value.

The separate prediction-blind routing screen selected all eight expected skill/mode combinations. Its reviewer noted that “Interview me about this draft” is ambiguous without product context. This is metadata routing by a model, not evidence that any installed host actually activates the skill. The broad stakeholder-mapping route remained distinct from artifact review.

## Disposition and remaining validation

Retain the bounded mode for review, with no new top-level skill. The screen supports its interaction contract on these examples; it does not establish general reliability or reduced human effort. Human review of real drafts and accepted patches remains pending. A reviewer should compare time/effort, irrelevant edits, missed decisions, and acceptance against the existing skill before claiming human value. No human sign-off or release-gated quality evidence is asserted.

## Repository checks

`make validate` passed (207 tests, 29 subtests; 66.06% coverage). Skill format, changed-skill quality, all eval manifests, the 27 focused eval-validator tests, catalog freshness, and the coverage ratchet passed. Existing eval case contents are unchanged. The broader `scripts/check-artifacts.py` check fails on the untouched Raleigh test `FireTests.test_cli_fire_group_filter_notes_pretransition_exclusion`; the identical failure was reproduced from an archive of baseline commit `96fbe0780a2fc2b7d063b613bfc1a5767e11b5d7`. It expects `2026+` in a warning for a relative `40w` window. This change does not modify Raleigh. Initial sandbox socket failures disappeared when the check ran with loopback access.
