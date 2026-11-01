# FFmpeg audit — #764

**Recommendation: no skill implementation for this inspected scope.** Eight
existing representative fixture tasks passed on the recorded local FFmpeg build.
No repeated wrapper/capability failure or reproduced severe boundary defect was
found. Actual editorial quality, source-specific failures, and real destination
acceptance remain unassessed; this is not a general certification of media workflows.

## Revision, inventory, and prior art

Source: `83d2784394ede4e4bab85aabc0545331fcb6ee31` (2026-11-01).
`execution.json` inventories hashes for every skill file, the exact test selection,
platform, interpreter, tool versions, and complete pytest stdout/stderr/exit.
`protocol.md` states the hypothesis, decision rule and bounds before execution.
Generated non-personal media and task-local evidence remain outside Git in
`/tmp/ffmpeg-audit-2026-11-01-tests`. No user footage, transcripts or private paths
are published. The committed receipt contains only sanitized test metadata.

Reviewed the entrypoint and README, integration and synthetic-fixture references,
selected tests and helper execution boundaries. Inventory covers core/evidence/
editorial/audio/verification/failure references, copyable templates, executable
helpers, existing tests and eval manifest. This is not a line-by-line re-audit of
every helper or a fresh behavioral generation over the entire eval manifest.

The following issue scopes and CLOSED state were checked live and treated as
completed prior art. No regression in them was assumed from old issue wording:

| Prior issue | Established scope / current artifact used in review |
|---|---|
| [#426](https://github.com/magnus919/agent-skills/issues/426) | Core FFmpeg pipeline, conditional recipes and source basis |
| [#428](https://github.com/magnus919/agent-skills/issues/428), [#430](https://github.com/magnus919/agent-skills/issues/430) | Named capability checks, parser/failure semantics and bounded subprocesses |
| [#438](https://github.com/magnus919/agent-skills/issues/438) | Intake/evidence/EDL/render/acceptance workflow and editorial boundaries |
| [#452](https://github.com/magnus919/agent-skills/issues/452) | Executable editorial integration with durable artifact identity |
| [#453](https://github.com/magnus919/agent-skills/issues/453) | Multi-source EDL planning, stream normalization, explicit supported/unsupported assembly |
| [#454](https://github.com/magnus919/agent-skills/issues/454) | Measured silence/loudness/clipping and transcript candidates with listening gate |
| [#455](https://github.com/magnus919/agent-skills/issues/455) | Attributed, bounded visual-review handoff |
| [#456](https://github.com/magnus919/agent-skills/issues/456) | Independent technical, content and downstream acceptance criteria |
| [#457](https://github.com/magnus919/agent-skills/issues/457) | Sanitized real-media fixture battery |
| [#458](https://github.com/magnus919/agent-skills/issues/458) | Named target/version compatibility and unavailable target lane |
| [#459](https://github.com/magnus919/agent-skills/issues/459) | Media-evidence research method, not another FFmpeg execution owner |

Recent path history also includes PRs #479–#483 implementing measured audio,
acceptance, visual handoff, target verification and research routing. These artifacts
already exist; their capabilities are not proposed again.

## Representative task execution

All cases are existing reproducible fixtures, not actual-user reports. Test source
and assertions were inspected before execution. The eight selected tests completed
with **8 passed, 0 failed, 0 skipped**, exit 0, in 3.74 seconds. Installed tool
identities: FFmpeg 9.0.1 and FFprobe 9.0.1 on the recorded Darwin host. Results are
specific to this build; historical 8.1.2 observations are not treated as current.

| Task / existing test | Evidence kind and observed result | What remains unproved |
|---|---|---|
| Multi-source decoded concat plan and render (`test_render_edl_concat_filter_plan_executes_against_synthetic_fixtures`) | Real synthetic media; plan executed, output exists, FFprobe finds audio and video | The selected test checks stream presence, not every frame boundary, perceptual join, arbitrary transition, or consumer |
| Audio analysis and edit candidates (`test_audio_inspect_measures_synthetic_candidates_and_builds_plan`) | Real synthetic audio; silence/loudness/peak values present; candidates retain source range and needs-listening-review; report overwrite rejected; mechanical fade renders and technical contract passes | Speech meaning, audibility and editorial cut quality require listening; generated voice-like input is not actual speech |
| Missing measurement capability (`test_audio_inspect_reports_missing_measurement_filter`) | Fake-tool inventory fixture; unavailable filter is preserved rather than claimed measured | Tests wrapper failure semantics, not availability of every real build's filters |
| Incomplete acceptance evidence (`test_media_verify_marks_missing_fields_and_evidence_unverified`) | Structured probe/evidence fixture; absent pixel format, decode, loudness and downstream evidence produce UNVERIFIED and exit 1 | Does not execute a real decoder or target |
| Blocked authorized review (`test_media_verify_preserves_blocked_review_status`) | Structured review fixture; BLOCKED reviewer reason survives, overall exit 1 | Does not recruit or qualify a reviewer |
| End-to-end editorial example (`test_editorial_workflow_example_runs_with_real_tools`) | Real synthetic source/render/decode/samples; workflow/source/event IDs agree across intake, EDL and acceptance; PASS_WITH_UNVERIFIED_BOUNDARIES | Semantic visual review, listening and downstream consumer compatibility explicitly remain unverified |
| Source/workspace preservation (`test_editorial_workflow_example_refuses_nonempty_workspace`) | Sentinel fixture; exit 2 and original sentinel content unchanged | Not exhaustive filesystem, hostile path, or arbitrary-input preservation proof |
| Unavailable target lane (`test_target_compatibility_keeps_unavailable_lane_separate`) | Structured named-target fixture; technical FAIL and target BLOCKED remain separate, overall FAIL | Not a real editor/player import or cross-version compatibility result |

No unexpected failure occurred, so the protocol did not authorize implementation.
No task was called passed because its dependency was skipped. Passing tests establish
only the assertions above, not every acceptance criterion of every media workflow.

## Coverage and ownership map

- **FFmpeg concepts:** the entrypoint covers typed streams, explicit mapping,
  input/output option scope, copy versus decoded cuts and build capability checks.
- **Wrapper behavior:** deterministic refusals, missing evidence states, artifact
  identity and the selected real-media paths were exercised; exhaustive arbitrary
  input, permissions and malicious-path analysis were outside this audit.
- **Version/platform variance:** local execution moved from the historical 8.1.2
  evidence to a recorded 9.0.1 build without a reproduced failure in these cases.
  This is not a compatibility matrix across versions or operating systems.
- **Unavailable codecs/filters:** preflight and audio tests retain absence; runtime
  inventories determine local capability. A published recipe cannot promise it.
- **Manifest/EDL/render/acceptance closure:** integration checks workflow/source/event
  identity and output evidence; technical, editorial and downstream states remain
  distinct rather than collapsed into command success.
- **Visual and audio semantics:** bounded frame packets and attributed observations
  remain separate from automatic interpretation; silence/clipping are candidates,
  not reasons to delete meaningful material. No human/vision/listening result was
  fabricated in this audit.
- **Destination acceptance:** target-version evidence belongs to the actual named
  consumer; the blocked-lane test proves reporting semantics only.
- **Operational media versus generation:** synthetic sources are test fixtures for
  media engineering. No image/video-generation demand, rights decision, automatic
  publishing, or HTML-authored composition is added to this skill.
- **Discovery versus capability:** the current description explicitly names local
  inspection, EDLs, audio cleanup, rendering and acceptance. No fresh client trigger
  run was performed, so no activation defect or rate improvement is claimed.

## Primary comparison

Checked 2026-11-01. Official website fetches timed out, so the primary FFmpeg
repository documentation was used as fallback:

- [FFmpeg manual source](https://raw.githubusercontent.com/FFmpeg/FFmpeg/master/doc/ffmpeg.texi): command option scope, stream selection and packet/frame pipeline distinctions support the existing mental model.
- [FFprobe manual source](https://raw.githubusercontent.com/FFmpeg/FFmpeg/master/doc/ffprobe.texi): structured stream/container information supports technical inspection, not semantic or destination acceptance.

These are upstream development documentation, not a pinned contract for every
installed build. Actual execution above is tied to the recorded local versions.
No universal codec availability or target compatibility is inferred from the docs.

## Failure clusters, rejected ideas, and next increment

No repeated failure cluster was demonstrated in this bounded task set. Remaining
evidence gaps cluster around **actual editorial judgment**, **real consumer
acceptance**, and **cross-build behavior**, which the current skill already treats
as separate unverified boundaries. A missing authorized reviewer or destination
session is not itself evidence that another wrapper or methodology is absent.

Rejected as duplicate: another intake/EDL/podcast/visual/target subsystem merely
restating #438/#452–#459. Rejected as speculative: universal crossfade handling,
more codecs, or a multi-platform compatibility claim without failing source/target
fixtures. Rejected as out of scope: generative production, rights clearance,
automatic publishing and HyperFrames composition. Raw install growth was not used
as a unique-user count, successful activation, continued use, or demand proof.

**Smallest useful next increment: no skill change now.** Obtain one approved real
media task with exact source/output hashes, source preservation requirements,
intended target/version, review authorization and bounded samples. Expected value:
test whether a real failure belongs to FFmpeg, wrapper behavior, environment,
destination or editorial judgment. Effort depends on that task; do not fabricate a
cost or participant estimate. Verify with current preflight/probe, a new-output
render, decode and source-preservation checks, authorized listening/visual review,
and the named consumer's receipt. Only a reproduced gap or severe boundary failure
should become a separately approved implementation issue.
