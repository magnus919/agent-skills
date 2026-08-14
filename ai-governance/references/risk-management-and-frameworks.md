# AI Risk Management and Frameworks

This reference teaches the structured discipline of AI risk management: how an
organization identifies, assesses, prioritizes, and mitigates the risks its models can
produce. It explains the two most influential risk frameworks — the NIST AI Risk
Management Framework (RMF) and the ISO/IEC 42001 / 23894 pair — and covers the
concepts those frameworks rely on: inherent versus residual risk, model risk tiering,
and the risk register. It is an original synthesis of the ideas in *Responsible AI in
the Enterprise*, *Platform and Model Design for Responsible AI*, and current research on
standards and frameworks (see `research-standards.md`). Read it with
`foundations-and-principles.md` (which draws the governance-versus-risk-versus-compliance
distinction) and `governance-operating-model.md` (which assigns the roles that own these
risks). It is not legal advice, and framework details should always be confirmed against
the governing bodies' current releases.

## Why Structured AI Risk Management Exists

The starting point of AI risk management is the recognition that a model can harm the
business, its customers, and its reputation in ways that ordinary software rarely does.
*Responsible AI in the Enterprise* lists concrete failure examples: an automated resume
screener that filters candidates along biased lines, a manufacturing defect detector
that degrades as the model drifts, and a credit model that refuses loans on the basis of
an applicant's employment type. Each is a plausible, ordinary deployment that can go
quietly wrong.

Risk management is the ongoing, analytical practice of making those possibilities
visible and tractable: identifying what could go wrong, assessing how bad it could be
and how likely, prioritizing the risks worth acting on, and mitigating them. It differs
from compliance, which only asks whether you meet the current letter of the law. As the
mission's standards research notes, the leading frameworks are explicitly risk-based
rather than rule-based for exactly this reason: the regulatory landscape is still
stabilizing, so an organization that anchors on risk stays ahead of whatever specific
laws arrive rather than reacting to each one.

Structured AI risk management typically hangs on four mechanisms, all of which this
reference explains below:

- **A vocabulary and a workflow** for naming, scoring, and escalating risk (the
  frameworks and the register).
- **A distinction between inherent and residual risk**, which drives how much mitigation
  a given model deserves.
- **Model risk tiering**, which routes each model in the inventory to the right depth of
  review.
- **A risk register** that is owned, reviewed, and kept current rather than filed away.

## Inherent vs. Residual Risk

Every model arrives with risk baked in, and every control the organization applies reduces
that starting risk. Keeping the two apart is what makes prioritization honest.

- **Inherent risk** is the level of risk a model would pose with no controls, validation,
  or mitigation applied — the danger present simply because the model exists and is used
  in a particular context. *Platform and Model Design for Responsible AI* observes that
  inherent risk grows from the absence or age of validation, unaddressed known issues, and
  the model's own complexity and reach.
- **Residual risk** is the risk that remains after the organization's controls,
  validation, monitoring, and safeguards are applied. It is the realistic risk the
  business actually carries day to day.

The gap between the two is the value of the control environment. Good practice assesses
both: you need to know the inherent risk to decide how much control is proportionate, and
you need the residual risk to know whether you are actually where you intend to be. If the
residual risk still exceeds the organization's appetite, the model should not ship as-is —
or the controls must be strengthened.

| Concept | What it captures | Question it answers |
|---|---|---|
| Inherent risk | Risk with no controls applied | "How dangerous is this model in its context, unmitigated?" |
| Residual risk | Risk after controls | "What risk are we actually carrying today?" |
| Risk appetite | The amount of risk the org accepts | "Is the residual risk acceptable?" |

## Model Risk Tiering

Not every model deserves the same depth of scrutiny, and applying the heaviest process to
everything is wasteful while applying the lightest to everything is reckless. Model risk
tiering is the practice of classifying each model in the inventory into a risk tier so the
governance effort matches the stakes.

*Platform and Model Design for Responsible AI* describes tiering as the industry's way of
making model risk comparable across a portfolio: it identifies and differentiates the risk
one model's use presents relative to others, weighing factors such as volume, context of
use, and financial or customer impact. A common arrangement sorts models into high-,
medium-, and low-risk tiers, each with its own depth of review, validation, and monitoring.
The book stresses several principles for building a tiering scheme:

- **Expert judgment drives it.** The classification tool quantifies and orders risk, but
  the priorities behind the weights are business and functional decisions, not pure math.
- **It should be simple, transparent, and consistent**, producing reliable and broadly
  understandable rankings across the whole inventory rather than opaque per-model scores.
- **It weights inherent risk over residual risk.** Tiering a model by how risky it would
  be unmitigated ensures the review depth tracks the true stakes, not just what a strong
  control environment currently hides.
- **It supports correlation across the portfolio**, so teams can see how risk clusters by
  business unit, entity, or model family.

A concrete tiering rule set is embedded in the `model-risk-assessment.md` template, and the
`use-case-risk-tier.py` script automates a defensible default classification from
structured inputs. Regardless of the exact weights, the tiering decision should be recorded
for each model so the reasoning is auditable and consistent over time.

## The Risk Register

A risk register is the central ledger of identified AI risks and the actions against them.
Each entry captures the risk, its source, who owns it, its likelihood and impact (and hence
a score), the mitigating controls in place, the residual score after those controls, and
the status of any planned response. A register is only useful if it is:

- **Owned.** Someone is accountable for keeping it current and for acting on its findings.
- **Reviewed.** It is revisited on a cadence and whenever a significant model or use case
  is added, so it reflects the live portfolio rather than a one-time snapshot.
- **Linked to escalation.** Entries above a threshold route into the tiered review and the
  governance council described in `governance-operating-model.md`.

*Responsible AI in the Enterprise* describes risk registers, heat maps, and scoring
models as complementary instruments for ranking risks by their likelihood and impact, so
that mitigation effort lands where it counts. The use-case intake flow
(`use-case-intake-form.md`) feeds new risks into the register, and the register in turn
informs board reporting on the aggregate risk profile.

## The NIST AI Risk Management Framework

> **Verify against current NIST releases at use time.** The AI RMF is under active
> revision and sector profiles (for example, critical-infrastructure and cybersecurity
> guidance) are still being added, so the exact structure, category lists, and profile set
> below may have moved by the time you read this. Confirm the current version, its
> Generative AI Profile, and any relevant sector profile on the NIST site before applying
> them.

The NIST AI RMF is a voluntary, consensus-built framework (first released January 2023)
that organizes AI risk management into four functions. As *Responsible AI in the
Enterprise* explains, it is deliberately risk-based, resource-efficient, and innovation
friendly: it offers a shared vocabulary, taxonomy, and set of target outcomes instead of
forcing uniform one-size-fits-all rules, and it is built to layer onto an organization's
existing risk management rather than stand in for it. The four functions are:

- **Govern** — the cross-cutting governance function that informs and runs through the
  other three: cultivating a risk-management culture, establishing roles and
  responsibilities, and embedding accountability into AI design, development, and use.
- **Map** — establishing the context of the AI system: who the actors are, what the system
  is for, and where its risks and benefits arise across the life cycle.
- **Measure** — identifying and applying metrics to evaluate and assess risks, including
  performance, trustworthiness, and bias-related measures.
- **Manage** — prioritizing, responding to, and mitigating the measured risks, then
  monitoring outcomes and feeding back into the system.

Each function breaks down into categories and subcategories that resolve into concrete
actions and outcomes. NIST stresses that the functions should be carried out continuously
and throughout the AI life cycle, incorporating multidisciplinary perspectives, rather
than as a one-time exercise.

The framework also calls out what makes AI risk *different* from traditional software risk
— a point the book emphasizes and that still shapes the field. AI-specific risks include
data representation and ground truth problems, harmful bias, data dependency, behavior
changes during training, detachment from training context, opacity, unpredictable failure
modes, and the attack surface introduced by pretrained models and third-party components.
Because privacy and cybersecurity frameworks (such as the NIST Cybersecurity and Privacy
frameworks) do not fully cover these, the AI RMF exists to close that gap.

NIST has since issued a companion document, the Generative AI Profile (labeled
NIST-AI-600-1, July 2024), which maps the four functions onto the distinctive hazards of
generative models: the ease of fabricating plausible synthetic output, confabulation,
degraded information integrity, and fresh avenues for misuse. As of the mission's research
(mid-2026), NIST continues to add sector profiles and revise the RMF, which is why this
section must be re-verified against current NIST releases.

## ISO/IEC 42001 and ISO/IEC 23894

On the international standards side, the key pair is ISO/IEC 42001 and ISO/IEC 23894,
both published under the JTC 1/SC 42 joint technical committee. They play complementary
roles, as the mission's research makes clear.

- **ISO/IEC 42001:2023** is the world's first management-system standard centered on
  artificial intelligence. It lays out the requirements for setting up, running, and
  steadily refining an AI Management System (AIMS) inside any organization that builds,
  sells, or relies on AI-based products or services. Following the Plan-Do-Check-Act cycle
  common to management-system standards, it hands the organization a disciplined mechanism
  for defining AI policies and targets, handling risks and opportunities, and showing
  responsible use — all while keeping innovation and control in balance. It has become a
  leading certification target precisely because it is a complete management system rather
  than just guidance.
- **ISO/IEC 23894:2023** is a guidance document rather than a full management-system
  standard. It advises organizations on handling AI-specific risk and on weaving risk
  management into their AI activities, and it can be tailored to any organization and
  situation.

In practice the two work in tandem: an organization can apply 23894 to understand and
evaluate AI-specific risk, then fold that discipline into the larger management system that
42001 calls for. Where NIST supplies a widely used risk structure in plain language, ISO
42001 supplies a certifiable management system and 23894 supplies the risk process that
feeds it. Many organizations map the two families onto one another — aligning NIST's
four functions with the risk process of ISO 23894 and meeting both through an ISO 42001-style
system — rather than treating them as competing choices.

## Choosing and Combining Frameworks

The frameworks are voluntary and overlapping, not a single compliance target, so the
mission's research recommends adopting a framework-based approach rather than chasing any
one document. A workable posture is:

- **Choose a primary structure** — commonly the NIST AI RMF or ISO/IEC 42001 — as the spine
  of the program.
- **Layer a risk standard** such as ISO/IEC 23894 for the detailed risk-management process.
- **Use principles** (such as the OECD principles) as the values baseline that keeps the
  structure honest.
- **Track the updates**, because the standards themselves are still stabilizing — the AI
  RMF is under revision and ISO is steadily expanding the AI standard family.

Because the frameworks are living documents, the risk-management program should re-verify
its assumptions on a schedule rather than treating a framework version as fixed. This is
also why the reference files and templates in this skill describe the *discipline* (what to
assess, how to score, how to record) in a way that survives changes to any single
framework's category list.

## Running Risk Management with the Rest of the Skill

Structured risk management is the connective tissue of the whole skill:

- **Principles** set what the organization values; risk management makes the consequences
  of those values measurable (`foundations-and-principles.md`).
- **The operating model** assigns who owns and escalates each risk
  (`governance-operating-model.md`).
- **The life cycle** gates when risk assessments must be refreshed, from ideation through
  retirement (`ai-lifecycle-governance.md`).
- **Fairness, transparency, privacy, and security** each contribute concrete risk measures
  and mitigations (`fairness-bias-accountability.md`, `transparency-and-explainability.md`,
  `privacy-and-data-governance.md`, `llm-and-agent-security.md`).
- **The board and third-party tiers** consume the aggregate risk picture for oversight
  (`procurement-third-party-and-board-oversight.md`).

Use the `model-risk-assessment.md` template to run a NIST-aligned assessment and tiering on
a single model, the `use-case-intake-form.md` template to route a new use case into the
register, and the `use-case-risk-tier.py` script to compute a defensible default tier from
structured inputs. Record the resulting inherent and residual scores in the register and
feed the aggregate to the governance council and board.

## Where to Go Next

- **`foundations-and-principles.md`** — why risk management is the substrate of governance.
- **`governance-operating-model.md`** — the roles and councils that own and escalate risk.
- **`ai-lifecycle-governance.md`** — the stage gates where risk assessments are refreshed.
- **`procurement-third-party-and-board-oversight.md`** — how the aggregate risk picture
  reaches the board and governs procured models.

---

### Synthesized from

This reference synthesizes (never reproduces) ideas from *Responsible AI in the Enterprise*
and *Platform and Model Design for Responsible AI*. Current context on the NIST AI RMF,
its Generative AI Profile, ISO/IEC 42001 and 23894, and the evolving standards landscape is
drawn from the mission research note `research-standards.md`. All prose is an original
paraphrase and synthesis of the ideas in these sources; idea-level attribution is
consolidated in `source-index.md`. Framework details must be verified against the
governing bodies' current releases at use time.
