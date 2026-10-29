# Fujifilm Legacy fixed-lens and bridge X cameras

Model-complete discovery routing, checked 2026-10-29. No camera was connected, patched or tested in this investigation.

## Model ledger

Official version = value displayed by the captured vendor index, not an update recommendation. FujiMod flags refer to the pinned source tree below. Firmware records and controls are research declarations, not working releases.

| Model / primary official route | Official version observed | FujiMod firmware records | Controls only/present | Other body-specific evidence |
|---|---|---|---|---|
| [X10](https://www.fujifilm-x.com/global/support/download/firmware/cameras/x10/) | 2.01 | None under exact model ID | Controls present | No body-specific operational result retained |
| [X20](https://www.fujifilm-x.com/global/support/download/firmware/cameras/x20/) | 1.03 | 1.03 | Controls present | No body-specific operational result retained |
| [X30](https://www.fujifilm-x.com/global/support/download/firmware/cameras/x30/) | 1.03 | 1.03 | Controls present | No body-specific operational result retained |
| [X70](https://www.fujifilm-x.com/global/support/download/firmware/cameras/x70/) | 1.10 | 1.10 | Controls present | fujicli declaration; FujiMod X70 release |
| [XF1](https://www.fujifilm-x.com/global/support/download/firmware/cameras/xf1/) | 1.01 | None under exact model ID | Controls present | FujiHack 1.01 debugger |
| [XF10](https://www.fujifilm-x.com/global/support/download/firmware/cameras/xf10/) | 1.12 | None under exact model ID | No exact control record found | No body-specific operational result retained |
| [XQ1](https://www.fujifilm-x.com/global/support/download/firmware/cameras/xq1/) | 1.21 | None under exact model ID | No exact control record found | No body-specific operational result retained |
| [XQ2](https://www.fujifilm-x.com/global/support/download/firmware/cameras/xq2/) | 1.01 | None under exact model ID | No exact control record found | No body-specific operational result retained |
| [X-S1](https://www.fujifilm-x.com/global/support/download/firmware/cameras/x-s1/) | 1.02 | None under exact model ID | Controls present | No body-specific operational result retained |

## Evidence routes and boundaries

Do not collapse XF1 and XF10, XQ1 and XQ2, or X-S1 and X-S10. FujiMod has a concrete X70 release lead; FujiHack has an XF1 debugger lead. Their support cannot be extended to every fixed-lens body.

- [FujiMod catalog at inspected revision](https://github.com/justjake/fujimod/tree/925640f1ff2327eeba118437af35790c0a1656eb/catalog/): body, controls and firmware identity records are separate. A controls-only entry can have no executable hardware model, and an emulator can have no patch release. XQ1/XQ2 use a shared `xq` catalog ID; no exact-ID absence here is a claim that their research is absent.
- [Current fujicli source declaration](https://github.com/karaolidis/fujicli/blob/6366cff82449d19dab9e6234c3dc6ec5922e6ccb/fml/camera.cue): a declared model/feature is not confirmed operation. Its [README](https://github.com/karaolidis/fujicli/blob/6366cff82449d19dab9e6234c3dc6ec5922e6ccb/README.md) says only X-T5 is extensively tested. The old indexed support page is gone; do not substitute its historical matrix for current source.
- [Furble](https://github.com/gkoh/furble): body reports concern external Bluetooth control. They do not demonstrate firmware patching, every feature or every firmware revision.
- [FujiMod public release page](https://fujimod.com/): starts with X70 and SD dual boot; features include focus/crop/control/recipe changes. The author explicitly says not every feature has been camera-tested. This is stronger than a catalog entry but not a whole-family release.

## Next evidence before operation

Resolve the requested feature, exact official image hash, actual release capability, device test scope and persistent changes. Consult `software-architecture-analysis` for source/project structure and `binary-analysis` for bounded static planning, preserving its backend limitation. This reference supplies discovery coverage even where a usable modification remains unknown.
