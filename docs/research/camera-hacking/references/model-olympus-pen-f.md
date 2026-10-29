# Olympus PEN-F HSL extension

Accessed 2026-10-29. Primary source: [Olympus PEN-F HSL extension project documentation](https://github.com/fishcu/oly_fw_analysis/blob/main/patches/hsl/pen-f/README.md). Findings below are source-attributed; no hardware reproduction was performed in this investigation.

## Exact source target

The documented source rebuilds release **alpha-20261017** from official **PEN-F 3.1, build 3101**. The displayed version remains 3.1 after patching: a version label alone cannot distinguish stock from modified firmware.

## Scope and verification

The HSL feature changes colour-profile editing and associated persistence, RAW development and metadata. This source does not add recording-limit, grain or vignette changes. Its builder checks original ranges, assembled spans, non-overlap, checksums and final release identity; it generates a matching stock restore image and build provenance.

The source calls this a reproducible build of the recorded release. We did not execute it. Rebuilding the same bytes is distinct from qualifying an edited patch or demonstrating physical recovery. MN103 emulation does not emulate image-processing hardware.

## Next evidence

Inspect the release's physical test scope and recovery limits, exact stock hash, settings migration and any existing third-party modifications. Retain the reference checks when exploring source changes; weakening a hash check cannot qualify a new patch.
