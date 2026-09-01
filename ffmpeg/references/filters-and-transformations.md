# Filters and Media Transformations

## Simple versus complex graphs

A simple video or audio filter can be attached with `-vf` or `-af`:

```sh
ffmpeg -i input.mp4 -vf 'scale=1280:-2,fps=30' -af 'loudnorm' output.mp4
```

The filter string is a graph, even when it is a linear chain. Filters consume frames or audio samples and produce new ones, so filtering implies decoding and re-encoding for that stream.

Use `-filter_complex` when multiple inputs, branches, overlays, joins, or separately labeled outputs are involved:

```sh
ffmpeg -i video.mp4 -i logo.png \
  -filter_complex '[0:v][1:v]overlay=20:20[vout]' \
  -map '[vout]' -map 0:a:0 -c:v libx264 -c:a copy output.mp4
```

Labels are graph edges. Every labeled output that should reach an output file must be mapped. Unmapped filtered output is not a harmless detail: it changes what reaches the muxer or causes an error.

## Common transformation classes

- `scale` changes dimensions and may require an explicit pixel format or aspect-ratio policy.
- `fps` changes frame cadence and can affect duration, motion, and synchronization.
- `crop`, `pad`, `transpose`, and `setsar` change geometry or display interpretation.
- `trim` and `atrim` select time ranges but generally need timestamp normalization such as `setpts` or `asetpts` before concatenation.
- `volume`, `loudnorm`, `aresample`, and `aformat` alter audio level, loudness, sample rate, or format.
- `subtitles` and `drawtext` render text into pixels when available, unlike a copied subtitle stream.
- `overlay`, `hstack`, `vstack`, `concat`, `amix`, and `amerge` combine streams and therefore require compatible timing and formats.

These names are not guarantees. Confirm local availability:

```sh
ffmpeg -filters
ffmpeg -h filter=scale
ffmpeg -h filter=drawtext
```

## Audio and video are separate graphs

A video filter cannot repair audio synchronization by itself. Treat audio and video as separate streams with separate clocks and sample/frame formats. When combining or transcoding them, inspect sample rate, channel layout, start timestamps, duration, and encoder delay.

The resampler can convert sample rates, channel layouts, and sample formats. The scaler converts image dimensions and pixel formats. Both have quality and range choices that should be explicit when the result matters.

## Local failure as evidence

The local FFmpeg 8.1.2 build did not include `drawtext`. A command that combined `scale`, `fps`, and `drawtext` stopped with `No such filter: 'drawtext'` before creating output. This demonstrates why a tutorial's command must be treated as a recipe conditioned on a build, not as a universal API.

## Debugging filtergraphs

Build graphs incrementally. First transcode without filters, then add one filter, then add labels and branches. Use short synthetic inputs, verbose logging, and explicit `-map`. If a graph fails, distinguish parser errors, missing filters, format negotiation errors, timestamp errors, and encoder/muxer errors.

SOURCES (LAYER 3 NAVIGATION)
https://ffmpeg.org/ffmpeg-filters.html
 -> Filtergraph syntax, pads, labels, filter families, framesync, and filter options.

https://ffmpeg.org/ffmpeg-scaler.html
 -> Image scaling and pixel-format conversion.

https://ffmpeg.org/ffmpeg-resampler.html
 -> Audio resampling, rematrixing, formats, dithering, and compensation.

https://trac.ffmpeg.org/wiki/FilteringGuide
 -> Official wiki tutorial lead for filtergraphs; access was blocked by Anubis during this research and commands require verification.

references/local-verification.md
 -> Local filter inventory counts and the verified missing-filter failure.
