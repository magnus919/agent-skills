# Model-specialization evidence and uncertainty

Accessed 2026-10-13 via GPU-host GroktoCrawl. Empirical results below are reported
by their authors, not reproduced in this enrichment. Source-level records and
snapshot hashes are tracked at repository `docs/research/coinbase-post-training/`.
Use `references/specialization-decisions.md` for the decision process.

## Baseline choice

- [Grinsztajn et al., 2022](https://arxiv.org/abs/2207.08815) benchmark tabular
  learners with hyperparameter search and find strong tree baselines on their
  medium-sized tasks. This supports including trees, not claiming all tabular
  transformers or language models are worse.
- [Booking.com fraud study, 2024](https://arxiv.org/abs/2405.13692) reports
  tabular-transformer/self-supervised gains over its GBDT setting. Private features,
  data size and business metrics differ from Coinbase. The retrieved full text
  begins in method sections; conclusions remain author-reported.
- [Yin, Hay and Roth, EMNLP 2019](https://aclanthology.org/D19-1404/) define
  zero-shot text classification with label-unseen evaluation and entailment.
  The retained ACL record provides author abstract/citation, not full-paper PDF.
- [Transformers NLI pipeline](https://huggingface.co/docs/transformers/main_classes/pipelines#transformers.ZeroShotClassificationPipeline)
  documents candidate-label hypothesis pairing and score normalization. Retrieved
  v5.19.0 documentation is not installed compatibility. Scores need task-specific
  calibration/threshold checks; label counts influence cost.
- [TabPFN author repository](https://github.com/PriorLabs/TabPFN) is a route to
  tabular foundation-model baselines. The Nature publication fetch failed and its
  superiority claims are not used here. README support/limits, license, weight
  terms, privacy and local hardware still require verification before execution.

## Coding adaptation

[SWE-Gym](https://arxiv.org/abs/2412.21139) and
[SWE-smith](https://arxiv.org/abs/2504.21798) provide runnable task/trajectory
infrastructure. [DeepSWE](https://www.together.ai/blog/deepswe) demonstrates an
RL agent at a much larger resource scale. These support measuring training on
software tasks, not universal SFT/RL dominance or a local quality promise.

The [SFT/RL generalization study](https://arxiv.org/abs/2501.17161) concerns
rule-based reasoning/navigation; [RLVR limits](https://arxiv.org/abs/2504.13837)
and [reasoning-aware counteranalysis](https://arxiv.org/abs/2506.14245) disagree
in interpretation with differing settings/metrics. Compare task outcomes under
fixed budgets; retain judge uncertainty rather than force a synthesis that RL
creates new reasoning or only reweights existing answers.

[LoRA Learns Less and Forgets Less](https://arxiv.org/abs/2405.09673) reports a
plasticity/retention tradeoff sensitive to hyperparameters and data regimes.
[QLoRA](https://arxiv.org/abs/2305.14314) addresses weight/optimizer memory but
not every training/rollout component; optimizer paging may use host memory.

## Verifier and reward integrity

[EvalPlus](https://arxiv.org/abs/2305.01210) shows that stronger tests can reveal
wrong programs and change rankings. [Verifier audit](https://arxiv.org/abs/2606.16062)
reports false accepts and false rejects from generated augmentations on selected
tasks. The [leaky-suite abstract](https://arxiv.org/abs/2607.11022) reports little
held-out capability change under a matched hardening experiment despite corrected
false reward. Its full-text extraction was incomplete; treat it as limited primary
abstract evidence rather than independently reproduced causal closure.

[Small-model coding RL](https://arxiv.org/abs/2605.30478) reports lint-only reward
failure and external test evaluation; its training used 24GB RTX3090 hardware.
[StepCoder](https://arxiv.org/abs/2402.01391) investigates curriculum/execution
feedback. [Anthropic](https://www.anthropic.com/research/emergent-misalignment-reward-hacking)
studies behavior transfer from deliberately vulnerable coding rewards. None of
these establishes local model quality from reward, lint or challenge coverage alone.

## Case-study interpretation

Coinbase's [three-part series](https://www.coinbase.com/blog/part-one-how-coinbase-built-evaluated-and-post-trained-a-fraud-agent)
contains an online incremental-review comparison, historical LLM-version replay,
and adapted-model/serving comparisons. Their authority boundary, pre-intervention
cohort and lifecycle discipline transfer well. Missing matched classifier alternatives,
private data and incomplete training/split disclosure limit architectural conclusions.
The user-supplied [X thread](https://x.com/brian_armstrong/status/2109412046244913643)
provided orientation; only partial replies were extracted. No assertion is
attributed to unseen commenters.

## Operational handoff

`unsloth` owns the researched local SFT/RL execution guides and tested offline
provenance/verifier-receipt helper. `llama-cpp`/`vllm` own serving. Official
[TRL SFT](https://huggingface.co/docs/trl/sft_trainer),
[GRPO](https://huggingface.co/docs/trl/grpo_trainer),
[PEFT](https://huggingface.co/docs/peft/developer_guides/lora) and
[SkyRL](https://docs.skyrl.ai/docs/tutorials/new_env) contracts must be matched
to the installed build. This source review did not run a new GPU experiment.

## Task-specific inference lead

[Neal Patel's CDM announcement](https://x.com/neal_k_patel/status/2109978626124898587)
led to official [classification](https://docs.scaledown.ai/api-reference/classify-overview),
[extraction](https://docs.scaledown.ai/api-reference/extract-overview) and
[summarization](https://docs.scaledown.ai/api-reference/summarize-overview) contracts.
They support concrete task-interface comparisons. A provider
[listing](https://vercel.com/ai-gateway/models/providers/scaledown) supports catalog
presence only. Calibration, speed/cost, context, DecisionBench and underlying
non-autoregressive architecture remain vendor claims without local or independent
verification here. The home page failed extraction; official task docs were retained.
