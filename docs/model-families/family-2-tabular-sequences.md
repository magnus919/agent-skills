# family-2-tabular-sequences: research evidence

Scoped primary-source and citation-chain research through Hermes GPU-host GroktoCrawl; source-level text inspected; reported results not reproduced.

Raw third-party snapshots remain local; original claims, limitations and hashes are tracked.

## tabtransformer

[retained](https://arxiv.org/abs/2012.06678); accessed 2026-10-13.

Contextual categorical embeddings and optional unlabeled pretraining support robust row classification in the reported tasks.

Limits/exclusion: Feature-token attention is not transaction-order attention; abstract results remain author-reported.

Snapshot SHA-256: `afcaee0f8daf4fe21656ad9fd37bc0f2787ee90d1a4cd7ab083b908c133f0e6c`.

## ft-transformer

[retained](https://arxiv.org/abs/2106.11959); accessed 2026-10-13.

Matched experiments compare ResNet-like and feature-transformer baselines with trees and report no universal winner.

Limits/exclusion: Comparative protocol matters more than architecture names; abstract alone supplies no local capacity evidence.

Snapshot SHA-256: `a03602adc41cca9efaa7cf66dc45eaa2b8a8d1460dd4c046ccf3b1cccb412587`.

## saint

[retained](https://arxiv.org/abs/2106.01342); accessed 2026-10-13.

Combines row and column attention with contrastive pretraining.

Limits/exclusion: Batch/cohort composition and inductive/transductive access must be declared; no local reproduction.

Snapshot SHA-256: `e62afccbbd674734c2058d7d2ddb390bb077fd4e52f6b3f1be9267b25c86cfce`.

## vime

[excluded](https://papers.nips.cc/paper/2020/hash/7d97667a3e056acab9aaf653807b4a03-Abstract.html); accessed 2026-10-13.

Proceedings target extracted administrative name-change content, not the paper.

Limits/exclusion: Exclude as substantive evidence; author implementation fetched separately.

Snapshot SHA-256: `f288114ecf6ba151e80adef7d2069ee2ece05e0882ef95be668c3c86148ff359`.

## tabnet

[retained](https://arxiv.org/abs/1908.07442); accessed 2026-10-13.

Stepwise feature selection and optional self-supervised reconstruction are described for tabular tasks.

Limits/exclusion: Attention/selection is not causal attribution; paper abstract claims not locally tested.

Snapshot SHA-256: `b97b06ef5d75e647bb3bd5d3b644f1847eadd78901686ec3437c478c328af514`.

## booking-sequence

[retained](https://arxiv.org/html/2405.13692v1); accessed 2026-10-13.

Production study compares self-supervised tabular transformers with boosted-tree fraud detection.

Limits/exclusion: This is a tabular row-model result, not evidence of transaction-sequence modeling; private data prevents direct reproduction.

Snapshot SHA-256: `13e9bb989aee6929dc6c94180a19dc32ddb47d761b6f527e9f142dc677cf1d93`.

## tft

[retained](https://arxiv.org/abs/1912.09363); accessed 2026-10-13.

Forecasting distinguishes static, known-future and observed historical covariates with recurrent/attention processing.

Limits/exclusion: Forecasting objectives/uncertainty do not automatically become fraud-classification probabilities.

Snapshot SHA-256: `432cfedc4d4c34dca35bf9427993c8152fe1f1f2f9490dc76d9ce4ccf2f3e913`.

## ts2vec

[retained](https://arxiv.org/abs/2106.10466); accessed 2026-10-13.

Hierarchical contrastive contexts yield timestamp representations that can be pooled for sequence tasks.

Limits/exclusion: Public time-series benchmark gains do not establish irregular transaction/fraud performance.

Snapshot SHA-256: `ee4b9e1e75cc12ffdde424b9e417a311504bd8ab5dff0ae8e0662bd7c4aaba5c`.

## ts2vec-code

[retained](https://github.com/zhihanyue/ts2vec); accessed 2026-10-13.

Author implementation exposes training/encoding/scoring and old dependency pins.

Limits/exclusion: README/code discovery, not executed current-stack compatibility.

Snapshot SHA-256: `c81ce8850d51c47f1177730274355be025f282daef1ed7942a1d9a370db0b24b`.

## sklearn-timesplit

[retained](https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.TimeSeriesSplit.html); accessed 2026-10-13.

TimeSeriesSplit yields chronological folds with configurable gap and documented equally-spaced comparability assumption.

Limits/exclusion: Row-index gaps are not automatically time-duration gaps for irregular events; no entity handling guarantee.

Snapshot SHA-256: `1c224febb4a1c04e2f4a5984d97e3d41c21433f537de1269ae83d6ba86fc2676`.

## tabtransformer-full

[retained](https://arxiv.org/html/2012.06678); accessed 2026-10-13.

Method text separates categorical embedding contextualization, supervised head and optional pretraining objectives.

Limits/exclusion: Compare numeric/categorical fusion and corruption assumptions on deployment-shaped data.

Snapshot SHA-256: `4dda82cc7166373071034d24e93b01c28768f2eb13c6092b521440db69eab801`.

## ft-transformer-full

[retained](https://arxiv.org/html/2106.11959); accessed 2026-10-13.

Method comparison uses shared experimental protocols and feature tokenization rather than claiming all tabular deep models dominate trees.

Limits/exclusion: Extracted methods do not establish fair budgets in a new study.

Snapshot SHA-256: `a1110211cb6df8a35202575a776d00828b5e18df7ecea648f07317bff1a9487d`.

## saint-full

[retained](https://arxiv.org/html/2106.01342); accessed 2026-10-13.

Method details provide intersample/intrasample attention, augmented views and supervised adaptation.

Limits/exclusion: Row-context composition is additional information; final holdout exposure must be explicit.

Snapshot SHA-256: `99552e220c6bcebace007ada0bf012277f2ed26d347ec22098e466f553a3791b`.

## ts2vec-full

[retained](https://arxiv.org/html/2106.10466); accessed 2026-10-13.

Method includes contextual augmentations and hierarchical contrastive representation objectives.

Limits/exclusion: Encoding/causal choices and pooled representation require task validation, not presumed forecasting or calibration.

Snapshot SHA-256: `9d9ce4b31b5e54d866053af923a2c491c57779f284e236cb242b7229d8a0db9d`.

## ft-code

[retained](https://github.com/yandex-research/tabular-dl-revisiting-models); accessed 2026-10-13.

Author repository supplies research configurations and experimental baselines.

Limits/exclusion: Pin and inspect actual implementation in isolation; not a validated operational skill.

Snapshot SHA-256: `16080189d2560b13f5484249d65cdf6156dc2e73b1b7ab3c548405f5219ae5e2`.

## vime-code

[retained](https://github.com/jsyoon0823/VIME); accessed 2026-10-13.

Author implementation separates self-supervised and semi-supervised feature-masking/recovery workflows.

Limits/exclusion: README is bounded evidence; augmentations and unlabeled exposure need task-specific validation.

Snapshot SHA-256: `a93e5f9c845f845a26e7860677f00c27ba47f1785016a892aadab2a763ee9d30`.
