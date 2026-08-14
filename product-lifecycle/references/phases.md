# Lifecycle Phases — product-lifecycle bundle

Each of the nine lifecycle phases defines: entry evidence (what must exist before
the phase starts), output artifacts (what the phase produces), escalation behavior
(when to stop and escalate), and completion criteria (how to know the phase is
done). Phases are sequential; a phase may be skipped only when its entry evidence
is already satisfied by prior work, and every skip must be recorded in the
lifecycle evidence ledger with a reason.

## Lifecycle evidence ledger

Every phase writes to a shared **lifecycle evidence ledger** — a durable record
that carries evidence, decisions, assumptions, and handoff artifacts across
phases. The ledger is the cross-phase contract: phase N+1 reads what phase N
wrote and does not re-derive it.

### Ledger fields

| Field | Written by | Read by |
|---|---|---|
| Product identity (name, type, context) | Phase 1 | All phases |
| Problem statement and evidence | Phase 1 | Phases 2–9 |
| Stakeholder map and discovery log | Phase 1 | Phases 2–4 |
| Strategy and positioning decisions | Phase 2 | Phases 3–9 |
| Portfolio allocation and bet record | Phase 3 | Phases 4–9 |
| UX contracts and design decisions | Phase 4 | Phases 5–6 |
| Experiment briefs and readouts | Phase 5 | Phases 3, 6–9 |
| Delivery plan, spec, readiness verdict | Phase 6 | Phases 7–9 |
| Adoption plan and rollout evidence | Phase 7 | Phases 8–9 |
| Outcome metrics and success evidence | Phase 8 | Phase 9 |
| Lifecycle review and retained learning | Phase 9 | Future cycles (new phase 1) |
| Phase skip records (any phase) | Skipping phase | All subsequent phases |
| Escalation and stop records (any phase) | Stopping phase | Terminal (ledger closed) |

### Ledger conventions

- Every entry is dated and attributed to the phase that wrote it.
- Assumptions are labeled as such and separated from observed evidence.
- Gaps ("not yet verified," "unknown," "deferred to phase N") are recorded explicitly.
- The ledger is append-only within a lifecycle run. A phase never deletes or alters a prior phase's entries.
- A stopped/escalated lifecycle preserves the ledger as evidence of what was learned.

---

## Phase 1 — Discovery

**What happens:** Understand the problem space, identify stakeholders, gather
evidence about user needs, and decide whether the problem is worth solving.

**Entry evidence:**
- A product idea, market signal, stakeholder request, or strategic initiative.
- Sufficient context to identify who to talk to and what to investigate.

**Output artifacts:**
- Problem statement with supporting evidence (not just opinion).
- Stakeholder map identifying who has relevant knowledge or authority.
- Discovery log: interviews conducted, observations, assumptions surfaced.
- Initial product type classification (B2B subscription, transactional, public-service, consumer, internal tool).
- Decision: proceed to strategy, escalate (no viable problem), or pause (more discovery needed).

**Escalation behavior:**
- Stop and escalate when: the problem cannot be articulated in user terms; no
  stakeholder can describe a real, current need; discovery reveals the problem
  is already adequately solved; or the problem is outside the organization's
  remit or authority.
- Record the escalation reason and evidence in the ledger. The lifecycle may
  terminate here (closed — no viable problem).

**Completion criteria:**
- A problem statement exists that a stakeholder would recognize as their own.
- The product type is classified and recorded.
- A proceed/pause/stop decision is recorded with rationale.

**Primary specialist:** [product-discovery](../../product-discovery/SKILL.md)

---

## Phase 2 — Strategy and portfolio choice

**What happens:** Evaluate the discovered problem against organizational strategy,
competitive landscape, market opportunity, and existing portfolio commitments.
Decide whether and how to invest.

**Entry evidence:**
- Problem statement and discovery log from Phase 1.
- Organizational strategy context (mission, vision, current strategic bets).
- Market context (size, competition, trends).

**Output artifacts:**
- Strategic assessment: fit with organizational strategy, competitive positioning.
- Market sizing (TAM/SAM/SOM) and opportunity assessment.
- Portfolio recommendation: new strategic bet, enhancement to existing bet, or no-go.
- Investment thesis and resource estimate (order-of-magnitude).
- Decision: proceed to roadmap, escalate (no strategic fit), or defer (not now).

**Escalation behavior:**
- Stop and escalate when: the opportunity conflicts with organizational strategy
  and the conflict is material; market evidence contradicts the investment thesis;
  resource constraints make investment infeasible; or strategic direction is
  ambiguous and requires executive resolution.
- Record the escalation reason and evidence in the ledger.

**Completion criteria:**
- A strategic assessment exists with explicit fit/no-fit reasoning.
- The portfolio decision (new bet / enhancement / no-go / defer) is recorded.
- Resource estimate is recorded (even if rough).

**Primary specialists:** [product-strategy](../../product-strategy/SKILL.md),
[strategy-frameworks](../../strategy-frameworks/SKILL.md) (for framework-guided analysis)

**Supporting:** [financial-modeling](../../financial-modeling/SKILL.md) (for unit economics and sizing)

---

## Phase 3 — Roadmap

**What happens:** Sequence the investment as an outcome-based roadmap entry.
Define what success looks like, map dependencies, and set confidence levels.

**Entry evidence:**
- Strategic assessment and portfolio decision from Phase 2.
- Resource estimate and investment thesis.

**Output artifacts:**
- Outcome roadmap entry: desired outcome, leading indicators, target timeframe.
- Now/Next/Later placement with rationale.
- Strategic bet record: hypothesis, confidence level, continue/pause/kill criteria.
- Dependency map (other teams, platforms, external factors).
- Capacity allocation decision.
- Decision: proceed to UX and requirements.

**Escalation behavior:**
- Stop and escalate when: dependencies cannot be resolved; capacity is
  unavailable and cannot be negotiated; confidence is below the organization's
  threshold for investment and cannot be raised with further discovery; or the
  bet conflicts with a higher-priority bet that cannot be deprioritized.
- Record the escalation reason in the ledger.

**Completion criteria:**
- The roadmap entry exists in the organization's roadmap view.
- Strategic bet record is complete with confidence level and kill criteria.
- Dependencies are mapped and acknowledged by owners.

**Primary specialist:** [product-roadmapping-and-portfolio](../../product-roadmapping-and-portfolio/SKILL.md)

**Supporting:** [product-methodology](../../product-methodology/SKILL.md) (for prioritization frameworks if ranking against other bets)

---

## Phase 4 — UX and requirements

**What happens:** Translate the roadmap entry into concrete user-facing behavior,
information architecture, interaction design, and verifiable requirements.

**Entry evidence:**
- Roadmap entry and strategic bet record from Phase 3.
- Discovery log from Phase 1 (user context, needs, pain points).

**Output artifacts:**
- Information architecture and task flows.
- Interface contracts (screens, states, recovery paths).
- User-facing behavior specification.
- Acceptance criteria derived from user needs.
- Decision: proceed to experimentation (if validation needed) or directly to delivery handoff.

**Escalation behavior:**
- Stop and escalate when: UX work reveals the problem is fundamentally different
  from what discovery suggested; user research contradicts the roadmap hypothesis;
  the required behavior cannot be specified testably; or accessibility, privacy,
  or security constraints cannot be satisfied within the proposed scope.
- Record the escalation reason in the ledger.

**Completion criteria:**
- Information architecture and key task flows are documented.
- Interface contracts exist for all user-facing surfaces.
- Acceptance criteria are testable and traceable to user needs.

**Primary specialist:** [product-design-and-ux](../../product-design-and-ux/SKILL.md)

**Supporting:** [spec-driven-development](../../spec-driven-development/SKILL.md) (for formal specification)

---

## Phase 5 — Experimentation

**What happens:** Test the riskiest assumptions before committing to full
delivery. Select the right experimental method, define guardrails, run the
experiment, and produce a readout that updates the decision record.

**Entry evidence:**
- UX contracts and acceptance criteria from Phase 4 (or roadmap entry if UX was lightweight).
- Assumptions register: what must be true for this to succeed.
- Risk assessment: which assumptions are riskiest or least validated.

**Output artifacts:**
- Experiment brief: hypothesis, method, guardrails, decision rule, stopping condition.
- Experiment readout: observed results, confidence, decision.
- Updated assumptions register.
- Decision: proceed to delivery (hypothesis supported), pivot (hypothesis partially supported), or stop (hypothesis disproved).

**Escalation behavior:**
- Stop and escalate when: the experiment cannot be designed ethically; the
  required method is infeasible (e.g., sample size too small, no control group
  possible); the experiment reveals a safety, privacy, or security risk; or the
  experiment disproves the core hypothesis and no pivot is viable.
- A disproved hypothesis is a legitimate stop — record the evidence and close the lifecycle.
- Record the escalation reason and experiment evidence in the ledger.

**Completion criteria:**
- An experiment brief exists with explicit hypothesis, method, and decision rule.
- An experiment readout exists with observed results.
- A proceed/pivot/stop decision is recorded with evidence.

**Primary specialist:** [product-experimentation](../../product-experimentation/SKILL.md)

**Supporting:** [data-scientist](../../data-scientist/SKILL.md) (for statistical design and analysis)

---

## Phase 6 — Delivery handoff

**What happens:** Hand off the verified product decision to delivery. This phase
bridges product management and production engineering. It produces the
implementation plan, specification, and production-readiness evidence — routing
to engineering and production skills rather than doing the work itself.

**Entry evidence:**
- Proceed decision from Phase 5 (or Phase 4 if experimentation was skipped).
- UX contracts and acceptance criteria from Phase 4.
- Updated assumptions register.

**Output artifacts:**
- Implementation plan: work breakdown, dependency map, rollout strategy.
- Formal specification (SPEC.md) with acceptance criteria.
- Production-readiness evidence packet: risk classification, evidence checklist, launch decision.
- Release plan: versioning, progressive delivery strategy, rollback plan.
- Decision: proceed to adoption (delivery complete and launched).

**Escalation behavior:**
- Stop and escalate when: the implementation plan reveals an infeasible
  dependency; production-readiness review returns No-go or blocked Exception;
  security, privacy, or compliance review blocks launch; or the release plan
  cannot satisfy the organization's change-governance requirements.
- Record the escalation reason and readiness verdict in the ledger.

**Completion criteria:**
- An implementation plan exists and is accepted by the delivery team.
- A production-readiness verdict (Go/No-go/Defer/Exception) is recorded with evidence.
- The release plan is documented and reviewed.

**Primary specialists:**
- [implementation-planning](../../implementation-planning/SKILL.md) — work breakdown, dependencies, rollout
- [spec-driven-development](../../spec-driven-development/SKILL.md) — formal specification and phase gates
- [production-readiness](../../production-readiness/SKILL.md) — risk-scaled launch evidence and go/no-go
- [release-engineering](../../release-engineering/SKILL.md) — release process, progressive delivery, versioning

**Supporting:**
- [neckbeard](../../neckbeard/SKILL.md) — change-request journey for the implementation itself
- [site-reliability-engineering](../../site-reliability-engineering/SKILL.md) — reliability and SLOs
- [platform-engineering](../../platform-engineering/SKILL.md) — infrastructure and CI/CD
- [secure-software-engineering](../../secure-software-engineering/SKILL.md) — security requirements and review
- [qa-methodology](../../qa-methodology/SKILL.md) — test strategy and quality gates
- [verification-methodology](../../verification-methodology/SKILL.md) — verification evidence

Note: The `production-excellence` bundle may also serve as a handoff target when
available — it composes production-readiness, migration-engineering,
resilience-and-recovery, capacity-and-cost-engineering, and incident-learning
under a single umbrella. When that bundle is installed, route to it; when it is
not, route to the individual production skills listed above.

---

## Phase 7 — Adoption

**What happens:** Drive user adoption after launch. Design onboarding, measure
activation, support behavior change, and monitor sustained use.

**Entry evidence:**
- Launch decision (Go) and release evidence from Phase 6.
- Target user segments and their needs from Phase 1.
- Success metrics from Phase 3 (roadmap outcomes).

**Output artifacts:**
- Adoption plan: onboarding design, activation path, time-to-value target.
- Segmentation and rollout record: who gets what, when.
- Activation and adoption metrics baseline.
- Behavior change and education strategy.
- Decision: adoption on track / needs intervention / pivot to re-launch.

**Escalation behavior:**
- Stop and escalate when: adoption metrics are materially below threshold after
  the intervention window; user feedback reveals a fundamental product-market
  mismatch; the adoption problem is structural (e.g., organizational resistance
  to an internal tool) and cannot be solved by product changes alone.
- A non-adoption outcome is a legitimate lifecycle result — record the evidence
  and feed into the lifecycle review (Phase 9).
- Record the escalation reason and adoption evidence in the ledger.

**Completion criteria:**
- Adoption plan is documented and executed.
- Activation, adoption, and retention baselines are measured.
- A proceed/intervene/pivot/stop decision is recorded with evidence.

**Primary specialist:** [product-adoption](../../product-adoption/SKILL.md)

**Supporting:** [go-to-market](../../go-to-market/SKILL.md) (for acquisition and positioning strategies)

---

## Phase 8 — Success

**What happens:** Measure outcomes against the success criteria defined in the
roadmap phase. Determine whether the product investment achieved its intended
results.

**Entry evidence:**
- Adoption evidence and metrics from Phase 7.
- Success criteria and leading indicators from Phase 3 (roadmap).
- Experiment readouts from Phase 5.

**Output artifacts:**
- Outcome measurement: metric tree with actuals vs. targets.
- Product analytics dashboard or report.
- Decision: success confirmed / mixed results / did not meet expectations.

**Note on customer-success routing:**
- `conditional-customer-success` is loaded ONLY for B2B subscription products
  with accounts, renewals, QBRs, and customer-success teams.
- For internal tools, public-service products, transactional products, and
  consumer products, skip customer-success routing and record the skip in the
  ledger with reason: "product type <type> — customer-success routing not applicable."

**Escalation behavior:**
- Stop and escalate when: outcomes are materially below expectations and the
  root cause is unknown after analysis; the measurement infrastructure is
  insufficient to evaluate success and cannot be remediated; or success evidence
  contradicts the original assumptions in a way that invalidates the investment
  thesis.
- Record the escalation reason and outcome evidence in the ledger.

**Completion criteria:**
- Outcome metrics are measured against success criteria.
- A success/mixed/not-met assessment is recorded with evidence.
- The ledger is complete and ready for lifecycle review.

**Primary specialist:** [product-analytics-and-measurement](../../product-analytics-and-measurement/SKILL.md)

**Conditional specialist:** [conditional-customer-success](../../conditional-customer-success/SKILL.md) (B2B subscription only)

**Supporting:** [financial-modeling](../../financial-modeling/SKILL.md) (for business outcome analysis)

---

## Phase 9 — Lifecycle review

**What happens:** Close the loop. Compare expected vs. observed outcomes, update
the assumption ledger, make a disciplined continue/improve/harvest/pivot/pause/retire
decision, and capture retained learning for future cycles.

**Entry evidence:**
- Outcome measurement and success assessment from Phase 8.
- Full lifecycle evidence ledger (all prior phases).
- Original assumptions register from Phase 2/5.

**Output artifacts:**
- Outcome review: expected vs. observed, epistemic categories (expected/observed/uncertain/inferred).
- Assumption ledger update: which assumptions held, which did not, what was learned.
- Feature health assessment across multiple dimensions.
- Lifecycle decision: continue, improve, harvest, pivot, pause, or retire.
- If retiring: deprecation communication, migration path, customer treatment plan, internal cleanup.
- Retained learning record: reusable insights fed back to roadmap, analytics, adoption, experimentation, and specifications.

**Escalation behavior:**
- Stop and escalate when: the retirement decision has material customer,
  revenue, or legal implications beyond the product team's authority; the
  retained learning contradicts a foundational organizational assumption that
  requires executive attention; or the lifecycle reveals a systemic pattern
  (e.g., third consecutive failed experiment in the same area) that suggests a
  strategy or governance issue.
- A justified retirement decision is a legitimate and valuable lifecycle outcome — record the
  evidence and retained learning, and close the lifecycle.

**Completion criteria:**
- An outcome review comparing expected vs. observed is recorded.
- A lifecycle decision (continue/improve/harvest/pivot/pause/retire) is recorded with rationale.
- Retained learning is captured in a durable, reusable format.
- The lifecycle evidence ledger is complete and closed.

**Primary specialist:** [product-lifecycle-learning](../../product-lifecycle-learning/SKILL.md)

**Supporting:** [product-operations-and-governance](../../product-operations-and-governance/SKILL.md) (for governance review and escalation)

---

## Phase skip rules

A phase may be skipped when its entry evidence is already satisfied by prior
work or the phase is not applicable to the product type. Every skip must be
recorded in the lifecycle evidence ledger with:

- The phase skipped.
- The reason (citing which entry evidence was pre-satisfied or why the phase is not applicable).
- The date and the authority for the skip.

| Phase | Skip criteria |
|---|---|
| 2 — Strategy and portfolio choice | The product is a minor enhancement to an existing bet and strategic alignment is already documented. |
| 3 — Roadmap | The work is a small, pre-prioritized task with no portfolio impact. |
| 4 — UX and requirements | The change has no user-facing behavior (backend-only, infrastructure). |
| 5 — Experimentation | The assumptions are already validated (e.g., a regulatory mandate leaves no choice). |
| 7 — Adoption | The product has no user-facing adoption surface (e.g., a backend data pipeline). |
| 8 — Customer-success routing | The product type is not B2B subscription (see Phase 8 conditional routing note). |

Phases 1 (Discovery), 6 (Delivery handoff), and 9 (Lifecycle review) may not be
skipped — they are the minimum viable lifecycle.
