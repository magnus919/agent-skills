# Fujifilm X-Pro rangefinders

Model-complete discovery routing, checked 2026-10-29. No camera was connected, patched or tested in this investigation.

## Model ledger

Official version = value displayed by the captured vendor index, not an update recommendation. FujiMod flags refer to the pinned source tree below. Firmware records and controls are research declarations, not working releases.

| Model / primary official route | Official version observed | FujiMod firmware records | Controls only/present | Other body-specific evidence |
|---|---|---|---|---|
| [X-Pro1](https://www.fujifilm-x.com/global/support/download/firmware/cameras/x-pro1/) | 3.82 | None under exact model ID | Controls present | No body-specific operational result retained |
| [X-Pro2](https://www.fujifilm-x.com/global/support/download/firmware/cameras/x-pro2/) | 5.11 | None under exact model ID | Controls present | fujicli declaration |
| [X-Pro3](https://www.fujifilm-x.com/global/support/download/firmware/cameras/x-pro3/) | 2.00 | 2.00 | Controls present | fujicli declaration; See recipe evidence below |

## Evidence routes and boundaries

X-Pro3 2.00 is an explicit failing body in the community recipe protocol report. Do not promote a different project's “likely compatible” statement above that negative result; the failure is specific to the tested protocol path, not every possible operation.

- [FujiMod catalog at inspected revision](https://github.com/justjake/fujimod/tree/925640f1ff2327eeba118437af35790c0a1656eb/catalog/): body, controls and firmware identity records are separate. A controls-only entry can have no executable hardware model, and an emulator can have no patch release. XQ1/XQ2 use a shared `xq` catalog ID; no exact-ID absence here is a claim that their research is absent.
- [Current fujicli source declaration](https://github.com/karaolidis/fujicli/blob/6366cff82449d19dab9e6234c3dc6ec5922e6ccb/fml/camera.cue): a declared model/feature is not confirmed operation. Its [README](https://github.com/karaolidis/fujicli/blob/6366cff82449d19dab9e6234c3dc6ec5922e6ccb/README.md) says only X-T5 is extensively tested. The old indexed support page is gone; do not substitute its historical matrix for current source.
- [Furble](https://github.com/gkoh/furble): body reports concern external Bluetooth control. They do not demonstrate firmware patching, every feature or every firmware revision.
- [Community recipe protocol](https://github.com/ILFforever/fujifilm-ptp-recipes): reported slot reads/property/name writes on X-H2 5.20 and X-T5 4.20; the tested X-Pro3 2.00 path fails. Do not convert the two successes into whole-family support.

## Next evidence before operation

Resolve the requested feature, exact official image hash, actual release capability, device test scope and persistent changes. Consult `software-architecture-analysis` for source/project structure and `binary-analysis` for bounded static planning, preserving its backend limitation. This reference supplies discovery coverage even where a usable modification remains unknown.
