# GxP AI Governance Research Brief

**Research question:** What must the `ai-governance` skill add to support a job requirement for AI governance aligned with GxP, ALCOA+, and data integrity?

**Decision context:** Determine whether the skill fully covers the job requirement and identify a bounded, reusable extension without turning the skill into legal advice or a complete pharmaceutical quality-system manual.

**Scope:** Governance of AI systems that create, transform, analyze, or influence GxP-relevant records, decisions, processes, or submissions. Includes data integrity, electronic records, validation/assurance, lifecycle controls, quality ownership, and AI-specific evidence. Excludes legal interpretation, detailed SOP authoring, site-specific validation protocols, and implementation of production security controls.

**Evidence standard:** Prefer current official regulator, inspectorate, and standards-body sources. Industry guidance is used for implementation context and is labeled accordingly. Regulatory claims require re-verification at use time.

## Executive summary

The existing skill covers the general governance architecture needed for GxP AI: accountable ownership, risk tiering, lifecycle gates, lineage, auditability, monitoring, vendor due diligence, and regulatory mapping. It does not yet cover the regulated operating vocabulary and evidence expected for GxP systems: ALCOA+ data-integrity attributes, computerized-system validation or risk-based assurance, electronic-record and electronic-signature controls, audit-trail governance, quality-unit oversight, deviation/CAPA/change control, periodic review, and the special validation and performance evidence needed when AI contributes to regulated decisions or processes.

The appropriate extension is a focused reference, not a claim that the skill makes a system compliant. That reference should add a GxP overlay to every AI lifecycle gate and require a documented boundary between general AI governance and the organization's QMS, CSV/CSA, data-integrity, privacy, and security owners.

## Key findings

### 1. GxP data integrity is a quality-system concern, not merely better data lineage

FDA's drug-CGMP data-integrity guidance frames data integrity within CGMP requirements. MHRA's GxP guidance covers compliant data-governance expectations across GLP, GCP, GMP, GDP, and pharmacovigilance. PIC/S PI 041-1 and WHO guidance make ALCOA+ attributes operational expectations for records and data, including audit trails and lifecycle controls.

**Implication for the skill:** Add an explicit ALCOA+ control review. Existing fields such as provenance, lineage, quality, and retention are necessary but do not ask whether records are attributable, legible, contemporaneous, original, accurate, complete, consistent, enduring, and available.

### 2. Electronic records and audit trails need explicit controls

21 CFR Part 11 requires controls for electronic records and signatures, including validation, record protection and retrieval, access limitation, and secure, computer-generated, time-stamped audit trails. WHO guidance calls for GxP-relevant audit trails to be enabled and periodically verified throughout the data life cycle.

**Implication for the skill:** A GxP deployment gate must ask whether the system creates or relies on regulated electronic records, whether audit trails capture create/modify/delete events, whether they are protected and reviewed, whether signatures are attributable and non-repudiable, and whether records remain retrievable for the retention period.

### 3. Validation/assurance and change control are missing

GAMP 5 Second Edition explicitly addresses risk-based compliant GxP computerized systems and adds AI/ML, cloud, open-source, and data-integrity considerations. FDA and ICH materials likewise connect computerized systems, validation, quality risk management, and data integrity.

**Implication for the skill:** Add a risk-based validation/assurance decision at intake and build gates. For adaptive or probabilistic AI, the evidence plan must define the intended use, model/data version, acceptance criteria, performance envelope, change boundaries, revalidation triggers, and rollback or retirement path.

### 4. AI introduces evidence questions beyond ordinary computerized-system validation

EMA's reflection paper on AI in the medicinal-product lifecycle emphasizes data integrity for model development and generalizability of performance to the target population and context of use. FDA's 2025 draft guidance addresses AI used to produce information or data supporting regulatory decision-making for drugs and biological products. These are guidance materials, not a universal AI validation standard.

**Implication for the skill:** Add AI-specific evidence requirements: context-of-use statement, representative data and provenance, training/evaluation separation, performance by relevant subgroups and operating conditions, uncertainty and failure handling, human review, model/version traceability, monitoring for drift, and controls for model or data changes.

### 5. Governance must connect to the QMS instead of creating a parallel bureaucracy

The sources converge on accountability, risk management, documentation, auditability, and lifecycle control, but they do not imply that an AI council replaces the quality unit or validation process.

**Implication for the skill:** Add an ownership map that distinguishes the AI governance body from QA/quality unit, system owner, process owner, data owner, validation/assurance lead, privacy, security, regulatory, and supplier-quality roles. Exceptions, deviations, CAPA, change requests, and periodic reviews must land in the authoritative QMS or linked controlled records.

## Capability gap map

| Capability | Existing skill | Required extension |
|---|---|---|
| AI governance operating model | Strong | Add QMS and quality-unit interfaces |
| Risk tiering | Strong | Add GxP criticality and patient/product/data-integrity impact |
| Lifecycle gates | Strong | Add GxP evidence and release criteria per gate |
| Data lineage/provenance | Strong | Add ALCOA+ and complete data lifecycle review |
| Electronic records/signatures | Minimal | Add Part 11 / equivalent control prompts, without legal interpretation |
| Audit trails | General auditability | Add enablement, protection, review, retention, and exception handling |
| Validation/assurance | Implied by evidence gates | Add risk-based CSV/CSA decision and validation evidence inventory |
| AI performance evidence | General evaluation | Add context of use, generalizability, uncertainty, drift, and change triggers |
| QMS operations | Not covered | Add deviation, CAPA, change control, periodic review, training, and SOP interfaces |
| Supplier oversight | Strong general due diligence | Add supplier quality, model/data provenance, audit rights, change notification, and continuity |
| Regulatory mapping | Strong generic mapping | Add GxP overlays and require primary-source verification |

## Recommended skill change

Add `references/gxp-and-data-integrity.md` with:

1. A boundary statement: educational governance guidance, not legal advice or a validation package.
2. A GxP applicability/intake screen.
3. ALCOA+ and data-lifecycle control prompts.
4. Risk-based validation/assurance decision logic.
5. GxP AI lifecycle gates and required evidence.
6. QMS ownership and escalation interfaces.
7. Supplier/model due diligence additions.
8. A verification checklist and primary-source links.

Add at least one evaluation case for a life-sciences AI system and assert that the answer distinguishes general AI governance from GxP validation and QMS responsibilities.

## Confidence and limitations

- **High confidence:** The skill currently has a material GxP/ALCOA+ coverage gap. This is supported by direct comparison between the skill's current references and multiple official or standards-body sources.
- **High confidence:** ALCOA+, audit trails, electronic-record controls, lifecycle integrity, and validation/assurance need explicit treatment.
- **Moderate confidence:** The exact evidence package for a particular AI use case depends on GxP domain, jurisdiction, intended use, system boundary, and the organization's QMS. No universal AI validation recipe should be asserted.
- **Open question:** Which GxP domains matter most for the target role: GMP manufacturing, GCP clinical trials, GLP laboratories, GDP distribution, or pharmacovigilance? The reference should remain cross-domain, with domain-specific obligations routed to QA/regulatory specialists.

## Sources

Accessed 2026-08-20 UTC.

1. FDA, *Data Integrity and Compliance With Drug CGMP*, https://www.fda.gov/media/119267/download
2. FDA, *Part 11, Electronic Records; Electronic Signatures — Scope and Application*, https://www.fda.gov/regulatory-information/search-fda-guidance-documents/part-11-electronic-records-electronic-signatures-scope-and-application
3. eCFR, *21 CFR Part 11 — Electronic Records; Electronic Signatures*, https://www.ecfr.gov/current/title-21/chapter-I/subchapter-A/part-11
4. MHRA, *GxP Data Integrity Guidance and Definitions*, https://www.gov.uk/government/publications/guidance-on-gxp-data-integrity
5. PIC/S, *PI 041-1 Guidance on Data Integrity*, https://picscheme.org/docview/4234
6. WHO, *TRS 1033 Annex 4: Guideline on Data Integrity*, https://www.who.int/docs/default-source/medicines/norms-and-standards/guidelines/inspections/trs1033-annex4-guideline-on-data-integrity.pdf
7. EMA, *Guideline on Computerised Systems and Electronic Data in Clinical Trials*, https://www.ema.europa.eu/en/documents/regulatory-procedural-guideline/guideline-computerised-systems-and-electronic-data-clinical-trials_en.pdf
8. EMA, *Reflection Paper on the Use of Artificial Intelligence in the Medicinal Product Lifecycle*, https://www.ema.europa.eu/en/documents/scientific-guideline/reflection-paper-use-artificial-intelligence-ai-medicinal-product-lifecycle_en.pdf
9. FDA, *Considerations for the Use of Artificial Intelligence to Support Regulatory Decision-Making for Drug and Biological Products*, https://www.fda.gov/regulatory-information/search-fda-guidance-documents/considerations-use-artificial-intelligence-support-regulatory-decision-making-drug-and-biological
10. ICH, *Q9(R1) Quality Risk Management*, https://database.ich.org/sites/default/files/ICH_Q9(R1)_Guideline_Step4_2022_1219.pdf
11. ISPE, *GAMP 5 Guide, 2nd Edition*, https://ispe.org/publications/guidance-documents/gamp-5-guide-2nd-edition
12. European Commission, *EudraLex Volume 4, Annex 11: Computerised Systems*, https://health.ec.europa.eu/system/files/2016-11/annex11_01-2011_en_0.pdf
