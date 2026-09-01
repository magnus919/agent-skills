# Media Research Source Index

Use this index to connect a media claim to the strongest available source. Prefer official documentation for FFmpeg semantics, local evidence for installed capability, controlled experiments for uncertain behavior, and attributed review for editorial judgments.

## Official FFmpeg sources

| Claim area | Official source | Supports | Does not establish |
|---|---|---|---|
| CLI option scope, seeking, stream selection, mapping, filtering, metadata, overwrite behavior | [ffmpeg Documentation](https://ffmpeg.org/ffmpeg.html) | Documented command-line semantics and processing model | Local component availability, editorial correctness, or destination acceptance |
| Format, stream, packet, frame, interval, and output-writer inspection | [ffprobe Documentation](https://ffmpeg.org/ffprobe.html) | Probe fields, selection, counting, intervals, and machine-readable output | Truth of embedded metadata, complete decode, or semantic content |
| Demuxers, muxers, concat, probing, and format-specific behavior | [FFmpeg Formats Documentation](https://ffmpeg.org/ffmpeg-formats.html) | Documented container and format options | Universal player/service support or validity of a specific damaged file |
| Audio/video filters, timelines, analysis, transforms, and metrics | [FFmpeg Filters Documentation](https://ffmpeg.org/ffmpeg-filters.html) | Filter parameters, outputs, and documented constraints | Suitability of thresholds, perceptual quality, or editorial intent |
| Encoder and decoder options | [FFmpeg Codecs Documentation](https://ffmpeg.org/ffmpeg-codecs.html) | Codec-specific controls exposed by FFmpeg | Presence in a local build, conformance of every output, or destination policy |
| Resampling and rematrixing | [FFmpeg Resampler Documentation](https://ffmpeg.org/ffmpeg-resampler.html) | `libswresample` options and documented behavior | Listening quality or correctness of a chosen channel policy |
| Scaling, pixel conversion, and dithering | [FFmpeg Scaler Documentation](https://ffmpeg.org/ffmpeg-scaler.html) | `libswscale` options and conversion controls | End-to-end color accuracy on an untested display pipeline |
| Time, duration, rate, size, color, and expression syntax | [FFmpeg Utilities Documentation](https://ffmpeg.org/ffmpeg-utils.html) | Shared value and expression syntax | The correct editorial timebase or rounding policy for a project |
| Device and protocol interfaces | [FFmpeg Devices Documentation](https://ffmpeg.org/ffmpeg-devices.html) and [FFmpeg Protocols Documentation](https://ffmpeg.org/ffmpeg-protocols.html) | Documented input/output devices and protocol options | Authorization, network safety, availability, or reliability in a given environment |

The website reflects a documented FFmpeg version that may differ from an installed binary. Capture `ffmpeg -version`, `ffprobe -version`, build configuration, and relevant local inventories before making availability claims.

## Evidence hierarchy

1. **Artifact-specific direct evidence:** exact probe/decode output, packets/frames, measurements, logs, samples, destination results, and attributed review tied to an asset digest.
2. **Official FFmpeg documentation:** primary source for documented interfaces and semantics; cite the page and, when consequential, the option/filter section and access date.
3. **Controlled local experiment:** fixture, digest, command, build, environment, raw result, expected result, and limitations. Reproduction supports only the tested conditions.
4. **External specification or destination documentation:** normative format/delivery requirement. It does not prove a particular encoder output or ingest result; test both.
5. **Secondary explanation:** useful for discovery, never stronger than the primary source it interprets.
6. **Heuristic or editorial convention:** label it, explain why it is reasonable, and assign a reviewer/test.

## Claim-record pattern

For consequential claims, record:

- claim and classification (`direct`, `derived`, `documented`, `experimental`, `heuristic`, or `human_review`);
- source URL or evidence locator;
- FFmpeg version/build and command where applicable;
- asset/fixture ID and bounded interval;
- observed result, confidence, assumptions, and counter-evidence;
- what the evidence does **not** establish.

Do not paste private URLs, credentials, absolute paths, personal names, raw transcripts, or identifying metadata into public research records. Use opaque IDs and restricted evidence locators.

## Evidence and heuristic boundary

Official documentation is evidence for documented behavior, not proof that the local build implements a feature or that a specific command produced the intended artifact. Local inventories establish availability only for that build. Experiments establish observations only for their fixture and conditions. Automated scores and detector events are measurements under declared parameters, not semantic truth. Editorial quality, meaning, identity, consent, and rights require appropriate human or authoritative evidence outside FFmpeg.
