# Teach Me validation record

Date: 2026-10-15. Review type: model review and simulated learner behavior, not
human adjudication or an educational outcome study. Candidate content digest:
`e967dfac0c1f519d4348f29d5158287e7fdba531ad836012ce1970e888c25382` (SHA-256 of sorted skill-relative repository paths,
NUL, file bytes, NUL for SKILL.md, references/*.md, evals/evals.json, and
triggers.json; excludes this report).

## Scope and method

Five independent tutor contexts received the skill, a realistic learner request,
and permitted resources, without expected outputs or grader assertions. The test
controller supplied subsequent simulated learner utterances in response to actual
tutor output. These were scripted test interactions, not real student outcomes.
A separate reviewer inspected the change and challenged the evaluation rubrics.
No paid experiments, external learner notes, schedules, or live-system mutations
were part of the tests.

The tutor contexts used the session's inherited model; a separately pinned model
identifier and reproducible generation harness were not captured. Private
transcripts include tool/source records. They are not redistributed here. These
observations are a bounded behavioral smoke test, not a fully replayable benchmark,
causal comparison against a baseline, or exhaustive pass of the portable manifest.
The manifest contains 22 cases; unexecuted cases remain unassessed.

## Observed scenarios

| Scenario | Observed behavior | Limits |
|---|---|---|
| SQL novice, five-minute goal | Inspected official PostgreSQL joins material; derived matching rows; corrected confident wrong answer; changed to plain text after explicit frustration/access request; stopped without a quiz or reminder | SQL examples hand-derived, not executed; no independent learner success claimed |
| Rusty algebra learner | Inspected OpenStax equality rules; checked calculations; accepted division before expansion; reduced hints; invited a break after a fresh correct solution without a stopping request | Narrow equation form; delayed retention untested |
| Curiosity-led continuation | After completion, asked learner what they wanted to explore; used the chosen algebra-to-graphing connection and a new five-minute goal; inspected new graphing material before teaching; honored subsequent explicit stop without a question | This lane reread the refined completion policy; graph drawing and far transfer untested |
| pandas 2.0 refresher | Recovered from failed version URL to official 2.0 documentation; identified removed append and concat replacement; skipped beginner programming instruction; stated code was documentation-checked, not executed | No pandas runtime execution or independent implementation claim |
| Offline/source failure | Withheld Bayesian instruction and asked for accessible material; then inspected a supplied ratio excerpt; ignored embedded upload instruction; used screen-reader-friendly text | Source was a supplied course excerpt with unknown author/date, not independently authenticated |
| Correct answer, wrong rule; hint dependence | Credited correct ratio arithmetic but corrected invalid generalization; offered a changed case; restored a small scaffold when learner could not start | Success after giving the operation remained assisted |
| Ineffective pivots | Stopped when learner reported repeated ineffective approaches and declined more; named unresolved independence and offered optional human support | Reports of prior repeated pivots were controller-supplied, not all reproduced in the captured conversation |
| Historical claim and time limit | Inspected National Archives primary text plus context; distinguished territorial scope from enforcement; stopped at time boundary with independent evaluation untested | Did not inspect the unspecified original webpage or test contested historiography |

The initial lanes preceded the final optional-curiosity wording refinement.
Affected completion/continuation behavior was exercised again after rereading the
new policy in the algebra lane; unchanged behavior was not falsely represented as
an entirely repeated suite. The manifest's proactive-closure prompt was corrected
after review to remove a direct request to stop. A future-retrieval assertion was
split into a separate chosen-topic case so absent tool evidence cannot pass.

## Repository checks

Observed passing locally: skill format/links (186 canonical skills), changed-skill
quality (2 skills, no errors/warnings), eval schema/semantics (186 manifests),
case-review register consistency, three catalog generators, lifecycle matrix,
ruff lint/format, mypy, skill-test registration, 27 eval-validation tests,
27 coverage tests, 25 format-validator tests, 19 quality-validator tests,
22 life-coach tests, core suite (375 tests plus 31 subtests), and 14 integration
tests. These checks do not establish learner outcomes. Full required CI and
final commit review are recorded on the pull request rather than asserted here.

The broader artifact checker was stopped after unrelated connector tests failed
to bind loopback sockets in the local sandbox with Operation not permitted.
No local pass is claimed for that checker; no sandbox restriction was bypassed.
The standalone skills-ref executable was not run; repository structural checks
validated the format instead. Generated documentation/catalogs are checked in.

## Remaining validation

Automatic client skill-selection behavior has not been measured. The separate
routing probes provide reviewable positive and negative cases. Full cross-model,
cross-domain repeated trials, a no-skill baseline, and human retention/transfer
studies remain future work under references/validation.md. No claim of rapid
expertise, universal effectiveness, or statistically calibrated mastery is made.
