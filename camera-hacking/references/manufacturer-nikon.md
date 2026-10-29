# Nikon: discovery reference

Accessed 2026-10-29. Status: **Historical DSLR tools and Z30 research documented**. Evidence is documentation and attributed project reports; no camera behavior was reproduced here.

## Retained primary sources

- [Nikon firmware tools](https://github.com/simeonpilgrim/nikon-firmware-tools): Research repository originally focused on D5100/D7000 with firmware, emulator and PTP tooling.
- [Wonder Lantern Z30](https://github.com/WonderLantern/wonder-lantern-z30): Experimental extensions with a model-specific builder, original-byte checks and explicitly separated offline/device evidence.

## Compatibility and next evidence

DSLR patching history is not evidence of general Z-series support. A valid EG module is not a complete Nikon firmware update package.

## Model records

- [nikon-z30](model-nikon-z30.md)

Before proposing a device operation, resolve exact stock identity, affected persistent state, release provenance, feature test scope, and the recovery evidence for that operation. Discovery does not establish installation readiness.

## Manufacturer completeness audit — 2026-10-29

Z mirrorless, ZR cinema, F digital SLR, Nikon 1, COOLPIX and KeyMission.

**Finding: coverage remains incomplete.** 192 names extracted from five camera categories in the official selector XML, excluding lenses/accessories. The separately inspected archive currently lists software, not additional cameras; older COOLPIX/E-series and regional names must be reconciled before declaring all-time completeness.

NikonHacker DSLR patch tools and Wonder Lantern Z30 are distinct. Legacy COOLPIX DIAG RAW decoding does not establish modern Z compatibility.

Source checks: [gphoto-cameras](https://gphoto.sourceforge.io/proj/libgphoto2/support.php) (retrieved), [libraw-cameras](https://www.libraw.org/supported-cameras) (retrieved), [nikon-archive](https://downloadcenter.nikonimglib.com/en/archive.html) (retrieved), [nikon-categories](https://downloadcenter.nikonimglib.com/en/0/product_data.xml) (retrieved), [nikon-hacker](https://raw.githubusercontent.com/simeonpilgrim/nikon-firmware-tools/master/README.md) (retrieved), [nikon-products](https://downloadcenter.nikonimglib.com/en/1/product_data.xml) (retrieved). Retrieval status is recorded separately from relevance; an HTTP response is not source validation.

Model evidence, split by source type:

- [inventory-nikon-official-1](inventory-nikon-official-1.md)
- [inventory-nikon-official-2](inventory-nikon-official-2.md)
- [inventory-nikon-gphoto-1](inventory-nikon-gphoto-1.md)
- [inventory-nikon-gphoto-2](inventory-nikon-gphoto-2.md)
- [inventory-nikon-gphoto-3](inventory-nikon-gphoto-3.md)
- [inventory-nikon-libraw-1](inventory-nikon-libraw-1.md)
- [inventory-nikon-libraw-2](inventory-nikon-libraw-2.md)

The [audit method and remaining gaps](evidence-scope.md) explain the denominator and completion boundary.
