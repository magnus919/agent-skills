# nli-zero-shot: research evidence

Scoped primary-source and citation-chain research through Hermes GPU-host GroktoCrawl; source-level text inspected; reported results not reproduced.

Raw third-party snapshots remain local; original claims, limitations and hashes are tracked.

## yin-nli-full

[retained](https://arxiv.org/html/1909.00161); accessed 2026-10-13.

Formulates label-unseen text classification through natural-language entailment and evaluates transfer settings.

Limits/exclusion: Research benchmarks do not prove fraud utility; hypothesis formulation and task/domain transfer remain experimental.

Snapshot SHA-256: `160e13e428aad3fdcd34513276cdbc50fcf4f6e1bd5ae45ac73702ea551645fd`.

## mnli

[retained](https://arxiv.org/abs/1704.05426); accessed 2026-10-13.

MultiNLI expands inference evaluation across genres with entailment, neutral and contradiction labels.

Limits/exclusion: English genre coverage does not establish calibrated deployment decisions.

Snapshot SHA-256: `1527a58fd1d50137f98267b23b794abe7c72b1ac1dcadf1a668566ffff703ba8`.

## xnli

[retained](https://arxiv.org/abs/1809.05053); accessed 2026-10-13.

XNLI provides cross-lingual inference evaluation in 15 languages.

Limits/exclusion: Benchmark language coverage is not all-language or domain-specific validation.

Snapshot SHA-256: `0a4691519e568bce75bfd3a7c45171db4873a85a325e072ac6308dea06c16480`.

## anli

[retained](https://arxiv.org/abs/1910.14599); accessed 2026-10-13.

Adversarial NLI collects difficult examples through human-and-model interactions.

Limits/exclusion: Adversarial benchmark performance is not a universal robustness guarantee.

Snapshot SHA-256: `966f29bebca3d70b7250539b9e06db5fddbd95225220b94d274fccc4129d37e3`.

## hans

[retained](https://arxiv.org/abs/1902.01007); accessed 2026-10-13.

HANS challenges lexical-overlap, subsequence and constituent heuristics behind seemingly strong inference performance.

Limits/exclusion: Target-domain heuristic failures must be tested independently.

Snapshot SHA-256: `e7ed83873b5f4bf93ec3c83739ba8b171a4c73ad8a5323afe74904fdd0aead10`.

## calibration

[retained](https://arxiv.org/abs/1706.04599); accessed 2026-10-13.

Modern neural networks can be miscalibrated; temperature scaling is evaluated as a practical calibration method.

Limits/exclusion: Reported results are not proof that target-domain NLI or domain shift is calibrated.

Snapshot SHA-256: `4fc6cc672671c19d6a991abc41fe49bb5f9e4183082b0d30bebf55551c729260`.

## bart-mnli

[retained](https://huggingface.co/facebook/bart-large-mnli); accessed 2026-10-13.

Model card describes a BART MNLI checkpoint and text-to-hypothesis zero-shot usage.

Limits/exclusion: Card examples are not local runtime or downstream fraud results.

Snapshot SHA-256: `bb025dce2b1ad5400248d3a49da565e5d39cbb264cd8b4f719a76d0dbad77fed`.

## deberta-zeroshot

[retained](https://huggingface.co/MoritzLaurer/deberta-v3-large-zeroshot-v2.0); accessed 2026-10-13.

Zero-shot checkpoint card describes classification-oriented training and a binary true/not-true head.

Limits/exclusion: Semantic mapping must be verified for the selected exact checkpoint; do not assume a three-class head.

Snapshot SHA-256: `3e3c53dbfc817d7f9634cbf4efe8532390b059a2652147401c5c15a1b442285a`.

## multilingual-nli

[retained](https://huggingface.co/MoritzLaurer/mDeBERTa-v3-base-mnli-xnli); accessed 2026-10-13.

mDeBERTa checkpoint combines English MNLI and multilingual XNLI for inference transfer.

Limits/exclusion: Target language, label phrasing and domain accuracy remain unmeasured locally.

Snapshot SHA-256: `1023a451e8c56b0ec9d79249495dcf354c0b877d75da88b63c588d8972abd992`.

## hf-nli-pipeline

[retained](https://huggingface.co/docs/transformers/main_classes/pipelines#transformers.ZeroShotClassificationPipeline); accessed 2026-10-13.

Pipeline documents candidate labels, hypothesis templates and multi-label classification behavior.

Limits/exclusion: Rolling documentation must be checked against the installed version.

Snapshot SHA-256: `5d4cb4a7278352f9606c458b16ecc4f3d4ec9bcc37515d141a3935f1813816e7`.

## hf-nli-code

[retained](https://github.com/huggingface/transformers/blob/v5.19.0/src/transformers/pipelines/zero_shot_classification.py); accessed 2026-10-13.

Pinned v5.19.0 source normalizes entailment across candidates for single-label K>1, uses entailment-versus-contradiction for multi-label or K=1, and preserves hypotheses through only-first truncation.

Limits/exclusion: Code inspection establishes implementation semantics, not correct head metadata, calibration or task accuracy.

Snapshot SHA-256: `f1ecf8a7577895da9513db40e82501a3bd4ac28937c656df8bf9884334c16c97`.
