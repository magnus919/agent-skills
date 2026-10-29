# Ricoh GR III

Checked 2026-10-29. [Official firmware page](https://www.ricoh-imaging.co.jp/english/support/digital/gr3_s.html) lists 2.20 and explicitly includes Street, Diary and HDF models. Sharing an official update does not establish identical third-party patch support.

## Primary research routes

- [GRKit](https://github.com/ahonn/grkit): card/RAM extension, with persistent SD-script enablement. Use the separate runtime reference for its current grouped body/version reports.
- [Look Editor](https://github.com/judgem00/gr3-look-editor): exact GR III 2.10 and IIIx 1.60 input identities; replaces a look and includes model-specific video work. Reports one body of each model for modified-image testing. Its GR III video result must not become a IIIx video claim.
- [GR3-LUTSmith](https://github.com/lemonadesaltbagel/GR3-LUTSmith): names GR III-family 2.10 and IIIx-family 1.60. Current version 1.0.0 is explicitly offline-checked and not camera-tested; another modified-image experiment does not qualify this output. Native matrix/curve fitting is not arbitrary on-camera 3D LUT execution.
- [m10v](https://github.com/zhaoo/m10v): broader workbench whose README says modified images still need camera validation.
- [gr3x-fw-hack](https://github.com/hhornbacher/gr3x-fw-hack): firmware exploration/emulation and foundational research, not a universal ready-to-install release.

## Boundary

Do not assume a 2.10-targeted patch accepts 2.20, or that HDF is supported by every plain-body patch. Keep standard, Street, Diary and HDF records separate. HDF has physical filtering differences; it is not just a new look. No body tested here.
