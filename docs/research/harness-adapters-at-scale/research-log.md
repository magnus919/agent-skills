# Harness-adapter research log

Sources accessed November 28, 2026. [Research question and catalog assessment](research-brief.md)

## Retrieval and decisions

| Pass | Method | Outcome |
|---|---|---|
| Article | Read the Hugging Face article and followed its first-party links | Extracted task qualification, training setup, paired comparisons, merge selection, transfer and interpretation boundaries |
| Corroboration | Read Tasksmith, OpenEnv, prior study, Agent Lightning and SkyRL materials | Checked executable controls and how production-style harnesses interact with the training system |
| Counterevidence | Checked the released model card, AutomationBench, thinking-leakage paper and merge papers | Bounded transfer, comparison denominators, inference effort and tuning effects |
| Catalog | Searched and read local Git files. Compared checkout `c50a9c5e97efa0b5f4c16ba9570d4a7e3df4095e` to remote main through the GitHub connector after direct Git DNS failed. | Main was one release commit ahead, with changes confined to the changelog and release manifest. The relevant skill files were current. Reviewed adjacent QA, verification, production and cost guidance for overlap. An issue search surfaced #104, which describes an evaluation runner interface. That interface serves a different purpose from the learned model adapter studied here. |

## Source records

### S1 · Hugging Face scale study

The authors used Qwen3.8-27B LoRA adapters with Pi 1.5.2, OpenCode 2.2.7 and Hermes Agent v0.22.6. The evaluation used frozen budgets and harness defaults, including different context-compaction behavior across harnesses. These settings permit within-harness base/adapter comparisons and leave cross-harness rankings confounded by configuration.

The task pipeline screened rights, duplicate cases, benchmark tasks and benchmark repositories, then tested reference reward, no-op separation, negative controls and repeatability. The authors report 858 of 1,127 Hub candidates passed validation. They report 171 mixed-outcome tasks among 442 scored in the difficulty screen. These counts describe separate stages. The short training ablation used 32 tasks per arm and up to 50 steps. Treat it as an exploratory pilot. Keep validation failure receipts, particularly infrastructure failures, and document training versus checkpoint selection versus final evaluation.

The authors report a Pi Terminal-Bench 2.1 gain of 16.3 percentage points, with 16 newly solved and two lost on their reported comparison. Their paired-intersection merge table uses different denominators from the headline rows. Efficiency on jointly solved cases describes work conditional on joint success. It leaves total cost of failures, retries, supervision and rework to an operational measurement. Their AutomationBench comparison simultaneously changes harness and domain and shows no clear broad positive transfer. The Hermes adapter's reported point estimate is lower than base by 5.3 points, with uncertainty.

The merged configuration improved the mean result but the Pi specialist retained a larger gain on both benchmarks with thinking disabled. The merge weight was selected using Terminal-Bench 2.1. The article's held-out wording therefore needs a distinction between held-out from training and held-out from selection. The authors' observations of pre-tool text with thinking disabled motivate a control, with the underlying mechanism unresolved in this experiment. Fewer rule-based blocks describe detector activity and support a hypothesis about behavior within its coverage. [Scale study](https://huggingface.co/blog/harness-adapters-at-scale)

### S2 · Tasksmith acceptance and OpenEnv execution

Tasksmith checks that the baseline fails, the reference passes, a wrong solution fails, and a valid alternative passes. A blind rollout can legitimately fail and leave task validity intact. Evidence attaches to the evaluated bundle and affected checks run again after repair. These controls probe opposite grader errors. QA already covers the ordinary known-bad/corrected regression pair. Combining the broader controls into repeatable task admission belongs with the grader contract. OpenEnv documents a tool-bearing endpoint probe and serving-side token traces, which motivate a runtime preflight beyond a connectivity check. [Tasksmith acceptance](https://huggingface.github.io/Repo2RLEnv/pipelines/tasksmith/#acceptance) · [OpenEnv Harbor integration](https://openenv.github.io/OpenEnv/main/environments/harbor)

### S3 · Earlier Hugging Face harness studies

The same research program previously ran unmodified harnesses in separate sandboxes and used serving-time tokens directly. Its earlier efficiency reward applied on correct rollouts. This is a precedent for constraining an efficiency objective by correctness, with the coefficient specific to the study. The lineage supports feasibility and scope, with shared authorship and infrastructure reducing independence. [Earlier adapter report](https://huggingface.co/blog/harness-hub/harness-adapters) · [Multi-harness RL guide](https://huggingface.co/spaces/FineEnvs/multi-harness-rl)

### S4 · Agent Lightning

Independent authors analyze template non-compositionality, decode–retokenize drift, and inference-time output normalization. The original request history and actual token prefix can differ even when text looks the same. The paper describes preserving the actual sampled prompt when constructing training sequences. Its experiments report a gain in a separate Qwen3.5-9B SWE-bench Verified setting. This corroborates the architectural concern and supplies a distinct experiment, with separate conditions from Hugging Face's result. [Agent Lightning v1.0, sections 2 and 4](https://arxiv.org/html/2608.17528v1)

### S5 · SkyRL and Harbor

The authors use Harbor to run the same agent logic through trajectory generation, evaluation and training. The implementation report corroborates the feasibility of harness fidelity. Results from this implementation provide no direct comparison of the scale study's adapters. [SkyRL and Harbor](https://novasky-ai.notion.site/skyrl-harbor)

### S6 · Released model card

The released merged adapter card documents the artifact and paired evaluation slices. It reports six gains and six losses under Pi on SWE-bench Pro with thinking enabled, despite identical aggregate pass rates. Its context-window section reports no compaction for the card's runs. The scale article describes Pi's default compaction as affecting its evaluation. The exact relationship between those run settings remains unresolved here, so report the configuration with each result and avoid collapsing them into one protocol. Keep complete-roster results, common graded subsets and missing grades visible when reporting a portability claim. Preserve identity through merging and serving. The separate trajectory bucket was reachable as a publication surface. Individual runs and reward receipts were outside this assessment. [Super-adapter model card](https://huggingface.co/harness-hub/Qwen3.8-27B-super-adapter) · [Trajectory bucket](https://huggingface.co/buckets/harness-hub/harness-adapters-trajectories)

### S7 · Thinking leakage and workload transfer

The cited Thinking Leakage preprint studies smaller Qwen3 models on AIME, with behavioral measurements and activation interventions. It provides a reason to compare thinking settings and match budgets and an example of a stronger mechanism test. The coding agents in the scale article were outside that study. AutomationBench's first-party materials describe a distinct business automation benchmark. The combined harness and workload shift in the article cannot identify which caused the changed gains. [Thinking Leakage paper](https://arxiv.org/html/2610.14270v1) · [AutomationBench](https://github.com/zapier/AutomationBench)

### S8 · Merge literature

Task Arithmetic studies composing weight deltas. TIES studies parameter interference and sign conflict. KnOTS examines why LoRA alignment differs and proposes an SVD-based method. These motivate behavioral evaluation of a composed artifact and preserve a reason to test for interference. The scale study used rank concatenation and its own scale sweep. Its chosen weight is an empirical result for that setup. [Task Arithmetic](https://arxiv.org/abs/2212.04089) · [TIES-Merging](https://arxiv.org/abs/2306.01708) · [KnOTS](https://arxiv.org/abs/2410.19735)

## Exclusions and preservation

- The article's dataset name resolved in retrieval to the [published dataset landing page](https://huggingface.co/datasets/harness-hub/harness-adapters). The split viewer could not be retrieved in this review. Counts in the brief and log are article-reported. No row count or contamination audit was independently reconstructed.
- The detailed trainer configuration, batch sizing, optimizer settings, merge scaling defaults and hardware recipe were outside the adoption question. The cited papers inform principles rather than universal settings.
- Blocked-call rates and publicly posted anecdotes were excluded as evidence for production safety, autonomy, local hardware feasibility or causal attribution. Existing control-integrity and operating-economics guidance covers the relevant decision boundaries.
- No GPU reproduction, tool execution or production trial was performed. Evidence here consists of public documents and inspection of the current catalog.
- This log preserves source-level claims and exclusions. The linked brief preserves the recommendation, proposed acceptance evidence and follow-up questions. Neither changes a skill or a release gate.
