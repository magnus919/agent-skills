# Judge stability, abstention, and escalation

A model judge is an instrument with its own error profile. Validate it before using it as a gate.

## Stability protocol

Freeze the rubric, judge model and prompt, reference material, candidate identity masking, and sampling plan. On a calibration set held out from prompt tuning:

1. Compare judge labels with independent human or domain labels appropriate to the task.
2. Repeat stochastic judgments when variation could change the decision; report the distribution, not only the mean.
3. Randomize candidate order and rerun pairwise cases with the order reversed.
4. Inspect disagreement by task, slice, length, style, and evidence availability.
5. Test insufficient-context and adversarial/judge-injection cases.
6. Freeze the accepted judge version and revalidate after model, prompt, rubric, reference, policy, task distribution, or telemetry changes.

Position, verbosity, and self-preference effects are documented risks in published judge studies, but their magnitude is setting-dependent. Do not import a universal correction or agreement threshold.

## Structured judgment

Prefer atomic checklist items when a holistic score hides the cause of failure. Each item names the observable property, evidence visible to the judge, pass/fail or ordinal scale, counterexample, and consequence of an error. Keep rationales short and structured; they are diagnostic evidence, not private reasoning or proof.

Use a panel or stronger judge only when the decision risk and expected disagreement justify its cost. Predefine aggregation, disagreement handling, and the boundary at which the judge must abstain. An abstention is a valid result: route it to human or domain review, or hold the release when no safe fallback exists. Never convert missing evidence into a confident score.
