# Casio: discovery gap

Accessed 2026-10-29. **No primary modification workflow qualified in this pass. This does not mean the cameras cannot be modified.**

## Search result

Targeted camera/firmware/RAW searches found legacy RAW-menu leads but no primary, camera-qualified modification workflow retained.

## Retained baseline

The [gPhoto camera list](https://gphoto.sourceforge.io/proj/libgphoto2/support.php) and [remote-control list](https://gphoto.sourceforge.io/doc/remote/) provide model-level interoperability leads. A transfer entry establishes neither remote shooting nor firmware modification. Resolve the exact model before interpreting an entry.

## Next investigation

Check QV/Exilim model-specific archives and distinguish data extraction from firmware modification.

No binary, patcher, recovery method, supported firmware or hardware test is claimed here.

## Manufacturer completeness audit — 2026-10-29

QV and EXILIM EX families, TR/TR M/FR/GZE, plus WQV camera watches.

**Finding: coverage remains incomplete.** Official regional manual search loads but warns some products are absent and does not render a complete model list. Thirteen gPhoto and 53 LibRaw labels are independent subsets, not the full QV/EX catalog.

New retained WQV protocol and WQV Blink interoperability projects; RAW-menu decoder labels alone do not qualify a firmware procedure.

Source checks: [casio-cameras](https://support.casio.com/en/dc/manual/) (unavailable), [casio-manual-models](https://www.casio.com/sg/support/digital-cameras/manual/) (retrieved), [casio-manuals](https://support.casio.jp/manuallist.php?cid=001) (unavailable), [casio-protocol](https://www.mgroeber.de/wqvprot.html) (retrieved), [casio-wqv](https://raw.githubusercontent.com/partlyhuman/wqv-blink/main/README.md) (retrieved), [gphoto-cameras](https://gphoto.sourceforge.io/proj/libgphoto2/support.php) (retrieved), [libraw-cameras](https://www.libraw.org/supported-cameras) (retrieved). Retrieval status is recorded separately from relevance; an HTTP response is not source validation.

Model evidence, split by source type:

- [inventory-casio-gphoto-1](inventory-casio-gphoto-1.md)
- [inventory-casio-libraw-1](inventory-casio-libraw-1.md)

The [audit method and remaining gaps](evidence-scope.md) explain the denominator and completion boundary.

## Additional primary interoperability evidence

[Marcus Gröber's WQV-1 protocol notes](https://www.mgroeber.de/wqvprot.html) document the infrared transfer protocol. [WQV Blink](https://github.com/partlyhuman/wqv-blink/) declares WQV-1/2 support in its wqv12 firmware and WQV-3/10 support in wqv310. These are replacement host/dongle implementations for extracting photographs, not new capture features flashed onto the watch. No hardware or modern-host result was reproduced in this audit.
