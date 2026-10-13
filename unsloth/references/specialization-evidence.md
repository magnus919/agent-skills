# Specialization source ledger

Accessed 2026-10-13 with GroktoCrawl on the Hermes-configured GPU-host API.
These are researched capabilities and findings, not new local GPU validations.
The tracked research package at repository `docs/research/coinbase-post-training/`
contains source-level extraction notes, snapshot hashes, search/exclusion log and
synthesis. Original whole-publication snapshots remain local; this ledger routes
to the primary sources rather than redistributing them.

## Data and task evaluation

| Source | Material contribution | Boundary |
|---|---|---|
| [SWE-Gym](https://arxiv.org/abs/2412.21139) | Runnable repository tasks, agent trajectories and verifier-based selection | Selection/scaling and single-attempt results are distinct |
| [SWE-smith](https://arxiv.org/abs/2504.21798), [author code](https://github.com/SWE-bench/SWE-smith) | Synthetic broken-code tasks, environments and trajectory generation | Generated bugs must resemble the intended task; pin code before running |
| [EvalPlus](https://arxiv.org/abs/2305.01210), [author code](https://github.com/evalplus/evalplus) | Stronger tests detect false accepts and change rankings | Augmented tests need reference acceptance and near-miss rejection |
| [SWE-bench evaluation](https://www.swebench.com/SWE-bench/guides/evaluation/) | Reproducible patch/environment/test inputs | Container presence does not prove task validity or confinement |

## Adaptation choice and failure modes

| Source | Material contribution | Boundary |
|---|---|---|
| [SFT vs RL](https://arxiv.org/abs/2501.17161) | Rule/navigation generalization experiments; SFT format stabilization | Not a universal comparison on coding or fraud |
| [RLVR limits](https://arxiv.org/abs/2504.13837) | Low-k efficiency versus high-k coverage | Same task/budget needed; empirical conditions limit interpretation |
| [RLVR reasoning](https://arxiv.org/abs/2506.14245) | Challenges pure efficiency explanation with reasoning-aware metrics | LLM reasoning judges add uncertainty; preserve disagreement |
| [LoRA retention](https://arxiv.org/abs/2405.09673) | Learning/forgetting tradeoffs; rank, modules and learning-rate sensitivity | Fewer updates do not guarantee unchanged general behavior |
| [Small-model coding RL](https://arxiv.org/abs/2605.30478) | Test/lint reward ablations and external tests | Short Python tasks; training 24GB GPU, not our executed RL path |
| [StepCoder](https://arxiv.org/abs/2402.01391) | Curriculum and execution-aware optimization for sparse code rewards | Different algorithm/environment from a generic GRPO callback |
| [DeepSWE](https://www.together.ai/blog/deepswe) | RL agent recipe, substantial GPU scale and test-time selection | 32B/64-H100 report is not consumer-GPU evidence |
| [Verifier audit](https://arxiv.org/abs/2606.16062) | False acceptance and generated-test gold-sanity failure | Selected sample; numerical prevalence not generalized |
| [Leaky reward study](https://arxiv.org/abs/2607.11022) | Author abstract reports little capability benefit from hardened tests despite reward correction | Full-text extraction incomplete; abstract-only result not reproduced |
| [Anthropic reward hacking](https://www.anthropic.com/research/emergent-misalignment-reward-hacking) | Selected vulnerable coding training can transfer harmful behavior | No universal incidence claim; test actual agent contexts |

## Operational contracts

- [TRL SFT](https://huggingface.co/docs/trl/sft_trainer) and
  [GRPO](https://huggingface.co/docs/trl/grpo_trainer): fetched docs resolve
  v1.15.0. Our historical validated SFT stack used a different version; inspect
  signatures and model-specific recipes before new execution.
- [Unsloth RL](https://docs.unsloth.ai/get-started/reinforcement-learning-rl-guide)
  and [memory design](https://unsloth.ai/blog/grpo): vendor recipe/memory leads;
  actual model, length, grouping and backend determine feasibility.
- [QLoRA](https://arxiv.org/abs/2305.14314): NF4 and adapter computation differ;
  paged optimizers can use host RAM, relevant to GPU-only requirements.
- [PEFT LoRA](https://huggingface.co/docs/peft/developer_guides/lora): merge/load
  semantics and quantized limitations; still test a fresh delivered artifact.
- [vLLM adapters](https://docs.vllm.ai/en/latest/features/lora/): fetched latest
  developer-preview docs, not a stable-version deployment promise.
- [SkyRL environment](https://docs.skyrl.ai/docs/tutorials/new_env) and
  [Megatron backend](https://docs.skyrl.ai/docs/examples/megatron): distinct
  environment/parallelism contracts. No named SkyRL tool skill/runtime validated
  in this catalog enrichment.

## Orientation and alternatives

Coinbase [Part One](https://www.coinbase.com/blog/part-one-how-coinbase-built-evaluated-and-post-trained-a-fraud-agent),
[Part Two](https://www.coinbase.com/blog/part-two-owning-intelligence-series) and
[Part Three](https://www.coinbase.com/blog/part-three-owning-intelligence-series)
provide a motivating case. Proprietary results compare contextual review and LLM
candidates; they do not establish superiority over all simpler classifiers.
The [linked X thread](https://x.com/brian_armstrong/status/2109412046244913643)
was partially visible; classifier comments described by the user were not captured
and are not attributed as retrieved evidence.

For classifier-versus-generation decisions, read `ml-engineering` and its
specialization decision/evidence guides. A classifier may preserve required task
behavior at lower cost; a zero-shot text classifier is not automatically a
calibrated predictor over structured transaction sequences.
