# Synthetic Media Fixture Battery

Use the fixture battery when an FFmpeg change needs real-media evidence for timestamp, concat, audio, subtitle, or visual-sampling boundaries. The generator creates non-personal media in a new task-local directory; generated binaries are not repository fixtures and must not be committed.

## Generate fixtures

```sh
scripts/generate-media-fixtures /tmp/ffmpeg-fixtures --json
```

The command refuses a non-empty directory and bounds every FFmpeg/FFprobe command. `fixture-manifest.json` records the exact build, generators, digests, probes, expected properties, environment-specific observations, and limitations.

## Covered boundaries

| Fixture group | Intended evidence |
|---|---|
| GOP source, stream-copy cut, decoded cut | Packet/keyframe-limited copying remains distinct from decoded precision |
| Irregular frame selection and offset/drift candidate | Container rates and stream durations are not a complete account of cadence or sync |
| Compatible pair and concat output | Concat-demuxer success for the exact recorded streams and build |
| Incompatible concat candidate | Dimensions, cadence, and sample-rate differences cause pre-concat rejection |
| Audio analysis, speech-like, and faded WAVs | Declared silence/over-range regions, a frequency-modulated voiced-like source, and a mechanical fade output for bounded measurement tests |
| SRT and subtitle-stream MKV | Subtitle source and explicit stream preservation; burn-in is exercised when the local filter exists and otherwise recorded unavailable |
| Three boundary PNGs | Samples around one timestamp with an explicit no-whole-video-claim boundary |

Portable assertions describe generator and workflow invariants. Probe values, packet placement, encoded durations, and filter behavior remain environment observations tied to the manifest's FFmpeg build.

## Test use

Tests should select the smallest fixture group that exercises the claimed behavior. Do not regenerate the full battery for a unit test that can use structured fake probe data. When a test relies on actual FFmpeg behavior:

- retain the manifest and exact command;
- assert the intended success or rejection boundary;
- allow declared timestamp/time-base tolerance rather than an invented exact decimal;
- label silence, clipping, and sparse-frame outputs as candidates;
- separate subtitle-stream presence from burn-in or player rendering;
- never generalize one build's result to another environment.
