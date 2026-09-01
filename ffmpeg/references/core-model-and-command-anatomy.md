# Core Model and Command Anatomy

## The pipeline

The `ffmpeg` command line accepts global options, one or more input blocks, and one or more output blocks:

```sh
ffmpeg [global_options] {[input_options] -i input_url} ... {[output_options] output_url} ...
```

Options generally apply to the next input or output, so order matters. Input and output indexes are zero-based. Stream specifiers such as `:v`, `:a`, `:s`, and `:1` narrow an option to a type or stream index.

The conceptual pipeline is:

```text
input URL -> protocol/IO -> demuxer -> streams -> decode -> filters -> encode -> muxer -> output URL
```

Stream copy skips decode, filtering, and encode for the copied stream. It is therefore fast and lossless with respect to the encoded stream, but cannot perform transformations on that stream.

## Selection and mapping

Automatic stream selection is convenient for simple files but unsafe for multi-input work. `-map 0:v:0 -map 1:a:0` selects the first video from input 0 and first audio from input 1. `-map 0` asks for all streams from input 0, subject to output-format limits. A complex filtergraph's labeled outputs must be mapped exactly once.

Use per-stream options deliberately:

```sh
ffmpeg -i input.mkv -map 0:v:0 -map 0:a:0 -c:v libx264 -crf 20 -c:a aac -b:a 160k output.mp4
```

This is an illustrative transcode, not a universal quality or bitrate recommendation. The correct settings depend on source, target, motion, delivery constraints, and playback support.

## Container and codec are different decisions

A container packages streams. A codec encodes one stream. Renaming a file does not convert it. A remux can change packaging without re-encoding:

```sh
ffmpeg -i input.mkv -map 0 -c copy output.mp4
```

The command can fail or produce an unsuitable file when the selected streams, metadata, or timing do not fit the target container. Probe both input and output.

## Quality and generation loss

Re-encoding is required for filtering, changing many codec properties, or adapting an incompatible stream. Each lossy generation may discard information. Prefer stream copy when the operation is only a compatible container change, but do not force copy when the target needs a different codec, pixel format, sample format, or timing structure.

## Time and timestamps

Video and audio use timestamps expressed in stream-specific time bases. FFmpeg documentation defines a time base as the fundamental time unit for frame timestamps. Fixed-frame-rate video commonly uses a time base related to the frame rate, while an MP4 stream may use a finer muxer time base. Do not compare raw PTS integers from different streams without rescaling them into a common time unit.

Seeking, trimming, synchronization, and concat problems are timestamp problems until proven otherwise. Record the relevant `start_time`, `duration`, `time_base`, frame rate, and packet/frame behavior with `ffprobe`.

## Probe before and after

```sh
ffprobe -v error -show_format -show_streams -of json input.mkv
ffprobe -v error -show_entries stream=index,codec_type,codec_name,width,height,sample_rate,channels,time_base,duration -of json output.mp4
```

Machine-readable output is preferable in scripts. Treat human-readable stderr as diagnostic evidence, not as a stable parsing interface.

SOURCES (LAYER 3 NAVIGATION)
https://ffmpeg.org/ffmpeg.html
 -> Command syntax, option scope, stream selection, stream copy, transcoding, and mapping.

https://ffmpeg.org/ffprobe.html
 -> Inspection, stream specifiers, machine-readable writers, and intervals.

https://ffmpeg.org/ffmpeg-codecs.html
 -> Codec options, rate control, time bases, and error detection.

https://ffmpeg.org/ffmpeg-formats.html
 -> Demuxers, muxers, probing, interleaving, and timestamp-related format behavior.

https://ffmpeg.org/ffmpeg-utils.html
 -> Duration syntax, rational numbers, expressions, and quoting/escaping.
