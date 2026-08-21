# AI Governance: Source Index and Provenance

This index records the provenance of every reference in the `ai-governance` skill. It
exists so that anyone can trace any idea back to its informing sources — the twelve
copyrighted books in the mission's ebook library and the five current research notes that
de-stale those books — and so that readers can be confident about how the material was
created.

## Attribution invariant: paraphrase and synthesis at the idea level

Every sentence in every reference of this skill that describes a book is an **original
paraphrase or synthesis of ideas** — never a verbatim reproduction. Several of the source
books carry explicit "all rights reserved, no part may be reproduced" notices, so the
skill authors deliberately did **not** copy book prose, contiguous passages, or near-verbatim
sentences. Instead, each reference:

- **Paraphrases** the underlying idea in fresh words, or
- **Synthesizes** ideas drawn from multiple books and the current research notes into new,
  original framing that belongs to this skill.

This is **idea-level attribution**: we attribute the origin of an *idea* (e.g., "governance
must span the full model lifecycle") to the book or research note that informed it, without
claiming to reproduce the source's wording. Where a book has aged past its publication
date — most visibly in the regulatory and standards areas — the reference is de-staled
against a current research note, and the note (not the book) is treated as authoritative on
the current state. Research notes may be summarized and cited, but large verbatim blocks
are not pasted into any reference.

Nothing in this skill is legal, financial, or security advice. Regulatory, standards, and
security material should be re-verified against primary sources at the time of use.

## The twelve reference files

The `ai-governance` skill ships twelve reference files under `references/`. The table below
names all eleven and maps each to its informing sources: book short names (see the
bibliography) and the mission research notes (see below). The book short names are the
canonical identifiers used consistently across the skill.

| Reference file | Focus | Informing sources |
|---|---|---|
| `foundations-and-principles.md` | What AI governance is; the core principles (fairness, accountability, transparency, privacy, safety, human oversight); governance vs. compliance vs. risk | Responsible AI in the Enterprise; Introduction to Responsible AI; Beyond the Algorithm; Responsible AI: Best Practices; research-standards.md; research-org-board-governance.md |
| `governance-operating-model.md` | Six-step operating model, councils, stewards, decision rights, RACI, federated vs. centralized, maturity, culture, charter | Designing Data Governance from the Ground Up; Data Governance Handbook; research-org-board-governance.md |
| `risk-management-and-frameworks.md` | NIST AI RMF (govern/map/measure/manage), ISO/IEC 42001 & 23894, model-risk tiering, risk registers, inherent vs. residual | Responsible AI in the Enterprise; Platform and Model Design for Responsible AI; research-standards.md |
| `ai-lifecycle-governance.md` | Stage gates across ideation, data, build, evaluate, deploy, monitor, retire; model inventory, lineage, drift, incident response | Platform and Model Design for Responsible AI; Designing Data Governance from the Ground Up; Data Governance Handbook; research-technical-controls.md |
| `fairness-bias-accountability.md` | Fairness metrics and their limits, algorithmic justice, bias sources, trade-offs, accountability, model cards | AI Fairness; Introduction to Responsible AI; Responsible AI: Best Practices; research-technical-controls.md |
| `transparency-and-explainability.md` | Explainability (XAI) methods, when explanation is required, disclosure, human-AI interaction, auditability | Responsible AI in the Enterprise; Platform and Model Design for Responsible AI; Introduction to Responsible AI |
| `privacy-and-data-governance.md` | Training and operational data governance, ownership, lineage, quality, consent, minimization, retention, privacy-enhancing techniques | Designing Data Governance from the Ground Up; Data Governance Handbook; Platform and Model Design for Responsible AI; research-regulatory.md; research-technical-controls.md |
| `llm-and-agent-security.md` | Trust boundaries, prompt injection, data exposure, hallucination, excessive agency, denial of service, supply chain, red-teaming | The Developer's Playbook for LLM Security; Beyond the Algorithm; research-llm-agent-security.md |
| `regulatory-landscape.md` | Current law by jurisdiction, compliance mapping, horizon scanning, enforcement | research-regulatory.md (authoritative); book regulatory chapters of Responsible AI in the Enterprise and Beyond the Algorithm as historical context only |
| `procurement-third-party-and-board-oversight.md` | Vendor and model due diligence, supply chain, board reporting, metrics, audit | The AI Product Manager's Handbook; Developing Cybersecurity Programs and Policies; research-org-board-governance.md |
| `gxp-and-data-integrity.md` | GxP AI governance, ALCOA+, data integrity, electronic records, audit trails, risk-based assurance, QMS interfaces | FDA, MHRA, PIC/S, WHO, EMA, ICH, ISPE; gxp-ai-governance-brief.md; gxp-ai-governance-log.md |
| `source-index.md` | This file: provenance, attribution, bibliography | All twelve books; all five research notes; GxP research artifacts (meta) |

## Research notes

Seven research notes, produced during the research foundation milestone, de-stale the books
against where AI governance stands today. They live in this skill's research directory and are cited by
short filename throughout the skill. All seven are used, with the two GxP artifacts informing the GxP reference:

- research-regulatory.md — current laws and enforcement across jurisdictions (EU AI Act,
  GDPR, US federal/state, UK, China, sectoral rules), the authoritative basis for
  `regulatory-landscape.md` and a de-staling input to `privacy-and-data-governance.md`.
- research-standards.md — NIST AI RMF and its Generative AI Profile, ISO/IEC 42001 and
  23894, IEEE and industry frameworks; informs `risk-management-and-frameworks.md` and
  `foundations-and-principles.md`.
- research-llm-agent-security.md — OWASP LLM Top 10, agentic risk, prompt-injection
  defenses, red-teaming, AI safety institutes; informs `llm-and-agent-security.md`.
- research-technical-controls.md — model and data cards, model inventories, monitoring,
  drift, audit trails, MLOps governance tooling; informs `ai-lifecycle-governance.md`,
  `fairness-bias-accountability.md`, and `privacy-and-data-governance.md`.
- research-org-board-governance.md — roles, governance councils, the Chief AI Officer,
  fiduciary duty, maturity models, third-party risk; informs `foundations-and-principles.md`,
  `governance-operating-model.md`, and `procurement-third-party-and-board-oversight.md`.

- gxp-ai-governance-brief.md and gxp-ai-governance-log.md — GxP, ALCOA+, data integrity, electronic records, validation/assurance, and QMS interfaces; inform `gxp-and-data-integrity.md`.

## Bibliography — the twelve source books

These are the twelve titles harvested for the skill, drawn from the mission's read-only
ebook library. All content derived from them is paraphrased and synthesized at the idea
level, as described above; no passages are reproduced. The books are listed by the short
name used across the skill.

### Primary (five)

1. **Responsible AI in the Enterprise** — the central operating book on governance, model
   risk, audit, compliance, the NIST AI RMF, maturity, and starter kit.
2. **Responsible AI: Best Practices for Creating Trustworthy AI Systems** — a pattern
   catalogue feeding the skill's control library, review checklists, and playbook.
3. **Designing Data Governance from the Ground Up** — the operating-model book: the six-step
   model, stewards, council, decision rights, roadmap, and lifecycle.
4. **Platform and Model Design for Responsible AI** — governance-as-architecture: risk
   assessment, privacy pipelines, MLOps, inventories, tiering, and lifecycle.
5. **The Developer's Playbook for LLM Security** — the LLM/agent security and
   deployment-control lane.

### Supporting (seven)

6. **AI Fairness** — conceptual and ethical depth: algorithmic justice, fairness metrics and
   their limits, and trade-offs.
7. **Beyond the Algorithm** — a landscape primer connecting governance to security, privacy,
   ethics, and law.
8. **Developing Cybersecurity Programs and Policies in an AI-Driven World** — governance
   infrastructure: policy, risk management, supply chain, privacy, and an AI-governance
   chapter.
9. **Data Governance Handbook** — data ownership, quality, lineage, and operations, with a
   regulated-financial-institution case study.
10. **Introduction to Responsible AI** — an onboarding primer on bias, transparency,
    privacy, and robustness.
11. **The AI Product Manager's Handbook** — the product-governance interface: lifecycle,
    third parties, metrics, and ethics.
12. **Practical Cybersecurity Architecture** — the control-environment architecture that
    surrounds AI systems.

## How to read this index

- To find where a book's ideas appear, scan the "Informing sources" column of the reference
  table for that book short name.
- To find which research note governs the current state of a topic, scan for the `research-*`
  filename.
- To understand why a book is sometimes treated as context rather than authority (e.g., the
  regulatory chapter of Responsible AI in the Enterprise), see the attribution invariant above:
  where obligations have moved past a book's publication date, the current research note is
  authoritative and the book is cited as historical context.

Each domain reference carries its own short "Synthesized from" footer repeating the
source-to-file mapping for that reference; this index is the consolidated, complete
record of attribution across the whole skill.
