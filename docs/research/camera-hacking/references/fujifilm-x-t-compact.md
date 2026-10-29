# Fujifilm X-T compact line

Model-complete discovery routing, checked 2026-10-29. No camera was connected, patched or tested in this investigation.

## Model ledger

Official version = value displayed by the captured vendor index, not an update recommendation. FujiMod flags refer to the pinned source tree below. Firmware records and controls are research declarations, not working releases.

| Model / primary official route | Official version observed | FujiMod firmware records | Controls only/present | Other body-specific evidence |
|---|---|---|---|---|
| [X-T10](https://www.fujifilm-x.com/global/support/download/firmware/cameras/x-t10/) | 1.31 | 1.31 | Controls present | fujicli declaration |
| [X-T20](https://www.fujifilm-x.com/global/support/download/firmware/cameras/x-t20/) | 2.11 | None under exact model ID | Controls present | fujicli declaration |
| [X-T30](https://www.fujifilm-x.com/global/support/download/firmware/cameras/x-t30/) | 2.01 | 2.01 | Controls present | Furble body report |
| [X-T30 II](https://www.fujifilm-x.com/global/support/download/firmware/cameras/x-t30-ii/) | 2.04 | 2.04 | Controls present | No body-specific operational result retained |
| [X-T30 III](https://www.fujifilm-x.com/global/support/download/firmware/cameras/x-t30-iii/) | 1.10 | None under exact model ID | Controls present | No body-specific operational result retained |
| [X-T50](https://www.fujifilm-x.com/global/support/download/firmware/cameras/x-t50/) | 1.32 | None under exact model ID | Controls present | No body-specific operational result retained |

## Evidence routes and boundaries

T30, T30 II and T30 III remain distinct rows. The latest body names must not be silently covered by an older T30 patch or Bluetooth test. Recognition and a physical-control declaration are weaker than a supported release.

- [FujiMod catalog at inspected revision](https://github.com/justjake/fujimod/tree/925640f1ff2327eeba118437af35790c0a1656eb/catalog/): body, controls and firmware identity records are separate. A controls-only entry can have no executable hardware model, and an emulator can have no patch release. XQ1/XQ2 use a shared `xq` catalog ID; no exact-ID absence here is a claim that their research is absent.
- [Current fujicli source declaration](https://github.com/karaolidis/fujicli/blob/6366cff82449d19dab9e6234c3dc6ec5922e6ccb/fml/camera.cue): a declared model/feature is not confirmed operation. Its [README](https://github.com/karaolidis/fujicli/blob/6366cff82449d19dab9e6234c3dc6ec5922e6ccb/README.md) says only X-T5 is extensively tested. The old indexed support page is gone; do not substitute its historical matrix for current source.
- [Furble](https://github.com/gkoh/furble): body reports concern external Bluetooth control. They do not demonstrate firmware patching, every feature or every firmware revision.

## Next evidence before operation

Resolve the requested feature, exact official image hash, actual release capability, device test scope and persistent changes. Consult `software-architecture-analysis` for source/project structure and `binary-analysis` for bounded static planning, preserving its backend limitation. This reference supplies discovery coverage even where a usable modification remains unknown.
