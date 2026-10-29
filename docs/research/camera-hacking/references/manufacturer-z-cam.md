# Z CAM: discovery reference

Accessed 2026-10-29. Status: **Official controls and independent firmware research documented**. Evidence is documentation and attributed project reports; no camera behavior was reproduced here.

## Retained primary sources

- [Z CAM E2 protocol documentation](https://github.com/imaginevision/Z-Camera-Doc/blob/master/E2/intro.md): Describes network control and E2 interface behavior.
- [E2 reverse engineering](https://github.com/storyboardcreativity/Z-Camera-E2-Reverse-Engineering): Independent firmware research lead; release-file provenance and compatibility require deeper inspection before use.

## Compatibility and next evidence

Treat E1, E2 and E2 variants separately. Distinguish media-format decoding from camera firmware functionality and do not acquire random historical firmware mirrors as a default.

Before proposing a device operation, resolve exact stock identity, affected persistent state, release provenance, feature test scope, and the recovery evidence for that operation. Discovery does not establish installation readiness.

## Manufacturer completeness audit — 2026-10-29

E1, E2/C/M4/S6/F6/F8 and Pro/Mark II/global-shutter variants; S/VR and PTZ families separately identified.

**Finding: coverage remains incomplete.** Current professional page/nav retains eight model labels, including four Mark II sensor bodies sharing a family route. Old E1/E2/VR and PTZ catalogs are not exhaustively reconciled.

Official E2 API and independent E2 firmware research; E1/E2 generations and firmware/SoC differences remain material.

Source checks: [zcam-cameras](https://www.z-cam.com/products/professional-cameras/) (retrieved). Retrieval status is recorded separately from relevance; an HTTP response is not source validation.

Model evidence, split by source type:

- [inventory-z-cam-official-1](inventory-z-cam-official-1.md)

The [audit method and remaining gaps](../manufacturer-audit-findings.md) explain the denominator and completion boundary.
