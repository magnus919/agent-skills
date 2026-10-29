# Ricoh GRKit: cross-generation card runtime

Checked 2026-10-29 against the directly retrieved [primary README](https://github.com/ahonn/grkit), whose digest is in the family source-capture record. The search-indexed README was older and used weaker statuses; retain the source discrepancy rather than merging the tables.

## Reported compatibility

The current README groups bodies as follows:

| Group | Listed under “Tested on a camera” | Listed only under “Supported” |
|---|---|---|
| GR III / III HDF | 2.10, 2.20 | — |
| GR IIIx / IIIx HDF | 1.60, 1.70 | — |
| GR IV / IV HDF | 1.11, 1.20 | — |
| GR IV Monochrome | 1.00 | 1.10 |

These are grouped maintainer reports, not independently verified testing of every body/feature combination. Other models/firmware are excluded by the project. The dedicated Monochrome target has no Film Look.

## Mechanism

Code loads from the card and changes camera RAM; installation enables a persistent SD-script setting. Removing the runtime/card and disabling that setting are distinct operations. A startup hang remains possible, so “no firmware flashing” does not establish zero persistent change or guaranteed recovery.

## Next evidence

Use exact target hashes and the release-specific recovery guide, then evaluate the requested module/output/lifecycle on the exact body. Never transplant this runtime to GR II, GR (2013), legacy GR DIGITAL or announced GR IVx without a new implementation and evidence.
