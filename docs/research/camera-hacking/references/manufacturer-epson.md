# Epson: discovery reference and gap

Accessed 2026-10-29. **Baseline/lead only; no camera modification qualified.** This is a bounded search result, not evidence that modification is impossible.

## Search and retained finding

Query: `Epson R-D1 firmware reverse engineering hack camera`. Some legacy brands were searched together; this is weaker coverage than an individual model investigation.

Official R-D1 firmware-update bulletin; an update procedure is not a third-party feature-modification project.

Source route: [Epson primary baseline](https://files.support.epson.com/pdf/rd1___/rd1___ps.pdf). A transfer, ordinary firmware-update or official control entry does not establish feature patching or recoverability. No device test was performed.

## Next evidence

Separate the R-D1, R-D1s and R-D1x identities. Printer-firmware reverse-engineering results are out of scope.

A future record needs exact stock identity, a primary implementation, its evidence level and an operation-specific recovery record before recommending a modification.

## Manufacturer completeness audit — 2026-10-29

R-D1/R-D1s/R-D1xG, L compact cameras and CP/PhotoPC heritage.

**Finding: coverage remains incomplete.** Japanese vendor index yields 20 download identities. CP regional names and international PhotoPC aliases need reconciliation; R-D1xG is the vendor grip-kit identity.

R-D1 vendor 2.0 upgrade explicitly disallows downgrade. No third-party feature patch qualified.

Source checks: [epson-cameras](https://www.epson.jp/support/portal/download/rd-1.htm) (unavailable), [epson-models](https://www.epson.jp/support/download/ks/13.htm) (retrieved), [gphoto-cameras](https://gphoto.sourceforge.io/proj/libgphoto2/support.php) (retrieved), [libraw-cameras](https://www.libraw.org/supported-cameras) (retrieved). Retrieval status is recorded separately from relevance; an HTTP response is not source validation.

Model evidence, split by source type:

- [inventory-epson-official-1](inventory-epson-official-1.md)
- [inventory-epson-gphoto-1](inventory-epson-gphoto-1.md)
- [inventory-epson-libraw-1](inventory-epson-libraw-1.md)

The [audit method and remaining gaps](../manufacturer-audit-findings.md) explain the denominator and completion boundary.
