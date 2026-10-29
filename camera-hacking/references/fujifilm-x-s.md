# Fujifilm X-S10 and X-S20

Model-complete discovery routing, checked 2026-10-29. No camera was connected, patched or tested in this investigation.

## Model ledger

Official version = value displayed by the captured vendor index, not an update recommendation. FujiMod flags refer to the pinned source tree below. Firmware records and controls are research declarations, not working releases.

| Model / primary official route | Official version observed | FujiMod firmware records | Controls only/present | Other body-specific evidence |
|---|---|---|---|---|
| [X-S10](https://www.fujifilm-x.com/global/support/download/firmware/cameras/x-s10/) | 3.11 | 3.11 | Controls present | Furble body report; fujicli declaration |
| [X-S20](https://www.fujifilm-x.com/global/support/download/firmware/cameras/x-s20/) | 3.30 | None under exact model ID | Controls present | Furble body report; fujicli declaration |

## Evidence routes and boundaries

X-S1 is an older fixed-lens bridge camera, routed separately. Filmcase has X-S10 hardware reports; X-S20 is present in fujicli's current model definitions but declared features are not an independent hardware test.

- [FujiMod catalog at inspected revision](https://github.com/justjake/fujimod/tree/925640f1ff2327eeba118437af35790c0a1656eb/catalog/): body, controls and firmware identity records are separate. A controls-only entry can have no executable hardware model, and an emulator can have no patch release. XQ1/XQ2 use a shared `xq` catalog ID; no exact-ID absence here is a claim that their research is absent.
- [Current fujicli source declaration](https://github.com/karaolidis/fujicli/blob/6366cff82449d19dab9e6234c3dc6ec5922e6ccb/fml/camera.cue): a declared model/feature is not confirmed operation. Its [README](https://github.com/karaolidis/fujicli/blob/6366cff82449d19dab9e6234c3dc6ec5922e6ccb/README.md) says only X-T5 is extensively tested. The old indexed support page is gone; do not substitute its historical matrix for current source.
- [Furble](https://github.com/gkoh/furble): body reports concern external Bluetooth control. They do not demonstrate firmware patching, every feature or every firmware revision.
- [Filmcase](https://github.com/gosku/Filmcase): author-tested X-S10, with other bodies proposed through protocol similarity. Its compatibility prose includes questionable generation groupings; use exact body/firmware observations, not the generation shorthand.

## Next evidence before operation

Resolve the requested feature, exact official image hash, actual release capability, device test scope and persistent changes. Consult `software-architecture-analysis` for source/project structure and `binary-analysis` for bounded static planning, preserving its backend limitation. This reference supplies discovery coverage even where a usable modification remains unknown.
