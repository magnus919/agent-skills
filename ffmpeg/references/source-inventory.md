# FFmpeg Source Inventory

**Research access date:** 2026-09-01

## Retained primary sources

| # | Source | Authority | Topics supported | Caveat |
|---|---|---|---|---|
| 1 | [FFmpeg documentation](https://ffmpeg.org/documentation.html) | Official project index | Current command-line and API documentation; versioned manuals | Online docs track the newest revision; use installed manuals for older builds. |
| 2 | [ffmpeg tool manual](https://ffmpeg.org/ffmpeg.html) | Official | Command anatomy, input/output order, stream selection, mapping, codecs, filtering, timestamps | Option scope is order-sensitive and many examples are contextual. |
| 3 | [ffprobe manual](https://ffmpeg.org/ffprobe.html) | Official | Container/stream inspection, machine-readable output, stream specifiers, intervals | Probe output describes the file; it does not prove universal playback compatibility. |
| 4 | [ffmpeg-all manual](https://ffmpeg.org/ffmpeg-all.html) | Official | Consolidated reference and examples across tools and libraries | Very large; use for lookup after learning the model. |
| 5 | [Filters manual](https://ffmpeg.org/ffmpeg-filters.html) | Official | Filtergraphs, pads, labels, audio/video filters, framesync, hardware filters | Availability and options depend on build and version. |
| 6 | [Formats manual](https://ffmpeg.org/ffmpeg-formats.html) | Official | Demuxers, muxers, probing, interleaving, timestamp handling, concat | Container behavior varies; codec and container compatibility are separate. |
| 7 | [Codecs manual](https://ffmpeg.org/ffmpeg-codecs.html) | Official | Encoder/decoder options, bitrate, time base, rate control, error detection | Private options are encoder-specific. |
| 8 | [Protocols manual](https://ffmpeg.org/ffmpeg-protocols.html) | Official | File, pipe, network, concat, UDP, HTTP and other I/O protocols | Network commands need explicit timeout, security, and endpoint assumptions. |
| 9 | [Utilities manual](https://ffmpeg.org/ffmpeg-utils.html) | Official | Duration syntax, quoting/escaping, expressions, rational numbers, channel layouts | Shell quoting is a second language layered over FFmpeg quoting. |
| 10 | [Scaler manual](https://ffmpeg.org/ffmpeg-scaler.html) | Official | Scaling, pixel-format conversion, algorithms, range and gamma | Quality depends on source/destination formats and range. |
| 11 | [Resampler manual](https://ffmpeg.org/ffmpeg-resampler.html) | Official | Sample-rate conversion, channel rematrixing, sample formats, dithering, sync compensation | Optional SoX support and defaults are build-dependent. |
| 12 | [NVIDIA FFmpeg GPU guide](https://docs.nvidia.com/video-technologies/video-codec-sdk/13.0/ffmpeg-with-nvidia-gpu/index.html) | Vendor primary source | CUDA decode, GPU surfaces, scale_cuda/scale_npp, NVENC | NVIDIA-specific; do not transfer commands to macOS or non-NVIDIA hosts. |
| 13 | [FFmpeg Git repository](https://git.ffmpeg.org/ffmpeg.git) | Official source | Source-level confirmation and release history | Source inspection does not replace testing the installed binary. |
| 14 | [FFmpeg download/release guidance](https://ffmpeg.org/download.html) | Official | Releases, source builds, release cadence and signed tags | Distribution packages may lag or differ in enabled components. |

## Secondary learning resources

- [FFmpeg Filtering Guide](https://trac.ffmpeg.org/wiki/FilteringGuide) - official project wiki guide. Automated retrieval was blocked by the site's Anubis proof-of-work page on this date, so treat it as a reading lead and verify commands against the filters manual.
- [FFmpeg Ultimate Guide](https://img.ly/blog/ultimate-guide-to-ffmpeg/) - readable secondary overview with practical transcoding examples; vendor context means commands should be checked against official manuals.
- [Shotstack FFmpeg guide](https://shotstack.io/learn/how-to-use-ffmpeg/) - broad examples and scripting orientation; secondary and service-oriented.
- [FFmpeg intermediate guide on Wikibooks](https://en.wikibooks.org/wiki/FFMPEG_An_Intermediate_Guide) - useful topic map; community-maintained and examples need current-build verification.
- [FFmpeg short guide and examples](https://github.com/term7/FFmpeg-A-short-Guide) - practical GitHub notes; inspect freshness before relying on a recipe.
- [slhck FFmpeg encoding course](https://github.com/slhck/ffmpeg-encoding-course) - maintained educational repository discovered during delegated research; strong intermediate bridge, but still secondary to the official manuals.
- [amiaopensource/ffmprovisr](https://github.com/amiaopensource/ffmprovisr) - preservation-oriented recipe collection; useful for real media workflows, with strong need for format-specific verification.

## Rejected or limited sources

- FFmpeg Trac pages for Concatenate, H.264, AAC, HWAccelIntro, StreamingGuide, Encode/YouTube, and CompilationGuide were not retained as evidence because retrieval encountered the site's JavaScript proof-of-work page. This is an access limitation, not evidence that the pages are wrong.
- DeepWiki pages were not used as primary evidence because they are generated/secondary explanations of source code.
- Search-result snippets and anonymous cheat sheets were used only for discovery, not evidence.

## Recommended learning order

1. `ffmpeg` synopsis and `ffprobe` inspection.
2. Containers, streams, codecs, demux/mux, decode/filter/encode, and stream mapping.
3. Remuxing versus transcoding, codec selection, quality controls, and stream specifiers.
4. Simple filters, then labeled `-filter_complex` graphs and explicit `-map`.
5. Time, seeking, trimming, concat demuxer versus concat filter, timestamps, and synchronization.
6. Metadata, subtitles, image sequences, pipes, and shell scripting.
7. Streaming protocols and latency controls, with explicit endpoint and timeout handling.
8. Hardware acceleration only after understanding software pipelines and verifying local capabilities.
9. Debugging with verbose logs, `ffprobe`, minimal reproductions, and build inventories.

SOURCES (LAYER 3 NAVIGATION)
https://ffmpeg.org/documentation.html
 -> Official documentation index and version links.

https://ffmpeg.org/ffmpeg.html
 -> Primary command-line semantics.

https://ffmpeg.org/ffmpeg-filters.html
 -> Primary filtergraph reference.

https://ffmpeg.org/ffprobe.html
 -> Primary inspection reference.
