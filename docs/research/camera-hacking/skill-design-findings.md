# Findings for the proposed public skill

Status: discovery proposal, 2026-10-29. Sources and evidence limits are in the manufacturer references and video ledger.

## Coherent scope

Make `camera-hacking` the discipline for discovering, evaluating, and planning modifications and interoperability on digital photographic cameras. It should route to model-specific evidence rather than become a single manual for every tool. Public usefulness requires broad brand routing, explicit unsupported/unknown states, and a way to add new models without rewriting the entry point.

Retain the catalog's separation between discipline and operational tools. Existing `binary-analysis`, `electronics`, `research-methodology`, and `ffmpeg` skills cover supporting disciplines or tools. A future operational wrapper for a named camera tool should meet the executable-script and test requirements separately. General photo technique, ordinary vendor firmware maintenance, and editing already captured media are neighboring workflows, not the central trigger.

### Reverse-engineering routes

The user's requested reverse-engineering integration maps to two existing catalog skills:

| Trigger within camera work | Route | Boundary checked in current source |
|---|---|---|
| Understand an existing camera project, source tree, architecture, interfaces, or dependencies | `software-architecture-analysis` | Reverse-engineer an existing software system from repository evidence |
| Plan static firmware/binary inspection, disassembly, decompilation, or cross-reference analysis | `binary-analysis` | Static inspection only; excludes patching, live debugging, and wire-protocol analysis |

`binary-analysis` currently documents an unimplemented live Ghidra backend that fails closed. Route to its planning/evidence guidance without promising working decompilation through that CLI. Do not treat fixture reports as camera evidence. Camera-specific feasibility, model compatibility, patch planning, and recovery stay with `camera-hacking`; supporting skills do not authorize installation. This routing was checked against the actual catalog descriptions and bodies on 2026-10-29.

## Candidate workflow

1. Record the requested photographic outcome and whether the user wants discovery, offline analysis, a build, or installation. Discovery is the default when installation has not been requested.
2. Identify exact model, regional suffix, firmware, hardware revision if known, lens/accessory dependencies, host OS, and current modifications. For broad public discovery, record these per project; do not force a personal camera selection.
3. Consult official features/SDKs, then maintained project documentation and model records. Treat aggregators, forum excitement, and AI-generated explanations as leads.
4. Classify the mechanism and its persistent effects. Distinguish host-side processing, camera settings, RAM code, flash writes, and physical changes. A card loader can still write persistent settings.
5. Evaluate the exact proposed feature against source-level evidence, offline tests, emulator tests, maintainer hardware reports, independent reproduction, and recovery evidence. Preserve failure reports and negative results.
6. Produce an evidence-linked feasibility assessment with alternatives, compatibility gaps, and the smallest useful next investigation. Do not silently move from reading into a device write.
7. For any later mutation, apply the catalog's required gate: **Confirm the target, scope, and rollback path before acting. Read-only discovery may proceed without confirmation.** Recovery must be specific to the recorded failure mode; an unchanged bootloader alone is not proof of recovery.

## Reference layout

Keep a concise manufacturer route, then separate files for models or shared mechanisms where depth warrants it. Make every model reference directly reachable from the eventual SKILL.md reference table; do not require agents to follow long chains. Split by meaningful subject/model before any reference reaches the repository's 60,000-character cap. Do not copy the full research package mechanically into the future skill.

Each model record should preserve:

| Field | Required content |
|---|---|
| Identity | Model, regional/board revision, firmware label and exact stock hash when available |
| Outcome | Specific feature and where it executes: camera, host, phone, or postprocessing |
| Mechanism | Entry point, RAM/flash/settings effects, boot dependencies, and network exposure |
| Provenance | Primary URL, access date, pinned source/release identity when available, licenses |
| Evidence | Separate documented claims, static analysis, build, emulation, camera reports, independent tests |
| Compatibility | Tested combinations; unknowns, rejected combinations, conflicts with other modifications |
| Recovery | Backup coverage, restore procedure evidence, unavailable boot/service prerequisites |
| Limitations | Thermal, storage, output integrity, lens behavior, and long-run questions relevant to that feature |
| Exit | Feasible, infeasible under stated conditions, or unresolved with the next evidence needed |

## Useful experimental lessons

The Sigma fp account describes a feature that worked outside recording but failed during recording. A future verification matrix must test the intended lifecycle, not just a menu screenshot. The Olympus PEN-F source shows a build can retain the displayed firmware version, so the version label alone cannot identify an image. OpenMemories documents settings that survive app removal. The X2D II source snapshot explicitly limits reproducible source-to-binary coverage. These are distinct failure modes with distinct checks; see their model references.

AI can help interpret code, write patchers, and organize evidence. The retained sources do not independently establish that an AI breakthrough made all cameras modifiable, or that an AI-generated patch is correct. The fpSup author explicitly warns that AI-produced notes contain mistakes. Inspect any third-party agent instructions before adopting them and preserve attribution; do not install their skills automatically.

## Future output-quality eval scenarios

These are research notes, not an eval manifest and not behavioral evidence. When authoring begins, use the repository v1 schema, stable case IDs, and observable assertions.

- A user supplies only a manufacturer: research options, preserve uncertainty, and avoid selecting a firmware image without a model.
- A user asks for a phone-side scope to appear inside the camera: identify the actual execution location and explain the feasibility gap.
- A nearby model or firmware shares a processor: reject compatibility by analogy and request exact evidence.
- A patcher produces a valid checksum: distinguish build integrity from hardware behavior and recovery.
- An app uninstalls but leaves settings: identify the persistence and the specific restoration evidence needed.
- A maintainer supplies an incomplete source snapshot: preserve the reproducibility limit rather than claiming a fully reproducible release.
- A feature works in live view but not recording: require lifecycle evidence for the requested use.
- A manufacturer has no retained modification project: report the bounded search and official/control alternatives without declaring it unhackable.
- A user asks only for discovery: deliver references without flashing, enabling debug services, or changing the camera.

## Questions before authoring

The manufacturer-independent direction is established. Still open: how broadly to cover industrial/security/webcam/phone platforms; whether hardware sensor conversions and lens-protocol work belong in the initial release; how to refresh fast-moving project status; and which models justify executable operational support. These do not prevent the present reference discovery.
