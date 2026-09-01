# Command Cookbook

These are learning commands, not universal production defaults. Check the installed build, input streams, target requirements, and output with `ffprobe`.

## Inspect

```sh
ffprobe -v error -show_format -show_streams -of json input.mp4
```

## List local capabilities

```sh
ffmpeg -hide_banner -formats
ffmpeg -hide_banner -codecs
ffmpeg -hide_banner -filters
ffmpeg -hide_banner -encoders
ffmpeg -hide_banner -hwaccels
```

## Remux without re-encoding

```sh
ffmpeg -n -i input.mkv -map 0 -c copy output.mp4
```

## Explicit transcode

```sh
ffmpeg -n -i input.mov -map 0:v:0 -map 0:a:0 \
  -c:v libx264 -crf 20 -preset medium \
  -c:a aac -b:a 160k output.mp4
```

## Scale and resample

```sh
ffmpeg -n -i input.mp4 -vf 'scale=1280:-2' -ar 48000 output.mp4
```

## Overlay a second input

```sh
ffmpeg -n -i video.mp4 -i logo.png \
  -filter_complex '[0:v][1:v]overlay=20:20[v]' \
  -map '[v]' -map 0:a:0 -c:v libx264 -c:a copy output.mp4
```

## Fast exploratory cut

```sh
ffmpeg -n -ss 00:01:00 -i input.mp4 -t 00:00:20 -c copy cut.mp4
```

## Extract audio

```sh
ffmpeg -n -i input.mp4 -map 0:a:0 -vn -c:a flac output.flac
```

## Generate a synthetic test asset

```sh
ffmpeg -f lavfi -i 'testsrc2=size=320x180:rate=30' \
  -f lavfi -i 'sine=frequency=440:sample_rate=48000' \
  -t 2 -c:v libx264 -pix_fmt yuv420p -c:a aac test.mp4
```

## Diagnostic null output

```sh
ffmpeg -hide_banner -loglevel verbose -i input.mp4 -f null -
```

## Build-aware filter check

```sh
ffmpeg -filters | grep -E 'scale|fps|drawtext|subtitles'
ffmpeg -h filter=scale
```

SOURCES (LAYER 3 NAVIGATION)
https://ffmpeg.org/ffmpeg.html
 -> Primary command syntax, mapping, copy/transcode, seeking, and filtering options.

https://ffmpeg.org/ffprobe.html
 -> Primary inspection and machine-readable output.

03-dossiers/local-verification.md
 -> Commands actually exercised on the local FFmpeg 8.1.2 build.
