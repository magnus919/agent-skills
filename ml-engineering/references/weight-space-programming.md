# Weight-space inspection and targeted repair

Use when an open-weight model has a measured failure and direct tensor inspection
or editing is a plausible experiment. This is experimental methodology, not an
Unsloth feature or a substitute for behavioral evaluation. Start with
`templates/weight-edit-study.md`; model selection remains in
`references/specialization-decisions.md`.

## Evidence and limits

Primary source, checked 2026-11-03:
[Sparks of Weight-Space Programming](https://rikiyat.github.io/blog/weight-space-programming/)
(Takehi, Teoh, Zhang and Khattab, November 2, 2026), especially experiments 3,
7 and 8 and the additional Gemma experiment. The authors link complete experiment
logs and an edited checkpoint. The following are their reported results, not
locally reproduced outcomes or a mature cross-model capability guarantee.

- On Qwen3.5-0.8B, a targeted edit affecting 131,072 parameters reduced looping;
  reported MATH-500 increased from 7.9% to 48.1%, under the same sampling settings.
  This supports a failure-repair hypothesis: answers the model could already
  produce became more likely to finish. It does not demonstrate new mathematical
  capability from arbitrary edits.
- A non-looping Gemma 3 270M showed no established math improvement. Preserve this
  negative result when considering generalization across architectures or errors.
- Weights alone did not distinguish sycophantic Gemma models in four attempts.
  Attention probes enabled identification in three trained pairs. Probe access is
  additional evidence; neither static tensor differences nor attention patterns
  alone establish a causal behavioral explanation.
- Small policy-construction demonstrations have explicit architecture, game and
  feedback restrictions. They do not establish superiority to training in general.
  Backdoor discovery, reliable unlearning and cross-architecture circuit transfer
  are proposed directions, not validated capabilities from these experiments.

## Choose the smallest testable intervention

1. Measure the original failure on development data: looping, termination,
   truncation, arithmetic mistakes, formatting or task error. Record evidence
   rather than inferring a defect from an unusual weight distribution.
2. Compare simpler remedies: supported decoding settings, token budget, prompt
   changes, an appropriate base checkpoint, or ordinary adaptation. Freeze a
   same-decoding comparison to isolate weight effects; record a separately tuned
   decoding control to assess practical alternatives. Do not attribute a bundled
   decoding/checkpoint change solely to weights.
3. State which tensors or directions are suspected and what observation would
   falsify the mechanism. Read-only inspection can suggest hypotheses. Use
   permitted probes and controlled ablation/reversion to test them; report a
   plausible explanation as unconfirmed if intervention evidence is absent.
4. Freeze development and final-test roles before editing. Diagnostic prompts,
   attention probes, scores and sampled outputs all supply feedback. Count model
   calls, batch sizes, sequences, tokens, wall time and cost; a batched call is
   not one example. Gradient-free does not mean data-free or compute-free.
5. Set edit scope, maximum candidates and feedback budget, quality thresholds,
   critical regressions and stop rules before inspecting candidate results.
   Keep final tests inaccessible to the editing loop. Repeated test-based edits
   turn that test into development data and require a new held-out assessment.

## Reproducible artifact boundary

Before the first write, confirm target, scope and rollback path. Existing explicit
session authorization can supply these facts. Work on a copy; preserve the
immutable base and its hash. Never overwrite a deployed checkpoint in place.

Record checkpoint/tokenizer/config revisions and hashes; tensor names, shapes,
dtypes, coordinate or direction selection, coefficients and before/after hashes;
editing script revision, dependencies, seed and ordered operations; editor model
and prompt revision; diagnostic data, probes and complete feedback history;
resulting checkpoint and evaluation artifact hashes. Record changed-element counts
and norms with their denominator and numerical tolerance. A sparse parameter
change does not bound behavioral impact. No optimizer state is implied by an
edited inference checkpoint.

Load only trusted artifacts using an appropriate safe tensor loader. Check tensor
keys, shape/dtype compatibility and finite values. Fresh-process reload and
reproduction of the patch must precede evaluation claims. After conversion,
quantization or export, repeat task and regression evaluation in the intended
runtime; an in-memory score does not validate the shipped artifact. Route named
server operation to `llama-cpp` or `vllm`, and actual Unsloth training/export to
`unsloth` only where compatibility is established.

A tensor diff or hash check verifies an artifact boundary only. It cannot certify
causality, absence of backdoors, successful unlearning, safety or task improvement.
Do not upload private weights or diagnostic data without the corresponding scope.

## Acceptance, stopping and rollback

Evaluate paired baseline/candidate outputs on the frozen roster, with controlled
sampling and repetitions. Report task quality, answer completion, loop detection
method, token-limit hits, generated tokens, latency and resource cost separately.
A lower truncation rate alone is not better reasoning; longer allowances alone
can change accuracy and cost. Include unrelated capabilities and consequential
failure slices; sparse edits can have broad regressions.

Compare the targeted patch to its reversion and relevant simpler controls. Where
needed, use layer/direction ablations to distinguish the proposed mechanism from
an incidental effect. Separate diagnostic evidence from causal conclusions.

Stop at the registered budget or when the hypothesis fails. Keep ineffective and
negative candidates in the ledger. Hold promotion for missing evidence or any
unresolved critical regression, even if the target benchmark improves. Completion
is a reproducible candidate plus a measured accept/reject/inconclusive decision,
limitations and rollback instructions, not necessarily an improved model.
Rollback restores the pinned original artifact and serving configuration, followed
by a baseline smoke check; release authority remains a separate decision.
