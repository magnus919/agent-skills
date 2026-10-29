# Sony: discovery reference

Accessed 2026-10-29. Status: **PMCA-era apps/settings and research modes documented**. Evidence is documentation and attributed project reports; no camera behavior was reproduced here.

## Retained primary sources

- [Sony-PMCA-RE](https://github.com/ma1co/Sony-PMCA-RE): Documents app installation, updater execution and service-mode paths, each with different compatibility and driver requirements. Some architectures reject the updater method through signatures.
- [OpenMemories Tweak](https://github.com/ma1co/OpenMemories-Tweak): Changes existing hidden settings on compatible cameras. Modified settings can persist after app removal; factory-reset behavior is not uniform.

## Compatibility and next evidence

Separate legacy PMCA bodies from modern Alpha/FX cameras. The video's a7 IV shutter-angle report was not traced to a primary patch/recovery record in this pass.

## Model records

- [sony-pmca-era](model-sony-pmca-era.md)

Before proposing a device operation, resolve exact stock identity, affected persistent state, release provenance, feature test scope, and the recovery evidence for that operation. Discovery does not establish installation readiness.

## Manufacturer completeness audit — 2026-10-29

Alpha A/E/NEX, Cyber-shot/DSC/RX/QX, digital Mavica, Handycam, Action Cam and FX/Cinema generations.

**Finding: coverage remains incomplete.** Official support shows 643 digital-category entries but includes lenses and exposes only initial results; video support is separately paginated. Direct captures failed. The 158 gPhoto and 115 LibRaw rows are subsets, not 643 cameras or a full Sony census.

PMCA updater/app/service modes and OpenMemories vary by architecture. Modern Alpha/FX claims require their own primary port and recovery evidence.

Source checks: [gphoto-cameras](https://gphoto.sourceforge.io/proj/libgphoto2/support.php) (retrieved), [libraw-cameras](https://www.libraw.org/supported-cameras) (retrieved), [sony-alpha-support](https://www.sony.com/electronics/support/interchangeable-lens-cameras-e-mount-body) (unavailable), [sony-cameras](https://www.sony.com/electronics/support/cameras-camcorders-digital-cameras) (unavailable), [sony-cybershot-support](https://www.sony.com/electronics/support/compact-cameras-dsc-rx-series) (unavailable), [sony-pmca-devices](https://raw.githubusercontent.com/ma1co/Sony-PMCA-RE/master/README.md) (retrieved), [sony-uk](https://www.sony.co.uk/electronics/support/cameras-camcorders-digital-cameras) (unavailable). Retrieval status is recorded separately from relevance; an HTTP response is not source validation.

Model evidence, split by source type:

- [inventory-sony-gphoto-1](inventory-sony-gphoto-1.md)
- [inventory-sony-gphoto-2](inventory-sony-gphoto-2.md)
- [inventory-sony-libraw-1](inventory-sony-libraw-1.md)
- [inventory-sony-libraw-2](inventory-sony-libraw-2.md)

The [audit method and remaining gaps](../manufacturer-audit-findings.md) explain the denominator and completion boundary.
