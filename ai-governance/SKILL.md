---
name: ai-governance
description: >-
  Design and operate an organization's AI governance system: define governance
  principles, operating models and decision rights, risk frameworks, lifecycle
  gates, and fairness, transparency, privacy, security, regulatory, and
  board-oversight controls. Use when standing up a governance program, tiering
  AI use-case risk, reviewing an LLM or agent system for governance and safety
  gaps, mapping a regulation to a compliance plan, scoring governance maturity,
  or preparing board reporting. For regulated life-sciences use cases, also cover GxP,
  ALCOA+, data integrity, electronic records, validation/assurance, and QMS interfaces.
  Do not use for interpreting regulations as legal
  advice (route to legal-strategy), data-governance mechanics
  (data-architect/data-engineering), or implementing application security
  (secure-software-engineering).
license: MIT
compatibility: Agent-agnostic methodology; no external services, APIs, or runtime dependencies. The two scripts are Python 3 standard-library only.
metadata:
  tags: ai-governance, responsible-ai, model-risk, ai-risk-management, governance-operating-model,
    ai-governance-principles, lifecycle-gates, fairness, transparency, privacy,
    llm-security, ai-regulation, ai-compliance, board-oversight, third-party-risk,
    governance-maturity, use-case-risk-tiering, model-cards, ai-audit, ai-oversight
---

# AI Governance

AI governance is the system an organization uses to decide, before a model is built and while it
runs, who is accountable for an AI system, what risk it is allowed to carry, what evidence must
gate each lifecycle stage, and how the organization reports and audits that posture. This skill
teaches an agent to reason about and operate that system: it is a methodology skill, not a tool
manual and not legal or security advice.

## Scope: What This Skill Owns

| You own | You don't own |
|---------|---------------|
| Governance principles and how they translate into policy and controls | Drafting or opining on legal interpretation of a regulation |
| The governance operating model: councils, stewards, decision rights, RACI, federated vs. centralized | Data-platform mechanics, pipelines, and lineage tooling internals |
| Risk frameworks: NIST AI RMF, ISO/IEC 42001 & 23894, model-risk tiering, risk registers | Implementing authentication, authorization, or vulnerability fixes |
| Lifecycle stage gates across ideation, build, evaluate, deploy, monitor, retire | CI/CD pipeline and deployment-gate configuration |
| Fairness, bias, transparency, explainability, and accountability controls | Product portfolio/roadmap governance cadences |
| Privacy and data governance for training and operational data | Capital allocation, org structure, or M&A governance |
| GxP AI governance overlay: ALCOA+, data integrity, electronic records, risk-based assurance, QMS interfaces | Legal applicability determinations, validation protocols, SOPs, or quality-system operation |
| LLM/agent safety: prompt injection, excessive agency, red-teaming, supply chain | Host-level or application-level security scanning |
| Regulatory landscape and compliance mapping (as guidance, not advice) | Legal drafting, regulatory filings, or attorney-client work product |
| Third-party and model due diligence, board reporting, audit | Any authoritative statement of "your system is compliant" |

This is a **prevention-and-operations** methodology: it gives the agent frameworks, decision
models, and controls to design and run governance, not a claim that a system is compliant or
safe. For every engagement, record the operating model, the risk tier, the evidence that gated
each stage, and the accountable owner of each accepted exception.

## When To Use

Load this skill to answer "how should we govern this AI system?" — standing up or maturing a
governance program, tiering use-case risk, designing the operating model and decision rights,
reviewing an LLM/agent system for governance and safety gaps, mapping a regulation to a
compliance/control plan, scoring governance maturity, or preparing board-level reporting.

## Reference Files (load on demand, one per task)

Progressive disclosure: load only the reference relevant to the current question.

| Load when | Reference |
|---|---|
| Framing what AI governance is and its principles; governance vs. compliance vs. risk | [references/foundations-and-principles.md](references/foundations-and-principles.md) |
| Designing the operating model, councils, stewards, decision rights, RACI, maturity, culture | [references/governance-operating-model.md](references/governance-operating-model.md) |
| Applying NIST AI RMF, ISO/IEC 42001 & 23894, model-risk tiering, inherent vs. residual risk | [references/risk-management-and-frameworks.md](references/risk-management-and-frameworks.md) |
| Placing stage gates across ideation, data, build, evaluate, deploy, monitor, retire | [references/ai-lifecycle-governance.md](references/ai-lifecycle-governance.md) |
| Fairness metrics and their limits, bias sources, trade-offs, algorithmic justice | [references/fairness-bias-accountability.md](references/fairness-bias-accountability.md) |
| Explainability (XAI) methods, when explanation is required, disclosure, auditability | [references/transparency-and-explainability.md](references/transparency-and-explainability.md) |
| Training/operational data governance, ownership, lineage, quality, consent, PETs | [references/privacy-and-data-governance.md](references/privacy-and-data-governance.md) |
| AI used in GLP, GCP, GMP, GDP, or pharmacovigilance contexts; ALCOA+, data integrity, electronic records, audit trails, validation/assurance, and QMS interfaces | [references/gxp-and-data-integrity.md](references/gxp-and-data-integrity.md) |
| Trust boundaries, prompt injection, excessive agency, hallucination, supply chain, red-teaming | [references/llm-and-agent-security.md](references/llm-and-agent-security.md) |
| Current law by jurisdiction, compliance mapping, enforcement, horizon scanning | [references/regulatory-landscape.md](references/regulatory-landscape.md) |
| Vendor/model due diligence, supply chain, board reporting, metrics, audit | [references/procurement-third-party-and-board-oversight.md](references/procurement-third-party-and-board-oversight.md) |
| Tracing any idea to its informing books and research notes; bibliography | [references/source-index.md](references/source-index.md) |

## Templates (fillable)

Use these to turn the methodology into working artifacts.

| Use when | Template |
|---|---|
| Standing up the governance council and its terms of reference | [templates/governance-charter.md](templates/governance-charter.md) |
| Registering a use case and classifying it at intake | [templates/use-case-intake-form.md](templates/use-case-intake-form.md) |
| Running a NIST-aligned risk assessment and tiering worksheet | [templates/model-risk-assessment.md](templates/model-risk-assessment.md) |
| Documenting a released model: intended use, data, performance, fairness, limitations | [templates/model-card.md](templates/model-card.md) |
| Conducting vendor/model supply-chain due diligence | [templates/third-party-due-diligence.md](templates/third-party-due-diligence.md) |
| Preparing executive/board AI-governance reporting | [templates/board-ai-governance-report.md](templates/board-ai-governance-report.md) |

## Scripts

Executable, flag-driven, stdlib-only Python CLIs with tests. Both accept a JSON input path and emit
deterministic output; `--json` prints one JSON object on stdout; `--dry-run` previews without
changing anything. Exit 0 on success; the maturity scorer also exits 1 on a critical posture, and both scripts exit 1 on input errors.

| Use when | Script |
|---|---|
| Scoring an organization's governance maturity from dimension scores (1-5); emits maturity level + gaps | [scripts/governance-maturity.py](scripts/governance-maturity.py) |
| Classifying an AI use case into a risk tier and its required controls | [scripts/use-case-risk-tier.py](scripts/use-case-risk-tier.py) |
| Verifying the maturity scorer (unit + behavior tests) | [scripts/test_governance_maturity.py](scripts/test_governance_maturity.py) |
| Verifying the risk-tier classifier (unit + behavior tests) | [scripts/test_use_case_risk_tier.py](scripts/test_use_case_risk_tier.py) |

## Evaluation and Configuration

- **Eval manifest:** [evals/evals.json](evals/evals.json) holds the output-quality cases (operating
  model design, use-case risk tiering, LLM-app governance review, fairness/accountability review,
  regulatory compliance mapping, board governance reporting, and GxP/data-integrity governance)
  used to grade this skill.
- **Configuration:** [pytest.ini](pytest.ini) overrides the repository's root coverage settings so
  the subprocess-based skill tests run cleanly; do not add a second override.
- **Entry points:** this [SKILL.md](SKILL.md) is the router; [README.md](README.md) is the
  human-facing overview for people evaluating whether to install the skill.

## When Not To Use

Do not load this skill for work that belongs to a neighbor methodology or to execution:

- **Regulatory/legal strategy.** Interpreting what a law or regulation *means*, structuring
  compliance legal risk, or preparing legal positions is `legal-strategy` work. This skill maps
  obligations to controls and records a defensible governance posture; it does not opine on the
  law. Prefer `legal-strategy` when the ask is legal interpretation, and return here to turn the
  resulting obligations into a control plan.
- **Product operations and governance.** Recurring product decision cadences (intake, portfolio,
  roadmap, experiment, launch, lifecycle reviews) with evidence standards belong to
  `product-operations-and-governance`, not to this skill. This skill governs the *AI system's risk
  and accountability*, not the product portfolio cadence.
- **Data-governance mechanics.** Building data catalogs, lineage pipelines, or platform storage
  internals is `data-architect` / `data-engineering` work. This skill consumes data governance as
  a control input but does not operate the data platform.
- **Implementation-time security.** Writing authentication, authorization, input validation, or
  dependency hardening for an application is `secure-software-engineering` work. This skill sets
  the AI governance and safety controls and the risk tier; it does not implement the security
  mechanisms.
- **Legal, financial, or security advice.** Nothing in this skill is legal, financial, or security
  advice. Regulatory and standards material must be re-verified against primary sources at the
  time of use.
- **Single one-off decisions.** If you only need to make one decision (not design the recurring
  governance system), use `adr-authoring` or `product-methodology` for a decision record instead.

## Related Skills (routing)

| When you need... | Route to |
|---|---|
| Regulatory and board-legal strategy, legal interpretation | [legal-strategy](../legal-strategy/SKILL.md) |
| Data-governance mechanics: catalogs, lineage, platform internals | [data-architect](../data-architect/SKILL.md) or [data-engineering](../data-engineering/SKILL.md) |
| Implementing application and system security controls | [secure-software-engineering](../secure-software-engineering/SKILL.md) |
| Recurring product decision cadences and evidence standards | [product-operations-and-governance](../product-operations-and-governance/SKILL.md) |
| A single durable architectural decision record | [adr-authoring](../adr-authoring/SKILL.md) |
