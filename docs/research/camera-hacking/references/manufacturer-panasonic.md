# Panasonic / LUMIX: discovery reference

Accessed 2026-10-29. Status: **Historical patching and modern control paths documented**. Evidence is documentation and attributed project reports; no camera behavior was reproduced here.

## Retained primary sources

- [PTool project wiki](https://www.personal-view.com/faqs/gh2-hack/ptool-software): Historical firmware manipulation for GH-series cameras; the example explicitly identifies GH1 1.32. The page alone is not a current compatibility roster.
- [GH4Hack](https://github.com/terrancewong/GH4Hack): Work-in-progress GH4 research, including regional ROM investigation. This is not evidence of a universally usable GH4 language unlock.
- [LUMIX Remote](https://github.com/sapoepsilon/lumix-remote): Reverse-engineered wireless control with a specific tested S5 record; other bodies are listed as untested generic profiles.
- [Official LUMIX SDK](https://av.jpn.support.panasonic.com/support/global/cs/soft/tool/sdk.html): Vendor integration route with an explicit supported-model list. SDK support is not permission or capability to install modified firmware.

## Compatibility and next evidence

Historical GH1/GH2 video patches do not establish modern S or G-series firmware modifiability. Compare official control options before proposing modifications.

## Model records

- [panasonic-s5](model-panasonic-s5.md)

Before proposing a device operation, resolve exact stock identity, affected persistent state, release provenance, feature test scope, and the recovery evidence for that operation. Discovery does not establish installation readiness.

## Manufacturer completeness audit — 2026-10-29

LUMIX S/G/GH/GX/GF/GM, earlier Four Thirds L1/L10, fixed-lens TZ/ZS/LX/FZ/FT/TS/FX/FH/FS/FP/LS/LZ/SZ/CM and digital camcorders.

**Finding: coverage remains incomplete.** 118 firmware source rows preserve regional alias bundles and exceptions. Models without updates, legacy Four Thirds and HC/AG/AU/V broadcast/camcorder lines are not a complete worldwide census. The initial /fts/index.html was an empty redirect stub, not a roster.

PTool GH1/GH2, GH4 language research, LUMIX Remote tested S5 and official SDK are separate compatibility paths.

Source checks: [gphoto-cameras](https://gphoto.sourceforge.io/proj/libgphoto2/support.php) (retrieved), [libraw-cameras](https://www.libraw.org/supported-cameras) (retrieved), [panasonic-compact](https://av.jpn.support.panasonic.com/support/global/cs/dsc/download/index2.html) (retrieved), [panasonic-firmware](https://av.jpn.support.panasonic.com/support/global/cs/dsc/download/fts/index.html) (retrieved), [panasonic-fullframe](https://av.jpn.support.panasonic.com/support/global/cs/dsc/download/index4.html) (retrieved), [panasonic-manuals](https://av.jpn.support.panasonic.com/support/global/cs/dsc/oi/index.html) (unavailable), [panasonic-mft](https://av.jpn.support.panasonic.com/support/global/cs/dsc/download/index.html) (retrieved). Retrieval status is recorded separately from relevance; an HTTP response is not source validation.

Model evidence, split by source type:

- [inventory-panasonic-official-1](inventory-panasonic-official-1.md)
- [inventory-panasonic-official-2](inventory-panasonic-official-2.md)
- [inventory-panasonic-gphoto-1](inventory-panasonic-gphoto-1.md)
- [inventory-panasonic-libraw-1](inventory-panasonic-libraw-1.md)

The [audit method and remaining gaps](../manufacturer-audit-findings.md) explain the denominator and completion boundary.
