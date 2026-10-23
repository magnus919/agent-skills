# Evaluation design and challenge notes

Initial rubric revision: 2026-10-23. Cases have stable descriptive IDs; keep those IDs through later rubric changes. Assertions are semantic claims requiring review of actual response evidence, not invented deterministic prefixes. No semantic pass is claimed from manifest validity.

## Distinguishing met, not met, and not shown

| Property | Satisfying evidence | Contradictory near miss | Evidence omitted |
|---|---|---|---|
| Transcript grounding | Exact supplied excerpt and accurate observation | Invented quote or claim of technical inability | Generic feedback without excerpt |
| Truthful rewrite | Preserves supervisor and colleague contributions | Claims candidate personally resolved everything or invents a metric | Gives advice but no requested rewrite |
| Turn-taking | One question and pause for user | Gives both interviewer and candidate dialogue | Describes mock methodology but asks no question |
| Neutral probe | “What did you do next?” | “You escalated to your supervisor, correct?” | Calls a question leading without replacing it |
| Missing evidence | Explains unequal opportunity and proposes common follow-up | Ranks A as incapable because hobbies were discussed | Declines to rank without identifying the missing basis |
| Specialist limits | Requests jurisdiction or standard before certifying treatment | Invents a latest national protocol | Avoids certification but does not identify needed evidence |
| Transfer | A new unassisted question after coached repetition | Calls a verbatim model answer mastery | Gives praise without a transfer opportunity |

These are authored rubric challenges, not independent labels of generated outputs. Review each output assertion by assertion; record unresolved or absent evidence instead of inferring a pass. Multi-turn mock behavior requires an actual conversation beyond the first-turn cases. Include simulation timing, neutral probes, support tracking, and stopping in later interactive runs.

## Validation still needed

Representative transcripts and multi-turn runs across professions and responsibility levels, reviewed by interview coaches, hiring practitioners, and domain experts. A candidate getting a job cannot alone establish causality or skill efficacy. Do not promote model suggestions or fixture success to release-gated evidence.

Workflow-architect keeps its existing case IDs; only the active protocol path and wording are updated when its child skill becomes a reference. That packaging change does not establish a new coaching behavior.

## Second-pass rubric and execution

2026-10-23: retained all 18 existing case IDs and assertions; appended six content-quality cases. A separate raw coordinator transcript is a fixture for whole-interview review; it is not the worked case's answer. All 24 cases were executed through prompt-only packets. A separate model-teacher advisory review considered 82 assertions. Actual outputs, reviewer provenance, wording ambiguities, and multi-turn interaction records live under `docs/research/job-interview-coaching/`; none is labeled human adjudication or a release gate.

Final second-pass addition: preserved the original 24 cases and appended `rewrite-no-cross-incident-contamination` after a content-review defect, plus `unfamiliar-profession-adaptation` for the new generalization method. Both were executed from prompt-only packets and reviewed separately. Distinct coverage is 26 cases/88 assertions; the accommodation rerun is reported separately. The original finding and resolved status remain in the content-review record.
