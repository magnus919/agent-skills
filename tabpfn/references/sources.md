# Source ledger

Accessed 2026-10-13 through GPU-host GroktoCrawl. Source-level findings, failures,
corrected discovery IDs and hashes are tracked in repository
`docs/model-families/family-1-tabular-foundations.md` and its JSON record.

- [Author code/README](https://github.com/PriorLabs/TabPFN): version/default,
  local checkpoint and authentication contracts. Code has not been executed here.
- [Model generations](https://docs.priorlabs.ai/models): version-specific and
  joint-capacity limitations, local/hosted boundaries. Not measured GPU limits.
- [Fine-tuning](https://docs.priorlabs.ai/capabilities/fine-tuning): separate
  weight-update classes and workflow; no adaptation run performed.
- [v2 weight license](https://huggingface.co/Prior-Labs/TabPFN-v2-clf/blob/main/LICENSE.txt)
  and [v3.5 weight terms](https://huggingface.co/Prior-Labs/tabpfn_3_5/blob/main/LICENSE):
  exact-generation scope matters; no automatic acceptance.
- [TabPFN-3.5 report](https://arxiv.org/abs/2609.17895): author abstract/capability
  claims, not independent runtime reproduction.
- [TabICL author implementation](https://github.com/soda-inria/tabicl),
  [original paper](https://arxiv.org/abs/2502.05564) and
  [v2 report](https://arxiv.org/abs/2602.11139): distinct model-family alternative,
  not operated by this skill.
- [From Tables to Time](https://arxiv.org/abs/2501.02945): forecasting via temporal
  features; not evidence of arbitrary sequence-model support.

Privacy-page extraction failed; the first guessed license URL returned an error
page despite wrapper success. Do not infer missing behavior or retain it as valid
license text. Updated docs may change these contracts; recheck the selected build.
