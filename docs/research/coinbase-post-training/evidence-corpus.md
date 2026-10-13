# Source-level evidence corpus

Accessed 2026-10-13 through the Hermes-configured GPU-host GroktoCrawl API.
Original extraction records; empirical findings are author-reported unless explicitly tested locally.
Snapshots were hashed and retained locally; this package publishes original notes and provenance rather than full third-party publications.

## patel-concept: CDM announcement

[vendor social announcement](https://x.com/neal_k_patel/status/2109978626124898587?s=20) — retained; locator: Post and author follow-up.

Proposes task-specific classification, extraction and summarization instead of using a general-purpose generator for every task.

Limits: Claimed calibration, context, speed/cost and benchmark numbers are not independently verified; underlying non-autoregressive mechanism is not established by this post.

Snapshot SHA-256: `c1652332011ecdeaa9bfadb7a27fff696a151a15399ffb3c29367c120dab8c82`.

## scaledown-classify: ScaleDown classify contract

[official vendor documentation](https://docs.scaledown.ai/api-reference/classify-overview) — retained; locator: Classify overview; API comparison; scores.

Rubric-defined labels return softmax-normalized scores; Jev-compatible Decisions API runs on the same scoring model.

Limits: Shape compatibility does not preserve semantics/calibration/thresholds; no provider calls or local weight training validated.

Snapshot SHA-256: `cc615675ed3d2c06dc4ec5df3bde7cedccbc8e5871dd0b42731487e7f3c6948c`.

## scaledown-extract: ScaleDown extract contract

[official vendor documentation](https://docs.scaledown.ai/api-reference/extract-overview) — retained; locator: Overview; classification keys; offsets.

Described entities return text spans, offsets, scores and context; categorical schema keys route to classification.

Limits: Evaluate source agreement and missing sensitive entities, not just JSON; scores do not independently validate extraction.

Snapshot SHA-256: `711463be256924881509cba3e0d1f5fc79be6b13a62345cffb3136d9db3cc68c`.

## scaledown-summarize: ScaleDown summarize contract

[official vendor documentation](https://docs.scaledown.ai/api-reference/summarize-overview) — retained; locator: Overview; abstractive versus extractive.

Summarization is documented as an abstractive rewrite with fixed/tuned sampling parameters and compression/latency metadata.

Limits: Output contract does not prove non-autoregressive architecture or factual faithfulness. Downstream retained-task quality must be tested.

Snapshot SHA-256: `85fb4611c28e4756a1a87bec62127a1bf04605a7e21066f05f4d1c09a36ba0df`.

## scaledown-provider: Vercel ScaleDown catalog

[provider listing](https://vercel.com/ai-gateway/models/providers/scaledown) — retained; locator: Provider models listing.

Corroborates task-specific product catalog presence in a provider gateway.

Limits: Listing does not prove calibration, quality, local availability or runtime compatibility.

Snapshot SHA-256: `f7eb255afbd344c7d1f945521ca9e72313a3c51297de3c49e67ec0896d16b63f`.

## coinbase-1: Coinbase Part One

[industry case study](https://www.coinbase.com/blog/part-one-how-coinbase-built-evaluated-and-post-trained-a-fraud-agent?country=NZ&currency=NZD&japan_bespoke_content=false&logged_in=false&mobile=false&null=) — retained; locator: Solution; online experiment; tradeoffs.

Contextual review downstream of rules/ML can veto an otherwise allowed transaction, but cannot reverse an upstream block. The online experiment tests adding this selective review layer.

Limits: No matched zero-shot/classifier-with-equivalent-context comparison; proprietary outcomes cannot be independently reproduced.

Snapshot SHA-256: `ba9881cedab362e5a60e331ae6f4070c01dff0a9a82ce8710660214be61fbd05`.

## coinbase-2: Coinbase Part Two

[industry case study](https://www.coinbase.com/blog/part-two-owning-intelligence-series) — retained; locator: Benchmark; results; model selection.

A pre-rollout historical cohort avoids agent-intervention bias. Fixed-policy replay compares LLM versions with precision, recall, F1 and value-weighted recall. Newer versions do not consistently win.

Limits: Historical replay and sampled legitimate prevalence are different from live impact; version changes do not identify training causes.

Snapshot SHA-256: `152c174c68fcb90a02dab4f05a35d60682d415551a23fabba243eb80a27338f3`.

## coinbase-3: Coinbase Part Three

[industry case study](https://www.coinbase.com/blog/part-three-owning-intelligence-series) — retained; locator: RLVR; training; results; serving.

LoRA GRPO with deterministic balanced outcome rewards adapts Qwen3.5-9B. Reported F1 gain over Opus 4.5 is 9.6 percentage points. Training uses a 96GB GPU; quality and online latency are separate evaluations.

Limits: No traditional/zero-shot classifier comparison establishes architecture optimality. Cost excludes an independently verified full lifecycle and does not transfer to our GPU.

Snapshot SHA-256: `8ce1fffc9478720ebd857e7131d01841850c4a6cc687a421b8f69e74725f2e56`.

## lora: LoRA: Low-Rank Adaptation

[research paper, partial extraction](https://arxiv.org/html/2106.09685) — retained; locator: Empirical analysis of adaptation matrices.

The retrieved analysis examines trainable matrix selection and rank structure of downstream weight changes. Low-rank updates reduce trainable parameters.

Limits: Extraction starts in empirical analysis and omits introduction/abstract; use PEFT documentation for the implementation contract. Hardware savings are configuration-specific.

Snapshot SHA-256: `564fffdfe911297024986f47529c09810960f3953b7466889b02a59fd151a68a`.

## qlora: QLoRA: Efficient Finetuning of Quantized LLMs

[research paper](https://arxiv.org/html/2305.14314) — retained; locator: Method; paged optimizers; limitations.

Quantized frozen weights are dequantized for computation while adapters train; NF4, double quantization and paged optimizers address different memory components. Paging may move optimizer state to host RAM.

Limits: Published large-model memory results are not RL rollout-memory budgets. Authors note paged-optimizer slowdowns are not fully characterized. All-VRAM requirements need separate verification.

Snapshot SHA-256: `0a5c4cef95b339e816b5750478d71bbedcb86bff94e2a76c62606ba04e4950da`.

## sft-rl-generalization: SFT Memorizes, RL Generalizes

[comparative research](https://arxiv.org/html/2501.17161) — retained; locator: Abstract; task definitions; generalization experiments.

In arithmetic-rule and visual-navigation tasks, outcome-based RL generalizes to tested variants while SFT stabilizes output format.

Limits: The title is not a universal law: domains, backbone, data, training budget and sequential-revision harness differ from repository coding.

Snapshot SHA-256: `a6ad5294d927165b1b449a612998a19cca998b3c31c0b682c831ee344e8d3a32`.

## rlvr-limits: RLVR capability limits

[comparative research, partial extraction](https://arxiv.org/html/2504.13837) — retained; locator: Introduction; pass@k analysis.

Within the studied model/task configurations, RLVR improves low-k success but base-model coverage can exceed it at large k. Sampling efficiency and diversity are distinct outcomes.

Limits: High-k sampling is a proxy, not a proof of a universal capability ceiling. Extracted HTML omits front matter; abstract is retained separately.

Snapshot SHA-256: `aee7e981223cfe50add07be10b0e0910901abbbdc150181cc9a0316d2c8d632c`.

## rlvr-limits-abstract: RLVR limits author abstract

[primary abstract](https://arxiv.org/abs/2504.13837) — retained; locator: Abstract.

Confirms the authors frame their results as limits to gains beyond the base model and compare sampling behavior.

Limits: Same study as rlvr-limits, not independent corroboration.

Snapshot SHA-256: `93fe272214642c4640ef227f2fb4c4de868bd6b9fca5b0b04f863711244d6e39`.

## rlvr-reasoning: RLVR implicitly incentivizes correct reasoning

[comparative research](https://arxiv.org/html/2506.14245v2) — retained; locator: Abstract; CoT-Pass@K; judge methodology.

The authors challenge a pure sampling-efficiency explanation and introduce reasoning-aware CoT-Pass@K alongside answer metrics.

Limits: Reasoning correctness uses model judges; different training conditions and metrics complicate a direct replication of the limits study. Do not turn this into a promise of reasoning gains.

Snapshot SHA-256: `8e6b9dae64ab38dd497fa313ab064f86473eddb75c7fc02cd9fee8c51af70ec6`.

## swe-gym: SWE-Gym

[research and dataset](https://arxiv.org/html/2412.21139v2) — retained; locator: Abstract; dataset construction; verifier scaling.

Runnable repository environments, tests and agent trajectories support training and learned trajectory selection. Repository separation is part of avoiding fine-tune contamination.

Limits: Combined verifier/inference scaling is a different system from one attempt. Public benchmark pretraining exposure and private-task transfer remain unresolved.

Snapshot SHA-256: `ec2e5b658e73cad29cb92eb48c1284827e5dc78a266fcbcad2e276c63fbf1865`.

## swe-smith: SWE-smith project

[author project summary](https://swesmith.com/) — retained; locator: Project overview.

Synthesizes runnable broken-code tasks across many Python repositories and releases task/trajectory/model artifacts.

Limits: Project headline does not audit every synthetic task or establish local model size feasibility; use paper/code records below.

Snapshot SHA-256: `04087487481e69ded8a441685b0728dfb586dd9da954e80ba5823f51d986acb5`.

## swe-smith-paper: SWE-smith paper

[research and dataset](https://arxiv.org/html/2504.21798) — retained; locator: Abstract; task-generation and evaluation method.

Generates code changes that break repository tests, constructs execution environments and trains a software agent. The paper reports a 32B single-attempt result.

Limits: Synthetic test-breaking bugs may not represent real user issues; task provenance, filtering and same-repository leakage require explicit review.

Snapshot SHA-256: `548bbc12a88114e2bff75fc84ec64ca28476487a69aa5ee8e5298f562871d7eb`.

## swe-smith-code: SWE-smith repository

[author implementation documentation](https://github.com/SWE-bench/SWE-smith) — retained; locator: README and release links.

Published repository supplies collection, environment and training-data tooling with an explicit license.

Limits: GroktoCrawl returned the README, not every executable file or an immutable source checkout; pin and inspect code before running.

Snapshot SHA-256: `2274bc854bed3a75715a1c73d24d72b1c2a527deb7c37b1cb3f950d0d5e57958`.

## deepswe: DeepSWE author report

[industry training report](https://www.together.ai/blog/deepswe) — retained; locator: Recipe; resource statement; test-time scaling.

Reports RL-only agent training from Qwen3-32B over runnable tasks, with separate pass@1, pass@16 and selected/scaled scores. Training uses 64 H100 GPUs over six days.

Limits: Substantial training resources; agent harness and inference selection contribute to results. Not a recipe demonstrated on a consumer GPU.

Snapshot SHA-256: `b1b97fc3fcea7b37c6715f2dc01230c77e7804188d1ed5111447ef02386543a0`.

## evalplus: EvalPlus project

[author project summary](https://evalplus.github.io/) — retained; locator: Project overview.

Introduces expanded tests for functional evaluation of generated code.

Limits: Landing page alone is limited evidence; paper and code are retained separately.

Snapshot SHA-256: `5dc80137e33589b9b7f9316388b18f68250912e80ee49d1caa47a51dec65db88`.

## evalplus-paper: EvalPlus paper

[empirical evaluation research](https://arxiv.org/html/2305.01210) — retained; locator: Abstract; test generation; evaluation.

Expanded HumanEval tests reveal wrong solutions that original tests accepted and can change model rankings. Test-suite strength changes the measured outcome.

Limits: More tests do not automatically constitute an independent oracle. Generated augmentations must accept reference solutions and be reviewed for intended behavior.

Snapshot SHA-256: `df0e06ca4d6b9a830831543b53a04459b179bb1742b953c4b8af44948414499e`.

## evalplus-code: EvalPlus repository

[author implementation documentation](https://github.com/evalplus/evalplus) — retained; locator: README; release change notes.

README exposes evaluation inputs, dataset/version selection, conservative timeouts and changes to tests/contracts.

Limits: README snapshot is not executed verification or a security sandbox. Dataset upgrades must be pinned; do not mix historical scores.

Snapshot SHA-256: `acf1e0ebd641fad83a9863673cc13ec0754ba8d7aea2be4cf13aab874aa00f4e`.

## lora-forgetting: LoRA Learns Less and Forgets Less

[comparative research](https://arxiv.org/html/2405.09673v2) — retained; locator: Abstract; experiments; throughput/memory appendix.

Reports adaptation/retention tradeoffs in code/math continued pretraining and instruction tuning. Rank, learning rate and target modules materially affect performance.

Limits: Less forgetting does not mean no forgetting; settings and data regimes are distinct. Larger rank can improve instruction tuning but adds cost.

Snapshot SHA-256: `319688f51dda5b3d19a7ddf6eef411f395189b2ee84837f822e551b787f7cc23`.

## verifier-audit: Auditing Reward Hackability

[2026 preprint](https://arxiv.org/html/2606.16062v1) — retained; locator: Abstract; Docker verification; gold-sanity gate.

Selected code tasks admit wrong patches; generated extra tests can also fail trusted gold solutions. A gold-sanity check is part of the proposed hardening loop.

Limits: Small selected samples and single-study claims are not population hackability estimates. This investigation did not reproduce Docker experiments.

Snapshot SHA-256: `d8d1707b4d0efb250e4944f8642c21207620fd306e38f30e67489e6e100145b0`.

## leaky-reward: Leaky reward suite full-text attempt

[partial extraction, excluded for whole-paper claims](https://arxiv.org/html/2607.11022) — excluded; locator: Extracted tables only.

Extraction contains isolated tables without the surrounding argument.

Limits: Cannot treat this as a complete paper reading. Abstract retained separately; whole-paper causal-method details remain unresolved.

Snapshot SHA-256: `17712a47510d9993217738e2bc74fe0af721a1ef2f4f304fe1db52502cfd4b7f`.

## leaky-reward-abstract: Leaky reward suite abstract

[2026 preregistered-study abstract](https://arxiv.org/abs/2607.11022) — retained; locator: Abstract.

Authors report matched-task/seed/compute comparisons between original and hardened reward suites. Hardening removes false reward while average held-out capability changes little in their setting.

Limits: Abstract-only evidence; no independently reproduced effect. False-positive mechanisms and study horizons cannot be generalized to every RL system.

Snapshot SHA-256: `f637cdfe4248b11aa7345b8ffd12a3676d322781462fcfa22ecc64f107ff8e8a`.

## small-code-rl: Small models with verification feedback

[2026 empirical preprint](https://arxiv.org/html/2605.30478v1) — retained; locator: Abstract; reward variants; setup; external validation; limitations.

Studies Qwen3-0.6B/Llama3.2-1B code RL with test and lint reward variants. Lint-only shaping can shorten outputs without correctness gains; independent EvalPlus tests assess transfer. Training uses RTX3090 24GB and evaluation RTX5060Ti 16GB.

Limits: Short Python tasks, few model families and reward choices; does not establish repository-agent performance or our 5070Ti RL stack compatibility.

Snapshot SHA-256: `86c7a508ef8e434b4b35ae679c2f24a6db6ad790b2d341ee1d8a6d583ab10d2d`.

## stepcoder: StepCoder

[coding RL research](https://arxiv.org/html/2402.01391) — retained; locator: Abstract; curriculum and fine-grained optimization.

Exploration is difficult for long code sequences. Curriculum over completion subtasks and masking unexecuted segments are studied with reviewed test data.

Limits: Specific algorithm and compiler environment are not automatic features of a GRPO callback or our SFT script.

Snapshot SHA-256: `ab03e38e2d0b913f3dac5810f6f2c0d8e43cf8d13c2466c4e2403c4305a3106c`.

## anthropic-reward: Natural emergent misalignment from reward hacking

[author research report](https://www.anthropic.com/research/emergent-misalignment-reward-hacking) — retained; locator: Experimental setup; consequences; mitigation discussion.

Deliberately vulnerable production-style coding environments and reward-hacking knowledge are used to study behavior transfer beyond the reward task. Chat-context safety results do not establish agent-context behavior.

Limits: Selected vulnerable setup; incidence cannot be extrapolated to all local adapters. Report is primary author evidence but experiments are not independently reproduced here.

Snapshot SHA-256: `b5ef17636db4549e636614b0be0fa496eddb48855fb84a86cc4272ecce315548`.

## trl-sft: TRL SFT Trainer

[official documentation](https://huggingface.co/docs/trl/sft_trainer) — retained; locator: Dataset formats; loss; SFTConfig.

Dataset form, completion/assistant loss, tokenizer/template masks, packing and trainer configuration are separate compatibility concerns.

Limits: Retrieved rolling docs resolve v1.15.0; installed baseline was a different version. Verify signatures and actual collated labels before using.

Snapshot SHA-256: `b4e20f119022efe2215fab23c1ca5ffcfb7e0d059a977e173039801d80d9246e`.

## trl-grpo: TRL GRPO Trainer

[official documentation](https://huggingface.co/docs/trl/grpo_trainer) — retained; locator: Algorithm; reward hooks; metrics; GRPOConfig.

Group-relative rewards, normalization, generation grouping, KL/loss choices and logged reward statistics define the actual learning loop.

Limits: Rolling v1.15.0 documentation is not proof of installed compatibility. Zero-variance task rewards and component domination require diagnosis.

Snapshot SHA-256: `c91c72ed92f804d78685a27e27c926caf4dc7f2335a79b2f9381e3c9144b0d20`.

## unsloth-rl: Unsloth RL guide

[official vendor documentation](https://docs.unsloth.ai/get-started/reinforcement-learning-rl-guide) — retained; locator: Model routes; verifier discussion; memory examples.

Provides model-specific RL notebook routes and distinguishes rewards from correctness verification; supported generation backends vary by model.

Limits: Vendor minimum VRAM/quality assertions are not measured workload guarantees. General background claims about always improving with time are not acceptance criteria.

Snapshot SHA-256: `65c17125237aafcfb0cb7ba9cc7120f98c0e4a54c7c6358bb550459adb4464ff`.

## unsloth-memory: Unsloth long-context GRPO

[vendor benchmark and design report](https://unsloth.ai/blog/grpo) — retained; locator: Memory derivation; benchmarks.

Explains memory savings around logits, rollout engine state and longer-context training configurations.

Limits: Vendor comparisons depend on configuration and versions; measure representative prompts and all-device peak before promising feasibility.

Snapshot SHA-256: `6d8db35d675c8415eb2006a6a27211c3ecac93ed6944120f0bc7be8e894c212d`.

## peft-merge: PEFT LoRA developer guide

[official documentation](https://huggingface.co/docs/peft/developer_guides/lora) — retained; locator: Merge operations; quantization; adapter settings.

Adapter loading/merging, target modules and quantized configurations have distinct contracts. merge_and_unload creates a merged model without active PEFT switching.

Limits: Merged/quantized numerical parity and runtime behavior still need tests; documentation is not a local experiment.

Snapshot SHA-256: `0ce62bb513a84186b8e11cf95662fd05b7874f20038e8510dbc2c46e03c08757`.

## vllm-lora: vLLM LoRA support

[official developer-preview documentation](https://docs.vllm.ai/en/latest/features/lora/) — retained; locator: Support boundary; per-request example.

Models must implement the LoRA support interface. Request-level adapter use requires explicit enablement and model/adapter mapping.

Limits: Fetched latest developer-preview documentation; select stable/version-matched docs for deployment. Local GPU-only placement and parity are not implied.

Snapshot SHA-256: `3008fbd24b613c513a9e19af76f6de0f5d80fc512228fddda2c83d5bb19bc03e`.

## skyrl-environment: SkyRL custom environment

[official documentation](https://docs.skyrl.ai/docs/tutorials/new_env) — retained; locator: BaseTextEnv; single/multi-turn examples; registration.

Environment step returns observations, numerical reward, termination and metadata, with registration and data-preparation steps.

Limits: A SkyRL environment is not interchangeable with a TRL reward function. Runtime lifecycle must be tested before a tool skill claims operational support.

Snapshot SHA-256: `11edd1bbce9b8a276972e40f198afb63a59f6686cebbbdb734fa419733857fc5`.

## skyrl-megatron: SkyRL Megatron backend

[official documentation](https://docs.skyrl.ai/docs/examples/megatron) — retained; locator: Backend selection; parallelism; checkpoint links.

Distributed backend separates data, tensor, pipeline, context and expert parallelism and model-specific checkpoint behavior.

Limits: Backend presence does not prove a specific quantized adapter/model combination or that GPUs automatically pool memory.

Snapshot SHA-256: `069a831a25cfa8bd659be6e6fca26e39174f89549e7efc576e14e54da4ea3a61`.

## swebench-evaluation: SWE-bench evaluation guide

[official benchmark documentation](https://www.swebench.com/SWE-bench/guides/evaluation/) — retained; locator: Overview; evaluation entrypoint; environment setup.

Patches are applied to pinned repository environments and verified through Docker tests, with explicit prediction and run inputs.

Limits: Environment/harness completion and test adequacy must be inspected; Docker alone does not guarantee confinement or real-world representativeness.

Snapshot SHA-256: `6bbcf48f6ffacaf13cff2bb9a078eccbb96de113f0de8b6f0188ef3ce2a098c8`.

## armstrong-thread: Brian Armstrong X thread

[orientation, partial reply coverage](https://x.com/brian_armstrong/status/2109412046244913643?s=20) — retained; locator: Post; visible follow-up/reply.

Author promotes specialized open-weight models and an internal fine-tune-and-serve skill. Scrape exposes the post, author follow-up and a small visible reply subset.

Limits: Classifier critiques reported by the user are not visible in this retrieved subset; no commenter attribution or complete-thread claim is made.

Snapshot SHA-256: `28125d98831456181bc6df753f1dd5d0b1aa0a7d1549a01f62cb2ea2c171de2a`.

## trees-tabular: Why trees outperform deep learning on tabular data

[comparative research](https://arxiv.org/html/2207.08815) — retained; locator: Abstract; benchmark methodology; inductive-bias analysis.

Benchmarks many learners/hyperparameters on medium-sized tabular datasets and finds strong tree baselines with favorable speed.

Limits: 2022 settings, not a comparison with all modern tabular/sequence foundation models or Coinbase context. Baseline recommendation, not universal superiority.

Snapshot SHA-256: `044aae20a92ad2c51e10766ff8678ef9829bfb755d6a12c6da4b865f873f83cb`.

## zero-shot-nli: Sentence-BERT mistaken discovery target

[excluded wrong-source match](https://arxiv.org/abs/1908.10084) — excluded; locator: Retrieved title/abstract.

The guessed identifier returned Sentence-BERT, not the intended zero-shot classification paper.

Limits: Excluded from zero-shot entailment claims. Correct ACL paper was found through GroktoCrawl search.

Snapshot SHA-256: `e86c3b8a87fab7d92a0a6d7598057caa3012d878ccd4a4381b4d123bfeebc854`.

## zero-shot-benchmark: Benchmarking Zero-shot Text Classification

[peer-reviewed primary abstract](https://aclanthology.org/D19-1404/) — retained; locator: ACL abstract/citation.

Yin, Hay and Roth define label-unseen evaluation and an entailment framing across topic, emotion and situation labels.

Limits: Retained ACL record includes author abstract/citation, not full PDF. Text-label generalization is different from calibrated numerical fraud prediction.

Snapshot SHA-256: `33ab017abe43f5e1650fcf488ad91c276397d871f20f60428b4bdc1c5ec39ccb`.

## hf-zero-shot: Transformers zero-shot classification pipeline

[official documentation](https://huggingface.co/docs/transformers/main_classes/pipelines#transformers.ZeroShotClassificationPipeline) — retained; locator: ZeroShotClassificationPipeline.

NLI premises/hypotheses are built per candidate label. Single-label scores normalize across labels; multi-label scores compare entailment/contradiction per label.

Limits: Labels/template, truncation and candidate count change behavior/cost. Scores are not automatically calibrated fraud probabilities; docs resolve v5.19.0.

Snapshot SHA-256: `5d4cb4a7278352f9606c458b16ecc4f3d4ec9bcc37515d141a3935f1813816e7`.

## booking-fraud: Tabular transformers at Booking.com

[production fraud research, partial extraction](https://arxiv.org/html/2405.13692v1) — retained; locator: Problem definition; results; online evaluation.

Compares supervised/self-supervised tabular transformers and GBDT fraud models, reporting business-metric gains in its production setup.

Limits: Extraction starts in problem/method sections; retain author abstract separately. Private data and labels, feature parity and business metric prevent direct transfer to Coinbase.

Snapshot SHA-256: `13e9bb989aee6929dc6c94180a19dc32ddb47d761b6f527e9f142dc677cf1d93`.

## tabpfn-author: TabPFN author repository

[official implementation documentation](https://github.com/PriorLabs/TabPFN) — retained; locator: README architecture; quickstart; resource/operation boundaries.

A pretrained tabular foundation model offers a distinct non-generative prediction alternative with version-specific input/hardware limits.

Limits: README rather than executed model/paper evidence. Code and weight licensing/telemetry and local versus hosted paths need separate review; no superiority claim retained.

Snapshot SHA-256: `ff373b05c1c1af5e22cfae782bfe000a04fe15a62a5d4e297fa080394b26c5d4`.
