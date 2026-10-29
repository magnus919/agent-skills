# Ricoh GR II

Checked 2026-10-29. [Official route](https://www.ricoh-imaging.co.jp/english/support/digital/gr2_s.html); vendor baseline 3.00. Silver Edition needs its own artwork/settings preservation record.

## Primary projects

- [FRAME-GR2](https://github.com/Lyle-xub/FRAME-GR2) is a real firmware/companion-app lead, not just a proposed boot-screen patch. Its retrieved README identifies WNX-L2 / app 1.0.6 and requires official 3.00 first. It advertises custom looks, grain, framing and personalization. These are developer claims; this investigation did not inspect a reproducible source-to-binary map or a comprehensive recovery matrix. Historical WN3/WN9 summaries must not be presented as the current release.
- [Boot-screen research](https://github.com/lc2425150/ricoh-gr2-boot-screen-mod) is separate static work. Its modified-image path has an unresolved update checksum. Its startup-script proposal writes a file inside the camera but also claims removing the card rolls back; this is not demonstrated restoration and must remain unresolved.
- [m10v](https://github.com/zhaoo/m10v) names GR II 3.00 for inspection/roundtrip only; it does not enable modified export for this target.

## Control versus modification

The community Bluetooth document broadly lists GR II among supported identities. This alone does not establish native BLE hardware or every listed characteristic on GR II. The separate Furble implementation explicitly excludes GR II/III. Verify the exact transport with vendor documentation and body evidence.

No package was installed or built, and no restoration was tested here.
