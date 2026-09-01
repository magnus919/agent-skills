# Intermediate Workflows

## Inspection and selective conversion

Start with `ffprobe`, then make selection explicit. For scripts, use JSON and fail if the expected stream is absent. For a simple conversion:

```sh
ffmpeg -i input.mov -map 0:v:0 -map 0:a:0 -c:v libx264 -c:a aac output.mp4
```

For a compatible remux:

```sh
ffmpeg -i input.mkv -map 0 -c copy output.mp4
```

Do not call remuxing a conversion of the encoded media. It changes packaging only.

## Trim and seek

`-ss` can be placed before input for fast input seeking or after input for output-side behavior with different accuracy and cost. `-t` limits duration; `-to` specifies an endpoint in the relevant command context. Test the actual cut, especially with inter-frame codecs, nonzero start timestamps, and audio.

```sh
ffmpeg -ss 00:01:00 -i input.mp4 -t 00:00:20 -c copy quick-cut.mp4
```

Stream-copy cuts may begin on keyframe boundaries and can preserve awkward timestamps. Re-encode when frame-accurate filtering or predictable normalization is more important than speed.

## Concatenation

There are distinct mechanisms:

- The concat demuxer reads a script describing files and is appropriate when streams are compatible and the files meet its safety and timestamp assumptions.
- The concat filter operates on decoded audio/video and can join segments after normalizing dimensions, formats, and timestamps.
- The concat protocol is physical byte/resource concatenation and is not a general-purpose media join.

Never choose a concat method solely because files share an extension. Inspect codecs, dimensions, frame rates, sample rates, channel layouts, time bases, and metadata.

## Metadata and subtitles

Metadata can be copied, mapped, or rewritten. FFmpeg's format documentation describes the `ffmetadata` muxer/demuxer for round-tripping metadata. Subtitle streams can be copied when the target container supports them, or rendered into video with a subtitle filter when permanent pixels are intended. Those are different deliverables.

## Batch scripting

Use shell quoting carefully and never construct commands by concatenating untrusted filenames into `sh -c`. Prefer arrays in Bash/Zsh, null-delimited file discovery, and explicit output paths. Probe each result and preserve stderr logs. Use `-n` to refuse overwriting during exploratory runs; use `-y` only when an overwrite policy is intentional.

A robust batch worker records input, exact command, FFmpeg version, exit status, output path, and a post-run probe. A zero exit status is not a complete acceptance gate if the downstream consumer has stricter requirements.

## Pipes and streaming

An output URL can be a file, pipe, or network protocol. `-f` can force the muxer when the output URL does not provide a useful extension. `-re` is relevant when reading a file at approximately its native rate for streaming demonstrations, not as a universal speed setting. Network operations need bounded timeouts, known protocols, authentication handling, and a safe destination.

The protocols manual documents protocol-specific options, including `rw_timeout`, protocol whitelists, UDP, and concat. Validate the receiving side independently.

SOURCES (LAYER 3 NAVIGATION)
https://ffmpeg.org/ffmpeg.html
 -> Seeking, stream copy, mapping, input/output option scope, and transcoding.

https://ffmpeg.org/ffmpeg-formats.html
 -> Demuxers, muxers, concat-related format behavior, metadata, probing, and interleaving.

https://ffmpeg.org/ffmpeg-protocols.html
 -> File, pipe, concat, UDP, HTTP, and network protocol options.

https://ffmpeg.org/ffmpeg-utils.html
 -> Time expressions and quoting/escaping needed for scripts.

https://shotstack.io/learn/how-to-use-ffmpeg/
 -> Secondary practical examples; verify all commands against current official manuals.

https://en.wikibooks.org/wiki/FFMPEG_An_Intermediate_Guide
 -> Secondary intermediate topic map; examples are version/build-sensitive.
