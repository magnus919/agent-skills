# Pentax: discovery reference

Accessed 2026-10-29. Status: **USB protocol/control and historical firmware leads**. Evidence is documentation and attributed project reports; no camera behavior was reproduced here.

## Retained primary sources

- [pkTriggerCord](https://github.com/asalamon74/pktriggercord): Documents Pentax USB tethering, a model support/bugs matrix and SCSI protocol notes. Captures are downloaded from camera buffers rather than written to the SD card.
- [Pentax Hack](https://www.pentax-hack.info/): Historical firmware-research lead surfaced in search, but direct retrieval returned no readable body in this pass. Do not use it as verified operational instructions.

## Compatibility and next evidence

K10D/GX-10 support is conditional on firmware 1.20 or later in pkTriggerCord. The unsupported/testing entries matter as much as the supported list. Ricoh GR findings do not apply to Pentax DSLRs.

Before proposing a device operation, resolve exact stock identity, affected persistent state, release provenance, feature test scope, and the recovery evidence for that operation. Discovery does not establish installation readiness.

## Manufacturer completeness audit — 2026-10-29

K/*ist DSLRs, 645 digital/IR, Q/K-01 mirrorless, Optio/MX/XG/X and WG/action families.

**Finding: coverage remains incomplete.** Firmware plus current product and Optio/WG archive records retained. Regional K-m/K2000 labels and slash-bundled K-5II/IIs are not silently deduplicated. Earliest compact/Optio bodies and all WG/GPS/region variants need archive reconciliation. Ricoh business/GR rows are kept in Ricoh.

pkTriggerCord model/bugs matrix and historical Pentax Hack accessibility limit retained; GR firmware cannot be applied to K/Q/645 bodies.

Source checks: [gphoto-cameras](https://gphoto.sourceforge.io/proj/libgphoto2/support.php) (retrieved), [libraw-cameras](https://www.libraw.org/supported-cameras) (retrieved), [pentax-archive](https://www.ricoh-imaging.co.jp/english/products/past/) (retrieved), [pentax-download](https://www.ricoh-imaging.co.jp/english/support/download_digital.html) (retrieved), [pentax-products](https://www.ricoh-imaging.co.jp/english/products/) (retrieved), [pentax-wg-archive](https://www.ricoh-imaging.co.jp/english/products/past/wg/) (retrieved). Retrieval status is recorded separately from relevance; an HTTP response is not source validation.

Model evidence, split by source type:

- [inventory-pentax-official-1](inventory-pentax-official-1.md)
- [inventory-pentax-official-2](inventory-pentax-official-2.md)
- [inventory-pentax-gphoto-1](inventory-pentax-gphoto-1.md)
- [inventory-pentax-libraw-1](inventory-pentax-libraw-1.md)

The [audit method and remaining gaps](../manufacturer-audit-findings.md) explain the denominator and completion boundary.
