# Mechanisms and compatibility decisions

Classify each proposed capability before selecting tools or claiming risk/reversibility.

| Mechanism | What it can establish | State and compatibility questions |
|---|---|---|
| Official SDK/API | Documented remote control on named models/transports | SDK/API generation, firmware, host OS, settings written, authentication and licenses |
| Reverse-engineered protocol | An implemented command/transfer/control path | Exact model and app/firmware version, transport, negative results, whether querying writes state |
| Host/phone processing | A feature performed outside the camera | Input transport, latency/output path; do not relabel it in-camera functionality |
| Card-loaded/RAM program | Execution through a specific entry point | Boot flags, flash/settings writes, startup persistence, removal and crash behavior |
| Hidden setting/calibration | Existing camera behavior controlled by persistent data | Original values, region/board restrictions, reset semantics and restoration evidence |
| Patched firmware/container | A modified image or container for an exact target | Hash/version/board binding, signatures, offsets, complete package contents and tested recovery |
| Physical conversion | Changes to sensor/filter/board/interface hardware | Exact assembly, calibration, measurement, physical restoration and electrical limits |

Prefer the least invasive mechanism that actually meets the outcome. An official
API is not a substitute if the user needs a feature to execute offline inside the
camera; explain that gap rather than silently changing the requirement.

## Evidence levels

Record these separately, per feature and target:

- **Documented claim:** what the vendor or project says; identify the source.
- **Source/static observation:** symbols, code paths, tables, flags, package structure.
- **Build/integrity result:** exact inputs, toolchain, output digest and structural checks.
- **Emulator result:** configuration, emulated path and known hardware omissions.
- **Maintainer camera report:** exact device/firmware/mode and the reporter's evidence.
- **Independent reproduction:** observed target behavior with output artifacts and conditions.
- **Recovery result:** the failure mode restored, backup coverage and actual restoration evidence.

None automatically implies the next. Preserve known failures and not-tested modes.
A source tree with modern camera names is not a release matrix. Absence from a
project list is unresolved unless that project explicitly rejects the combination.
A valid checksum says nothing about thermal behavior, recording, calibration or
whether the boot ROM accepts a modified image.

## Lessons to carry into decisions

- Fujifilm X-A2/XF1 research does not establish that X100VI or other X/GFX bodies
  accept the same patch. Broader Fuji catalogs and emulation/control definitions
  have different evidence levels.
- Ricoh GR DIGITAL, APS-C GR, III/IIIx, HDF, IV and Monochrome remain distinct.
  An edition can share hardware yet have unresolved firmware identity. A patch for
  a specific stock hash does not apply automatically after a vendor update.
- Magic Lantern, CHDK and a camera's official firmware index answer different
  questions. Verify the actual port/build/feature status, not a platform folder.
- Sony OpenMemories settings may survive app removal. Model-specific restoration
  is required; deleting the app is not evidence that all effects were undone.
- Sigma fp live-view success does not prove operation while recording. Test the
  requested capture state and preserve the failing result.
- Hasselblad first-/second-generation work has different reconstruction paths;
  computer-side multishot reconstruction is not an in-camera result. An incomplete
  source snapshot cannot establish a fully reproducible binary release.
- Olympus modified firmware can retain a stock-looking version label. Record image
  hashes and provenance instead of treating the screen's version as image identity.

The linked manufacturer/model references supply the dated sources behind these
lessons. Refresh them for the actual task rather than treating this list as a runbook.
