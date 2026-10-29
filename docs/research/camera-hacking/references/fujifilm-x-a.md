# Fujifilm X-A entry line

Model-complete discovery routing, checked 2026-10-29. No camera was connected, patched or tested in this investigation.

## Model ledger

Official version = value displayed by the captured vendor index, not an update recommendation. FujiMod flags refer to the pinned source tree below. Firmware records and controls are research declarations, not working releases.

| Model / primary official route | Official version observed | FujiMod firmware records | Controls only/present | Other body-specific evidence |
|---|---|---|---|---|
| [X-A1](https://www.fujifilm-x.com/global/support/download/firmware/cameras/x-a1/) | 1.50 | 1.50 | Controls present | No body-specific operational result retained |
| [X-A2](https://www.fujifilm-x.com/global/support/download/firmware/cameras/x-a2/) | 1.30 | 1.30 | Controls present | FujiHack 1.30 debugger |
| [X-A3](https://www.fujifilm-x.com/global/support/download/firmware/cameras/x-a3/) | 2.22 | None under exact model ID | Controls present | No body-specific operational result retained |
| [X-A5](https://www.fujifilm-x.com/global/support/download/firmware/cameras/x-a5/) | 2.03 | None under exact model ID | Controls present | No body-specific operational result retained |
| [X-A7](https://www.fujifilm-x.com/global/support/download/firmware/cameras/x-a7/) | 1.33 | None under exact model ID | Controls present | No body-specific operational result retained |
| [X-A10](https://www.fujifilm-x.com/global/support/download/firmware/cameras/x-a10/) | 2.21 | None under exact model ID | Controls present | No body-specific operational result retained |
| [X-A20](https://www.fujifilm-x.com/global/support/download/firmware/cameras/x-a20/) | 1.12 | None under exact model ID | No exact control record found | No body-specific operational result retained |

## Evidence routes and boundaries

FujiHack's actual X-A2 1.30 debugger target is specific. Later A bodies and A10/A20 require independent container/CPU/firmware analysis; the primary RTOS inventory is neither complete nor a support table.

- [FujiMod catalog at inspected revision](https://github.com/justjake/fujimod/tree/925640f1ff2327eeba118437af35790c0a1656eb/catalog/): body, controls and firmware identity records are separate. A controls-only entry can have no executable hardware model, and an emulator can have no patch release. XQ1/XQ2 use a shared `xq` catalog ID; no exact-ID absence here is a claim that their research is absent.
- [Current fujicli source declaration](https://github.com/karaolidis/fujicli/blob/6366cff82449d19dab9e6234c3dc6ec5922e6ccb/fml/camera.cue): a declared model/feature is not confirmed operation. Its [README](https://github.com/karaolidis/fujicli/blob/6366cff82449d19dab9e6234c3dc6ec5922e6ccb/README.md) says only X-T5 is extensively tested. The old indexed support page is gone; do not substitute its historical matrix for current source.
- [Furble](https://github.com/gkoh/furble): body reports concern external Bluetooth control. They do not demonstrate firmware patching, every feature or every firmware revision.

## Next evidence before operation

Resolve the requested feature, exact official image hash, actual release capability, device test scope and persistent changes. Consult `software-architecture-analysis` for source/project structure and `binary-analysis` for bounded static planning, preserving its backend limitation. This reference supplies discovery coverage even where a usable modification remains unknown.
