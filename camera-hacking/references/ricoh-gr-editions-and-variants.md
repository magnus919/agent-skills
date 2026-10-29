# Ricoh GR variants, editions and announced models

Checked 2026-10-29. Every identity below appears separately in the family ledger. A shared vendor update is one compatibility fact, not a general endorsement of third-party packages.

## Hardware/processing variants

- GR III HDF, GR IIIx HDF and GR IV HDF have explicit project-specific support records. A base-body patch can still exclude HDF. GR-DLC's HDF IIIx feedback and gr3x-fw-play's plain IIIx feedback must remain separate.
- GR IV Monochrome is a dedicated target. GR4-MonoUnlock is for the standard colour GR IV; it does not establish compatibility with the Monochrome camera. GRKit lists Monochrome support with Film Look absent.

## Editions with primary identity sources

| Edition | Source / base route | Modification boundary |
|---|---|---|
| GR DIGITAL 1st Anniversary | [Vendor legacy page](https://www.ricoh-imaging.co.jp/japan/dc/gr/digital/) | Legacy GR DIGITAL; no qualified mod retained |
| GR DIGITAL III x STUSSY | [Vendor release](https://www.ricoh-imaging.co.jp/english/r_dc/press/release/nr_grd3_stussy.html) | Base performance retained; resource/patch identity unqualified |
| GR DIGITAL IV White | [Vendor page](https://www.ricoh-imaging.co.jp/english/products/gr-digital4/whiteEdition.html) | Base functionality retained; no qualified mod retained |
| GR Limited Edition (2013) | [Vendor release](https://news.ricoh-imaging.co.jp/rim_info/2013/20131022_018807.html) | Route to APS-C GR 2013, not GR DIGITAL or GR II |
| GR II Silver | [Vendor page](https://www.ricoh-imaging.co.jp/english/products/gr-2/silver/) | Separate shutdown artwork; save per-body original |
| GR III Street / Diary | [Official variant index](https://www.ricoh-imaging.co.jp/english/products/gr-3/special/) | Named by some firmware tools; not tested by every runtime |
| GR IIIx Urban | [Official variant index](https://www.ricoh-imaging.co.jp/english/products/gr-3/special/) | Separate shutdown-image report; restoration was not established for every related workflow |
| GR IV 30th Anniversary | [Vendor release](https://news.ricoh-imaging.co.jp/rim_info2/2026/20260916_042580.html) | Separate artwork/resources; verify exact installed image before any older 1.11 patch |

## GR IVx is not a released modification target

The [2026-08-27 vendor announcement](https://news.ricoh-imaging.co.jp/rim_info2/2026/20260827_042443.html) describes development with planned winter-2026-or-later release. This investigation found no released firmware or qualified modification for it. Do not alias it to GR IV or IIIx.

## Naming exclusions

GR1/GR1s/GR1v, GR10/GR21 are film-camera lines, not targets for this digital-firmware work. GXR GR LENS modules have a separate body/module update architecture; GR branding on a lens is not inclusion in the fixed-lens GR firmware family. Other regional/collaboration packages must retain their exact product IDs and original resources even when routed to a base model.
