# Research Log: Nine-Phase Journey Validation Against SDLC and Agentic Frameworks

**Question:** Does the neckbeard nine-phase change-request journey have phases or feedback loops with no counterpart in established SDLC lifecycle models or published agentic-workflow frameworks, and which differences should neckbeard adopt, adapt, or reject?

**Issue:** #372 (research-only; no behavior changes)
**Track:** Academic/comprehensive, comparative + gap-finding
**Subject pinned at:** journey.md commit `04a9b60b58244b5007e9279d53ed504362303320` (branch `research/neckbeard-journey-sdlc-validation`, off `origin/main`)
**Started/completed:** 2026-08-22 UTC
**Companion dossier:** [journey-sdlc-validation-brief.md](journey-sdlc-validation-brief.md)

## Scope

**Inclusion criteria:** primary/published standards text or official catalog metadata; first-party technical literature from framework owners (Anthropic, OpenAI, agentskills.io); full public reproductions of SEI technical reports; reputable secondary explainers only as triangulation for paywalled standards, never as sole support for a finding.

**Exclusion criteria:** vendor marketing, unauthenticated scans of copyrighted standards, blog summaries where a first-party source was reachable, opinion pieces without verifiable authorship.

**Depth:** moderate-to-deep (support for an adopt/adapt/reject decision); 10+ retained sources, 3 angles (standards, capability-maturity, agentic practice).

## Search record

| Query / action | Purpose | Result |
|---|---|---|
| `git fetch origin` + `git log -1 --format=%H -- neckbeard/references/journey.md` | Pin the studied revision | SHA `04a9b60b58244b5007e9279d53ed504362303320` |
| Read journey.md, SKILL.md, stages.md (§ Stage 6, gates), lifecycle.md, delivery-packet.md, risk-authority-gates.md (grep) | Ground truth on the subject | Full phase/gate/path model captured; Stage-6 "Deliver and learn" obligation identified |
| WebSearch: ISO/IEC 15288 retirement disposal stage | SDLC model 1 | Retained ISO catalog + IEEE SA + Wikipedia clause inventory |
| WebSearch: ISO/IEC/IEEE 12207 maintenance disposition | SDLC model 2 | Retained ISO catalog; arc42 summary fetched |
| WebSearch: CMMI-DEV V1.3 SEI technical report | SDLC model 3 | Retained full-text mirror; DTIC/Kilthub located, not fetched |
| WebSearch: ISO/IEC/IEEE 29148 requirements engineering | Candidate SDLC model 4 | **Rejected — no legitimate primary text accessible** (unauthorized PDF scans only); dropped from dossier |
| WebSearch: ITIL 4 service value system / value chain | SDLC model 4 | Retained InvGate explainer + itSM.tools practitioner analysis (incl. ITIL v5 note); PeopleCert text licensed, not accessible |
| WebSearch: Anthropic building effective agents | Agentic approach 1 | Retained full first-party article |
| WebSearch: OpenAI practical guide building agents | Agentic approach 2 | Retained first-party PDF (downloaded + locally converted via anydoc) |
| Fetch agentskills.io/specification.md | Agentic approach 3 | Retained full specification |
| Grep neckbeard/ for feedback/learning/retire/rollback/monitor terms | Internal cross-check for RQ1 | Confirmed Stage-6 lesson capture exists but journey phase 9 does not consume it |

All web access dates: 2026-08-22.

## Sources gathered (retained)

| Source | URL | Accessed | Tier / strength | Used for |
|---|---|---|---|---|
| ISO/IEC/IEEE 15288:2023 catalog entry | https://www.iso.org/standard/81702.html | 2026-08-22 | Tier 1 (official catalog; text paywalled) | Edition identity, scope |
| IEEE SA 15288 page | https://standards.ieee.org/ieee/15288/10424/ | 2026-08-22 | Tier 1 | Corroboration |
| ISO/IEC 15288 clause inventory (Wikipedia) | https://en.wikipedia.org/wiki/ISO/IEC_15288 | 2026-08-22 | Tier 3, corroborated ×2 | 30-process / 14-technical-process structure incl. Operation, Maintenance, Disposal |
| ISO/IEC/IEEE 12207:2017 catalog entry | https://www.iso.org/standard/63712.html | 2026-08-22 | Tier 1 | Scope incl. maintenance/disposal categories |
| arc42 12207 summary | https://quality.arc42.org/standards/iso12207 | 2026-08-22 | Tier 2 | Process-category detail; triangulates ISO catalog |
| CMMI-DEV V1.3 full text (CMU/SEI-2010-TR-033, public mirror) | http://cmmis.free.fr/cmmi-dev/text/index.php | 2026-08-22 | Tier 2 mirror of Tier 1 report (front matter verified) | 22 process areas; CAR/PPQA/VER/VAL/DAR/CM |
| ITIL 4 SVS explainer | https://invgate.com/itsm/itil/service-value-system | 2026-08-22 | Tier 2 | SVS components; six SVC activities; continual improvement |
| ITIL 4 SVC practitioner analysis | https://itsm.tools/itil-4-service-value-chain/ | 2026-08-22 | Tier 2 (named practitioner, itSMF UK board) | SVC activity semantics; ITIL Version 5 announcement (Jan 2026) |
| Anthropic, Building Effective Agents | https://www.anthropic.com/engineering/building-effective-agents | 2026-08-22 | Tier 1 (first-party) | Workflow/agent patterns; human-gate placement; coding-agent conclusions |
| OpenAI, A Practical Guide to Building Agents (PDF) | https://cdn.openai.com/business-guides-and-resources/a-practical-guide-to-building-agents.pdf | 2026-08-22 | Tier 1 (first-party; downloaded, converted locally with `anydoc` — exit 0, 517 lines, headings verified) | Orchestration; guardrails; tool risk ratings; human-intervention triggers |
| Agent Skills specification | https://agentskills.io/specification.md | 2026-08-22 | Tier 1 (first-party) | Format scope; `allowed-tools`; absence of lifecycle semantics |
| neckbeard internal references (journey.md, SKILL.md, stages.md, lifecycle.md, delivery-packet.md, risk-authority-gates.md) | repo paths | 2026-08-22 | Tier 1 (subject of study) | Ground truth; internal-alignment check |

## Sources rejected and why

| Source | Reason |
|---|---|
| ISO/IEC/IEEE 29148:2018 — unauthorized scanned PDFs (drkasbokar.com, nirmt.com mirrors) | Copyright/unauthorized copies; CRAAP authority/legality failure. Standard dropped from the dossier; findings rest on 15288/12207/CMMI instead. |
| ISO 29148 ReqView template page | Vendor template marketing, not normative content. |
| openai.com/business/... landing page | HTTP 404 at access time; superseded by direct PDF retrieval from cdn.openai.com. |
| Medium posts (Dubetcky; MAA1; Bharatkumar), dev.to summary, Reddit threads | Tier 3-4 commentary duplicating first-party sources already retained. |
| jamasoftware.com / konfirmity.com / pacificcert.com 15288 explainers | Commercial vendor glossaries; superseded by catalog + corroborated clause inventory. |
| sprintzeal.com ITIL blog | Training-provider marketing. |
| DTIC ADA532839 PDF, CMU Kilthub record, ieeexplore.ieee.org entries | Legitimate but not fetched (redundant with retained CMMI mirror / catalog metadata); recorded per the durable-artifact gate so exclusion is distinguishable from oversight. |
| broadswordsolutions.com / gob.mx CMMI PDF mirrors | Redundant copies; mirror provenance less clear than the retained full-text reproduction. |

## Access failures / unverifiable sources

- **Paywalled normative texts:** ISO 15288, ISO 12207, ITIL 4 (PeopleCert/Axelos). Structural claims triangulated via official catalog metadata + ≥2 independent secondary sources; clause-level detail carries the limitation noted in the dossier.
- **openai.com/business landing page:** HTTP 404 (2026-08-22). PDF retrieved directly instead.
- **ITIL Version 5 normative text:** announced Jan 2026, not yet accessible; flagged for revalidation.
- No other access failures; all retained URLs returned HTTP 200 on 2026-08-22.

## Durable-artifact record (research-methodology gate)

- **Durable destination:** this log + the companion brief, committed in-repo at `neckbeard/research/` (repo precedent: `ai-governance/research/gxp-ai-governance-{brief,log}.md`). PR branch `research/neckbeard-journey-sdlc-validation`.
- **Extraction granularity:** every retained source appears in the retained-sources table with URL, access date, tier, and use; every material claim in the brief traces to a table row or to the subject repo files. Rejected sources and access failures are recorded above with reasons.
- **Provenance:** subject pinned to journey.md SHA `04a9b60b58244b5007e9279d53ed504362303320`; comparison basis and doctrine lens recorded in the brief header.
- **Extraction vs synthesis:** the brief carries verdicts and synthesis; this log carries source-level records and the search/decision trail.
- **Not preserved:** paywalled full texts were not reproduced (license); only structural claims drawn from accessible metadata/corroboration are preserved. OpenAI PDF conversion artifact lives in `/tmp/journey-research/` (ephemeral; content represented by the retained claims above).

## Pre-publication gateway check

Academic/comprehensive track: inclusion/exclusion criteria fixed before searching; triangulation applied (each standards finding rests on ≥2 independent sources or is flagged single-source in the brief); confidence labels (H/M) assigned per finding; limitations and open questions stated explicitly; no factual claim in the brief rests on a rejected source.
