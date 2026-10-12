# Capabilities and selection

Research snapshot: 2026-10-12. These are operating decisions, not performance
guarantees. Product facts are grounded in the official [repository](https://github.com/unslothai/unsloth)
and [installation overview](https://unsloth.ai/docs/get-started/install).

| Surface | Choose it for | Verify first |
|---|---|---|
| Core | Python/notebook training with explicit code and experiment control | Model loader, dependencies, backend kernels |
| Studio | Browser-driven chat, training, dataset recipes and export | Installed build, backend and available UI features |
| Desktop | Native local application | OS installer and model/backend support |

Core integrates with the Hugging Face training ecosystem and supplies optimized
execution paths. It is not a model family. A model uploaded by Unsloth, an
Unsloth training installation, and a GGUF runtime are distinct things.
The same named model can have different weight formats and resource requirements.

## Choose the training objective before the recipe

These are engineering decision rules for this skill:

| Need and evidence | Starting approach | Failure to avoid |
|---|---|---|
| Change answer style, schema, or demonstrated task behavior | SFT on reviewed examples | Assuming low loss proves task accuracy |
| Prefer one valid response over another | Preference optimization with consistent comparisons | Reversed chosen/rejected data |
| Improve behavior with an executable outcome score | GRPO or model-matched RL recipe | Optimizing formatting while task correctness falls |
| Learn domain text distribution or new language | Continued pretraining followed by task validation | Catastrophic forgetting, losing instruction behavior |
| Answer questions over frequently changing private facts | Consider retrieval first | Trying to use weights as an updateable database |
| Run an existing model locally | Inference path; no training required | Installing a training stack unnecessarily |

Use a small supported instruct model for the first conversational pilot unless
the task needs a base model. Select model size against measured task ability and
available memory, not size alone. Verify the base model's license and any gated
access before download or distribution. Treat support as a tuple of surface,
model revision, task, precision, backend, and package versions.

Studio's [getting-started guide](https://unsloth.ai/docs/new/studio/start.md)
provides chat, training, and export workflows. For a GUI run, still preserve data
splits, parameter settings, logs, and the resulting files in the run record;
a screenshot of a completed progress bar is not an evaluation.
