# FFmpeg Edit Decision Lists

An edit decision list (EDL) is the reviewable source of truth between editorial intent and an FFmpeg render plan. Keep it data-oriented, versioned, and independent of private filesystem paths.

## Canonical semantics

Use opaque asset IDs and identify streams explicitly. For each source, retain probe evidence for stream index, time base, start time, duration, cadence, audio layout, and source digest.

Define ranges as half-open intervals, `[in, out)`, on the selected source stream timeline. State the time unit and precision. Decimal seconds are convenient for review; preserve exact timestamps or integer ticks when frame/sample boundaries matter. Never silently treat timecode, container time, wall-clock time, and frame number as interchangeable.

Each event should record:

- stable event ID and action (`keep`, `remove`, `insert`, or `treatment`);
- source asset and stream references;
- source `in` and `out`, plus any transition handles;
- destination order or lane;
- linked audio/video policy;
- rationale, evidence locators, confidence, and reviewer status;
- transformations, transition type/duration, and expected duration effect;
- whether the cut requires decoded precision or permits packet-level copy;
- verification points around the resulting boundary.

Store commands as generated render records, not as the EDL’s only meaning. Raw paths and shell fragments are unsafe substitutes for structured fields.

## Pre-render validation

Reject or flag an EDL when:

- a source, stream, time unit, or range endpoint is missing;
- `in >= out`, a range falls outside declared source bounds, or rounding behavior is undefined;
- events overlap unintentionally or leave an unexplained gap;
- linked streams use incompatible timelines or omit a sync policy;
- transitions lack sufficient handles or their overlap is absent from duration math;
- concat inputs have unresolved format differences;
- frame/sample-accurate intent is paired with an unverified stream-copy strategy;
- required editorial decisions have no evidence or review status.

Calculate expected output duration from kept ranges, inserts, speed changes, and transition overlaps. Mark the result as derived and declare a tolerance for timestamp/time-base rounding.

## Mapping to FFmpeg

For decoded segment assembly, use `trim`/`atrim`, reset segment timestamps with `setpts`/`asetpts` where required, normalize compatible media parameters deliberately, and join with the concat filter. Map output streams explicitly.

For separate compatible files, the concat demuxer consumes an `ffconcat` list. Its `inpoint` and `outpoint` can include packets outside the requested interval because of inter-frame dependencies and packet boundaries; timestamps can also be adjusted globally. Review the decoded joins.

Fast seek and stream copy may choose seek points or packets that do not correspond to an exact visual/audio edit boundary. Label keyframe/packet status as one of `verified`, `not_verified`, or `not_applicable`; never infer it from a round timestamp.

Record FFmpeg/ffprobe versions, complete generated command, mapping, codec settings, environment-sensitive capabilities, output digest, and acceptance report alongside the rendered artifact.

## Evidence and heuristic boundary

- **Direct evidence:** source probe data, exact EDL fields, reviewed source samples, packet/frame observations, generated command, and output verification records.
- **Derived evidence:** output order and duration computed from declared EDL semantics and a stated rounding rule.
- **Heuristic:** transcript-aligned endpoints, scene/silence candidates, guessed keyframes, or assumed concat compatibility. These must be labeled and tested.
- **Human decision:** rationale, continuity, context, and approval are editorial evidence only when attributed.
- **Not established:** an internally valid EDL does not prove render precision, sync, semantic correctness, rights, or downstream acceptance.

## Official FFmpeg sources

- [ffmpeg Documentation](https://ffmpeg.org/ffmpeg.html) — seeking, timestamps, stream selection/mapping, filtering, and codec-copy behavior.
- [FFmpeg Filters Documentation](https://ffmpeg.org/ffmpeg-filters.html) — `trim`, `atrim`, `setpts`, `asetpts`, concat, `xfade`, and `acrossfade` semantics.
- [FFmpeg Formats Documentation](https://ffmpeg.org/ffmpeg-formats.html) — concat demuxer syntax, `duration`, `inpoint`, `outpoint`, and format behavior.
- [FFmpeg Utilities Documentation](https://ffmpeg.org/ffmpeg-utils.html) — duration and time expression syntax.

The sources define FFmpeg’s timeline and assembly mechanisms. The EDL conventions above are workflow rules; they are not an FFmpeg-native interchange standard.
