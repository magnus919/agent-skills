# Discovery Brief — product-operations-and-governance

Bounded discovery brief for issue #193, Milestone 4. Records the pre-implementation survey of existing material and the ownership/routing boundary decision.

## Surveyed Skills

The following existing and same-wave skills were surveyed to avoid duplication and define ownership boundaries:

| Skill | Surveyed | Boundary finding |
|-------|----------|-----------------|
| `product-strategy` | Yes | Owns product vision, North Star, competitive positioning, market analysis. Product governance routes *to* strategy for strategic context but does not duplicate it. |
| `product-methodology` | Yes | Owns tactical prioritization (RICE, MoSCoW), decision logs, spec drafting. Product governance owns the *system* for recurring decisions; methodology owns the *tools* for individual decisions. |
| `product-roadmapping-and-portfolio` | Yes (wave 2) | Owns outcome roadmaps, strategic bets, portfolio sequencing. Product governance owns the *review cadence and decision-rights framework* that surrounds roadmap work; roadmap owns the roadmap artifact itself. |
| `product-experimentation` | Yes (wave 2) | Owns experiment design, method selection, guardrails, readouts. Product governance owns the *experiment review cadence* and the *proceed/stop decision authority*; experimentation owns the experiment itself. |
| `chief-of-staff-methodology` | Yes | Owns executive decision memos, CoS methods, board materials, organizational sensing. This is **executive governance**, not product governance. Product governance must route executive questions here and not duplicate. |
| `strategy-frameworks` | Yes | Owns strategic planning, capital allocation, OKR frameworks, Five Forces, Blue Ocean, M&A evaluation. This is **executive governance**. Product governance routes strategic-bet and capital questions here. |
| `release-engineering` | Yes | Owns release mechanics, deployment pipelines, versioning, rollback plans. This is **delivery gates**. Product governance owns the launch *decision* (go/no-go); release engineering owns the launch *mechanics*. |
| `spec-driven-development` | Yes | Owns specification-phase gates, acceptance criteria, task planning. This is **delivery gates**. Product governance does not own spec-phase gating. |
| `adr-authoring` | Yes | Owns architecture decision records. Product governance owns product-level decisions, not architecture decisions. The ADR format may be referenced as an example of a structured decision record. |
| `product-lifecycle-learning` | Prose (same-wave) | Owns post-launch learning, expected-vs-observed outcomes, lifecycle choices (continue/improve/harvest/pivot/pause/retire). Product governance owns the *lifecycle/health review cadence*; lifecycle learning owns the *evidence and decision framework* for lifecycle choices. |

## The Three Governance Layers

This discovery brief defines and distinguishes three governance layers. This distinction is the core architectural decision for the skill and must be visible in SKILL.md itself, not only in this brief.

### Layer 1: Product Governance (OWNED by this skill)

**What it is:** The recurring system for product-level decisions — what gets built, in what order, with what evidence, reviewed by whom, on what cadence.

**Scope:**
- Intake and opportunity review (what enters the product system)
- Portfolio review and prioritization (sequencing and resource allocation across bets)
- Roadmap review (commit, adjust, defer roadmap items)
- Experiment review (proceed, stop, or iterate based on experiment results)
- Launch review (go/no-go/defer with risk acceptance)
- Lifecycle and health review (continue, invest, harvest, or retire)

**Key traits:**
- Product-level accountable owners (product lead, not CEO or CTO)
- Evidence standards that scale by product risk, not company size
- Cadences tied to product rhythm, not fiscal calendar
- Escalation upward to executive governance when decisions exceed product authority

### Layer 2: Executive Governance (NOT owned — routes to chief-of-staff-methodology, strategy-frameworks)

**What it is:** Company-level decisions about capital, structure, and strategic direction.

**Scope:**
- Capital allocation across business lines
- Organizational structure and role design
- Strategic bets at the company level (not product-level bets)
- M&A evaluation and integration
- Board-level reporting and governance

**Key traits:**
- Executive accountable owners (CEO, CFO, board)
- Decisions that bind the entire company, not one product
- Fiscal-year and board-meeting cadences
- Product governance escalates *to* this layer when a decision exceeds product authority

**Why the separation matters:** A product lead deciding to kill an underperforming feature is product governance. The CEO deciding to divest the entire business line is executive governance. Conflating them produces either product leads making capital-allocation decisions without authority, or executives micromanaging product-level choices.

### Layer 3: Delivery Gates (NOT owned — routes to release-engineering, spec-driven-development)

**What it is:** Technical checks that gate the progression of work through the delivery pipeline.

**Scope:**
- CI/CD pipeline stages and required checks
- Release approval workflows and deployment checklists
- Specification-phase gates (acceptance criteria met, task plan complete)
- Infrastructure change review and approval
- Rollback verification and post-deployment monitoring

**Key traits:**
- Technical accountable owners (engineering lead, release manager, platform team)
- Automated where possible; manual approval for high-risk changes
- Per-change cadence, not recurring review cadence
- Product governance *feeds* delivery gates (a launch go decision triggers the release pipeline) but does not own them

**Why the separation matters:** A product governance launch review says "this product is ready to ship." A delivery gate says "the deployment pipeline passed, artifacts are signed, rollback is verified." Both must be true to ship. Conflating them produces either product leads approving deployment checklists they don't understand, or release engineers making product-scope decisions they're not accountable for.

## Ownership Boundary

**This skill owns:**
- The product operating model (configurable patterns, not a universal org chart)
- Decision-rights maps with named accountable owners
- Six recurring review cadences (intake through lifecycle) with purpose, participants, inputs, outputs, and decision authority
- Minimum evidence standards per decision type, scaled by operating mode
- Exception records (waived requirements with revisit triggers)
- Escalation records (unresolved decisions escalated through the governance system)
- The distinction between lightweight and high-assurance operating modes

**This skill does NOT own:**
- Executive governance methods (routes to chief-of-staff-methodology, strategy-frameworks)
- Technical delivery gates (routes to release-engineering, spec-driven-development)
- Individual decision frameworks (routes to product-methodology for RICE/MoSCoW/decision logs)
- Experiment design or statistical analysis (routes to product-experimentation, data-scientist)
- Roadmap artifact creation (routes to product-roadmapping-and-portfolio)
- Lifecycle evidence and decision frameworks (routes to product-lifecycle-learning — same-wave, prose)
- Architecture decisions (routes to adr-authoring)

## Design Decisions

1. **Three-layer governance boundary as first-class content.** The product/executive/delivery distinction is not buried in a reference file; it appears in SKILL.md body under "Governance Boundary (Read First)" so an agent loading the skill sees it immediately.

2. **Two operating modes, not one.** Lightweight and high-assurance are configuration choices, not maturity levels. A high-assurance mode is not "more mature" than lightweight — it is appropriate for a different risk profile. The mode drives evidence standards, review formality, and escalation thresholds.

3. **Configurable patterns, not a universal org chart.** Four patterns (single accountable owner, product council, tiered review, delegated authority) are starting points to adapt, not mandates. No pattern assumes a specific company size, reporting structure, or industry.

4. **Evidence classification in every artifact.** All outputs distinguish observed, inferred, asserted, and committed categories. This makes the evidence base auditable and prevents assertions from being treated as facts.

5. **Exception and escalation records as first-class artifacts.** Without exception records, waivers become the new default. Without escalation records, the governance system cannot learn or improve. Both are mandatory outputs for their respective scenarios.

6. **Routing, not duplication.** Every adjacent concern routes to its canonical owner. The skill does not re-explain RICE, experiment design, roadmap mechanics, or executive methods.

## Non-Goals

- Does NOT create a universal org chart or impose a single governance model.
- Does NOT duplicate chief-of-staff-methodology authority methods or executive decision-memo formats.
- Does NOT duplicate release-engineering deployment mechanics or spec-driven-development phase gates.
- Does NOT replace product-methodology's decision-log format (the exception/escalation records are governance artifacts, not general-purpose decision logs).
- Does NOT prescribe a specific tool (Jira, Linear, spreadsheet, wiki) — templates are tool-agnostic.
