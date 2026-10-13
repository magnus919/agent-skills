# Specialization assertion challenges

2026-10-13; appended rubric v1 for new stable case IDs. Existing cases unchanged.
Author-written satisfying/contradictory/omitted examples, not executed model grading.
Artifact checks require a complete inventory; semantic claims require readable artifacts.
Presence of a filename or policy phrase does not prove correct design or execution.

## classifier-versus-generative-baselines

| Assertion | Satisfying | Contradiction | Omission |
|---|---|---|---|
| 1 | Include incumbent rules/trees and task-suitable classifiers. | LLM is necessary because the article calls it an agent. | No alternatives. |
| 2 | NLI label-relative scores need fraud calibration. | NLI scores are calibrated fraud probabilities. | No score semantics. |
| 3 | Same historical context or separate feature ablation. | Deny the tree history and attribute gain solely to LLM. | No information parity. |
| 4 | Mature delayed labels and correct sampled prevalence. | Use future labels/features or replay precision as production precision. | No temporal/prevalence protocol. |
| 5 | Winner remains unresolved on private data. | Unseen comments or case study prove zero-shot wins. | No evidence boundary. |

## matched-budget-task-comparison

| Assertion | Satisfying | Contradiction | Omission |
|---|---|---|---|
| 1 | Inventory includes comparison-plan.md. | Complete inventory lacks it. | Inventory absent. |
| 2 | Compare pass@1 and matched best-of-k separately. | 42 pass@1 versus 59 best-of-16 proves RL better. | No budget comparison. |
| 3 | Missing/infra tasks make evidence incomplete; retain timeouts. | Drop inconvenient tasks. | No task/status roster. |
| 4 | Resolve critical regression and all guardrails. | Aggregate gain overrides critical failure. | No promotion criteria. |
| 5 | Exit zero means descriptive completion only. | Helper zero approves release. | No interpretation of helper. |

## rl-evidence-disagreement

| Assertion | Satisfying | Contradiction | Omission |
|---|---|---|---|
| 1 | Rule/navigation results do not settle coding. | Paper title is a universal law. | No domain boundary. |
| 2 | Differing metrics/settings leave interpretations open. | Declare one universal new-capability theorem. | No disagreement discussed. |
| 3 | Fixed task budgets with distinct training/generation seeds. | Compare unequal attempts or collapse seed uncertainty. | No falsifiable protocol. |
| 4 | Judge agreement is limited evidence. | Teacher agreement independently proves reasoning. | No label/judge provenance. |

## paired-group-evidence

| Assertion | Satisfying | Contradiction | Omission |
|---|---|---|---|
| 1 | Hold model-only attribution with unequal harness/decoding. | Model name alone makes comparison matched. | No condition checks. |
| 2 | Expected roster includes missing tasks. | Intersection-only scoring omits gaps. | No coverage check. |
| 3 | Resample independent source groups. | Treat same-repo variants as independent. | No dependence model. |
| 4 | Intervals descriptive; seeds and release separate. | Positive interval automatically ships. | No uncertainty/promotion boundary. |

## task-specific-cdm-claims

| Assertion | Satisfying | Contradiction | Omission |
|---|---|---|---|
| 1 | Contract known; architecture/calibration/benchmarks unverified. | Post proves one-pass quality and calibration. | No evidence distinction. |
| 2 | New label scores/thresholds need matched calibration. | Compatible API implies old thresholds valid. | No probability semantics. |
| 3 | Check source spans and factual/downstream retention. | JSON or token savings alone proves quality. | No task-quality scoring. |
| 4 | Hosted endpoint does not establish local weights/training. | Download/train locally assumed from API presence. | No execution boundary. |
| 5 | Prepared comparison only; no provider call. | Upload private content for a demo. | No scope handling. |

## tabular-foundation-selection

| Assertion | Satisfying | Contradiction | Omission |
|---|---|---|---|
| 1 | Same permitted information/tuning budget. | Tree denied history or tuning. | No comparison conditions. |
| 2 | Save training context and exclude test labels. | Test labels included or context discarded. | No context artifact. |
| 3 | Separate measured capacity, exact terms and calibration. | Ceiling/open code/probability certifies all three. | No evidence boundaries. |

## tabular-self-supervision

| Assertion | Satisfying | Contradiction | Omission |
|---|---|---|---|
| 1 | Feature/row attention distinct from event order. | Row attention claimed temporal causality. | No token semantics. |
| 2 | Final/future exposure disclosed and controlled. | Unlabeled holdout assumed harmless. | No pretraining scope. |
| 3 | Comparable information and budget. | Tree denied equivalent context. | No baseline protocol. |

## forward-history-contract

| Assertion | Satisfying | Contradiction | Omission |
|---|---|---|---|
| 1 | Shared past okay; future/outcomes excluded. | Reject all shared history or permit future labels. | No history policy. |
| 2 | Target removed, availability/maturity checked. | Target self-history retained. | No source cutoff. |
| 3 | Masks cannot repair leaked features. | Causal mask makes any feature safe. | No leakage boundary. |

## forecast-versus-classification

| Assertion | Satisfying | Contradiction | Omission |
|---|---|---|---|
| 1 | Objectives separated. | Anomaly/forecast score automatically fraud probability. | No output contract. |
| 2 | Use time/horizon-based gap. | Ten rows called ten days. | No gap interpretation. |
| 3 | Independent calibration and simple control. | No classifier/calibration needed. | No task scoring. |

## sequence-runtime-evidence

| Assertion | Satisfying | Contradiction | Omission |
|---|---|---|---|
| 1 | Metadata only. | Screen proves hidden semantics. | No scope. |
| 2 | Observe runtime/device/reset/task. | No execution required. | No stage evidence. |
| 3 | Stages not run. | Audit called model pass. | No statuses. |

## extraction-source-contract

| Assertion | Satisfying | Contradiction | Omission |
|---|---|---|---|
| 1 | Original source mapping verified. | Byte offsets sliced as code points after normalization. | No offset/mapping contract. |
| 2 | Independent gold and critical recall. | JSON/.99 establishes coverage. | No gold/recall evidence. |
| 3 | Redacted artifact tested; teacher provenance limited. | Same model certifies all PII removed. | No artifact test. |

## summary-critical-retention

| Assertion | Satisfying | Contradiction | Omission |
|---|---|---|---|
| 1 | Critical facts/downstream tested. | ROUGE/compression is sufficient. | No retention protocol. |
| 2 | Authored receipts are consistency only. | Fixture zero is semantic pass. | No evidence distinction. |
| 3 | Hold on deadline/negation loss. | Cost gain overrides critical failures. | No promotion decision. |

## encoder-versus-chat-training

| Assertion | Satisfying | Contradiction | Omission |
|---|---|---|---|
| 1 | Three training contracts separated. | One chat trainer operates all. | No objective distinction. |
| 2 | Actual model-specific labels/retention checked. | JSON validity certifies collator. | No label/source audit. |
| 3 | Calibration requires task evidence. | Confidence score is calibrated. | No score semantics. |

## NLI family rubric additions

Each new assertion is challenged below; these are reviewer fixtures, not execution evidence.

| Case | Satisfying evidence | Contradictory near miss | Evidence omitted |
|---|---|---|---|
| `nli-score-semantics`: Explains that single-label scores depend on the candidate roster | Explicitly establishes this boundary with the relevant scoring/split/evidence contract | Claims the opposite or uses the rejected shortcut | Discusses NLI generally without addressing this property |
| `nli-score-semantics`: Distinguishes multi-label independent entailment-versus-contradiction scoring from single-label normalization | Explicitly establishes this boundary with the relevant scoring/split/evidence contract | Claims the opposite or uses the rejected shortcut | Discusses NLI generally without addressing this property |
| `nli-score-semantics`: Requires target-domain calibration and consequential-error evaluation before using a score to block accounts | Explicitly establishes this boundary with the relevant scoring/split/evidence contract | Claims the opposite or uses the rejected shortcut | Discusses NLI generally without addressing this property |
| `nli-head-and-truncation`: Requires checkpoint-specific verification of semantic label IDs instead of assuming index 2 | Explicitly establishes this boundary with the relevant scoring/split/evidence contract | Claims the opposite or uses the rejected shortcut | Discusses NLI generally without addressing this property |
| `nli-head-and-truncation`: Does not invent a neutral class for a binary head | Explicitly establishes this boundary with the relevant scoring/split/evidence contract | Claims the opposite or uses the rejected shortcut | Discusses NLI generally without addressing this property |
| `nli-head-and-truncation`: Requires evaluation of decisive evidence lost through premise truncation | Explicitly establishes this boundary with the relevant scoring/split/evidence contract | Claims the opposite or uses the rejected shortcut | Discusses NLI generally without addressing this property |
| `nli-abstention-and-language`: Keeps hypothesis and threshold selection separate from the held-out test set | Explicitly establishes this boundary with the relevant scoring/split/evidence contract | Claims the opposite or uses the rejected shortcut | Discusses NLI generally without addressing this property |
| `nli-abstention-and-language`: Requires evaluation by target language and domain rather than treating MNLI as multilingual validation | Explicitly establishes this boundary with the relevant scoring/split/evidence contract | Claims the opposite or uses the rejected shortcut | Discusses NLI generally without addressing this property |
| `nli-abstention-and-language`: Evaluates abstention with coverage and error risk at the chosen operating point | Explicitly establishes this boundary with the relevant scoring/split/evidence contract | Claims the opposite or uses the rejected shortcut | Discusses NLI generally without addressing this property |
| `nli-abstention-and-language`: Accounts for premise-by-candidate pair count in resource comparisons | Explicitly establishes this boundary with the relevant scoring/split/evidence contract | Claims the opposite or uses the rejected shortcut | Discusses NLI generally without addressing this property |
| `nli-helper-evidence`: Limits helper success to saved-logit arithmetic and contract checks | Explicitly establishes this boundary with the relevant scoring/split/evidence contract | Claims the opposite or uses the rejected shortcut | Discusses NLI generally without addressing this property |
| `nli-helper-evidence`: States that semantic label-map provenance is not verified by the helper | Explicitly establishes this boundary with the relevant scoring/split/evidence contract | Claims the opposite or uses the rejected shortcut | Discusses NLI generally without addressing this property |
| `nli-helper-evidence`: Requires real model and independently labeled task evidence before claiming accuracy | Explicitly establishes this boundary with the relevant scoring/split/evidence contract | Claims the opposite or uses the rejected shortcut | Discusses NLI generally without addressing this property |

Concrete response contrasts for the NLI assertions above:

- `nli-score-semantics`: satisfying: "Adding candidates changes the denominator; multi-label normalizes each entailment/contradiction pair. Fit and evaluate calibration and critical false blocks on target labels before account actions." Near miss: ".94 is a calibrated fraud probability in both modes; block now." Omitted: "NLI is useful for fraud" with no scoring or decision evidence.
- `nli-head-and-truncation`: satisfying: "Verify true/not-true role IDs against the pinned card/config; binary heads have no neutral. Test narratives whose decisive fact falls beyond the tokenizer's premise budget." Near miss: "Index 2 is always entailment; fill neutral with zero and truncate safely." Omitted: "Use a newer checkpoint" with no head or truncation discussion.
- `nli-abstention-and-language`: satisfying: "Tune wording and thresholds on development/calibration splits; freeze before testing each target language/domain. Report coverage versus error risk and N×K pair latency." Near miss: "Choose .9 and the best template on the test set; English MNLI validates all languages and N documents cost N pairs." Omitted: "Measure F1" without split, language, abstention or pair-count evidence.
- `nli-helper-evidence`: satisfying: "Exit zero checks saved arithmetic/shape only; mapping provenance is unverified. Execute the pinned model and test against independently labeled cases before accuracy claims." Near miss: "Synthetic helper success proves the weights, mapping and accuracy." Omitted: "The script works" with no evidence boundary.
