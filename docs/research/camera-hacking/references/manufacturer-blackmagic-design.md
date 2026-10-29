# Blackmagic Design: discovery reference

Accessed 2026-10-29. Status: **Official camera-control protocols documented**. Evidence is documentation and attributed project reports; no camera behavior was reproduced here.

## Retained primary sources

- [Blackmagic developer camera resources](https://www.blackmagicdesign.com/developer/products/camera/sdk-and-software): Provides camera-control and REST documentation, plus SDI, Bluetooth and other interfaces. These are integration paths rather than evidence of replacement firmware.

## Compatibility and next evidence

Match the document and API generation to the camera and transport. Blackmagic RAW decoding or DeckLink support alone says nothing about modifying a camera.

Before proposing a device operation, resolve exact stock identity, affected persistent state, release provenance, feature test scope, and the recovery evidence for that operation. Discovery does not establish installation readiness.

## Manufacturer completeness audit — 2026-10-29

URSA Cine/Immersive, PYXIS, URSA Mini/Pro, Pocket/Cinema, Studio/Micro Studio and Broadcast; historical Cinema/Production/Micro Cinema bodies.

**Finding: coverage remains incomplete.** Current products page yields 16 camera/family headings after excluding accessories and the phone app. URSA Cine sensor/mount variants and discontinued bodies require product/support detail pages; the list is not every SKU.

Official REST/SDI/Bluetooth/control protocols. Media decoding and host capture cards do not establish firmware modification.

Source checks: [blackmagic-products](https://www.blackmagicdesign.com/products) (retrieved), [libraw-cameras](https://www.libraw.org/supported-cameras) (retrieved). Retrieval status is recorded separately from relevance; an HTTP response is not source validation.

Model evidence, split by source type:

- [inventory-blackmagic-design-official-1](inventory-blackmagic-design-official-1.md)
- [inventory-blackmagic-design-libraw-1](inventory-blackmagic-design-libraw-1.md)

The [audit method and remaining gaps](../manufacturer-audit-findings.md) explain the denominator and completion boundary.
