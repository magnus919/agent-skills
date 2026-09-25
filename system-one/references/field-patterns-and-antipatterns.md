# Field patterns and anti-patterns from Jev builds

Use this as orientation when a proposed System One application looks like a
community demo. It distills a 2026-09-25 review of the AY Automate Jev-builds
index and selected original posts and repositories. The patterns are candidate
designs for Jev, Laya, or another typed decision model; measured behavior and
thresholds do **not** transfer between models. Use `worked-decision-pilot.md`
to turn one candidate into a local evaluation.
For the earlier project-level walkthroughs—browser and voice control, routing,
ranking, action gates, and deadline-bound loops—use `use-case-patterns.md`.
Those examples remain useful design evidence; this reference extracts the
cross-project lessons and counterexamples without repeating their catalogs.

## How to use the survey

The AY Automate index spans 1,305 Jev build entries across browser agents,
routing, judging, games, analysis, trading, and other applications. Treat it as
a discovery map. An index card, original post, README, inspected code path,
controlled reproduction, and field outcome are different evidence levels.
Some source pages require sign-in or omit runnable artifacts. Neither a
catalog score nor social popularity establishes correctness, calibration,
safety, or production use.

## Recurring useful shapes

| Shape | Bounded model job | What code or people retain |
|---|---|---|
| Observed-action selector | Choose among currently valid controls, tools, or game actions. | Build candidates from fresh state; enforce permissions, timing, one-time execution, and postconditions. |
| Router or triage stage | Choose a queue/model/skill or score difficulty from a compact state. | Maintain `other`/no-fit, hard rules, budget, fallback, and outcome labels. |
| Shortlist then judge | Score one retrieved passage, candidate, or document at a time. | Retrieve candidates first; preserve shortlist recall, source provenance, deterministic merge, and user override. |
| Semantic filter before generation | Decide relevance, contradiction, instruction attempt, or evidence sufficiency. | Separate evidence from conflicts; let a generator write only after the filter; verify citations against source text. |
| Bulk tagging | Ask one narrow proposition per record. | Bound concurrency and retries, count in code, sample accepted and rejected tags, and version downstream features. |
| Advisory judge or lint | Apply a written rubric to a PR, test result, error message, or generated claim. | Start advisory; compare with independent labels and exact checks before any blocking gate. |
| Time-bound tactical choice | Select a legal move from structured telemetry. | Keep physics, arithmetic, hard safety reflexes, deadlines, and stale-result rejection deterministic. |

An inspected browser implementation constructs a temporary legal
action table from the observed page, binds choices to a page fingerprint,
consumes each decision once, and records later observations to detect stale
or unchanged state. Its README describes separate verification of the
requested outcome. A separate computer-use README makes dry run, step caps, stall
stops, and emergency stop visible; it reports that overlapping action labels
caused stalls. Candidate options need distinct meanings, and `DONE` still
requires independent verification.

A skill-router README describes a two-stage shortlist over hundreds of
possible skills, explicit no-fit behavior, and comparison with what the
session actually loaded. Its README reports a language-sensitive score gap
without enough evidence for a broad correction. Treat that as a challenge
hypothesis.
This is a useful pattern for large candidate sets: test shortlist recall
before celebrating the second-stage classifier.

## Earlier project examples worth retaining

The earlier `use-case-patterns.md` project review adds several distinct
failure boundaries. These are dated design observations, not newly reproduced
results:

| Project | Lesson to carry into a new pilot |
|---|---|
| `pi-verdict` | Run exact permission and rule fast paths before a semantic `allow / ask / deny` judgment; the model cannot create authority. |
| `jev-assist` | Evaluate a file shortlist against files developers actually changed, not only labels made by the ranking model. |
| `mastra-jev-moderation` | A fail-open circuit breaker is a product-specific policy choice; test unavailable-provider behavior for the actual risk tier. |
| `jev-drone` | Keep perception, physics, and safety reflexes outside a slower tactical decision loop. |
| `Laya-vs-Jev arena` | Sharing a request shape proves interface compatibility, not matching judgment quality or pacing. |

The detailed contract, sequence checks, and source caveats for these examples
remain in `use-case-patterns.md`. Copy the boundary, not a demo's threshold.

## Evidence that changes an adoption decision

- A routing experiment attributed much of its gain to retrieved neighbors;
  removing its Jev difficulty signal changed little. Run a
  **no-decision-model ablation** and compare with the best simple baseline
  before crediting the new stage.
- A memory-relevance cascade improved one reported speed measure while its
  fallback increased cost. Measure the whole cascade, including double-paid
  cases, review, retrieval, and fallback quality.
- An issue-triage report showed that an early favorable subset overstated the
  full sample's advantage. Inspect hard errors, log loss, and slices rather
  than stopping at average accuracy or a convenient prefix.
- A refund-message experiment reported different answers for individual and
  batched requests. It does not establish a general batching defect. Test the
  **exact production request shape**, including batch size, option order,
  state serialization, and concurrent load.
- A failure-attribution benchmark mixed injected failures and several scoring
  axes. Compare only tasks with matching answer spaces and label provenance;
  do not turn one comparable axis into an overall model win.

These are author-reported observations, not expected performance for a new
application. Use them to frame a target-domain experiment.

## Anti-patterns to challenge before release

| Warning sign | Better boundary or test |
|---|---|
| “Its probability is the chance of being right here.” | Test calibration against independently labeled target cases, by class, language, question form, and action lane. Do not use a semantic classifier as a probability calculator for known random processes. |
| “The same fact asked as Noul, Choice, or a negation must agree.” | Pin one direct question form and evaluate it. Jev 1.13 documentation gives counterexamples to complement identities; never reuse a threshold across forms without calibration. |
| “Batching is fast, so the answers will be equivalent.” | Check exact batched and standalone requests on the same frozen cases, as well as question interaction and response validation. |
| “Give it the whole page, trace, or database row.” | Select minimal authorized state; test irrelevant-context, truncation, and adversarial-text cases. Preserve source boundaries. |
| “The model can count, compare dates, interpolate a number from Score, or decide an exact policy.” | Parse, calculate, compare, and authorize in code. Use the model only for a bounded semantic judgment that remains after exact work. |
| “A fast model makes the workflow cheaper.” | Include retrieval, preprocessing, network, retries, review, fallback calls, and final outcome in the measured boundary. |
| “The demo shows live success.” | Distinguish code path, dry run, paper trade, submitted action, confirmed fill, and durable outcome. One trading repository explicitly describes its deployed instance as dry-run/mock despite vivid order-placement copy. |
| “A supervisor/judge can approve itself.” | Keep independent authorization and a separate verifier where needed. Measure what a pre-action check can actually observe; it cannot prevent later regret or downstream failures by assertion alone. |
| “A large or perfect-looking benchmark proves production quality.” | Inspect labels, sample selection, natural versus injected failures, matching answer spaces, uncertainty, held-out slices, and ablations. Preserve `not_shown` and disagreement. |

High-impact examples in the index include hiring screens, fraud flags,
financial trading, and political truth-style meters. A CV-screening rubric
can embed sensitive or disputed factors even when the classifier returns a
well-formed score. A score cannot validate that policy or authorize the
outcome. Keep accountable domain review and exact eligibility outside the
model.

## Read a new example critically

For any promising build, record its **source tier** (index card, original
post, README, inspected code, reproduced run, field outcome), model/version,
decision contract, baseline, labels, denominator, failures, latency/cost
boundary, and deployment mode. Ask which result survives a no-model ablation
and which parts depend on exact rules or a generative fallback. Then write a
small, independent pilot for the target workflow. Stop after the evidence
decides adoption, shadowing, investigation, or rejection; more demos are not
a substitute for that decision.
