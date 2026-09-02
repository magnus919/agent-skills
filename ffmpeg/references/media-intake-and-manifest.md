# Media Intake and Manifest

Use an intake manifest before inspecting or editing supplied or otherwise authorized media. The manifest is a record of what was received, what the local tools reported, and what the output must satisfy; it is not a rights determination or an editorial brief.

## Minimum intake

1. Assign a non-identifying `asset_id`. Keep real names, account identifiers, and private storage paths out of shareable records.
2. Record authorization scope, permitted operations, retention limits, and who may review the media. If authority is unclear, stop.
3. Preserve the source. Work from a copy or render to a new destination; do not normalize, rename, or overwrite the only original.
4. Record source identity separately from content claims: byte size, whole-file digest if available, acquisition date, and a private locator. A filename extension is only a hint.
5. Capture the exact `ffprobe` and FFmpeg versions used. Build options and enabled libraries can change available codecs, filters, and behavior.
6. Probe structure without decoding the entire asset:

```sh
ffprobe -v error -show_format -show_streams -show_chapters -of json INPUT
```

Preserve absent fields as absent or `null`; do not invent duration, frame rate, language, or channel layout. For ambiguous or damaged inputs, record probe warnings and any non-default `-probesize` or `-analyzeduration` used.

## Manifest fields that matter

- **Source:** opaque asset ID, private locator, size, digest, preservation status.
- **Tool context:** `ffprobe` version, FFmpeg version, build identity, command, exit status, warning-log locator.
- **Container:** reported format names, start time, duration, bit rate, chapters, and tags needed for the task.
- **Streams:** index, codec type/name, time base, start time, duration, disposition, language, and stream-specific fields such as dimensions, pixel format, field order, color metadata, sample rate, channel layout, and subtitle type.
- **Timing:** whether durations come from the container, stream metadata, counted packets/frames, or another declared method.
- **Output contract:** required container, stream set and order, codecs, geometry, frame cadence, audio layout/rate, duration tolerance, subtitle/metadata policy, file-size constraint, and target player/editor/service.
- **Assumptions and unknowns:** each assumption, why it is being used, risk, and how it will be tested.

Probe output may contain identifying tags, device data, creation times, titles, comments, and private paths. Store raw output in the restricted task workspace; publish only a minimized/redacted derivative.

## Output-contract discipline

Express acceptance criteria before rendering. Prefer measurable criteria such as “one H.264 video stream and one AAC stereo audio stream,” “1920×1080,” or “duration within the declared tolerance.” Keep subjective criteria such as pacing or intelligibility as separate human-review items. “Plays for me” and “command exited zero” are not output contracts.

## Evidence and heuristic boundary

| Classification | What may be claimed |
|---|---|
| Direct evidence | The exact probe output, warnings, command, build, source digest, and authorization record captured for this asset. |
| Derived evidence | Values calculated from recorded fields using a stated formula and rounding rule. Label them as derived. |
| Heuristic | Meaning inferred from an extension, filename, tags, nominal frame rate, sampled content, or prior behavior of a destination. Mark it as an assumption. |
| Not established | Rights ownership, complete decodability, semantic content, editorial quality, sync, or destination compatibility. Probe metadata alone establishes none of these. |

A detector or probe result is evidence about this input under the recorded build and options. It is not universal evidence about every copy, FFmpeg build, decoder, or playback environment.

## Official FFmpeg sources

- [ffprobe Documentation](https://ffmpeg.org/ffprobe.html) — stream/container inspection, output writers, counting, intervals, and probe options.
- [FFmpeg Formats Documentation](https://ffmpeg.org/ffmpeg-formats.html) — demuxer/muxer behavior, probing controls, and format-specific options.
- [ffmpeg Documentation](https://ffmpeg.org/ffmpeg.html) — option scope, stream selection, mapping, transcoding, and overwrite behavior.
- [FFmpeg Utilities Documentation](https://ffmpeg.org/ffmpeg-utils.html) — duration, size, rate, and related value syntax.

These official pages define FFmpeg interfaces and documented behavior. They do not prove that a local build includes a component, that metadata is truthful, or that an output meets an editorial or downstream requirement.
