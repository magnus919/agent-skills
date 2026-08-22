# Nine-Phase Change-Request Journey — Validation Against Established SDLC Models and Agentic-Workflow Frameworks

| Field | Value |
|---|---|
| **Issue** | #372 (research only — no neckbeard behavior changes proposed here) |
| **Date** | 2026-08-22 |
| **Subject studied** | `neckbeard/references/journey.md` at commit `04a9b60b58244b5007e9279d53ed504362303320` (`git log -1 --format=%H -- neckbeard/references/journey.md`), branch `research/neckbeard-journey-sdlc-validation`, based on `origin/main`. Supporting context: `neckbeard/SKILL.md` core loop, `neckbeard/references/stages.md` § Stage 6 and § Change-request gates, `neckbeard/references/risk-authority-gates.md` stop rules. |
| **Comparison basis** | Four established lifecycle/process models (ISO/IEC/IEEE 15288:2023, ISO/IEC/IEEE 12207:2017, CMMI-DEV V1.3, ITIL 4 service value system) and three published agentic-workflow approaches (Anthropic "Building Effective Agents", OpenAI "A Practical Guide to Building Agents", the Agent Skills specification). |
| **Method** | research-methodology skill, academic/comprehensive track (Scope → Gather → Evaluate → Analyze → Synthesize → Report). Companion evidence log: [journey-sdlc-validation-log.md](journey-sdlc-validation-log.md). All access dates 2026-08-22. |
| **Doctrine lens** | Every verdict below is judged against neckbeard's stated doctrine: evidence over assertion, smallest safe intervention, and hard authority boundaries (readiness ≠ release; merge authority ≠ release authority). |

---

## Research questions (restated from issue #372)

1. **RQ1 — Missing counterparts.** Do established lifecycle models contain phases or feedback loops with NO counterpart in the nine-phase journey? Specifically examined: maintenance/operations feedback into planning, post-release learning loops, retirement/decommission stages.
2. **RQ2 — Agentic workflow structures and authority gates.** How do published agentic-workflow approaches structure multi-stage software delivery, and where do they place human authority gates relative to neckbeard's five gates?
3. **RQ3 — Phase boundaries.** Are the phase boundaries themselves right — anything merged that should be split, or split that should be merged?
4. **RQ4 — Verdicts.** For each material difference: adopt, adapt to neckbeard's evidence-first doctrine, or reject, with rationale.

---

## Part 1 — Per-framework mapping

### 1.1 ISO/IEC/IEEE 15288:2023 — System life cycle processes

Primary: ISO catalog entry, https://www.iso.org/standard/81702.html (accessed 2026-08-22); IEEE SA, https://standards.ieee.org/ieee/15288/10424/ (accessed 2026-08-22). Clause inventory corroborated via https://en.wikipedia.org/wiki/ISO/IEC_15288 (accessed 2026-08-22). Full normative text is paywalled; see log § limitations.

The standard defines 30 processes in four categories (agreement; organizational project-enabling; technical management; technical). The fourteen technical processes include, in order: business/mission analysis, stakeholder needs and requirements definition, system requirements definition, architecture definition, design definition, system analysis, implementation, integration, verification, transition, validation, **operation**, **maintenance**, **disposal**.

| 15288 element | Nine-phase journey counterpart | Notes |
|---|---|---|
| Stakeholder needs & requirements definition (6.4.2), System requirements definition (6.4.3) | Phases 1, 4 | Intake captures provenance, authority, conventions, linked work; phase 4 produces SPEC.md with acceptance criteria mapped to the change contract. Deep stakeholder elicitation is handled by the phase-4 escalation path (product-discovery), not a dedicated phase. |
| Architecture definition / Design definition (6.4.4–6.4.5) | Phase 3 (+ gate 1) | Direct counterpart including decision records and rejected alternatives. |
| System analysis (6.4.6) | Phase 3 risk assessment | Risks, compatibility, migration, rollback plan are mandatory phase-3 outputs. |
| Implementation (6.4.7) | Phase 6 | Direct. |
| Integration (6.4.8) | Phases 6–8 | Branch/CI mechanics; exact-final-head SHA binding. |
| Verification (6.4.9) | Gates 2 and 5; phases 5, 7 | Pre-planned QA-owned verification plan plus boundary verification at the declared target. Stronger than most implementations of 15288 because the verification plan precedes implementation. |
| Validation (6.4.11) | Partial — gate 4 review + acceptance criteria | Confirming the change serves stakeholder intent is implicit in acceptance criteria and the issue thread; there is no named validation step distinct from verification. See Finding F4. |
| Transition (6.4.10) | Phases 8–9 | Merge/release = transition into the protected target; release gate ≈ transition authorization. |
| **Operation (6.4.12)** | **None** | Journey stops at post-release smoke check evidence. Operational monitoring/feedback is outside the single change request. Finding F1. |
| **Maintenance (6.4.13)** | **None as a phase — structurally absorbed** | Each subsequent issue/ticket starts a new journey; the journey *is* the unit of maintenance under 12207-style taxonomies. There is no explicit "feed operations learnings into the next planning cycle" loop inside one journey. Findings F1, F2. |
| **Disposal (6.4.14)** | **None** | Retirement/decommissioning has no counterpart. Finding F3. |
| Technical-management processes (risk, decision, config mgmt, QA, assessment/control) | Distributed across all phases | Head-SHA binding + materiality rule ≈ configuration management; escalation/stop rules ≈ decision management; gate verdict ledger ≈ project assessment and control. |

**Authority-gate placement:** 15288 locates authority in organizational processes (agreement, project assessment and control) and does not prescribe where human sign-off occurs within a change. The journey is far more prescriptive: five named gates, authority classes at intake, and a hard separation of readiness (phase 8) from release (phase 9). This is a tightening, not a contradiction.

### 1.2 ISO/IEC/IEEE 12207:2017 — Software life cycle processes

Primary: ISO catalog entry, https://www.iso.org/standard/63712.html (accessed 2026-08-22). Process-category structure corroborated via arc42 quality-model summary, https://quality.arc42.org/standards/iso12207 (accessed 2026-08-22). Normative text paywalled.

12207 organizes software life-cycle activity into agreement, organizational project-enabling, technical-management, and technical process categories; the technical processes span stakeholder requirements through implementation, integration, verification, validation, operation, **maintenance** (including corrective, adaptive, perfective, preventive maintenance), and **disposal**.

Key analytical result: **the nine-phase journey is best classified as 12207's maintenance-and-development technical processes instantiated per change request.** Under 12207, corrective/perfective maintenance activity flows through the same requirements → design → implementation → verification pipeline; the journey models exactly that pipeline for one change, entered from an issue (the maintenance trigger). What 12207 adds that the journey lacks inside one journey instance:

| 12207 element | Journey counterpart | Notes |
|---|---|---|
| Agreement processes | Phase 1 authority class + change contract | Close functional match: the change contract records who authorized what class of work. |
| Life-cycle model management / tailoring | Delivery paths (lightweight/full/refactor/high-risk) with recorded skips | Tailoring with mandatory skip-reason recording exceeds typical tailoring guidance (silent omission prohibited). |
| Verification / Validation | Gates 2, 4, 5 | Same verification-vs-validation asymmetry as 15288. Finding F4. |
| **Operation / Maintenance feedback** | None inside one journey; next journey is the vehicle | Finding F1/F2. |
| **Disposal** | None | Finding F3. |

**Authority-gate placement:** 12207 permits combined development/assurance roles unless the acquirer constrains them; the journey independently mandates reviewer-implementer separation (gate 4 "distinct from spec-compliance checking"; QA-owned gate 2 "post-hoc self-approval by the implementer is not permitted"). Tightening, consistent.

### 1.3 CMMI for Development, Version 1.3 (CMU/SEI-2010-TR-033)

Primary: full SEI technical-report text consulted via public reproduction at http://cmmis.free.fr/cmmi-dev/text/index.php (unofficial mirror of CMU/SEI-2010-TR-033; content verified against report front matter, accessed 2026-08-22). Official alternate locations identified but not fetched: https://apps.dtic.mil/sti/tr/pdf/ADA532839.pdf, CMU Kilthub record.

CMMI-DEV organizes 22 process areas across staged maturity levels. Engineering category: Requirements Development (RD), Technical Solution (TS), Product Integration (PI), Verification (VER), Validation (VAL). Support: Configuration Management (CM), Process and Product Quality Assurance (PPQA), Measurement and Analysis (MA), Decision Analysis and Resolution (DAR), **Causal Analysis and Resolution (CAR, level 5)**.

| CMMI-DEV PA | Journey counterpart | Notes |
|---|---|---|
| RD / REQM | Phases 1, 4 | Requirements developed and managed against the change contract. |
| TS | Phases 3, 6 | Design alternatives evaluated and recorded (rejected alternatives are mandatory phase-3 output) — mirrors TS SP 1.1/1.2 and DAR-style selection criteria. |
| PI | Phases 6–8 | Build/integration with CI as boundary evidence. |
| VER | Gates 2, 5; phase 5 | Peer-review + verification practices; journey's pre-implementation test planning matches VER SG 1 intent. |
| VAL | Partial — gate 4 + acceptance criteria | Same verification/validation asymmetry. Finding F4. |
| CM | Packet group (c)/(h) head-SHA binding; materiality rule | The exact-final-head re-verification and material/non-material classification are a disciplined CM baseline-and-change mechanism. |
| PPQA | Gate 4 independent review; QA-owned gate 2 | PPQA requires assurance by someone not producing the work product — the journey's independence doctrine matches this precisely. |
| DAR | Phase-3 decision records; escalation when two defensible approaches diverge | Direct match. |
| RSKM | Phase-3 risk assessment; high-risk path | High-risk path adds escalation review at gates 1, 2, 5 — proportional risk management. |
| MA | CI status, gate-verdict ledger, packet groups | Evidence-first doctrine institutionalizes measurement. |
| **CAR** | **No journey counterpart** | CMMI's formal post-defect causal-analysis loop (select defect data → root-cause → propose/implement actions) lives at organizational level. Its nearest in-repo analogue is core-loop Stage 6 "Deliver and learn," which is NOT wired into the nine-phase journey's phase 9 outputs. Finding F2. |

**Authority-gate placement:** CMMI embeds authority in institutionalized process (GP 2.9/2.10, PPQA separation) rather than per-change human gates. The journey's explicit gates are compatible and more granular for agentic execution.

### 1.4 ITIL 4 service value system

Sources: InvGate ITIL 4 SVS explainer, https://invgate.com/itsm/itil/service-value-system (accessed 2026-08-22); practitioner analysis of the service value chain by D. Breston, https://itsm.tools/itil-4-service-value-chain/ (accessed 2026-08-22; also documents the January 2026 ITIL Version 5 announcement). PeopleCert/Axelos normative text is licensed and was not directly accessible; see log § limitations.

The SVS comprises guiding principles, governance, 34 practices, continual improvement, and the six-activity service value chain: **plan, improve, engage, design & transition, obtain/build, deliver & support**.

| SVC activity | Journey counterpart | Notes |
|---|---|---|
| Engage | Phase 1 intake; phase 7 review engagement; phase 9 enterprise CAB | Partial. Stakeholder dialogue beyond intake/review (value confirmation with users) is absent. |
| Plan | Phases 4–5 | Spec + task plan + verification plan. |
| Design & transition | Phases 3, 7, 8, 9 | Includes enterprise-mode CAB/change-manager sign-off and change-freeze compliance — direct ITIL change-enablement mapping already present in phase 9. |
| Obtain/build | Phase 6 | Direct. |
| Deliver & support | Phase 9 (deliver only) | Release evidence, smoke check. Ongoing support/operations is out of journey scope. Finding F1. |
| **Improve (continual improvement)** | **No journey counterpart** | ITIL treats improvement as built into the system ("improvement isn't a side project"). The journey declares phase 9 output "terminal; not consumed," so nothing in the journey itself carries lessons forward — although core-loop Stage 6 does. Finding F2. |

**Authority-gate placement:** ITIL's change-enablement practice routes changes through a change authority (CAB/change manager) sized to risk — the journey's enterprise mode already maps this onto the phase 9 release gate, and its GitHub mode separates merge from release authorization in exactly the ITIL sense of delegated change authority. Convergent; no change indicated.

*Currency caveat:* ITIL Version 5 was announced in January 2026, replacing the service value chain with a "digital product and service lifecycle" while keeping the rest of the SVS largely unchanged. The continual-improvement finding (F2) is expected to survive that revision, but revalidation is warranted once published.

### 1.5 Anthropic, "Building Effective Agents" (Dec 19, 2024)

Primary first-party engineering publication: https://www.anthropic.com/engineering/building-effective-agents (accessed 2026-08-22).

Structures for multi-stage delivery: augmented LLM building block; workflows (prompt chaining with programmatic "gates", routing, parallelization sectioning/voting, orchestrator-workers, evaluator-optimizer); autonomous agents with environment ground-truth at each step, checkpoint pauses for human input, and stopping conditions.

| Anthropic construct | Nine-phase journey counterpart |
|---|---|
| Prompt chaining with programmatic checks ("gates") between steps | Five gates blocking phase progression — same shape, made explicit and auditable. |
| Routing | Conditional specialist routing via routing-table.md; four delivery paths select the route at intake. |
| Parallelization / voting | Multi-dimension independent review at gate 4 (code quality, architecture, security, accessibility, docs) — several reviewers over one frozen candidate. |
| Orchestrator-workers | Specialist composition with one recorded lead per stage (packet group (e)). |
| Evaluator-optimizer loop | Phase 7 → phase 8 CI/review feedback iteration, bounded by the materiality rule (material change ⇒ re-enter phase 7). |
| "Gain ground truth from the environment at each step" | Evidence-ledger doctrine: files changed, commands run, observed outputs appended per phase. |
| Stopping conditions / max iterations | Bounded loops: escalation after two undiagnosable CI failures; stop after two materially different approaches fail; timed-out review is inconclusive and does not restart against a mutable candidate. |

**Human authority-gate placement:** Anthropic places human involvement at task initiation ("command from, or interactive discussion with, the human user"), at checkpoints, and on blockers — leaving gate placement to the implementer. For coding specifically it concludes automated tests verify functionality but "**human review remains crucial** for ensuring solutions align with broader system requirements." The journey agrees and goes further: authority classes at intake, escalation stop rules at every boundary, and separate merge/release authorization. **Convergence, with neckbeard strictly more prescriptive.**

**Doctrinal alignment:** Anthropic's core counsel — simplest solution possible, add complexity only when demonstrably justified — is the same judgment as smallest safe intervention, and the four delivery paths operationalize it proportionally.

### 1.6 OpenAI, "A Practical Guide to Building Agents" (April 2025)

Primary first-party guide (PDF): https://cdn.openai.com/business-guides-and-resources/a-practical-guide-to-building-agents.pdf (downloaded and converted locally; accessed 2026-08-22).

Structures: foundations (model + tools + instructions); a "run" loop until an exit condition; orchestration via single agent, manager pattern, or decentralized handoffs; layered guardrails; explicit human-intervention design.

| OpenAI construct | Nine-phase journey counterpart |
|---|---|
| Run loop with exit conditions | Core-loop spine; journey phases bound each run. |
| Manager pattern / decentralized handoffs | Orchestrating SKILL.md loads journey reference; specialists routed per phase. |
| Layered guardrails (input, tool, output) | Gate stack + stop rules + skip transparency. |
| **Tool safeguards:** rate each tool low/medium/high by read-only vs write access, reversibility, required permissions, financial impact; **pause before high-risk functions or escalate to a human** | Authority classes (explore/modify/release) + risk-authority-gates.md hard stops (never delete data/branches/releases/infra without directive; never escalate privileges; never deploy/merge without granted authority). Same principle, coarser per-call granularity. Finding F6. |
| **Human-intervention trigger 1: exceeding failure thresholds** | Escalation after two failed diagnostic attempts; stop after two materially different failed approaches. Matches. |
| **Human-intervention trigger 2: high-risk, sensitive, irreversible, or high-stakes actions** | Hard stops on irreversible/trust-boundary acts; release gate. Matches. |

**Human authority-gate placement relative to neckbeard's gates (RQ2):** both vendors converge on the same three placements the journey already encodes — upfront authorization scoping, threshold-based escalation, and mandatory human oversight of consequential/irreversible actions. Neither vendor structures software delivery into SDLC phases; their guidance is runtime-architecture advice. The journey therefore occupies complementary territory: it supplies the lifecycle sequencing and auditability those guides leave undefined. No conflicting recommendation found.

### 1.7 Agent Skills specification (agentskills.io)

Primary specification: https://agentskills.io/specification.md (accessed 2026-08-22).

The Agent Skills format packages capabilities (SKILL.md + optional scripts/references/assets) with progressive disclosure and an experimental `allowed-tools` pre-approval field. It contains **no lifecycle phases, no gates, and no workflow semantics** — it is a capability-packaging layer, orthogonal to process models.

Relevance: neckbeard is itself structured per this format, loads the journey as a conditionally-loaded reference, and routes phase work to packaged specialist skills. The spec's static `allowed-tools` grant is a blunter instrument than the journey's authority classes; the journey's approach (authority bound to the change contract and re-examined at gates) is stronger for change delivery. No restructuring indicated.

---

## Part 2 — Findings and verdicts

Confidence: H = triangulated across ≥3 independent sources; M = 2 sources or single-source-on-secondary-point.

| # | Material difference | Sources | Confidence | Verdict | Rationale grounded in neckbeard doctrine |
|---|---|---|---|---|---|
| **F1** | **Post-release operations and monitoring have no journey counterpart.** 15288 defines Operation (6.4.12) and Maintenance (6.4.13) as technical processes; ITIL's deliver & support extends past release. The journey ends at phase 9 with release evidence and a terminal packet. | 15288; 12207; ITIL 4 | H | **ADAPT (minimal)** | Do not add a phase 10 — that would violate smallest safe intervention and duplicate `site-reliability-engineering`/`release-engineering` competencies the routing table already reaches. Adapt instead: phase 9 closeout should record **rollback/follow-up triggers** (already a core-loop obligation, SKILL.md step 6) alongside release evidence, and route operational discoveries to a *new* change request via phase 1 intake. Evidence-first: the terminal record then states what would cause re-entry. |
| **F2** | **Post-release learning loop is mandated by the core loop but not wired into the journey.** ITIL makes continual improvement structural; CMMI CAR formalizes post-defect causal analysis; neckbeard's own stages.md Stage 6 ("Deliver and learn") requires capturing "post-delivery findings and reusable lessons… back into the appropriate durable layer." Yet journey phase 9's required outputs are only terminal state + release/close evidence, and the phase-continuity table marks phase 9 output "terminal; not consumed." This is an internal misalignment between journey.md and stages.md, not just an external gap. | ITIL 4; CMMI-DEV CAR; neckbeard stages.md (internal) | H | **ADAPT** | Extend phase 9 closeout outputs to include a lesson-capture field with skip transparency: either the captured lesson(s) and their durable destination, or an explicit "no reusable lesson identified" determination — mirroring how skipped phases/specialists must be recorded with reasons. Small diff, restores consistency with the skill's own Stage 6 doctrine, preserves terminal-state semantics. |
| **F3** | **Retirement/decommissioning has no journey counterpart.** 15288 Disposal (6.4.14) and 12207 disposal address retiring systems. Nothing in the nine phases covers decommissioning. | 15288; 12207 | H | **REJECT (deliberate scope boundary)** | The journey governs individual change requests, not asset lifecycles. Decommissioning enters as what it is — a high-risk change request (path selection already forces all nine phases, all five gates, no skips) whose irreversibility is caught by existing hard stops ("never delete data, branches, releases, or infrastructure without an explicit human directive"). Adding a retirement phase would conflate change-delivery scope with portfolio-level lifecycle management. Record the boundary in docs if desired; do not add phases. |
| **F4** | **Validation is under-distinguished from verification.** 15288 separates verification (product reflects specified requirements) from validation (product fulfills stakeholder need in intended use), as does CMMI VER vs VAL. The journey has strong verification (gates 2/5, declared boundary targets) and independent review (gate 4), but confirming the change solves the *requester's actual problem* rides only implicitly on acceptance-criteria mapping in phase 4. | 15288; 12207; CMMI-DEV | H | **ADAPT** | Make requester-outcome traceability explicit at gate 3: SPEC.md acceptance criteria already map to the change contract; require that at least one criterion traces to the requester's stated outcome/problem restated in phase 2 (which is already mandatory primary-evidence work). Zero new phases; strengthens evidence-over-assertion where it is thinnest — did we build what was actually asked for? |
| **F5** | **Stakeholder-needs elicitation is not a phase.** 15288 6.4.2 and 12207 treat stakeholder-needs definition as first-class. The journey assumes the change request arrives with adequate intent and handles ambiguity reactively (phase 4 escalation to product-discovery). | 15288; 12207 | M | **REJECT** | Proactive elicitation as a standing phase would penalize the lightweight path and contradict smallest safe intervention; the reactive escalation plus the phase-2 mandatory restatement-from-primary-evidence covers the failure mode at lower ceremony. Revisit only if intake-quality data shows repeated late discovery of misunderstood requests. |
| **F6** | **Per-tool risk rating granularity.** OpenAI recommends rating each agent tool by write-access/reversibility/permissions and pausing before high-risk calls. The journey grants authority by class per change rather than per tool. | OpenAI guide; contrast neckbeard risk-authority-gates.md | M | **REJECT (for now)** | Per-tool ratings would duplicate risk-authority-gates.md stop rules and routing-table contracts at finer grain than decisions actually occur, adding ceremony without adding evidence. The authority-class model binds permission to the *change*, which is where accountability lives. Plausible future refinement for enterprise mode only; file as open question, not a defect. |
| **F7** | **Gate placement converges with published agentic practice.** Both Anthropic (checkpoints, blockers, human review essential for code) and OpenAI (failure thresholds, high-risk action oversight) place human authority exactly where neckbeard's five gates and stop rules sit; neither is more prescriptive. The readiness/release authority split exceeds both. | Anthropic; OpenAI | H | **ADOPT AS VALIDATED (no change)** | Independent convergence is evidence that the gate architecture is sound, not idiosyncratic. Preserve as-is; the divergence (more prescription) is justified by the doctrine's auditability goals and the packet ledger that makes verdicts inspectable. |
| **F8** | **Phase boundaries are correctly cut.** Design (3) vs specification (4) matches 15288/12207 architecture-vs-requirements separation and CMMI TS vs RD; QA-owned pre-implementation test planning (5) matches VER practice and the independence doctrine; review + boundary verification sharing phase 7 is acceptable because both bind verdicts to the same frozen head SHA and stages.md keeps the gate definitions separate; readiness-with-CI-loops (8) matches real PR mechanics. No merged-that-should-split or split-that-should-merge case survived analysis. Gate numbering (1→3→2→4→5 execution order) is explained in-text as area grouping; renumbering would break cross-references for zero evidentiary gain. | 15288; 12207; CMMI-DEV; Anthropic | H | **REJECT any restructuring** | Stability of the phase contract is itself a safety property; every framework examined supports the current cuts. |

---

## Part 3 — Explicit conclusion: does the nine-phase model have material gaps?

**The nine-phase journey has no material structural gaps.** Against four established lifecycle models, every phase of the change-delivery core (intake, discovery, design, specification, test planning, implementation, review, readiness, release) has a clear counterpart or a documented, defensible scope boundary. Against three published agentic-workflow approaches, the journey's gate placement and stop rules are not merely compatible but *converge independently* with vendor-published recommendations for human-oversight placement, and exceed them in auditability (SHA-bound verdicts, skip transparency, evidence ledger).

Three differences are material enough to act on, all **ADAPT**-class, all small:

1. **F1 — Record rollback/follow-up triggers at phase 9 closeout** so the terminal packet states what would cause re-entry (aligns journey with core-loop step 6; 15288 Operation/Maintenance, ITIL Deliver & Support).
2. **F2 — Add skip-transparent lesson capture to phase 9** (captured lesson + destination, or explicit "none identified") — this repairs an internal misalignment with stages.md Stage 6 and answers ITIL continual improvement / CMMI CAR at the smallest possible scale.
3. **F4 — Require explicit requester-outcome traceability in gate 3 acceptance criteria** (15288/12207/CMMI validation discipline).

One deliberate non-gap should be documented as such: **retirement/decommissioning (F3) is intentionally out of scope** and remains reachable as a high-risk change request under existing authority gates.

A well-evidenced near-null result, stated plainly: **nothing examined warrants adding, splitting, merging, or reordering phases.** If any change is pursued from this dossier, it should be limited to the three documentation-level adaptations above.

## Open questions / limitations

1. **Paywalled norms.** 15288, 12207, and ITIL 4 normative texts are license-encumbered; mappings rely on catalog metadata (Tier 1), a standards-summary corpus (arc42), and reputable secondary explainers cross-checked against each other. Clause-level citations (e.g., "6.4.12") come from the corroborated clause inventory, not purchased copies. Risk of drift is low for structural claims but nonzero for fine detail.
2. **ITIL Version 5** (announced January 2026) replaces the service value chain with a digital-product-and-service lifecycle. Finding F2 rests on continual improvement, which survives in outline, but revalidate after publication.
3. **CMMI version.** CMMI V3.0 (2023) supersedes V1.3; the analysis used V1.3 because its full SEI text is publicly reproducible. The process-area concepts relied upon (CAR, PPQA, VER/VAL separation, DAR) persist in V3.0 by name; a V3.0 spot-check is cheap follow-up.
4. **ISO/IEC/IEEE 29148** (requirements engineering) was scoped in but **not retained**: only unauthorized scanned copies were locatable, and none were used (see log). Findings that might otherwise cite it (F4, F5) rest on 15288/12207/CMMI equivalents instead.
5. **Single-journey scope assumption.** The dossier evaluates the journey as a per-change-request model, matching its stated purpose. Portfolio-level concerns (multi-change programs, 15288 organizational project-enabling processes) were treated as out of scope by design.
6. **Un-fetched official mirrors.** DTIC/Kilthub copies of CMMI-DEV and IEEE Xplore entries were located but not retrieved (see log); conclusions do not depend on them.
