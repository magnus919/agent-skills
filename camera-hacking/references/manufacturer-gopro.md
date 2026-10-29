# GoPro: discovery reference

Accessed 2026-10-29. Status: **Vendor experimental firmware and developer interfaces documented**. Evidence is documentation and attributed project reports; no camera behavior was reproduced here.

## Retained primary sources

- [GoPro Labs](https://github.com/gopro/labs): Vendor-hosted experimental firmware uses QR controls and publishes a model/feature matrix. Extended features are off by default; individual functions remain experimental.
- [GoPro developer tools](https://gopro.com/en/ps/info/developer-tools): Official SDK and individual HTTP/BLE controls provide interoperability alternatives.

## Compatibility and next evidence

Treat Labs as a vendor experimental path, not a third-party jailbreak. Verify the exact camera release and feature row; a function existing in Labs does not mean every GoPro supports it.

Before proposing a device operation, resolve exact stock identity, affected persistent state, release provenance, feature test scope, and the recovery evidence for that operation. Discovery does not establish installation readiness.

## Manufacturer completeness audit — 2026-10-29

MISSION, HERO Black/Silver/White/Session/Mini/Bones, MAX/MAX2 and Fusion heritage.

**Finding: coverage remains incomplete.** Shop/compare labels and Labs release list retained. Bare HERO is ambiguous across years; editions/creator kits are not separate bodies. Early Digital HERO and all historical Silver/White/Session variants are not fully reconciled.

Labs exact model releases plus per-feature matrix; Open GoPro official control. Not every current body has a Labs release (e.g. do not infer LIT HERO).

Source checks: [gopro-cameras](https://gopro.com/en/us/shop/cameras) (retrieved), [gopro-labs](https://raw.githubusercontent.com/gopro/labs/master/README.md) (retrieved), [gopro-manuals](https://gopro.com/en/us/update) (unavailable), [gphoto-cameras](https://gphoto.sourceforge.io/proj/libgphoto2/support.php) (retrieved), [libraw-cameras](https://www.libraw.org/supported-cameras) (retrieved). Retrieval status is recorded separately from relevance; an HTTP response is not source validation.

Model evidence, split by source type:

- [inventory-gopro-official-1](inventory-gopro-official-1.md)
- [inventory-gopro-gphoto-1](inventory-gopro-gphoto-1.md)
- [inventory-gopro-libraw-1](inventory-gopro-libraw-1.md)

The [audit method and remaining gaps](evidence-scope.md) explain the denominator and completion boundary.

## Labs release scope refresh

The [vendor Labs README](https://github.com/gopro/labs) currently lists MISSION 1 PRO ILS/PRO/1, MAX2 and HERO13 Black as shipping-camera releases, alongside older HERO12/11/11 Mini/10/MAX/9/8/7 and HERO5 Session releases. Each feature row has its own compatibility outcomes; neither a release entry nor a successful QR decode proves every feature works on that body. LIT HERO and bare HERO shop entries must not inherit Labs compatibility. No firmware binary was downloaded.
