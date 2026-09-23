# Jev CI reference deployment runlog

Status: advisory CI deployment verified; semantic accuracy calibration remains
open. This is an evidence log, not a declaration that a Jev decision is
production-calibrated or authorized to change required CI gates.
Times below are UTC. No API keys, unredacted logs, or personal data belong
here.

## 2026-09-23 01:57 — Scope and initial audit

Objective: integrate Jev where it adds useful bounded judgments to this
repository's CI, examine existing LLM calls for possible replacement, evaluate
the per-skill evals as a showcase, test/calibrate on held-out cases, and verify
the actual GitHub Actions deployment. Preserve deterministic validation and
human authority; remain advisory until independent evidence supports a gate.

Current workflow inventory from `.github/workflows/`:

| Workflow | Current inference | Initial assessment |
|---|---|---|
| `validate.yml` | None; deterministic checks | Do not replace |
| `skillevaluator.yml` | None in selected Tier 1 checks | Do not replace |
| `skill-eval.yml` | OpenAI-compatible model generates full eval responses on main; fake adapter on PR | Jev cannot generate responses; possible bounded secondary grading of semantic assertions after deterministic checks |
| `droid-review.yml` | Factory Droid performs open-ended code/security review | Jev cannot replace review; possible routing only if it does not suppress review |
| `droid.yml` | DeepSeek-backed interactive Droid response | Jev cannot replace open-ended response |
| `ci-failure-to-issue.yml` | None; creates/updates issue after a failed main validation run | Bounded triage is plausible, but must preserve issue creation and failure status; send only approved/minimized evidence |
| `jev-qa-pilot.yml` | 22 synthetic API calls, manual only | Mechanics proven, not calibrated deployment |
| Raleigh/release workflows | No relevant LLM inference | Do not replace |

Per-skill `evals/evals.json` manifests contain free-text prompts, expected
outcomes, and observable assertions. `eval_runner/grader.py` checks a small
set of machine-readable assertion prefixes deterministically; prose
assertions become `manual_review` and currently do not fail a grade. This is
the strongest potential Jev showcase, but semantic grading must be separated
from exact checks and tested against independently reviewed labels before it
can influence any verdict. The model may not substitute for response
generation or for exact existence/exit-status assertions.

Prior pilot evidence (2026-09-22): 22 synthetic analyst-labeled cases, simple
rules baseline 17/22, Jev local runs 20/22 and 21/22, GitHub Actions manual
run [35808017339](https://github.com/magnus919/agent-skills/actions/runs/35808017339)
21/22. A borderline semantic case crossed the 0.50 boundary between runs;
neither probability nor provider confidence is calibrated. These cases are
not independent operational ground truth.

Next evidence gates: inspect real eval outputs and existing CI failure runs;
identify privacy-safe, human-labeled evaluation records; compare Jev to
deterministic and current-model baselines; measure disagreement, calibration,
latency, cost, and fallback; only then select CI integration points.

## 2026-09-23 02:00 — Actual eval and failure-run evidence

- Latest failed main validation run sampled:
  [35803752557](https://github.com/magnus919/agent-skills/actions/runs/35803752557)
  failed the deterministic `deptry` step. A model cannot replace that verdict;
  it might only route the subsequent investigation.
- Completed real-model paired-eval run
  [35804599469](https://github.com/magnus919/agent-skills/actions/runs/35804599469)
  actually executed the OpenAI-compatible model job and produced candidate,
  baseline, manifest, and comparison artifacts for `system-one`. The response
  generator is open-ended and cannot be replaced by Jev.
- Repository-wide count: 180 skill eval manifests; 5,452 prose assertions and
  278 assertions with a recognized deterministic prefix. The current
  `eval_runner/grader.py` sets `passed=true` when all assertions are
  `manual_review`. Example: `calibration-review` candidate and baseline each
  report `passed=true`, `pass_count=0`, `manual_count=5`. These are **not five
  verified passes**. A Jev semantic audit could make the gap visible without
  changing today's required gate.
- The real eval artifact's responses can exceed 14,000 characters. TypeSafe's
  current [Jev 1.13 model page](https://docs.typesafe.ai/models) lists a 64k
  request context and warns that accuracy degrades as irrelevant state grows.
  Their [jaggedness guide](https://docs.typesafe.ai/model-jaggedness/jev-1.13)
  specifically cautions about large irrelevant state, literal wording,
  adversarial content, and generation. Test full-response versus focused
  excerpts; keep exact matching and counting in code.
- [GitHub's workflow security guidance](https://docs.github.com/en/actions/reference/security/securely-using-pull_request_target)
  says a secret-bearing `workflow_run` job must not execute untrusted PR code
  or downloaded artifacts. Any Jev audit should run trusted default-branch
  code on a GitHub-hosted runner and treat model-output artifacts as data.

Decision: prioritize an advisory semantic-assertion audit for completed
default-branch eval artifacts, with bounded request size and no PR secrets.
Leave Droid's open-ended code review and the real-model response generator
intact. CI failure triage remains a secondary candidate pending labeled run
evidence and a safe, minimal extraction contract.

## 2026-09-23 02:07 — First real-artifact Jev shadow pass

Prototype: `system-one/scripts/jev_eval_audit.py` reads comparison JSON as
data, selects only `manual_review` assertions, sends each generated response
once with atomic three-way Choice questions (`met`, `not_met`, `not_shown`),
and emits no response text or key. It enforces a pinned model, validated
response shape, file/response size limits, call/asssertion budgets, and
stops on provider errors. The first live shadow run on the completed
`system-one` artifact covered 9 reports / 18 generated responses / 88 prose
assertions in 18 successful API calls. Jev suggested `met` for 35/44
candidate assertions and 16/44 baseline assertions. This is a **model
opinion**, not measured accuracy or a verified candidate improvement.

Manual spot-check found a decisive false positive: in `reranking-pipeline`,
the generated candidate response proposes **one Score question for all 30
candidates** and a fabricated 30-object response shape. The eval assertion
requires one bounded score or Noul judgment **per candidate**, which the
response does not provide. Jev labeled that assertion `met` with
`met_probability=0.99`. High Jev probability therefore cannot safely promote
this prose assertion to a pass. The appropriate use is reviewer triage and
disagreement surfacing, not gate replacement. Preserve this as a challenge
case for rubric tuning, and reserve other cases for a frozen test set.

Next: build a labeled challenge set with paraphrase/negation, omission,
contradiction, prompt injection, and API-shape mistakes; tune only on a dev
split, then report held-out selective precision/coverage and failure examples.

## 2026-09-23 — User steer: eval shape

The per-skill eval assertions may need substantial redesign for Jev. Treat
this as an eval-quality issue, not just prompt tuning: make each semantic
criterion atomic, observable in a generated response or artifact, and explicit
about omissions versus contradictions. Keep generated-response tasks and
exact checks unchanged in purpose. Do not rewrite criteria merely to improve
Jev scores; preserve the intended behavior and stable eval IDs. The current
v1 `evals/evals.json` is a versioned repository contract, so any new fields
or grader bindings require an explicit schema evolution. Initial rollout can
use the existing assertions as shadow data, then migrate representative
skills after measuring the effect. Compound assertions must not receive a
`met` simply because one clause appears in the response.

## Lessons to carry into a future write-up (working notes)

1. **The apparent eval pass rate was not the semantic pass rate.** We expected
   paired eval reports to tell us how many output-quality assertions passed.
   In the real `calibration-review` artifact, both candidate and baseline
   reported `passed=true` with zero machine-checked passes and five
   `manual_review` assertions. Lesson: report *verified*, *failed*, and
   *unreviewed* separately; a green wrapper is not evidence of a semantic
   pass. This finding is confirmed by the current grader code and artifact.
2. **Replacing a language model requires matching the output shape.** The
   repo's two model-using workflows ask for full code/security review or full
   responses to eval prompts. Jev returns typed judgments, not a review
   narrative or generated answer. Lesson: the natural integration point is
   *after* generation, as a bounded secondary judgment—not a drop-in
   replacement for the generative model. Confirmed from workflow and adapter
   code; no claim about cost savings yet.
3. **A 0.99 model probability can still endorse a wrong API design.** The
   first shadow pass marked a generated reranking design as satisfying
   “one judgment per candidate” even though the design used one Score
   question for the entire set. Lesson: high probability does not certify
   semantics, especially where a short assertion hides a subtle structural
   distinction. Confirmed by the response text and Jev shadow result; its
   frequency in broader workloads remains unknown.
4. **Good eval wording helps people and models.** The many compound prose
   assertions are difficult to score reliably. Hypothesis to test: atomic,
   observable criteria with explicit omitted/contradicted lanes improve
   Jev-human agreement without weakening the intended skill behavior. Do
   not turn this into a claimed improvement until a frozen comparison says so.
5. **Privilege boundaries shape the deployment.** A secret-bearing CI helper
   can audit trusted main-branch eval outputs, but it must not execute PR
   artifacts or let the model alter required checks. This is an architectural
   constraint from the GitHub workflow security model, not merely an
   implementation preference.

## 2026-09-23 — Rubric tuning and assertion-shape screen

Across all 5,730 assertions, a simple textual screen found 3,207 containing
`and`, `or`, or similar clause separators. This is only a **candidate list**
for editorial review, not proof that every one is genuinely compound. It
shows why a bulk, automatic rewrite would be risky. The `system-one`
reranking assertion combines per-candidate judgment and code-side sort/fusion
in one line; a false `met` can hide which part failed.

An 18-case balanced, author-constructed development set was frozen separately
from an 18-case test set. Generic Choice rubric v1 matched 17/18 dev labels;
it falsely marked the “one Score question returns 30 scores” API shape `met`
at 0.82. Clarifying that **every clause** must hold and an incompatible API
shape is `not_met`, and making the dev assertion more explicit, still matched
17/18 but shifted the error: the invalid shape was caught, while a valid
batched-per-candidate response became `not_shown` at low confidence. This is
a tradeoff, not a simple quality gain. The real artifact's invalid reranking
response still received `met` at 0.90 under rubric v2. Do not pick a
confidence threshold from these development examples: a real-shaped false
positive remained above 0.90. Test split remains unqueried at this point.

Lesson: rubric tuning alone cannot repair an assertion that collapses a
structural API requirement and a downstream sorting requirement into one
short sentence. Rework the eval criterion itself and compare again. More
importantly, keep Jev in a **shadow/reviewer-prioritization** role until
independently labeled real outputs demonstrate selective precision.

## 2026-09-23 — A sharper criterion catches the known failure

The `system-one` reranking eval was edited to separate the per-candidate
question shape from code-side ranking. Its API-shape assertion now says that
each candidate needs a distinct Score or Noul question ID; those questions
may be batched in one request, but one question may not return a score array
for all candidates. In one live replay against the **same known-invalid**
generated response, Jev changed from `met` to `not_met` (`met_probability=0.0`,
provider confidence 0.99; 297.4 ms). This is a useful diagnosis of why the
old wording failed, **not** independent validation: the criterion was tuned
after inspecting this exact error. Valid batched-per-candidate responses and
the frozen test split still need to be checked, and the edited manifest must
pass repository validation before any CI use.

Blog-ready lesson: the quality of a model-assisted grader is partly a property
of the *contract it is asked to grade*. A single short assertion left room
to confuse “one score for each candidate” with “one question that returns
many scores.” Making the interface invariant explicit exposed the known
violation without loosening the requirement. The next experiment must test
whether that precision transfers beyond the example that motivated the edit.

## Notes for the eventual lessons-learned article

Potential narrative, subject to later evidence: we began looking for LLM
inference to replace in CI, found that the existing generative tasks were the
wrong shape for Jev, and discovered a more important gap in semantic eval
evidence. A shadow grader revealed both an opportunity and a high-confidence
failure; revising the eval contract improved the known case but introduced
the possibility of overfitting. The deployment story should end with the
held-out results, the actual CI behavior, and the boundaries we kept—not
with a synthetic accuracy headline.

Evidence to retain for the article: the exact workflow/run IDs above,
versioned model and rubric, dev-versus-test provenance, counts of deterministic
versus unreviewed assertions, representative false positives and false
negatives, latency/cost observations when measured, and the final CI gate
status. Avoid publishing keys, raw private logs, or generated text without a
separate review. Label every proposed improvement as a hypothesis until a
frozen comparison supports it.

## 2026-09-23 — One frozen synthetic test pass

With the generic v2 rubric and the previously frozen test cases, a single
live Jev 1.13.0 pass completed all 18 cases. It matched 17/18 author labels
(six `met`, six `not_met`, six `not_shown`); the sole disagreement was T08, an
explicitly incompatible typed-API behavior labeled `not_met` but predicted
`not_shown`. It suggested `met` for six cases, all six labeled `met`, with
met probabilities from 0.73 to 0.99. Mean squared error for the binary
`met` probability on this balanced fixture was 0.0092. Observed request
latencies were roughly 0.21–0.34 seconds per case. The 18 examples are
author-constructed synthetic cases, not independent real-output labels;
six apparent true accepts do not establish production precision or calibrate
a threshold. The 0.99 false accept on the real reranking artifact remains a
counterexample to trusting a probability cutoff by itself.

Lesson: a clean held-out synthetic score can coexist with a consequential
real-output miss. Preserve both results in the story. The next meaningful
test is independently labeled real paired-eval responses, including API-shape
near misses, rather than more repetitions on this frozen set.

## 2026-09-23 — Advisory CI integration drafted

Added a proposed `jev-eval-audit` job to the existing paired-eval workflow.
It runs only after default-branch real-model evaluation, on a GitHub-hosted
runner with trusted checkout, and downloads that run's generated evaluation
artifact as **data**. The Jev secret is scoped to the audit step; no key is
passed to pull-request or self-hosted eval jobs. The audit is explicitly
non-blocking and cannot change exact grades, paired-eval results, required
validation, or release approval. It has fixed 20-call/100-assertion budgets
and uploads only bounded verdict/probability metadata, not generated response
text. An absent model artifact skips the audit; it is not a semantic pass.

Five local contract tests now cover prose-only extraction, omission accounting,
artifact path/size/identity checks, and separation of the generated text from
the audit report. They pass locally. The job itself has **not yet run on
GitHub** at this point, and a successful job would still prove deployment
mechanics rather than grading accuracy. A CI run, artifact inspection, and
real-output human labels remain open evidence gates.

Lesson: a useful CI integration can be deliberately weaker than a gate. The
first deployment should make the unreviewed semantic surface legible while
preserving the existing source-of-truth checks. Its own absence, errors, and
coverage limits must remain visible rather than masquerading as passes.

## 2026-09-23 — PR review found a failure-path skip

PR [#528](https://github.com/magnus919/agent-skills/pull/528) passed the
repository's validation and paired-eval tests, but Droid review found a
critical workflow-condition mistake before merge. The advisory audit job
depended on `paired-eval-model` and initially lacked an explicit `always()`
condition. GitHub would therefore skip the audit whenever the model eval
failed, despite that job's `always()` artifact upload. That is the case where
reviewer triage may be most valuable. The condition was amended to run the
audit after a failed model job on `main`, then let the download step skip it
only when no artifact exists. This does **not** make a failed paired eval
green: the audit job remains advisory and the original failure persists.

Lesson: test the failure path of an advisory helper, not only its happy path.
CI dependency defaults can silently remove an observer precisely when the
upstream check fails. A green PR check for a main-only job is no evidence of
that path; inspect the actual main workflow after merge.

## 2026-09-23 — First merged deployment and a biased coverage budget

PR #528 merged as `1935fc8` after the failure-path fix and green checks.
The resulting [main paired-eval run
35810480945](https://github.com/magnus919/agent-skills/actions/runs/35810480945)
completed its real-model generation and Jev audit successfully. The audit
used `jev-1.13.0` and reported 9 comparison reports, 104 prose assertions,
17 generated responses audited, 95 assertions selected, 9 omitted by the
100-assertion budget, and zero provider errors. Its 33 suggested `met`
verdicts (27 candidate, 6 baseline) are **not** verified passes. The uploaded
audit report contains assertion text, verdicts, probabilities, and response hashes,
not the generated response text or API key.

The coverage result uncovered a second integration defect: the first 17
candidate/baseline responses fit under the assertion cap, but the final
`reranking-pipeline` baseline did not. That makes raw candidate-versus-baseline
counts biased by traversal order. A job-level success did not reveal this;
the report's `assertions_omitted_by_budget` field did. We changed selection
to admit both sides of a paired case or neither, and to skip an incomplete
pair rather than present one side as a comparison. On the **same downloaded
artifact**, offline replay with the old 100-assertion cap selects 16 responses
/ 86 assertions and omits the full 18-assertion reranking pair. A 120-assertion
cap selects all 18 responses / 104 assertions with no budget omission. Seven
local contract tests pass. This fix has not yet had a second live GitHub run.

Lesson: coverage and sampling policy are part of model evaluation quality.
Even an advisory classifier can produce a misleading comparative headline if
the budget clips one side of a pair. Report selected, omitted, and unpaired
work explicitly; test those fields against a real artifact before interpreting
candidate/baseline tallies.

## 2026-09-23 — Paired-coverage fix verified on main

Follow-up PR [#529](https://github.com/magnus919/agent-skills/pull/529)
merged after green validation and review with no findings. Its [main run
35811979212](https://github.com/magnus919/agent-skills/actions/runs/35811979212)
completed the real-model evaluation and the advisory Jev audit. The downloaded
audit artifact reports 9 comparison reports, 18 response groups, and all 104
prose assertions selected. Budget omissions, oversized inputs, unpaired
skips, unattempted groups, and provider errors are all zero. Both candidate
and baseline for `reranking-pipeline` appear. The Jev audit job itself ran
from 03:04:31 to 03:04:49 UTC; its 18 recorded provider-call latencies ranged
from 111.8 to 942.3 ms, averaging about 202 ms. That is call latency, not
the duration of generating the paired responses. Provider billing cost was
not measured.

Deployment conclusion: the reference CI helper is now **working as an
advisory semantic-audit producer** at the default-branch boundary, with
complete paired coverage for this run and no change to deterministic grades
or release gates. It is **not** validated as an automatic semantic pass/fail
gate. The 18-case held-out synthetic fixture, one known real high-confidence
false positive, and two live CI runs are useful engineering evidence but do
not establish selective precision or calibration on independently labeled
real outputs. That work is the next evaluation gate, not a hidden completion
claim.

Article ending to preserve: the most valuable finding was not a faster model
call. It was that an apparently green eval hid unreviewed semantics, that
clearer assertions changed one known verdict, and that CI success still hid
an unfair coverage budget until the artifact was inspected. The final
deployment retained rules and human authority while making the uncertain
surface visible. Future writing should present the false positive and the
budget defect alongside the final successful run, not edit them out of the
story.

## 2026-09-23 — Turn the pilot into contributor expectations

The observed failures are now reflected in `AGENTS.md` and `CONTRIBUTING.md`
as proposed authoring guidance for future skill evals. The guidance asks for
stable cases, independently checkable semantic assertions, precise structural
boundaries, and a deliberate check against satisfying, contradictory, and
missing-evidence responses. Exact properties still belong in deterministic or
environment checks. This is a quality standard for humans **and** model
auditors; it is not a new field in the v1 eval schema or a requirement to
rewrite every existing assertion automatically.

The boundary matters: our one known real-output false positive demonstrates
that assertion wording can hide a consequential API mistake, but it does not
prove that atomic wording will make Jev reliable across the catalog. The
docs therefore keep Jev advisory, warn that `manual_review` is not a verified
pass, and reserve any scoring threshold or release gate for independently
labeled real-output evidence. Blog lesson: institutionalize the authoring
practice that the experiment actually supports without turning a promising
pilot into an unearned correctness claim.

## 2026-09-23 — Freeze a real-output review sample before scoring

The first complete live Jev audit (run 35811979212) is now the source for a
local, prediction-blinded human-review packet. The packet samples 16 assertion
pairs (32 candidate/baseline judgments) by a frozen hash seed without using
Jev's answer, then adds 12 distinct high-`met`-probability items as a separate
false-accept challenge set. It covers 44 of the run's 104 audited assertions
and 17 generated response groups. The raw responses and source mapping stay
in a private local directory; no response text is added to this repository or
to a CI artifact. The sampling seed and source artifact hashes are preserved
for replay. Local contract tests verify pairing, identity, private file modes,
and separation of the response text from the scoring map.

This is **sampling and review preparation**, not calibration results. There
are no independently assigned labels yet, so there is no measured real-output
false-accept rate, no accepted probability threshold, and no gate promotion.
The prevalence-oriented paired sample and the deliberately enriched challenge
items must be reported separately. Blog lesson: a well-instrumented audit
does not calibrate itself; freeze the evidence and blind the reviewer before
examining its predictions.

## 2026-09-23 — CI inference inventory and visible coverage

The current workflow inventory has two generative-model jobs: the paired
evaluation's OpenAI-compatible adapter generates full candidate and baseline
answers on a self-hosted runner, and Droid produces code/security review with
DeepSeek V4 Flash. Jev's typed Choice/Score/Noul answers cannot replace either
output contract. The NVIDIA SkillEvaluator job explicitly runs keyless,
LLM-free checks; the repository's validators and fake-adapter smoke are also
deterministic. No other CI LLM classification step was found to replace.

The viable replacement opportunity is at the *grader* boundary: prose
assertions previously stopped at `manual_review`; Jev can make an advisory
typed judgment after generation. Its audit already ran on trusted `main`, but
the CI check surface showed only a green/failed step while coverage and
omissions lived in a downloaded JSON artifact. A coverage-only job summary
now states how many prose assertions were judged, skipped, omitted by budget,
or left after an error. Missing model artifacts or an audit that fails before
writing a report are explicitly called missing evidence. No summary calls a
model verdict accurate or changes release authority. The calibration helper's
contract tests now run alongside the audit tests in the paired-eval job.

Lesson for the article: a fast classifier helps only where the required output
is a bounded judgment. Treating a model's successful API call as CI coverage
is another way to hide missing evidence; expose denominators and failure lanes
before celebrating latency or accuracy. Independent labels remain outstanding.

## 2026-09-23 — Main-branch deployment proof after PR #533

[Run 35815520138](https://github.com/magnus919/agent-skills/actions/runs/35815520138)
completed successfully on merged `main` at `6ebe743`. The paired-eval test job
ran both the audit and calibration-helper tests. Real-model paired generation
took 13m25s; the downstream Jev audit job took 11s. The uploaded live audit
artifact identifies `jev-1.13.0` and records 9 comparison reports, 18 response
groups, and 108/108 prose assertions selected, with zero skipped responses,
oversized assertions/groups, unpaired assertions, budget omissions, or provider
errors. The rendered GitHub run summary was inspected: it displays complete
advisory coverage and all omission/error lanes, explicitly distinguishing
coverage from agreement, calibration, and merge permission.

A new private, prediction-blinded packet was frozen from this exact run using
seed `jev-ci-review-v2`: 16 assertion pairs plus 12 separate high-`met`
challenge judgments, totaling 44 review items across 17 response groups.
It and the raw response text remain local rather than in the repository or CI
artifact. Human labels are still missing; do not infer any Jev accuracy or
threshold from the 108/108 coverage count. The time comparison also measures
different jobs and output contracts—Jev did not replace the generative stage.

## 2026-09-23 — Keep reviewer disagreement upstream of Jev scoring

The latest 44-item private review packet still has zero independently assigned
labels. A single filled template could be scored, but that would conflate one
reviewer's judgment with adjudicated truth. The calibration helper now supports
two separately frozen, prediction-blind label files and reports their exact
agreements, disagreements, and unresolved `uncertain` items without reading
Jev's private prediction map. Reviewers can resolve rubric ambiguity before
seeing model answers; the original reviews remain intact. This is preparation
for independent evidence, not evidence that Jev agrees with humans. Blog
lesson: measure and preserve disagreement in the supposed ground truth before
optimizing a model against it.

## 2026-09-23 — Offline replay comparison finds one boundary flip

The private 44-item human review packet remained unlabeled. A proposed local
live replay of run 35817642002 stopped on DNS resolution before any Jev answer
was received. A request for network permission was rejected because that
would resend CI-generated response text to the external TypeSafe API without
specific authorization for this payload. No indirect retry was attempted.

A safer comparison used two *existing* complete CI audits: runs
[35815520138](https://github.com/magnus919/agent-skills/actions/runs/35815520138)
and [35817642002](https://github.com/magnus919/agent-skills/actions/runs/35817642002).
All 18 response groups had identical response hashes and assertion text/order;
both requested `jev-1.13.0`. The auditor source file was byte-identical at
their respective full source commits. Across 108 matched judgments, one
verdict flipped: the `jev-integration` candidate assertion about keeping
`TYPESAFE_API_KEY` server-side changed from `not_shown` (met probability 0.46)
to `met` (0.51). Provider confidence was 0.27 in both. Mean absolute change
in `met` probability was 0.0147; maximum was 0.14. The offline stability
helper now checks identical inputs and source implementation before computing
these statistics, without sending another request or exposing raw responses.

This is repeatability evidence, **not** an accuracy or calibration estimate.
The single flip near 0.5 reinforces the need for a review/abstention lane;
it does not determine a usable threshold. Blog lesson: opportunistic repeated
CI runs can reveal boundary instability without paying for or authorizing a
new provider call, but agreement with oneself is not agreement with reality.

## 2026-09-23 — Three identical-input audits after PR #536

[Run 35819232877](https://github.com/magnus919/agent-skills/actions/runs/35819232877)
on merged `main` at `10eaafa` passed the calibration-helper tests, real-model
paired eval, and Jev audit. Its uploaded `jev-1.13.0` audit again selected
108/108 prose assertions across the same 18 byte-identical response groups,
with zero skips, budget omissions, or provider errors. The auditor source was
unchanged across this and the two preceding complete runs.

Across all three existing audits, 106/108 matched assertions kept one verdict;
two changed at least once. The server-side-secret assertion changed
`not_shown → met → not_shown` with first-run provider confidence 0.27. A
`deadline-bound-stream` baseline assertion changed `not_shown → not_shown → met`
with first-run confidence 0.30. Grouping by **first-run** provider confidence,
the unstable counts were 1/4 below 0.30, 1/16 from 0.30 to below 0.50, 0/15
from 0.50 to below 0.70, and 0/73 at or above 0.70. This is a tiny,
post-hoc repeatability screen on one System One skill, **not** a calibrated
confidence policy, a false-accept estimate, or a claim about the wider catalog.
Human labels and broader real-output slices remain necessary.

Blog lesson: repeated identical inputs surfaced two decision-boundary flips
that a single green CI audit could not reveal. Showing a stability/coverage
slice is useful for deciding what humans should inspect next; setting an
automation threshold from it would overfit the same few observations.

## 2026-09-23 — Make paired-eval selection coverage explicit

Inspection of both paired-eval jobs found a silent `head -5` cap on changed
skills with eval manifests. A six-skill change could run only five paired evals
while the downstream Jev audit still reported complete coverage of the
*generated* reports. That percentage did not represent coverage of all
eligible changed skills. This was a selection-denominator defect, not evidence
of Jev misclassification.

The selector now records eligible and selected counts, selects all skills up
to the five-skill resource cap, and fails without starting a truncated subset
when the cap is exceeded. Both the fake-adapter PR path and the real-model
default-branch path use it. Unit tests cover duplicate paths, unrelated
changes, empty selection, and the six-skill failure case. Contributor guidance
now distinguishes selection completeness from assertion-level audit coverage.
No new TypeSafe calls or human-label claims were made in this change.

Blog lesson: a model audit can be internally 100% complete while the upstream
work selector silently omitted cases. Track the denominator at each pipeline
boundary, and fail visibly when a resource cap would hide work.

## 2026-09-23 — Include reference and template changes in the denominator

After PR #538, the paired-eval workflow still triggered only for `SKILL.md`,
eval manifest, and script paths. Its selector used the same narrow set. Editing
a skill's `references/`, `templates/`, assets, or human README could change
what the agent sees or how contributors use the skill while causing **no paired
eval job at all**. The five-skill completeness check therefore applied only to
a subset of skill edits.

The workflow now triggers on any file under a top-level directory, and the
selector accepts the change only when that directory is a skill with both
`SKILL.md` and `evals/evals.json`. A local temporary-Git-repository test verifies
that a reference-only commit is discovered; the existing duplicate, missing,
and over-cap tests still pass. Non-skill top-level changes may start the light
workflow, but are reported as no eligible skill rather than audited work.

Blog lesson: a complete *selection result* is only complete relative to its
event trigger and changed-file query. Check both before interpreting audit
coverage as a property of the contributor's whole change.

## 2026-09-23 — Reference-only edit reaches real Jev audit

[PR #539](https://github.com/magnus919/agent-skills/pull/539) changed the
System One QA reference without changing its `SKILL.md`, eval manifest, or
scripts. Its PR paired-eval smoke job passed, and the selector reported one
eligible and selected skill: `system-one`. After merge at `2f34bcf`,
[main run 35822037156](https://github.com/magnus919/agent-skills/actions/runs/35822037156)
completed paired-eval tests, fake-adapter smoke, real-model paired evaluation,
and the advisory Jev audit successfully. Both the model and audit artifacts
were uploaded.

The audit artifact requested `jev-1.13.0` and marked itself advisory. It saw
9 comparison reports and 108 prose assertions, selected all 18 response
groups and all 108 assertions, and recorded zero skipped responses, oversized
items, unpaired assertions, budget omissions, or provider errors. This proves
that a reference-only change can reach the end-to-end CI path and that this
run's generated prose assertions were fully attempted. It does **not** prove
Jev accuracy, calibration, or semantic correctness; independent labels for
real outputs are still missing.

Blog lesson: verify coverage fixes with a change that previously would have
been invisible to the trigger, then follow that change through generation,
audit, and artifact metadata. A green job alone is a weaker observation.

## 2026-09-23 — Carry expected cases across the model/audit boundary

The reference-only run above established 108/108 *observed-assertion* coverage,
but exposed a remaining denominator gap: Jev read whatever comparison reports
the model job uploaded. If generation stopped before writing an expected case
report, Jev could call the observed set "complete" while omitting that case.

The selector now writes a small JSON artifact containing the selected skill
manifests and their case IDs **before** generation. The model job uploads it
with the reports, even when a later paired-eval step fails. The auditor checks
expected against observed `(skill, case ID)` pairs, rejects malformed or
duplicate identities, and reports missing and unexpected cases separately
from skipped assertions and provider errors. Without selection evidence, it
labels selected-case coverage unknown rather than complete. This remains
advisory; it does not alter exact grades or authorize a release.

An offline replay of the existing [main run 35822037156](https://github.com/magnus919/agent-skills/actions/runs/35822037156)
artifact found 9 expected and 9 observed case reports, with no missing or
unexpected IDs, and 108 observed prose assertions. Synthetic missing-case,
whole-skill omission, unexpected-report, and unsafe-selection tests exercise
the failure lanes without another TypeSafe request. This is pipeline coverage
evidence, **not** human-labeled Jev accuracy or calibration.

Blog lesson: freeze the worklist before an expensive stage. Comparing only
what arrives afterward can hide precisely the cases that failed to arrive.
