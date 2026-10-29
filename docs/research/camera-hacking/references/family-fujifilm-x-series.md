# Fujifilm X series: full-family discovery map

Checked 2026-10-29. Coverage is **52 X-series camera identities in the retrieved official firmware index plus X-T1 IR**, for 53 explicit entries. GFX is a separate family. Cosmetic colourways/kits route to their named base body; their firmware identity still requires verification. This roster covers camera identities, not a promise of a working hack on every model.

The first pass only detailed X-A2/XF1. This audit adds the missing interchangeable-lens lines, all X100 generations, older compacts/bridge models, X half and the IR variant.

| Lineage reference | Explicit models |
|---|---|
| [X-Pro rangefinders](fujifilm-x-pro.md) | X-Pro1, X-Pro2, X-Pro3 |
| [X-E rangefinders](fujifilm-x-e.md) | X-E1, X-E2, X-E2S, X-E3, X-E4, X-E5 |
| [X-T main line and IR variant](fujifilm-x-t-main.md) | X-T1, X-T1 IR, X-T2, X-T3, X-T4, X-T5 |
| [X-T compact line](fujifilm-x-t-compact.md) | X-T10, X-T20, X-T30, X-T30 II, X-T30 III, X-T50 |
| [X-T100 and X-T200](fujifilm-x-t-bayer.md) | X-T100, X-T200 |
| [X-H line](fujifilm-x-h.md) | X-H1, X-H2, X-H2S |
| [X-S10 and X-S20](fujifilm-x-s.md) | X-S10, X-S20 |
| [X-A entry line](fujifilm-x-a.md) | X-A1, X-A2, X-A3, X-A5, X-A7, X-A10, X-A20 |
| [X-M line](fujifilm-x-m.md) | X-M1, X-M5 |
| [X100 fixed-lens line](fujifilm-x100.md) | X100, X100S, X100T, X100F, X100V, X100VI |
| [Legacy fixed-lens and bridge X cameras](fujifilm-fixed-legacy.md) | X10, X20, X30, X70, XF1, XF10, XQ1, XQ2, X-S1 |
| [X half / X-HF1](fujifilm-x-half.md) | X half |

## Source and capability distinctions

- [Official firmware index](https://www.fujifilm-x.com/global/support/download/firmware/cameras/) is the roster baseline, supplemented by the [official X-T1 IR page](https://www.fujifilm.com/us/en/consumer/digitalcameras/ir-camera). It is not a third-party compatibility list.
- [FujiHack RTOS inventory](https://wiki.fujihack.org/supported/) explicitly says it is not a list of cameras on which FujiHack runs. Its actual debugger targets remain much narrower.
- [FujiMod](https://fujimod.com/) supplies a concrete X70 release lead and much broader research/emulation catalogs. Controls, firmware definitions, emulation and released modifications remain separate.
- libfuji, Furble, fujicli and recipe tools provide protocol/setting capabilities with uneven model evidence. A setting write is still a mutation, even without flashing.

Every body has a vendor source, a lineage reference, independently recorded project-declaration flags and an explicit unresolved state in [the machine-readable family ledger](../family-coverage.json). We inspected project-wide catalogs and their test matrices, not an exhaustive internet search for each individual model. Missing operational evidence must stay visible.

## Known conflicting or stale evidence

The old fujicli support document remains search-indexed but returns 404; current source and manual routes take precedence. Filmcase's predicted compatibility is not hardware evidence and its generation shorthand should not be copied as authoritative sensor classification. The X100VI manager's 1.32 target differs from the captured official index's 1.31: resolve the exact direct vendor page/image before any operation. Do not use either conflict to invent a downgrade path.
