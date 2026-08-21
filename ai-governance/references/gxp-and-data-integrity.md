# GxP AI Governance and Data Integrity

Use this reference when an AI system creates, transforms, analyzes, or influences GxP-relevant data, records, processes, decisions, or regulatory submissions. It adds a GxP quality-system overlay to the general AI governance method.

This is governance guidance, not legal advice, a validation package, a QMS replacement, or a declaration that a system is compliant. Confirm applicability and current requirements with the organization's QA/quality unit, regulatory, validation/assurance, privacy, security, and legal owners.

## The governing boundary

General AI governance answers:

- Who owns the AI system and its risks?
- What is the intended use and risk tier?
- What evidence gates development, release, monitoring, change, and retirement?
- How are model, data, supplier, security, fairness, and performance risks managed?

The GxP quality system additionally answers:

- Does the system create, modify, transmit, retain, or rely on regulated records or data?
- Which GxP domain and jurisdiction apply: GLP, GCP, GMP, GDP, or pharmacovigilance?
- What data-integrity attributes and electronic-record controls are required?
- What validation or computer-software-assurance evidence is proportionate to risk?
- How do deviations, CAPA, change control, training, periodic review, and quality-unit decisions operate?

Do not create a parallel AI bureaucracy. Connect AI governance decisions to the authoritative QMS, controlled records, validation repository, supplier-quality process, and incident/deviation system.

## GxP applicability screen

At intake, record:

- GxP domain(s), product/process, jurisdiction, and regulated business owner.
- Whether the AI system is used in discovery, clinical research, laboratory work, manufacturing, quality control, distribution, safety/pharmacovigilance, or regulatory submission support.
- Whether it creates, modifies, interprets, approves, transmits, or stores GxP-relevant records or data.
- Whether an AI output can affect patient safety, product quality, batch disposition, study integrity, subject safety, or a regulatory decision.
- System boundary: model, prompts, retrieval sources, data pipelines, human review, downstream systems, hosted services, and retained records.
- Named process owner, system owner, data owner, QA/quality-unit reviewer, validation/assurance lead, and AI-governance reviewer.
- Applicable internal procedures and external requirements, with a primary-source verification owner and review date.

If the system does not touch GxP-relevant processes or records, document why the GxP overlay is out of scope instead of silently assuming it.

## ALCOA+ data-integrity review

Use ALCOA+ as a control review, not as a slogan. For every GxP-relevant record or dataset, identify the control and evidence for each attribute:

| Attribute | Governance question |
|---|---|
| Attributable | Can the person, system, or agent responsible for each action be identified? |
| Legible | Can authorized users read and interpret the record throughout its retention period? |
| Contemporaneous | Is the record captured when the activity occurs, with reliable time handling? |
| Original | Is the source record preserved, or is the relationship to the original demonstrable? |
| Accurate | Are the record, transformation, calculation, and output correct and checked? |
| Complete | Are relevant data, metadata, failed runs, exceptions, changes, and audit-trail events retained? |
| Consistent | Are sequence, timestamps, formats, units, and meanings coherent across systems? |
| Enduring | Will the record remain intact and usable for the required retention period? |
| Available | Can authorized users retrieve the record, metadata, and audit history when needed? |

For AI, extend the review across the full chain: source data, labeling or curation, prompt/context, retrieval results, model/version, parameters and configuration, output, human review, downstream action, and retained evidence. A polished answer is not an acceptable substitute for the underlying record.

## Electronic records, signatures, and audit trails

When the system creates or relies on regulated electronic records, the gate must explicitly assess the applicable electronic-record and signature controls. Do not infer applicability from the presence of a model alone.

Confirm, as applicable:

- Validation or assurance evidence supports the intended use and critical functions.
- Access is limited to authorized individuals and service identities; privileges are reviewed.
- Records are protected against unauthorized alteration and remain accurately retrievable.
- Audit trails capture time-sequenced creation, modification, deletion, and relevant configuration or model changes.
- Audit trails are enabled, protected, periodically reviewed, and linked to investigations or deviations when needed.
- Electronic signatures identify the signer, bind the signature to the record, and cannot be repudiated casually.
- Time sources, time zones, clock changes, and synchronization are controlled and documented.
- The retention, archival, backup, restoration, export, and readability plan covers records plus relevant metadata and audit history.
- AI-generated or AI-assisted content is distinguishable from human review and approval where the process requires that distinction.

These are control prompts, not a legal conclusion about 21 CFR Part 11, EU GMP Annex 11, or another regime. Have the responsible quality and regulatory functions determine which requirements apply.

## Risk-based validation and assurance

Use a documented, risk-based validation or computer-software-assurance decision. The question is not “is AI validated?” in the abstract. The question is whether the system is fit for its intended GxP use and whether the evidence is proportionate to the risk.

The evidence plan should state:

1. **Intended use and context of use.** What the system may and may not do, who uses it, and what decisions it can influence.
2. **Criticality and risk.** Impact on patient safety, product quality, subject rights, study integrity, data integrity, and regulatory submissions.
3. **Requirements and acceptance criteria.** Functional, data-integrity, performance, security, human-oversight, and record-retention requirements agreed before testing.
4. **Traceability.** Links among requirements, risk controls, tests, results, deviations, approvals, and the released system/model/data versions.
5. **Test evidence.** Representative data, boundary and failure cases, relevant subgroups, abnormal inputs, uncertainty, fallback behavior, and human-review effectiveness.
6. **Release decision.** Named approver, QA/quality-unit involvement where required, unresolved deviations, residual risk, and operating restrictions.
7. **Change boundaries.** What changes require impact assessment, regression testing, revalidation or re-assurance, retraining review, or a new approval.
8. **Retirement and continuity.** Record retention, reproducibility, migration, rollback, decommissioning, and access to historical outputs and evidence.

For probabilistic, adaptive, or generative systems, add controls for nondeterminism, model/provider changes, prompt and retrieval changes, data drift, version pinning, output review, and the risk that a vendor changes behavior without the organization's approval.

## GxP overlay on AI lifecycle gates

| Gate | Minimum GxP questions and evidence |
|---|---|
| Intake / ideation | GxP applicability, domain, intended use, system boundary, criticality, owners, initial risk, and QMS route |
| Data | ALCOA+ review, provenance, authorized use, source and transformation history, quality, representativeness, retention, and access controls |
| Build / configure | Controlled versions of code, model, prompts, retrieval, data, configuration, and infrastructure; documented deviations and decisions |
| Evaluate / validate | Approved requirements, risk-based assurance plan, traceability, representative and edge-case testing, failure handling, human oversight, and evidence review |
| Release | QA/quality-unit decision as required, approved residual risk, complete records and audit trails, training, SOP/work-instruction updates, monitoring, rollback, and incident/deviation routes |
| Operate / monitor | Performance and data-integrity monitoring, audit-trail review, drift and vendor-change monitoring, periodic review, access review, incidents, deviations, CAPA, and escalation |
| Change | Impact assessment, change control, version and provenance update, regression/revalidation decision, approvals, and retained comparison evidence |
| Retire | Controlled decommissioning, retention and retrieval, archival integrity, migration or destruction evidence, supplier exit, and closure of open risks or CAPA |

## QMS and accountability interfaces

The governance record should identify which system owns each decision:

| Decision or event | Primary accountable function | AI-governance contribution |
|---|---|---|
| GxP applicability and process impact | Process owner with QA/quality unit | Ensure AI use case, boundaries, and risk are recorded |
| Validation/assurance strategy | Validation/assurance lead and system owner | Set AI-specific evidence and change questions |
| Data integrity controls | Data owner, system owner, and QA | Apply ALCOA+ across data and model lineage |
| Release for regulated use | Authorized quality and business approvers | Confirm governance gates and residual-risk record |
| Deviation, incident, or suspected integrity failure | QMS/quality process owner | Escalate AI-specific evidence and preserve affected artifacts |
| CAPA and change control | QMS/quality process owner | Ensure model, data, prompt, vendor, and configuration changes are in scope |
| Supplier/model due diligence | Procurement and supplier quality | Require provenance, audit rights, change notification, service continuity, and evidence access |
| Periodic review | System/process owner with QA | Recheck intended use, performance, integrity, access, drift, and changes |

## Supplier and hosted-model controls

For third-party models, hosted APIs, retrieval services, labeling vendors, or cloud systems, document:

- Model, provider, service, and dependency identity, version, location, and change-notification mechanism.
- Provider evidence about development data, evaluation, limitations, security, availability, incident handling, and business continuity.
- Contractual rights and practical ability to obtain records, audit trails, logs, evidence, and timely incident information.
- How provider updates, model substitutions, prompt changes, safety-filter changes, outages, and data-location changes trigger impact assessment.
- Whether the service permits retention, deletion, access restriction, and export of GxP-relevant prompts, inputs, outputs, metadata, and audit history.
- Exit, rollback, migration, and record-retention plans that do not depend on indefinite vendor availability.

## Verification checklist

- [ ] GxP domain, jurisdiction, intended use, and system boundary are documented.
- [ ] Named process, system, data, quality, validation, and AI-governance owners exist.
- [ ] ALCOA+ review covers source data through retained AI output and human action.
- [ ] Electronic-record, signature, audit-trail, time, access, and retention controls are assessed where applicable.
- [ ] Risk-based validation/assurance strategy and acceptance criteria were approved before testing.
- [ ] Model, data, prompt, retrieval, configuration, and provider versions are traceable.
- [ ] Testing covers representative use, failure modes, uncertainty, generalizability, and human oversight.
- [ ] Release, monitoring, change, deviation/CAPA, periodic-review, rollback, and retirement routes are connected to the QMS.
- [ ] Supplier changes and evidence-access limitations are controlled.
- [ ] Current primary sources and internal procedures were re-verified by the responsible functions.

## Primary sources and implementation references

Accessed 2026-08-20 UTC. Re-verify current versions and applicability at use time.

- FDA, [Data Integrity and Compliance With Drug CGMP](https://www.fda.gov/media/119267/download)
- FDA, [Part 11, Electronic Records; Electronic Signatures — Scope and Application](https://www.fda.gov/regulatory-information/search-fda-guidance-documents/part-11-electronic-records-electronic-signatures-scope-and-application)
- eCFR, [21 CFR Part 11](https://www.ecfr.gov/current/title-21/chapter-I/subchapter-A/part-11)
- MHRA, [Guidance on GxP Data Integrity](https://www.gov.uk/government/publications/guidance-on-gxp-data-integrity)
- PIC/S, [PI 041-1 Guidance on Data Integrity](https://picscheme.org/docview/4234)
- WHO, [TRS 1033 Annex 4: Guideline on Data Integrity](https://www.who.int/docs/default-source/medicines/norms-and-standards/guidelines/inspections/trs1033-annex4-guideline-on-data-integrity.pdf)
- EMA, [Guideline on Computerised Systems and Electronic Data in Clinical Trials](https://www.ema.europa.eu/en/documents/regulatory-procedural-guideline/guideline-computerised-systems-and-electronic-data-clinical-trials_en.pdf)
- EMA, [Reflection Paper on AI in the Medicinal Product Lifecycle](https://www.ema.europa.eu/en/documents/scientific-guideline/reflection-paper-use-artificial-intelligence-ai-medicinal-product-lifecycle_en.pdf)
- FDA, [AI for Drug Development](https://www.fda.gov/about-fda/center-drug-evaluation-and-research-cder/artificial-intelligence-drug-development)
- ICH, [Q9(R1) Quality Risk Management](https://database.ich.org/sites/default/files/ICH_Q9(R1)_Guideline_Step4_2022_1219.pdf)
- ISPE, [GAMP 5 Guide, 2nd Edition](https://ispe.org/publications/guidance-documents/gamp-5-guide-2nd-edition)
