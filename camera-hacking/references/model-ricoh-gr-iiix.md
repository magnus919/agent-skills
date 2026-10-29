# Ricoh GR IIIx

Checked 2026-10-29. [Official firmware page](https://www.ricoh-imaging.co.jp/english/support/digital/gr3x_s.html) supplies the 1.70 route; project targets below mostly name 1.60. Standard, Urban and HDF identities are separately tracked.

## Primary projects

- [gr3x-fw-play](https://github.com/tinyblckc0000al/gr3x-fw-play) targets plain IIIx 1.60. B2.4.2 is reported to have camera feedback for loading, startup/shutdown and RAW/JPEG capture. Its README does not extend those tests to HDF/Urban or other generations.
- [GR-DLC](https://github.com/Mrjie7205/GR-DLC) instead has a specific IIIx HDF 1.60 adaptation. Camera feedback covers selected slots, framing, RAW and shutdown-image functions; it does not cover every catalog look or combination. Its GR IV nine-slot adaptation is documented separately as awaiting camera validation.
- [Look Editor](https://github.com/judgem00/gr3-look-editor) and [GR3-LUTSmith](https://github.com/lemonadesaltbagel/GR3-LUTSmith) provide different image-processing projects and evidence levels; neither inherits the other's tests.
- [GRKit](https://github.com/ahonn/grkit) offers a different card/RAM path. Factory-interface shutdown-image research has separate Urban/HDF evidence and restoration limitations.

## Next evidence

Resolve the exact IIIx variant, old/current firmware and selected project. A downloader offering 1.70 does not qualify a 1.60 patch or prove a downgrade is possible. Do not infer IIIx support from the same tool's III result. No body tested here.
