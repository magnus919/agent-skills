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

`-ss` before the input is input seeking: the demuxer jumps to the nearest seek point before the target, which is fast. `-ss` after the input (before the output) is output seeking: FFmpeg decodes and discards from the stream start until the target, which is slow for late cut points. `-t` limits duration; `-to` specifies an endpoint in the relevant command context. Test the actual cut, especially with inter-frame codecs, nonzero start timestamps, and audio.

Decision rule:

- **Re-encoding anyway:** put `-ss` before `-i`. With the default accurate seek, frames between the keyframe and the target are decoded and discarded, so the cut is frame-accurate and still fast.
- **Stream copy (`-c copy`):** packets cannot be decoded and discarded, so output starts at the packet boundary the demuxer lands on — typically the keyframe at or before the target. Accept keyframe-aligned cuts and verify the actual start time with `ffprobe`, or re-encode for frame accuracy.

```sh
ffmpeg -ss 00:01:00 -i input.mp4 -t 00:00:20 -c copy quick-cut.mp4
```

Stream-copy cuts may begin on keyframe boundaries and can preserve awkward timestamps. Re-encode when frame-accurate filtering or predictable normalization is more important than speed.

## Concatenation

There are distinct mechanisms:

- The concat demuxer reads a script describing files and is appropriate when streams are compatible and the files meet its safety and timestamp assumptions.
- The concat filter operates on decoded audio/video and can join segments after normalizing dimensions, formats, and timestamps.
- The concat protocol is physical byte/resource concatenation and is not a general-purpose media join.

Decision rule:

- **Streams match (same codecs, parameters, and time bases) and the target container accepts the concat demuxer:** use the demuxer with `-c copy`. It is fast and lossless. Verify the combined duration and stream count afterwards.
- **Inputs differ in codecs, dimensions, frame rates, pixel formats, sample rates, or start times:** decode and normalize, then use the concat filter. Normalize video with `scale`/`fps` (and pixel format), audio with `aresample`/`aformat` to a common rate, and reset each segment's timestamps with `setpts=PTS-STARTPTS` and `asetpts=PTS-STARTPTS` before joining. This path re-encodes.
- **Raw byte-concatenatable formats only (for example MPEG-TS segments):** the concat protocol. Do not use it for container files.

Never choose a concat method solely because files share an extension. Inspect codecs, dimensions, frame rates, sample rates, channel layouts, time bases, and metadata.

## Metadata and subtitles

Metadata can be copied, mapped, or rewritten. FFmpeg's format documentation describes the `ffmetadata` muxer/demuxer for round-tripping metadata.

For subtitles, choose between preserving the stream and rendering pixels — they are different deliverables:

- **Copy (`-c:s copy` or an explicit subtitle codec)** when the text should remain selectable, restylable, or removable and the target container supports the subtitle codec. Matroska accepts text (SRT/ASS) and bitmap (PGS/DVB) subtitles; MP4 text tracks use `mov_text`, so remuxing SRT into MP4 typically requires `-c:s mov_text`, and bitmap subtitles generally do not fit MP4. Verify with `ffprobe` that the subtitle stream survived.
- **Burn in (`subtitles=` or `ass=` filter)** when the video must render identically in players that ignore subtitle tracks. This requires a build with libass (confirm with `ffmpeg -filters` or `scripts/ffmpeg-preflight --filter subtitles`), decodes and re-encodes the video, and fixes styling at encode time.

Never assume a copied subtitle stream will survive into the target container; probe the output and confirm the intended track count.

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

https://ffmpeg.org/ffmpeg-filters.html
 -> Subtitle rendering filters, setpts/asetpts, and concat filter normalization requirements.

https://shotstack.io/learn/how-to-use-ffmpeg/
 -> Secondary practical examples; verify all commands against current official manuals.

https://en.wikibooks.org/wiki/FFMPEG_An_Intermediate_Guide
 -> Secondary intermediate topic map; examples are version/build-sensitive.
