# Media Verification and Acceptance

Accept a media artifact from recorded evidence against a declared contract. A zero exit status proves only that one command completed without reporting a fatal error; it does not prove correct streams, complete decode, editorial quality, or destination compatibility.

## Layered acceptance

### 1. Artifact and provenance

Record the output asset ID, digest, size, producing command, source/EDL versions, FFmpeg build, completion status, warning log, and whether the path was new or pre-existing. Confirm the accepted file is the file that was reviewed.

### 2. Structural conformance

Probe the output and compare every required field with the contract:

```sh
ffprobe -v error -show_format -show_streams -show_chapters -of json OUTPUT
```

Check container, stream count/order, codecs, dispositions, language, dimensions, aspect ratios, pixel format, color metadata, cadence, start times, durations, audio sample rate/layout, subtitles, chapters, and metadata policy. Treat absent or ambiguous fields explicitly.

### 3. Processing-path check

Exercise all expected audio/video streams through FFmpeg and preserve errors:

```sh
ffmpeg -v error -i OUTPUT -map '0:v?' -map '0:a?' -f null -
```

This can expose decode or timeline faults in FFmpeg’s processing path. It does not exercise every player, subtitle/data stream, hardware decoder, display pipeline, or network/service ingest path.

### 4. Signal and timing checks

Use only metrics tied to criteria: frame/packet counts, start/end timestamps, cadence, A/V offset at declared points, black/freeze candidates, audio statistics, loudness, peaks, or silence events. Record filters, thresholds, intervals, and tolerances. Re-measure the rendered artifact rather than assuming encoder/filter targets were met.

### 5. Content review

Review the opening and closing, every cut/join/transition/treatment, titles/subtitles, high-risk regions, representative motion and detail, loud/quiet passages, and declared sync points. Use full-resolution frames or short clips where contact sheets are insufficient. Attribute reviewer and time.

### 6. Editorial and downstream acceptance

An accountable reviewer decides whether meaning, pacing, continuity, intelligibility, accessibility, and the brief are satisfied. Then import, play, upload, or validate the exact artifact in the intended destination. Record destination identity/version, settings, result, warnings, and any transformed derivative.

## Acceptance record

For every criterion, capture:

- criterion and tolerance;
- evidence method and exact artifact/interval;
- observed value or attributed observation;
- status: `pass`, `fail`, `blocked`, or `not_applicable`;
- reviewer and date;
- exception owner and rationale, if any.

The final verdict is `accepted`, `rejected`, or `blocked`. Do not convert an untested criterion into a pass. Any post-review change invalidates affected evidence and requires re-verification.

Minimize reports before sharing: remove private paths, personal names, account identifiers, unnecessary transcript excerpts, and embedded metadata.

## Evidence and heuristic boundary

| Classification | Boundary |
|---|---|
| Direct evidence | Probe/decode output, measurements, samples, destination result, and attributed review for the exact accepted artifact. |
| Derived evidence | Contract comparisons and timing calculations with a stated method and tolerance. |
| Heuristic | Sparse sampling, automated quality scores, detector events, or compatibility inferred from a similar file. Label as supporting evidence only. |
| Human judgment | Editorial quality, intelligibility, context, and visual acceptability require attributed review. |
| Not established | Universal playback, rights, long-term preservation, accessibility, or unsampled-content correctness unless separately tested. |

## Official FFmpeg sources

- [ffprobe Documentation](https://ffmpeg.org/ffprobe.html) — machine-readable structural, packet, and frame inspection.
- [ffmpeg Documentation](https://ffmpeg.org/ffmpeg.html) — stream mapping, decoding/transcoding, progress, logging, and exit behavior context.
- [FFmpeg Filters Documentation](https://ffmpeg.org/ffmpeg-filters.html) — measurable video/audio analysis filters and their parameters.
- [FFmpeg Formats Documentation](https://ffmpeg.org/ffmpeg-formats.html) — muxer/demuxer behavior and container-specific options.
- [FFmpeg Codecs Documentation](https://ffmpeg.org/ffmpeg-codecs.html) — decoder/encoder options and capabilities.

Official documentation supports the mechanics of checks. It does not define the project’s acceptance criteria or guarantee behavior outside the recorded build and destination.
