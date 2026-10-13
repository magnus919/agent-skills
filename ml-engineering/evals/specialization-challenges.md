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
