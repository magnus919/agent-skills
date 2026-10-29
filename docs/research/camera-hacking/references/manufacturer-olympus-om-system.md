# Olympus / OM System: discovery reference

Accessed 2026-10-29. Status: **Multiple model-specific firmware projects documented**. Evidence is documentation and attributed project reports; no camera behavior was reproduced here.

## Retained primary sources

- [Olympus firmware research](https://github.com/fishcu/oly_fw_analysis): PEN-F-focused firmware research with cross-model comparisons, MN103 tools and explicit evidence levels. Image-processing hardware is not emulated.
- [OM modification release dbv0.3.0](https://github.com/azqeurio/om-c-firmware/releases/tag/dbv0.3.0): Release notes report Panasonic lens aperture-ring compatibility across several bodies and additional OM-1 features. Per-body firmware identities and recovery need further inspection.

## Compatibility and next evidence

Lens interoperability belongs to the camera-body record: an Olympus patch enabling a Panasonic lens ring is not a Panasonic firmware hack. Do not infer E-M or OM compatibility from similar code.

## Model records

- [olympus-pen-f](model-olympus-pen-f.md)
- [om-system-om1](model-om-system-om1.md)

Before proposing a device operation, resolve exact stock identity, affected persistent state, release provenance, feature test scope, and the recovery evidence for that operation. Discovery does not establish installation readiness.

## Manufacturer completeness audit — 2026-10-29

OM/OM-D/PEN, Four Thirds E, TG/Tracker; older C/CAMEDIA/FE/SP/mju/STYLUS/XZ/SZ/VH/VR.

**Finding: coverage remains incomplete.** Body/manual and firmware tables merged as source rows, with no-update E-PL10 and TG-6 retained. Compact and early Four Thirds archive completeness remains unresolved; firmware availability is not the model denominator.

fishcu/firmware analysis and per-model Olympus firmware database are documentary routes. PEN-F/OM-1 offsets or recovery cannot be generalized.

Source checks: [gphoto-cameras](https://gphoto.sourceforge.io/proj/libgphoto2/support.php) (retrieved), [libraw-cameras](https://www.libraw.org/supported-cameras) (retrieved), [om-download](https://support.jp.omsystem.com/en/support/imsg/digicamera/download/software/) (retrieved), [om-ilc-firmware](https://support.jp.omsystem.com/en/support/imsg/digicamera/download/software/firm/e1/) (retrieved), [om-legacy-manuals](https://support.jp.omsystem.com/en/support/imsg/digicamera/download/manual/compact.html) (unavailable), [om-pen-manuals](https://support.jp.omsystem.com/en/support/imsg/digicamera/download/manual/pen.html) (retrieved), [om-tg-manuals](https://support.jp.omsystem.com/en/support/imsg/digicamera/download/manual/tg.html) (retrieved). Retrieval status is recorded separately from relevance; an HTTP response is not source validation.

Model evidence, split by source type:

- [inventory-olympus-om-system-official-1](inventory-olympus-om-system-official-1.md)
- [inventory-olympus-om-system-gphoto-1](inventory-olympus-om-system-gphoto-1.md)
- [inventory-olympus-om-system-libraw-1](inventory-olympus-om-system-libraw-1.md)

The [audit method and remaining gaps](../manufacturer-audit-findings.md) explain the denominator and completion boundary.
