# Leica: discovery reference

Accessed 2026-10-29. Status: **Firmware analysis and debug-interface tooling documented**. Evidence is documentation and attributed project reports; no camera behavior was reproduced here.

## Retained primary sources

- [LeicaHacks](https://github.com/alexhude/LeicaHacks): Provides M240 firmware/UI tools, IDA scripts, Softune signatures and a debug-PTP proof of concept; separate tools inspect M8/M9 containers and M9 XOR encoding.

## Compatibility and next evidence

The retained project demonstrates analysis tooling, not a maintained consumer feature package. Do not transfer M240 findings to M10/M11, Q, SL or D-Lux bodies, or cross-flash related Panasonic/Leica cameras.

## Model records

- [leica-m8-m9-m240](model-leica-m8-m9-m240.md)

Before proposing a device operation, resolve exact stock identity, affected persistent state, release provenance, feature test scope, and the recovery evidence for that operation. Discovery does not establish installation readiness.

## Manufacturer completeness audit — 2026-10-29

Digital M, Q, SL, S/S2, CL/T/TL, X, D/C/V-Lux, Digilux, SOFORT 2 and Digital-Modul-R heritage.

**Finding: coverage remains incomplete.** Fourteen current digital/hybrid navigation labels plus legacy LibRaw subset retained. Analog M6/MP/M-A and original analog SOFORT excluded. Legacy firmware/download taxonomy is not a complete model census or full special-edition roster.

LeicaHacks M8/M9/M240 scope stays separate from M10/M11/Q/SL; official FOTOS/control is another mechanism.

Source checks: [gphoto-cameras](https://gphoto.sourceforge.io/proj/libgphoto2/support.php) (retrieved), [leica-cameras](https://leica-camera.com/en-int/photography/cameras) (retrieved), [leica-download](https://leica-camera.com/en-int/downloads) (retrieved), [libraw-cameras](https://www.libraw.org/supported-cameras) (retrieved). Retrieval status is recorded separately from relevance; an HTTP response is not source validation.

Model evidence, split by source type:

- [inventory-leica-official-1](inventory-leica-official-1.md)
- [inventory-leica-gphoto-1](inventory-leica-gphoto-1.md)
- [inventory-leica-libraw-1](inventory-leica-libraw-1.md)

The [audit method and remaining gaps](../manufacturer-audit-findings.md) explain the denominator and completion boundary.
