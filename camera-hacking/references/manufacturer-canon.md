# Canon: discovery reference

Accessed 2026-10-29. Status: **Established add-ons and newer creative firmware documented**. Evidence is documentation and attributed project reports; no camera behavior was reproduced here.

## Retained primary sources

- [Magic Lantern source](https://github.com/reticulatedpines/magiclantern_simplified): Card-loaded software runs alongside Canon firmware; the project documents boot enablement and a related QEMU camera emulator.
- [CHDK autobuild](https://build.chdk.photos/): Offers an unofficial add-on for selected Canon cameras. Release-branch stability describes features/interfaces, not a guarantee against camera crashes.
- [The Ritual](https://latentstudios.art/firmware/): Advertises in-camera film rendering for EOS 5D and 5D Mark II, with Canon 1.1.1 and 2.1.2 respectively. The page says install/removal steps will accompany release; release readiness needs checking.

## Compatibility and next evidence

Keep CHDK and Magic Lantern target lists separate, including their EOS M overlaps. Do not infer support for current EOS R bodies from DSLR history.

## Model records

- [canon-5d-family](model-canon-5d-family.md)

Before proposing a device operation, resolve exact stock identity, affected persistent state, release provenance, feature test scope, and the recovery evidence for that operation. Discovery does not establish installation readiness.

## Manufacturer completeness audit — 2026-10-29

EOS DSLR/M/R, PowerShot/IXUS/IXY, Cinema EOS, digital video and HD camcorders.

**Finding: coverage remains incomplete.** 466 museum product entries extracted from digital categories, excluding film, analog still-video and 8mm tape. Regional aliases may share entries. Current store retrieval failed; museum coverage is not a verified current worldwide offering list.

CHDK and Magic Lantern are separate compatibility paths; modern ML platform directories are research evidence, not released ports. The Ritual remains a separate 5D target.

Source checks: [canon-chdk](https://build.chdk.photos/) (retrieved), [canon-current](https://www.usa.canon.com/shop/cameras) (unavailable), [canon-ml-platforms](https://api.github.com/repos/reticulatedpines/magiclantern_simplified/git/trees/dev?recursive=1) (retrieved), [canon-museum](https://global.canon/en/c-museum/camera.html) (retrieved), [gphoto-cameras](https://gphoto.sourceforge.io/proj/libgphoto2/support.php) (retrieved), [libraw-cameras](https://www.libraw.org/supported-cameras) (retrieved). Retrieval status is recorded separately from relevance; an HTTP response is not source validation.

Model evidence, split by source type:

- [inventory-canon-official-1](inventory-canon-official-1.md)
- [inventory-canon-official-2](inventory-canon-official-2.md)
- [inventory-canon-official-3](inventory-canon-official-3.md)
- [inventory-canon-official-4](inventory-canon-official-4.md)
- [inventory-canon-official-5](inventory-canon-official-5.md)
- [inventory-canon-gphoto-1](inventory-canon-gphoto-1.md)
- [inventory-canon-gphoto-2](inventory-canon-gphoto-2.md)
- [inventory-canon-gphoto-3](inventory-canon-gphoto-3.md)
- [inventory-canon-gphoto-4](inventory-canon-gphoto-4.md)
- [inventory-canon-libraw-1](inventory-canon-libraw-1.md)
- [inventory-canon-libraw-2](inventory-canon-libraw-2.md)

The [audit method and remaining gaps](evidence-scope.md) explain the denominator and completion boundary.

## Magic Lantern source-tree scope refresh

The inspected [development tree](https://github.com/reticulatedpines/magiclantern_simplified/tree/dev/platform) includes older DSLR/EOS M ports and newer research directories for EOS R/RP/R5/R6, M50/M6 II, SX70/SX740 and XF605. A directory is **not** a released, supported or camera-qualified build. Check the project's port/build status and exact stock version independently before interpreting it as useful capability. The captured tree is complete (`truncated=false`) and its immutable tree SHA is recorded in [the platform inventory](../assets/canon-platform-inventory.json). CHDK's autobuild branch selector was also inspected; the dynamic build matrix was not extracted, so no full CHDK supported-model claim is made.
