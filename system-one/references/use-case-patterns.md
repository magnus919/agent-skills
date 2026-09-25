# Reusable System One application patterns

Use this reference when moving beyond a single classifier into app control,
real-time decisions, ranking, permissions, moderation, or agent orchestration.
The examples below were inspected as design evidence on 2026-09-22; their
published accuracy, latency, and economic results are not independently
reproduced here. The [awesome-jev list](https://github.com/yibie/awesome-jev)
is a discovery index, not a security or maturity endorsement.
For the cross-category survey of 1,305 Jev index records, including source
coverage and counterexamples, read `field-patterns-and-antipatterns.md`.

## Find the right decision

The 2026-09-19 AY Automate use-case survey groups Jev examples into routing,
guardrails, reranking, scoring, bulk classification, semantic linting, and
live control. The portable lesson is to look for a **frequent, bounded
judgment** inside a larger workflow. Before selecting a model, write down:

1. The actual state available at decision time and one question whose answers
   are fixed in advance. Use Choice for a label, Score for an ordered rubric,
   or Noul for one proposition.
2. The deterministic action for each answer, including `unknown`, malformed,
   low-evidence, and unavailable results. An LLM or person can be a fallback,
   but is not automatically the correct fallback for every risk tier.
3. The cost of a false accept versus a false reject. Set thresholds from
   held-out local evidence per action; article examples are illustrations,
   not deployment defaults.
4. A current exact-rule or production baseline and an independently labeled
   shadow sample. Start with one high-volume decision before replacing a
   whole workflow.

Examples: route a support ticket with Choice plus a separate complexity Score;
decide whether a request needs a stronger LLM with Noul or Score; rate each
retrieved passage for relevance; flag whether a tool call is inconsistent with
the user's request. These return evidence to policy code. They do not write
the support reply, prove a citation, or authorize the tool call.

Prefer ordinary code for exact checks. For citation review, first test whether
a quote literally appears in the cited source; only then ask a bounded
semantic question about whether the surrounding passage supports the claim.
Keep `supported`, `contradicted`, `unrelated`, and `not_shown` distinct so a
missing source does not become a model-certified citation. A provider demo on
planted citation errors is an example of mechanics, not a validated accuracy
estimate for new documents.

## The shared loop

```text
observe authorized state -> construct bounded candidate set -> ask typed questions
-> validate complete response -> deterministic policy -> act / wait / abstain
-> observe actual outcome -> record decision and outcome separately
```

Do not confuse a constrained output *shape* with a correct or authorized
judgment. The executor must not accept model-generated selectors, commands,
coordinates, prices, privileges, or free text as unreviewed authority.
For implementation review, fill `templates/action-control-contract.md`.

## 1. Control an observed application

**When:** browser, desktop menu, drawing canvas, or other interface whose
available actions change with each observation.

1. Snapshot actionable controls and assign temporary IDs tied to that
   observation. Include role, visible label, current value, and permitted
   operations; omit unrelated or sensitive page text.
2. Ask `Choice` for operation and operation-compatible target in the same
   request when independent heads can be speculated. Include `WAIT`, `DONE`,
   `BLOCKED`, and `none` where appropriate. Only the selected operation's
   target head can drive execution.
3. Validate the answer IDs, option set, and probabilities. Recheck that the
   target is still present, enabled, visible, and associated with the same
   page/state fingerprint immediately before execution.
4. Treat generated text as a separate task: copy a verified user-provided span
   verbatim or call a bounded text generator. Never synthesize a URL, selector,
   or shell command from a Choice label.
5. Consume a decision once before mutation. Record the action before the
   post-action observation; a failed observation must not cause a duplicate
   click. Verify `DONE` against the actual goal, not the model's claim.
6. On ambiguity, show candidates or escalate. On stale state, observe and
   re-decide; on repeated no-progress actions, stop at a step/cost budget.

The [Jev Ultrafast model code](https://github.com/browser-use/jev-ultrafast/blob/main/jev_ultrafast/model.py)
builds a dynamic action table and validates selected Choice heads; its
[agent loop](https://github.com/browser-use/jev-ultrafast/blob/main/jev_ultrafast/agent.py)
consumes a decision once and retries on a stale page. The
[voice browser](https://github.com/moritzkremb/jev-voice-browser) adds partial
speech, context, correction, and confirmation. The
[canvas controller](https://github.com/gaborishka/jev-canvas) combines speech
with pointer state; [DWIM](https://github.com/rohit9mehta/dwim) illustrates
desktop menu selection. Confirm the current source and API before reuse.

**Test sequences:** page changes between answer and click; speech recognizer
revises a partial transcript; two targets share a name; an action executes
but observation fails; a `DONE` answer arrives before the goal is met.

## 2. Route, classify, and compose judgments

**When:** ticket queues, candidate screening, alert ownership, document
classes, model/skill routing.

Ask independent `Choice`, `Score`, and `Noul` questions together, then
combine scores, caps, weights, and exclusions in versioned code. Preserve
component answers; a composite score alone is not auditable. Cache by state
identity, model revision, question/rubric version, and policy version so a
policy-only change can be replayed without confusing new inference with new
policy. Make `other` and review lanes explicit. The
[CV screener](https://github.com/gtaras7/typesafe-jev/tree/main/cv-screen)
illustrates this separation; [jev-oncall](https://github.com/mingleiw/jev-oncall)
illustrates multi-signal alert routing. Check the source before adopting
project-specific thresholds.

**Test:** a policy weight changes while cached model answers remain fixed;
unknown categories do not get forced into a known handler; two correlated
questions do not masquerade as independent evidence.

## 3. Rank a bounded shortlist

**When:** search results, code files, evidence passages, recommendations.

Use a deterministic retriever or candidate source first. Batch a `Score` or
`Noul` judgment per candidate, sort in code, and retain original scores for
fusion. Do not claim reranking can recover a relevant item absent from the
shortlist. Measure candidate recall, end-to-end ranking, and latency/cost;
compare lexical, embedding, fusion, and current production baselines. Use
labels independent of the model under test. The
[retrieval study](https://github.com/zhuyansen/jev-search-rerank-eval) found
that a Jev-only rerank was not a universal improvement over embeddings in its
sample, while fusion helped; its label sources and confidence intervals are
part of the result, not a footnote. [jev-assist](https://github.com/glud123/jev-assist)
uses historical file changes to test whether a relevance shortlist covers
files developers actually touched.

## 4. Gate a consequential action

**When:** agent tool permissions, moderation, external sends, deletion,
financial orders, or security review.

Apply exact deterministic prohibitions and authorization checks first. Model
judgment can triage ambiguous semantic cases but cannot grant a permission
the caller does not have. Use `allow / ask / deny` or a comparable explicit
set; define malformed, low-confidence, timeout, and provider-unavailable
behavior for each risk tier. Bind confirmation to the exact pending action,
target, state fingerprint, and expiry. An apparent "undo" is not rollback for
an external send, purchase, trade, or deletion.

[pi-verdict](https://github.com/jesset/pi-verdict) uses deterministic
fast-paths and a three-way judgment. [jev-logtriage](https://github.com/jyatesdotdev/jev-logtriage)
maps answers to triage lanes without executing remediation.
[mastra-jev-moderation](https://github.com/CodeAlive-AI/mastra-jev-moderation)
documents a fail-open circuit breaker; that is one product choice, not a
general safety default. [jev-trader](https://github.com/jarrodwatts/jev-trader)
demonstrates a model preference separated from order placement and exposure
caps; its public dry-run/mock deployment is not proof of live profitability.

**Test:** authorization denial despite a high model probability; malformed
answer; ambiguous timeout after submission; duplicate event; confirmation
for one target applied to a changed target; circuit-breaker state transitions.

## 5. React under a deadline

**When:** block/event streams, games, robotics, live UI, on-call streams.

Specify decision freshness, per-event deadline, one-in-flight or cancellation
policy, and what a late answer means *before* inference. Avoid an automatic
"last known answer" unless that is safe for the domain. Keep the fast safety
or physics control loop deterministic; a slower model may make tactical
choices at a lower rate. Log event ID, state timestamp, decision arrival,
chosen action, actual execution, and later confirmation separately.

[jev-trader's loop](https://github.com/jarrodwatts/jev-trader/blob/main/src/trader.ts)
skips late blocks and confirms orders asynchronously.
[jev-drone](https://github.com/RomanSlack/jev-drone) describes a slower
tactical judgment behind conventional perception and safety reflexes.
[Laya-vs-Jev arena](https://github.com/PromptEngineer48/laya-vs-jev-arena)
shows a shared application contract, but its pacing adapts to the slower
model, so its results are not a standalone model-quality comparison.

## 6. Label, evaluate, and recalibrate

Save frozen states, question text, option order, model revision, raw answer,
human label, later outcome, and policy lane. Split rubric/threshold fitting
from final testing. Report quality by primitive, domain, language, option
count, and harm tier; include selective risk/coverage and a constant or rule
baseline. Keep repeated calls to one prompt distinct from genuinely diverse
cases. [jev-behavior-study](https://github.com/RINNECODER/jev-behavior-study)
tests wording and option-order changes;
[jevcal](https://github.com/abhixhek/jevcal) separates threshold/calibrator
fitting from held-out assessment. See `references/evaluation-and-calibration.md`
for the release gate.

## 7. Classify a large corpus

**When:** tagging archived support messages, agent traces, listings, or notes
with a bounded semantic property that an exact filter misses.

Ask a distinct Noul or Choice question per record, preserve record IDs, and
bound concurrency, retries, rate, cost, and duplicate writes. For example,
"Does this message request a refund?" can feed a tag queue. If aggregate
counts matter, sample and independently label accepted, rejected, and
uncertain records; estimate false accepts and misses before trusting a total.
Keep exact counts in code and distinguish model-produced tags from verified
facts. If these tags feed a forecast or another model, version the feature
definition and test whether it adds value beyond the existing features.

## 8. Lint meaning in CI

**When:** a guideline needs semantic judgment, such as whether an error
message tells a user what to do next.

Express one rubric-backed Noul or Choice question per check and attach the
rule ID, evidence span, and model revision to the result. Run exact syntax,
schema, and policy checks first. Start the semantic check as advisory; promote
it to a blocking gate only after independently labeled real changes establish
false-block, false-pass, abstention, and drift behavior at the proposed
threshold. Missing model evidence must not appear as a passing lint result.

## Porting Jev-shaped code to Laya

The [Laya-vs-Jev arena](https://github.com/PromptEngineer48/laya-vs-jev-arena)
uses the same `{state, questions}` shape behind separate backends. That is
interface compatibility evidence, not equal decision quality or latency.
Before a swap, run the same frozen cases through both; compare option-set
integrity, class errors, calibration, abstention coverage, language slices,
head/context truncation, cold/warm latency, and real action outcomes. Refit
thresholds only on a calibration split and retain independent final tests.
