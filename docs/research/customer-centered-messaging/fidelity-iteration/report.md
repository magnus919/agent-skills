# Factual-fidelity iteration: findings and delivery

Date: 2026-11-06. Status: bounded experiment completed; drafting checklist retained
with explicit limitations. **Reliable automatic factual correction was not
established.** No self-audit, suggested verdict or structural CI result is promoted
to independent behavioral acceptance.

## What changed

The existing GTM and brand skills now route to a final-copy fact-check reference.
It distinguishes supplied facts, proposals, unknowns and explicit exclusions;
checks actual new headlines, captions, answers and actions; and asks for a compact
new-claim/support/disposition plan before rendering final copy. The message brief
includes that plan and an actual-expression audit. Brand adaptations preserve these
boundaries instead of adding technical properties while polishing tone.

These are authored editorial instructions, not a validated automatic verifier. A
model can produce a convincing audit and still contradict it. Consequential claims
still require source-grounded review; neither a claim-plan table nor this small
experiment removes that need.

Six added eval cases (19 semantic assertions) preserve the important failure modes:
fee contradictions, dated-record overreach, unknown versus absent, invented process
commitments, cross-channel meaning changes and rejected claims leaking into final
copy. Existing case IDs and assertions remain unchanged. Author challenge examples
are in [eval-author-review.md](eval-author-review.md).

## Experiment and budget

Provider: Nous Portal; model: `google/gemini-3.8-flash`, selected by the user. Same
neutral wrapper and task text in each arm, temperature 0, top_p 1, case-specific
seed, max_tokens 6000. No model tools, paid judge, Jev, fallback or automatic retry.
There was one generation per frozen context/task arm, not repeated sampling.

| Spending | Calls | Provider-reported USD |
|---|---:|---:|
| Earlier Qwen and Gemini comparison | 8 | 0.1055236 |
| Phase 1: development, focused rerun, held-out pairs | 10 | 0.238668375 |
| Phase 2: three arms on two additional fresh briefs | 6 | 0.1108454325 |
| **Cumulative** | **24** | **0.4550374075** |

User ceiling: $5. Remaining: **$4.5449625925**. Reservations in the ledgers are
conservative guards, not extra charges. Totals use provider response usage costs,
not an independent wallet reconciliation. Uncached catalog estimates can differ
from reported cost when provider caching applies. All 16 new responses returned
the requested model ID and completed with stop, without token truncation.

## Phase 1: an audit reminder was insufficient

The [original plan](plan.md) and [tasks](tasks.json) were frozen before generation.
The published baseline is `c728b82d2bf7770e9861a87b8f4682545f3272f4`.

1. Candidate v1 added fact/proposal/unknown distinctions and final-copy checks. Two
   development pairs used new textile-assessment and volunteer-roster briefs.
2. Development outputs still filled unknown methods with promises and turned
   unknown identity logging into a negative claim. Candidate v2 added explicit
   checks for negative clauses, invented resolution stages and audience needs
   becoming access permissions. Both development cases were rerun for candidate
   only; that selection effect is disclosed.
3. The [candidate decision](candidate-decision.json) froze v2 with development
   results explicitly labeled mixed. Two held-back museum and greenhouse briefs
   were then generated, baseline versus v2, with no further edits to that candidate.

Selected evidence:

| Pair / response | Actual observation |
|---|---|
| Textile baseline [2faad8](2faad8.md) | Says a request reserves a slot and invents fee timing, while retaining the assessment mechanism. |
| Textile v1 [ea8321](ea8321.md) | Improves the request/project distinction but invents methods defined per review. |
| Roster v1 [c1ec34](c1ec34.md) | Says the record does not log editor identity while its own table calls identity logging unknown. |
| Textile v2 [e40bdf](e40bdf.md) | Still invents variable methods and confirmation of terms before booking. |
| Roster v2 [01ebcb](01ebcb.md) | Removes the explicit identity denial from the caption but says submission schedules a demo and grants direct venue visibility. |
| Museum v2 [c4107d](c4107d.md) | Caption denies unspecified scope; its audit claims it avoided asserting absence. |
| Greenhouse v2 [b5b785](b5b785.md) | Preserves CSV/date mechanisms but denies unknown validation capabilities and invents billing substantiation. |

The comparison did not establish reliable transfer. Raw baseline and candidate
outputs, including all misses, remain beside their JSON receipts. Full provisional
criterion reviews: [development](development-review.json) and
[held-out](held-out-review.json).

## Phase 2: plan new claims first, then render

The [phase-2 plan](phase2-plan.md) was frozen after phase 1, with two additional
[briefs](phase2-tasks.json) about heritage map layouts and building-ticket summaries.
Each compared published baseline, frozen v2 and frozen v3. No phase-1 test prompt was
reused in this phase. Fact IDs were supplied equally to every arm. These new briefs
are author-constructed synthetic transfer probes, not independently sampled real
tasks or an independently labeled held-out benchmark.

The new hypothesis was that the model was treating “audit” as critique of old copy,
not checking its new assertions. V3 asks for the new-claim/support/disposition plan
before the final expressions. It is a process hypothesis, not a claim about hidden
model internals.

| Task | Baseline | Candidate v2 | Candidate v3 |
|---|---|---|---|
| Heritage layout | [39443b](39443b.md): invents confirmation stages and says a request books an appointment. | [23fc48](23fc48.md): avoids instant booking but asserts billing is not initiated, despite unknown payment timing. | [b54ff0](b54ff0.md): keeps the request/review/print distinction and avoids that billing assertion; still says unknown print specifications are determined separately. |
| Building-ticket summary | [405ac8](405ac8.md): describes unknown access/signature/verification properties as absent. | [18b695](18b695.md): preserves output fields but invents when unknown scheduling/setup terms are confirmed. | [ce4256](ce4256.md): the claim plan correctly rejects an identity/timestamp denial, then a final pitch footnote denies unknown access, timestamp and certification properties anyway. |

V3 improved some local wording and made planned claim support inspectable. It did
**not** solve final-copy fidelity. In particular, an accepted claim plan can coexist
with new unsupported statements introduced during rendering. The requested copy
and supplied mechanisms remained present, so the issue was not merely refusal or
vagueness. No general quality win, calibrated accuracy or production readiness is
inferred. The [phase-2 review](phase2-review.json) preserves provisional judgments.

## Decision and next boundary

Retain the guidance as an explicit, source-grounded drafting checklist and the
regressions as desired behavior. Do not advertise the checklist as a dependable
automatic correction mechanism or use this model's self-audit as approval. The
synthetic results provide negative evidence against relying on prompting alone.
The checklist's logical boundaries are authored requirements; their presence is
not evidence that a sampled model follows them.

Stop live testing after the frozen phase-2 responses rather than tune repeatedly to
known misses or spend the budget for its own sake. A later experiment could test a
separate source-check/correction pass against a matched control on additional fresh
briefs. That approach was not executed here and is not claimed to work.

## Provenance, review and verification

- Readable response Markdown has trailing whitespace normalized for repository
  hygiene. The response text in each JSON receipt is the exact returned content.
- Each context snapshot contains exact source bytes and hashes. Baseline uses 11
  files; candidates add the fact-check reference and changed routes/template. The
  joint bundle is tested, not any individual file or length effect.
- Candidate v3 source bytes match the final skill files; all prior contexts remain
  unchanged. Request hashes were reconstructed for every response from context,
  task, wrapper and parameters. [Verification](verification.json) separates these
  transport/accounting checks from semantic quality.
- Reviewer provenance is `model_teacher`, authoring assistant, not blind and not
  independent human adjudication. Suggested states are provisional. There is no
  aggregate semantic score, new grader contract or required behavioral gate.
- Earlier motivating findings are extracted with response IDs, model IDs and request
  hashes in [prior-findings.json](prior-findings.json); the full earlier report is
  preserved in the user's original comparison artifact.
- Catalog checks, schema/coverage checks, the existing brand CLI tests and required
  exact-head CI govern repository delivery separately. Live run completion and
  authored semantic review do not establish release-gated behavioral evidence.
