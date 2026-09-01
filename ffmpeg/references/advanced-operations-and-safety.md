# Advanced Operations and Safety

## Hardware acceleration is a pipeline decision

Hardware acceleration may affect decoding, filtering, and encoding separately. A hardware encoder alone does not guarantee faster end-to-end processing. Transfers between system memory and device memory can erase gains, and hardware encoders can have different quality, feature, and rate-control behavior from software encoders.

First inspect the local build:

```sh
ffmpeg -hwaccels
ffmpeg -encoders
ffmpeg -filters | grep -E 'cuda|vaapi|qsv|videotoolbox|vulkan'
```

The local macOS build lists `videotoolbox`. NVIDIA CUDA examples from the vendor guide do not apply to this host. Verify the exact device, pixel formats, filter path, and encoder before benchmarking.

## Timestamp and synchronization diagnosis

When audio drifts, video freezes, concat jumps, or duration is wrong, collect:

```sh
ffprobe -v error -show_streams -show_format -of json input
ffmpeg -loglevel verbose -i input -f null -
```

Compare stream start times, durations, time bases, frame rates, sample rates, packet ordering, and whether a muxer is buffering sparse streams. Avoid cargo-culting timestamp flags. Options such as `-start_at_zero`, `-copyts`, `-vsync`/the modern synchronization controls, `setpts`, `asetpts`, `aresample`, and `avoid_negative_ts` solve different problems and can interact.

## Reproducible experiments

Pin the binary version, record `ffmpeg -version` and `-buildconf`, preserve the exact input or synthetic generator, and probe both sides. Run more than once when measuring speed. Separate wall-clock throughput from output quality and compatibility. If a tutorial omits hardware, build, driver, codec settings, or measurement method, treat its performance claim as incomplete.

## Security and operational boundaries

Do not feed untrusted media to an experimental decoder or enable permissive protocol behavior without understanding the exposure. Avoid secrets in command-line arguments when process listings or logs can expose them. Restrict network protocols and destinations. Refuse overwrites by default during development, write to a new path, and keep the original until the output is independently verified.

A syntax check, successful process exit, valid container, or local playback test proves only that layer. Acceptance should match the real boundary: target player, editor, streaming receiver, archival standard, or API consumer.

## Advanced learning resources

Use the official filter, codec, format, protocol, utility, scaler, and resampler manuals as the reference corpus. Use `slhck/ffmpeg-encoding-course` for a structured intermediate bridge, `amiaopensource/ffmprovisr` for preservation-oriented practice, and the NVIDIA guide for a vendor-specific hardware path. The official Trac wiki is useful but was inaccessible during this research pass, so its examples remain leads rather than verified evidence.

SOURCES (LAYER 3 NAVIGATION)
https://ffmpeg.org/ffmpeg-codecs.html
 -> Codec options, rate control, time bases, error detection, and encoder-specific behavior.

https://ffmpeg.org/ffmpeg-protocols.html
 -> Protocol options, network I/O, timeouts, and whitelists.

https://ffmpeg.org/ffmpeg-formats.html
 -> Probing, interleaving, timestamp shifting, and muxer/demuxer behavior.

https://docs.nvidia.com/video-technologies/video-codec-sdk/13.0/ffmpeg-with-nvidia-gpu/index.html
 -> NVIDIA-specific CUDA/NVENC pipeline examples and performance cautions.

https://github.com/slhck/ffmpeg-encoding-course
 -> Maintained secondary course for encoding concepts and practical progression.

https://github.com/amiaopensource/ffmprovisr
 -> Secondary preservation/media workflow recipe collection.

https://ffmpeg.org/download.html
 -> Official release and source-build guidance.
