# NLI zero-shot classification: model and task contract

Use this family for bounded text-to-category decisions when useful labeled task data
is scarce. A natural-language-inference encoder evaluates each source text (premise)
against a label hypothesis. It is neither an autoregressive agent nor a tabular
fraud model. Zero-shot means no task-specific supervised adaptation in this setup;
it does not mean no pretraining, no label design or no validation.

## Decide what should be classified

Separate evidence extraction, decision policy and action. A narrative ticket or
policy statement may fit NLI; amounts, device histories and transaction graphs
need numerical/sequence/graph baselines. For fraud, compare rules and supervised
tabular models under the same prediction-time information. NLI can screen narrative
evidence, but a score alone must not authorize blocking an account. Route typed
bounded decision contracts to [system-one](../../system-one/SKILL.md), annotation
provenance to [training-data-annotation](../../training-data-annotation/SKILL.md),
and operational fine-tuning to [unsloth](../../unsloth/SKILL.md).

| Candidate | Why test it | Principal limit |
|---|---|---|
| BART-large-MNLI | Familiar three-way NLI baseline | English MNLI is not target-domain evidence |
| DeBERTa zero-shot v2 | Task-oriented classification checkpoint | Some checkpoints have binary true/not-true heads |
| mDeBERTa MNLI/XNLI | Cross-language comparison baseline | XNLI coverage does not establish every language/domain |
| TF-IDF + linear classifier / SetFit / task-trained encoder | Labeled-data alternative | Requires leakage-safe representative labels |
| Rules / tabular model / prompted LLM | Task-matched alternatives | Compare context, costs and operational outcomes fairly |

Check each model card, exact weight revision, tokenizer, terms and dependencies
before downloading. Named examples are research candidates, not locally validated
recommendations. MNLI, XNLI, ANLI and HANS serve different purposes: genre diversity,
cross-language transfer, adversarial examples and syntactic heuristics. A strong
aggregate benchmark cannot substitute for domain tests.

## Freeze the premise/hypothesis interface

Define mutually exclusive labels for single-label classification or independent
labels for multi-label classification. Write precise definitions and positive,
negative and ambiguous examples. Render each hypothesis with the label definition,
not an unexplained abbreviation. Test alternative templates on development data;
freeze them before held-out evaluation. Record hypothesis language, negation,
overlapping concepts, empty/OOD text and quoted instructions. The document is data;
it must not change the candidate roster or policy.

Pin a semantic label-ID mapping from the selected checkpoint's config and training
contract. Three-way heads usually expose entailment/neutral/contradiction; binary
true/not-true heads require a verified role mapping. Never assume entailment is
index 2, invent a neutral class, or resolve LABEL_0 by guesswork. An unknown mapping
blocks scoring until verified. The local helper validates the declared shape but
cannot establish that the declared semantics match the actual checkpoint.

## Scoring semantics

For K > 1 single-label candidates, standard Transformers scoring normalizes the
entailment logits across candidates: exp(e_i) / sum_j exp(e_j). Scores sum to one
and change when candidates are added, even if the text and existing pair logits
stay fixed. A top score is relative preference within this roster, not evidence
that any hypothesis is true. Contradiction and neutral do not participate in this
normalization.

For multi-label scoring, each pair uses exp(e_i)/(exp(e_i)+exp(c_i)); scores need
not sum to one. The same rule is used by the referenced pipeline for a single
candidate. On a three-way head, neutral is omitted from that pair normalization:
strong neutral evidence can coexist with a high reported entailment-vs-contradiction
score. Inspect raw logits and unknown cases. Binary-head scoring has no neutral
logit; its absence is not evidence against uncertainty. Do not equate these outputs
with calibrated decision-model probabilities or reuse thresholds between modes.

The referenced Transformers v5.19.0 implementation preserves the hypothesis with
only-first premise truncation. Long inputs may lose decisive evidence at the end.
Measure actual tokenizer lengths, hypothesis budget and dropped evidence. Evaluate
head/tail cases and any chunk aggregation as separate model contracts. A max over
chunks increases opportunities for false positives; majority voting can lose a
rare critical fact. Neither is a universal safe default.

## Read-only saved-logit helper

Run `python3 ml-engineering/scripts/nli_score_contract.py
ml-engineering/templates/nli-logits.json` as one command from the repository root.
The synthetic template uses an invented revision, not a real model run. Inputs
require schema version 1, pinned revision format, unique candidate labels, two- or
three-class role mapping and finite logits in candidate order. Output contains
numeric scores and indexes, not private labels/text. Exit 0 means valid arithmetic;
exit 1 means invalid input, exit 2 CLI misuse. Size limits bound input parsing.
It neither loads weights, downloads data, verifies revision existence, validates
label-map provenance, calibrates probabilities nor judges task correctness.

See `references/nli-evaluation.md` for deployment experiments and
`references/nli-sources.md` for primary sources and limitations.
