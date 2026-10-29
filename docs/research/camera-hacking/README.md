# Camera-hacking discovery

Research for a public, manufacturer-independent `camera-hacking` skill. This directory is the discovery archive. The installable [camera-hacking skill](../../../camera-hacking/SKILL.md) packages the workflow and source-bound references. No camera modifications were performed during this research. Researched **2026-10-29** using `research-methodology` and the catalog's `agent-skills` guidance.

## What the evidence supports

There is a substantial ecosystem of camera modification and interoperability work, both established and recent. The useful organizing unit is **manufacturer → model → firmware/board revision → feature → evidence**, rather than a universal hacking recipe. The [manufacturer index](manufacturer-index.md) routes to individual references and explicitly records weaker coverage.

The projects use materially different mechanisms: official SDKs, reverse-engineered remote protocols, card-loaded programs, persistent settings, firmware patches, and hardware changes. An external monitor's waveform is not an in-camera waveform. Code execution does not establish that a proposed photographic feature works. A checksum or emulator result does not establish safe camera operation.

## Start here

| Artifact | Purpose |
|---|---|
| [Manufacturer completeness audit](manufacturer-audit-findings.md) | Per-brand denominator, source limitations and split model inventories |
| [Manufacturer index](manufacturer-index.md) | Brand coverage, evidence status, and individual reference routes |
| [Video claim ledger](video-claim-ledger.md) | Timestamped claims from the supplied video and corroboration limits |
| [Research log](research-log.md) | Scope, retrieval method, exclusions, limitations, and continuation work |
| [Skill design findings](skill-design-findings.md) | Proposed workflow, routing, model reference contract, and future eval scenarios |
| [Transcript provenance](transcript-provenance.json) | Video identity, caption quality, coverage, and artifact hashes |

The full downloaded auto-caption transcript and original JSON3 captions are preserved as separate user artifacts, outside the public catalog source tree. They have not been licensed for redistribution as part of this repository. The provenance record identifies their filenames and digests. Source-linked paraphrases, rather than copied upstream manuals or firmware, make up the references here.

## Expanded Fujifilm X and Ricoh GR coverage

- [Fujifilm X-series map](references/family-fujifilm-x-series.md): 53 explicit identities, organized into 12 lineage references, including legacy compacts and X-T1 IR.
- [Ricoh GR-series map](references/family-ricoh-gr-series.md): 13 digital body/processing variants, nine named editions and announced GR IVx, with model-specific references.
- [Machine-readable family ledger](family-coverage.json): per-model official sources, observed versions, project declarations and unresolved states.

Coverage means every listed identity has a research route. It does not mean every camera has a proven modification.

## Confidence and limits

High confidence in the existence and documented boundaries of the retained projects; limited confidence in generalized compatibility or safety. This investigation inspected public documentation and downloaded captions. It did not build patches, run third-party scripts, connect a camera, verify photographic output, test recovery, or independently reproduce maintainers' hardware reports. Repository activity, stars, and video popularity are not safety evidence.

This is a broad discovery pass, not an exhaustive census of every camera manufacturer or model. Brands with sparse results remain visible in the index. Smartphone cameras, surveillance cameras, industrial cameras, and DIY camera modules are separate expansion tracks; their inclusion needs an explicit scope decision before the public skill claims coverage.

## Manufacturer audit refresh

All 43 indexed brand families now have a completeness assessment, with **3,656 source rows** split into **93 model-ledger pages** and matching readable references. Counts overlap across sources and include family/alias labels; they are not a unique-camera census. Vendor archives, current offerings, gPhoto transfer/control and LibRaw decoding remain separate. Read [the findings and per-brand gaps](manufacturer-audit-findings.md) before drawing coverage conclusions. The existing X-series and GR-series maps remain the deeper family references.
