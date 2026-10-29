# Kodak: discovery reference

Accessed 2026-10-29. Status: **Distinct legacy digital-back and Charmera projects documented**. Evidence is documentation and attributed project reports; no camera behavior was reproduced here.

## Retained primary sources

- [Kodak DCS Tools](https://github.com/Alexey-Danilchenko/Kodak-DCS-Tools): Research spans ProBack 645M/C/H, DCS 14n and SLR/n/SLR/c: firmware tools, calibration/remapping, profiles, protocol work and a hardware backlight upgrade.
- [Keychain Camera Plus](https://github.com/benbadio/keychain-camera-plus): Charmera toolkit claims a card-installed UVC webcam mode with retained standalone capture and a stock restoration route. It identifies a Generalplus GPCV1235F target.

## Compatibility and next evidence

The Kodak name does not establish a shared firmware lineage. Charmera, PIXPRO and old DCS bodies require separate board/firmware records. Do not redistribute vendor blobs merely because an upstream repository includes them.

## Model records

- [kodak-charmera](model-kodak-charmera.md)

Before proposing a device operation, resolve exact stock identity, affected persistent state, release provenance, feature test scope, and the recovery evidence for that operation. Discovery does not establish installation readiness.

## Manufacturer completeness audit — 2026-10-29

DCS/ProBack, EasyShare/DC/Advantix digital heritage, PIXPRO, Charmera and licensed instant/hybrid cameras.

**Finding: coverage remains incomplete.** PIXPRO support yields 44 current/previous labels plus 100 gPhoto and 42 LibRaw rows. Serial-number firmware branches matter. No single Kodak page covers every historical/licensee line; Charmera and other licensed mini/hybrid bodies need separate catalogs.

Kodak DCS/ProBack tools and Charmera Generalplus project are unrelated firmware families; raw decoding is separate.

Source checks: [gphoto-cameras](https://gphoto.sourceforge.io/proj/libgphoto2/support.php) (retrieved), [kodak-cameras](https://kodakpixpro.com/cameras/) (retrieved), [kodak-legacy](https://kodakpixpro.com/support/downloads/) (retrieved), [libraw-cameras](https://www.libraw.org/supported-cameras) (retrieved). Retrieval status is recorded separately from relevance; an HTTP response is not source validation.

Model evidence, split by source type:

- [inventory-kodak-official-1](inventory-kodak-official-1.md)
- [inventory-kodak-gphoto-1](inventory-kodak-gphoto-1.md)
- [inventory-kodak-libraw-1](inventory-kodak-libraw-1.md)

The [audit method and remaining gaps](../manufacturer-audit-findings.md) explain the denominator and completion boundary.
