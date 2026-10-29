# Fujifilm X-E rangefinders

Model-complete discovery routing, checked 2026-10-29. No camera was connected, patched or tested in this investigation.

## Model ledger

Official version = value displayed by the captured vendor index, not an update recommendation. FujiMod flags refer to the pinned source tree below. Firmware records and controls are research declarations, not working releases.

| Model / primary official route | Official version observed | FujiMod firmware records | Controls only/present | Other body-specific evidence |
|---|---|---|---|---|
| [X-E1](https://www.fujifilm-x.com/global/support/download/firmware/cameras/x-e1/) | 2.71 | None under exact model ID | Controls present | fujicli declaration |
| [X-E2](https://www.fujifilm-x.com/global/support/download/firmware/cameras/x-e2/) | 4.11 | 4.11 | Controls present | fujicli declaration |
| [X-E2S](https://www.fujifilm-x.com/global/support/download/firmware/cameras/x-e2s/) | 1.11 | 1.11 | Controls present | No body-specific operational result retained |
| [X-E3](https://www.fujifilm-x.com/global/support/download/firmware/cameras/x-e3/) | 1.32 | None under exact model ID | Controls present | fujicli declaration |
| [X-E4](https://www.fujifilm-x.com/global/support/download/firmware/cameras/x-e4/) | 2.01 | 2.01 | Controls present | Furble body report; fujicli declaration |
| [X-E5](https://www.fujifilm-x.com/global/support/download/firmware/cameras/x-e5/) | 1.12 | None under exact model ID | Controls present | Furble body report |

## Evidence routes and boundaries

Keep E2 and E2S separate. Furble has reported E4/E5 Bluetooth operation; it does not follow that older E bodies have Bluetooth or that firmware patches transfer between generations.

- [FujiMod catalog at inspected revision](https://github.com/justjake/fujimod/tree/925640f1ff2327eeba118437af35790c0a1656eb/catalog/): body, controls and firmware identity records are separate. A controls-only entry can have no executable hardware model, and an emulator can have no patch release. XQ1/XQ2 use a shared `xq` catalog ID; no exact-ID absence here is a claim that their research is absent.
- [Current fujicli source declaration](https://github.com/karaolidis/fujicli/blob/6366cff82449d19dab9e6234c3dc6ec5922e6ccb/fml/camera.cue): a declared model/feature is not confirmed operation. Its [README](https://github.com/karaolidis/fujicli/blob/6366cff82449d19dab9e6234c3dc6ec5922e6ccb/README.md) says only X-T5 is extensively tested. The old indexed support page is gone; do not substitute its historical matrix for current source.
- [Furble](https://github.com/gkoh/furble): body reports concern external Bluetooth control. They do not demonstrate firmware patching, every feature or every firmware revision.

## Next evidence before operation

Resolve the requested feature, exact official image hash, actual release capability, device test scope and persistent changes. Consult `software-architecture-analysis` for source/project structure and `binary-analysis` for bounded static planning, preserving its backend limitation. This reference supplies discovery coverage even where a usable modification remains unknown.
