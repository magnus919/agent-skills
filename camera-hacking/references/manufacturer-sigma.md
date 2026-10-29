# Sigma: discovery reference

Accessed 2026-10-29. Status: **fp firmware research and card tooling documented**. Evidence is documentation and attributed project reports; no camera behavior was reproduced here.

## Retained primary sources

- [fpSup](https://github.com/ijigen/fpSup): Research targets fp 5.02; fp L addresses differ. The author describes AI-assisted development, a recording-state test miss, persistent settings, and fallible AI notes.

## Compatibility and next evidence

Use the project as a model-specific research lead, not a general Sigma firmware manual. Confirm released feature records for open-gate/gyro claims separately.

## Model records

- [sigma-fp](model-sigma-fp.md)

Before proposing a device operation, resolve exact stock identity, affected persistent state, release provenance, feature test scope, and the recovery evidence for that operation. Discovery does not establish installation readiness.

## Manufacturer completeness audit — 2026-10-29

BF, fp/fp L, sd Quattro/H, SD DSLR, DP/dp Merrill/Quattro and prior compact revisions.

**Finding: coverage remains incomplete.** Twenty-two camera-only firmware rows extracted, excluding all lens/accessory rows. LibRaw adds SD10/DP1s leads absent from that table. No-update and regional/kit variants need reconciliation.

fpSup targets fp 5.02; fp L/BF/SD/DP addresses and functions are not covered by that result.

Source checks: [gphoto-cameras](https://gphoto.sourceforge.io/proj/libgphoto2/support.php) (retrieved), [libraw-cameras](https://www.libraw.org/supported-cameras) (retrieved), [sigma-firmware](https://www.sigma-global.com/en/support/firmware/) (retrieved). Retrieval status is recorded separately from relevance; an HTTP response is not source validation.

Model evidence, split by source type:

- [inventory-sigma-official-1](inventory-sigma-official-1.md)
- [inventory-sigma-gphoto-1](inventory-sigma-gphoto-1.md)
- [inventory-sigma-libraw-1](inventory-sigma-libraw-1.md)

The [audit method and remaining gaps](evidence-scope.md) explain the denominator and completion boundary.
