# Media Failure Modes

Diagnose from the first discriminating evidence, preserve the source, and change one assumption at a time. Do not “repair” the only copy or hide warnings merely to obtain a zero exit status.

## Diagnostic matrix

| Symptom | Evidence to collect | Common hypotheses | Safe next action |
|---|---|---|---|
| Wrong or missing output stream | Full input/output `ffprobe`; complete command; mapping log | Automatic stream selection, disposition, program, optional map, or unsupported type | Declare `-map` and retention policy explicitly; verify the new output. |
| Duration/start time is surprising | Format and stream start/duration/time base; chapters; packet/frame sample near boundaries | Container estimate, edit list, timestamp offset, VFR, sparse index, truncation | Keep raw timestamps; compare decoded boundaries; do not overwrite metadata blindly. |
| Cut begins early/late | Seek placement, keyframe/packet data, decoded frames/audio around the boundary | Input seek point, inter-frame dependency, packet-level copy, time-base rounding | Use a decoded trim for precision or approve the observed packet boundary. |
| Concat fails or drifts | Probe every segment; concat method; per-stream parameters and timestamps | Codec/parameter mismatch, inconsistent time bases, missing streams, incorrect duration directives | Normalize intentionally or use decoded concat; review every join. |
| Non-monotonic DTS or timestamp warnings | Full warning context; packet timestamps around event; muxer and sync options | Broken source timestamps, reordered frames, concat offsets, inappropriate passthrough | Isolate the first bad interval; avoid speculative timestamp generation; test a new artifact. |
| Filter, encoder, or hardware path is unavailable | Local version/build configuration and component inventories | Local build lacks dependency/component; unsupported device/pixel format | Choose a verified available path; software fallback must be explicit and reaccepted. |
| A/V sync changes over time | Independent stream starts/durations/time bases; declared sync points across the timeline | Clock/cadence mismatch, dropped/duplicated frames, resampling, incorrect trim/concat | Measure drift before choosing timestamp, frame-rate, or resampling correction. |
| Color, range, or geometry is wrong | Source/output color and aspect metadata; decoded reference frames; filtergraph | Unstated conversion, ignored display metadata, range/matrix mismatch, SAR/DAR error | Declare the conversion and target; compare in the intended display path. |
| Audio clips, pumps, or changes tone | Source/output measurements plus listening around affected regions | Excess gain, dynamics/denoise settings, resampling, channel rematrixing | Bypass filters, compare one stage at a time, then re-measure and listen. |
| Probe succeeds but decode fails | Decode-check errors and first failing timestamp/stream | Truncated/corrupt packets, unsupported feature, damaged index, decoder defect | Preserve evidence; isolate stream/interval; seek an alternate authorized source when repair is uncertain. |
| Local playback succeeds but destination rejects | Exact accepted artifact plus destination error/version/settings | Unsupported container/codec/profile/level, metadata, file limit, ingest policy | Test against documented destination requirements; make a new derivative and reaccept it. |

## Recovery rules

1. Save the exact command, build, exit status, and unfiltered first relevant warnings.
2. Probe before changing anything; compare source and failed output.
3. Reduce to one stream and the smallest failing interval only in a new diagnostic artifact.
4. Verify local availability before adding codec, filter, format, protocol, or hardware options.
5. Prefer explicit mapping, formats, time bases, and channel/pixel choices over guessed defaults.
6. After a change, repeat the checks affected by that change. A workaround is not a diagnosis until evidence distinguishes it.

Stop when authorization is unclear, the only source would be modified, damage/repair would alter meaning, encryption or access controls are encountered, private material would leave its approved boundary, or acceptance requires an unavailable human/destination review.

## Evidence and heuristic boundary

- **Direct evidence:** exact probe fields, packet/frame observations, logs, commands, decoded samples, and destination errors for the named artifact/build.
- **Discriminating experiment:** a controlled one-variable comparison; its conclusion is limited to the recorded fixture and environment.
- **Hypothesis:** every “common cause” in the matrix until evidence rules it in. Similar symptoms can have different causes.
- **Heuristic:** increasing probe limits, regenerating timestamps, forcing a codec/tag, changing sync mode, or re-encoding “because it usually works.” Never present these as proven repairs.
- **Not established:** absence of warnings is not proof of integrity, editorial correctness, sync everywhere, or downstream compatibility.

## Official FFmpeg sources

- [ffmpeg Documentation](https://ffmpeg.org/ffmpeg.html) — option scope, seeking, mapping, timestamps, filtering, codecs, logging, and overwrite controls.
- [ffprobe Documentation](https://ffmpeg.org/ffprobe.html) — format/stream/packet/frame inspection and bounded intervals.
- [FFmpeg Formats Documentation](https://ffmpeg.org/ffmpeg-formats.html) — probing, concat, muxer/demuxer, and timestamp-related format options.
- [FFmpeg Filters Documentation](https://ffmpeg.org/ffmpeg-filters.html) — filter requirements, timeline behavior, analysis filters, and transformations.
- [FFmpeg Codecs Documentation](https://ffmpeg.org/ffmpeg-codecs.html) — codec options and implementation-specific constraints.

The documentation describes interfaces and known semantics; it does not identify the cause of a particular failure without artifact-specific evidence.
