# Reproducible Editorial Workflow Example

Use this example to prove that the FFmpeg skill artifacts compose from intake through acceptance. It generates synthetic media only; it does not authorize work on user media and it does not establish editorial quality or destination compatibility.

## Run the example

From the `ffmpeg` skill directory, choose a new or empty task-local directory:

```sh
scripts/editorial-workflow-example /tmp/ffmpeg-editorial-example --json
```

The helper refuses a non-empty workspace and uses `-n` for every generated media artifact. It creates a short `testsrc2` video with an 880 Hz synthetic audio track, then performs this complete path:

```text
generate -> probe/intake -> bounded evidence -> EDL -> decoded trim
         -> output probe/decode -> frame/audio checks -> acceptance
```

The example requires locally installed `ffmpeg` and `ffprobe`. It accepts `--ffmpeg` and `--ffprobe` paths and bounds source duration and per-command runtime.

## Artifact closure

Every durable record uses `workflow_id: synthetic-editorial-example`; the source is `asset-synthetic-001`, and the bounded trim is `event-001`.

| Artifact | Evidence role |
|---|---|
| `synthetic-source.mkv` | Deterministically generated source with video and audio streams |
| `source-probe.json` | Source structure reported by the current FFprobe build |
| `intake-manifest.json` | Source identity, digest, tool versions, preservation policy, and output contract |
| `evidence-packet.json` | Bounded observation and explicit semantic/listening/downstream gaps |
| `edit-decision-list.json` | Reviewed synthetic trim with source/event identity and expected duration |
| `edited-output.mkv` | New rendered output; the source is not overwritten |
| `output-probe.json` | Output stream and duration evidence |
| `review-frame-*.png` | Opening/closing samples that cover only their timestamps |
| `acceptance-report.json` | Criterion-level component, integration, signal, sampling, and downstream verdicts |
| `command-log.json` | Exact executed commands for the recorded local build |

## What the result proves

A successful run proves that the recorded local FFmpeg/FFprobe build completed this synthetic workflow, the output decoded, required streams were present, duration met tolerance, bounded frames were extracted, and the audio processing path completed.

It does **not** prove semantic visual correctness, listening quality, accessibility, rights, or compatibility with any player, editor, host, archive, or upload API. The acceptance report must retain those items as `UNVERIFIED` until the appropriate reviewer or destination supplies evidence.

Do not commit generated media or task-local evidence. Preserve the report package with the task when it is being used as release evidence.
