# Camera-hacking research log

Date: 2026-10-29. Commission: discover material for a public camera-hacking skill, beginning with the supplied video and expanding across manufacturers. User clarified that this is for anyone, not a personal inventory, and requested manufacturer/model references plus reverse-engineering routing.

## Scope and method

Moderate technical discovery. Questions: what people change, how they gain interoperability, which bodies/firmware they actually document, what evidence supports the features, and how the future skill should route readers. Prefer project authors, source repositories, release notes and vendor protocols. Use secondary articles, community posts and directories to find primary material. Include historical projects while marking toolchain/provenance gaps.

The natural durable destination is this repository's `docs/research/camera-hacking/` package. It holds discovery notes without activating a new catalog skill. Full captions and compact video metadata are separate user artifacts in the task's artifact workspace; they are excluded from catalog source files. No firmware, proprietary libraries, camera data or downloaded third-party executable is included. No source contact, account registration, purchases, camera writes, debug enablement, publishing, commit or PR was performed.

## Search history

Searches used the web search/open tool, followed by direct primary README retrieval when useful. Result counts are intentionally not used as completeness evidence.

| Pass | Queries or direct routes | Outcome |
|---|---|---|
| Video identity | Exact video ID; canonical YouTube URL; short URL; title lookup | Canonical web retrieval initially failed; short URL supplied title. Search mirror supplied leads only. yt-dlp later retrieved primary metadata and original English captions. |
| Existing ecosystem | Digital-camera hacking + Magic Lantern / CHDK / OpenMemories / Nikon | Established project documentation retained; aggregator lists used only as discovery leads. |
| Creator-linked projects | Ricoh GR IV, Hasselblad research and reconstruction, WonderLantern, fpSup, OpenPocketCine, Ritual, GoPro Labs | Inspected primary project pages; read detailed READMEs for central evidence and limitations. |
| Required additional brands | Olympus/OM firmware projects; Panasonic PTool/GH4/LUMIX controls; Leica M reverse engineering | Retained primary projects and split model notes. |
| Wider still-camera brands | Pentax/pkTriggerCord; Samsung NX; Kodak DCS and Charmera | Distinct mechanisms and firmware families retained. |
| Action and 360 | Insta360 firmware/SDK; Xiaomi/YI autoexec; SJCAM; AKASO | Primary projects retained with model/board boundaries and negative compatibility findings. |
| Cinema and medium-format | Phase One SDK; Z CAM control/RE; Blackmagic developer protocols; ARRI CAP; RED RCP/RCP2 | Official interfaces retained as alternatives; distinguish control from modification. |
| Unusual/legacy | Lytro unlock; Casio firmware/RAW; Minolta; Polaroid digital; ZEISS ZX1 | Lytro primary research retained. Other searches preserved as explicit gaps; analog Polaroid controller work excluded. |
| Legacy extension audit | Epson R-D1; JVC; Kinefinity; Digital Bolex; grouped AgfaPhoto/BenQ/GE, Contax/Kyocera, HP/Toshiba/Sanyo, Rollei/Vivitar/Yashica | Official baselines and weak/negative discovery results recorded individually. Grouped searches explicitly carry weaker coverage. |
| Supporting routes | Read current `binary-analysis` and `software-architecture-analysis` catalog source | Correct routing names and implementation limitations recorded in skill findings. |

## Caption acquisition and preservation

Installed yt-dlp was available. A sandbox attempt failed DNS resolution. An authorized network-enabled retry retrieved video metadata but the `en` VTT request returned HTTP 429. A bounded retry selecting **`en-orig` / JSON3** succeeded. No cookies, account login, video download, proxy service, paid transcript API or generated speech transcription was used.

Flattened all **531 nonempty caption events**, preserving their start times and text without silent spelling/name corrections. Caption timing extends to **1219.52 seconds**, while video metadata reports **1218 seconds**. Preserve this discrepancy: it is another reason not to treat auto-caption boundaries as frame-accurate. No audio/visual review was performed, so names, negations and demonstrations remain unverified. The raw captions, readable transcript and compact metadata have SHA-256 digests in [transcript-provenance.json](transcript-provenance.json). Raw extraction metadata containing temporary media URLs was not copied into repository artifacts.

## Source evaluation and extraction ledger

The [structured source records](source-records.json) preserve primary URLs, access date, extracted contributions and evidence class. The manufacturer references are the source-level notes; model references expand consequential compatibility and validation boundaries. The synthesis lives in the README, video ledger and skill findings. Source inclusion does not mean independent confirmation.

| Source group | Decision / strength | Extraction and durable destination |
|---|---|---|
| Creator metadata and auto-caption track | Retain as attributed media; imperfect transcription | Source identity/hashes in provenance; complete transcript in separate user artifact; every chapter disposition in video claim ledger |
| Primary camera-project READMEs and releases | Retain as primary documentation and attributed test reports; self-reported hardware results remain unreplicated | Individual manufacturer/model references; source records retain URLs and access date |
| Official SDK/protocol/update pages | Retain as vendor-documented interfaces only | Manufacturer references; SDK/update ability not upgraded to custom-firmware compatibility |
| gPhoto support and remote-control lists | Retain as a cross-brand alternative/baseline | Manufacturer index and gap records; transfer versus control distinction preserved |
| Awesome-Camera-Hacking and firmware project directories | Discovery leads; not authoritative compatibility evidence | Used to find primary projects such as Kodak; broad activity/quality labels excluded |
| Zolotube mirror of supplied video | Identity/project-link lead only; replaced by primary metadata/captions | No technical conclusion depends on the mirror |
| SonyAlphaRumors and Phoblographer newsletter | Leads to original-a7 story; direct linked article unavailable via web tool | PMCA/OpenMemories primary documentation supplies mechanism; modern shutter-angle primary artifact still unresolved |
| Reddit discussions and camera press | Leads only, including OM release, GH4, Digital Bolex rebuild, recent Sony report | Followed primary URLs where available; untraced claims remain unresolved |
| Pentax Hack site | Inaccessible primary body in direct retrieval | Historical lead retained with retrieval gap; pkTriggerCord provides actual retained protocol evidence |
| Incorrect `fujihack/libfuji` guessed URL | Reject: 404 | Corrected through project's own link to `petabyt/libfuji`; no dead route retained |
| Epson printer RE, Kyocera phone unlocking, analog SX-70 replacement board, film scanners | Exclude from digital photographic camera feature evidence | Scope mismatch; do not count them as evidence of same-brand camera modification |
| Random binaries, firmware mirrors and proprietary upstream files | Not downloaded or qualified | Any later investigation needs provenance/licensing review; public visibility is not a blanket license |
| Video warranty/regulatory statements | Exclude from technical conclusions; legal research not undertaken | Video ledger flags unresolved jurisdiction/date-specific interpretation; no legal guarantee adopted |
| Video predictions, AI subscriptions and sponsorship/mentorship | Exclude from skill requirements and technical evidence | Chapter dispositions preserved in video ledger; full source remains in transcript artifact |

## Analytical conclusions

The strongest reusable pattern is exact identity and evidence separation. Project existence, static analysis, build integrity, emulation, single-device reports, independent reproduction and recovery are different claims. The references keep these boundaries explicit. Similar firmware names, SoCs or retail branding cannot safely replace matching image identity.

The source set is mostly authored by project developers, so independent convergence is limited. Multiple news stories repeating one README or demonstration are not independent replications. No hardware-qualified recommendation or quantitative safety estimate follows from this pass. “No project qualified” describes the search performed, not impossibility.

## Preservation and completion check

- Every retained primary contribution is linked from the manufacturer/model notes or source records; cross-brand sources have their own records.
- Every supplied-video chapter has a retained claim, unresolved status or exclusion decision.
- Raw captions, complete flattened text and compact metadata are preserved as user artifacts with matching provenance hashes.
- The public notes preserve source dates, attribution, uncertainty, contradictions and explicit next evidence.
- The package remains discovery material. No `camera-hacking/SKILL.md`, catalog registration, eval manifest or executable operational wrapper has been authored.

## Continuation priorities

1. Deepen each selected model's source/release provenance and actual feature tests. Primary documentation suffices for discovery, not for an installation recommendation.
2. Trace unresolved video claims: exact Ricoh imperial patch, GR III tool roster, modern Sony shutter-angle implementation/recovery, specific fpSup open-gate/gyro release and claimed GoPro chatbot.
3. Investigate weaker manufacturer gaps at the model/OEM level; grouped legacy searches are a starting inventory, not a comprehensive negative audit.
4. Decide initial category boundaries for webcams, industrial/security cameras, phones, DIY modules, hardware conversions and lens interfaces. The public skill can grow without collapsing these into one generic procedure.
5. Author the actual skill only after this discovery scope is accepted; follow current catalog requirements for metadata, README, trigger probes, evals, references, applicable scripts/tests and generated projections. This is a next phase, not a request to change cameras.

## Follow-up: full Fujifilm X / Ricoh GR family audit

The user specifically requested full-family reference coverage. The initial X-A2/XF1 and GR IV samples were insufficient for that scope. The follow-up uses the same research-methodology process with an explicit completeness denominator: the vendor's model roster, not the set of projects that happened to appear in search.

### Scope and preservation

- **Fujifilm:** all 52 X-series identities in the retrieved official firmware index, plus vendor-documented X-T1 IR. Twelve lineage references account for every row, including compact/bridge X models, X-A, X-M, X-E, X-Pro, X-H, both X-S lines, X-T tiers, X100 generations and X half. GFX remains separate. Cosmetic colourways/kits route to their base body; no byte-level identity is inferred from appearance.
- **Ricoh:** all four legacy GR DIGITAL generations, APS-C GR (2013), GR II, III/IIIx and IV, their HDF/Monochrome variants, nine named editions, and announced GR IVx. There are 13 released digital body/processing variants, nine edition identities and one announced target. Film GRs and GXR modules are explicitly distinguished.
- **Durable records:** [family ledger](family-coverage.json), [Fujifilm map](references/family-fujifilm-x-series.md), [GR map](references/family-ricoh-gr-series.md), lineage/model notes and [source-capture manifest](family-source-captures.json). Thirty retrieved source files are preserved separately as task research artifacts with their URL, date, byte count and digest. Third-party documentation and raw catalog snapshots are not vendored into public skill content.

### Discovery performed

Retrieved vendor current/legacy firmware rosters, Ricoh history and special-model pages. Followed primary project references for FujiMod, fujicli, libfuji, Furble, community recipe tooling, Filmcase, GRKit, FRAME-GR2, m10v, GR-DLC, GR Mod, GR3-LUTSmith, Look Editor, plain-IIIx firmware work, and GR wireless research. GR DIGITAL II/III/IV and 2013-GR firmware/hacking searches retained explicit gaps rather than importing newer-body methods. A secondary GR directory provided 34 primary project links; the [inventory](references/ricoh-gr-project-inventory.md) distinguishes inspected sources from uninspected leads.

This is model-roster-complete discovery routing for the stated captures, not an exhaustive web search or independent camera qualification for each model. Known official names can be added as new rows as releases occur; the announced IVx is not counted as a released or supported modification target.

### Material findings and contradictions

1. FujiMod has a concrete **X70** release lead, alongside a broader identity/control/emulation catalog. Catalog presence is not a working modification release. Its tree was inspected at `925640f1ff2327eeba118437af35790c0a1656eb`; the tree was checked for completeness before deriving flags.
2. The old fujicli support page remained search-indexed but returned 404. Resolved current README and CUE model declarations at `6366cff82449d19dab9e6234c3dc6ec5922e6ccb`; do not reuse the obsolete matrix as current support. Only X-T5 is described as extensively tested. A schema declaration cannot replace a device observation.
3. The community recipe protocol reports successes on specific X-H2/X-T5 firmware and a failing X-Pro3 path. Filmcase's broader predictions cannot erase that failure or establish model generations authoritatively.
4. X100VI slot-manager eligibility is 1.32, while the captured vendor index shows 1.31. The discrepancy is preserved; neither an upgrade nor a downgrade is inferred.
5. The directly retrieved GRKit README has newer grouped test claims than the indexed page. The model map uses that captured primary README, attributes its reports and preserves the persistent SD-script setting boundary. It does not claim that every grouped body/module combination was separately tested.
6. Current GR Mod and FRAME READMEs differ from older directory summaries: GR Mod now names III/IIIx as well as IV, while FRAME describes WNX-L2/app 1.0.6. The secondary summaries are leads, not current compatibility authority.
7. GR III/IIIx official updates now have newer versions than many firmware patch inputs. Each project keeps its own version/variant eligibility, including HDF differences. The GR II startup proposal writes internally and nevertheless claims card removal rolls back; this is an unverified persistence/recovery claim, not a safe-operation guarantee.
8. GR IV Monochrome and colour-body monochrome-look unlocks are different targets. Announced GR IVx has no qualified released firmware/modification evidence here.

No camera connections, third-party script execution, builds, setting writes, firmware installs, or recovery tests were performed. Validation checks cover source-roster accounting, unique identities, all local links, JSON parsing, reference-size caps and capture hashes. They do not establish behavior of any upstream project.

## Manufacturer completeness audit and publication scope — 2026-10-29

The user expanded the task to audit the other manufacturers and publish the discovery package through a merged PR with local synchronization. Issue #741 records that delivery scope. The work remains discovery: no installable camera-hacking skill, firmware binaries, camera operations or new tool wrappers are included. The reverse-engineering routing findings remain in skill-design-findings.md.

The audit checks every one of the 43 existing manufacturer/brand-family entries and records a completeness limitation for each. This is an audit result, not a certification of all-time model completeness. Current/legacy vendor catalogs were queried first, followed by gPhoto and LibRaw primary implementation rosters. Their different semantics and alias/category exclusions are preserved in manufacturer-audit-findings.md, manufacturer-model-index.json and the split model-ledgers/ records. Network-unavailable, dynamic, irrelevant, partial and retained captures have separate dispositions in manufacturer-source-captures.json.

Searches included maker-specific camera/firmware/reverse-engineering/GitHub queries for BenQ, AgfaPhoto, General Imaging, Contax/Kyocera, Casio, Epson, HP, Toshiba, Sanyo, Rollei, Vivitar, Yashica, ZEISS, Digital Bolex, Konica/Minolta, Polaroid, JVC, Kinefinity and Phase One, and vendor catalog/archive searches for the larger makers. Retained primary source paths are linked from each manufacturer's audit. Duplicate codec lists, analog-only repairs, phone/security-camera work, generic reviews without original evidence and the unrelated current General Imaging domain were not promoted to digital-camera modification claims. Search non-discovery is not proof of impossibility.

New retained routes: Casio WQV original protocol and model-separated WQV Blink support; JVC's official camera/API/firmware matrix; Phase One IIQ/calibration exploration; LibRaw's DiMAGE Z2 input-identification logic; Magic Lantern's modern research directories without a release-support inference; GoPro Labs' current releases with feature-specific limits. Each has an extracted source record or a manufacturer-source capture entry. No upstream code was executed and no live camera result was inferred.

Raw documentary captures remain separate private research artifacts, with only metadata, factual model labels, hashes, source-linked paraphrases and our analysis published. Full captions were not redistributed. Local verification checks structural consistency and source hashes only; it does not establish camera safety, photographic behavior, recovery or source-to-device reproduction.
