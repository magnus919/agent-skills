---
name: ffmpeg
description: >-
  Use this skill when an agent needs to inspect, convert, remux, transcode, filter,
  combine, stream, or troubleshoot audio and video with the FFmpeg command-line
  tools, especially ffmpeg and ffprobe. It teaches explicit stream selection,
  filtergraph construction, timestamp diagnosis, build-aware commands, safe
  scripting, and post-run verification. Do not use it for libav API programming,
  professional color-management certification, DRM circumvention, or untested
  platform-specific capture hardware; route those to specialized guidance.
license: MIT
compatibility: Requires ffmpeg and ffprobe for execution; exact filters, codecs, protocols, and hardware backends vary by build and version.
---

# FFmpeg Expert

Treat FFmpeg commands as typed media pipelines, not incantations. Start from what the input actually contains, choose the smallest operation that satisfies the output contract, and verify the resulting artifact at the boundary that matters.

## When Not to Use

- Do not use this skill for libav*/FFmpeg C API application development.
- Do not use it as a complete codec encyclopedia or a professional color-management certification guide.
- Do not use it to circumvent DRM or to document capture hardware that has not been tested on the target platform.
- For a named hosting or media platform's API, use that platform skill and use this skill only for the local media transformation.

## Operating Loop

1. **Inspect first.** Run `ffprobe -v error -show_format -show_streams -of json INPUT` and identify streams, codecs, dimensions, rates, durations, time bases, metadata, and start timestamps.
2. **Classify the operation.** Choose remux/stream copy, transcode, filter, combine, extract, or protocol/pipe output. Remuxing changes packaging; transcoding decodes and re-encodes.
3. **Check capabilities.** Use `ffmpeg -formats`, `-codecs`, `-encoders`, `-filters`, and `-hwaccels`. Never assume a tutorial's filter, encoder, or hardware backend exists locally.
4. **Make selection explicit.** Use `-map` for multiple inputs, tracks, or complex graphs. Remember that options generally apply to the next input or output, so order matters.
5. **Protect the source.** Use `-n` while exploring, write to a new path, avoid untrusted shell concatenation, and keep credentials out of command lines and logs.
6. **Probe and exercise the result.** Check the output with `ffprobe`, then test the actual player, editor, receiver, archive rule, or API consumer. Exit code and container validity are necessary but not sufficient.

## Choose the Right Reference

- Read `references/core-model-and-command-anatomy.md` for containers, streams, codecs, option scope, mapping, copy/transcode, and timestamps.
- Read `references/filters-and-transformations.md` for simple and complex filtergraphs, labels, audio/video processing, and incremental graph debugging.
- Read `references/intermediate-workflows.md` for seeking, trimming, concatenation, metadata, subtitles, batch scripts, pipes, and streaming.
- Read `references/advanced-operations-and-safety.md` for hardware acceleration, synchronization diagnosis, reproducibility, network and overwrite safety, and failure boundaries.
- Read `references/command-cookbook.md` for short examples with stated assumptions. Adapt them only after inspection and capability checks.
- Read `references/learning-summary.md` for the newcomer-first progression and consolidated mental model.
- Read `references/source-inventory.md` when assessing evidence, choosing authoritative documentation, or refreshing version-sensitive guidance.
- Read `references/local-verification.md` when interpreting the recorded local FFmpeg 8.1.2 evidence. It is a host-specific observation, not a universal capability claim.
- Run `scripts/ffmpeg-preflight` before automating a version-sensitive workflow. It reports tool status, parsed filter/encoder/hwaccel counts, and repeatable named checks: `--filter NAME`, `--encoder NAME`, `--hwaccel NAME`. Use `--json` for machine-readable output and `--timeout SECONDS` to bound each probe (10 seconds by default). Named FFmpeg-only checks do not require `ffprobe`; media inspection and the no-query environment check do. Exit codes: 0 every requested capability is present, 1 a required tool/probe failed or the requested inventory was empty/unparseable, 2 a usable inventory was parsed and a requested capability is absent. Empty inventories without named queries are reported as warnings.

## Debugging Rules

- For missing filters, encoders, or protocols, reproduce with `ffmpeg -filters`, `-encoders`, or the relevant inventory before changing the command.
- For drift, bad cuts, concat jumps, or unexpected duration, compare timestamps and stream properties before adding flags. `-copyts`, `-start_at_zero`, synchronization controls, `setpts`, `asetpts`, `aresample`, and `avoid_negative_ts` solve different problems.
- Build filtergraphs incrementally: baseline transcode, one filter, then labels/branches. Distinguish parser, availability, format negotiation, timestamp, encoder, and muxer failures.
- Treat examples as conditional on input, target, build, version, and downstream consumer. State those conditions in explanations and scripts.

## Completion

Stop when the requested artifact exists, the relevant output probe and downstream-boundary check pass, and any untested capability or compatibility gap is stated explicitly. If execution is blocked, report the exact layer and evidence rather than substituting a plausible result.
