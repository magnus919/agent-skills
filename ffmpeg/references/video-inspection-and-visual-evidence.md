# Video Inspection and Visual Evidence

Inspect video in bounded layers: structural metadata, decoded technical signals, sampled frames or clips, then semantic review. Keep the source ID, stream index, timestamps, commands, build, and coverage limits attached to every artifact.

## Inspection sequence

1. **Probe the stream.** Record dimensions, sample/display aspect ratio, pixel format, field order, nominal and average frame rates, time base, start/duration, disposition, rotation/display metadata, and color fields.
2. **Define the question.** Examples: “Is there a black interval near the head?” or “Does the approved title appear in the sampled opening?” Avoid an unbounded request to “check the video.”
3. **Choose declared coverage.** Use specific timestamps, a fixed cadence, bounded intervals, or event-driven candidates. Record the interval, cadence, number of samples, and omissions.
4. **Decode evidence to a new review location.** A typical single-frame extraction is:

```sh
ffmpeg -ss START -i INPUT -map 0:v:0 -frames:v 1 -an REVIEW_FRAME.png
```

For cadence sampling, use the documented `fps` filter; for representative candidates, `thumbnail` can select a frame from each batch and `tile` can assemble a contact sheet. Preserve each sample’s source timestamp rather than relying only on sequential filenames.
5. **Review at the right resolution.** Contact sheets establish overview, not fine detail. Use full-resolution frames or short clips for text, motion, transitions, sync, compression artifacts, and color judgments.

Input `-ss` seeks to a nearby seek point; with transcoding, accurate seek processing normally decodes and discards material before the requested position. Container indexing, timestamps, variable frame rate, and output rounding can still affect the exact frame. Record the observed frame timestamp when precision matters.

## Technical aids

Useful video filters include:

- `showinfo` for per-frame timestamps, format, type, and checksums.
- `signalstats` for frame signal statistics.
- `blackdetect` or `blackframe` for threshold-based black candidates.
- `freezedetect` for threshold- and duration-based freeze candidates.
- `scdet` for scene-change scores and candidate events.
- `cropdetect` for suggested crop values.

Treat every detector as a candidate generator. Record thresholds, durations, filter order, and any color/range conversion performed before the detector. A detector’s log line is not a semantic judgment.

## Visual review packet

For each sample include:

- opaque asset ID and selected stream;
- source and observed timestamps;
- extraction command and FFmpeg build;
- whether the image was scaled, cropped, deinterlaced, tone-mapped, or color-converted;
- the question being tested and reviewer observation;
- coverage statement and known blind spots.

Avoid embedding private source paths, personal names, faces, transcript text, or location metadata unless required and authorized. Share the smallest packet that answers the review question.

## Evidence and heuristic boundary

| Classification | Defensible statement |
|---|---|
| Direct evidence | Probe fields for the recorded stream; decoded pixels and filter measurements at the listed timestamps under the recorded command/build. |
| Threshold evidence | A configured detector emitted a candidate under stated thresholds. This is reproducible, but threshold-dependent. |
| Human observation | A reviewer observed a visible feature in the supplied sample. Attribute it and preserve the sample. |
| Heuristic | A sparse sample represents an interval; a scene score denotes an editorial cut; a crop suggestion is compositionally correct. Label and review these assumptions. |
| Not established | Absence throughout unsampled material, speaker/person identity, intent, rights, complete accessibility, exact color on another display, or downstream playback quality. |

Frame samples cannot prove what happens between samples. Extracted stills can also differ from target playback because of scaling, color management, HDR handling, deinterlacing, and display behavior.

## Official FFmpeg sources

- [ffprobe Documentation](https://ffmpeg.org/ffprobe.html) — stream/frame inspection and bounded read intervals.
- [ffmpeg Documentation](https://ffmpeg.org/ffmpeg.html) — seeking, stream mapping, frame limits, and transcoding behavior.
- [FFmpeg Filters Documentation](https://ffmpeg.org/ffmpeg-filters.html) — `fps`, `thumbnail`, `tile`, `showinfo`, `signalstats`, `blackdetect`, `freezedetect`, `scdet`, and `cropdetect`.
- [FFmpeg Utilities Documentation](https://ffmpeg.org/ffmpeg-utils.html) — time-duration and rate syntax.

The documentation supports option and filter semantics. It does not validate a chosen sampling plan, detector threshold, semantic interpretation, or display pipeline.
