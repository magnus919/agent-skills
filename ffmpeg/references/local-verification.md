# Local Verification Dossier

**Access/test date:** 2026-09-01
**Host:** macOS
**Binary:** Homebrew-installed `ffmpeg`
**Version:** FFmpeg 8.1.2, libavutil 60.26.102, libavcodec 62.28.102
**Build evidence:** `ffmpeg -version` reports `--enable-videotoolbox`, `--enable-audiotoolbox`, libx264, libx265, libsvtav1, libvmaf, libopus, libmp3lame, libdav1d, and libvpx.

## Inventory

The local build reported 488 filters, 201 encoders, and 2 hardware acceleration methods in the captured inventories. The exact lists are preserved in `local-filters.txt`, `local-encoders.txt`, and `local-hwaccels.txt`. Availability is build-specific: never assume a filter, encoder, protocol, or hardware backend exists just because an online example uses it.

## Successful experiment

A synthetic 320x180, 30 fps test video and 48 kHz mono sine-wave audio were generated with lavfi and encoded to MP4 using libx264 and native AAC. `ffprobe` verified a 2.00-second MP4 containing H.264 video and AAC audio. The source log is `../03-dossiers/local-probe.json` and the command output is recorded in the run log outside this dossier.

The intended follow-up transcode used `-ss 0.5 -t 0.75`, scaling to 160 pixels wide, reducing to 15 fps, and adding `drawtext`. It failed before writing output because this local build reported `No such filter: 'drawtext'`. This is useful evidence: filter names and compiled capabilities must be checked with `ffmpeg -filters` or `ffmpeg -h filter=<name>` before placing them in automation. The failed and successful run logs were preserved in the local study record; their host-specific paths are intentionally omitted here.

## Verification lesson

A command that looks portable can still fail at the filter-availability boundary. The correct response is not to silently substitute a different filter or claim success. Inspect the local build, choose an available equivalent, or install/use a build with the required feature, then rerun and probe the resulting media.

## Reproduction commands

```sh
ffmpeg -version
ffmpeg -filters
ffmpeg -encoders
ffmpeg -hwaccels
ffprobe -v error -show_format -show_streams -of json input.mp4
```

SOURCES (LAYER 3 NAVIGATION)
https://ffmpeg.org/ffprobe.html
 -> Official description of machine-readable media inspection.

https://ffmpeg.org/ffmpeg.html
 -> Official command-line processing model and option semantics.
