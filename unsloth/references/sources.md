# Source ledger and refresh guide

Retrieved 2026-10-12. All retained sources are upstream documentation or maintainer
repositories; they are mutable pages, not pinned release contracts. Documentation
was inspected through web retrieval. Source agreement within one vendor is not
independent validation. Short extractions below record the claim used, not copied
documentation. Installation commands and GPU recipes have not been run here.

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
outputs are generated and reviewed. No GPU run, cloud job, model download,
publication, comparative speed benchmark or behavioral uplift is established.
