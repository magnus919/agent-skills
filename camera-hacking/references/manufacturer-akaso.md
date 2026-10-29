# AKASO: discovery reference

Accessed 2026-10-29. Status: **Firmware unpack/repack tools and recovery caveat documented**. Evidence is documentation and attributed project reports; no camera behavior was reproduced here.

## Retained primary sources

- [BRAVE8 firmware tool](https://github.com/Fexiven/ambarella-firmware-tools): A Python unpacker/repacker for BRAVE8 containers, including CRC and section handling; explicitly excludes other formats.
- [iCatch V50 playground](https://github.com/Linouth/iCatch-V50-Playground): Research lead whose documented recovery instructions explicitly do not work on AKASO V50 Pro.

## Compatibility and next evidence

A parser/repacker is not a camera-qualified patch. Do not use one AKASO recovery recipe across different chipsets, revisions or products.

Before proposing a device operation, resolve exact stock identity, affected persistent state, release provenance, feature test scope, and the recovery evidence for that operation. Discovery does not establish installation readiness.

## Manufacturer completeness audit — 2026-10-29

BRAVE, V50, EK7000 and AKASO 360; Lite/Pro/LE/revision suffixes remain distinct.

**Finding: coverage remains incomplete.** Action marketing page covers five labels; the shop collection could not be retrieved. Older EK/V50/BRAVE variants and SKU-specific boards remain unenumerated.

BRAVE8 Ambarella unpack/repack; V50 Pro recovery is explicitly excluded by the retained iCatch project.

Source checks: [akaso-cameras](https://www.akasotech.com/action-camera) (retrieved), [akaso-shop](https://shopakaso.com/collections/action-camera) (unavailable). Retrieval status is recorded separately from relevance; an HTTP response is not source validation.

Model evidence, split by source type:

- [inventory-akaso-official-1](inventory-akaso-official-1.md)

The [audit method and remaining gaps](evidence-scope.md) explain the denominator and completion boundary.
