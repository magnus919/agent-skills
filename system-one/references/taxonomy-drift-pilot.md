# Pilot: adapt a typed classifier when labels change

Use this as a companion to [comparison design](comparison-design.md), not as
a model leaderboard. The question is whether each approach can recover useful
quality after the **same intentional label change**, and what it costs to
reach that point. A valid enum does not establish a correct decision.

## Pin the old and new contracts

| Taxonomy | Label | Meaning |
| --- | --- | --- |
| Both | `technical` | An application error or malfunction needs investigation. |
| Both | `review` | Evidence is missing or conflicting; no automatic route. |
| v1 only | `billing` | Broad account billing, receipt and payment-related requests, even if underspecified. |
| v2 only | `invoice_copy` | A copy of an existing invoice or receipt is the requested outcome; no disputed payment. |
| v2 only | `payment_issue` | A payment failed, is disputed, or was charged incorrectly. |

The v2 split retires `billing`. There is no safe one-to-one remap; classify
from the input or review. A text that mentions a duplicate charge only to deny
it is not proof of a payment dispute. If testing a wholly new label instead,
version its definition and examples; do not invent gold labels in the v1
contract. Keep action policy fixed: the result is a recommendation and can
never change payment state or send a message. Unknown enums, malformed
responses, and timeouts go to review and remain counted as failures.

## Compare adaptation strategies, not just endpoints

1. **Freeze v1**: capture the rule revision, local checkpoint and training
   manifest, and the pinned Jev revision, prompt and typed request. Measure
   each against v1 references. Replay frozen v1 systems under the v2 guard
   without coercing retired labels into either new class; report route loss
   and invalid outputs as a no-adaptation control.
2. **Give each arm the same v2 semantic specification and labeled adaptation
   allowance.** Keep decision unit, input text and review semantics fixed.
   The rules arm edits logic and tests. The local trained arm adapts the
   existing checkpoint using only the allotted data, recording any schema or
   head changes; checkpoint selection belongs on development data. The Jev
   arm changes its Choice labels and instructions, not provider weights.
   Compare a definitions-only arm separately from few-shot adaptation, if
   testing both. Record what was actually changed, including no-change cases.
3. **Freeze before the test.** Group split by source family, thread,
   near-duplicate template or time cohort. Keep v1 training, v2 adaptation,
   model/prompt selection, calibration, and final test membership separate;
   do not let the same final-test groups enter any arm's corpus or prompt.
   For a real study, have independent reviewers label both contracts and
   adjudicate disagreement before unblinding predictions. Use authorized
   synthetic or public examples only; do not copy an inbox or private
   training artifact into a hosted request or this repository.
4. **Pair decisions on a held-out set.** Report v1 original quality, frozen
   v1 rejected under v2, adapted v2 quality, unchanged-class regression,
   and new-label quality/coverage separately. Include per-label counts,
   confusion, wrong automatic routes, abstentions, invalids and missing
   outputs; do not hide abstention behind accuracy on answered cases.
   Report risk at matched coverage or the actual chosen operating point,
   along with uncertainty across source groups. A validated fallback routing
   a failed response to review does not erase the contract failure.
5. **Charge the whole adaptation.** Predeclare a practical quality floor and
   maximum wrong-route and regression rates. Record elapsed time to the
   frozen candidate, person-minutes for taxonomy/rules/prompt edits and
   adjudication, number of labels, training/compute time, query cost, and
   ongoing latency, review load and serving cost. Count failed iterations.
   Mark unmeasured fields unknown. Distinguish a quick prompt change from
   evidence that it meets the same operating floor.

Use the [benchmark record](../templates/benchmark-record.md) for measurements
and [evaluation and calibration](evaluation-and-calibration.md) for thresholds.
If an arm cannot faithfully represent the contract, report it as incompatible,
not less accurate. Do not test live or paid options without authorization.

## Offline contract example

From the skill root:

```bash
python3 scripts/taxonomy_drift.py
python3 -m pytest -q -o addopts= scripts/test_taxonomy_drift.py
```

The hand-authored fixture separates adaptation, calibration and held-out
source groups. These are public illustrations, not a blind study: the
baseline is hard-coded and only the test split is scored. The fixture uses
adaptation/calibration rows to demonstrate separation, not to fit the rule
or a model. Seven test cases exercise unchanged labels, a retired label,
conflicting cues and a paraphrase. On those seven cases the frozen v1 rule
returns four retired labels under the v2 contract; the adapted rule returns
none, routes five correctly and misses two v2 routes through review. Exact
counts are a smoke test of behavior on this fixture, not transferable quality,
latency or cost. Both local trained and Jev arms are **not run**.

## Evidence and limits

Public primary sources accessed November 20, 2026:

- [Chinmay Goyal, Glean, 5:36:09–5:36:20 in the conference stream](https://www.youtube.com/watch?v=ZZ19zhYnDKY&t=20169s)
  reports that adjusting the Jev prompt helped their changing taxonomy avoid
  repeated fine-tunes. This is practitioner evidence of a useful hypothesis,
  not a controlled drift comparison or proof for an unrelated taxonomy.
- [Diogo Almeida, I Love You So Jevving Much](https://ai.engineer/talks/Cyt3LU8TyNc-i-love-you-so-jevving-much)
  motivates training for machine decisions and discusses reliability (talk
  chapter 5:39 and 9:28). It informs the design, not expected arm performance.
- [TypeSafe product documentation](https://docs.typesafe.ai/introduction)
  documents Jev typed decisions, Choice and optional confidence by question
  type. It establishes the API concept, not drift robustness.

The durable observed artifact is the synthetic fixture and its repeatable
runner. No private email, proprietary labels, deployment metrics, model
predictions or inferred pricing were used.
