# Desktop media generation and artifact checks

Documented/source-inspected 2026-10-12; generation, media training and playback
**not run**. Sources: [Desktop](https://unsloth.ai/docs/desktop),
[image guide](https://unsloth.ai/docs/desktop/diffusion-image) and pinned upstream
`b865e89586eb1af3185f416c448becd08f0e15d8` media-family implementations. A gallery
feature does not prove a chosen model/workflow fits this GPU or runs offline.

## Choose a model/task/backend tuple

| Request | Route and required distinction |
|---|---|
| Generate/transform an image | Images → Create/Transform; choose a supported diffusion model and format |
| Follow an image-edit instruction | Edit requires an editing model; Transform is a different operation |
| Inpaint/extend/upscale/reference | Verify that operation is offered for the loaded model; do not promise every mode for every model |
| Video | Verify supported video family, frame count/FPS, dimensions, precision and required components |
| Speech/music | Verify task/family and audio backend; a TTS training notebook does not prove Desktop music inference |
| Train an image LoRA | Use a matched diffusion training recipe; vision-language SFT is not diffusion training |

The official image guide distinguishes editing models such as Qwen-Image-Edit
and FLUX.1 Kontext from generative/transform models; reference support is model
specific. The upstream audio catalog includes Stable Audio music; video family
code has separate model implementations. This is source presence, not measured
runtime compatibility or a recommendation to download those models immediately.

## Reproducible first artifact

1. Inventory app/build, hardware/backend, free VRAM/RAM/disk and active jobs.
   Record all component repository IDs/revisions, exact weight files/hashes,
   licenses/access requirements, LoRA revisions and precision. A quantized main
   model can still require text encoders, VAE/vocoder or projection files.
2. Use a new run/gallery destination and a small first operation. Select the
   model's supported mode; set a fixed prompt/seed, dimensions, batch 1, step
   count, guidance, sampler and duration/frames where applicable. Preserve the
   settings/recipe next to the output. Separate cold download/compile/load time
   from warm generation time and measure peak memory.
3. When GPU-only is required, disable CPU offload/fallback and verify actual
   component placement. The guide's Low VRAM/TIGHT modes can use system memory;
   a model-picker recommendation is not a placement guarantee. Report a missing
   fail-closed control instead of silently using CPU. Reduce dimensions/duration
   or choose a smaller supported model within the authorized run; do not stop
   unrelated workloads or change drivers.
4. Save the real output, settings and hash. Inspect the artifact: image decodes
   with requested dimensions; video decodes with observed frame count, FPS and
   duration; audio decodes with observed sample rate, channels and duration.
   Use `ffmpeg` for media probes and bounded samples. Metadata cannot establish
   visual quality, intelligibility, identity preservation or absence of faults.
5. Review the requested outcome using a predeclared rubric and attributed review:
   prompt adherence, required edit/mask preservation, temporal behavior, speech
   intelligibility or musical structure as relevant. Record adverse examples,
   not only a pleasing gallery sample. Same seed across models/backends does
   not guarantee identical pixels or waveforms.

For voice reference/clone tasks, establish whose authorized recording is being
used, its permitted use and retention before upload or training. Keep private
media on the authorized host. Local UI does not authorize a hosted provider,
public tunnel or publication of generated artifacts.

Completion requires a playable/decodable artifact, recorded settings, observed
placement/resources and scoped quality evidence. If only instructions are
prepared, mark generation, playback and quality review not run. Do not report a
synthetic file-header check as successful model generation.
