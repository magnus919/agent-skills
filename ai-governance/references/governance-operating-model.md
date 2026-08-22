# AI Governance Operating Model

This reference teaches the machinery that turns governance principles into a working
system: the six-step operating model, the councils and stewards that carry it, how decision
rights are assigned and made explicit (including RACI), how to choose between federated and
centralized structures, how to gauge maturity, and the culture that makes the whole thing
hold together. It is an original synthesis of the ideas in *Designing Data Governance from
the Ground Up*, the *Data Governance Handbook*, and current research on organizational and
board governance (see research-org-board-governance.md). Read it alongside
`foundations-and-principles.md`, which explains *why* governance matters; this file explains
*how to run it*. It is not legal advice.

## What a Governance Operating Model Is

A governance operating model is the concrete arrangement of roles, bodies, and decision
rules an organization uses to run governance day to day, as distinct from the principles
themselves. Principles tell you *what you value*; the operating model tells you *who gets to
decide, who must be consulted, who does the work, and how disagreements get resolved*. Think
of it as the wiring diagram under the policy statements.

Three commitments are essential to any operating model, and they recur across the sources:

- **Documented accountability.** Every significant decision and every piece of the life
  cycle has a named owner. *Designing Data Governance from the Ground Up* stresses that
  governance fails when nobody is explicitly accountable for a decision right, and current
  research extends this to the boardroom: director fiduciary duty of oversight now reaches
  mission-critical AI, so accountability must trace all the way up.
- **A bounded escalation path.** The operating model defines who approves higher-risk
  actions and how disputes are raised. A council exists precisely to arbitrate across
  domains so that a single team cannot quietly decide something consequential alone.
- **A living, maturing system.** The model is not a static org chart; it is reassessed as
  the organization grows, as its risk profile changes, and as its maturity rises. The books
  and the current research both treat the operating model as something that evolves rather
  than something you install once.

Because AI systems sit across data, engineering, product, legal, risk, privacy, and
security, the operating model is necessarily cross-functional. The *Data Governance
Handbook* argues that the people dimension is the cornerstone: identifying who is
responsible and accountable for a domain is what makes data (and by extension AI)
governable at all.

## The Six-Step Model

*Designing Data Governance from the Ground Up* offers a pragmatic, sequenced model for
building a governance program that is easy to translate from data to AI. The six steps are:

1. **Find your framework.** Decide which governance framework fits your organization and
   connect every initiative back to a clear mission statement. Without a shared "why," the
   rest of the machinery has no anchor.
2. **Select data stewards.** Identify people who own the strategic and tactical decisions
   within each domain. Stewards are the trusted advisors for their area, whether that is
   sales, finance, a specific dataset, or a specific AI model.
3. **Build the governance council.** Stewards cannot coordinate from silos; a cross-functional
   council brings them together, sets shared standards, and arbitrates across domains.
4. **Write a roadmap.** Turn the strategy into a living, single source of truth that maps
   initiatives to milestones and success metrics, so the program has a measurable direction.
5. **Practice governance-driven development.** Governance is not something bolted on after
   building; it is woven into how teams choose tools, partners, and architecture as they
   build and deploy.
6. **Monitor in production.** Governance continues after launch: stewards watch quality,
   behavior, and drift in the running system and act when things degrade.

The power of this sequence is that it is deliberately culture-first and people-first: it
starts with alignment and ownership before it reaches for tools or controls. For AI, the
"steward" and "council" steps map naturally onto model owners and an AI risk council, and
the monitoring step maps onto production drift detection and incident response (see
`ai-lifecycle-governance.md`).

## Roles: Stewards, Owners, and the Chief AI Officer

The operating model resolves into a small set of recurring roles. The *Data Governance
Handbook* distinguishes clear layers that transfer well to AI governance:

- **Executive / accountable owner.** The most senior person accountable for a domain's
  success or failure. In data this is often a chief data officer; in AI, organizations are
  increasingly naming a Chief AI Officer (CAIO) or equivalent, a trend current research
  shows is accelerating — including a U.S. federal mandate in 2024 for agency-level CAIOs.
  This role sets vision, owns policy, and reports up to the executive team and board.
- **Domain steward / owner.** The day-to-day leader for a specific domain, asset, or model.
  Stewards answer for data quality, access, and management within their area and keep the
  accountable executive informed. In *Designing Data Governance from the Ground Up*,
  stewards are split between *business stewards* (who own the data for business processes
  and know what "good" looks like for the domain) and *technical stewards* (who own the
  systems, pipelines, and implementation details).
- **Functional professionals.** The analysts, data scientists, engineers, and architects who
  do the hands-on work under the stewards and are consulted on decisions affecting their
  specialty.

The key discipline is that these roles are **named and documented**, not implied. Current
research on NIST's AI RMF "govern" function reinforces this: organizations are expected to
document roles, responsibilities, and lines of communication, and to put executive
ownership explicitly on the record for AI development and deployment decisions.

## Councils and Committees

Councils are the coordination layer that stops stewards from operating in silos. Both books
describe a tiered structure that scales with the organization, and the current research
confirms the same three-tier pattern for AI:

- **Board / board committee.** The top oversight tier, responsible for fiduciary oversight of
  mission-critical AI, reviewing risk and mitigation as a recurring agenda item, and being
  briefed promptly on material incidents. Research describes this as "noses in, fingers
  out": boards stay informed enough to govern without stepping into operations.
- **Enterprise council / committee.** The cross-functional body that sets policy and
  standards and approves higher-risk use cases. The *Data Governance Handbook* distinguishes
  an *enterprise data committee* (executives, meeting quarterly, accountable to the CEO and
  board) from an *enterprise data council* (senior leaders one to two levels below the
  C-suite, doing the detailed policy and monitoring work and reporting up to the committee).
  For AI this is the AI ethics or AI risk council that convenes compliance, legal, privacy, risk,
  security, data, product, and engineering.
- **Stewards / operating owners.** The people who run day-to-day controls and drive
  implementation inside their domains.

Each body should be run under a **charter** — a written terms of reference covering purpose,
key representatives, responsibilities, reporting lines, meeting cadence, communication plan,
and how it evaluates its own effectiveness. The *Data Governance Handbook* includes sample
charters for the committee and council, and this skill ships a fillable
[governance-charter.md](../templates/governance-charter.md) template to instantiate one. A recurring practical note from
*Designing Data Governance from the Ground Up* is that councils need a regular cadence (for
example, roughly an hour every other week, plus focused work between meetings) and ground
rules for psychological safety so that honest discussion, including disagreement, is
possible.

## Decision Rights and RACI

The operating model only works if it is explicit about who decides what. *Designing Data
Governance from the Ground Up* frames this as a set of questions: Who owns data within each
domain? Who is responsible for it? Who decides which teams and people gain access? The same
questions apply to an AI model or use case: who approves its development, who approves its
deployment, who owns its monitoring, and who can escalate if it drifts or fails.

**RACI** is the standard tool for making these decision rights legible. A RACI matrix assigns
each task or decision one or more of four labels:

| RACI letter | Meaning | Practical role in AI governance |
|---|---|---|
| **R**esponsible | Does the work | The steward/engineer who builds or monitors the model |
| **A**ccountable | Owns the outcome | The executive or owner who answers for it and signs off |
| **C**onsulted | Must be asked before deciding | Legal, risk, privacy, security, affected business units |
| **I**nformed | Must be told after deciding | Broader stakeholders, sometimes the board |

A well-built RACI makes disputes rare because it answers the question in advance: for any
given decision, exactly one person is accountable, the right people are consulted, and
everyone who needs to know is informed. For a use case this might assign the model owner as
Responsible, the head of the domain as Accountable, legal and privacy as Consulted, and the
AI council and board as Informed. Documenting this explicitly in the governance charter and
the use-case intake flow is what turns an abstract commitment to accountability into an
enforceable decision right.

## Federated vs. Centralized Operating Models

Organizations must choose how much authority sits at the center versus in the business units.
The *Data Governance Handbook* describes a spectrum of operating models:

- **Centralized.** All responsibilities sit in a central office. This maximizes consistency
  and is useful short term to remediate large maturity gaps or quality problems, but the book
  cautions that long-term centralization separates stewards from their business units and
  erodes the subject-matter expertise that makes a steward effective. The guidance is to
  treat full centralization as a bounded, roughly 12-to-24-month phase and then move toward a
  more distributed model.
- **Federated.** The center defines policy and does the bare minimum, while business units do
  the implementation. This empowers each unit but makes it hard to assemble an
  enterprise-wide view, and often needs a rationalization effort later once programs
  formalize.
- **Semi-federated.** Units stand up their own accountable leaders who implement centrally set
  policy within their divisions, with a data domain model assigning a steward to each asset.
- **Hub-and-spoke.** A strong central office provides expectations, policies, standards, and
  shared capabilities (the hub), while business units and functions drive implementation
  (the spokes). The book regards this as the strongest model for lasting success, precisely
  because it standardizes capabilities across the organization while keeping expertise in
  the business — but only when the central office is well established and funded.

There is no single correct answer. The books and the current research converge on the
principle that the best model is the one that drives progress and maturity for your specific
organization, and that most organizations try several arrangements before settling on one.
Current research adds that there is no one prescribed AI operating model either: the balance
between a CAIO, the governance council, and a board committee is not uniform, but authoritative
guidance consistently requires documented roles, clear accountability that reaches the
board, and periodic reporting.

## Maturity and Culture

**Maturity.** Governance programs are rarely complete; they improve in stages. The *Data
Governance Handbook* treats maturity assessment as an annual exercise that measures the
organization across governance dimensions (using models such as DCAM), gives each dimension
a level, surfaces gaps, and reports results up to the executive team and board in aggregate.
Current research reinforces the idea for AI: NIST's AI RMF functions (govern, map, measure,
manage) function like a maturity ladder — a nascent organization merely identifies its
systems, while a mature one governs, maps, measures, and manages AI risk continuously and
feeds results back into improvement. ISO/IEC 42001 provides a certifiable management-system
structure built around a Plan-Do-Check-Act cycle, which is itself a maturity mechanism. The
practical takeaway is that the operating model should include an explicit way to score
itself and a roadmap to move up, not a one-time compliance checkbox. (This skill ships the
`governance-maturity.py` script to operationalize such a self-assessment.)

**Culture.** Both books stress that governance succeeds on culture, not just structure.
*Designing Data Governance from the Ground Up* emphasizes transparency and psychological
safety: people must be able to surface problems without fear of blame, or they will hide
exactly the issues governance exists to catch. The *Data Governance Handbook* makes a more
provocative point: resist treating "data culture" or "data literacy" as separate campaigns.
Instead, weave data-informed decision-making into the ordinary culture of the company and
build trust through delivery; the culture change follows from demonstrated value rather than
from a formal program. The current research echoes this for AI adoption, where knowledge
gaps, budget constraints, and regulatory uncertainty remain the leading implementation
barriers — problems that are cultural and educational as much as structural.

## Running the Operating Model Day to Day

An operating model has value only when it is exercised. Concretely, this means:

- **A standing, documented decision rights map** (RACI) that is consulted for every new AI
  use case, not an afterthought.
- **A regular cadence of council and committee meetings**, with a charter that says how often
  they meet, what they approve, and how they report upward.
- **Use-case intake and tiering** that routes new AI proposals to the right level of review
  based on risk (see `risk-management-and-frameworks.md`).
- **Incident and escalation paths** so that when a system misbehaves in production, the
  operating model tells people whom to call and who is accountable for the response (see
  `ai-lifecycle-governance.md`).
- **Periodic board reporting** so that leadership has visibility into risk, incidents, and
  third-party exposure, consistent with the oversight duty described in the research (see
  `procurement-third-party-and-board-oversight.md`).
- **An annual maturity review** that scores the program, identifies gaps, and feeds a revised
  roadmap.

## Adapting the Model to AI

The six-step model and the role/council structure transfer to AI with only modest
adjustments, and current research points to where AI-specific attention is needed:

- **Name an accountable executive and, where warranted, a Chief AI Officer** to reduce
  fragmentation, because uncoordinated AI projects otherwise proliferate without executive
  oversight.
- **Make third-party risk first-class.** Much of an organization's AI footprint is procured,
  embedded, or inherited through vendors and M&A, so supply-chain diligence and vendor
  accountability must be embedded in the operating model from the start (see
  `procurement-third-party-and-board-oversight.md`).
- **Extend stewardship to models.** Assign a named owner to every model and dataset, using
  the same business/technical steward split the books describe for data.
- **Treat the board as a real tier.** Because oversight of mission-critical AI is now a
  recognized director responsibility, the operating model should include a standing board or
  board-committee view and prompt escalation of material incidents.

Use the fillable [governance-charter.md](../templates/governance-charter.md) template to instantiate the council terms of
reference, and the use-case intake and model-risk-assessment templates to exercise the
decision rights the operating model defines.

## Where to Go Next

- **`foundations-and-principles.md`** — the values this operating model operationalizes.
- **`risk-management-and-frameworks.md`** — how the model routes work through risk tiering.
- **`ai-lifecycle-governance.md`** — the stage gates the model enforces across the life cycle.
- **`procurement-third-party-and-board-oversight.md`** — the board and vendor tiers of the model.

---

### Synthesized from

This reference synthesizes (never reproduces) ideas from *Designing Data Governance from the
Ground Up* and the *Data Governance Handbook*. Current context on board fiduciary duty, the
Chief AI Officer role, governance councils, maturity, and third-party risk is drawn from the
mission research note research-org-board-governance.md. All prose is an original paraphrase
and synthesis of the ideas in these sources; idea-level attribution is consolidated in
`source-index.md`.
