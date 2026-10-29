# Insta360: discovery reference

Accessed 2026-10-29. Status: **Official SDKs and multiple independent research targets documented**. Evidence is documentation and attributed project reports; no camera behavior was reproduced here.

## Retained primary sources

- [Official SDK guide](https://onlinemanual.insta360.com/developer/en-us/resource/sdk): Separates camera control from media processing SDKs and links professional-camera APIs.
- [ONE R live-stream research](https://github.com/NiklasVoigt/Insta360-Livestream): Reports partial success on ONE R 1.3.8 and failure on X3 1.0.04. The negative result is a useful compatibility boundary.
- [Luna Ultra research](https://github.com/derrickyau9/insta360-luna-ultra-reverse-engineering): Reports a developer environment on firmware 1.0.47 with persistent services; wireless ADB is unauthenticated according to its own warning.
- [Link firmware research](https://github.com/schlarpc/insta360-link-firmware-re): Separate webcam firmware/protocol study. Its host controls and firmware-update behavior are not transferable to action/360 models.

## Compatibility and next evidence

Keep 360/action, Luna and Link webcam hardware in separate records. Discovery does not enable persistent debug services or modify capture indicators. Source claims here were not independently reproduced.

Before proposing a device operation, resolve exact stock identity, affected persistent state, release provenance, feature test scope, and the recovery evidence for that operation. Discovery does not establish installation readiness.

## Manufacturer completeness audit — 2026-10-29

X/ONE/ONE X/ONE R/RS, GO, Ace, Luna, Pro/Titan; Link/Connect webcam track kept distinct.

**Finding: coverage remains incomplete.** Product navigation and download data extracted; hot downloads are not the full catalog. Original ONE/RS lens-module bundles, EVO/Nano/Air and region-specific retired models need support archive closure. Phone-only Flow and microphones excluded.

ONE R positive/X3 negative live-stream report, Luna Ultra specific firmware and Link webcam research are separate targets; official SDK capabilities also need model checks.

Source checks: [insta360-cameras](https://www.insta360.com/product) (unavailable), [insta360-downloads](https://www.insta360.com/download) (retrieved). Retrieval status is recorded separately from relevance; an HTTP response is not source validation.

Model evidence, split by source type:

- [inventory-insta360-official-1](inventory-insta360-official-1.md)

The [audit method and remaining gaps](evidence-scope.md) explain the denominator and completion boundary.
