# Fujifilm X100 fixed-lens line

Model-complete discovery routing, checked 2026-10-29. No camera was connected, patched or tested in this investigation.

## Model ledger

Official version = value displayed by the captured vendor index, not an update recommendation. FujiMod flags refer to the pinned source tree below. Firmware records and controls are research declarations, not working releases.

| Model / primary official route | Official version observed | FujiMod firmware records | Controls only/present | Other body-specific evidence |
|---|---|---|---|---|
| [X100](https://www.fujifilm-x.com/global/support/download/firmware/cameras/x100/) | 2.11 | None under exact model ID | Controls present | No body-specific operational result retained |
| [X100S](https://www.fujifilm-x.com/global/support/download/firmware/cameras/x100s/) | 1.21 | 1.21 | Controls present | No body-specific operational result retained |
| [X100T](https://www.fujifilm-x.com/global/support/download/firmware/cameras/x100t/) | 1.11 | 1.11 | Controls present | No body-specific operational result retained |
| [X100F](https://www.fujifilm-x.com/global/support/download/firmware/cameras/x100f/) | 2.12 | None under exact model ID | Controls present | fujicli declaration |
| [X100V](https://www.fujifilm-x.com/global/support/download/firmware/cameras/x100v/) | 3.01 | 3.01 | Controls present | Furble body report; fujicli declaration |
| [X100VI](https://www.fujifilm-x.com/global/support/download/firmware/cameras/x100vi/) | 1.31 | 1.31 | Controls present | fujicli declaration; See 1.32 slot-manager scope below |

## Evidence routes and boundaries

Keep all six generations separate, including the original FinePix-branded X100 alias. The X100VI custom-slot tool has a narrow 1.32 allowlist; this differs from the 1.31 displayed by the captured official index and requires direct version validation before use.

- [FujiMod catalog at inspected revision](https://github.com/justjake/fujimod/tree/925640f1ff2327eeba118437af35790c0a1656eb/catalog/): body, controls and firmware identity records are separate. A controls-only entry can have no executable hardware model, and an emulator can have no patch release. XQ1/XQ2 use a shared `xq` catalog ID; no exact-ID absence here is a claim that their research is absent.
- [Current fujicli source declaration](https://github.com/karaolidis/fujicli/blob/6366cff82449d19dab9e6234c3dc6ec5922e6ccb/fml/camera.cue): a declared model/feature is not confirmed operation. Its [README](https://github.com/karaolidis/fujicli/blob/6366cff82449d19dab9e6234c3dc6ec5922e6ccb/README.md) says only X-T5 is extensively tested. The old indexed support page is gone; do not substitute its historical matrix for current source.
- [Furble](https://github.com/gkoh/furble): body reports concern external Bluetooth control. They do not demonstrate firmware patching, every feature or every firmware revision.
- [Omarchy X100VI slot manager](https://github.com/ctl0v0/omarchy-fujifilm-recipes): experimental, one-slot operations; only X100VI 1.32 allowlisted. It explicitly excludes other firmware/bodies and bulk writing. A guarded attempt at rollback is not guaranteed recovery.

## Next evidence before operation

Resolve the requested feature, exact official image hash, actual release capability, device test scope and persistent changes. Consult `software-architecture-analysis` for source/project structure and `binary-analysis` for bounded static planning, preserving its backend limitation. This reference supplies discovery coverage even where a usable modification remains unknown.
