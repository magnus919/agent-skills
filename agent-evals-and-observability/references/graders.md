# Grader Families and Calibration

Compose graders by the property each can observe; no universal taxonomy or single grader is sufficient.

| Family | Direct evidence | Common boundary |
|---|---|---|
| Deterministic/programmatic | Schema, arithmetic, exact state-independent properties | A regex or keyword does not prove semantics, safety, or grounding |
| Execution/environment | Sandbox state, permissions, tool results, side effects | Requires faithful fixtures and reset evidence |
| Human-rubric | Contextual/domain judgment against an anchored rubric | Training, fatigue, incentives, and context affect results |
| Model judge | Structured assessment at scale | Prompt/model changes and bias require calibration |
| Pairwise/ranking | Relative preference or ordering | Randomize position and blind identity; full round robin is only one costly design |
| Domain/safety | Specialist or policy criteria | Must define scope, false positives, false negatives, and escalation |

For model judges and subjective rubrics, hold out calibration material from tuning. Blind candidate identity, randomize order where relevant, inspect rationales, compare errors and disagreement by slice, and use an agreement/error analysis appropriate to label type and decision. Predefine acceptable error for the risk; do not impose universal rater counts, agreement thresholds, or interpretations of kappa/correlation. Revalidate after grader prompt, model, rubric, task distribution, or policy changes.

Human review is valuable evidence, not definitive truth. Resolve disagreement through rubric refinement, adjudication rules, or escalation appropriate to the decision, and retain the disagreement rather than averaging it away.

## Build A Grader Contract

For every grader, record the property, inputs visible to it, output schema, direction/scale, abstention and error behavior, reference material, versioned implementation or prompt, cost/latency constraints, slices where it is valid, known failure modes, and false-positive/false-negative consequences. A reference answer is evidence, not automatically correct; version and review it like any other oracle.

Deterministic checks should target properties such as parseability, exact identifiers, allowed tool names, numerical invariants, or observed sandbox state. They should not use keyword presence as a proxy for factual grounding or policy compliance. Execution graders should query the environment after the run, distinguish planned from committed effects, and verify cleanup or reconciliation.

A model judge needs the task contract, only the evidence required to judge it, an anchored rubric with counterexamples, an abstain/insufficient-context path, and a structured rationale. Do not ask a judge to verify external facts it cannot access. Blind candidate identity and irrelevant metadata; randomize order in pairwise work; test order reversal and legitimate format/length variation. Sampled pairs, tournaments, active selection, and full round robins are different designs with different coverage and cost.

## Calibrate And Revalidate

1. Freeze rubric, calibration cases, human-review instructions, and candidate identities before the comparison.
2. Collect independent labels where the decision requires them; preserve reviewer identity or role in restricted metadata so systematic disagreement can be investigated.
3. Compare confusion/error patterns and disagreement by task and slice. Select agreement statistics for the label scale and sampling design rather than treating one coefficient as universal.
4. Inspect rationales and adjudicate sampled disagreements. Distinguish rubric ambiguity, missing evidence, grader bias, reviewer error, and legitimately plural answers.
5. Define where the grader can gate, where it can screen for review, and where it must abstain. Freeze the accepted grader version.
6. Revalidate after changes to the grader model, prompt, rubric, reference answers, task distribution, policy, or telemetry available to the grader.
