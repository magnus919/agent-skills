# Tabular representation and sequence evidence

Accessed 2026-10-13 via GPU-host GroktoCrawl. Original source records, extraction
failures and hashes are tracked at repository `docs/model-families/family-2-tabular-sequences.md`.
No encoder training, forecasting or fraud improvement was reproduced here.

- [TabTransformer](https://arxiv.org/abs/2012.06678): contextual categorical
  embeddings and semi-supervised pretraining; not event-sequence attention.
- [Revisiting tabular DL/FT-Transformer](https://arxiv.org/abs/2106.11959),
  [author code](https://github.com/yandex-research/tabular-dl-revisiting-models):
  comparable experiments, strong ResNet baseline and no universally best learner.
- [SAINT](https://arxiv.org/abs/2106.01342): feature/intersample attention and
  contrastive views; inference cohort effects require explicit control.
- [TabNet](https://arxiv.org/abs/1908.07442): feature selection/self-supervision;
  model attributions do not establish causal identification.
- [VIME author code](https://github.com/jsyoon0823/VIME): masking/recovery and
  semi-supervised routes. Proceedings extraction failed substantively and is excluded.
- [Booking.com fraud](https://arxiv.org/abs/2405.13692): private-data production
  tabular-transformer study; not evidence that order was modeled as a sequence.
- [TFT](https://arxiv.org/abs/1912.09363): mixed covariate/horizon forecasting;
  transfer to classification remains a separate hypothesis.
- [TS2Vec](https://arxiv.org/abs/2106.10466),
  [author implementation](https://github.com/zhihanyue/ts2vec): contextual
  representations and pooled tasks; old dependency recipes are not current validation.
- [TimeSeriesSplit](https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.TimeSeriesSplit.html):
  chronological folds, gap and equal-spacing assumptions; does not replace entity/
  availability/horizon reasoning.
