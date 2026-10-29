# Xiaomi / YI: discovery reference

Accessed 2026-10-29. Status: **Model-specific action-camera scripting documented**. Evidence is documentation and attributed project reports; no camera behavior was reproduced here.

## Retained primary sources

- [Xiaomi Yi autoexec](https://github.com/PJanisio/Xiaomi_Yi_autoexec): Script collection targets first-generation Yi Sport; memory-write scripts need firmware/revision matching.
- [Yi 4K hacks](https://github.com/ddimensia/yi_4k_hacks): A separate project explicitly based on Yi 4K firmware 1.10.9.

## Compatibility and next evidence

Do not merge first-generation and 4K offsets or assume a startup script is transient. Consumer action-camera findings do not establish compatibility with YI home/security cameras.

Before proposing a device operation, resolve exact stock identity, affected persistent state, release provenance, feature test scope, and the recovery evidence for that operation. Discovery does not establish installation readiness.

## Manufacturer completeness audit — 2026-10-29

Yi Sport, Lite/Discovery, 4K/4K+, M1 mirrorless and Xiaomi/Mijia action hardware as distinct OEM tracks.

**Finding: coverage remains incomplete.** Current YI homepage promotes home/security systems and is not an action-camera archive. LibRaw identifies YI 4K and M1 only. Older action/4K+ and Xiaomi/Mijia regional/hardware revisions need separate manuals.

First-generation autoexec and 4K 1.10.9 projects remain separate. Security camera Yi-Hack does not establish action-camera compatibility.

Source checks: [libraw-cameras](https://www.libraw.org/supported-cameras) (retrieved), [yi-cameras](https://www.yitechnology.com/) (retrieved). Retrieval status is recorded separately from relevance; an HTTP response is not source validation.

Model evidence, split by source type:

- [inventory-xiaomi-yi-libraw-1](inventory-xiaomi-yi-libraw-1.md)

The [audit method and remaining gaps](../manufacturer-audit-findings.md) explain the denominator and completion boundary.
