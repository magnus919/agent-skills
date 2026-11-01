# Product design and UX audit — #763

**Recommend a narrow follow-on to align legacy eval expectations with the current
skill, rather than expanding the UX method.** Two inspected cases over-prescribe
implementation or research choices that the current references leave evidence-dependent.
A third expected answer needs a narrower clarification. This is a source/rubric consistency finding, not an observed
model failure or measured user harm. No skill or eval implementation is included;
any repair remains a separately scoped follow-on.

## Scope, revision, and evidence

Pinned source: `67ef94cc7958e43f956add2fcb83325f03bff88c`.
`inspection.json` preserves hashes for all skill files and the complete seven-case
inspection corpus. The supplied embedded-loan reference hash was recalculated and
matches its recorded reference-input hash. That proves source identity only.

Inspected the entrypoint, human README, interface/state/usability/AI/external-agent/
handoff references and templates, scenario probes, eval manifest, embedded-loan
worked example and rubric challenges. There is no executable scripts/ directory;
this skill owns behavior design, not a design-tool runtime. No fresh generated
model output, recruited participant, prototype, browser/assistive-technology test,
backend action, usability result or calibrated grader score is claimed.

Completed prior art reviewed before recommending a change:

- [#24](https://github.com/magnus919/agent-skills/issues/24): the approved middle
  layer is behavior design between discovery and specification, with no visual-brand,
  CSS, proprietary-tool or frontend dependency ownership.
- [#494](https://github.com/magnus919/agent-skills/issues/494), delivered by #504:
  uncertainty, human control, source freshness, correction, opt-out, feedback and
  model-change contracts already exist. Another AI-conversation umbrella duplicates it.
- [#656](https://github.com/magnus919/agent-skills/issues/656), delivered by #657:
  cross-app delegation, distinct principals, cancellation/partial effects and
  product-side evidence are already explicit.
- Eval-backfill/refinement history includes #237/#261, #683's embedded-loan pattern
  and #685's bounded reference-input work. The current embedded reference hash is
  valid; missing references were not assumed from historical defect reports.
- `docs/agent-interface-enrichment-results.md` retains a historical matched
  design-response screen and its limitations: one response per condition, shared
  within-suite context, no tool execution or user study, and corrected model-teacher
  over-crediting. This audit reviewed the record; it did not repeat or independently
  adjudicate that run or promote its labels to ground truth.

## Seven representative tasks

These are existing reproducible output fixtures, not actual-user accounts. The
outcomes are analyst source/task inspection. A row labeled covered means the
instructions contain the needed mechanism, not that a new agent response passed.

| Case / job | Current decision and artifact path | Inspection outcome / gap |
|---|---|---|
| task-flow-design: invite teammates end to end | Workflow step 4, task-flow/state model, recipient-side acceptance and role assignment | Covers inviter/invitee, partial batches, revocation and unresolved decisions. No new flow artifact or live email/account outcome was tested |
| state-recovery-model: checkout loses work | State/recovery reference, privacy limits, permission and persistence fields in interface contract | Recovery mechanism exists; legacy expected_output proposes local autosave without a permitted-data boundary. The broader assertion permits autosave and does not itself require local storage |
| interface-contract-handoff: search states and spacing drift | Interface-contract reference says behavior, leaving coordinates/CSS/props to implementation unless constrained; template records actions, states, permission, recovery and evidence | Legacy assertion requires concrete spacing/sizing tokens even though no design system/token values were supplied. A sound behavior contract can instead link an implementation constraint or flag missing tokens |
| usability-study-plan: test navigation before build | Usability/privacy reference chooses participation by decision risk and variation; template requires owner, consent, accommodations, fidelity, limits and empty-until-observed results | Legacy expected_output gives 5–8 participants and prescribes moderated think-aloud; an assertion requires that protocol rather than permitting an equally justified task-based method |
| ai-human-control-boundary: recommend or execute account changes | AI interaction contract compares modes/stakes and separates preview, approval, current authorization, commit and partial recovery | Method covered; runtime grants, server enforcement and verified effects remain with runtime/security owners, not UX prose |
| external-agent-cross-app-delegation: three records across apps | External handoff contract separates human/product/integration principals, unknown identity and cooperative cancellation, partial results and inspectable return path | Method covered; actual host/product support cannot be inferred from protocol or agent claim. No new actor attribution or cancellation guarantee was invented |
| embedded-loan-recovery: revoked permission, timeout, partial effects | Filled loan contract binds preview/revision/policy; rechecks execution authority; queries persisted command ID; separates reservation from failed notification | Synthetic end-to-end design is coherent and its supplied reference hash matches. No reservation, accessibility result, listening/visual result or observed usability is claimed |

## Repeated finding: legacy rubrics prescribe incidental choices

The consequential common mechanism is **evaluating an evidence-dependent design as
if one implementation or research protocol were mandatory**. Two direct rubric tensions and one narrower expectation ambiguity
support reviewing the cases; none proves that a runtime model followed
the wrong choice.

| Finding | Exact current tension | Why review matters / counterexample |
|---|---|---|
| U1 safe persistence | state-recovery-model expected_output says input is autosaved locally; its assertion allows autosave or local persistence. No field classification, retention or architecture is supplied | Server-side autosave of permitted fields can satisfy the existing assertion; clarify the expected example rather than claiming the assertion necessarily rejects it. Do not infer sensitive-field permission from the example |
| U2 supplied design constraints | interface-contract-handoff requires “concrete spacing and sizing tokens”; the current reference explicitly excludes styling/component names except supplied constraints | A response may identify missing token definitions, link the design-system owner, and still specify complete states, focus, recovery and acceptance; invented token values would not fix actual drift |
| U3 research fit | usability-study-plan expected_output gives 5–8 participants and its assertion specifies moderated think-aloud; the current method rejects a universal count or protocol | A reasoned task-based remote/tree test or different formative sample may answer the decision; do not reward participant-count recitation without a rationale |

These counterexamples are authored challenge fragments, not independent labels.
A satisfying response preserves the consequential behavior, grounds constraints,
and states unknowns. A contrary near miss stores sensitive checkout fields without
limits, invents design tokens, or treats one participant count as universally valid.
An omission supplies no recovery, no verifiable interface behavior, or no task-based
study plan. Review each property separately; do not replace semantic quality with
keyword checks or tune Jev inputs to reward these fragments.

## Coverage map and scope answers

- Visually plausible but unusable designs: state/permission/recovery/recipient paths,
  human action/commit boundaries and observable receipts are already explicit. This
  audit did not observe real generated interfaces, so cannot estimate that failure rate.
- #494 end-to-end uncertainty: the loan example composes provenance, edits, approval,
  revalidation and recovery; external-agent guidance covers cross-app handoffs. Their
  actual usability remains untested here, not silently promoted from source coverage.
- Accessibility and responsiveness: contracts carry names/roles/states, focus,
  width/reflow/text expansion/input constraints and recovery; detailed WCAG/ARIA and
  conformance evidence route to web-accessibility. This is a concrete contract handoff,
  not proof that a built interface conforms.
- Design-system constraints and implementation: link supplied constraints and the
  implementation owner; the behavior skill should not invent tokens or CSS. The
  legacy rubric tension is narrower than a missing design-system capability.
- Research evidence: observation, participant report, inference and decisions remain
  distinct; results stay empty without authorized observations. No recruitment occurred.
- Deterministic checks/templates: existing contracts and one reference-hash check are
  useful bounded mechanisms. They cannot prove usability or safe side effects. A
  new universal UX scoring script is unsupported by these findings.
- Trigger boundaries: description starts after validated discovery/approved scope;
  body excludes brand/pixels/CSS and routes accessibility and implementation outward.
  No client activation was executed, so over-trigger frequency is unknown. The new
  catalog router (#755/#761) handles common-language discovery without duplicating UX.

## Primary comparison

Checked 2026-11-01:

- [GOV.UK moderated usability guidance](https://www.gov.uk/service-manual/user-research/using-moderated-usability-testing) ties task design to research questions and actual/likely users, with neutral goals and appropriate data safeguards. It illustrates a method; it does not make that method universal.
- [Microsoft HAX guidelines](https://www.microsoft.com/en-us/haxtoolkit/ai-guidelines/) frames AI interaction across initial use, ongoing use, errors and time, and asks teams to prioritize applicability. This supports the existing conditional contracts rather than a new universal interface pattern.

These sources motivate the audit comparison; they do not validate this product,
set a local research sample size, or replace accessibility/authority evidence.

## Smallest next increment and rejected ideas

Proposed follow-on: **review only the three named legacy eval cases against their
current owning references**, preserve stable IDs/schema and meaningful required
outcomes, and allow evidence-equivalent persistence, supplied design constraints,
and justified study methods. Record satisfying/contrary/missing challenge outputs
for every material assertion revision. Do not change the skill to fit an over-specific
rubric or bulk-rewrite other manifests.

Value: avoid rewarding unsafe or fabricated specifics and penalizing valid design
alternatives. Effort: three bounded case/rubric reviews plus focused validation;
no new subsystem, tool or user study is required to review consistency. Acceptance:
case IDs stay stable, essential recovery/state/evidence properties stay required,
safe equivalent fragments remain distinguishable from contrary and absent evidence,
manifest/coverage checks pass, and model-teacher opinions remain advisory. A real
behavioral improvement claim would additionally require matched held-out actual
outputs with independent review; no such claim is made here. Implementation needs
a separately approved follow-on, as required by #763.

Rejected: new AI-UX umbrella (duplicates #494), new external-agent skill (duplicates
#656), mandatory frontend component library or CSS manual (wrong owner), automatic
UX score from template completion (unsupported quality inference), and claims of
actual demand or usability from raw install counters. A broad UX expansion is not
supported. No-change is appropriate for the inspected core method; the narrower
rubric-consistency recommendation remains open for separately approved repair.
