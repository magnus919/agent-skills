# Fine-tuning Gemma 4

Choose the smallest Gemma 4 checkpoint that meets the task, modality, and serving requirements. Measure the unchanged instruction-tuned model first, using the production prompt or retrieval path if the task already has one. Freeze a task-representative test set and define the quality, regression, memory, and latency thresholds before training. Use the [training run record](../templates/training-run-record.md) to pin the experiment.

## Choose a checkpoint and method

| Checkpoint | Architecture and inputs | QLoRA / full tuning at 2,048 tokens |
| --- | --- | --- |
| E2B | Dense with per-layer embeddings (PLE), text, image, audio | ~7 GB / ~32 GB |
| E4B | Dense with PLE, text, image, audio | ~9 GB / ~42 GB |
| 12B | Shared decoder with direct image and audio projections, text, image, audio | ~11 GB / ~80 GB |
| 26B A4B | Mixture of experts (MoE), text and image | ~21 GB / ~160 GB |
| 31B | Dense, text and image | ~22 GB / ~200 GB |

The memory figures are Google's example peak VRAM estimates at the stated sequence length. The 26B A4B QLoRA figure uses a backend that quantizes the fused expert tensors. Budget for loaded parameters, including PLE or the resident experts, and measure peak VRAM on a short run with representative sequence lengths, media and microbatches. The model card's context limits (128K for E2B/E4B, 256K for the larger models) describe supported context, and a training batch at that length requires its own memory budget. [Fine-tuning overview](https://gemma.ai/tuning/) · [Model card](https://gemma.ai/models/gemma-4/model-card/) · [MoE tuning](https://gemma.ai/tuning/moe-finetune/)

| Goal | Starting point |
| --- | --- |
| Fresh facts or access-controlled records | Keep the deployed checkpoint and evaluate retrieval with the real access and freshness requirements. |
| Output schema, support tone, extraction or tool use | Start from `-it` and use supervised fine-tuning (SFT). Try BF16 LoRA when it fits or NF4 QLoRA to reduce frozen-weight memory. |
| Major new domain or language | Continue pre-training on packed raw text from the checkpoint without `-it`. Follow with SFT if instruction following is required. |
| Custom chat protocol | Start from the pre-trained checkpoint if deliberately teaching a new format. Train role boundaries and the termination sequence together and test the exported serving template. |
| Style preference or other comparative judgments | Start from `-it` or a qualified SFT checkpoint. Use preference pairs and DPO when the tradeoff can be labeled reliably. |
| Tasks with machine-checkable answers | Establish SFT and verifier baselines. Consider GRPO when correct rollouts exist and a reliable verifier can distinguish them from plausible failures. |
| Adapter misses the target after controlled trials | Compare full tuning with a qualified adapter under matched evals. Budget weights, gradients, optimizer state, activations, and sharding before starting. |

### A first text SFT run

1. Pin the model revision, processor/tokenizer and template, training-library versions, data and split hashes, and serving configuration. Split by source, customer, document family or time whenever those are the units of generalization. Keep checkpoint selection on validation data and run the final comparison on the untouched test set.
2. Start with a supported `-it` checkpoint, such as `google/gemma-4-E4B-it` for a compact pilot. For the unmodified Transformers/TRL path, start with BF16 compute on compatible hardware and PyTorch SDPA. Google's guide flags the 512-dimensional global attention heads as incompatible with standalone FlashAttention-2 and flags FP16 overflow risk for the compact audio encoders. Test the actual attention backend and dtype on a forward/backward batch.
3. In the dense decoder, inspect adapter attachment across `q_proj`, `k_proj`, `v_proj`, `o_proj`, `gate_proj`, `up_proj` and `down_proj` where present. Keep E2B/E4B PLE and unused modality modules frozen for ordinary text SFT. Preserve input/output weight tying and the model's media components in saved artifacts.
4. Google's starting range for SFT is a learning rate of `1e-4`–`2e-4`, effective batch size 16–32, 3–5% warmup, and 1–3 epochs. Rank 16 is a reasonable first sweep point for narrow formatting tasks and rank 32 for broader behaviors. For QLoRA, the example uses frozen NF4 weights with BF16 compute. Run a tiny overfit check, confirm finite gradients and trainable parameter names, then continue with validation and held-out task metrics. Report coverage and exact schema or tool-action correctness alongside loss.
5. Compare the untouched checkpoint, the adapter reloaded on its pinned base, and the intended runtime artifact. Include a same-precision base comparison when measuring adapter benefit and a production-precision comparison when evaluating deployment. Use identical test cases, prompt/processor settings, decoding budgets and scoring rules.

[Best practices](https://gemma.ai/tuning/best-practices/) · [(Q)LoRA recipe](https://gemma.ai/tuning/qlora/) · [Full fine-tuning recipe](https://gemma.ai/tuning/full-finetune/)

### Check the rendered tokens before training

- Render real rows with the pinned processor and chat template. The structured `assistant` role renders as `model` inside Gemma turns. In training, include the labeled response and its closing `<turn|>`. For standard generation, test stopping on both `<turn|>` and EOS (IDs 106 and 1 in Google's guide) against the loaded tokenizer and generation config.
- Inspect paired `input_ids` and `labels` after collation, including the longest examples. Expect `-100` on system, user, retrieved content, tool definitions and tool results, padding and media soft tokens. Supervise assistant answer text, assistant tool calls and the modeled turn close. If supervising reasoning, retain the intended assistant thought spans. Drop or resize examples whose truncation removes supervised tokens or terminal boundaries.
- Use structured `prompt` and `completion` for completion-only text SFT, or verify a custom collator or assistant-generation mask against rendered examples. With tools, a tool response can be embedded inside a rendered model turn and still needs its own mask. Confirm the template preserves within-turn thought across tools and drops previous completed turns' thought blocks as the target runtime does.
- Keep test coverage for thinking and direct modes when both are served. Google documents different non-thinking serialization for E2B/E4B and the larger variants. If using teacher-generated training traces, use training prompts, verify final answers and trace quality separately, and measure retained reasoning and output budget on held-out cases.

[Dataset formatting](https://gemma.ai/tuning/datasets-formatting/) · [Custom chat templates](https://gemma.ai/tuning/custom-chat-template/) · [Model card](https://gemma.ai/models/gemma-4/model-card/)

## Adapt architecture or objective deliberately

| Route | What to change and verify |
| --- | --- |
| Continued pre-training | Use the pre-trained checkpoint, full-token next-token prediction on packed documents, and clear document boundaries. Google's example includes about 10% general replay. Track target-domain and general-domain held-out loss separately and test downstream behavior after SFT. If adding vocabulary, initialize new embeddings from constituent subwords where appropriate, preserve the tied head, and round-trip the tokenizer and checkpoint. [Continued pre-training](https://gemma.ai/tuning/continued-pretraining/) |
| Full tuning | Begin with a small learning-rate sweep around the documented `1e-5`–`2e-5` range. Pin precision and the actual optimizer, including its state dtype. Compare task gain and retention to LoRA before paying the full cost. [Full fine-tuning](https://gemma.ai/tuning/full-finetune/) |
| 26B A4B | Keep the router frozen and verify zero trainable router parameters. Target the shared expert and attention modules as appropriate, and use PEFT `target_parameters` for the fused routed-expert tensors `experts.gate_up_proj` and `experts.down_proj` on the documented BF16 path. Confirm expert coverage and kernel support. Google's recipe estimates ~56 GB for BF16 LoRA and describes an Unsloth ~21 GB path. Standard bitsandbytes module quantization in that recipe skips the fused 3-D expert tensors. Compare routing and held-out quality before selecting the quantized path. [MoE tuning](https://gemma.ai/tuning/moe-finetune/) |
| Reserved tokens | Use a deliberate registry of assigned token strings and IDs for compact control tags. Check single-ID encoding in context, decode visibility, trainable row initialization before adapter wrapping, and tied weights. Check PLE rows on compact variants when adapting reserved embeddings and verify round-trip export plus ordinary text regressions. [Unused tokens](https://gemma.ai/tuning/unused-tokens/) |
| Vision | Use the matching multimodal processor and preserve the same media/text order and soft-token budget between training and evaluation. Benchmark several budgets (70, 140, 280, 560 and 1,120 are documented) for the quality and latency target. Check field accuracy as well as schema validity. E2B/E4B, 26B and 31B have a separate vision encoder. Changes in the shared 12B decoder can also affect text and audio. [Vision tuning](https://gemma.ai/tuning/vision-qlora/) |
| Audio | Use E2B, E4B or 12B. The transcription recipe uses BF16 LoRA, 16 kHz mono clips no longer than 30 seconds, and completion-only labels with audio soft tokens masked. Freeze dedicated encoders where present for decoder-only adaptation. Compare WER and CER across held-out speakers and relevant noise and language groups, and check text and image retention. [Audio tuning](https://gemma.ai/tuning/audio-qlora/) |
| Preferences | Use matched `prompt`, `chosen`, and `rejected` examples with explicit preference criteria. Pin the frozen reference checkpoint. If the trainer disables the active adapter to compute reference scores, use the merged qualified SFT checkpoint as the base when that is the intended reference, then attach a fresh preference adapter. Check correctness and subgroup regressions alongside preference win rate and response length. [Preference optimization](https://gemma.ai/tuning/preference-alignment/) |
| Verifiable rewards | Define a correctness check on the final answer. Probe the verifier with malformed, confidently wrong and superficially well-formatted answers. Track correctness, format and length separately and keep quality thresholds independent of training reward. Compare the base/SFT baseline and GRPO under matched generation budgets. [Verifiable rewards](https://gemma.ai/tuning/reinforcement-learning/) |

## Scale, export, and compare the deployed artifact

- If a full training replica exceeds one card, evaluate FSDP2 using the documented Accelerate approach. Try data parallelism when a QLoRA replica fits on each card and throughput is the goal. Record world size, effective tokens per update, measured peak per-rank memory, communication overhead and save/resume behavior. Keep QLoRA training and deployment quantization distinct. If post-training quantization loses task quality, measure a TorchAO QAT candidate against the same test cases and confirm the target kernel can load it. [Scaling](https://gemma.ai/tuning/scaling/)
- Preserve the adapter and exact base revision. For a merged deliverable, use the workflow's supported merge path and retain processor, tokenizer, template and generation settings. Reopen the merged SafeTensors checkpoint in a fresh process. Verify adapter or merged vLLM support for the exact variant and target types. For llama.cpp or Ollama, validate GGUF conversion and quantization, including any required modality projector and engine support. For LiteRT-LM on E2B/E4B, confirm the variant-specific chat template and externalized PLE support on the target device. [Export](https://gemma.ai/tuning/export/)
- Run the same end-to-end probes on the runtime build. Cover turn stops, structured parsing, multi-turn tool use where applicable, thinking mode, each supported modality, long inputs and failure behavior. Record format, converter/runtime versions, hashes, generation settings, quality deltas, peak memory, latency, and throughput at target concurrency. Keep the qualified prior artifact available for rollback.

## Tool routing and evidence

Use [TRL](https://huggingface.co/docs/trl) with Transformers/PEFT for the core recipes and [Axolotl's Gemma 4 guide](https://docs.axolotl.ai/docs/models/gemma4.html) for its YAML-based path. The catalog's [Unsloth skill](../../unsloth/SKILL.md) covers local training and export operations. Google also documents [Unsloth for Gemma 4](https://gemma.ai/tuning/unsloth/) and its upstream [`gemma-trainer` skill](https://gemma.ai/tuning/gemma-trainer/). Check current managed service support for the exact model, region and tuning method. The overview's linked [GKE destination](https://cloud.google.com/kubernetes-engine/docs/tutorials/finetune-gemma-gpu) redirected to general inference documentation during collection. The [managed open-model tuning destination](https://cloud.google.com/vertex-ai/generative-ai/docs/models/open-model-tuning) describes a broader workflow and needs a checkpoint-specific compatibility check.

[Source capture record](gemma-4-sources.md) records the guide coverage and extraction gaps. Tutorial numbers and capabilities are attributed to upstream docs. Hardware fit, quality changes and runtime parity require evidence from the intended environment.
