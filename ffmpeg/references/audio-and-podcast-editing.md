# Audio and Podcast Editing

Separate mechanical assembly, signal processing, and editorial judgment. FFmpeg can measure and transform audio; it cannot decide whether a pause, breath, correction, tone, identity, or statement should be removed.

## Intake and plan

Probe each candidate stream and record codec, sample format/rate, channel count/layout, time base, start/duration, disposition, and language metadata. Define the output contract, target loudness policy if one exists, required channel layout, allowed repairs, prohibited edits, and review owner.

Divide proposed work into:

- **Mechanical:** explicit range cuts, reorder, fades, slate/tone removal, channel mapping, resampling, and encoding.
- **Signal repair:** gain, equalization, hum/noise reduction, de-essing, dynamics, clipping prevention, or dropout repair.
- **Editorial:** removing speech, changing sequence, shortening pauses, selecting takes, or altering context.

Put source ranges and evidence in a podcast edit plan or EDL. A transcript is a navigation aid; verify words, timing, speaker changes, and context by listening to the source.

## Measurement and candidate detection

Relevant filters include:

- `astats` for time-domain audio statistics;
- `volumedetect` for volume statistics;
- `ebur128` for EBU R128 analysis and metadata/log output;
- `loudnorm` for EBU R128 normalization and measured values;
- `silencedetect` for threshold- and duration-based silence candidates;
- `aphasemeter` for channel phase measurements where applicable.

Record the exact interval, filter options, channel mode, FFmpeg build, and unfiltered source. Noise floors, breaths, room tone, music, cross-talk, and codec artifacts can invalidate a generic threshold.

For loudness normalization, a measured first pass followed by a parameterized second pass is more reviewable than assuming one-pass behavior meets a delivery policy. Verify the rendered output again; a filter’s reported target is not acceptance evidence by itself.

## Editing and processing

- Use `atrim` for ranges and `asetpts=PTS-STARTPTS` when a segment needs a zero-based timeline.
- Use the concat filter after making sample rate, sample format, and channel layout deliberate.
- Use `afade`/`acrossfade` only when their duration and overlap are editorially approved.
- Treat `silenceremove` as an editorial transform, not harmless cleanup.
- Apply `highpass`, `lowpass`, `afftdn`, `arnndn`, compression, limiting, or normalization only after a bounded comparison. Filter availability and behavior depend on the local build and options.
- Avoid repeated lossy encoding. Keep a suitable intermediate when multiple review passes are required.
- Map audio and attached video/subtitle streams explicitly; define metadata and chapter retention.

## Listening acceptance

Listen to the opening and closing, every cut/fade/transition, all repaired regions, representative loud and quiet passages, channel fold-down if relevant, and any section flagged by measurements. Check speech intelligibility, clicks, truncation, pumping, tonal shifts, room-tone jumps, phase issues, context, and sync with video. Test the intended destination.

Keep review records privacy-safe: use opaque speaker labels, quote only the minimum required text, and do not publish raw transcripts, private paths, or embedded tags.

## Evidence and heuristic boundary

| Classification | Boundary |
|---|---|
| Direct evidence | Probe fields, decoded samples, filter measurements, commands, logs, and attributed listening observations for declared intervals. |
| Threshold evidence | Silence, loudness, clipping, or phase candidates under explicitly recorded filter settings. |
| Heuristic | Speaker labels, transcript timing, “noise-only” regions, acceptable pause length, or a preset suitable for another recording. |
| Editorial judgment | Whether an edit preserves meaning, consent, tone, and continuity. This requires accountable listening review. |
| Not established | Whole-program quality from a few measurements, speaker identity, legal clearance, accessibility, or destination acceptance from an FFmpeg exit status. |

## Official FFmpeg sources

- [ffprobe Documentation](https://ffmpeg.org/ffprobe.html) — audio stream and packet/frame inspection.
- [ffmpeg Documentation](https://ffmpeg.org/ffmpeg.html) — mapping, filtering, codecs, timestamps, and transcoding.
- [FFmpeg Filters Documentation](https://ffmpeg.org/ffmpeg-filters.html) — `atrim`, `asetpts`, concat, fades, silence, statistics, loudness, equalization, denoising, dynamics, and resampling filters.
- [FFmpeg Resampler Documentation](https://ffmpeg.org/ffmpeg-resampler.html) — resampling and rematrixing options.
- [FFmpeg Codecs Documentation](https://ffmpeg.org/ffmpeg-codecs.html) — codec-specific capabilities and options.

Official documentation establishes mechanics, not local component availability, editorial correctness, or compliance with an external delivery specification.
