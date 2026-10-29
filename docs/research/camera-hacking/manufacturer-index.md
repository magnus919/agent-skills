# Manufacturer discovery index

Start with the [manufacturer completeness audit](manufacturer-audit-findings.md) for model-source inventories and the unresolved denominator for each brand. These project references do not claim every model can be modified.

Accessed 2026-10-29. Public scope: digital photographic cameras across brands, including legacy, action, light-field, medium-format and cinema devices. Every row links to a brand reference. “Documented” means the source was inspected, not that this investigation tested a camera.

| Manufacturer | Current evidence |
|---|---|
| [Ricoh](references/manufacturer-ricoh.md) | Firmware research and patcher documented |
| [Fujifilm](references/manufacturer-fujifilm.md) | Research code and remote-control library documented |
| [Canon](references/manufacturer-canon.md) | Established add-ons and newer creative firmware documented |
| [Olympus / OM System](references/manufacturer-olympus-om-system.md) | Multiple model-specific firmware projects documented |
| [Panasonic / LUMIX](references/manufacturer-panasonic.md) | Historical patching and modern control paths documented |
| [Leica](references/manufacturer-leica.md) | Firmware analysis and debug-interface tooling documented |
| [Hasselblad](references/manufacturer-hasselblad.md) | Separate first- and second-generation extensions documented |
| [Nikon](references/manufacturer-nikon.md) | Historical DSLR tools and Z30 research documented |
| [Sony](references/manufacturer-sony.md) | PMCA-era apps/settings and research modes documented |
| [Sigma](references/manufacturer-sigma.md) | fp firmware research and card tooling documented |
| [Pentax](references/manufacturer-pentax.md) | USB protocol/control and historical firmware leads |
| [Samsung](references/manufacturer-samsung.md) | NX-generation Linux modification projects documented |
| [Kodak](references/manufacturer-kodak.md) | Distinct legacy digital-back and Charmera projects documented |
| [GoPro](references/manufacturer-gopro.md) | Vendor experimental firmware and developer interfaces documented |
| [DJI](references/manufacturer-dji.md) | External monitor/control application documented |
| [Insta360](references/manufacturer-insta360.md) | Official SDKs and multiple independent research targets documented |
| [Xiaomi / YI](references/manufacturer-xiaomi-yi.md) | Model-specific action-camera scripting documented |
| [SJCAM](references/manufacturer-sjcam.md) | Board-specific firmware and protocol research documented |
| [AKASO](references/manufacturer-akaso.md) | Firmware unpack/repack tools and recovery caveat documented |
| [Phase One / Mamiya](references/manufacturer-phase-one-mamiya.md) | Official control SDK and legacy back-protocol research |
| [Blackmagic Design](references/manufacturer-blackmagic-design.md) | Official camera-control protocols documented |
| [Z CAM](references/manufacturer-z-cam.md) | Official controls and independent firmware research documented |
| [ARRI](references/manufacturer-arri.md) | Vendor integration route documented |
| [RED Digital Cinema](references/manufacturer-red.md) | Official control-protocol evidence |
| [Lytro](references/manufacturer-lytro.md) | Original light-field camera research documented |
| [Casio](references/manufacturer-casio.md) | Searched; primary modification evidence unresolved |
| [Konica / Minolta](references/manufacturer-konica-minolta.md) | Searched; primary modification evidence unresolved |
| [ZEISS](references/manufacturer-zeiss.md) | Searched; primary modification evidence unresolved |
| [Polaroid](references/manufacturer-polaroid.md) | Searched; primary modification evidence unresolved |

| [Epson](references/manufacturer-epson.md) | Baseline/lead only; modification evidence unresolved |
| [JVC](references/manufacturer-jvc.md) | Baseline/lead only; modification evidence unresolved |
| [Kinefinity](references/manufacturer-kinefinity.md) | Baseline/lead only; modification evidence unresolved |
| [Digital Bolex](references/manufacturer-digital-bolex.md) | Baseline/lead only; modification evidence unresolved |
| [AgfaPhoto](references/manufacturer-agfaphoto.md) | Baseline/lead only; modification evidence unresolved |
| [BenQ](references/manufacturer-benq.md) | Baseline/lead only; modification evidence unresolved |
| [GE / General Imaging](references/manufacturer-general-imaging.md) | Baseline/lead only; modification evidence unresolved |
| [Contax / Kyocera](references/manufacturer-contax-kyocera.md) | Baseline/lead only; modification evidence unresolved |
| [HP](references/manufacturer-hp.md) | Baseline/lead only; modification evidence unresolved |
| [Toshiba](references/manufacturer-toshiba.md) | Baseline/lead only; modification evidence unresolved |
| [Sanyo](references/manufacturer-sanyo.md) | Baseline/lead only; modification evidence unresolved |
| [Rollei](references/manufacturer-rollei.md) | Baseline/lead only; modification evidence unresolved |
| [Vivitar](references/manufacturer-vivitar.md) | Baseline/lead only; modification evidence unresolved |
| [Yashica](references/manufacturer-yashica.md) | Baseline/lead only; modification evidence unresolved |

## Coverage still to extend

This is an open index, not a claim to cover every manufacturer. The 43 brand/family records include individually researched projects, official interface baselines, and explicitly weaker grouped legacy-brand searches. Many models remain unexamined. Rebranded cameras require OEM/SoC identification as well as the retail brand. Broaden with new manufacturer/model records whenever a primary source warrants it; do not use this pass as a closed support roster.

Smartphone makers, webcam vendors beyond the retained Insta360 lead, surveillance brands, industrial/machine-vision vendors, Raspberry Pi and ESP32 modules need explicit category expansion. A broad public skill should admit these through the same model/evidence contract if that scope is chosen.

## Cross-brand baseline

[gPhoto supported cameras](https://gphoto.sourceforge.io/proj/libgphoto2/support.php) defines general support around transfer; use its separate [remote-control overview](https://gphoto.sourceforge.io/doc/remote/) for capture/control capabilities. These are alternatives to firmware changes, not universal compatibility guarantees.
