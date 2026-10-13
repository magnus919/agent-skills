# Evaluating NLI as a decision component

## Preregister the comparison

Use `templates/nli-experiment.md`. State the actual outcome, prediction timestamp,
permitted text, policy revision and critical errors. Freeze source IDs and splits,
label definitions, hypotheses, tokenizer/truncation, candidate roster, scoring mode,
model/head revisions and hardware. Select thresholds and wording using development
and calibration data only. Retain a source/entity/time-held-out test set.

Compare rules, lexical/embedding baselines, a supervised encoder or SetFit when
labels exist, NLI and a prompted LLM where relevant. Allocate matched development
budgets and report pair counts: N premises × K hypotheses is N×K model inputs,
not N requests worth of compute. Measure tokenized lengths, batch size, memory,
p50/p95 latency and end-to-end preprocessing cost. Do not call a classifier cheaper
without measurement at the intended candidate count and concurrency.

## Quality, uncertainty and abstention

Report per-label precision/recall, macro/micro F1 where appropriate, confusion
matrices and prevalence. Include rare-critical errors, out-of-domain rejection,
negation, lexical-overlap traps, conflicting labels, label/template paraphrases,
quoted policies and truncation placement. Multi-label thresholds are per-label
unless evidence supports pooling. English benchmarks do not validate multilingual
premises or translated hypotheses; score language/domain slices and disagreements.

Calibration must use independent target-domain labels with known reviewer
provenance. Reliability curves, Brier/log loss and a properly described ECE help
assess probability claims; sparse bins and shifted prevalence can mislead. Guo's
temperature-scaling result motivates an experiment, not a guarantee that temperature
scaling fixes zero-shot or domain shift. Separate temperature fitting from decision
threshold selection. Test both on held-out data; report confidence intervals and
support counts. Another model's labels are advisory pseudo-labels, not human truth.

Define an abstention policy using development evidence: low support, close competing
scores, neutral evidence where available, OOD inputs or critical missing context.
Compare coverage-versus-risk curves and critical false acceptance at the selected
operating point. A softmax margin or arbitrary 0.9 threshold is not a calibrated
confidence guarantee. In single-label mode an explicit unknown candidate still
competes through wording; measure its behavior rather than assuming universal
OOD detection. Send unresolved high-impact cases to human review or a separately
evaluated escalation route; measure that route's cost and quality too.

## Adapt only after baseline evidence

If zero-shot misses the task, identify whether labels, context, truncation or
representation explain the errors before gradient training. Compare few-shot
encoder tuning, SetFit, task-specific NLI adaptation and distillation under fixed
label budgets. Distillation transfers teacher errors unless independent labels
challenge them. Freeze teacher/version/prompt, preserve disagreements and separate
teacher agreement from target accuracy. For general coding or generation, route
back to the fine-tuning methodology and Unsloth; NLI cannot replace a code generator.

Promotion requires every preregistered quality and resource guardrail, independent
review of consequential outcomes, a reproducible artifact and measured runtime.
Monitor roster/policy/template changes, prevalence, language mix, truncation and
abstention. Any such change can invalidate thresholds and requires a new comparison.
Rollback restores the previous model, tokenizer, label/policy bundle and thresholds
together. Stop with a documented non-promotion result when evidence is incomplete.

## Evidence boundaries

Unit tests of `scripts/nli_score_contract.py` establish arithmetic, rejection and
privacy behavior on synthetic records only. They do not establish NLI accuracy,
GPU feasibility or calibrated abstention. Eval manifests are authoring contracts;
structural validation does not imply successful model-generated skill behavior.
