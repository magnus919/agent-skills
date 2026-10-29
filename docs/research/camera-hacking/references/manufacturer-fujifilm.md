# Fujifilm: discovery reference

Accessed 2026-10-29. Status: **Research code and remote-control library documented**. Evidence is documentation and attributed project reports; no camera behavior was reproduced here.

## Full-family coverage

Start with the [complete X-series model map](family-fujifilm-x-series.md). It includes every captured vendor-roster identity, model/lineage references, primary project routes and explicit gaps. This supersedes the initial narrow model sample as the discovery entry point; it does not broaden any existing patch's compatibility.

## Retained primary sources

- [Fujihack](https://fujihack.org/): Documents patched-firmware code execution on X-A2 1.30 and XF1 1.01, but says there are no hacks ready for public use.
- [Fujihack source](https://github.com/fujihack/fujihack): Provides USB code/memory tools, RTOS interfaces and experimental extensions. Its recovery path via SoC boot ROM is not yet reverse-engineered.
- [libfuji](https://github.com/petabyt/libfuji): Reverse-engineered USB, Wi-Fi and BLE interoperability, including tethering and RAW-conversion modes. This is a separate path from firmware modification.

## Compatibility and next evidence

Do not generalize these two old body targets to current X or GFX cameras. Runtime APIs and protocol support need their own per-model matrices.

## Model records

- [fujifilm-x-a2-xf1](model-fujifilm-x-a2-xf1.md)

Before proposing a device operation, resolve exact stock identity, affected persistent state, release provenance, feature test scope, and the recovery evidence for that operation. Discovery does not establish installation readiness.

## Manufacturer completeness audit — 2026-10-29

Full X-series family audit retained; GFX and FinePix appear only as supplementary raw/transfer subsets.

**Finding: coverage remains incomplete.** X-series coverage is source-bound to 53 identities in family-coverage.json, not all Fuji products. FinePix and GFX worldwide/history completeness remains outside that denominator.

Fujihack/FujiMod, libfuji/fujicli and Furble evidence remain model/firmware-specific.

Source checks: [gphoto-cameras](https://gphoto.sourceforge.io/proj/libgphoto2/support.php) (retrieved), [libraw-cameras](https://www.libraw.org/supported-cameras) (retrieved). Retrieval status is recorded separately from relevance; an HTTP response is not source validation.

Model evidence, split by source type:

- [inventory-fujifilm-gphoto-1](inventory-fujifilm-gphoto-1.md)
- [inventory-fujifilm-libraw-1](inventory-fujifilm-libraw-1.md)

The [audit method and remaining gaps](../manufacturer-audit-findings.md) explain the denominator and completion boundary.
