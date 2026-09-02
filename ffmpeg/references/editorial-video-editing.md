# Editorial Video Editing

Treat an editorial edit as a sequence of reviewable decisions, not as one opaque FFmpeg command. Preserve source media, use an edit decision list (EDL), render to a new path, and separate technical conformance from human approval.

## Plan before rendering

1. Write the editorial goal, audience, required duration or range, prohibited changes, output contract, and reviewer.
2. Probe all selected streams and establish their timelines, time bases, start times, frame cadence, audio layout, subtitles, and metadata.
3. Use transcripts, scene scores, silence events, and frame samples only to navigate. Verify consequential words, cuts, identities, and context against decoded media.
4. Record each keep/remove/reorder/treatment decision with source range, rationale, evidence locator, confidence, and required review.
5. Validate the EDL before generating a filtergraph: ranges must be ordered, bounded, and compatible with transitions and linked audio.

## Cut and assembly choices

- **Filter-based cuts:** `trim` and `atrim` select ranges but do not reset timestamps. Follow them with `setpts=PTS-STARTPTS` and `asetpts=PTS-STARTPTS` when segments must begin at zero before concatenation.
- **Concat filter:** use for decoded segments in one graph. Corresponding streams must have compatible parameters; normalize geometry, pixel format, sample format/rate, and channel layout deliberately.
- **Concat demuxer:** use an `ffconcat` list for separate files whose streams are suitable for packet-level concatenation. Its `duration`, `inpoint`, and `outpoint` directives have documented timestamp and packet-boundary caveats.
- **Stream-copy cuts:** fast and lossless at the packet level, but start/end precision is constrained by seek points, inter-frame dependencies, timestamps, and muxer behavior. Do not promise frame-accurate editorial cuts without checking the decoded result.
- **Transitions:** overlaps such as `xfade` or `acrossfade` consume timeline duration and require adequate handles. Put the overlap and expected output-duration calculation in the EDL.

Map streams explicitly. Define whether chapters, attachments, data streams, subtitles, language tags, dispositions, and metadata are retained, rewritten, or removed. An omitted `-map` leaves stream selection to automatic rules that may not match editorial intent.

## Treatments

Apply only treatments required by the brief:

- geometry: `crop`, `scale`, `pad`, rotation/orientation handling;
- timing: `fps`, `setpts`, `atempo`, or resampling only with an explicit cadence/sync decision;
- compositing: overlays, masks, titles, or subtitles with rights and readability review;
- picture: deinterlacing, range/color conversion, or grading with source and target color assumptions recorded;
- sound: fades, gain, loudness, noise reduction, and channel mapping under the audio plan.

Keep an intermediate render when it improves reviewability, but avoid unnecessary generations. Record codecs and settings at every lossy boundary.

## Review gates

1. **EDL review:** all consequential cuts and treatments approved.
2. **Technical render review:** expected streams, timestamps, duration, geometry, cadence, color tags, audio format, and decode behavior.
3. **Content review:** opening/closing, every join and transition, titles/subtitles, linked audio, and any high-risk treatment.
4. **Editorial review:** meaning, pacing, continuity, context, accessibility, and approved claims.
5. **Destination review:** playback or import in the intended player, editor, service, or archive workflow.

## Evidence and heuristic boundary

- **Direct evidence:** probe/decode results, recorded EDL ranges, commands, logs, and reviewed samples for this build and artifact.
- **Derived evidence:** expected duration or transition math computed from declared ranges and rounding rules.
- **Heuristic:** transcript alignment, scene/silence candidates, automated crop choices, inferred continuity, or “visually lossless” judgments. Mark and review them.
- **Human decision:** editorial suitability and preservation of meaning require an accountable reviewer.
- **Not established:** a successful render does not prove frame-accurate cuts, correct context, accessibility, rights, sync everywhere, or destination acceptance.

## Official FFmpeg sources

- [ffmpeg Documentation](https://ffmpeg.org/ffmpeg.html) — seeking, stream selection, mapping, filtering, codecs, metadata, and overwrite controls.
- [FFmpeg Filters Documentation](https://ffmpeg.org/ffmpeg-filters.html) — `trim`, `atrim`, timestamp filters, concat, transitions, geometry, subtitles, and audio/video treatments.
- [FFmpeg Formats Documentation](https://ffmpeg.org/ffmpeg-formats.html) — concat demuxer and muxer/container behavior.
- [FFmpeg Utilities Documentation](https://ffmpeg.org/ffmpeg-utils.html) — timeline and duration expressions.

These sources define mechanics. They do not supply an editorial rationale, validate transcript meaning, or guarantee compatibility with a particular destination.
