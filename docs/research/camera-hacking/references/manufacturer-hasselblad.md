# Hasselblad: discovery reference

Accessed 2026-10-29. Status: **Separate first- and second-generation extensions documented**. Evidence is documentation and attributed project reports; no camera behavior was reproduced here.

## Retained primary sources

- [X-System research](https://github.com/radium-wang/Hasselblad-X-System-CIM-Firmware-Research-Feature-Extensions): Separates X2D/X2D II work, static findings, device reports and unresolved behavior. Much second-generation analysis is offline only.
- [X2D/907 toolkit](https://github.com/Gothenburg-R-D-Team/x2d-907-one-click-extension-toolkit): Experimental first-generation body extensions. Restoration has version- and backup-specific constraints.
- [X2D II 400 MP source](https://github.com/Jimmy6Smiles/Hasselblad-X2DII-400MP-Source): A distinct second-generation reconstruction project with explicitly incomplete source-to-binary reproduction coverage.

## Compatibility and next evidence

Keep X2D sequence capture requiring computer reconstruction distinct from X2D II in-camera reconstruction. Third-party extensions may share runtimes and conflict.

## Model records

- [hasselblad-x2d-907](model-hasselblad-x2d-907.md)
- [hasselblad-x2d-ii](model-hasselblad-x2d-ii.md)

Before proposing a device operation, resolve exact stock identity, affected persistent state, release provenance, feature test scope, and the recovery evidence for that operation. Discovery does not establish installation readiness.

## Manufacturer completeness audit — 2026-10-29

X1D/X2D, 907X/CFV, H digital bodies/backs and older CF/CFV; Lunar/Stellar/HV require separate legacy identities.

**Finding: coverage remains incomplete.** X/V/H vendor pages and 39 LibRaw labels retained. H6X is a host body rather than a standalone digital capture device. Older H sensor/multishot/CF/back combinations, rebadges and all editions remain a roster gap.

Keep X2D/907 first-generation extensions separate from X2D II; no support inferred for X1D/H/older CFV.

Source checks: [hasselblad-download](https://www.hasselblad.com/support/downloads/) (unavailable), [hasselblad-h](https://www.hasselblad.com/h-system/) (retrieved), [hasselblad-products](https://www.hasselblad.com/products/) (retrieved), [hasselblad-v](https://www.hasselblad.com/v-system/) (retrieved), [hasselblad-x](https://www.hasselblad.com/x-system/) (retrieved), [libraw-cameras](https://www.libraw.org/supported-cameras) (retrieved). Retrieval status is recorded separately from relevance; an HTTP response is not source validation.

Model evidence, split by source type:

- [inventory-hasselblad-official-1](inventory-hasselblad-official-1.md)
- [inventory-hasselblad-libraw-1](inventory-hasselblad-libraw-1.md)

The [audit method and remaining gaps](../manufacturer-audit-findings.md) explain the denominator and completion boundary.
