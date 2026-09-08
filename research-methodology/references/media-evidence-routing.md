# Media Evidence Routing

Use the shared research lifecycle for media questions, but keep operational media mechanics with the owning tool skill. This reference defines the handoff; it is not an FFmpeg runbook.

## Ownership boundary

| Concern | Owner |
|---|---|
| Research question, inclusion/exclusion rules, source evaluation, current-claim dates, rejected-source log, source-to-claim audit, synthesis confidence, and durable preservation | `research-methodology` |
| FFmpeg/FFprobe commands, build inventories, media intake, bounded extraction, EDLs, rendering, signal measurement, and output/target verification | `ffmpeg` |
| Transcript acquisition and timing quality | The authorized source or transcription skill |
| Semantic frame/audio interpretation and editorial approval | An attributed human or capable reviewer |
| Upload, account, or platform API action | The named platform skill |

Start from `assets/research-brief.md` and `assets/research-log.md`. For consequential media claims, also copy `assets/media-claim-ledger.md`. Route command selection and experiment execution to `ffmpeg`; return its versioned records to the research ledger before synthesis.

## Media brief additions

Record these before gathering evidence:

- editorial or technical objective and the decision it will inform;
- output contract and named downstream consumer, if any;
- rights, authorization, privacy, retention, and sharing boundary;
- decision granularity: whole asset, interval, event, frame, packet, or stream;
- review points and accountable human decisions;
- required coverage and what would make sampling insufficient.

## Evidence classes

Keep unlike evidence separate:

- **Documented semantics:** an official specification or tool manual, with URL, accessed date, relevant version, and exact supported claim.
- **Reproduced behavior:** exact tool/build, environment, fixture/digest, commands, raw results, and repeated observations.
- **Observed artifact:** probe fields, decoded samples, measurements, destination results, or attributed review for the named artifact and interval.
- **Environment-specific claim:** availability or behavior tied to one build, device, operating system, target, or account.
- **Heuristic:** detector threshold, sparse sampling, transcript navigation, inferred continuity, or editorial convention requiring review.
- **Unresolved:** conflicting, inaccessible, untested, undersampled, or authorization-blocked claim.

Official documentation explains documented behavior; it does not prove local availability or the outcome of a command. A reproduction establishes only its recorded fixture and conditions. A target result applies only to that target/version.

## Sampling and editorial guardrails

Every frame, clip, waveform, transcript span, or detector event needs an asset ID, stream/interval, selection method, transformations, and coverage statement. Audit whether the sample can support the claim's scope. Sparse frames cannot establish absence throughout a video; a detector event cannot establish editorial meaning; a transcript cannot establish exact audiovisual continuity; a local decode cannot establish downstream acceptance.

When coverage is insufficient, narrow the claim, collect more bounded evidence, request attributed review, or leave the question unresolved. Technical facts and human editorial approval remain separate ledger entries.

## Worked source-to-claim closure

This compact example demonstrates the method, not a portable compatibility guarantee.

| Field | Record |
|---|---|
| Claim | Explicit stream mapping preserved one MPEG-4 video stream followed by one PCM audio stream in a Matroska remux under the recorded experiment. |
| Classification | Reproduced behavior plus observed artifact. |
| Source | [FFmpeg documentation](https://ffmpeg.org/ffmpeg.html), accessed 2026-09-08; supports `-map` stream-selection semantics, not this run's outcome. |
| Experiment | Synthetic 64x64/10 fps video plus 48 kHz sine audio; FFmpeg and FFprobe 8.1.2; create source, remux with `-map 0:v:0 -map 0:a:0 -c copy`, then probe stream index/type/codec. |
| Observation | FFprobe reported stream 0 as MPEG-4 video and stream 1 as PCM signed 16-bit little-endian audio. |
| Limitation | One local build, synthetic fixture, Matroska container, and one stream order. This does not establish visual/audio quality, exact timing, other builds/containers, or downstream compatibility. |
| Durable artifacts | Claim ledger entry, access-dated source record, exact command log, build record, source/output probe JSON, fixture generator, and rejected/untested-source entries. |

Closure requires the claim to link to every named artifact and the durable log to record missing evidence. Preserve inaccessible, rejected, redundant, and untested sources with reasons so omission cannot masquerade as coverage.
