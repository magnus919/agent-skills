# Ricoh GR: full digital-family discovery map

Checked 2026-10-29. This map includes **13 digital body/processing variants, nine named editions and one announced model**: 23 explicit identities. It covers the older small-sensor GR DIGITAL I–IV as well as APS-C GR generations. Model coverage is not a claim that every camera has usable custom firmware.

## Complete identity ledger

Official versions are observations from the current or legacy vendor index; an edition with no separately resolved image is marked unknown instead of inheriting a version.

| Identity / official source | Vendor version observed | Research route |
|---|---|---|
| [GR DIGITAL](https://www.ricoh-imaging.co.jp/english/r_dc/download/index.html) | 2.40 | [GR DIGITAL](model-ricoh-gr-digital.md) |
| [GR DIGITAL II](https://www.ricoh-imaging.co.jp/english/r_dc/download/index.html) | 2.40 | [GR DIGITAL II](model-ricoh-gr-digital-ii.md) |
| [GR DIGITAL III](https://www.ricoh-imaging.co.jp/english/r_dc/download/index.html) | 2.50 | [GR DIGITAL III](model-ricoh-gr-digital-iii.md) |
| [GR DIGITAL IV](https://www.ricoh-imaging.co.jp/english/r_dc/download/index.html) | 2.30 | [GR DIGITAL IV](model-ricoh-gr-digital-iv.md) |
| [GR (2013 APS-C)](https://www.ricoh-imaging.co.jp/english/support/digital/gr_s.html) | 5.01 | [GR (2013 APS-C)](model-ricoh-gr-2013.md) |
| [GR II](https://www.ricoh-imaging.co.jp/english/support/digital/gr2_s.html) | 3.00 | [GR II](model-ricoh-gr-ii.md) |
| [GR III](https://www.ricoh-imaging.co.jp/english/support/digital/gr3_s.html) | 2.20 | [GR III](model-ricoh-gr-iii.md) |
| [GR III HDF](https://www.ricoh-imaging.co.jp/english/products/gr-3/special/) | 2.20 | [GR III](ricoh-gr-editions-and-variants.md) |
| [GR IIIx](https://www.ricoh-imaging.co.jp/english/support/digital/gr3x_s.html) | 1.70 | [GR IIIx](model-ricoh-gr-iiix.md) |
| [GR IIIx HDF](https://www.ricoh-imaging.co.jp/english/products/gr-3/special/) | 1.70 | [GR IIIx](ricoh-gr-editions-and-variants.md) |
| [GR IV](https://www.ricoh-imaging.co.jp/english/support/digital/gr4_s.html) | 1.20 | [GR IV](model-ricoh-gr-iv.md) |
| [GR IV HDF](https://www.ricoh-imaging.co.jp/english/products/gr-4/special/hdf/) | 1.20 | [GR IV](ricoh-gr-editions-and-variants.md) |
| [GR IV Monochrome](https://www.ricoh-imaging.co.jp/english/support/download_digital.html) | 1.10 | [GR IV Monochrome](ricoh-gr-editions-and-variants.md) |
| [GR DIGITAL 1st Anniversary](https://www.ricoh-imaging.co.jp/japan/dc/gr/digital/) | Separate identity/version unresolved | [GR DIGITAL](ricoh-gr-editions-and-variants.md) |
| [GR DIGITAL III x STUSSY](https://www.ricoh-imaging.co.jp/english/r_dc/press/release/nr_grd3_stussy.html) | Separate identity/version unresolved | [GR DIGITAL III](ricoh-gr-editions-and-variants.md) |
| [GR DIGITAL IV White Edition](https://www.ricoh-imaging.co.jp/english/products/gr-digital4/whiteEdition.html) | Separate identity/version unresolved | [GR DIGITAL IV](ricoh-gr-editions-and-variants.md) |
| [GR Limited Edition (2013)](https://news.ricoh-imaging.co.jp/rim_info/2013/20131022_018807.html) | Separate identity/version unresolved | [GR (2013 APS-C)](ricoh-gr-editions-and-variants.md) |
| [GR II Silver Edition](https://www.ricoh-imaging.co.jp/english/products/gr-2/silver/) | Separate identity/version unresolved | [GR II](ricoh-gr-editions-and-variants.md) |
| [GR III Street Edition](https://www.ricoh-imaging.co.jp/english/products/gr-3/special/) | Separate identity/version unresolved | [GR III](ricoh-gr-editions-and-variants.md) |
| [GR III Diary Edition](https://www.ricoh-imaging.co.jp/english/products/gr-3/special/) | Separate identity/version unresolved | [GR III](ricoh-gr-editions-and-variants.md) |
| [GR IIIx Urban Edition](https://www.ricoh-imaging.co.jp/english/products/gr-3/special/) | Separate identity/version unresolved | [GR IIIx](ricoh-gr-editions-and-variants.md) |
| [GR IV 30th Anniversary Edition](https://news.ricoh-imaging.co.jp/rim_info2/2026/20260916_042580.html) | Separate identity/version unresolved | [GR IV](ricoh-gr-editions-and-variants.md) |
| [GR IVx (announced)](https://news.ricoh-imaging.co.jp/rim_info2/2026/20260827_042443.html) | Separate identity/version unresolved | [GR IVx](ricoh-gr-editions-and-variants.md) |

## Primary project routes

- [GRKit runtime](ricoh-grkit-runtime.md): current cross-generation matrix, persistent-setting boundary and Monochrome limitations.
- [GR II](model-ricoh-gr-ii.md): FRAME and separate static startup research.
- [GR III](model-ricoh-gr-iii.md) and [GR IIIx](model-ricoh-gr-iiix.md): multiple exact-image tools and variant-specific evidence.
- [GR IV](model-ricoh-gr-iv.md): exact older patch evidence, with broader current projects in the supplementary notes below.
- [Variants/editions](ricoh-gr-editions-and-variants.md): hardware changes, identity/resource caveats, and GR IVx announcement.
- [Project inventory](ricoh-gr-project-inventory.md): inspected primary sources versus uninspected discovery leads.

## Source audit and conflicts

Use [official current downloads](https://www.ricoh-imaging.co.jp/english/support/download_digital.html) and [legacy downloads](https://www.ricoh-imaging.co.jp/english/r_dc/download/index.html) to identify the body and official image. Most captured modified-image tools still target III 2.10 / IIIx 1.60 / IV 1.11 even though the vendor index has newer versions. Do not silently update their compatibility claims.

The indexed GRKit page and directly retrieved README differ on camera-test status; the runtime reference identifies which capture it uses. One patcher excludes HDF while other projects explicitly include it. Treat that as project-specific eligibility, not a global firmware-family rule. The community Bluetooth document lists GR II broadly, while a separate implementation excludes it; no generic BLE support is inferred.

The [machine-readable ledger](../assets/family-coverage.json) records every identity and its source. No primary third-party modification was qualified for GR DIGITAL I–IV or GR 2013 in the bounded searches. Those explicit research gaps are part of coverage, not unsupported claims that modification is impossible.
