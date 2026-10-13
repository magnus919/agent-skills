# Source ledger and refresh guide

Retrieved 2026-10-12. All retained sources are upstream documentation or maintainer
repositories; they are mutable pages, not pinned release contracts. Documentation
was inspected through web retrieval. Source agreement within one vendor is not
independent validation. Short extractions below record the claim used, not copied
documentation. This original source review did not execute installation commands; the later
GPU baseline is recorded in [validated SFT](validated-sft.md).

| ID | Primary source | Retained finding / use |
|---|---|---|
| U01 | [Repository](https://github.com/unslothai/unsloth) | Project scope includes running and training models; avoid treating it as a model family. |
| U02 | [Documentation index](https://unsloth.ai/docs/llms.txt) | Discovery entrypoint for model-specific and less common tasks. An index listing alone is not verified recipe support. |
| U03 | [Installation overview](https://unsloth.ai/docs/get-started/install) | Select Core, Studio or Desktop before installation. |
| U04 | [pip/uv installation](https://unsloth.ai/docs/get-started/install/pip-install.md) | Separate Core and Studio installation paths; current Core uv bootstrap uses backend selection. |
| U05 | [Requirements](https://unsloth.ai/docs/get-started/fine-tuning-for-beginners/unsloth-requirements.md) | Product-specific requirements; listed VRAM values are minima, not capacity guarantees. |
| U06 | [Mac installation](https://unsloth.ai/docs/get-started/install/mac.md) | Mac UI workflows differ from Core CUDA recipes. |
| U07 | [Windows installation](https://unsloth.ai/docs/get-started/install/windows-installation) | Native Windows and alternative installation routes; vLLM-dependent tasks need their own OS compatibility check. |
| U08 | [AMD installation](https://unsloth.ai/docs/get-started/install/amd) | Dedicated AMD stack; verify current ROCm recipe instead of substituting CUDA packages. |
| U09 | [Intel installation](https://unsloth.ai/docs/get-started/install/intel) | Dedicated XPU installation with platform-specific dependencies. |
| U10 | [Studio start](https://unsloth.ai/docs/new/studio/start.md) | UI launch and workflow entrypoints; supports password setup and remote-access options. |
| U11 | [Dataset guide](https://unsloth.ai/docs/get-started/fine-tuning-llms-guide/datasets-guide) | Normalize conversation/instruction input intentionally. |
| U12 | [Chat templates](https://unsloth.ai/docs/basics/chat-templates.md) | Matching template and training/inference rendering matter; ShareGPT normalization is explicit. |
| U13 | [LoRA parameters](https://unsloth.ai/docs/get-started/fine-tuning-llms-guide/lora-hyperparameters-guide.md) | Rank, alpha, rate and training duration are starting choices to evaluate. |
| U14 | [Fine-tuning guide](https://unsloth.ai/docs/get-started/fine-tuning-llms-guide.md) | Overall training workflow and entrypoint to specialized recipes. |
| U15 | [TRL SFT Trainer](https://huggingface.co/docs/trl/sft_trainer) | Current SFT interfaces and constraints of assistant-only masking; match installed TRL. |
| U16 | [GRPO tutorial](https://unsloth.ai/docs/get-started/reinforcement-learning-rl-guide/tutorial-train-your-own-reasoning-model-with-grpo) | Use a task-matched online RL example. |
| U17 | [Advanced RL](https://unsloth.ai/docs/get-started/reinforcement-learning-rl-guide/advanced-rl-documentation.md) | Generation grouping and batching differ from simple SFT arithmetic. |
| U18 | [Preference training](https://unsloth.ai/docs/get-started/reinforcement-learning-rl-guide/preference-dpo-orpo-and-kto.md) | DPO/ORPO/KTO are separate objective/data paths. |
| U19 | [Vision](https://unsloth.ai/docs/basics/vision-fine-tuning.md) | Vision-specific loader/collator and response masking options. |
| U20 | [Speech](https://unsloth.ai/docs/basics/text-to-speech-tts-fine-tuning.md) | Audio-text preparation and model-specific speech paths. |
| U21 | [Continued pretraining](https://unsloth.ai/docs/basics/continued-pretraining.md) | Domain/language adaptation can include embeddings/output heads. |
| U22 | [Multi-GPU overview](https://unsloth.ai/docs/basics/multi-gpu-training-with-unsloth) | Manual integration and balanced placement are discussed separately from DDP. |
| U23 | [DDP](https://unsloth.ai/docs/basics/multi-gpu-training-with-unsloth/ddp) | `torchrun` workflow uses replicas; capacity is not a pooled-memory guarantee. |
| U24 | [Checkpoint recovery](https://unsloth.ai/docs/basics/finetuning-from-last-checkpoint) | Trainer resume requires saved checkpoint state. |
| U25 | [GGUF export](https://unsloth.ai/docs/basics/inference-and-deployment/saving-to-gguf.md) | Merge/export APIs, prompt/termination mismatch and save-memory issues. |
| U26 | [vLLM deployment](https://unsloth.ai/docs/basics/inference-and-deployment/vllm-guide.md) | Serving handoff; runtime compatibility still needs validation. |
| U27 | [Local API](https://unsloth.ai/docs/basics/api.md) | Authenticated endpoints, actual port/model discovery and tool controls. |
| U28 | [Studio security](https://unsloth.ai/docs/new/studio/security) | Refresh authentication and exposure rules for the installed build. |
| U29 | [Troubleshooting](https://unsloth.ai/docs/basics/troubleshooting-and-faqs.md) | Diagnose dependency, training and export issues; broad fixes need narrower local evidence. |
| U30 | [Docker installation](https://unsloth.ai/docs/get-started/install/docker) | Official container workflow; image and host GPU compatibility still require local validation. |

## Currency and disagreements

- Search results exposed older versions of installation pages; fresh `.md`
  retrieval showed Core/Studio/Desktop distinctions and newer Mac workflows.
  Prefer current official pages and installed source over cached summaries.
- U05's broad Mac support statement and its Core Apple-support caveat are not
  interchangeable. Record surface/backend/task; leave an untested tuple unknown.
- U22 combines available manual integrations with future-support wording. U23
  supplies a concrete DDP workflow; neither guarantees every sharded model path.
- U04 retains older Torch/CUDA extra examples alongside a newer uv path. Do not
  combine them into an invented install command. Pin a resolved working stack.
- U20 contains model-specific token/duration guidance and a contradictory comment
  beside `load_in_4bit=False`. This skill uses parameter semantics and avoids
  generalizing that example to all speech models.
- Marketing speed/memory multipliers and blanket model-support claims were not
  retained as guarantees. All performance conclusions need workload measurements.

## Refresh procedure

For a new run, consult U02 and open the exact product/backend/model guide. Record
the selected source revision, package versions and model revision in the run
record. Inspect the corresponding notebook at a fixed commit and installed
signatures. If documentation and source disagree, reproduce the smallest case and
state what remains unknown. Never silently broaden support from a page title.

The initial retrieval of several `.md` endpoints failed: multi-GPU, DDP,
checkpoint recovery and security succeeded at their non-`.md` canonical URLs.
An old running-and-saving-models documentation path failed and was replaced via U02
with U25/U26. A guessed Qwen3 Python notebook path failed; no recipe claim is based
on it. Direct shell HTTP was unavailable in the sandbox; web retrieval supplied
the retained sources. Docker installation was subsequently retrieved as U30;
no image was downloaded or executed.

## Evidence limits

The split audit, bounded diagnostics, comparison ladder and run record are this
skill's engineering synthesis. Offline script tests validate the helper contract,
not Unsloth training effectiveness. Evals are schema-valid scenarios only until
outputs are generated and reviewed. The later [validated SFT](validated-sft.md) establishes one GPU BF16 LoRA and
F16 GGUF smoke path. This source ledger alone establishes no runtime pass,
comparative speed benchmark or behavioral uplift.

## Desktop and decision research extension

The 2026-10-12 follow-up research package is preserved at
`docs/research/unsloth/desktop-research/` in the repository. The video is orientation
only; retained claims come from the sources below and pinned implementation
`b865e89586eb1af3185f416c448becd08f0e15d8`. Runtime execution of these new paths
was not performed. Docs/source disagreement is preserved in the relevant guide.

| ID | Primary source | Retained finding / use |
|---|---|---|
| U31 | [Decision training](https://unsloth.ai/docs/new/train-your-own-decision-model-with-unsloth) | Dedicated loader/trainer/head, calibration and distinct recipes. |
| U32 | [Decision serving](https://unsloth.ai/docs/models/decision-laya) | CPU defaults/fallback, confidence and option-length migration limits. |
| U33 | [Agent integration](https://unsloth.ai/docs/desktop/unsloth-start) | Agent commands, Codex GGUF requirement, lifecycle claim needing verification. |
| U34 | [Chat/tool execution](https://unsloth.ai/docs/new/studio/chat) | Search and built-in tools differ from offline inference. |
| U35 | [Sandboxing](https://unsloth.ai/docs/new/studio/sandboxing-in-unsloth) | OS/software modes; source reports network is not confined. |
| U36 | [MCP](https://unsloth.ai/docs/desktop/mcp) | Server setup/toggles and scoped tool-use checks. |
| U37 | [Data Recipes](https://unsloth.ai/docs/new/studio/data-recipe) | Provider selection, preview/build, tool profiles and validator limits. |
| U38 | [Image workflows](https://unsloth.ai/docs/desktop/diffusion-image) | Model-specific operation support, offload and settings/artifact records. |
| U39 | [Dynamic GGUF](https://unsloth.ai/docs/basics/dynamic-3.0-ggufs) | Distinct variants; next-token agreement differs from agent task quality. |
| U40 | [Dynamic NVFP4](https://unsloth.ai/docs/basics/dynamic-3.0-ggufs/nvfp4) | Separate Blackwell W4A4 path; do not generalize B200 benchmarks. |
| U41 | [Decision notebook](https://github.com/unslothai/notebooks/blob/87c1e89e973562a5fa94aaffe523e2da84f75785/nb/Qwen3_5_%284B%29-Decision.ipynb) | Inspected immutable workflow; installer is not fully pinned. |
| U42 | [Bug and fix](https://github.com/unslothai/unsloth/issues/13160) | Upstream compiler failure/fix; package inclusion not locally demonstrated. |
| U43 | [Original Clef](https://blog.cloudflare.com/clef-decision-models/) | Head/backbone and non-autoregressive scoring architecture, vendor measurements. |
| U44 | [Calibration research](https://arxiv.org/abs/1706.04599v2) | Calibration must be assessed separately from classification accuracy. |
