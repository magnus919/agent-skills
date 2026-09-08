# FFmpeg Expert Skill

A practical FFmpeg skill for inspecting local media, planning reviewable video or podcast edits, rendering safely, and accepting outputs from evidence rather than command success alone.

## Why Install This Skill

FFmpeg failures often happen at boundaries: the wrong stream is selected, a cut lands on an unexpected keyframe, a filter is absent from the installed build, timestamps drift, or a technically valid output fails in its real destination. Editorial work adds another risk: sparse frames, silence intervals, and imperfect transcripts can look more conclusive than they are.

This skill provides a repeatable intake-to-acceptance workflow. It separates technical measurements from editorial judgment, preserves originals, makes cuts reviewable in an edit decision list, and records what was actually checked.

## What You Get

### Core guidance

| Path | Purpose |
|---|---|
| `SKILL.md` | Trigger boundaries, capability routing, evidence classes, and the core workflow |
| `references/core-model-and-command-anatomy.md` | Containers, streams, codecs, mapping, option scope, and timestamps |
| `references/filters-and-transformations.md` | Simple and complex filtergraphs, audio/video filters, and graph debugging |
| `references/intermediate-workflows.md` | Trimming, concat, metadata, subtitles, scripting, pipes, and streaming |
| `references/advanced-operations-and-safety.md` | Hardware, synchronization, reproducibility, and operational safety |
| `references/command-cookbook.md` | Short, assumption-labeled commands |
| `references/learning-summary.md` | Learning progression and consolidated mental model |
| `references/source-inventory.md` | Original primary/secondary source inventory and evidence boundaries |
| `references/local-verification.md` | Version- and host-specific FFmpeg 8.1.2 experiments |

### Media editing and evidence guidance

| Path | Purpose |
|---|---|
| `references/media-intake-and-manifest.md` | Authorization, source identity, probe capture, output contracts, privacy, and preservation |
| `references/video-inspection-and-visual-evidence.md` | Bounded frame/clip sampling and defensible visual claims |
| `references/editorial-video-editing.md` | Transcript-assisted decisions, sequencing, treatments, and review gates |
| `references/audio-and-podcast-editing.md` | Mechanical edits, signal cleanup, editorial audio decisions, and listening checks |
| `references/ffmpeg-edit-decision-lists.md` | EDL semantics, validation, keyframe status, mapping, and command planning |
| `references/media-verification-and-acceptance.md` | Layered probe, decode, content, editorial, and downstream acceptance evidence |
| `references/media-failure-modes.md` | Diagnosis matrix, safe recovery, and stop rules |
| `references/media-research-source-index.md` | Claim-to-source map for official docs, standards, experiments, and heuristics |
| `references/editorial-workflow-example.md` | Reproducible synthetic intake-to-acceptance integration workflow |
| `references/synthetic-media-fixtures.md` | Deterministic real-media fixture coverage and evidence boundaries |

### Copyable templates

| Path | Purpose |
|---|---|
| `templates/media-intake.json` | Parseable source, stream, timing, contract, privacy, and assumption manifest |
| `templates/edit-decision-list.json` | Parseable source ranges, evidence, confidence, treatments, mapping, and verification |
| `templates/video-inspection-report.md` | Fixed-section technical and sampled-evidence report |
| `templates/visual-review-packet.md` | Timestamped review samples with attribution and coverage limits |
| `templates/vision-review-observations.json` | Machine-readable reviewer attribution, evidence classes, blind spots, and EDL links |
| `templates/podcast-edit-plan.md` | Mechanical, signal-processing, and editorial audio plan |
| `templates/media-acceptance-report.md` | Criterion-by-criterion evidence and release verdict |
| `templates/media-acceptance-contract.json` | Parseable stream, format, evidence, loudness, and downstream criteria |
| `templates/research-experiment-record.md` | Versioned, reproducible command experiment record |

### Existing automation and evals

| Path | Purpose |
|---|---|
| `scripts/ffmpeg-preflight` | Tool status, inventory counts, and named filter/encoder/hwaccel checks |
| `scripts/test_ffmpeg_preflight.py` | Deterministic tests for the capability preflight |
| `scripts/fixtures/ffmpeg-8.1.2-inventories.json` | Small version-labeled parser fixture |
| `scripts/media-intake` | Read-only input inventory with bounded `ffprobe` metadata |
| `scripts/extract-review-frames` | Bounded timestamp frame extraction for human or vision review |
| `scripts/vision-review-handoff` | Privacy-safe bounded frame packet with provenance, limits, hashes, and pending-review manifest |
| `scripts/import-vision-review` | Validate attributed observations and link them to EDL events without rendering |
| `scripts/render-edl` | Validate single- or multi-source EDLs and emit non-executing concat-filter or concat-demuxer plans |
| `scripts/audio-inspect` | Bounded silence, loudness, peak/clipping, transcript-candidate, and podcast-plan evidence |
| `scripts/media-verify` | Evaluate output probe and review evidence against a declared acceptance contract |
| `scripts/editorial-workflow-example` | Generate synthetic audio/video and exercise the complete workflow with durable evidence |
| `scripts/generate-media-fixtures` | Generate a bounded sanitized fixture battery and versioned evidence manifest |
| `evals/evals.json` | Output-quality cases for core FFmpeg, media evidence, video, podcast, EDL, safety, and acceptance behavior |

## Quick Start

Install FFmpeg with your platform package manager and inspect the source before choosing an edit:

```sh
ffmpeg -version
ffprobe -version
ffprobe -v error -show_format -show_streams -of json input.mp4
```

For a media editing task:

1. Copy `templates/media-intake.json` into a private task workspace and record the source and output contract.
2. Collect only the bounded frame, clip, transcript, or signal evidence needed for the decision.
3. Copy `templates/edit-decision-list.json` or `templates/podcast-edit-plan.md` and review consequential cuts.
4. Render to a new path with overwrite refusal while exploring.
5. Copy `templates/media-acceptance-report.md`, probe and review the result, then test the intended player, editor, service, or archive boundary.

Before using a version-sensitive recipe, inspect the local capability:

```sh
scripts/ffmpeg-preflight --filter scale --filter loudnorm --encoder libx264 --hwaccel videotoolbox
```

Named checks report each capability as present or absent. Exit code `1` means a required tool/probe failed; `2` means a requested capability is absent from a usable inventory. Add `--json` for machine-readable output.

Run the complete synthetic integration example in a new or empty task-local directory:

```sh
scripts/editorial-workflow-example /tmp/ffmpeg-editorial-example --json
```

The resulting acceptance report passes only the exercised component and integration checks; semantic, listening, and downstream-consumer boundaries remain explicitly unverified.

Generate the richer real-media test battery when a change needs timestamp, concat, audio, subtitle, or bounded visual evidence:

```sh
scripts/generate-media-fixtures /tmp/ffmpeg-fixtures --json
```

Generated media remains task-local; commit the generator and test assertions, not the binary outputs.

Produce measured audio evidence and a reviewable plan without changing the source:

```sh
scripts/audio-inspect input.wav \
  --measure-silence --silence-threshold=-45dB --silence-duration 0.7 \
  --measure-loudness --measure-clipping --json
```

Optional timed transcript JSON must disclose alignment quality. Detector intervals and transcript ranges remain candidates until listening review approves an edit.

Evaluate a rendered output against declared criteria:

```sh
scripts/media-verify acceptance-contract.json output-probe.json \
  --evidence review-evidence.json --json
```

Missing fields or review evidence remain `UNVERIFIED`; blocked reviews remain `BLOCKED`; local probe/decode success never supplies downstream compatibility evidence.

Prepare visual evidence around proposed edit boundaries without exposing the source path:

```sh
ffmpeg/scripts/vision-review-handoff private.mov --asset-id asset-017 \
  --question "Does the sampled boundary preserve title continuity?" \
  --timestamp 12.4 --neighbor-seconds 0.25 --output-dir review-packet --json
```

The manifest covers only its listed samples. An authorized reviewer must add attributed observations before `import-vision-review` can link them to an EDL; sparse frames never prove absence throughout a video.

## Triggers

Load this skill for:

- Media intake, FFprobe manifests, stream/container/timestamp inspection, or output contracts
- Remuxing, transcoding, filtering, trimming, joining, extraction, subtitles, or synchronization
- Bounded review-frame or audio-evidence preparation from supplied/authorized local media
- Transcript-assisted video edits, reviewable EDLs, or deterministic render plans
- Podcast cutting, silence/noise analysis, loudness measurement, and audio cleanup
- Build capability checks, overwrite-safe batch work, output verification, or failure diagnosis

Use another capability first for online media/transcript acquisition, semantic image interpretation, HTML-authored HyperFrames composition, platform publishing/API work, DRM, or rights clearance.

## Requirements

- `ffmpeg` and `ffprobe` on `PATH` for execution
- A shell with careful filename and filter-expression quoting
- A vision-capable or human reviewer for semantic claims about extracted images
- Listening playback for editorial audio acceptance
- Network access only for linked documentation or an explicitly requested network protocol
- Hardware acceleration only with the relevant device, drivers, compiled support, and a verified end-to-end path
