# Artifacts, recovery, and serving

For executed save/reload, stateful checkpoint resume, merged-weight reload and
GPU F16 GGUF parity, read `references/validated-sft.md` from the skill root. The
bundled `scripts/verify_export.py` and `scripts/gpu_completion.cpp` provide the
matched fixed-prompt checks. Quantized exports and services below remain separate
unverified paths.

## Name the artifact before saving

| Artifact | Contains/needs | Suitable for |
|---|---|---|
| Adapter | Trainable delta/config plus exact base revision | Small distribution, continued adaptation |
| Trainer checkpoint | Model/adapter and saved trainer/optimizer/scheduler/RNG state | Resume interrupted training |
| Merged weights | Base plus adapter in a chosen precision | Supported Transformers/serving runtime |
| GGUF | Converted model, possibly quantized | Supported llama.cpp-family runtime |

Always keep tokenizer or multimodal processor, template, special tokens, model
revision, license/provenance, and evaluation results with the artifact. A file
extension is not proof that the receiving runtime supports its architecture.

## Save and resume deliberately

Adapter save uses `model.save_pretrained(...)` plus tokenizer/processor save.
For a supported merge path:

```python
model.save_pretrained_merged("run/merged", tokenizer, save_method="merged_16bit")
```

Keep an adapter first, then verify disk and peak memory before merging. This can
need much more space than training a four-bit base. The official [GGUF guide](https://unsloth.ai/docs/basics/inference-and-deployment/saving-to-gguf.md)
documents merge and conversion APIs:

```python
model.save_pretrained_gguf("run/gguf", tokenizer, quantization_method="q4_k_m")
```

Check conversion/toolchain support, including auxiliary files for multimodal
models, before export. Export helpers may download/build conversion dependencies;
include that in the operation scope. Keep a higher-precision comparison artifact
when diagnosing quantization loss.

For an actual interrupted run, follow [checkpoint recovery](https://unsloth.ai/docs/basics/finetuning-from-last-checkpoint):

```python
trainer.train(resume_from_checkpoint="run/checkpoint-100")
```

Verify that the directory has trainer state and the optimizer state required for
the desired continuation, and that the dataset, world size, tokenizer and
configuration are compatible. Adapter reload alone resets training state; call
that continued fine-tuning, not exact resume. Record deviations when resuming
with changed hardware or data order.

## Fresh-process parity ladder

This ladder is an engineering recommendation, not a vendor benchmark:

1. Reload the adapter with its exact base. Check a fixed set of prompts and
   tokenizer output; verify adapter parameters are actually active.
2. Reload merged weights in a fresh process. Compare task outcomes under
   equivalent decoding; tiny floating-point differences need not be failures.
3. Load the converted/quantized artifact in the intended runtime. Compare task
   correctness and termination against the unquantized candidate and base.
4. If the target loops or emits gibberish, inspect rendered prompts, BOS/EOS,
   stop settings, template and base revision before retraining.

The [deployment guide for vLLM](https://unsloth.ai/docs/basics/inference-and-deployment/vllm-guide.md)
describes serving integration. Route actual server configuration to `vllm` or
`llama-cpp` once export is verified. Merged weights and runtime-loaded adapters
have different compatibility and memory constraints.

## Studio/Desktop and local API

The [API guide](https://unsloth.ai/docs/basics/api.md) describes model listing,
Chat Completions and Messages endpoints, with bearer authentication. Read the
running port and served model ID from the actual instance; do not assume 8000 or
8888 is correct. A minimal read-only check, with existing environment values:

```bash
curl --fail --silent --show-error "$UNSLOTH_BASE_URL/v1/models" \
  -H "Authorization: Bearer $UNSLOTH_API_KEY"
```

Do not echo tokens or enable verbose HTTP traces containing authorization. Keep
server-side tools disabled unless the task calls for them and the filesystem,
network and caller scope are established. The [security guide](https://unsloth.ai/docs/new/studio/security)
is the authority for the installed surface's authentication and exposure model.
Local chat capability does not authorize remote access, external tools, model
publication, or transferring training data to recipe providers.

For Hugging Face publishing, establish the destination repository and visibility,
check distribution rights, inspect the exact artifact set, and upload only the
approved scope. Verify the remote revision with a clean reload; retain the prior
artifact as rollback. Do not treat a local export request as upload authorization.
