# Learning FFmpeg Without Memorizing Recipes

FFmpeg is best understood as a graph of media transformations. An input URL is demuxed into streams, streams may be selected and either copied or decoded, decoded frames can pass through audio/video filters, encoders turn processed frames back into packets, and a muxer writes those packets to an output URL. `ffprobe` is the inspection tool that tells you what the container and streams actually contain.

## The practical mental model

- A **container** such as MP4, Matroska, MPEG-TS, or WAV packages one or more streams and their metadata.
- A **codec** describes the encoded elementary stream, such as H.264, AV1, AAC, Opus, or PCM.
- A **stream** is one typed track, usually video, audio, subtitles, data, or attachments.
- **Remuxing** changes the container while copying encoded streams. It is fast and avoids generation loss, but only works when the target container accepts those streams.
- **Transcoding** decodes and re-encodes. It enables filtering and format changes, but costs time and can reduce quality.
- **Mapping** makes stream selection explicit. Use it whenever multiple inputs, multiple tracks, or complex filters make automatic selection ambiguous.
- A **filtergraph** is a directed graph of named inputs, filters, and outputs. A labeled output from `-filter_complex` must be mapped explicitly.

## A reliable operating loop

1. Inspect: `ffprobe -v error -show_format -show_streams -of json input.mkv`.
2. Decide: remux, stream-copy, transcode, filter, or combine inputs.
3. Verify capabilities: `ffmpeg -formats`, `-codecs`, `-encoders`, `-filters`, and `-hwaccels`.
4. Build a minimal command with explicit stream selectors and output options.
5. Run without overwriting first, capture stderr, and probe the output.
6. Test playback and the intended downstream consumer. A successful exit code and valid container are not universal compatibility proof.

## Learning path

Start with inspection and the command line, then understand stream selection and copy/transcode. Add simple filters before learning labeled filtergraphs. Next learn seeking, timestamps, concat, metadata, subtitles, pipes, and shell loops. Only then move to streaming, hardware acceleration, and complex debugging.

## What local testing changed

The local macOS Homebrew FFmpeg 8.1.2 build successfully generated and probed an H.264/AAC MP4. A subsequent scale/fps/text-filter experiment failed because this build did not contain `drawtext`. That failure is part of the lesson: online recipes are not portable promises. Check the installed build and verify the final artifact.

## Implications

FFmpeg becomes predictable when commands are treated as typed pipelines rather than incantations. Most difficult failures occur at boundaries: stream selection, option scope, timestamps, filter availability, codec/container constraints, shell escaping, or hardware/software memory transfer. Make those boundaries explicit and debugging becomes a sequence of observable checks.

SOURCES (LAYER 2 NAVIGATION)
02-analysis/core-model-and-command-anatomy.md
 -> Detailed model of containers, streams, codecs, option scope, mapping, and copy/transcode.

02-analysis/filters-and-transformations.md
 -> Filtergraph construction and audio/video transformation boundaries.

02-analysis/intermediate-workflows.md
 -> Inspection, joining, metadata, scripting, and streaming workflows.

02-analysis/advanced-operations-and-safety.md
 -> Hardware acceleration, timestamps, reproducibility, and diagnosis.
