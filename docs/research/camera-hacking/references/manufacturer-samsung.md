# Samsung: discovery reference

Accessed 2026-10-29. Status: **NX-generation Linux modification projects documented**. Evidence is documentation and attributed project reports; no camera behavior was reproduced here.

## Retained primary sources

- [Samsung NX hacks](https://github.com/ge0rg/samsung-nx-hacks): The project distinguishes Linux-based NX generations from other processors/OS families; a family-wide Linux assumption is incorrect.
- [NX1/NX500 modding](https://github.com/ottokiksmaler/nx500_nx1_modding): Historical modifications include video settings, scripting and focus stacking. NX-KS2 is persistent in flash; its original developer page has disappeared and binaries rely on mirrors.

## Compatibility and next evidence

Archive provenance, exact firmware and model-specific behavior need recovery before any installation recommendation. Modern host availability and mirrored binaries were not tested.

## Model records

- [samsung-nx1-nx500](model-samsung-nx1-nx500.md)

Before proposing a device operation, resolve exact stock identity, affected persistent state, release provenance, feature test scope, and the recovery evidence for that operation. Discovery does not establish installation readiness.

## Manufacturer completeness audit — 2026-10-29

NX/NX mini/GX DSLRs; EX/WB/ST/PL/ES/Digimax/i/L/NV compact families; separate Gear 360 camera track.

**Finding: coverage remains incomplete.** Manufacturer downloads shell does not yield the retired camera roster. Six gPhoto and 44 LibRaw labels do not cover every digital compact or regional NX/GX variant.

NX generation architecture differences, NX1/NX500 mods and GX-10 pkTriggerCord route; no Linux assumption for every Samsung camera.

Source checks: [gphoto-cameras](https://gphoto.sourceforge.io/proj/libgphoto2/support.php) (retrieved), [libraw-cameras](https://www.libraw.org/supported-cameras) (retrieved), [samsung-cameras](https://www.samsung.com/us/support/downloads/) (retrieved). Retrieval status is recorded separately from relevance; an HTTP response is not source validation.

Model evidence, split by source type:

- [inventory-samsung-gphoto-1](inventory-samsung-gphoto-1.md)
- [inventory-samsung-libraw-1](inventory-samsung-libraw-1.md)

The [audit method and remaining gaps](../manufacturer-audit-findings.md) explain the denominator and completion boundary.
