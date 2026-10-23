# Initial validation observations

Date: 2026-10-23. These observations describe a prototype, not validated coaching efficacy. The two forward trials were model-generated applications by separate agents, without the eval manifest or intended answer supplied. They are smoke-test evidence, not human adjudication, calibration labels, or release-gated semantic evidence. No real candidate data was used.

## Candidate trial

Prompt: a first customer-service candidate supplied an untimestamped volunteer-service excerpt: “We always tried to keep people happy” and “I think we were successful,” followed by the interviewer moving to the next question. The user requested frank feedback, impressive wording including numbers if helpful, and one-question-at-a-time practice.

Actual output excerpts:

> I've added turn IDs because your transcript has no timestamps.
>
> T02: “We always tried to keep people happy.” This shows a service-minded intention, but doesn't describe a dissatisfied person or what you personally did.
>
> T02: “I think we were successful.” The outcome is vague. Explain what you actually observed afterward. Numbers help only if you know they're accurate; a concrete qualitative result is useful too.
>
> Customer-service judgment is not demonstrated in this answer; that isn't evidence that you lack it. Your tone and delivery aren't assessable from this text.
>
> Tell me about one occasion while volunteering when someone was unhappy with the help or service they received.

The trial ended at that question. It did not establish how the agent handles the next answer, repeated practice, or transfer. The output also identified that the interviewer had not probed the vague example. No fabricated achievement or numeric result appeared.

References used: candidate coaching, transcript analysis, practice and feedback, operational professions, responsibility levels, and interview formats.

## Interviewer trial

Prompt: a manager requested a ranking after giving A five minutes about hobbies and B twenty minutes about maintenance work. The target was an apprentice trained after hiring; the manager wanted a 35-minute follow-up scorecard and improvement to “You would always call your supervisor before doing anything, right?”

Actual output excerpts:

> You have more job-relevant evidence about B, but these interviews do not support a fair ranking.
>
> Give both candidates the same structured follow-up before comparing them. Keep any previous observations in a separate evidence record, noting the unequal questions and time. Don't turn A's missing evidence into a low score.
>
> You are learning a maintenance task with a supervisor. Something differs from the instructions you were given. What would you do next, and why?

The output supplied a 35-minute agenda: 4 minutes opening, three 7-minute capability discussions, 7 minutes for candidate questions, and 3 minutes closing. It proposed learning, checking/handoff, and supervision-boundary criteria with distinct observable anchors. It separated “Not demonstrated” from limited evidence, requested supervisor confirmation of entry expectations, and stated that the interview could not establish hands-on competence.

References used: interviewer coaching, assessment and calibration, interview formats, responsibility levels, and operational professions.

## Limits and next work

Neither trial exposed a material application difficulty. That does not establish a general semantic pass. The 18-case manifest remains a scenario contract, not 18 completed runs. Full multi-turn simulation, specialist correctness, multilingual and cross-cultural adaptations, real transcript diversity, and review by experienced coaches and domain practitioners remain untested.

The rubric challenge notes preserve satisfying examples, contradictory near misses, and omitted-evidence cases. No model confidence threshold or automated hiring gate is introduced.

## Local repository verification

Implementation commit: `01d8baf060629261a7849472c4d88139727bbcf6`. Checks ran against its staged implementation bytes; this record is a subsequent documentation-only update.

- Skill format: 189 canonical skills validated.
- Changed-skill quality: four changed skills, zero errors or warnings.
- Eval manifest validation: 189 accepted; 27 validator tests passed.
- Eval coverage ratchet: 189/189 schema-valid, 100%; no decrease.
- Bundle manifests: eight validated. Bundle validation tests: 14 passed, 307 assertions.
- Claude marketplace, Codex packaging, llms.txt, and lifecycle matrix: current.
- AGENTS consistency and skill script-test conventions: passed.
- Curated case-review register accepted; it reports evidence gaps separately, not behavioral completeness.
- Diff whitespace check: passed.

The broader `scripts/check-artifacts.py` command also launches unrelated test suites. Several local HTTP-stub tests failed because this sandbox forbids socket binding; the broad run was interrupted. No whole-repository test-suite pass is claimed. No executable implementation code changed in this project.

Publication is pending. Automatic approval review rejected the initial push because it required separate authorization for external disclosure to GitHub. No push or PR was completed, and no remote CI result is available. The local branch is `codex/job-interview-coaching`.
