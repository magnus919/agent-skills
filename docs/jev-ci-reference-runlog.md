# Jev CI reference deployment runlog

Status: advisory CI deployment is active; semantic accuracy calibration and
transient provider availability remain open. This is an evidence log, not a
declaration that a Jev decision is production-calibrated or authorized to
change required CI gates.
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

## 2026-09-23 — A new eval case outgrew the Jev assertion budget

The laya.cpp enrichment in [PR #541](https://github.com/magnus919/agent-skills/pull/541)
raised System One from nine to ten eval cases. The manifest now contains 122
prose assertions across candidate and baseline responses, requiring 20 Jev
calls at the current one-group-per-call design. [Main run 35823747886](https://github.com/magnus919/agent-skills/actions/runs/35823747886)
uploaded 10 comparison reports, but its `jev-1.13.0` audit selected only 18
groups and 104/122 assertions: an entire 18-assertion case was omitted by the
120-assertion cap. There were zero provider errors. This is a real budget
omission, not an inference about the missing case's quality.

The CI assertion allowance is increased to 160 while retaining the 20-call
limit. A test checks that the current System One manifest fits both bounds;
the audit still reports omissions rather than silently treating over-budget
work as complete. The change is bounded headroom for the present suite, not a
general promise that every combination of up to five changed skills can fit.
An offline replay of the same 10-report model artifact with the new allowance
selected all 20 groups and 122/122 assertions, with no budget omissions and
10 expected/10 observed case reports. This verifies selection arithmetic,
not live Jev judgments under the increased allowance.

Blog lesson: adding one eval case can push a paired, all-or-nothing selection
past a budget boundary. Watch the omitted-*counts* in actual artifacts and
version the allowance against the evolving manifest; a green advisory job is
not a coverage guarantee.

## 2026-09-23 — Live coverage after the budget repair

[Main run 35824738032](https://github.com/magnus919/agent-skills/actions/runs/35824738032)
confirmed the frozen selection list matched all ten uploaded comparison
reports, with no missing or unexpected IDs. It still used the old
120-assertion allowance: 18 groups and 104/122 prose assertions were selected,
18 were omitted by budget, and there were zero provider errors.

[Main run 35825585445](https://github.com/magnus919/agent-skills/actions/runs/35825585445)
then exercised the merged 160-assertion allowance with live Jev calls. Its
artifact has ten expected and ten observed case reports, 20 selected groups,
122/122 selected prose assertions, zero skips, zero budget omissions, and zero
provider errors. The tests, real-model generation, smoke job, and advisory Jev
audit all completed successfully. This establishes selected-case and
assertion coverage **for this run**, not judgment accuracy, calibrated
confidence, or authority to block a release. Independent labels are still
missing for the 44-item blind review packet.

Blog lesson: verify the artifact after the repair, not just the repaired
selection arithmetic. Preserve the failed-budget run beside the successful
one so the change and its limits remain visible.

## 2026-09-23 — Droid is not a Jev replacement, and green is not enough

The separate [Droid/Nous experiment in PR #544](https://github.com/magnus919/agent-skills/pull/544)
tested a generative code-review workload. Nous Portal accepted GPT-6 Luna at
`low` reasoning via Responses, including ordinary function tools and streaming,
but returned HTTP 400 for a Responses `custom` tool. Droid's normal review
request includes custom tools, so the full review failed. A read-only
compatibility run avoided that request error and its GitHub job turned green,
but Droid did not write its review-candidates file; no validated review was
produced. PR #544 remains a draft experiment, not a replacement deployment.

Jev can judge bounded assertions *after* a model has generated an answer; it
cannot replace the generative review or the tool-using agent here. Blog lesson:
a green AI job may mean only that the process exited cleanly. Check the
workflow's actual output artifact and downstream validator before claiming
that useful work happened.

## 2026-09-23 — Calibrating the selected worklist, not just what arrived

The first private calibration helper checked that every prose assertion in
the *observed* audit was judged, but did not require the audit's frozen
selected-case list to match the observed reports. That left a whole missing
case outside its definition of a complete run. Packet preparation now rejects
missing or unknown selection evidence, missing/unexpected reports, and
inconsistent report counts or case identities. Repeatability comparisons of
older audit artifacts remain readable; this stricter rule applies to preparing
a new calibration packet.

The complete [main run 35825585445](https://github.com/magnus919/agent-skills/actions/runs/35825585445)
passed the strengthened preparation path. A fresh private packet contains 44
blinded judgments from 18 response groups: 32 population-sampled paired
assertions and 12 risk-enriched suggested-`met` challenges. The packet is
local-only; no labels have been assigned, so there is still no real-output
accuracy or confidence calibration result.

Blog lesson: an audit can be internally complete for the subset it saw while
the upstream worklist is incomplete. Freeze and check the intended case list
before asking humans to calibrate the model against the resulting sample.
## 2026-09-23 — Spread capped audit calls across changed skills

The paired-eval auditor previously consumed reports in path order. With the
20-call CI cap, the first alphabetic skill could use all available calls while
other changed skills received no Jev audit. This was a coverage-allocation
problem, not a claim that the model mislabeled any assertion. The selected
count and budget-omission count remained honest, but the allocation was biased.

The auditor now visits complete candidate/baseline case pairs round-robin
across skills, in stable hash order within each skill. A focused four-report
fixture verifies that a four-call budget selects one complete pair from each
of two skills, reports the other four assertions as budget omissions, and is
deterministic across runs. This is breadth-first *allocation*, not random
sampling or an accuracy estimate. A capped multi-skill audit remains partial;
independently labeled calibration is still pending.

Blog lesson: a truthful omission counter is necessary but insufficient for a
useful bounded audit. Inspect which populations receive the scarce calls.

## 2026-09-23 — Verify the calibration-scope repair on main

The main-branch paired-eval run
[35830055808](https://github.com/magnus919/agent-skills/actions/runs/35830055808)
at merge commit `58886c9f015b092aaa580c058fecf0383d850876` completed its real-model
generation and live Jev audit successfully. The downloaded `jev-eval-audit`
artifact reports `selection_scope.status=selected`, ten expected and ten
observed comparison reports, no missing or unexpected reports, 20 selected
candidate/baseline groups, and 122/122 prose assertions attempted. It reports
zero skipped responses, oversized groups/assertions, unpaired assertions,
budget omissions, post-error omissions, or provider errors. This confirms
complete *selected-case coverage* on that run. Its 33 `met`, six `not_met`,
and 83 `not_shown` suggestions are observations, not independently verified
accuracy or calibration.

The subsequent balanced-selector run
[35830774978](https://github.com/magnus919/agent-skills/actions/runs/35830774978)
at merge commit `e8a6f99b0e09ddfb8504a75c29a357d2bcd9a084` also completed
real-model generation and the live Jev audit successfully. Its downloaded
artifact identifies budget policy `skill_round_robin_stable_hash_v1`, matches
all ten expected comparison reports, and records 20/20 groups and 122/122
prose assertions attempted, with zero skips, budget omissions, or provider
errors. It yielded 33 `met`, seven `not_met`, and 82 `not_shown` suggestions;
these are not accuracy estimates. This live run selects only `system-one`, so
the policy's *cross-skill* allocation remains evidenced by the four-report
deterministic test, not by a live multi-skill run.

We also checked `ci-failure-to-issue.yml` as a possible second Jev workload.
It contains no LLM inference to replace: a deterministic failure event creates
or updates a tracking issue. GitHub's main-branch `Validate skills` history
returned only two failed runs (2026-07-29, IDs `30494023779` and
`30493470742`). That is insufficient historical failure evidence to tune or
calibrate a probabilistic triage classifier. No Jev step was added there;
mandatory issue creation and failure signals remain deterministic.

Blog lesson: successful live coverage and a sensible allocation policy are
different claims. Test the latter with multi-skill fixtures, and do not infer
semantic correctness from a green provider call or a small incident history.

## 2026-09-23 — Same-input Jev repeatability from two completed CI runs

We compared the live audit artifacts from main runs
[35825585445](https://github.com/magnus919/agent-skills/actions/runs/35825585445)
and [35830055808](https://github.com/magnus919/agent-skills/actions/runs/35830055808)
with `scripts/jev_eval_calibration.py stability`. The tool verified that the
two commits used byte-identical `jev_eval_audit.py` implementations (SHA-256
`a85a531d11a1d7fbf1e2e775b5d9e3c713bf4fd6809e77614a958eafefd6d2a0`),
then matched all 20 audited response groups by skill, case, side, and response
SHA-256. All 122 assertion texts and their order also matched. This is a
same-input Jev repeatability comparison, not merely a comparison of two
different model generations.

Jev's suggested verdict changed on one of 122 assertions: `contract-design`
candidate, “Keeps thresholds, human review, authorization, and side effects
in deterministic code,” moved from `not_met` to `met`. Its `met` probability
moved from 0.44 to 0.47 while provider confidence moved from 0.23 to 0.20.
Across all matched assertions, mean absolute `met` probability change was
0.0134, maximum 0.09; mean absolute provider-confidence change was 0.0222,
maximum 0.15. The flip was near the decision boundary and had low reported
confidence in both runs. It strengthens the case for an abstention/review lane,
but does **not** establish any threshold, correctness, probability calibration,
or suitability as a release gate.

A proposed third local call was blocked before egress because this environment
required explicit approval to retransmit the saved responses. We did not work
around that restriction. The two already-completed CI artifacts supplied the
same-input comparison without additional provider traffic.

Blog lesson: compare hashes and audit implementation before calling two runs
“repeatability.” A green rerun can still hide a low-confidence verdict flip;
keep that uncertainty visible rather than rounding agreement up to certainty.

## 2026-09-23 — Prediction-blinded provisional assertion screen

The 44-item human-review packet still had zero submitted labels, so we created
a separate 12-item *agent* pilot from the same complete run using four hashed
candidate/baseline assertion pairs (eight population items) and four remaining
high-`met` challenge items. The reviewer saw response text and assertion IDs,
not Jev predictions, and froze evidence notes before opening the private map.
This is a diagnostic screen, **not** independent human adjudication. No new
model/provider traffic occurred.

Of the 12 pilot items, 11 received a provisional `met` or `not_shown` label;
those 11 matched Jev's suggested verdicts. One item was left `uncertain`:
the `jev-integration` assertion “Uses bounded retries/timeouts and does not
turn a timeout into a confident default.” The generated code limits retry
attempts and per-request timeouts and routes failures to review, but it sleeps
for an uncapped server-provided `Retry-After` and has no total wall-clock
deadline. Jev suggested `met` with `met_probability=1.0` and reported
confidence `0.99`. This is a **rubric-boundary question**, not a proven Jev
error: the assertion does not say whether “bounded” includes the total
backoff/deadline. Ask an independent reviewer to adjudicate it before changing
the eval wording or scoring Jev. A high confidence field cannot resolve an
underspecified assertion.

The private pilot labels and score remain outside the public repository; the
original 44-item prediction-blinded packet is unchanged and still needs
independent reviewers. The pilot's high-`met` challenge selection and tiny
size make its agreement count unsuitable for an accuracy or calibration claim.

Blog lesson: write assertions so a satisfying response, contradiction, and
missing-evidence response are distinguishable. When a real output exposes an
ambiguous quantifier such as “bounded,” freeze the example and adjudicate the
criterion before tuning the model or turning its confidence into policy.

## 2026-09-23 — Make independent review easier without exposing predictions

The full 44-item packet still had no independent labels. Hand-editing a long
Markdown packet plus JSON template is a practical obstacle to calibration, so
`jev_eval_calibration.py prepare` now also emits a private `review.html` form.
It groups assertions with their generated response, offers `met`, `not_met`,
`not_shown`, and `uncertain`, requires a brief evidence note for final export,
and downloads schema-v1 labels JSON. Draft save/load supports a reviewer
working across sessions without browser storage. The reviewer must attest to
prediction blinding before final export. The HTML is self-contained; no
network requests or external assets are needed, and untrusted response and
assertion text is HTML-escaped under a restrictive Content Security Policy.

We regenerated the original 44-item selection with its frozen seed. Its
Markdown packet, private map, and JSON label template were byte-identical to
the earlier packet; only the new HTML file was added, with private file mode.
Unit tests cover blinding, private permissions, malicious HTML escaping, and
the inline-script CSP hash. JavaScript syntax passed `node --check`. The
computer-use browser refused a local `file://` URL under its security policy;
we did not try another browser surface, so actual click/export behavior is
**not browser-verified** here. The Markdown-plus-JSON path remains available.
No new model or provider call occurred.

The first PR validation also rejected backticked names of generated private
files as stale repository references. We changed the prose to identify those
artifacts descriptively and reran the skill validator. Contributor docs need
to distinguish files produced locally from paths tracked in the public skill.

Blog lesson: a calibration protocol can be technically sound yet remain
unfinished because collecting blinded labels is too awkward. Improve the
reviewer's workflow, preserve the same frozen sample and private mapping, and
keep unverified UI behavior clearly labeled.

## 2026-09-23 — Post-merge Jev audit on the review-form revision

PR [#551](https://github.com/magnus919/agent-skills/pull/551) merged as
`23bb379772ba1aa3c265647513fcdb83f11a3c9f`. The ensuing [main-branch
run](https://github.com/magnus919/agent-skills/actions/runs/35835888717)
completed successfully: paired-eval tests, fake-adapter smoke, real-model
generation, and the advisory Jev audit all passed. The independent
[validation run](https://github.com/magnus919/agent-skills/actions/runs/35835888434)
also passed. This verifies deployment of the review-form revision through the
normal main-branch workflow, not just PR checks.

We downloaded and inspected the audit JSON rather than inferring coverage from
the green job. It requested `jev-1.13.0` in live mode and found all 10 expected
reports. Across 20 selected response groups it scored all 122 prose
assertions: 35 suggested `met`, 6 `not_met`, and 81 `not_shown`. There were zero
budget omissions, skipped responses, unattempted assertions, or provider
errors. Mean reported provider confidence was 0.757 (range 0.13–1.00), but
that field is **not** an empirically calibrated probability of correctness.
The artifact records 20 response hashes, so results can be matched to their
source outputs without publishing those outputs in this runlog.

This is operational evidence for selection and serving reliability, not an
accuracy or release-gate result. The 44-item blinded packet still needs
independent human labels. In particular, the provisional high-confidence
“bounded retries/timeouts” boundary case above remains unresolved; neither a
passing audit nor the aggregate confidence figure adjudicates it.

Blog lesson: verify the live post-merge path and inspect the audit artifact's
denominators. Report coverage, omissions, and provider failures separately
from agreement and calibration; a clean 122/122 service run answers only the
first set of questions.

## 2026-09-23 — Replace manual review toil with a model-teacher screen

The owner authorized an inference model to supply labels rather than requiring
manual review of the 44-item packet. This does **not** create ground truth:
the separate teacher can share blind spots with Jev, and two calls to the same
teacher are correlated. The new manual, main-branch-only workflow prepares the
same prediction-blind sample, asks Nous Portal GPT-6 Luna for two passes with
reversed assertion order, and leaves disagreements `uncertain`. It uploads
only hashed item IDs, labels, and aggregate Jev-versus-teacher counts, not the
generated responses, Jev private map, or teacher rationales. It cannot change
required validation or release status.

We reproduced the frozen `jev-543-blind-v1` selection from main run
[35825585445](https://github.com/magnus919/agent-skills/actions/runs/35825585445):
44 item IDs, 32 population judgments in 16 candidate/baseline pairs, 12
risk-enriched challenge judgments, and 18 response groups. The selected ID
sequence matched the earlier packet byte-for-byte by SHA-256. The new
machine-readable `review-items.json` contains only `id`, `assertion`, and
`response`; tests reject prediction-bearing fields and verify private file
permissions. This section records preflight design and offline tests only;
live teacher reliability and agreement are not yet established.

Jev is a managed API with no public weight-training path. TypeSafe's current
[customer agreement](https://typesafe.ai/legal/mca) restricts using its
Services or Output for distillation or imitation-model training. Therefore
the teacher receives no Jev predictions and the work is an evaluation of the
existing CI policy, **not** training a competing classifier from Jev output.
If a separately trained Laya classifier is desired, its dataset and license
boundary need an explicit design outside this Jev audit.

Blog lesson: replacing reviewer toil with model pseudo-labels can accelerate
error discovery, but it changes the kind of evidence. Keep provenance,
blinding, disagreement, abstention, and provider terms visible; never rename
teacher consensus to independent accuracy.

## 2026-09-23 — First teacher run exposed a wire mismatch

The first [manual teacher run](https://github.com/magnus919/agent-skills/actions/runs/35909689507)
successfully verified the trusted main source run, downloaded both artifacts,
and reproduced the frozen blind packet. The first provider call then failed
HTTP 404 on `POST /v1/responses`; no labels or score were produced. The
`NOUS_API_KEY` secret was present, so this was not a missing-credential result.
The provider's published integration describes OpenAI-compatible chat
completions. We changed the teacher client to `POST /v1/chat/completions` with
chat-shaped request and response validation, preserving the same sample,
blinding, and fail-closed output policy. A second live run must verify this
correction before claiming that the teacher screen works.

Blog lesson: “OpenAI-compatible” does not imply every OpenAI API surface is
implemented. Probe the exact wire used by the workload and record failures as
missing evidence, not as a classifier verdict.

The [second live run](https://github.com/magnus919/agent-skills/actions/runs/35910464057)
used the provider's documented chat-completions path but again returned HTTP
404 on its first call, before any label was generated. This means the wire
format alone did not explain the failure; the requested `openai/gpt-6-luna`
model identifier or account availability is now suspect. The next revision
checks the authenticated `/v1/models` catalog *before* sending response text
and allows an exact catalog model ID as a manual workflow input. Do not infer
model availability from a local CLI's model list or from an unrelated provider.

The catalog check in the [third run](https://github.com/magnus919/agent-skills/actions/runs/35911223591)
found `openai/gpt-6-luna` listed, but the first chat request
still returned HTTP 404. A [fourth run](https://github.com/magnus919/agent-skills/actions/runs/35911350771)
found `anthropic/claude-sonnet-4.6` in the same catalog and got the same
404. Neither run produced labels or a score. Catalog listing is therefore not
proof that inference works. The next workflow revision sends a synthetic
one-line probe *before* downloading private artifacts and reports only its
status and sanitized machine-readable error type/code.

The objective here is **application-level tuning of Jev API inputs**: the
question, evidence, criteria, and abstention policy. No model weights are
being fine-tuned. Separate inference-model judgments, if obtained, are
pseudo-labels for finding questionable Jev request shapes, not ground truth
or a new release gate. If the provider route remains unavailable, pause this
screen rather than modifying Jev prompts based on absent labels.

The [synthetic preflight run](https://github.com/magnus919/agent-skills/actions/runs/35912008261)
confirmed that the catalog lists `openai/gpt-6-luna`, but
`POST /v1/chat/completions` with only `Reply OK.` returned HTTP 404. The
provider body had no sanitized `error.type` or `error.code` to report. The
workflow stopped before downloading the evaluation artifacts. This isolates
the current blocker from the frozen sample and its request size: the same
route fails on a minimal synthetic request. No teacher labels, agreement
estimate, Jev false-accept estimate, or calibrated Jev input revision exists
yet. A working inference route/account entitlement is needed before resuming
this calibration; do not infer that changing Jev prompt wording would fix it.

Correction after an unauthenticated comparison: `GET /v1/models` itself
returned HTTP 200 with no Authorization header. The catalog step never
verified the stored key; earlier descriptions implying it did were wrong.
We removed the secret from that public listing request, retained the listing
only as a model-ID precheck, and made the synthetic inference request the
actual credential/route check. The distinction matters: **catalogued** is
not **callable**, and a public catalog cannot establish key validity.

A [third catalogued model](https://github.com/magnus919/agent-skills/actions/runs/35912615122),
`deepseek/deepseek-v4-flash-0731`, also failed the keyed synthetic request
with HTTP 404 before any eval artifact download. Three model families now
share that failure; this increases suspicion of credential, account, or
gateway behavior, but does not identify which one. No blind labels exist.

## 2026-09-23 — A no-new-egress diagnostic while Nous is unavailable

The repository already runs its paired-eval answer generator on a
self-hosted runner with a local OpenAI-compatible service at
`http://host.docker.internal:8080`. We added a separate manual, main-only
local-model teacher workflow as a *feasibility diagnostic*, not a substitute
for independently labeled calibration. It reuses the prediction-blind packet
and two-pass/abstention contract, restricts the endpoint to that existing
runner service, probes with synthetic text before downloading private
artifacts, and uploads only aggregate/hashed-ID outputs. Its first run will
use four candidate/baseline pairs plus four challenge assertions so a JSON
contract or runtime failure does not turn into a long, costly replay.

The local model may be the very model that generated the evaluated answers;
the original source-run manifest uses a generic model label, so exact
identity is not provable from the public artifact. Agreement would therefore
be correlated self-review and cannot establish Jev accuracy, probability
calibration, or a release gate. It can still expose disagreement examples
worth inspecting while the independent Nous route is unavailable. This is
preflight design and tests only; no live local-teacher result is claimed yet.

The [first local workflow run](https://github.com/magnus919/agent-skills/actions/runs/35914644889)
stopped at source validation because the self-hosted runner has no `gh` CLI.
It never probed the local model or downloaded response artifacts, so it says
nothing about label quality. We replaced the `gh` request and `jq` processing
with Python 3.12 standard-library code, already provisioned in the job.
This is a runner-portability lesson: test the actual target runner rather
than assuming GitHub-hosted convenience tools are installed there.

The [second local run](https://github.com/magnus919/agent-skills/actions/runs/35915518491)
passed source validation and a simple `Reply OK.` HTTP probe, downloaded the
frozen artifacts, and prepared the 12-item blind packet. Its first label
request returned content that could not be decoded as JSON; the labeling
script failed closed with `JSONDecodeError`, so no consensus or score exists.
The simple probe tested only route availability, not the needed output
contract. We now request JSON-object output from the local server and make
the preflight use the exact label request/parser on synthetic data before
downloading response artifacts. The local server's documented API supports
`response_format: {"type": "json_object"}`, but that is a request for a
format, not evidence that this checkpoint will honor it. A live rerun must
prove the response shape; do not reinterpret malformed output as a label.

The [third local run](https://github.com/magnus919/agent-skills/actions/runs/35917300013)
passed the real label-contract synthetic probe and produced parseable JSON for
the frozen packet, but at least one item had blank or oversized evidence.
The strict parser rejected the batch before consensus or scoring. We now
request a 1–250-character paraphrase and convert only an item with missing
or oversized evidence to `uncertain`; its `met`/`not_met` suggestion is never
accepted. Invalid IDs, classes, response shape, or missing items still fail
the entire pass. This can retain soundly formatted items while exposing the
model's abstention rate. One bounded rerun should decide whether this local
self-review route offers useful diagnostic coverage; do not tune Jev from
forced labels or report a pass when every item abstains.

The [fourth local run](https://github.com/magnus919/agent-skills/actions/runs/35918057015)
completed on the same frozen source run and small-sample seed. The uploaded
safe artifact reports 10/12 non-uncertain two-pass consensus labels: six
`met`, two `not_met`, two `not_shown`, and two `uncertain`. In the eight-item
population sample, six resolved and two abstained. Jev suggested `met` for
two resolved population items, both also `met` for the local teacher; four
risk-enriched challenge items all resolved `met` for both. The two resolved
non-`met` subtype disagreements are `not_met` versus `not_shown`; they do not
establish an unsafe Jev `met` acceptance. Population precision and Brier
fields remain null because the population has abstentions. The challenge
slice's 4/4 agreement and numeric metrics are **not** accuracy or calibration:
the sample was selected by Jev's high-`met` scores, is tiny, and the teacher
may be the same model that generated the answers.

The local route now has a usable diagnostic contract, but it has not shown
whether Jev's input rubric transfers to the original 44-item packet. We
added an explicit manual `small`/`full` sample profile; the full profile uses
16 candidate/baseline pairs plus 12 high-`met` challenge items. We will run
the previously frozen `jev-543-blind-v1` seed and report the two strata
separately. No model weights are trained and no Jev gate is promoted.

The [full-profile run](https://github.com/magnus919/agent-skills/actions/runs/35920327508)
passed source verification, synthetic label-contract probing, artifact
downloads, and preparation of the original 44-item packet. After roughly
three minutes in the two-pass labeling step, the local model produced a
non-JSON response (`JSONDecodeError`). The script failed closed; it uploaded
no consensus or score. The earlier 10/12 small-screen result cannot be
extrapolated to the full sample. A one-item synthetic probe also cannot
establish structured-output reliability for longer real responses.

Bounded stop for this route: do not keep rewriting the local teacher prompt
against this same packet to obtain a green score. The local model may also
be judging its own generated answers, so even a complete run would be
correlated pseudo-label evidence, not independent Jev calibration. Retain
the full profile as an explicit, manual diagnostic that fails closed; do
not use its absent score, the small screen, or provider confidence to tune
Jev API inputs or set a CI gate. Next meaningful evidence requires a working
separate inference route with authorized data flow, or independently assigned
labels from another approved source.

## 2026-09-23 — Clarifying the optimization target

The user clarified that this work is **not model fine-tuning**. The adjustable
surface is our Jev API request: assertion wording, trusted question text,
Choice criteria, state selection, and grouping. Model weights remain fixed.
The existing synthetic benchmark already screened one rubric revision, but
its 17/18 held-out result did not prevent a high-confidence false `met` on a
real generated response. Repeated local-teacher prompt repair on the same
44-item packet would not remedy that evidence gap, and the full run produced
no valid score. Therefore no new Jev rubric or gate is promoted here.

Next input experiment, once independently assigned real-output labels are
available: freeze the current request and labeled sample; preregister one
specific error hypothesis and candidate input revision; replay both requests
against byte-identical response/criterion pairs; compare false `met` accepts,
`not_met`/`not_shown` confusion, coverage, latency, and probability quality by
slice; then test the chosen revision on untouched examples. Preserve the
known reranking false accept as a regression challenge, not as held-out proof.
The unqueried-label problem is a data/evidence boundary, not a reason to
train Jev or to use a pseudo-label agreement rate as calibration.

## 2026-09-23 — Request-shape provenance for input comparisons

The advisory audit recorded the pinned Jev model and response hashes, but no
fingerprint of its own trusted question instructions and Choice criteria.
That meant two reports from different input rubrics could look comparable
unless a reviewer reconstructed their source revisions. Add a SHA-256 of a
canonical placeholder API request to each audit report and CI summary; it
changes when the model, state/question shape, instructions, or criteria change,
but contains no generated response text. The test changes one criterion and
checks that the fingerprint changes. This improves reproducibility of the
planned input-only experiment; it does not improve or establish grading
accuracy, and no Jev input or required CI gate changes in this revision.

## 2026-09-23 — Live provenance artifact verified

The first main-branch run after the fingerprint change,
[35923727892](https://github.com/magnus919/agent-skills/actions/runs/35923727892),
completed successfully. Its real-model job ran on the single self-hosted
`agent-skills-eval` runner (15m17s after two earlier runs occupied the queue),
then the hosted Jev audit ran. The downloaded advisory JSON is `mode=live`,
requests `jev-1.13.0`, and records question-contract SHA-256
`645c26640eaea298e2cd10bf7e3dd72d2c8c3d702796b1c8b5bd8a39a0cb0f9e`.
That value matches `question_contract_sha256()` from the merged source
revision `b4861628581cae5bdb748ffcbdf6afe522c4bc9d`. Its selection evidence
expects 10 comparison reports and observes exactly 10, with no missing or
unexpected reports. Jev judged all 122 prose assertions in 20 groups; there
were zero skips, budget omissions, or provider errors. This verifies live
artifact provenance and selected-case coverage, **not** the truth of any
`met` suggestion or calibration of its probability.

A nearby main run,
[35923184979](https://github.com/magnus919/agent-skills/actions/runs/35923184979),
also had a green `jev-eval-audit` job, but its selection status was `none`:
zero expected reports, zero observed reports, and zero Jev calls. The earlier
[35922337142](https://github.com/magnus919/agent-skills/actions/runs/35922337142)
was a true live audit with 10/10 reports and 122/122 prose assertions.
Lesson: never cite a green Jev job as model-health or coverage evidence
without inspecting its selection denominator, judged count, and provider
errors. Single-run success also does not substitute for independent labels
or a held-out input comparison.

## 2026-09-23 — Prediction-blind model-review screen and provenance fix

From the complete live artifacts of run
[35923727892](https://github.com/magnus919/agent-skills/actions/runs/35923727892),
we prepared a private 12-item blind packet with seed `jev-569-blind-v1`:
four candidate/baseline assertion pairs (eight population items) and four
remaining high-`met` challenge items. Codex, acting as a **single inference-
model reviewer**, assigned labels from the visible generated responses before
opening Jev's predictions. One ambiguous assertion was marked `uncertain`.
The final private label file has SHA-256
`6001f9a6d471cd9a02ea285bea8b34636a17913e50315a9b16a3abbfec569575`;
neither responses nor labels are published here. This is pseudo-label evidence,
not independent human adjudication or a representative calibration sample.

On the seven resolved population items, Jev and the blind reviewer agreed on
one `met`, one `not_met`, and five `not_shown`; the eighth item was uncertain,
so population precision and Brier remain null. In the four deliberately
high-`met` challenge items, three agreed `met` and one disagreed: Jev
suggested `met` with probability 1.0 for an answer-ID/type/probability
validation assertion, while the blind reviewer labeled the generated
validator `not_met` because it does not compare each **returned answer type**
with the requested question type. This is a concrete review target and an
API-input wording hypothesis, **not** a proven Jev error rate. No threshold
or release gate is changed.

The first score attempt omitted `reviewer_kind`; the helper silently called
the reviewer `human`. We corrected the private file's provenance field to
`model_teacher` without changing any item label and rescored. To prevent a
repeat, missing provenance now reports `unknown`, while the offline human
form/template writes `human` explicitly. Comparison outputs carry reviewer
kinds as well. This is an evidence-integrity fix, not a Jev model change.

A proposed local replay of that private generated response to the TypeSafe
endpoint with a sharper assertion was denied by the environment's approval
review before transmission. We did not retry by another route. The main CI
workflow's prior Jev call does not by itself authorize this separate local
replay; explicit user approval has been requested. Synthetic-only input
checks and offline review remain available in the meantime.

## 2026-09-23 — Second blind screen: execution status is not outcome confirmation

The post-merge [main run 35927793841](https://github.com/magnus919/agent-skills/actions/runs/35927793841)
completed its real-model paired eval and advisory Jev audit. The downloaded
audit requested `jev-1.13.0`, recorded the same question-contract SHA-256
`645c26640eaea298e2cd10bf7e3dd72d2c8c3d702796b1c8b5bd8a39a0cb0f9e`,
observed all 10 expected comparison reports and all 122 selected prose
assertions across 20 groups, and reported zero skips or provider errors.
These are workload and coverage facts, not quality labels.

Using seed `jev-571-population-1`, we froze another private, prediction-blind
single-model review of four candidate/baseline pairs (eight items) from that
run. Its eight item IDs did not overlap the preceding 12-item packet, but
the seed was chosen partly to achieve that non-overlap; this is not a random
or representative draw. No high-`met` challenge items were included. The
private label file SHA-256 is
`46c22f399dbf643fa658438f9981f9160d213f5f194f43aaa5df18bce7f71218`;
it explicitly records `reviewer_kind=model_teacher`. Responses and private
labels are not published.

All eight labels were resolved before Jev predictions were opened. In this
sample the reviewer labeled two `met` and six `not_shown`; Jev agreed on the
two `met` and four `not_shown`, but suggested `met` for two `not_shown` items.
Both disagreements concern the assertion “Separates decision, attempted
execution, and confirmed outcome.” The reviewed responses distinguish a
decision from execution but do not show a separate confirmation of the
external outcome. One uses a decision/action/observation loop; the other
marks an action `EXECUTED` when the action call returns. The latter status
does not, by itself, prove that the intended external effect occurred.
Jev's `met` probabilities on these two items were 0.90 and 0.68. The scorer's
0.50 precision among four suggested `met` labels and 0.199575 binary Brier
score describe agreement with this one model teacher on this selected packet,
**not** accuracy against independent truth or deployment calibration.

API-input hypothesis: the existing compound assertion may let evidence of
decision and execution overshadow the missing confirmation. A candidate
question should ask separately whether the response records (1) decision,
(2) attempted execution, and (3) independently confirmed external outcome,
and should define a return from the executor as insufficient confirmation.
This is a proposed Jev request revision, not model-weight fine-tuning and
not yet an observed improvement. Freeze it before any permitted replay, test
against both known failure cases and untouched cases, and keep the audit
advisory. The earlier local replay denial still applies; do not infer
permission from this offline analysis.

For an operational baseline, the earlier complete run 35923727892 made 20
Jev calls for 122 prose assertions. Per-call reported latency had a 365.0 ms
median, 450.2 ms nearest-rank p95, and 526.9 ms maximum; the sum was about
7.0 seconds. Its Jev job elapsed about 18 seconds, whereas upstream real-model
generation took 15m17s on the single self-hosted eval runner. These two
job durations are not interchangeable: Jev is auditing already-generated
responses, not replacing their production. The artifact contains no cost
figure. Blog lesson: measure the *stage* being optimized, and keep coverage,
reviewer provenance, and semantic validity distinct.

## 2026-09-23 — Input-only development screen rejected a broad evidence reminder

We tested, but did not deploy, one Jev API-input revision suggested by the
blind execution/outcome disagreements. The candidate appended a general
instruction to seek direct evidence for each clause and not equate a plan,
example code path, or successful action-call return with a confirmed external
effect. Model, state, assertion, and Choice criteria remained unchanged. The
current request fingerprint was
`645c26640eaea298e2cd10bf7e3dd72d2c8c3d702796b1c8b5bd8a39a0cb0f9e`;
the candidate's was
`67901b85a17ad6b3fd735a61fcba2213a4cc008a97cd2599486291a1a90c1e76`.
Tests verified that the default request retained its fingerprint and that
only the candidate question instructions differed. No private generated CI
response was sent in this experiment.

On the same 18 author-constructed **development** cases, each rubric made
18 valid calls to `jev-1.13.0`. Both returned the same 17/18 verdicts and
made zero suggested-`met` false accepts. The candidate's binary `met` Brier
score was worse: 0.0649 versus 0.0241 for the current request. At a 0.7
`met`-probability screen it retained only one of the five suggested `met`
cases retained by the current request; this is a descriptive screen, not a
selected automation threshold. Median per-call latency was 395.65 ms versus
378.05 ms in these sequential, unreplicated runs; that difference is too
weak to claim a performance regression. The first unprivileged baseline
attempt failed at DNS before any model response; the complete comparison
used a network-enabled call path and synthetic fixture only.

Because the candidate showed no verdict gain and weaker probability quality
on development data, we did **not** open the synthetic held-out split, replay
private real outputs, change the audit's deployed request, or retain the
experimental code. The current Jev audit contract remains advisory and
unchanged. The two model-teacher disagreements remain a useful failure
hypothesis, but the next question must be more targeted and assessed with
independently adjudicated real-output evidence before promotion. Blog lesson:
explicitly log a failed input revision; a plausible rubric reminder can
reduce confidence in true positives without correcting the observed errors.

## 2026-09-23 — Split the execution/outcome eval claim at its evidence boundary

The broad Jev question reminder failed its development screen, so the next
change targets the assertion itself, which is part of the Jev API input. In
the existing `deadline-bound-stream` eval, “Separates decision, attempted
execution, and confirmed outcome” allowed partial evidence of a decision
loop to obscure the distinct confirmation requirement. The case ID and user
prompt remain stable. Its two revised assertions ask independently whether
the response records a proposed decision separately from an attempted action,
and whether an attempted action requires independent observation of the
external effect before being recorded as successful. The case-level expected
output now names independent confirmation. This changes the eval rubric and
future generated-output distribution; do not compare old and new assertion
counts or scores as though they share one contract.

We constructed a public six-item synthetic challenge fixture with one
`met`, one `not_met`, and one `not_shown` response for each new assertion.
The `not_met` confirmation example explicitly records success on function
return without external observation; the `not_shown` example discusses
deadlines and retries but says nothing about confirmation. Pinned
`jev-1.13.0` classified all six as labeled, with valid responses and no
provider error. This verifies that the revised wording is interpretable on
simple constructed cases; it does **not** show that Jev would have correctly
graded the earlier private generated responses or that real-output accuracy
improved. The fixture is a development regression screen, not independent
ground truth or held-out proof. The CI audit remains advisory; no probability
threshold or release gate is introduced.

## 2026-09-23 — Merged atomic eval reached the live Jev audit

After [PR #575](https://github.com/magnus919/agent-skills/pull/575) merged at
`e2dfadb8ac2a55440ee565df3831468b5a0fc2b8`, the exact
[main run 35931348911](https://github.com/magnus919/agent-skills/actions/runs/35931348911)
completed successfully. Real-model generation and the downstream advisory
Jev audit both ran. The downloaded audit is `mode=live`, requested
`jev-1.13.0`, observed 10/10 selected comparison reports, and judged all
124/124 prose assertions in 20 groups. It recorded zero skipped responses,
oversized items, budget omissions, or provider errors. The two extra
assertions versus earlier 122-assertion runs are the candidate/baseline
instances created by splitting one assertion in this case.

For `deadline-bound-stream`, Jev suggested `met` for the baseline and
`not_shown` for the candidate on the decision-versus-attempt assertion.
It suggested `not_shown` for both on the independent-outcome-confirmation
assertion. The generated candidate design says to observe the outcome after
acting but does not clearly specify a separate confirmed-success record.
The baseline example sets `EXECUTED` when the action function returns, with
no independent confirmation before that status. These observations make the
new `not_shown` outcome judgments plausible, but this inspection happened
**after** reading Jev's answers; it is not a prediction-blind label or an
accuracy measurement. The distinction between an explicit contradiction
(`not_met`) and missing confirmation evidence (`not_shown`) remains worth
independent adjudication.

The audit's generic question-contract SHA-256 stayed
`645c26640eaea298e2cd10bf7e3dd72d2c8c3d702796b1c8b5bd8a39a0cb0f9e`.
That fingerprint covers the template instructions and Choice criteria but
not individual eval assertion text; the **actual API questions changed**
despite the same template hash. Compare manifest revision and assertion
text as well as the generic fingerprint when attributing outcomes. This
live run verifies delivery and complete selected-case coverage, not Jev
calibration or fitness for a required release gate.

## 2026-09-23 — Fingerprint each exact Jev question input

The atomic eval run showed a provenance gap: the generic placeholder
`question_contract_sha256` stayed constant while the actual assertion text
sent to Jev changed. The auditor now records a per-result
`question_input_sha256` of the pinned model and the full trusted questions,
including each assertion and Choice criteria, but excluding generated response
text. The existing `response_sha256` remains separate, so an investigator can
distinguish question drift from answer drift without publishing either text.
Tests verify that changing an assertion or criterion changes the question
fingerprint, while changing only the generated response does not.

The private calibration helper verifies the exact-question fingerprint
against the downloaded comparison bundle when it is present and rejects a
mixture of fingerprinted and legacy rows. Fully legacy audits remain readable
but cannot claim this new provenance. The `calibration-review` skill eval now
asks for exact-question and criterion versioning as an output-quality claim.
This adds auditability, **not** Jev accuracy, independent labels, permission
for local replay, or a release gate. The merged main-branch run must still
prove that these new fields appear in the live artifact.

## 2026-09-23 — Exact-question fingerprints verified in the main audit

The first main-branch run after [PR #577](https://github.com/magnus919/agent-skills/pull/577),
[35933798600](https://github.com/magnus919/agent-skills/actions/runs/35933798600),
completed real-model generation and the advisory Jev audit successfully at
merge SHA `c0706efdbad24d583f0c517fedf0dc37f179837a`. Its downloaded
`mode=live` audit requested `jev-1.13.0`, expected and observed 10/10
comparison reports, selected and judged all 126 prose assertions across
20 groups, and reported zero skips, budget omissions, or provider errors.
The two additional judgments versus the preceding 124-assertion run reflect
the added `calibration-review` assertion on candidate and baseline; these
are different eval contracts, not an accuracy trend.

All 20 result rows carried 64-character `question_input_sha256` values.
There were 10 distinct exact-question hashes, one per case; each
candidate/baseline pair shared a hash while retaining distinct response
hashes. The private calibration helper matched the live audit to its
downloaded comparison bundle and reconstructed all 126 review records,
verifying each exact-question fingerprint against the source assertion text
and the running rubric. The audit artifact SHA-256 was
`beae26ca4fb0d1285bdc8f972630eafd93d5d123169b9d371747d50386905891`.
No generated response text or labels were published in this runlog.

This proves the new provenance field is deployed on the actual CI path and
detectable by the calibration helper. It does not show Jev's verdicts are
correct, that its probabilities are calibrated, or that an advisory label
can become a required gate. The generic template hash remained constant;
the per-group hashes are the evidence that exact questions can now be
distinguished.

## 2026-09-23 — Make the CI reference deployment operable

The audit and this runlog had accumulated evidence, but a copier still had
to reconstruct setup, verification, failure handling, and rollback from
workflow YAML and dated entries. Add the focused
`system-one/references/jev-ci-reference-deployment.md` operator guide and
route to it from the skill. It names the exact main-branch data flow, secret
and runner prerequisites, selected-case and assertion denominators, private
artifact handling, zero-call interpretation, and a reviewed no-egress
rollback that preserves deterministic checks. Add a dedicated output-quality
eval case for that operator task instead of assuming the guide is sufficient
because it exists.

The additional eval case adds two candidate/baseline response groups. Raise
the explicit Jev budget from 20 to 22 calls while retaining the 160-assertion
cap; if the workload exceeds either, the audit must report omissions rather
than silently shrink its denominator. The prior verified run had 126 prose
assertions across 20 groups, so this case should fit at roughly 140
assertions across 22 groups, but actual generation and audit coverage still
need verification after merge. This change does not make Jev a required
grader or replace the open-ended response generator or Droid review.

The first PR check failed in `test_current_system_one_manifest_fits_ci_audit_budget`:
its repository guard still asserted the former 20-call cap. This was not a
Jev provider failure. Update the guard to require the deliberate 22-call
budget and prove the expanded manifest fits; keep this check so later eval
growth cannot silently exceed the CI selection budget. Re-run the focused
suite before relying on the PR check.

## 2026-09-23 — Operator-guide workload verified on main

[PR #579](https://github.com/magnus919/agent-skills/pull/579) merged at
`e14cbbb2a29f4bed277fb8070e2ab95a03047005`. The matching main-branch
[run 35936520162](https://github.com/magnus919/agent-skills/actions/runs/35936520162)
completed the real-model generator and advisory Jev audit successfully. The
downloaded audit reported `mode=live`, requested `jev-1.13.0`, selected the
expected 11/11 comparison reports, and judged all 140/140 prose assertions
across 22 candidate/baseline groups. It reported zero skipped responses,
oversized assertions or groups, budget omissions, unattempted groups, and
provider errors. The audit remained `advisory_only=true`.

All 22 rows had 64-character exact-question SHA-256 fingerprints. There were
11 distinct question hashes, one per case, and each candidate/baseline pair
shared its question hash. Against the privately downloaded comparison bundle,
`records_from_artifacts` reconstructed all 140 review records and verified
the response and exact-question identities. The first artifact download hit a
transient GitHub API connection error; retrying the same run succeeded. No
generated response text was published here.

This establishes that the operator guide's new case fits the actual CI
budget and that complete Jev coverage is observable in this deployment. It
does **not** establish correct verdicts, calibrated probabilities, or an
appropriate release gate. Those still require independent real-output labels
and held-out evaluation; green jobs and complete coverage are necessary but
not sufficient.

## 2026-09-23 — Reopen the separate teacher route at a synthetic boundary

The main-only Nous teacher workflow had repeatedly received HTTP 404 from
`/v1/chat/completions`, so it never labeled the frozen real-output packet.
The separate, unmerged Droid/Nous experiment showed that a minimal
GPT-6 Luna request to `/v1/responses` can return HTTP 200; it did **not**
establish a working teacher label contract or deploy Droid review. We changed
only the remote teacher transport to request a low-reasoning, non-stored
Responses result. The local-model diagnostic retains its chat-completions
transport. Offline tests cover the prediction-blind request, reversed item
order, completed-response parsing, and incomplete/multiple-output rejection.

The manual workflow now probes the **actual label request and parser** on a
synthetic example before downloading any generated response artifact. If the
remote model does not return the required JSON labels or declines to mark the
obvious synthetic case `met`, the workflow stops without private-data egress.
This is a new feasibility attempt, not a calibration result. Even if a live
run succeeds, its two-pass consensus will be pseudo-label evidence, not
independent ground truth or a Jev release threshold. The target remains
tuning our Jev API input contract; no model weights are changed.

## 2026-09-23 — First complete separate-model teacher screen

After the owner approved Nous inference on this repo's private generated
paired-eval response and assertion text, [PR #581](https://github.com/magnus919/agent-skills/pull/581)
merged the Responses-route teacher change. The manual
[run 35940465551](https://github.com/magnus919/agent-skills/actions/runs/35940465551)
used the completed main Jev source run 35936520162 and frozen seed
`jev-543-blind-v1`. It passed the synthetic label-contract probe *before*
downloading source artifacts, completed two prediction-blind teacher passes,
and uploaded only the safe summary and aggregate score. A private local replay
of the 44-item selection matched the uploaded blind-item SHA-256 exactly.

Two-pass teacher consensus resolved 37/44 items: 19 `met`, four `not_met`,
14 `not_shown`, and seven `uncertain`. In the population slice, 26/32
resolved; one of nine Jev suggested-`met` items was `not_met` by both teacher
passes. The challenge slice resolved 11/12, all 11 agreeing on `met`; it was
selected for high Jev `met` probability and is not a representative accuracy
sample. The sole resolved population false-`met` disagreement concerned the
baseline response for `jev-ci-operations` and the public assertion requiring
expected-versus-observed selected-report coverage **and all** skip/error
counters. Jev's `met` probability was 0.59 and provider confidence 0.38;
both teacher passes said `not_met`. No generated response text or teacher
rationales were published.

This is a useful input-design hypothesis: a compound audit-coverage assertion
may invite partial-credit `met` even when a required counter is absent. It is
not independent adjudication of the case. Do not set a 0.7 gate merely because
it would screen out this example, and do not report precision or Brier from
the resolved subset while six population items abstained. Next, inspect the
private response locally, split any separable eval claim on its intended
behavior rather than for a favorable Jev score, then preregister a targeted
input comparison and test on untouched examples. Keep Jev advisory.

## 2026-09-23 — Separate selected-report proof from counter accounting

Private inspection of the flagged baseline response found a generic proposed
fork workflow with example paths, not evidence that this repository's actual
selected report identities, counts, and Jev skip/error lanes were reconciled.
The former `jev-ci-operations` assertion combined those two independently
checkable operator obligations. Keep the case ID and prompt stable, but split
the assertion into one check for expected-versus-observed selected report
identities and counts and another for all skip, omission, not-attempted, and
provider-error lanes before claiming complete assertion coverage. This is an
eval-contract change; any subsequent verdict counts or question fingerprints
are **not directly comparable** with the 140-assertion run. The change was
motivated by the actual operator procedure and a witnessed near miss, not by
an attempt to raise Jev's score. A live run must still show that the expanded
manifest fits the 22-call/160-assertion budget and preserves full coverage.

## 2026-09-23 — Split coverage claims reached the live audit

The merged [PR #583](https://github.com/magnus919/agent-skills/pull/583)
produced main [run 35941490540](https://github.com/magnus919/agent-skills/actions/runs/35941490540)
at `a8f60faa4d889737c3214f1388f78437f9bb06af`. Real-model generation
and the advisory Jev job both completed. The downloaded `mode=live` audit
requested `jev-1.13.0`, selected the expected 11/11 reports, and judged all
142/142 prose assertions across 22 groups. All skip, budget-omission,
not-attempted, and provider-error counters were zero. All 22 rows had valid
exact-question hashes; the 11 candidate/baseline pairs shared their respective
question hashes. The private calibration helper matched the audit to the
downloaded comparison bundle and reconstructed all 142 records with response
and exact-question identities verified.

For `jev-ci-operations`, Jev suggested `met` for selected-report identity/count
reconciliation and `not_shown` for full skip/omission/error-lane accounting on
both candidate and baseline. The case's exact-question hash changed from
`e16d1ffc3a857aedc306f3b4d4dc276a403cbc38cb5c44653af1d92044238aac`
to `55a24a352f44b531e2f5c7e4df6196502a094d9a16a6aa08257b6d6b99512a95`.
These verdicts illustrate the split's diagnostic resolution, **not** an
accuracy gain. The candidate and baseline response hashes for this case
matched the earlier run, but its question hash changed and no independent
labels have been assigned for the new assertions. Do not combine it with the
140-assertion teacher screen as though the questions were byte-identical.
No generated response text was published here.

## 2026-09-23 — Selection identity and count are distinct evidence

The approved Nous teacher screen on the new contract,
[run 35943607782](https://github.com/magnus919/agent-skills/actions/runs/35943607782),
passed its synthetic probe and completed two prediction-blind passes. A
private local reproduction of the frozen 44-item packet matched its published
blind-item SHA-256. Consensus resolved 38/44: 20 `met`, three `not_met`,
15 `not_shown`, and six `uncertain`. In the population slice 27/32 resolved;
one of ten Jev suggested-`met` items was `not_shown` by both teacher passes.
The high-`met` challenge slice resolved 11/12, all agreeing on `met`; this
enriched slice is not representative. These are correlated model pseudo-labels,
not accuracy or calibrated probabilities.

The disagreement was the `jev-ci-operations` candidate's selected-report
assertion. Jev suggested `met` at 0.77 `met` probability and 0.64 provider
confidence, while both teacher passes said `not_shown`. Private inspection
found an example expected-versus-queried **count** comparison and per-eval IDs,
but no comparison of expected selected **IDs** with observed report IDs or
missing/unexpected reports. This is a concrete partial-evidence shape, not a
reason to choose a probability threshold. Preserve the case ID and prompt;
split the assertion into independently checkable selection-identity and
selection-count claims. This changes the eval/question contract again. Test
the expanded budget and verify a new main audit; do not compare verdict totals
across contracts or publish the generated response text.

## 2026-09-23 — Identity/count split verified in the actual Jev audit

Merged [PR #585](https://github.com/magnus919/agent-skills/pull/585)
produced main [run 35944221843](https://github.com/magnus919/agent-skills/actions/runs/35944221843)
at `62d8c76deac80cec6b0cc7d90a3fd34111c50338`. The real-model and Jev
jobs completed. The `mode=live`, advisory audit requested `jev-1.13.0`,
observed the expected 11/11 selected reports, judged 144/144 prose assertions
across 22 groups, and reported zero skips, budget omissions, unattempted
groups/assertions, or provider errors. Its 22 rows carried 64-character
exact-question hashes, shared by candidate/baseline pairs. The private
comparison-bundle check reconstructed all 144 records and verified their
response and exact-question identities.

For `jev-ci-operations`, Jev suggested `not_shown` on expected-versus-observed
selected case-ID reconciliation and `met` on selected-report count comparison
for both candidate and baseline. It also kept complete skip/error-lane
accounting `not_shown`. This demonstrates that the revised *questions* expose
the witnessed count-only near miss as distinct verdicts on this run. It does
not prove the model is generally accurate, calibrated, or ready to gate CI;
the question contract changed, no independent labels cover the new assertions,
and the earlier model-teacher labels were pseudo-labels. Do not interpret the
change as a before/after accuracy improvement or publish generated responses.

## 2026-09-23 — Preregistered synthetic coverage-question experiment

This is an input-only experiment, not model training. The author-constructed
`system-one/examples/jev-ci-coverage.synthetic.json` has six development and
six reserved test cases, balanced across `met`, `not_shown`, and `not_met`.
It tests selected-report identity and count reconciliation, including explicit
false-completeness claims. The deployed Jev question scored 5/6 development
labels with binary `met` Brier 0.1579. On CID-D06 it returned `met` with
`met_probability=0.95` and provider confidence 0.93 although the response
states expected=4 and observed=3, then calls the mismatch harmless. This is
synthetic evidence of a consequential false accept, not an estimate of live
accuracy or calibration.

**Candidate (fixed before further calls):** append this exact sentence to the
single-question `instructions`, leaving model, assertion, state, choice labels,
and criteria unchanged: “A comparison is not itself success: if the response
shows a mismatch and still recommends claiming the assertion's successful
condition, choose not_met.” First run the six development cases. Proceed only
if CID-D06 is no longer a false `met`, there are no new false `met` accepts,
and binary `met` Brier is no worse than 0.1579. If that passes, compare on the
existing 18-case development fixture with paired baseline calls; require no
new false accepts and no worse Brier. Only then run the six reserved test cases.
Stop at the first failed gate and report the candidate as rejected. Even a
passing synthetic screen does not authorize a CI rollout or release gate:
independent representative real-output labels are still required. Only
synthetic response text may be sent to TypeSafe in this local experiment.

**Observed screen:** The candidate passed the six-case development gate:
6/6 labels versus baseline 5/6; binary `met` Brier 0.0262 versus 0.1579;
CID-D06 changed from `met` (0.95) to `not_met` (0.01), with no new false
accepts. On the paired existing 18-case development fixture it scored 18/18
versus baseline 17/18, with zero false `met` accepts in both and Brier 0.0195
versus 0.0237. The reserved six-case synthetic test scored 5/6 versus baseline
2/6, zero versus one false `met` accept, and Brier 0.0511 versus 0.1786.
The candidate corrected the test's explicit count-mismatch false accept
(CID-T06), but still marked a count-only omission `not_met` rather than
`not_shown` (CID-T02). These are small, author-constructed, balanced examples;
they are not independently sampled operational labels, and the provider's
confidence values are not calibrated by this screen. The single wording change
is promising for a future separately reviewed rollout, but the deployed Jev
question remains unchanged. Do not infer a release threshold or promote the
advisory result to a CI gate.

## 2026-09-23 — Shadow CI comparison boundary

The next proposed step was to compare the candidate question instruction on
the *same* private generated paired-eval responses as the deployed Jev audit.
That would require a second transmission of those responses to TypeSafe.
The CI workflow edit for this extra pass was rejected by the execution
reviewer because this specific private-payload/destination flow lacks explicit
authorization. No shadow CI call or private local replay was made. The
workflow and deployed Jev question remain unchanged.

For reproducible **synthetic-only** development, the audit and benchmark now
accept `mismatch-shadow-v1` as an explicit question variant; the default stays
`deployed`. The variant is recorded in each report and changes the exact
question fingerprint. A later CI shadow experiment needs specific approval
for retransmitting private generated eval responses to TypeSafe, a separate
artifact, and a comparison against independent labels before any promotion.
No variant verdict alone is evidence of calibration or permission to gate.

## 2026-09-23 — CI inference replacement inventory

Reviewed `.github/workflows/skill-eval.yml`, `droid-review.yml`,
`skillevaluator.yml`, and `ci-failure-to-issue.yml` for inference that could
move to Jev. The paired-eval generator needs open-ended skill responses;
replacing it with a typed decision would remove the behavior under evaluation.
The existing Jev prose-assertion audit is already the natural bounded
decision-helper insertion point. The Droid workflow performs broad code and
security review; its main output is explanatory findings and suggested fixes,
which Jev's typed judgments cannot produce. A separate Jev risk/severity
classifier could be evaluated as a routing aid, but no CI contract or labeled
review set currently supports that addition. SkillEvaluator explicitly runs
the keyless Tier 1 checks `schema,pii,license,quality,unicode,lint`; its
workflow comments say these checks exclude security scanning, and its optional
LLM scan is not configured. The failure-to-issue workflow maps a failed main
validation run to a fixed issue template and deduplicates by labels/title;
there is no model inference to replace there.

Current decision: keep the paired-eval generator and Droid review as text
generation/review stages. Evaluate a Jev classifier beside Droid only if a
bounded routing question, ground-truth outcomes, and a safe fallback are
defined; do not present a typed classifier as a replacement for code review.
The additional question-wording shadow on paired-eval outputs remains pending
specific approval for its second TypeSafe transmission. At this point the only
deployed Jev use remains the advisory paired-eval prose audit.

## 2026-09-24 — Real-output teacher screen found a compound control-loop miss

Main run [35946700587](https://github.com/magnus919/agent-skills/actions/runs/35946700587)
completed successfully at `f7819d0f2048d1b71e0c261c660476965aa26602`: 11/11
selected comparison reports and 144/144 prose assertions across 22 groups,
with no audit omissions or provider errors. The approved two-pass Nous Portal
teacher run [35948040662](https://github.com/magnus919/agent-skills/actions/runs/35948040662)
resolved 40/44 labels; four were uncertain. On the challenge stratum, Jev
suggested `met` for all 12 high-probability items; the teacher agreed on 11
and labeled one `not_met`. Population labels were 28/32 resolved, with four
uncertain and no Jev-suggested `met` disagreement among resolved labels. These
are correlated model pseudo-labels, not human truth or calibration.

The disagreement was `system-one/deadline-bound-stream`, baseline side,
assertion “Bounds in-flight work and handles duplicate events or retries”:
Jev gave `met` probability 0.97 and provider confidence 0.96; Nous consensus
was `not_met`. Private local inspection of the response revealed a bounded
input queue, but the proposed downstream decision queue had no declared
capacity and the action-failure handler was a placeholder. It also discussed
retrying after a timeout without a demonstrated durable/downstream idempotency
guarantee. The case output combines backpressure, queue bounds, duplicate
suppression, retry limits, and ambiguous side-effect recovery, so the single
verdict does not show which criterion was missing. No generated response text
or teacher rationale is retained here.

Refine the existing `deadline-bound-stream` assertion into separately
checkable questions for inference concurrency, input-queue capacity and
overflow, action-queue capacity and overflow, duplicate side-effect
prevention, finite retries, terminal handling, and idempotency across
uncertain timeouts. This replaces one claim with eight, adding 14 judgments
across candidate and baseline and taking the observed 144-assertion audit
shape to 158, within the current 160-assertion cap. This is contract
refinement grounded in a concrete partial
implementation, not a prompt tweak to inflate scores. The changed eval will
receive a new Jev audit on its next successful main run; compare only matching
assertion/question fingerprints. A Jev shadow re-audit of the old private
response still requires the separately requested TypeSafe data-flow approval.

## 2026-09-24 — Atomic assertion contract exercised in main CI

Main run [35949075876](https://github.com/magnus919/agent-skills/actions/runs/35949075876)
at `3dbbd18e5cb5b613a05eedbc727aae553ec7bfaf` completed all four jobs. Its
standard live Jev audit covered 11/11 selected reports, 22 groups, and all
158/158 prose assertions with zero skips, omissions, or provider errors. The
model output was regenerated after the assertion contract changed, so do not
compare its totals with the preceding 144-assertion run as an accuracy delta.

The approved Nous screen [35950558246](https://github.com/magnus919/agent-skills/actions/runs/35950558246)
resolved 39/44 labels; five were uncertain. In the 12-item high-probability
challenge stratum, Jev had zero suggested-`met` disagreements. In the
32-item population sample, 27 labels were resolved and Jev had one
suggested-`met` disagreement. It was a candidate `deadline-bound-stream`
assertion requiring independent observation before recording success: Jev
returned `met` probability 0.58 and provider confidence 0.37; Nous consensus
was `not_shown`. This remains one model's pseudo-label against another model,
not a human adjudication or calibrated rate.

The selected atomic rows also separated evidence shapes: for the candidate's
stable-idempotency assertion both models said `not_shown`; for the baseline
the same Jev verdict had a Nous `not_met` consensus. On retry-limit policy,
candidate Jev and Nous both said `not_shown`, while baseline Jev said `met`
with probability 0.93 and Nous was uncertain. Preserve uncertainty and do not
average it into a forced label. These few sampled rows show why splitting the
compound criterion is diagnostically useful, but they do not establish that
the changed eval improved model quality.

## 2026-09-24 — Preregistered prose-versus-procedure conflict screen

The revised audit still found one population disagreement on
`deadline-bound-stream`: for “Requires independent observation of the external
effect before recording an attempted action as successful,” Jev suggested
`met` at 0.58 probability and 0.37 provider confidence; Nous consensus was
`not_shown`. The generated answer's summary described observation, while its
pseudocode recorded success immediately after the submit call. This is a
concrete prose/algorithm conflict shape. It is not proof Nous is correct or
that Jev has calibrated confidence.

Before additional Jev calls, created
`system-one/examples/jev-procedure-conflict.synthetic.json`: 12
author-labeled synthetic cases, split evenly into six development and six
reserved test examples, with two `met`, two `not_met`, and two `not_shown` in
each split. The candidate question appends this exact instruction:
“When prose summaries conflict with a concrete algorithm, pseudocode, or code
path, judge the concrete path. A safeguard named in prose is not established
if the steps omit it or record success before it occurs.” No model, state,
assertion, answer options, or criteria change.

Screen deployed and candidate wording on the six development cases. Open the
reserved test split only if the candidate does not falsely accept the explicit
summary/code contradiction (PC-D02), does not increase false `met` accepts,
has accuracy no worse than deployed wording, and has binary `met` Brier no
worse than the paired baseline. If any condition fails, stop and reject the
candidate. If they all pass, run the same six held-out cases once and report
all results. These author-constructed synthetic cases can test input
mechanics only; they do not justify changing live CI, confidence thresholds,
or release behavior. No private generated response is included in this
screen.

**Observed first screen:** Deployed wording scored 5/6 development labels and
binary `met` Brier 0.0000333. `procedure-conflict-shadow-v1` also scored 5/6,
with Brier 0.0001000, and made no prediction changes across the six cases.
Both versions correctly rejected PC-D02, so v1 did not fix a baseline false
accept; both incorrectly called the underspecified PC-D03 `not_met`. The
preregistered Brier condition failed, so v1 is rejected and the six reserved
test cases remain unopened. The tiny Brier difference is not meaningful as a
population estimate; it is retained because the screen's stop rule was frozen
before calls.

**Second development-only candidate (fixed before calls):** append this exact
sentence instead: “Distinguish missing evidence from contradiction: if the
procedure omits an independent observation without specifying an incompatible
success rule, choose not_shown; if it records success on submission or
acknowledgment before observation, choose not_met, even when a summary claims
verification.” Reuse only the six development examples for this iteration.
Proceed to the still-unopened test split only if v2 correctly labels both
PC-D02 and PC-D03, creates no false `met`, has accuracy at least 5/6, and
binary `met` Brier no worse than the frozen deployed baseline 0.0000333.
Otherwise reject v2 and stop. This limited synthetic screen remains input
development, not calibration or authority to change live CI.

**Observed reserved test screen:** Deployed wording and v2 each scored 6/6
labels with zero false `met` accepts. Their binary `met` Brier scores were
0.0001833 and 0.0004500 respectively. V2 corrected PC-D03 on development but
made no classification change on the reserved test cases and had worse
probability error there. The instruction is therefore not promoted to the
deployed contract. These 12 obvious synthetic cases do not estimate CI
performance; the candidate remains an experiment, and the default question
remains in use. The real-run disagreement was not replayed to Jev.

## 2026-09-24 — Repeated Nous labels separate stable disagreement from noise

Compared the approved two-pass Nous Portal screens for Jev audits
[35950558246](https://github.com/magnus919/agent-skills/actions/runs/35950558246)
and [35953231307](https://github.com/magnus919/agent-skills/actions/runs/35953231307)
entirely from already-downloaded local artifacts. No model call was made for
this comparison, and no generated answer text is retained here. The screens
used the same Nous model and prompt revision; each resolved 39/44 items and
left five uncertain.

Of the 44 hashed item IDs in each screen, 43 overlapped and all 43 had
identical generated-response hashes. Nous gave the same resolved consensus on
all 36 overlapping items resolved in both runs. The other seven had at least
one `uncertain` consensus and are not counted as agreement. Jev kept the same
suggested verdict on 42/43 shared items; mean absolute change in its `met`
probability was 0.0058 (maximum 0.05). The single verdict flip was
`system-one/jev-ci-operations`, candidate side: “Describes a reviewed way to
disable Jev egress while preserving deterministic validation and the original
red CI result.” Jev changed `not_shown` to `not_met` while its `met`
probability stayed 0.11 (provider confidence 0.20 to 0.17). This is a small
decision-boundary stability observation, not evidence that either verdict is
correct.

One disagreement did persist on identical bytes: for the candidate
`deadline-bound-stream` assertion requiring independent observation before
recording success, Jev suggested `met` in both runs (probabilities 0.58 and
0.57; provider confidence 0.37 and 0.34), while Nous consensus was
`not_shown` both times. The second run also had a Jev `met` / Nous
`not_shown` disagreement on the baseline finite-retry-limit assertion (Jev
probability 0.93, provider confidence 0.89); the first run's Nous label for
that item was `uncertain`, so this is not a repeated disagreement.

This repeated-output screen helps prioritize what to inspect: the
independent-observation claim is a reproducible Jev/Nous disagreement, while
most other labels and verdicts were stable. The same-model Nous consensus is
correlated pseudo-label evidence, not ground truth; uncertain items stay
unresolved. Do not infer accuracy, confidence calibration, a threshold, or a
release gate from these runs. Blog lesson: repeatability can distinguish a
persistent review question from a one-run disagreement, but it cannot settle
the question without independent adjudication.

## 2026-09-24 — Broaden real-output review and split compound performance claims

The complete main-branch Jev audit for run
[35929395680](https://github.com/magnus919/agent-skills/actions/runs/35929395680)
covered all 7 `performance-optimization` reports and 68/68 prose assertions,
with no skipped assertions, budget omissions, or provider errors. Its existing
private model/audit artifacts supplied a second-skill screen; the responses
were not sent to Jev again. The approved Nous workflow
[35954790516](https://github.com/magnus919/agent-skills/actions/runs/35954790516)
used `openai/gpt-6-luna`, prompt revision `jev-blind-teacher-v1`, and two
prediction-blind passes over a fixed 44-item packet. Nous consensus resolved
40/44 items and left four uncertain. In the uniform population stratum, Jev
and Nous agreed on 22/28 resolved items; in the intentionally high-Jev-`met`
challenge stratum they agreed on 12/12. The sample covers one additional
skill, not the catalog, and the challenge stratum is not workload prevalence.

The six resolved population disagreements were mixed, not six verified Jev
errors. They included one Jev `met` versus Nous `not_shown` on whether the
response required repeated, controlled baseline/candidate measurements and
reported variability; three Jev `not_shown` versus Nous `not_met` judgments;
one `not_shown` versus `met`; and one `not_met` versus `met` on a negatively
worded proxy-metric assertion. Local inspection showed that several reviewed
assertions each joined independently checkable requirements, including
journey selection and boundaries, telemetry audit and instrumentation details,
benchmark controls and spread, and profile validation and post-gain checks.
Nous labels remain correlated model pseudo-labels; they do not resolve those
disputes as ground truth.

As a behavior-preserving eval-contract change, split only the compound claims
in `unmeasured-user-journey`, `noisy-benchmark-comparison`, and
`profile-guided-service-optimization`. The new assertions separately expose
journey choice/start/completion; existing-signal audit, missing boundary,
minimum instrumentation, version context, privacy, overhead, and sampling;
repeated paired measurements, matched workload/fixture, controlled and
recorded conditions, and variability; and trace/profile correspondence,
representative workload, correctness, evidence classification, and
re-profiling. Case IDs, prompts, and expected outcomes remain unchanged. The
new 49 assertions across candidate and baseline produce 98 judgments, within
the live 160-assertion Jev budget. A `proxy-metric-validation` negation claim
was deliberately left unchanged: one low-confidence disagreement is not a
reason to rewrite a valid assertion toward a teacher label.

The split claims were checked against a response that supplies the evidence,
a near miss that contradicts or omits one requirement, and an answer with no
evidence for it. The paired fake-adapter run still executes all 7 cases; its
`both_pass` labels are only harness structure, while every semantic assertion
remains `manual_review`. Do not treat either Nous agreement or green fake
smoke as proof of semantic accuracy. The next live main run must verify the
98-judgment Jev audit has complete selected-case coverage and no budget
omissions; compare with earlier totals only for unchanged question/assertion
fingerprints. Blog lesson: the second skill exposed the same practical value
of atomization without justifying prompt overfitting—small independent claims
make disagreements actionable while preserving the eval's original behavior.

## 2026-09-24 — Separate environment, warmup, and evidence-order judgments

After PR #594, main paired-eval run
[35956308198](https://github.com/magnus919/agent-skills/actions/runs/35956308198)
completed all 7 `performance-optimization` reports. Its Jev audit selected
all 98/98 prose assertions across 14 groups, with zero skipped assertions,
budget omissions, or provider errors. The selected report count matched the
expected count. This is complete advisory coverage, not a semantic pass rate.

With explicit Nous authorization, teacher run
[35956827256](https://github.com/magnus919/agent-skills/actions/runs/35956827256)
used `openai/gpt-6-luna`, prompt revision `jev-blind-teacher-v1`, and two
prediction-blind passes over a frozen 44-item packet (seed
`performance-optimization-atomic-claims-20260924-v1`). Nous resolved 37/44
labels and left 7 uncertain. Jev and Nous matched on 32/37 resolved items:
20/25 in the population sample and 12/12 in the intentionally high-Jev-`met`
challenge stratum. The challenge stratum is not workload prevalence. These
remain correlated model pseudo-labels, not independent ground truth or
probability calibration.

Five resolved disagreements concentrated in two cases. On the noisy benchmark
case, Jev said `met` and Nous `not_shown` for the environment-control assertion
on both candidate and baseline; for the combined environment-and-warmup
assertion on the baseline, Jev said `met` and Nous `not_shown`. Local inspection
found concrete environment controls in both answers, no warmup discussion in
the candidate, and a generic warmup recommendation in the baseline. The old
assertion bundled independent questions about environment details and warmup,
so that disagreement could not identify which evidence was missing. On the
profile-guided case, Jev said `not_shown` for workload reproduction on both
sides; Nous said `met` for the candidate and `not_met` for the baseline. Local
inspection found that the candidate puts representative workload replay
before fix selection, while the baseline offers specific batching/caching
fixes before its later staging/load-test validation. This is an ordering
distinction, not proof that either model is always right. No response text or
teacher rationale is retained here.

Refine the existing contract, preserving every case ID, prompt, and
`expected_output`: split environment parity from naming a concrete environment
control and from stating a shared warmup policy; make workload replay an
explicit prerequisite to choosing a fix. These wording changes express the
existing case outcomes more literally; they do not adopt Nous labels as truth.
The eval now has 50 assertions (100 candidate/baseline judgments), below the
160-assertion audit cap.

Reviewed challenge shapes before testing:

- Satisfying environment evidence names a shared runner/build and controlled
  CPU/load conditions; a near miss changes runner or build between versions;
  an omitted-evidence response says nothing about test conditions.
- Satisfying warmup evidence states that both versions use the same
  pre-measurement protocol or explains why warmup is unnecessary; a near miss
  warms only the candidate; an omitted-evidence response gives no warmup
  guidance.
- Satisfying workload-order evidence requires a representative large-account
  replay before selecting a fix; a near miss picks batching/caching first and
  validates only after implementation; an omitted-evidence response gives
  general profiling advice without workload evidence or ordering.

The fake paired-eval path still checks all 7 cases structurally; semantic
assertions remain `manual_review`. The next successful main run must cover all
100 assertions without omissions before the new wording is assessed. Let the
normal Jev audit see the newly generated responses once; do not replay private
responses to Jev. An approved Nous pass can again provide low-toil triage, but
neither it nor CI green status authorizes a confidence threshold or release
gate.

Blog lesson: a disagreement is most useful when it exposes a missing rubric
dimension or ordering distinction. Split the criterion, preserve uncertainty,
and avoid turning a second model's vote into ground truth.

Provenance caveat for the next screen: after this source run, main PR #595
routed paired-response generation through Nous `stepfun/step-3.7-flash:free`.
The frozen source outputs above predate that change. A future gpt-6-luna
teacher pass would share Nous as a provider with the StepFun generator, making
the pseudo-labels more correlated; record both exact model IDs and treat the
comparison as diagnostic disagreement triage only, not independent
validation.

## 2026-09-24 — Keep generation failures out of Jev coverage

The post-merge run
[35958317434](https://github.com/magnus919/agent-skills/actions/runs/35958317434)
selected all 7 `performance-optimization` cases, but both candidate and
baseline generation failed with HTTP 400 for every case (14 failed sides).
The paired runner nevertheless exited successfully because its exit status
only considered candidate regressions. The Jev artifact reader then treated
all 100 `infra_error` assertion rows as untouched exact checks, counted zero
prose assertions, and made no Jev calls. This was not a Jev result, not complete
semantic coverage, and not evidence about model quality.

The approved Nous teacher workflow rejected the same source run before making
either teacher pass: the audited result identities did not cover the selected
case identities. No generated response text was sent to Nous in that failed
attempt. This fail-closed behavior is correct and should remain.

The follow-up changes make infrastructure errors fail the paired-model job,
report generation-error sides and skipped assertions separately from exact
checks, mark the Jev audit incomplete, and refuse to prepare calibration data
from errored generations. The Nous request also stops sending the
non-standard `chat_template_kwargs` extension previously added to disable
thinking. A fresh main run still returned HTTP 400 after that extension was
removed, so this change did not resolve the failure and the extension is not a
sufficient explanation. Do not replay these failed outputs to Jev or a teacher
model.

Focused paired-runner, Jev-audit, and calibration tests pass; eval validation
remains 181/181 schema-valid and the eval coverage ratchet is unchanged. Blog
lesson: distinguish “artifact exists” from “model response exists,” and
“selected reports found” from “assertions actually judged.” Preserve those
denominators explicitly before making claims about coverage or quality.

## 2026-09-24 — Nous model IDs are provider-specific

After PR #597, fresh main run
[35959596211](https://github.com/magnus919/agent-skills/actions/runs/35959596211)
selected 11 `system-one` cases. Both generation sides failed for every case:
22 infrastructure-error sides and 158 skipped assertion rows, all with HTTP
400. The paired job now failed as intended. The audit reported 0 prose
assertions, 0 groups selected, 0 assertions selected, and 0 Jev provider
errors; therefore it made no Jev calls. The green PR checks only established
that code and fake-eval validation worked; they did not establish a successful
Nous inference path.

Read-only inspection found the repository `EVAL_MODEL` variable set to
`stepfun/step-3.7-flash:free`. The current Nous-maintained model catalog lists
`stepfun/step-3.7-flash` for the Nous provider without that suffix. The user's
Nous Portal screenshot on 2026-09-24 lists StepFun Step 3.7 Flash among the
models currently marked free, alongside Upstage Solar Pro 4, Meituan LongCat
2.0, Poolside Laguna S 2.1, InclusionAI Ling 3.0 Flash Fin, InclusionAI Ling
3.0 Flash Sante (free), Poolside Laguna XS 2.1, and Space Bunny Alpha. This
corrects the earlier hypothesis that the free offering may have disappeared:
the leading explanation for HTTP 400 is now the stale `:free` suffix, though
the exact request has not yet been validated against Nous's authenticated live
catalog. Removing the non-standard thinking extension did not change the
outcome. The generation response's recorded model label was also the generic
string `configured-model`, which obscures the exact model in artifacts; future
comparisons should preserve the provider's actual model ID.

The historical failed outputs remain in Actions artifacts only as error
metadata; no response text exists to score or replay. Blog lesson:
provider-compatible API shape does not imply interchangeable model IDs or
pricing semantics—validate the exact configured ID against that provider's
catalog before inference, and retain exact model provenance.

PR [#598](https://github.com/magnus919/agent-skills/pull/598) merged the
authenticated model-catalog preflight, exact model provenance, fail-fast
generation, and safe structured HTTP error context. The repository variable
is now `stepfun/step-3.7-flash`, matching the Nous catalog and the user's
Portal listing. Post-merge run
[35961147079](https://github.com/magnus919/agent-skills/actions/runs/35961147079)
confirmed the exact ID against the authenticated catalog. No changed skill
evals were selected (0/0), so Nous generation made zero calls. The advisory
Jev report recorded 0 expected reports, 0 observed reports, and 0 calls. This
confirms catalog availability only; it is not a model-response or Jev result.

The manual smoke path previously selected the fixed `agent-skills` manifest
but did not write frozen expected-case evidence, and the Jev audit only ran on
push events. A follow-up wires that existing bounded main-branch smoke to
write the same case-ID denominator as normal selection and invoke the advisory
Jev audit after its model artifact is uploaded. This lets the next smoke
measure actual generations and Jev judgments together without replaying the
failed HTTP-error artifacts. The Portal currently marks StepFun free, but the
free designation is not a quality claim or a reason to relax any evaluation
boundary.

## 2026-09-24 — Transport success is not a usable completion

After PR #601, bounded main-branch run
[35962104493](https://github.com/magnus919/agent-skills/actions/runs/35962104493)
used the authenticated Nous catalog ID `stepfun/step-3.7-flash` and selected
all 6 cases in the fixed `agent-skills` smoke manifest. All 12 candidate and
baseline requests were recorded as completed with no infrastructure errors,
but only 6 of 12 contained non-empty assistant text. Five baseline outputs
had exactly 4096 output tokens and empty text; a candidate output was also
empty despite reporting 76 output tokens. The exact provider finish reason
was not retained, so reaching the configured token limit is a plausible
explanation, not a confirmed cause.

Jev saw all 6 expected case reports and no provider errors, but could form a
complete candidate/baseline pair for only `third-party-vetting`. It judged 10
of 60 prose assertions; 30 were skipped because responses were empty and 20
because the remaining responses were unpaired. Its 10 suggestions were 4
`met` and 6 `not_shown`, with met probabilities from 0.00 to 1.00 and provider
confidence from 0.38 to 1.00. There are no human labels for this sample, so
these numbers are neither correctness nor calibration evidence.

The model job's green status therefore overstated usable generation: the
adapter currently treats an empty assistant content field as `completed`,
while the Jev audit correctly skips it and exposes the lost denominator. Blog
lesson: a successful HTTP response and token usage do not prove a usable model
answer. Preserve safe finish-reason metadata, classify empty content as a
generation failure, and stop before spending calls on further pairs; keep
transport, completion, and semantic-judgment coverage as separate counts.

The follow-up now implements that boundary in the adapter: blank content and
known non-final completion reasons (`length`, `content_filter`, `tool_calls`,
and `function_call`) become infrastructure errors, and partial response text is
not copied into the comparison artifact. The normalized finish reason and token
counts remain available as safe diagnostics; the run-manifest schema accepts an
optional `outputs.finish_reason` so older v1 artifacts remain valid. The
OpenAI-compatible API reference defines `length` as reaching the requested
token maximum and `content_filter` as content omitted by filtering; other
providers may have their own reason vocabulary ([API reference](https://platform.openai.com/docs/api-reference/chat)).

Mocked adapter and paired-run tests now cover blank/whitespace answers,
token-limited and filtered completions, unsafe provider reason strings, and the
resulting `infra_error` report with no partial text. These tests establish the
local failure contract only. They do not establish how Nous StepFun behaves on
the next live run; the bounded manual smoke must confirm that a blank or
truncated response fails the model job and that Jev receives no unusable
response. The registered model fixture now uses the live ID
`stepfun/step-3.7-flash` (without the obsolete `:free` suffix).

The next bounded main run
[35964665427](https://github.com/magnus919/agent-skills/actions/runs/35964665427)
confirmed the guard against live Nous StepFun. Model catalog preflight passed
and all 6 smoke cases were selected. In the first case,
`skill-creation-structure`, the candidate completed; the baseline returned empty
assistant content with `finish_reason=length` at 4096 output tokens. Its
manifest contains `status=error`, the safe finish reason and usage counts, and
no response text. The paired job stopped after these 2 requests, leaving the
other 10 of 12 planned requests unspent and all 5 remaining cases unattempted.
This confirms token-limit termination as the observed cause for that baseline
failure, not a key or catalog mismatch.

The audit observed 1 expected report, 0 complete candidate/baseline groups,
and selected 0 assertions; 5 candidate prose assertions were unpaired, 5
baseline assertions were skipped as infrastructure errors, and Jev provider
errors were 0. The audit exited nonzero because generation was incomplete; it
made no Jev calls. That is an incomplete evaluation, not a Jev API failure.

The run also exposed a separate reporting flaw: despite the missing baseline,
comparison report v1 labeled the completed candidate side
`candidate_improvement`. The model job failed, but the case-level label still
implied evidence that did not exist. The follow-up introduces version 2 of the
comparison-report contract, with `insufficient_data` whenever either arm has
an infrastructure error; the v1 schema remains unchanged. Lesson: the paired
delta itself must fail closed, not merely the enclosing workflow.

## 2026-09-24 — Screen Nous free models for Droid tool compatibility

The failed GPT-6 Luna experiment in [PR #544](https://github.com/magnus919/agent-skills/pull/544)
showed that Nous Portal's Responses route rejected Droid's custom-tool request.
The subsequent [PR #605](https://github.com/magnus919/agent-skills/pull/605)
therefore tested OpenAI Chat Completions function calling against model IDs
from the user's current free-model list. The prompt was fixed and contained no
repository data; each probe allowed 96 output tokens and asked for one
`probe({"ok":true})` call.

The authenticated Nous catalog returned multiple IDs for several display
models, with and without a `:free` suffix. The bounded screen on
[run 35968966758](https://github.com/magnus919/agent-skills/actions/runs/35968966758)
matched 12 IDs. Ten returned a `tool_calls` response whose function arguments
were valid JSON; StepFun's unsuffixed ID returned an XML-like `<tool_call>`
string inside `function.arguments`, and its `:free` alias returned HTTP 400.
The model-name filter did not match an Upstage Solar Pro 4 ID, so Solar Pro 4
was not part of this screen. These are protocol observations, not quality
scores or comparative review results.

The selected model is `poolside/laguna-s-2.1:free`: its exact free ID returned
standard JSON function arguments in the screen, and the follow-up
[run 35969275064](https://github.com/magnus919/agent-skills/actions/runs/35969275064)
repeated that exact probe successfully. Nous reported the model ID exactly
and recorded cost as 0 for the 164-token request. Poolside describes Laguna S
2.1 as an agentic coding model with 118B parameters; that makes it a relevant
candidate for code review, but says nothing about its review accuracy. The
Droid workflows now use Factory's `generic-chat-completion-api` provider for
Nous Chat Completions. Factory's custom-model docs say reasoning-effort flags
do not apply to custom models, so the prior GPT-specific `low` override is
omitted.

The pre-merge Factory action skipped because its workflow file differs from
the default-branch copy; that safeguard is expected and is not a successful
review. After PR #605 merged as
[commit `fc7c941`](https://github.com/magnus919/agent-skills/commit/fc7c941cfce5ede8dc2381984e81390009ee3d21),
rerun [35969726932](https://github.com/magnus919/agent-skills/actions/runs/35969726932)
passed the exact-model Nous function-call probe again, but the Factory action
could not check out the already-merged PR branch (`Failed to checkout PR #605
branch for review`). Thus the provider configuration and basic function-call
protocol were verified, but that rerun did not establish review behavior.

The open-PR test on [PR #606](https://github.com/magnus919/agent-skills/pull/606)
then completed in 6m20s in
[run 35970281646](https://github.com/magnus919/agent-skills/actions/runs/35970281646).
The exact Nous model probe passed, Droid reported success with empty prepare,
review, and validator error fields and no fallback note, and Factory posted a
review plus its security-review-ran badge. The generated review said “LGTM”
and posted 0 inline comments on this documentation-only diff. This verifies
that the automatic review path can execute with the configured Nous custom
model; it does not validate review accuracy, security-detection quality, or
performance on code changes. The separate interactive comment-triggered path
remains untested. The repository validator and paired-eval checks passed.
Blog lesson: an OpenAI-compatible base URL does not guarantee that every
routed model serializes tool arguments compatibly; inspect the actual response
shape, preserve the provider model ID, and distinguish a successful API
response from a usable tool call and from a successful agent task.

## 2026-09-24 — Make free-model smoke comparisons reproducible

The corrected default model ID, `stepfun/step-3.7-flash`, was already merged
with PR #598; the later live paired smoke established that the catalog entry
exists but a baseline completion hit the configured 4,096-token ceiling with
`finish_reason=length`. The user's current Portal screenshot still lists
StepFun Step 3.7 Flash among free offerings. A model's presence in the catalog
or successful short function-call probe is not evidence that it can complete
the longer paired-evaluation prompts.

Added a main-only manual workflow override for an exact Nous `model_id` and a
bounded per-response `max_output_tokens` choice (4,096, 8,192, or 12,288).
Manual runs default to the corrected StepFun ID and 8,192 tokens, but can screen
other catalog IDs such as Poolside Laguna S 2.1 without changing the repository
default. The existing authenticated exact-ID catalog check remains mandatory;
the fixed `agent-skills/evals/evals.json` screen and subsequent advisory Jev
audit remain unchanged. The chosen ID and token ceiling appear in the run
summary and each paired artifact retains the exact configured model. Normal
main pushes continue to use the repository model variable and 4,096-token
ceiling until a candidate has completed a live smoke. A runtime allowlist also
rejects unsupported token budgets passed directly through the workflow API.

Adding the candidate-screen behavior to the `system-one` eval manifest raised
its full candidate-plus-baseline assertion count from 158 to 164. The existing
160-assertion Jev audit cap would have omitted four assertions; the focused test
caught that mismatch before merge. Updated the CLI default, workflow cap, test,
and operator runbook together to 164 while retaining the 22-call maximum.

Focused paired runner, release runner, selection, Jev audit, calibration,
eval-contract tests all pass; all 181 eval manifests validate, and the schema
coverage ratchet remains at 181/181. This is local evidence only. No candidate
generation or Jev audit has yet been run with the new override, so it does not
establish that StepFun at 8,192 tokens or any alternative can complete the
paired workload. After merge, run fixed-manifest smokes at the same token
budget for each candidate, inspect non-empty completions, finish reasons,
selected-case counts and Jev omissions, then decide whether the persistent
model variable should change. Do not treat the Jev suggestions as independent
model-quality labels or a release gate.

Blog lesson: keep an exact provider model ID and its output budget attached to
every experiment. A successful catalog probe and a successful tiny tool call
answer different questions from “did this model produce usable output on the
real workload?”; a bounded fixed-manifest comparison makes that distinction
reproducible without silently changing the deployed default.

## 2026-09-24 — Choose a model from the real CI workload

PR [#607](https://github.com/magnus919/agent-skills/pull/607) merged as
[`678e277`](https://github.com/magnus919/agent-skills/commit/678e27721bf0220fe10511417eb99b2dfb6cde34).
Its automatic main run used the then-configured `stepfun/step-3.7-flash` at
4,096 output tokens. On the 11-case `system-one` selection, the candidate
response completed but its paired baseline ended at the token limit with
`finish_reason=length`. Only 1 of 11 reports arrived; Jev selected zero groups
and made zero calls, with zero Jev-provider errors. This is incomplete model
generation, not a Jev outage.

The fixed six-case `agent-skills` smoke then tested StepFun at the manual
8,192-token ceiling in
[run 35975430295](https://github.com/magnus919/agent-skills/actions/runs/35975430295).
Two of six reports arrived; one side of the second case reached 8,192 tokens
and ended with `finish_reason=length`. Jev saw two reports, selected two groups
and ten assertions, skipped five infrastructure-error and five unpaired
assertions, and recorded zero provider errors. The audit correctly remained
incomplete. Raising StepFun's output ceiling again was not selected as the
default fix.

Poolside Laguna S 2.1 was screened at the same fixed manifest and the normal
4,096-token CI ceiling. The initial 8,192-token run
[35975844954](https://github.com/magnus919/agent-skills/actions/runs/35975844954)
and confirmation at 4,096 tokens
[35976488745](https://github.com/magnus919/agent-skills/actions/runs/35976488745)
both produced all 12 candidate/baseline completions with normal `stop` finish
reasons, all six expected comparison reports, and no missing or unexpected
reports. At 4,096, the largest observed completion used 2,571 output tokens.
Both Jev artifacts reported 12 groups and all 60 selected prose assertions,
with zero budget omissions, skipped assertions, generation errors, or Jev
provider errors. Every comparison's deterministic assertion delta was
`both_pass`.

These are bounded operational compatibility observations for the fixed smoke,
not a representative model-quality benchmark or semantic-accuracy score.
Jev remains advisory; a complete Jev artifact proves coverage, not that its
suggested semantic labels are correct. After the two successful matched runs,
the repository's `EVAL_MODEL` variable was changed from
`stepfun/step-3.7-flash` to `poolside/laguna-s-2.1:free` and read back. The
manual workflow input default is aligned to the same exact model ID in the
follow-up PR; the normal 4,096-token limit is retained.

Blog lesson: select the deployed model against the actual request path and
budget, not from its display name, catalog presence, or a short tool-call
probe. Keep failed/truncated generations as infrastructure evidence, compare
the full selected-case denominator, and separate operational completion from
semantic quality and calibration.

## 2026-09-24 — Recheck the merged default and preserve a rate-limit failure

PR [#608](https://github.com/magnus919/agent-skills/pull/608) merged as
[`4087c91`](https://github.com/magnus919/agent-skills/commit/4087c91bd94137204dcefaadb74edfc86691b37d).
Its automatic main push passed paired-eval tests and the fake-adapter smoke,
but selected no skill manifests. The workflow therefore performed no live
generation on that push; a green post-merge workflow alone was not sufficient
to verify the model path.

The follow-up manual run
[35978853974](https://github.com/magnus919/agent-skills/actions/runs/35978853974)
left `model_id` unspecified, exercising the merged
`poolside/laguna-s-2.1:free` workflow default, and used the normal 4,096-token
ceiling. Unit tests and authenticated model-catalog preflight passed. The
fixed six-case manifest selected all six cases, but generation stopped after
one paired report: one side completed in 63.8 seconds with 918 output tokens;
the other received HTTP 429 `Too Many Requests` from Poolside. The old adapter
did not retain response retry headers. Comparison v2 correctly reported
`insufficient_data`; Jev saw one report, selected zero groups and assertions,
made zero calls, and recorded zero Jev-provider errors. The Jev job failed
closed because the selected evaluation was incomplete. This is provider rate
limiting, not a Jev failure or a semantic model-quality result.

This run qualifies the earlier two complete Poolside smokes: the model can
complete the fixed workload at 4,096 tokens, but free-endpoint availability is
intermittent. Keep the exact configured model for now because the evidence does
not establish a better tested alternative; do not hide 429s with model
fallback or count partial outputs. A local follow-up adds exactly one retry
for HTTP 429, honors a numeric or HTTP-date `Retry-After` up to 60 seconds,
uses a one-second fallback only when the header is absent or invalid, and
records a deferred retry when the provider asks for a longer wait. Other HTTP
errors remain single-attempt. The focused retry test functions were added, but
a later audit found they were not called by the test file's script-style
`__main__` runner, which is how CI executes that file. Their presence was
mistaken for CI coverage. A retry that still receives 429 must remain an
explicit incomplete run.

The same PR's Factory Droid review
[run 35977488831](https://github.com/magnus919/agent-skills/actions/runs/35977488831)
eventually completed successfully after about 12 minutes, with a successful
Nous function-call preflight and zero inline review comments. This verifies
that the open-ended review route ran for this small configuration/documentation
diff; it does not measure review accuracy or security-detection quality.

The current full workflow audit still finds no drop-in Jev replacement for
existing generated artifacts: `skill-eval` requires full candidate/baseline
answers, and Droid requires full code/security review. Jev's typed judgments
fit the post-generation semantic-audit boundary instead. The failure-to-issue
workflow has no model call to replace; advisory failure-lane triage remains a
separate, unvalidated addition. The Nous teacher workflow must stay separate
from Jev because its role is to provide a non-Jev pseudo-label comparison; the
local teacher can be the response-generating model and is diagnostic only.

Blog lesson: a successful provider preflight does not promise service
capacity, and a green validation run may not exercise an inference path at all.
Check the selected-case denominator, separate the model endpoint's 429 from
Jev's provider health, and keep a bounded retry observable without converting
an incomplete evaluation into a pass.

## 2026-09-24 — Verify the merged retry path and make retries observable

PR [#609](https://github.com/magnus919/agent-skills/pull/609) merged as
[`aa1d93c`](https://github.com/magnus919/agent-skills/commit/aa1d93c3d595bfcabd7ad5c47b187b48eaa9c76f).
The post-merge bounded run
[35982396921](https://github.com/magnus919/agent-skills/actions/runs/35982396921)
completed on the Poolside `:free` model: all 6 selected cases produced 6/6
comparison reports, all 12 candidate/baseline outputs completed, and Jev
selected all 12 groups and 60 prose assertions with zero skipped assertions,
generation errors, budget omissions, or Jev provider errors. All reports had
`paired_delta=both_pass` and normal `stop` finish reasons. This verifies a
complete operational path on the fixed smoke, not Jev label accuracy or
semantic model quality.

The same run overlapped the long-running Factory Droid review
[35980792942](https://github.com/magnus919/agent-skills/actions/runs/35980792942),
which used the same free Nous endpoint. Treat that concurrency as a capacity
confound. More importantly, manifests contained no retry count, so the
successful run cannot establish whether the new retry was used; the slowest
completion time is not evidence of a retry.

The follow-up adds `outputs.rate_limit_retries` to the run manifest when the
OpenAI-compatible adapter can report it. Zero means no retry was attempted;
one means the single bounded retry was issued, whether it completed or failed.
It remains optional in the v1 schema so existing artifacts validate
unchanged. Tests now cover the normal path, retry success, a second 429,
deferred long waits, persisted counts, and legacy-manifest compatibility. They
are explicitly called by the script-style test entrypoint used in CI. A new
post-merge manual smoke is still required to inspect retry counts on real
responses; until then, unit coverage is not live retry evidence.

Blog lesson: behavior without telemetry is not operational evidence. Test
functions must be wired into the command CI actually executes, and a successful
job must retain enough privacy-safe metadata to distinguish first-attempt
success from retry success without storing raw responses.

## 2026-09-24 — Verify retry telemetry on a live Nous smoke

PR [#610](https://github.com/magnus919/agent-skills/pull/610) merged as
[`60d44b9`](https://github.com/magnus919/agent-skills/commit/60d44b9fe57a50d946ede518ce5d546368dd4aa3).
Its merge-triggered push workflow
[35989562000](https://github.com/magnus919/agent-skills/actions/runs/35989562000)
passed tests, but selected no changed skill manifests, so real-model generation
was skipped. A green push workflow alone was not live retry evidence.

The manual main-branch smoke
[35989698935](https://github.com/magnus919/agent-skills/actions/runs/35989698935)
used `poolside/laguna-s-2.1:free` (the model ID shown as free in Nous Portal)
with an 8,192-token response ceiling. Endpoint preflight and tests passed;
real-model generation completed in 3m42s. All six selected cases produced six
comparison reports, and all 12 candidate/baseline outputs completed with
`finish_reason=stop`, no recorded failures, and
`outputs.rate_limit_retries=0`. All six paired reports were `both_pass`.
This verifies that the new counter is persisted as zero on normal first-attempt
responses. No 429 occurred, so this live run does **not** verify successful
recovery from a real rate limit; the retry-success and second-429 behavior
remain covered by deterministic tests only.

Jev 1.13's advisory audit observed exactly the six expected reports, selected
all 12 groups and 60 prose assertions, and had no skipped assertions,
generation errors, budget omissions, or Jev-provider errors. Its suggested
labels were 13 `met`, 3 `not_met`, and 44 `not_shown`. Provider-confidence
values ranged from 0.25 to 1.00; without independently adjudicated labels this
is not calibration evidence. The Jev audit remains advisory and these counts
do not establish semantic accuracy.

Blog lessons: inspect the selected-manifest denominator and actual step outcome
before calling CI a model run; successful completions with a zero retry counter
are evidence of first-attempt success, not retry recovery; and complete Jev
coverage is still distinct from correctness or calibration.

## 2026-09-24 — Admit complete manual smokes to blind calibration

The successful main-branch smoke [35989698935](https://github.com/magnus919/agent-skills/actions/runs/35989698935)
has both `paired-eval-model-artifacts` and `jev-eval-audit` artifacts, and its
six-case selection is complete. The independent Nous teacher workflow rejected
this run only because its source guard allowed `push` and not
`workflow_dispatch`. That made the best fixed-manifest operational comparison
unavailable for the existing blind calibration protocol.

The source contract now permits only successful `skill-eval.yml` runs on
`main` from `push` or `workflow_dispatch`, checks that the GitHub API response
matches the requested run ID, and has focused tests for valid and rejected
metadata. Artifact download and the existing calibration `prepare` validation
still must succeed before the teacher receives any generated responses. The
synthetic provider probe now runs after that artifact validation, avoiding a
paid inference call for an empty or malformed source run. The teacher remains
a distinct Nous pseudo-labeler; its agreement is not human ground truth.

Manual fixed-manifest smokes now default to 4,096 output tokens, matching the
normal main-branch paired-eval budget. This makes the next controlled smoke
directly comparable to the production CI request path; larger ceilings remain
explicit experiments. After this change is merged, run the default Poolside
smoke at 4,096, then pass that run ID to the blind teacher workflow with a
frozen seed. Compare population and challenge strata separately and retain
manual review for disagreement; do not derive an accuracy threshold from
teacher pseudo-labels.

Open/closed issue searches for the exact "CI failure on main" phrase returned
no incident examples. The `area/ci-cd` results surfaced model-routing and
evaluator proposals, not adjudicated failure labels. Therefore the separate
Jev CI-failure triage idea remains uncalibrated and is not being added to issue
creation.

Blog lessons: a run may be complete yet unusable by a downstream calibration
workflow because the source-event contract is too narrow; validate provenance
and artifact coverage separately. Keep the smoke budget aligned with the
normal CI path, and do not mistake model-teacher agreement for verified truth.

## 2026-09-24 — Size blind calibration to the evidence that exists

After PR #612 merged, the automatic main run
[36001349998](https://github.com/magnus919/agent-skills/actions/runs/36001349998)
selected all 11 System One cases, but generated only nine comparison reports.
The Jev artifact reported two missing reports (`jev-ci-operations` and
`reranking-pipeline`), 96 of 109 prose assertions selected, and an incomplete
audit. The `deadline-bound-stream` baseline ended with
`finish_reason=length` and empty assistant content at the 4,096-token ceiling.
The model job still uploaded its artifacts; a failed/incomplete run is not
eligible for teacher calibration.

The first teacher-workflow attempt
[36003602688](https://github.com/magnus919/agent-skills/actions/runs/36003602688)
validated the completed manual source and Nous model, then stopped during
prediction-blind packet preparation before probing the API or using
`NOUS_API_KEY`. The complete six-case source has 60 assertions, but the
calibration helper required 16 population pairs plus 12 remaining high-met
challenge items. The requested challenge sample exceeded what remained after
population sampling. This was a sample-size contract error, not model
disagreement or an inference failure. The source smoke used Poolside Laguna S
2.1 at 8,192 tokens, so it is not a substitute for the newly aligned 4,096-token
manual smoke when comparing against the normal CI budget.

The sampler now caps requested strata at the available population and
challenge counts, records requested/available/selected sizes, and retains the
selected-case completeness gate. A preparation-only local replay of run
`35989698935`, using seed `poolside-8192-local-check`, produced 16 of 30
requested population pairs and 8 of 12 requested challenge items (40 review
items total). This verifies only that a private packet can be prepared; it
produced no teacher labels and made no inference call. A reduced or empty
challenge stratum must remain visible in the summary; do not present it as a
risk-stratified population estimate. After this fix is merged, run a fresh
fixed-manifest Poolside smoke at 4,096 tokens and use only its complete model
and Jev artifacts for the teacher screen.

Blog lessons: distinguish source provenance, artifact completeness, sample
feasibility, and inference success as separate gates. Small complete datasets
should yield an honestly smaller sample, not fail on arbitrary defaults or
silently claim the requested challenge denominator. An incomplete run should
be diagnosed from its generation and audit artifacts, not “fixed” by treating
missing cases as negative examples.

## 2026-09-24 — Separate Jev input tuning from response generation

After PR #613, the automatic main run
[36008593676](https://github.com/magnus919/agent-skills/actions/runs/36008593676)
selected 11 System One eval cases but produced only four comparison reports;
seven expected case IDs were missing. The Laya C++ serving baseline received
HTTP 429 after the bounded retry, while its candidate completed. The Jev job
reported an incomplete audit and did not turn the missing cases into passes.
This is a Poolside availability failure in generation, not a Jev provider
failure.

The fixed-manifest manual smoke
[36008669961](https://github.com/magnus919/agent-skills/actions/runs/36008669961)
completed all six expected reports with the default
`poolside/laguna-s-2.1:free` model at 4,096 output tokens. All 12 response
manifests completed with `finish_reason=stop`, no failures, and two rate-limit
retries total. Jev saw six of six reports and judged 60 of 60 assertions, with
no skips, budget omissions, generation errors, or Jev provider errors. Its
suggestions were 11 `met`, three `not_met`, and 46 `not_shown`; mean `met`
probability was 0.1795, and mean provider confidence was 0.843 (ranges 0.00–1.00
and 0.29–1.00 respectively). These scores have no independent correctness
labels and are not calibration evidence.

Two blind passes from the same Nous `openai/gpt-6-luna` model were run against
that same frozen source in workflow run
[36011105432](https://github.com/magnus919/agent-skills/actions/runs/36011105432).
The recreated packet matched the workflow's `blind_items_sha256`
`de5bce626eac47e5557dcca947f6fd0412ab932a469204f97d7878dc21cd6d12`. The
sample contained 32 population judgments (30 resolved, two uncertain) and four
available challenge judgments (three resolved, one uncertain). Overall, 33 of
36 labels had two-pass consensus: seven `met`, three `not_met`, 23 `not_shown`,
and three `uncertain`. This is same-model pseudo-label self-consistency, not
independent truth or model agreement with Jev.

There were five resolved Jev/teacher-label disagreements across four case
sides: Jev said `not_shown` while the teacher said `not_met` for both sides of
`evals-manifest-authoring`; Jev said `met` (probability 0.57, provider
confidence 0.36) while the teacher said `not_shown` for candidate
`skill-review-compliance`; on the `client-discovery-loading` challenge, Jev
said `met` (0.78 / 0.68) while the teacher said `not_met`; and on candidate
`third-party-vetting`, Jev said `met` (0.79 / 0.68) while the teacher said
`not_shown`. These are adjudication candidates, not proven Jev false accepts
or teacher false negatives. A local evidence screen found plausible omissions
in the review/vetting answers and an actual conflicting instruction in the
discovery answer, reinforcing the need for an independent label before
assigning fault.

The bounded follow-up adds an opt-in, main-only manual replay workflow with a
successful-source-run check, untrusted-artifact handling, an explicit
per-run TypeSafe egress acknowledgement that defaults off, a complete
selected-report identity requirement, and the existing 22-call cap. A new
`all-requirements-shadow-v1` variant tests item-by-item list coverage and
contradiction handling; the normal CI audit remains on `deployed` and does not
change its decision path. The three evidence-driven eval splits reduce
compound list assertions to independently reviewable claims, which raises the
complete System One candidate-plus-baseline maximum from 164 to 168. The
bounded CI cap and runbook were adjusted to that exact manifest size. The
teacher workflow summary now says “consensus resolved” rather than calling
resolved pseudo-label count “agreement.”

No generated response was replayed to Jev under a shadow variant while the
separate egress approval is pending. No raw model response or teacher rationale
was added to this runlog.

Model-ID clarification: the Portal screenshot lists StepFun Step 3.7 Flash as
free, but the provider ID is the bare `stepfun/step-3.7-flash`. PR #598 already
changed the repository variable to that ID and the authenticated catalog
preflight passed in run
[35961147079](https://github.com/magnus919/agent-skills/actions/runs/35961147079).
The current main workflow default was later changed to Poolside following the
matched StepFun generation tests, which produced empty/truncated responses at
the normal token ceiling. No active configuration uses a StepFun `:free`
suffix; its only remaining code occurrence is a deliberate negative fixture
that proves the stale alias is rejected. Free catalog status does not prove
usable generation or semantic quality.

## 2026-09-24 — Recheck which CI inference Jev can replace

I re-audited the workflows in the `codex/jev-audit-replay` PR snapshot against
TypeSafe's current [System One introduction](https://docs.typesafe.ai/introduction),
[API reference](https://docs.typesafe.ai/api), and [model reference](https://docs.typesafe.ai/models).
The documented contract is a `state` plus named Choice, Score, and Noul
questions returning typed answers and probabilities. The questions are
evaluated independently in parallel. It does not return the generated prose
or code needed by the repository's response-generation or code-review tasks.
These are capability boundaries from the provider contract, not evidence that
any individual decision will be correct or calibrated.

| CI surface | Inference or decision today | Jev fit / disposition |
|---|---|---|
| `.github/workflows/skill-eval.yml` model job | Nous-backed model generates candidate and baseline skill responses | Not replaceable: generating the responses is the workload under test. The subsequent Jev audit is the decision-shaped semantic-review addition; it remains advisory. |
| `.github/workflows/droid-review.yml` and `droid.yml` | Factory Droid uses a chat model for open-ended code/security review or requested responses | Not a drop-in replacement: Jev cannot write findings, explanations, or code. A future bounded classifier over independently produced findings would be a separate experiment, not a substitute for review. |
| `.github/workflows/jev-teacher-calibration.yml` and `jev-local-teacher-calibration.yml` | A separate hosted or local language model labels blinded real-output samples | Do not replace the teacher with Jev: comparing Jev with its own judgments is circular. These are model-teacher pseudo-label diagnostics, not accuracy ground truth; human adjudication remains the stronger evidence. |
| `.github/workflows/ci-failure-to-issue.yml` | Deterministic issue creation from failed-workflow metadata | No inference to replace. Jev-based failure routing remains only a candidate: the existing 22-case pilot is synthetic, and the repository has no representative labeled CI-failure set. Do not add a live egress call or alter issue priority from that evidence. |
| `.github/workflows/skillevaluator.yml` | Selected Tier 1 checks are keyless and deterministic | No LLM inference to replace. Preserve exact checks. |
| `.github/workflows/jev-qa-pilot.yml` | Manually dispatched Jev calls on synthetic triage, test-priority, and evidence cases | Already exercises Jev directly; it is a capability pilot, not a replacement for an existing CI model call or a production-calibrated gate. |

Decision: there is no currently identified LLM inference job whose required
output shape is a bounded decision and whose work can safely be replaced
outright by Jev. The existing post-generation audit is the well-matched use:
deterministic code retains exact checks and selection/coverage authority, while
Jev supplies advisory judgments for semantic assertions. Failure triage could
be reconsidered only after a representative, independently labeled set and a
privacy-safe extraction contract exist; any first deployment should annotate
or route for a human, never change the failed workflow result or auto-assign
issue severity. This audit changed no workflow behavior, release rule, or data
egress scope.

Blog lesson: choose replacements by the output contract, not by the fact that
both systems are called “models.” Jev can replace a probabilistic judgment
coerced from generated text when the software needs a typed decision; it cannot
replace a job whose deliverable is the generated text itself. A separate
teacher model can help find disagreement, but swapping in the tested model
destroys the independence that makes the comparison informative.

## 2026-09-24 — Isolate System One completion limits in a manual smoke

The first automatic main run after PR #614,
[36021921396](https://github.com/magnus919/agent-skills/actions/runs/36021921396)
at `460e30ec9b8fd545d66055cdbf9b78b01fd1aed0`, passed the paired-eval unit
tests and keyless fake-adapter smoke. Nous model-catalog preflight also passed.
The model job selected both `agent-skills` (six cases) and `system-one` (11
cases), for 17 expected case reports. It used the configured Poolside Laguna S
2.1 model with a 4,096-token output ceiling.

Generation wrote 14 of 17 comparison reports before stopping at
`system-one/observed-app-control`: the baseline completion ended with
`finish_reason=length`, used all 4,096 output tokens, and had no usable
assistant content. The adapter classified this as an infrastructure failure;
the paired runner's deliberate first-infrastructure-error stop then left
`deadline-bound-stream`, `jev-ci-operations`, and `reranking-pipeline`
unattempted. A generated response ending at the provider's length limit is not
a semantic failure and must not be passed to Jev as if it were an answer.

The advisory Jev job ran with no provider errors, but correctly failed
completeness: 14 reports seen versus 17 expected, one generation-error side,
five assertions skipped for infrastructure error, 22 groups and 140 assertions
judged, and 20 assertions omitted by the audit budget. The 140 suggestions were
24 `met`, four `not_met`, and 112 `not_shown`; mean met probability was 0.1622
and mean provider confidence was 0.8318. These are opinions on an incomplete,
budget-selected subset, not calibration or correctness evidence. The Jev API
was not the source of this run's failure.

To isolate whether the failure is a response-ceiling issue, the manual
main-only smoke now accepts an explicit allowlisted skill manifest
(`agent-skills` or `system-one`), while retaining `agent-skills` and 4,096
tokens as defaults. The selector rejects any other value before creating
selection evidence. The next diagnostic is a fresh System One-only Poolside
smoke at 8,192 tokens, followed by a denominator and budget review; this is a
targeted experiment, not a change to normal CI limits or release gates. Do not
replay these generated outputs to Jev under a different question variant
without separate per-run egress approval.

Blog lesson: report completion, audit coverage, and API health as separate
dimensions. A provider can return successful typed judgments while the overall
audit remains incomplete because upstream generations were truncated or the
bounded audit budget omitted work.

## 2026-09-24 — The 8,192-token smoke still truncates one baseline

After PR #615 merged at
`2660ec18c127fa7463f4cdaf274d37560a056431`, manual run
[36026794037](https://github.com/magnus919/agent-skills/actions/runs/36026794037)
selected only `system-one` and used Poolside Laguna S 2.1 with an 8,192-token
per-response ceiling. The paired test job and authenticated model preflight
passed. The model job ran for ten minutes and produced nine of 11 expected
case reports before the baseline side of `deadline-bound-stream` hit
`finish_reason=length` at exactly 8,192 output tokens with no usable assistant
content. Its candidate side completed normally. Fail-fast then left
`jev-ci-operations` and `reranking-pipeline` unattempted; the model job uploaded
its metadata artifacts and the advisory Jev job still ran.

Jev saw nine of 11 expected reports, 109 prose assertions, 13 assertions
skipped because of generation infrastructure error, 16 groups selected, and
96 assertions judged. There were zero budget omissions and zero Jev provider
errors. Suggestions were 14 `met`, one `not_met`, and 81 `not_shown`; mean met
probability was 0.1425 and mean provider confidence was 0.8245. These are
advisory judgments on incomplete evidence, not correctness or calibration
results. The audit's incompleteness came from generation truncation and the two
missing reports, not Jev availability or its call/assertion budget.

The manual smoke now also accepts an optional exact case ID, validates that it
exists in the selected manifest, and records only that case in the frozen
selection denominator. Normal push CI and manual smoke defaults still run the
full selected manifest. Next, use this narrower selector for one fresh
`deadline-bound-stream` run at 12,288 tokens. This isolates whether a larger
response ceiling produces usable content without repeating the other 20
candidate/baseline generations. Do not replay the failed or successful output
text to Jev or another model.

Blog lesson: when a complete evaluation is expensive, make the diagnostic
selection explicit and carry the same narrowed denominator into the downstream
audit. A case-level smoke is useful for debugging a generation boundary, but it
cannot stand in for a complete skill-level run or establish semantic quality.

## 2026-09-24 — Compare the failing case without widening the default budget

After PR #616 merged at
`5e7f15818636cefd6a6daa84bfe8450ab27776fa`, three case-isolated runs
distinguished the Jev path from the Poolside generation issue:

| Run | Nous model and ceiling | Generation evidence | Jev evidence |
|---|---|---|---|
| [36029470871](https://github.com/magnus919/agent-skills/actions/runs/36029470871) | Poolside Laguna S 2.1, 12,288 | `deadline-bound-stream` candidate ended normally; baseline used all 12,288 output tokens, returned empty content with `finish_reason=length`, and had one rate-limit retry. | One expected and observed report, but all 13 assertions were skipped as unpaired; zero groups/assertions judged, zero budget omissions, zero Jev provider errors. |
| [36030253874](https://github.com/magnus919/agent-skills/actions/runs/36030253874) | Poolside Laguna S 2.1, 4,096 | `contract-design` candidate and baseline both ended normally at 664 and 678 output tokens, with no retries or generation errors. | One of one reports, eight of eight prose assertions judged in two groups, no skips/omissions/provider errors. Suggestions were two `met` and six `not_shown`; mean met probability 0.315 and mean provider confidence 0.8613. |
| [36030732563](https://github.com/magnus919/agent-skills/actions/runs/36030732563) | Poolside Laguna XS 2.1, 4,096 | Authenticated catalog preflight accepted `poolside/laguna-xs-2.1:free`. The `deadline-bound-stream` candidate ended normally; its baseline again used the entire 4,096-token ceiling and returned empty content with `finish_reason=length`. | One expected and observed report, but all 13 assertions were skipped as unpaired; zero judgments and zero provider errors. |

The one-case selector therefore works end to end: it freezes the selected
case ID, runs only its candidate/baseline pair, and gives the Jev audit the
matching expected-report denominator. On `contract-design`, Jev completed its
bounded advisory review with no API or audit-budget errors. Those eight
suggestions have no independent gold labels; this proves pipeline operation,
not semantic accuracy or calibration.

For the long `deadline-bound-stream` baseline, Laguna S still returned no
usable content at 8,192 and 12,288 tokens; Laguna XS did the same at 4,096.
The earlier 4,096-token mixed run
[36021921396](https://github.com/magnus919/agent-skills/actions/runs/36021921396)
failed on a different System One case, `observed-app-control`, and did not
reach `deadline-bound-stream`. The 12,288-token trial took 4m12s and did not
increase semantic coverage. Do not raise the normal CI token budget, change the
configured model, or infer that a model is better from one successful case.
Keep the 4,096 default and Jev's advisory-only role. At the time, the right
next step was a materially larger manual-only budget; changing the eval prompt
or treating empty output as a semantic answer would have confounded that
diagnostic. No response text was copied into this runlog or replayed.

Blog lesson: an accepted model ID, successful API transport, usable assistant
completion, complete paired report, and completed Jev audit are separate
milestones. Increasing token ceilings can increase latency without increasing
usable evidence; report each stage and its denominator independently.

## 2026-09-24 — Reasoning models need a real output-budget probe

The earlier 4,096/8,192/12,288 manual choices were inherited from the workflow,
not justified as sufficient reasoning budgets. A run that consumes the entire
12,288-token ceiling establishes only that the request was cut off there; it
does not establish the model's limit, that the provider accepted enough room,
or that the model cannot complete the task. Do not describe this as a model
failure without testing a materially larger output ceiling.

Poolside describes Laguna S 2.1 as a reasoning model and advertises a 1M-token
context window. Context length and maximum generated output are distinct
limits, and this does not document Nous Portal's hosted completion cap. The
manual workflow now offers 16,384, 32,768, and 65,536 output-token ceilings
for bounded diagnostics. Its normal 4,096 default and automatic CI path remain
unchanged. The next probe should select only
`system-one/deadline-bound-stream` at 65,536, then record the endpoint's actual
acceptance, completion tokens, finish reason, elapsed time, paired-report
status, and Jev audit coverage. If it still reaches the cap, investigate the
provider's documented/request-reported output limit and a longer bounded
diagnostic before drawing a quality conclusion. Never infer quality from token
consumption alone.

This corrects the earlier premature recommendation to leave the long case as a
known generation limitation after only 4K–12K attempts. The proper conclusion
is still open until a sufficiently roomed run produces a usable response or a
verified provider/runtime bound explains why it cannot.
