# Ricoh: discovery reference

Accessed 2026-10-29. Status: **Firmware research and patcher documented**. Evidence is documentation and attributed project reports; no camera behavior was reproduced here.

## Full-family coverage

Start with the [complete digital GR-series model map](family-ricoh-gr-series.md). It includes every captured vendor-roster identity, model/lineage references, primary project routes and explicit gaps. This supersedes the initial narrow model sample as the discovery entry point; it does not broaden any existing patch's compatibility.

## Retained primary sources

- [GR IV research](https://github.com/radium-wang/ricoh-gr4-firmware-analysis-and-feature-expansion): Firmware formats, factory interfaces, model identification and shutdown-image experiments. The project distinguishes offline results from camera qualification and supplies no general installable firmware.
- [GR4-MonoUnlock](https://github.com/lemonadesaltbagel/GR4-MonoUnlock): A local patcher for monochrome looks on the standard colour GR IV, specifically stock 1.11. Different GR variants and versions need independent evidence.

## Compatibility and next evidence

Keep GR III, IIIx, GR IV, HDF and Monochrome identities separate. The presenter's imperial-units patch remains a video report; its exact patch/source artifact was not located.

## Model records

- [GR II](model-ricoh-gr-ii.md)
- [GR III](model-ricoh-gr-iii.md)
- [GR IIIx](model-ricoh-gr-iiix.md)
- [GR IV](model-ricoh-gr-iv.md)
- [Legacy, HDF, Monochrome, editions and GR IVx](family-ricoh-gr-series.md)

Before proposing a device operation, resolve exact stock identity, affected persistent state, release provenance, feature test scope, and the recovery evidence for that operation. Discovery does not establish installation readiness.

## Manufacturer completeness audit — 2026-10-29

Full digital GR family audit retained; Caplio/R/CX/GX/GXR, WG/G business and THETA are separate expansion tracks.

**Finding: coverage remains incomplete.** GR source-bound coverage is 23 identities in family-coverage.json. Supplementary Ricoh firmware/gPhoto/LibRaw lists do not establish completeness of the other families. GXR modules and THETA require model-level records.

GR runtime, patcher and protocol project inventory remain per model/firmware; no GR IV patch compatibility inferred for other Ricoh cameras.

Source checks: [gphoto-cameras](https://gphoto.sourceforge.io/proj/libgphoto2/support.php) (retrieved), [libraw-cameras](https://www.libraw.org/supported-cameras) (retrieved), [pentax-download](https://www.ricoh-imaging.co.jp/english/support/download_digital.html) (retrieved). Retrieval status is recorded separately from relevance; an HTTP response is not source validation.

Model evidence, split by source type:

- [inventory-ricoh-official-1](inventory-ricoh-official-1.md)
- [inventory-ricoh-gphoto-1](inventory-ricoh-gphoto-1.md)
- [inventory-ricoh-libraw-1](inventory-ricoh-libraw-1.md)

The [audit method and remaining gaps](evidence-scope.md) explain the denominator and completion boundary.
