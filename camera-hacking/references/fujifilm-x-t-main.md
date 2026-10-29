# Fujifilm X-T main line and IR variant

Model-complete discovery routing, checked 2026-10-29. No camera was connected, patched or tested in this investigation.

## Model ledger

Official version = value displayed by the captured vendor index, not an update recommendation. FujiMod flags refer to the pinned source tree below. Firmware records and controls are research declarations, not working releases.

| Model / primary official route | Official version observed | FujiMod firmware records | Controls only/present | Other body-specific evidence |
|---|---|---|---|---|
| [X-T1](https://www.fujifilm-x.com/global/support/download/firmware/cameras/x-t1/) | 5.52 | 5.52 | Controls present | fujicli declaration |
| [X-T1 IR](https://www.fujifilm.com/us/en/consumer/digitalcameras/ir-camera) | Not resolved separately | None under exact model ID | No exact control record found | No body-specific operational result retained |
| [X-T2](https://www.fujifilm-x.com/global/support/download/firmware/cameras/x-t2/) | 4.41 | None under exact model ID | Controls present | fujicli declaration |
| [X-T3](https://www.fujifilm-x.com/global/support/download/firmware/cameras/x-t3/) | 5.11 | 5.11 | Controls present | Furble body report; fujicli declaration |
| [X-T4](https://www.fujifilm-x.com/global/support/download/firmware/cameras/x-t4/) | 2.12 | 2.12 | Controls present | Furble body report; fujicli declaration |
| [X-T5](https://www.fujifilm-x.com/global/support/download/firmware/cameras/x-t5/) | 4.31 | None under exact model ID | Controls present | Furble body report; fujicli declaration; See recipe evidence below |

## Evidence routes and boundaries

X-T1 IR has its own official identity; do not assume the ordinary T1 image is safe on it. X-T5 has useful USB tool evidence, while the T3/T4 and other T bodies require their own feature/firmware evidence.

- [FujiMod catalog at inspected revision](https://github.com/justjake/fujimod/tree/925640f1ff2327eeba118437af35790c0a1656eb/catalog/): body, controls and firmware identity records are separate. A controls-only entry can have no executable hardware model, and an emulator can have no patch release. XQ1/XQ2 use a shared `xq` catalog ID; no exact-ID absence here is a claim that their research is absent.
- [Current fujicli source declaration](https://github.com/karaolidis/fujicli/blob/6366cff82449d19dab9e6234c3dc6ec5922e6ccb/fml/camera.cue): a declared model/feature is not confirmed operation. Its [README](https://github.com/karaolidis/fujicli/blob/6366cff82449d19dab9e6234c3dc6ec5922e6ccb/README.md) says only X-T5 is extensively tested. The old indexed support page is gone; do not substitute its historical matrix for current source.
- [Furble](https://github.com/gkoh/furble): body reports concern external Bluetooth control. They do not demonstrate firmware patching, every feature or every firmware revision.
- [Community recipe protocol](https://github.com/ILFforever/fujifilm-ptp-recipes): reported slot reads/property/name writes on X-H2 5.20 and X-T5 4.20; the tested X-Pro3 2.00 path fails. Do not convert the two successes into whole-family support.

## Next evidence before operation

Resolve the requested feature, exact official image hash, actual release capability, device test scope and persistent changes. Consult `software-architecture-analysis` for source/project structure and `binary-analysis` for bounded static planning, preserving its backend limitation. This reference supplies discovery coverage even where a usable modification remains unknown.
