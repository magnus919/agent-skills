# Ricoh GR IV

Accessed 2026-10-29. Primary source: [Ricoh GR IV project documentation](https://github.com/lemonadesaltbagel/GR4-MonoUnlock). Findings below are source-attributed; no hardware reproduction was performed in this investigation.

## Exact target and mechanism

GR4-MonoUnlock documents the standard colour GR IV on stock **1.11**, with `fwdc248b.bin` supplied by the user. It adds six monochrome looks through a locally generated modified image. Three looks are listed for movie mode; the HDR monochrome look is experimental. The stated target excludes other variants and newer firmware.

## Evidence and unresolved recovery

The README claims return to official firmware is possible. This investigation did not inspect a successful restore trace or test a body. Record stock and generated hashes, exact image identity and restore conditions before a future build/install assessment. “Monochrome look” does not mean the colour camera has become the dedicated monochrome sensor model.

The [separate research repository](https://github.com/radium-wang/ricoh-gr4-firmware-analysis-and-feature-expansion) records shutdown-image changes through factory interfaces, with some model-specific restoration untested. Keep these operations separate from the patcher.

The video's metric-to-imperial conversion is a presenter report at approximately 01:04–03:40. Its precise patch bytes, affected language resources and recovery trace are unresolved. Captions alone are insufficient to reproduce it.

## Expanded discovery routes

The [full GR-family map](family-ricoh-gr-series.md), [GRKit runtime](ricoh-grkit-runtime.md), [variant ledger](ricoh-gr-editions-and-variants.md) and [current project inventory](ricoh-gr-project-inventory.md) add current GR Mod/DLC/card-runtime leads. The older 1.11 MonoUnlock analysis above remains specific to that patch and must not be read as the complete current GR IV ecosystem.
