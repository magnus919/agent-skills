# family-3-extraction-summarization: research evidence

Scoped primary-source and citation-chain research through Hermes GPU-host GroktoCrawl; source-level text inspected; reported results not reproduced.

Raw third-party snapshots remain local; original claims, limitations and hashes are tracked.

## gliner-paper

[retained](https://arxiv.org/abs/2311.08526); accessed 2026-10-13.

GLiNER uses a bidirectional text/label representation to identify spans for requested entity types.

Limits/exclusion: Author abstract; labels/scores do not establish calibration or critical-entity recall.

Snapshot SHA-256: `db9810c99e1e90544288ecc5e6ffe985d1b589238c3d34189944658fe9c415a5`.

## gliner-code

[retained](https://github.com/urchade/GLiNER); accessed 2026-10-13.

Author implementation exposes open-label extraction and model-specific inference/training routes.

Limits/exclusion: Repository/README is not an executed checkpoint or verified deployment.

Snapshot SHA-256: `c5907752c75d052ab559000f83bd1dddbbe89ed8721173997888b7febbf95cf6`.

## gliner2-code

[retained](https://github.com/fastino-ai/GLiNER2); accessed 2026-10-13.

Author SDK documents entities, confidence/offset controls and structured extraction/classification operations with versioned schemas.

Limits/exclusion: Decide classification weights and all extraction heads are not interchangeable; exact source offset mapping and permissions still need validation.

Snapshot SHA-256: `5122ef352a68ee50c5ff3d48107db63be002ab279d3c5bf739860e0a4d080c05`.

## bart

[retained](https://arxiv.org/abs/1910.13461); accessed 2026-10-13.

BART pretrains an encoder-decoder with corruption and reconstruction and supports generation tasks.

Limits/exclusion: Abstractive outputs can hallucinate; source/task fine-tuning and factuality evidence remain needed.

Snapshot SHA-256: `c442d42d5b9a97ba8f592317af0aa49625599d11e0223796c744f75ed4589188`.

## pegasus

[retained](https://arxiv.org/abs/1912.08777); accessed 2026-10-13.

Gap-sentence pretraining is tailored to abstractive summarization and evaluated across domains.

Limits/exclusion: Author benchmark claims do not establish private-domain retention or faithfulness.

Snapshot SHA-256: `0a5caca5c8f82f6a6781da60fa65ac6fa66e84574418c4199ccc49e3132568b7`.

## qags

[retained](https://arxiv.org/abs/2004.04228); accessed 2026-10-13.

Question-answer consistency offers a summary factuality screen compared with human judgments.

Limits/exclusion: QA/question generation errors and missed facts limit independent truth/coverage.

Snapshot SHA-256: `53f7947e817ca812df9c4ba236a9355921ee0f991c7e79de0d0f2cf4a0b040b9`.

## frank

[retained](https://arxiv.org/abs/2104.13346); accessed 2026-10-13.

A human-annotated factual-error typology distinguishes kinds of fluent but wrong summaries and metric strengths/weaknesses.

Limits/exclusion: Dataset/domain/annotator scope does not guarantee one universal factuality metric.

Snapshot SHA-256: `58bc8362627733addf1373c80d85b213860664307dac44e4791a0d910a6a3de4`.

## summac

[retained](https://arxiv.org/abs/2111.09525); accessed 2026-10-13.

Sentence-level NLI granularity and aggregation improve inconsistency detection in the studied summary tasks.

Limits/exclusion: Score is a model prediction, not independently adjudicated truth.

Snapshot SHA-256: `d456d108281687bab082677eed63243912564216b743571fab8676f5fee9222e`.

## hf-summary

[retained](https://huggingface.co/docs/transformers/tasks/summarization); accessed 2026-10-13.

Official seq2seq guide describes source/target preprocessing, labels and generation evaluation.

Limits/exclusion: Version-matched runtime required; training a chat decoder is a different contract.

Snapshot SHA-256: `b48427b38503192f6dfd104b9b00ae439ff6aa188fa7bec67a255f5b08362e9d`.

## cdm-extract

[retained](https://docs.scaledown.ai/api-reference/extract-overview); accessed 2026-10-13.

Vendor docs define description-driven spans/offsets and categorical-field classifier routing.

Limits/exclusion: Hosted contract is not proof of local weights or calibrated confidence.

Snapshot SHA-256: `711463be256924881509cba3e0d1f5fc79be6b13a62345cffb3136d9db3cc68c`.

## cdm-summary

[retained](https://docs.scaledown.ai/api-reference/summarize-overview); accessed 2026-10-13.

Vendor docs define an abstractive rewrite with tuned/fixed sampling and size/latency metadata.

Limits/exclusion: Interface does not establish claimed architecture, factuality or complete-task quality.

Snapshot SHA-256: `85fb4611c28e4756a1a87bec62127a1bf04605a7e21066f05f4d1c09a36ba0df`.

## gliner-full

[retained](https://arxiv.org/html/2311.08526); accessed 2026-10-13.

Method includes label-conditioned span representation and supervised extraction rather than autoregressive entity text generation.

Limits/exclusion: Actual tokenizer/truncation/label threshold compatibility and downstream recall require an executed trial.

Snapshot SHA-256: `cf17cb9b85982400885841169f58407c9ac7114bc941ff9d411e748ae867e432`.

## qags-full

[retained](https://arxiv.org/html/2004.04228); accessed 2026-10-13.

Method compares source/summary answers and human factuality judgments and discusses sensitivity to pipeline components.

Limits/exclusion: QA-based agreement cannot certify every claim or critical omission.

Snapshot SHA-256: `c0c7a221a412343de95fb93dfe29127d61a3da9678610127c427b2c4aba9b9ae`.

## frank-full

[retained](https://arxiv.org/html/2104.13346); accessed 2026-10-13.

Method analyzes multiple factual-error classes and compares metrics against annotated summaries.

Limits/exclusion: Independent reviewer/domain evidence is still necessary for consequential sources.

Snapshot SHA-256: `7ce890d68b289c5a1035f9f67c67d40fecbc74e692f408ae9f273d52bba095a1`.

## summac-code

[retained](https://github.com/tingofurro/summac); accessed 2026-10-13.

Author implementation supplies sentence/document inconsistency scoring and evaluation routes.

Limits/exclusion: Dependency/model/version/runtime not verified; no local model call made.

Snapshot SHA-256: `5b00ba42d446f87c7a1a6b33a00ed8005ce1f5677a6dd4c16a44bd12254c26e1`.

## t5

[retained](https://arxiv.org/abs/1910.10683); accessed 2026-10-13.

Text-to-text transfer pretraining provides an encoder-decoder task formulation, including generation.

Limits/exclusion: Architecture/output formulation alone does not prove faithful summarization or calibration.

Snapshot SHA-256: `71b425168a35a37bb5d8d37bd258ac46371960e3f962cc16688cba95e0ccc579`.
