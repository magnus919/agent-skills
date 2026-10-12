# Advanced training paths

Start with an official notebook for the **same model, task and backend**, record
its commit, then minimize it to a short reproducible run. These paths are not
interchangeable extensions of a text-SFT script.

## GRPO and reward design

The [GRPO tutorial](https://unsloth.ai/docs/get-started/reinforcement-learning-rl-guide/tutorial-train-your-own-reasoning-model-with-grpo)
and [advanced RL guide](https://unsloth.ai/docs/get-started/reinforcement-learning-rl-guide/advanced-rl-documentation.md)
cover online sampling and reward-based training. Generation count, prompt and
completion lengths, rollout engine memory and batch grouping matter independently
of SFT batch size. Read the installed GRPOConfig validation rules; do not paste
SFT effective-batch arithmetic into a newer RL release.

Engineering checklist for a reward before spending GPU time:

1. Give it known correct, plausible incorrect, empty, malformed, and adversarial
   outputs. Assert finite scores and intended ordering.
2. Make task correctness independently observable. Formatting bonuses must not
   allow a wrong answer to dominate a correct one.
3. Record per-component distributions, parse failures, completion lengths, task
   success and held-out performance. Reward saturation without task improvement
   is a diagnosis trigger.
4. Treat model-generated code as untrusted execution: isolate filesystem/network,
   bound time and memory, and protect the reward's expected answers from outputs.
5. Budget rollout KV cache as well as training state. For OOM, reduce sequence
   lengths or generations in a configuration that still satisfies the trainer's
   grouping requirements; validate after every change.

## Preference data

Use the [preference guide](https://unsloth.ai/docs/get-started/reinforcement-learning-rl-guide/preference-dpo-orpo-and-kto.md)
for DPO/ORPO/KTO recipes. For pairwise objectives, verify shared prompt context
and correct chosen/rejected direction on sampled rows. KTO has a different data
contract; do not fabricate pairs just to reuse a loader. Prevent duplicate
prompt families crossing splits. Test behavior beyond preference score.

## Vision

The [vision guide](https://unsloth.ai/docs/basics/vision-fine-tuning.md) documents
`FastVisionModel` and `UnslothVisionDataCollator`. Retain image blocks and processor
behavior; plain JSON stringification loses the training signal. Use the vision
collator's masking controls for response-only loss. Before training verify an
image actually reaches the batch, decoded targets are correct, and resolution
does not exhaust memory. Split related images/documents as groups. Compare base
and candidate on held-out images with image-dependent scoring; text-only answers
can hide an ignored vision path.

## Audio, embeddings, diffusion

The [speech guide](https://unsloth.ai/docs/basics/text-to-speech-tts-fine-tuning.md)
covers TTS and STT model families with different processors and codecs. Use the
exact model's sample rate, audio tokens and decoder; seconds-per-token is not
universal. Confirm rights to recordings and speaker use. Split by speaker/session
as appropriate; evaluate audio output or transcription, not only token loss.

For embedding or diffusion tasks, locate the current model-specific guide through
the official documentation index. These are discovery routes, not a claim that
the text trainer supports them. Confirm objective, processor, trainable
components, hardware and export support before producing an execution recipe.

## Continued pretraining

The [continued-pretraining guide](https://unsloth.ai/docs/basics/continued-pretraining.md)
discusses language/domain adaptation and embedding/output-head training. Do not
add new tokens without resizing and saving the corresponding weights. Treat
tokenizer changes as artifact changes. Preserve a general-domain regression set
and validate later instruction behavior. Loading a previous adapter for another
phase starts a new experiment unless full trainer state is restored.

## Multiple GPUs

The [DDP guide](https://unsloth.ai/docs/basics/multi-gpu-training-with-unsloth/ddp)
demonstrates `torchrun --nproc_per_node=2 train.py`; each process normally carries
a model replica. DDP improves data-parallel throughput, not the size of a single
replica that fits. Verify rank-to-device assignment, distributed sampling, global
batch and checkpoint ownership on a two-step test.

The [multi-GPU overview](https://unsloth.ai/docs/basics/multi-gpu-training-with-unsloth)
also discusses manual integration and balanced placement. Model splitting and
FSDP/DeepSpeed require a matching tested configuration; generic library support
does not establish every quantized adapter combination. Never add `device_map`
from an inference snippet to a DDP script as an OOM fix. Record topology and
per-rank memory, and keep a single-device baseline where feasible.
