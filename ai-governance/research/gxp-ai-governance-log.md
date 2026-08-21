# Research Log: GxP AI Governance Gap

**Question:** What must `ai-governance` add to support GxP, ALCOA+, and data-integrity expectations?

**Track:** Academic/comprehensive, narrow technical/regulatory investigation
**Started/completed:** 2026-08-20 UTC
**Inclusion criteria:** Official regulators, inspectorates, standards bodies, and established life-sciences guidance directly addressing GxP data integrity, electronic records, computerized systems, validation/assurance, or AI in the medicinal-product lifecycle.
**Exclusion criteria:** Vendor marketing, generic responsible-AI commentary, legal interpretation, and sources that only mention AI without GxP/data-integrity relevance.

## Search record

| Query | Purpose | Result |
|---|---|---|
| `site:fda.gov data integrity ALCOA+ guidance pharmaceutical CGMP official` | FDA data-integrity baseline | Retained FDA CGMP data-integrity guidance |
| `site:fda.gov 21 CFR Part 11 electronic records electronic signatures official guidance` | Electronic-record controls | Retained FDA Part 11 guidance and eCFR |
| `site:ema.europa.eu Annex 11 computerized systems GMP official data integrity` | EU computerized-system expectations | Retained EMA computerized-system and Annex 11 materials |
| `site:gov.uk MHRA GxP data integrity guidance ALCOA official` | Cross-GxP inspectorate guidance | Retained MHRA final guidance |
| `site:ich.org ICH Q9(R1) quality risk management computerized systems data integrity official` | Risk-management baseline | Retained ICH Q9(R1) |
| `site:fda.gov artificial intelligence machine learning drug manufacturing quality systems guidance` | AI-specific FDA context | Retained FDA AI drug-development/manufacturing materials |
| `site:ema.europa.eu artificial intelligence reflection paper medicines lifecycle governance data integrity` | AI-specific EMA context | Retained EMA AI reflection paper |
| `site:picscheme.org PI 041 data integrity ALCOA official PDF` | ALCOA+ operational detail | Retained PIC/S PI 041-1 |
| `site:who.int guidance data integrity ALCOA pharmaceutical official` | Independent global corroboration | Retained WHO data-integrity guidance |
| `site:ispe.org GAMP 5 second edition artificial intelligence machine learning regulated systems` | Industry implementation context | Retained ISPE GAMP 5 description |

## Source decisions and extracted claims

### Retained: FDA CGMP data integrity guidance

- **Authority:** Tier 1 official regulator.
- **Relevant claim:** Data integrity is part of CGMP compliance for drugs under 21 CFR parts 210, 211, and 212.
- **Use in synthesis:** Establishes that data integrity belongs inside the quality and compliance system, not only in an AI/data platform.
- **Limitation:** Drug-CGMP focus; does not by itself cover every GxP domain or AI-specific validation.

### Retained: FDA Part 11 guidance and eCFR Part 11

- **Authority:** Tier 1 regulator and codified regulation.
- **Relevant claims:** Electronic records/signatures require controls for authenticity, integrity, confidentiality where appropriate, record retrieval, access control, validation, and secure time-stamped audit trails.
- **Use in synthesis:** Justifies an explicit electronic-record/audit-trail gate.
- **Limitation:** Applicability depends on the system's records and regulated use; this research does not make a legal applicability determination.

### Retained: MHRA GxP data-integrity guidance

- **Authority:** Tier 1 inspectorate guidance.
- **Relevant claim:** Guidance applies to data-integrity expectations across GxP sectors including GLP, GCP, GMP, GDP, and pharmacovigilance.
- **Use in synthesis:** Supports a cross-GxP reference and a data-governance/QMS boundary.
- **Limitation:** Guidance is not a substitute for jurisdiction-specific legal or quality advice.

### Retained: PIC/S PI 041-1 and WHO data-integrity guidance

- **Authority:** Tier 1 international inspection/health authority guidance.
- **Relevant claims:** ALCOA+ attributes and audit-trail lifecycle controls make data usable for informed decisions and support integrity across the data life cycle.
- **Use in synthesis:** Provides the operational vocabulary missing from the current skill.
- **Limitation:** These are guidance documents; exact adoption and terminology can vary by authority and domain.

### Retained: EMA computerized-system and AI materials

- **Authority:** Tier 1 regulator.
- **Relevant claims:** Computerized-system data security includes integrity, reliability, and availability; AI lifecycle considerations include integrity of model-development data and generalizability to the target population and context of use.
- **Use in synthesis:** Supports adding AI-specific performance/context evidence to GxP lifecycle gates.
- **Limitation:** The AI reflection paper is guidance/reflection material, not a universal validation standard.

### Retained: European Commission EudraLex Volume 4 Annex 11

- **Authority:** Tier 1 European Commission good-manufacturing-practice guidance.
- **Relevant claim:** Annex 11 provides the computerized-system control context relevant to regulated records, system operation, validation, and data integrity.
- **Use in synthesis:** Supports the explicit electronic-record, audit-trail, validation/assurance, and QMS-interface prompts in the GxP overlay.
- **Limitation:** Applicability and current interpretation depend on the system boundary, GxP domain, jurisdiction, and responsible quality/regulatory functions.

### Retained: ICH Q9(R1)

- **Authority:** Tier 1 international harmonization guidance.
- **Relevant claim:** Quality risk management provides the framework for risk-based decisions, including computerized-system and data-integrity concerns.
- **Use in synthesis:** Supports risk-based validation/assurance rather than one fixed control burden.
- **Limitation:** It is a framework, not an implementation procedure for a specific AI system.

### Retained: ISPE GAMP 5, 2nd Edition

- **Authority:** Tier 2 established industry guidance.
- **Relevant claim:** The second edition addresses risk-based compliant GxP computerized systems and includes AI/ML, cloud, open-source, and data-integrity topics.
- **Use in synthesis:** Supplies implementation vocabulary for validation/assurance and supplier/system lifecycle controls.
- **Limitation:** Industry guidance, not law or regulator-issued binding requirements.

## Rejected or not promoted

- Generic AI governance and responsible-AI sources: redundant with the existing skill and not specific enough to fill this gap.
- Vendor blogs and certification marketing: excluded because the question requires an authoritative baseline and vendor incentives would add little evidence.
- Search snippets without a retrievable primary document: used only for discovery, not as standalone evidence.

## Synthesis status

The research reached saturation for the bounded question: every retained source adds one of the same convergent control families — data integrity attributes, electronic records/audit trails, risk-based assurance, lifecycle traceability, AI context/performance evidence, or QMS accountability. The remaining uncertainty is domain- and jurisdiction-specific applicability, which the new reference must explicitly route to QA/regulatory owners rather than resolve itself.
