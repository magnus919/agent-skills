# Execution report: second pass

Date: 2026-10-23. Actual model execution and advisory semantic review are recorded separately. No human adjudication or hiring-outcome validation is claimed.

## Scenario execution

All 18 original case IDs and eight added content/regression cases were executed: 26/26 distinct response records are stored in `execution/cases-1.json`, `execution/cases-2.json`, and `execution/cases-3.json`, plus `execution/final-regressions.json`. Workers received only prompts and raw fixtures, with no expected outcomes or assertions. Each batch used one model-agent context with instructions to treat tasks separately; these are not independently randomized model runs. No external provider calls, private interview data, or live hiring systems were used.

The added cases cover whole-transcript evidence across later probes, technical task semantics with a counterexample, unsupported causal attribution, correcting erroneous feedback, concrete teaching assessment, and bounded revision. Existing IDs and assertions were retained.

## Separate semantic review

A fresh model-teacher reviewed the initial saved outputs against every assertion in those cases: 24 cases, 82 assertions, with 82 suggestions of met and none of not_met/not_shown. See `execution/advisory-review.json` for exact excerpts and reasoning. These suggestions are advisory; they do not create a semantic release pass or establish accuracy against independent labels. The primary agent also read all outputs.

The initial 24-case review is preserved unchanged; its manifest hash predates the two appended regression cases. Reviewer ambiguities include implicit refusal to invent numbers, multipart wording within a single interview question, and inferred relevance to a senior analyst role. The current outputs were usable under the intended task interpretations. These are observations to challenge in future evaluation, not reasons to inflate certainty.

## Actual interactive sessions

| Saved sequence | Actual extent | Observations | Limit |
|---|---|---|---|
| `execution/coaching-session.json` | Four user turns and four assistant turns | Baseline critique, factual elicitation, outlined retry, different-question attempt, evidence-linked debrief, stop | Synthetic improving replies supplied by the primary agent; does not prove a human learned |
| `execution/simulation-session.json` | Four user turns and four assistant turns | Exactly three questions, no mid-round coaching, debrief after third answer, requested stop | Hypothetical reasoning only; no actual workplace performance established |
| `execution/interviewer-session.json` | Four user turns and four assistant turns | Role clarification, 30-minute plan, leading-probe correction, coached neutral retry, evidence recording, stop | Retry echoed a supplied neutral probe, so independent interviewer transfer was explicitly not claimed |

The primary agent supplied synthetic user replies incrementally after observing the coach's actual responses. The worker did not write both sides in one prompt. This verifies interaction protocol under those replies, not user improvement, delayed retention, or the quality of unscripted human participation.

## Source binding

`execution/source-inventory-before-trials.json` records the skill-file hashes before the initial 24-case and session trials. Later inclusion/source additions and two extra templates are tracked in Git and the final inventory; a focused accommodation regression is saved separately; later factuality/adaptation regressions are also saved. The inventories are local provenance records, not the repository's release-freeze contract.

## Content defect found and repaired

The separate content review found that the worked transcript's facts-only rewrite borrowed urgency from another incident. This was a material factual-fidelity defect. The unsupported timing was removed and source action order retained. The original finding and follow-up verification remain in `content-review.md`. A new cross-incident rewrite case was executed and reviewed; the actual response keeps the incidents separate. An unfamiliar-profession case also exercised the new adaptation method. Both outputs are in `execution/final-regressions.json`.

The delta model-teacher review in `execution/regression-review.json` suggested met for six assertions in the two new cases, bringing distinct scenario coverage to 26 cases/88 assertions. The inclusion-reference rerun separately exercised three existing assertions, excluded from the distinct denominator. This remains advisory evidence, not a release pass.

## Failures and unresolved work

No additional material response defect was observed in the bounded scenario/session trials after the content correction. The separate advisory reviewer recorded wording ambiguities above. Do not infer that failures cannot occur or that model-teacher agreement is independent ground truth. Domain correctness beyond the supplied synthetic tasks, extended human interactions, translated transcripts, audio/video delivery, and real employment outcomes remain unassessed.

First-pass observations and the broader unrelated sandbox test failures remain in `validation.md`. Full repository test-suite success is not claimed. Focused structural, schema, ratchet, and generated-artifact checks are recorded separately when completed.

## Final local verification

The staged implementation passed:

- `python3 scripts/validate-evals.py`: 189 valid manifests, including all 26 current coaching scenarios.
- `ruby scripts/validate-skills.rb`: 189 canonical skills accepted.
- `ruby scripts/validate-skill-quality.rb --base origin/main`: four changed skills, zero errors/warnings.
- `python3 scripts/eval-coverage.py --modified-from origin/main`: 189/189 schema-valid, 100%, no ratchet regression.
- `python3 scripts/test-eval-validation.py`: 27 tests passed; validator code unchanged after this run.
- Bundle manifests and lifecycle matrix: eight accepted, generated files current.
- Claude marketplace, Codex packaging, and llms.txt: current.
- AGENTS consistency and script-test conventions: passed.
- Entry point: 110 lines; all 36 references within 60,000 characters.
- All saved execution JSON parsed; 26 distinct nonempty case responses matched the current roster; all 82 initial advisory-review excerpts were found verbatim; three sessions each contained four incremental user/assistant exchanges. These are structural evidence checks, not semantic proofs.
- `git diff --cached --check`: passed.

No whole-repository executable-suite pass or remote CI result is claimed. No executable implementation scripts were added. The exact local commit is reported at delivery; final source hashes are in `execution/source-inventory-final.json`.
