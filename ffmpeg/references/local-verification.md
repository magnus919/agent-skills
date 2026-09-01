# Local Verification Dossier

**Access/test date:** 2026-09-01
**Host:** macOS
**Binary:** Homebrew-installed `ffmpeg`
**Version:** FFmpeg 8.1.2, libavutil 60.26.102, libavcodec 62.28.102
**Build evidence:** `ffmpeg -version` reports `--enable-videotoolbox`, `--enable-audiotoolbox`, libx264, libx265, libsvtav1, libvmaf, libopus, libmp3lame, libdav1d, and libvpx.

Every observation below is reproducible with the commands in this document on any build; nothing here relies on an artifact outside this skill. These are host-specific observations from one build, not portable capability claims.

## Inventory

The local build reported 481 filter entries, 192 encoders, and 1 hardware acceleration method (VideoToolbox) from the inventories listed under "Reproduction commands". Counts and contents are build-specific: never assume a filter, encoder, protocol, or hardware backend exists just because an online example uses it. `scripts/ffmpeg-preflight --filter NAME --encoder NAME --hwaccel NAME` answers the same question for a specific build without printing the full inventories.

## Successful experiment

A synthetic 320x180, 30 fps test video and 48 kHz mono sine-wave audio were generated with lavfi and encoded to MP4 using libx264 and native AAC:

```sh
ffmpeg -f lavfi -i 'testsrc2=size=320x180:rate=30' \
  -f lavfi -i 'sine=frequency=440:sample_rate=48000' \
  -t 2 -c:v libx264 -pix_fmt yuv420p -c:a aac test.mp4
```

`ffprobe -v error -show_format -show_streams -of json test.mp4` verified a 2.00-second MP4 containing H.264 video and AAC audio. The command is deterministic (lavfi sources), so rerunning it reproduces the evidence on any build with libx264 and the AAC encoder.

## Missing-filter experiment

The intended follow-up transcode used `-ss 0.5 -t 0.75`, scaling to 160 pixels wide, reducing to 15 fps, and adding `drawtext`:

```sh
ffmpeg -ss 0.5 -t 0.75 -i test.mp4 -vf 'scale=160:-2,fps=15,drawtext=text=Hi' -c:a copy test-small.mp4
```

It failed before writing output because this local build reports `No such filter: 'drawtext'`. The same build confirms the absence with `ffmpeg -filters | grep -w drawtext` (no match) and `scripts/ffmpeg-preflight --filter drawtext` (reported absent). This is useful evidence: filter names and compiled capabilities must be checked with `ffmpeg -filters`, `ffmpeg -h filter=<name>`, or the preflight before placing them in automation.

## Verification lesson

A command that looks portable can still fail at the filter-availability boundary. The correct response is not to silently substitute a different filter or claim success. Inspect the local build, choose an available equivalent, or install/use a build with the required feature, then rerun and probe the resulting media.

## Reproduction commands

```sh
ffmpeg -version
ffmpeg -hide_banner -filters
ffmpeg -hide_banner -encoders
ffmpeg -hide_banner -hwaccels
ffprobe -v error -show_format -show_streams -of json test.mp4
```

SOURCES (LAYER 3 NAVIGATION)
https://ffmpeg.org/ffprobe.html
 -> Official description of machine-readable media inspection.

https://ffmpeg.org/ffmpeg.html
 -> Official command-line processing model and option semantics.
