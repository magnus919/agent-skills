# Manufacturer completeness audit

Checked 2026-10-29. This audit assesses all **43 manufacturer/brand-family entries** in the discovery index, retaining the prior Fujifilm X and Ricoh GR audits. It does **not** establish an exhaustive census of every digital camera ever sold or every camera manufacturer. The result is a source-bound inventory with an explicit completeness finding for each brand.

## Method and acceptance boundary

1. Seek a vendor product catalog, museum, download index, manual archive or lifecycle list. Capture URL, retrieval time and digest where a body is retrievable. Extract camera-only names, excluding lenses, printers, monitors, analog cameras, phone-only gimbals and accessory kits.
2. Preserve regional alias bundles and edition labels as written. A model name, a store SKU, a firmware build, a body/back combination and a source row are different units. Counts below are not added together as unique cameras.
3. Cross-check gPhoto for transfer/control implementation and LibRaw for raw-file decoding. These primary implementation lists are incomplete manufacturer rosters. Never infer an unlisted model is unsupported or an entire family can be patched.
4. Route each manufacturer to its retained original project/code/official API. Apply its exact model, firmware, board, transport and feature boundaries. A source tree, parser, emulator, SDK, checksum and camera-qualified feature result are distinct evidence levels.
5. Record inaccessible archives, pagination, omitted no-update models, rebadging and historical/region gaps as findings. **Audit complete** means every indexed manufacturer has an evidence assessment and continuation route; it does not mean every roster gap has been closed. No camera experiments, third-party installers or firmware writes were performed.

Photographic, cinema, action and historical digital-camera discovery is covered. Drone payloads, surveillance, industrial cameras, smartphone cameras and DIY modules remain separate tracks. Some documentary rows expose adjacent products; these are source labels rather than an expansion of operational scope. New manufacturers can be added using the same process; 43 is the existing index denominator, not an assertion that only 43 makers exist.

## Results and routes

“Vendor” is the number of distinct labels extracted from retained vendor sources. It can include family labels, alias bundles, editions, and discontinued products. gPhoto and LibRaw columns count independent source rows. **Every manufacturer still has a completeness limitation**; read the individual finding rather than treating a nonzero count as coverage proof.

| Manufacturer audit | Vendor labels | gPhoto rows | LibRaw rows |
|---|---:|---:|---:|
| [agfaphoto](manufacturer-agfaphoto.md) | 6 | 7 | 1 |
| [akaso](manufacturer-akaso.md) | 5 | 0 | 0 |
| [arri](manufacturer-arri.md) | 9 | 0 | 0 |
| [benq](manufacturer-benq.md) | 0 | 1 | 0 |
| [blackmagic-design](manufacturer-blackmagic-design.md) | 16 | 0 | 8 |
| [canon](manufacturer-canon.md) | 466 | 362 | 171 |
| [casio](manufacturer-casio.md) | 0 | 13 | 53 |
| [contax-kyocera](manufacturer-contax-kyocera.md) | 0 | 0 | 1 |
| [digital-bolex](manufacturer-digital-bolex.md) | 0 | 0 | 2 |
| [dji](manufacturer-dji.md) | 15 | 0 | 18 |
| [epson](manufacturer-epson.md) | 20 | 8 | 3 |
| [fujifilm](manufacturer-fujifilm.md) | 0 | 98 | 88 |
| [general-imaging](manufacturer-general-imaging.md) | 0 | 0 | 0 |
| [gopro](manufacturer-gopro.md) | 14 | 17 | 9 |
| [hasselblad](manufacturer-hasselblad.md) | 11 | 0 | 39 |
| [hp](manufacturer-hp.md) | 0 | 53 | 0 |
| [insta360](manufacturer-insta360.md) | 29 | 0 | 0 |
| [jvc](manufacturer-jvc.md) | 5 | 0 | 0 |
| [kinefinity](manufacturer-kinefinity.md) | 11 | 0 | 3 |
| [kodak](manufacturer-kodak.md) | 44 | 100 | 42 |
| [konica-minolta](manufacturer-konica-minolta.md) | 0 | 14 | 17 |
| [leica](manufacturer-leica.md) | 14 | 8 | 61 |
| [lytro](manufacturer-lytro.md) | 0 | 0 | 0 |
| [nikon](manufacturer-nikon.md) | 192 | 208 | 110 |
| [olympus-om-system](manufacturer-olympus-om-system.md) | 58 | 79 | 79 |
| [panasonic](manufacturer-panasonic.md) | 118 | 22 | 82 |
| [pentax](manufacturer-pentax.md) | 110 | 27 | 44 |
| [phase-one-mamiya](manufacturer-phase-one-mamiya.md) | 69 | 0 | 70 |
| [polaroid](manufacturer-polaroid.md) | 0 | 6 | 1 |
| [red](manufacturer-red.md) | 8 | 0 | 0 |
| [ricoh](manufacturer-ricoh.md) | 10 | 38 | 16 |
| [rollei](manufacturer-rollei.md) | 0 | 2 | 1 |
| [samsung](manufacturer-samsung.md) | 0 | 6 | 44 |
| [sanyo](manufacturer-sanyo.md) | 0 | 8 | 0 |
| [sigma](manufacturer-sigma.md) | 22 | 2 | 23 |
| [sjcam](manufacturer-sjcam.md) | 27 | 0 | 0 |
| [sony](manufacturer-sony.md) | 0 | 158 | 115 |
| [toshiba](manufacturer-toshiba.md) | 0 | 5 | 0 |
| [vivitar](manufacturer-vivitar.md) | 0 | 7 | 0 |
| [xiaomi-yi](manufacturer-xiaomi-yi.md) | 0 | 0 | 2 |
| [yashica](manufacturer-yashica.md) | 7 | 0 | 0 |
| [z-cam](manufacturer-z-cam.md) | 8 | 0 | 0 |
| [zeiss](manufacturer-zeiss.md) | 0 | 0 | 1 |

## Source-quality findings

- Canon's museum has 466 entries in selected digital categories; the current store was unavailable, and the museum is not a current worldwide retail inventory. Nikon's public selector XML supplies 192 camera names ; its separate archive page currently lists software, not additional cameras.
- Sony's official digital-category result count includes lenses and is paginated. Neither 643 results nor the first ten visible cards establishes 643 camera models. Direct page captures were unavailable; gPhoto/LibRaw subsets remain clearly separate.
- Firmware indexes omit bodies without updates: OM's E-PL10 and TG-6 manual records demonstrate why manuals are also needed. Sigma's SD10/DP1s raw-decoder entries similarly exceed its firmware list. Panasonic's useful S/MFT/compact indexes are different from the empty historical redirect stub.
- The former ZEISS ZX1 URL redirects to a generic photography page with no model record and was rejected as roster evidence.
- General Imaging's former domain now hosts unrelated material and was rejected. AgfaPhoto's requested category resolved to a homepage canonical; its products are a sample. Casio's regional manual search warns that some models are excluded and did not expose its full denominator in the captured HTML.
- Search results included precise-sounding patch, sensor and recovery claims on generic review pages without an original repository or reproducible evidence. Those claims were not promoted into compatibility records. Search snippets and brand resemblance are discovery leads, not hardware facts.
- The new Casio WQV interoperability route, JVC vendor API matrix and Phase One IIQ/calibration project add useful primary evidence beyond firmware patching. None establishes a universal replacement-firmware route.

## Durable artifacts and refresh

[Model index](https://github.com/magnus919/agent-skills/blob/7fb8a7c80e1a0811cf704502be3396d36a885420/docs/research/camera-hacking/manufacturer-model-index.json) routes to bounded JSON pages under `model-ledgers/` and readable source tables under `references/`. [Capture manifest](https://github.com/magnus919/agent-skills/blob/7fb8a7c80e1a0811cf704502be3396d36a885420/docs/research/camera-hacking/manufacturer-source-captures.json) records URLs, digests, retrieval outcomes and dispositions. [Audit status](https://github.com/magnus919/agent-skills/blob/7fb8a7c80e1a0811cf704502be3396d36a885420/docs/research/camera-hacking/manufacturer-audit-status.json) records the per-brand findings. Existing [family coverage](https://github.com/magnus919/agent-skills/blob/7fb8a7c80e1a0811cf704502be3396d36a885420/docs/research/camera-hacking/family-coverage.json) remains the detailed Fujifilm X / Ricoh GR denominator. Raw copyrighted manuals, vendor firmware, and the full video captions are not redistributed.

For a refresh, retrieve each listed source, reapply the recorded extraction boundary, reconcile added/removed identities and aliases, and retain old model records rather than silently deleting discontinued cameras. Close a gap only with a complete source denominator or a documented source-by-source reconciliation. A failed retrieval stays unresolved. The original research package retains its own inventory validator; it does not validate camera behavior. The installed skill contains the readable source tables and the detailed X/GR identity ledger without depending on that repository checkout.
