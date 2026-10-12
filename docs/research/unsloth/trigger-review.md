# Description boundary review

2026-10-12. Author review, not measured harness activation. These probes are
separate from the portable output-quality eval manifest.

| Prompt | Expected route | Reason |
|---|---|---|
| Install Unsloth on my AMD workstation. | unsloth | Named tool and installation |
| My Unsloth QLoRA loss is zero after response masking. | unsloth | Tool-specific training diagnosis |
| Export my Unsloth adapter to GGUF and check llama.cpp output. | unsloth, then llama-cpp | Artifact boundary followed by runtime operation |
| Set up Unsloth Desktop on my Mac. | unsloth | Explicit Desktop surface |
| Should we use retrieval or fine-tune for changing product prices? | ml-engineering | Framework-neutral strategy |
| Tune batching in an existing standalone vLLM server. | vllm | No Unsloth training/export task |

The skill name is lowercase `unsloth` as required by the format. Its human-facing
title is Unsloth. No alias or separate Core/Studio/Desktop skill is introduced.
