# Konica / Minolta: discovery gap

Accessed 2026-10-29. **No primary modification workflow qualified in this pass. This does not mean the cameras cannot be modified.**

## Search result

Targeted searches found photography/metadata and legacy transfer material, not a retained feature-modification project.

## Retained baseline

The [gPhoto camera list](https://gphoto.sourceforge.io/proj/libgphoto2/support.php) and [remote-control list](https://gphoto.sourceforge.io/doc/remote/) provide model-level interoperability leads. A transfer entry establishes neither remote shooting nor firmware modification. Resolve the exact model before interpreting an entry.

## Next investigation

Investigate individual DiMAGE, Dynax/Maxxum and Konica identities; do not infer Sony Alpha firmware compatibility.

No binary, patcher, recovery method, supported firmware or hardware test is claimed here.

## Manufacturer completeness audit — 2026-10-29

Konica KD/Q/MG/Revio; Minolta RD/DiMAGE and Dynax/Maxxum/Alpha DSLR regional aliases.

**Finding: coverage remains incomplete.** Vendor support root unavailable. Fourteen gPhoto rows and 17 LibRaw names cover subsets; cameras across both brands and premerger naming need authored archive records. Modern licensed Minolta products are another unresolved catalog.

LibRaw source contains DiMAGE Z2 RAW-identification logic; this is decoding evidence, not a recovered camera-side enablement/recovery procedure. Sony firmware compatibility is not implied.

Source checks: [gphoto-cameras](https://gphoto.sourceforge.io/proj/libgphoto2/support.php) (retrieved), [konica-cameras](https://www.konicaminoltasupport.com/) (unavailable), [libraw-cameras](https://www.libraw.org/supported-cameras) (retrieved), [libraw-z2](https://raw.githubusercontent.com/LibRaw/LibRaw/master/src/metadata/identify.cpp) (retrieved). Retrieval status is recorded separately from relevance; an HTTP response is not source validation.

Model evidence, split by source type:

- [inventory-konica-minolta-gphoto-1](inventory-konica-minolta-gphoto-1.md)
- [inventory-konica-minolta-libraw-1](inventory-konica-minolta-libraw-1.md)

The [audit method and remaining gaps](evidence-scope.md) explain the denominator and completion boundary.

## Additional primary file-format evidence

[LibRaw identify.cpp](https://github.com/LibRaw/LibRaw/blob/master/src/metadata/identify.cpp) includes special identification paths for DiMAGE Z2 raw dumps. That source establishes decoder handling; the camera-side RAW enablement method, exact stock firmware and recovery procedure have not been recovered here. Treat historical RAW-mode forum instructions as leads until their original method is verified.
