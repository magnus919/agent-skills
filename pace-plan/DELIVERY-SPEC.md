# Specification: Issue #159 Research Remediation and `pace-plan` Delivery

## Status

- **Author:** OpenCode
- **Version:** 1.0.0
- **Status:** Approved
- **Reviewed by:** OpenCode plus independent issue/spec and safety/source review agents
- **Gate verdict:** Approved

## Problem Statement

The research performed for issue #159 damaged reusable `research-methodology` templates, overstated what retained sources support, published those claims to GitHub without explicit authorization, and stopped short of specifying all repository and operational safeguards needed for the requested `pace-plan` skill. The work must be repaired without losing valid evidence, and issue #159 must then be implemented as a concise, source-grounded Agent Skills skill.

## Success Criteria

1. The reusable `research-methodology` assets are byte-for-byte equivalent to their state at `HEAD` before the issue #159 investigation.
2. Every retained factual claim has a directly inspected source, exact citation, access date, and calibrated confidence; no synthesis claim exceeds its evidence.
3. No repository artifact attributes testing cadence, HSEEP, after-action procedures, or quantitative metrics to CISA's four-page PACE publication unless an exact supporting passage is cited.
4. The external GitHub comment remains unchanged until the user explicitly confirms the target, scope, and rollback path.
5. A new `pace-plan` skill satisfies issue #159, repository format rules, all required eval cases, and the state-modification safety gate.
6. All repository skill and eval validators pass, and generated catalog checks report no stale tracked artifacts.

## Scope

### In Scope

- Restore the two overwritten `research-methodology/assets/` templates.
- Preserve valid issue #159 research in a destination that does not alter another skill's reusable assets.
- Re-evaluate every source and remove, reclassify, or independently source unsupported claims.
- Define and, after explicit approval, correct the existing GitHub issue comment.
- Create the complete top-level `pace-plan` skill requested by issue #159.
- Add required human documentation, focused references, four operational templates, and at least five output-quality eval cases.
- Validate skill format, local references, eval schema, and generated catalog freshness.
- Remove superseded issue-specific scratch artifacts only after all retained evidence has been migrated.

### Out of Scope (Explicit)

- Inventing local frequencies, channels, talkgroups, contact details, call signs, infrastructure, permissions, or activation authority.
- Giving medical, law-enforcement, firefighting, public-warning, or other public-safety operational instructions.
- Defining radio programming, frequency allocation, channel plans, deployment plans, or vendor-specific procedures.
- Building a CLI, validator script, generator, web application, or external service for PACE plans.
- Activating, transmitting on, testing, or changing a real communications system.
- Deleting or editing the GitHub comment without a separate explicit approval.
- Committing, pushing, or opening a pull request unless separately requested.

## Source Authority Contract

Factual claims used by the implementation must be classified as follows:

| Class | Meaning | Permitted wording |
|---|---|---|
| Primary-direct | The retained primary source was directly inspected and contains the cited passage | State as fact with exact citation |
| Secondary-direct | A retained secondary source was directly inspected | Attribute explicitly to that source |
| Indirect | Only a citation, quotation, or summary in another source was inspected | State as indirect or omit |
| Synthesis | Derived by comparing retained evidence or applying repository conventions | Label as a design decision or recommendation |
| Unsupported | No inspected source supports the claim | Remove |

The CISA publication at `https://www.cisa.gov/sites/default/files/2024-10/2024_NCSWICPTE_Leveraging_PACE_Plan_Emergency_Comms_Ecosystems.pdf` supports redundancy, distinguishable paths, explicit triggers, collaborative planning, regular training, and exercises. It must not be cited as prescribing daily/monthly/quarterly cadence, HSEEP, hot washes, AAR/IP workflows, corrective-action matrices, setup-time metrics, or success-rate metrics unless another directly inspected source independently supports those details.

## User Stories

### US-001: Restore Reusable Research Assets

**Priority:** P0
**Description:** As a maintainer, I want issue-specific research removed from reusable templates so future investigations start from intact assets.

**Acceptance Criteria:**

1. [AC-001.1] Given the current worktree, when remediation is complete, then `research-methodology/assets/research-brief.md` is byte-for-byte equal to `HEAD:research-methodology/assets/research-brief.md`.
2. [AC-001.2] Given the current worktree, when remediation is complete, then `research-methodology/assets/research-log.md` is byte-for-byte equal to `HEAD:research-methodology/assets/research-log.md`.
3. [AC-001.3] Given valid issue #159 evidence in the overwritten files or scratch dossier, when the templates are restored, then retained evidence has first been migrated to its final issue-specific or `pace-plan` destination.
4. [AC-001.4] Given unrelated worktree changes, when restoration occurs, then no file outside the issue #159 change set is modified or reverted.

**Edge Cases:**

- The reusable templates contain concurrent user edits beyond the issue-specific replacement: stop and ask before restoring.
- A claim exists only in an overwritten template: migrate and classify it before restoration.
- `HEAD` changes during implementation: compare against the implementation session's starting commit and report the commit ID.
- The scratch dossier contains duplicate claims: preserve one evidence record and note deduplication.

### US-002: Rebuild the Evidence Record

**Priority:** P0
**Description:** As a future skill maintainer, I want a traceable evidence base so every operational instruction can be audited and updated.

**Acceptance Criteria:**

1. [AC-002.1] Given each retained source, when the evidence base is complete, then it records title, author or issuing body, exact URL, publication date when known, access date, source-authority class, and availability status.
2. [AC-002.2] Given each material claim, when it appears in the evidence base, then it has an exact quotation or bounded paraphrase and a page, section, or line locator.
3. [AC-002.3] Given Ryan (2013) or NIFOG material that was not directly inspected, when retained, then it is classified `Indirect` and is not presented as independently verified.
4. [AC-002.4] Given a numerical source score, when it is retained, then the scoring rubric and per-dimension values are recorded; otherwise the numerical score is removed.
5. [AC-002.5] Given rejected, inaccessible, superseded, or redundant sources, when research closes, then each has an explicit exclusion reason.
6. [AC-002.6] Given the claim that no overlapping public skill exists, when retained, then the searched catalogs, queries, date, and limitations are recorded; otherwise the claim is narrowed to the inspected repository.

**Edge Cases:**

- A primary URL is dead but an official archive exists: cite the archive and record the original URL separately.
- A secondary source quotes an inaccessible primary source: retain only as indirect evidence.
- Two government documents disagree: preserve both and state the unresolved contradiction.
- A source is live but cannot be text-extracted: record the limitation and do not infer unseen content.
- A source changes after access: preserve publication/version metadata sufficient to identify the inspected edition.

### US-003: Correct the Research Synthesis

**Priority:** P0
**Description:** As an issue reader, I want recommendations that distinguish sourced PACE doctrine from repository-specific skill design decisions.

**Acceptance Criteria:**

1. [AC-003.1] Given the corrected synthesis, when it describes canonical PACE behavior, then it covers mission or function, communication parties, P/A/C/E order, distinguishable dependencies, transition triggers, sender and receiver feasibility, training, and exercises only to the extent supported by inspected sources.
2. [AC-003.2] Given cadence, HSEEP, AAR, improvement planning, metrics, or troubleshooting sequences, when no directly inspected source supports a detail, then it is removed or explicitly labeled as an unsourced proposal requiring validation.
3. [AC-003.3] Given lifecycle phase names, when used anywhere, then one vocabulary is used consistently: `PLAN`, `COORDINATE`, `OPERATE`, `TROUBLESHOOT`, `EXERCISE`, `IMPROVE`.
4. [AC-003.4] Given statements such as "definitive," "standardized," "most common," "most dangerous," or "guarantees," when retained, then the evidence base explicitly supports that comparative claim; otherwise neutral wording replaces it.
5. [AC-003.5] Given the corrected synthesis, when confidence is reported, then confidence is calibrated per finding rather than asserted globally from source count.

**Edge Cases:**

- A recommendation is operationally sensible but unsourced: label it `Design decision`, not doctrine.
- A source supports exercises but no cadence: require a plan-local cadence without prescribing one.
- A source uses military authority language: translate only the planning concept, not military command assumptions.
- PACE cannot provide four feasible methods: preserve the gap explicitly instead of inventing a tier.

### US-004: Correct the Published GitHub Record Safely

**Priority:** P0
**Description:** As the repository owner, I want the inaccurate issue comment corrected without another unauthorized external mutation.

**Acceptance Criteria:**

1. [AC-004.1] Given issue comment `5086185139`, when no explicit approval has been received, then no GitHub mutation occurs.
2. [AC-004.2] Before any mutation, the user is shown the exact target, proposed scope, original-body backup location, proposed replacement or follow-up text, and rollback command or API operation.
3. [AC-004.3] Given explicit approval, when the correction is applied, then unsupported CISA cadence/HSEEP/metrics claims and the `false-redudancy` typo are corrected.
4. [AC-004.4] Given explicit approval, when the correction is applied, then links point only to durable artifacts that exist in the final repository state or to stable external sources.
5. [AC-004.5] After mutation, the issue is fetched again and the returned comment body is compared with the approved text.
6. [AC-004.6] If verification fails, the original saved body is restored and the failure is reported.

**Edge Cases:**

- The comment was edited by another actor after this specification: stop and request a new decision.
- GitHub rejects editing but permits replies: ask whether to post a correction reply; do not choose automatically.
- The user prefers deletion: require an explicit destructive directive before deleting.
- Durable artifact URLs are unavailable until a branch or PR exists: omit them rather than linking to local paths.

### US-005: Implement the `pace-plan` Skill

**Priority:** P0
**Description:** As a group supporting emergency communications, I want an agent skill that helps us plan, coordinate, operate, troubleshoot, exercise, and improve an authorized PACE plan without inventing local facts or authority.

**Acceptance Criteria:**

1. [AC-005.1] A top-level `pace-plan/SKILL.md` exists with valid frontmatter; `name` equals `pace-plan`; the description starts imperatively and states positive and negative trigger boundaries.
2. [AC-005.2] `SKILL.md` stays below 500 lines and 5,000 tokens and conditionally routes detail to focused one-level references and templates.
3. [AC-005.3] The skill distinguishes emergency communications path resilience from generic project incident messaging, radio programming, frequency/channel planning, and unauthorized real-world activation.
4. [AC-005.4] Before the first real external mutation, transmission, activation, or live-system test, the skill requires: `Confirm the target, scope, and rollback path before acting. Read-only discovery may proceed without confirmation.`
5. [AC-005.5] Every P/A/C/E path captures purpose, operational use, owner, participants, decision or activation authority, prerequisites, interoperability constraints, dependencies, contact/check-in/escalation/fallback procedure, activation trigger, abandonment criteria, verification evidence, bounded test, failure modes, troubleshooting, recovery or handoff, review cadence, findings, corrective actions, and change record.
6. [AC-005.6] Unknown local facts remain explicitly `UNKNOWN` with an owner and validation action; no plausible replacement is generated.
7. [AC-005.7] The skill never invents frequencies, channels, talkgroups, contacts, regulatory permission, medical/public-safety instructions, or authority to transmit or activate.
8. [AC-005.8] The skill requires deference to authorized operating procedures, applicable regulation, and incident leadership.
9. [AC-005.9] The skill's completion gate requires owner approval, defined triggers and check-ins, exercises to the available extent, and recorded unresolved gaps with owners and follow-up actions.
10. [AC-005.10] The skill uses `PACE` consistently as Primary, Alternate, Contingency, and Emergency.

**Edge Cases:**

- Only two feasible communication paths exist: document missing C/E tiers as owned gaps.
- Two paths use different applications over one network: flag the shared dependency for human review.
- Sender and receiver capabilities differ: do not mark the path viable until both ends are validated.
- No authorized activator is identified: planning may continue, but execution remains blocked.
- A user asks the agent to transmit or activate without authority evidence: refuse the mutation and identify the required decision-maker.
- An exercise cannot safely test the Emergency path: record the limitation and use the most representative authorized bounded test.
- The scenario involves immediate danger: defer to emergency services and authorized incident procedures rather than improvising instructions.

### US-006: Provide the Required Operational Artifacts

**Priority:** P0
**Description:** As a plan owner, I want reusable artifacts that make the plan operable and auditable rather than merely descriptive.

**Acceptance Criteria:**

1. [AC-006.1] `pace-plan/templates/pace-plan-worksheet.md` covers every field in AC-005.5 and includes dependency-independence checks.
2. [AC-006.2] `pace-plan/templates/communications-check-in-card.md` contains plan-local contact/check-in/escalation/fallback fields without example operational identifiers that could be mistaken for real values.
3. [AC-006.3] `pace-plan/templates/exercise-and-after-action-review.md` contains authorization, safety bounds, objectives, injects, expected evidence, observations, findings, corrective actions, owners, due dates, validation action, and next review.
4. [AC-006.4] `pace-plan/templates/troubleshooting-decision-log.md` records observed symptom, current tier, checks performed, evidence, decision authority, transition decision, recovery or handoff, and follow-up.
5. [AC-006.5] Templates represent missing facts as `UNKNOWN`, `OWNER`, and `VALIDATION ACTION` fields rather than illustrative local details.
6. [AC-006.6] Conditional references cover plan design, coordination and authorized operation, troubleshooting, and exercise/improvement governance without duplicating the templates.

**Edge Cases:**

- A template field does not apply: require `N/A` plus rationale rather than leaving it ambiguous.
- A template contains sensitive contact information: instruct users to store and distribute it according to local policy.
- Corrective action has no owner or due date: keep it open and fail completion.
- Exercise observations conflict: preserve both observations and assign a validation action.

### US-007: Add Representative Output-Quality Evals

**Priority:** P0
**Description:** As a maintainer, I want executable contract cases that detect unsafe assumptions and lifecycle regressions.

**Acceptance Criteria:**

1. [AC-007.1] `pace-plan/evals/evals.json` uses schema version 1, names `pace-plan`, and contains at least five cases with stable kebab-case IDs, realistic prompts, expected outcomes, and observable `assertions`.
2. [AC-007.2] The manifest includes `incomplete-plan-discovery`, which asserts explicit unknowns, owners, validation actions, and no invented local details.
3. [AC-007.3] The manifest includes `failed-primary-path-drill`, which asserts authority checks, observable transition criteria, and bounded exercise behavior.
4. [AC-007.4] The manifest includes `coordination-handoff`, which asserts named ownership, sender/receiver alignment, and escalation or handoff evidence.
5. [AC-007.5] The manifest includes `troubleshooting-scenario`, which asserts evidence-led checks, shared-dependency detection, and no unsupported technical commands.
6. [AC-007.6] The manifest includes `after-action-improvement-cycle`, which asserts findings, corrective actions, owners, validation actions, unresolved gaps, and next review.
7. [AC-007.7] At least one case asserts refusal or blocking when a user requests unauthorized transmission or activation.
8. [AC-007.8] Trigger-only probes are not placed in `evals/evals.json`; separately documented probes include at least three should-trigger and two should-not-trigger near misses.

**Edge Cases:**

- A case tests only keyword presence: replace it with observable behavioral assertions.
- Two eval IDs collide or an ID is renamed after evidence is recorded: fail validation.
- A prompt includes real-looking operational details: use unmistakable placeholders.
- A boundary prompt combines incident messaging and emergency path planning: expected output must route only the PACE portion to this skill.

### US-008: Validate and Clean the Final Change Set

**Priority:** P0
**Description:** As a maintainer, I want reproducible evidence that the repaired work and new skill satisfy repository contracts without collateral changes.

**Acceptance Criteria:**

1. [AC-008.1] `ruby scripts/validate-skills.rb` exits 0.
2. [AC-008.2] `python3 scripts/validate-evals.py pace-plan/evals/evals.json` or the repository-supported focused equivalent exits 0; if only whole-repository validation is supported, that command exits 0.
3. [AC-008.3] `python3 scripts/test-eval-validation.py` exits 0 in the documented development environment.
4. [AC-008.4] `ruby scripts/gen-claude-marketplace.rb`, `ruby scripts/gen-codex-plugin.rb`, and `ruby scripts/gen-llms-txt.rb` check modes exit 0; if stale, generated artifacts are regenerated with documented `--write` commands and rechecked.
5. [AC-008.5] The final diff contains only restored templates, the complete `pace-plan` skill, required generated catalog updates, and an issue-specific evidence destination if retained.
6. [AC-008.6] Superseded `pace-planning/` scratch files are removed only after a preservation check confirms no unique retained evidence will be lost.
7. [AC-008.7] Final verification reports each AC as PASS, FAIL, or BLOCKED with command output or direct file evidence.

**Edge Cases:**

- A validator is unavailable: report BLOCKED and perform named manual checks without claiming validator success.
- Whole-repository validation fails on an unrelated pre-existing defect: isolate and report it; do not modify unrelated files.
- Generated artifacts include concurrent changes: inspect and preserve them rather than regenerating blindly.
- The worktree changes during validation: re-run status and diff before declaring completion.

## Non-Functional Requirements

| ID | Requirement | Threshold | Verification Method |
|---|---|---|---|
| NFR-001 | Source fidelity | 100% of retained factual claims have a source class and locator | Evidence-ledger audit |
| NFR-002 | Unsupported attribution | 0 unsupported claims attributed to CISA or another source | Search claims and compare to source passages |
| NFR-003 | Unknown preservation | 100% of missing operational facts remain explicit unknowns with owner and validation action | Template and eval inspection |
| NFR-004 | Authority safety | 100% of live mutation/activation paths encounter the confirmation gate first | SKILL review plus unsafe-request eval |
| NFR-005 | Progressive disclosure | `SKILL.md` under 500 lines and 5,000 tokens; references one level deep | Line/token count and link validation |
| NFR-006 | Eval coverage | At least 5 required scenarios plus 1 unauthorized-action assertion | Eval manifest inspection and validation |
| NFR-007 | Repository integrity | 0 unrelated files modified or reverted | Starting/final `git status` and diff comparison |
| NFR-008 | Portability | No vendor, harness, radio service, or jurisdiction required for core use | Content review |

## Data Contracts & Interfaces

### PACE Path Record

Each Primary, Alternate, Contingency, and Emergency entry must expose this semantic contract, whether represented as Markdown fields or a table:

```yaml
tier: primary | alternate | contingency | emergency
purpose: string | UNKNOWN
operational_use: string | UNKNOWN
owner: string | UNKNOWN
participants: [string] | UNKNOWN
decision_authority: string | UNKNOWN
activation_authority: string | UNKNOWN
prerequisites: [string]
interoperability_constraints: [string]
dependencies: [string]
shared_dependency_findings: [string]
contact_procedure: string | UNKNOWN
check_in_procedure: string | UNKNOWN
escalation_procedure: string | UNKNOWN
fallback_procedure: string | UNKNOWN
activation_trigger: string | UNKNOWN
abandonment_criteria: string | UNKNOWN
verification_method: string | UNKNOWN
expected_evidence: string | UNKNOWN
bounded_test: string | UNKNOWN
known_failure_modes: [string]
troubleshooting_sequence: [string]
recovery_or_handoff: string | UNKNOWN
last_reviewed: date | UNKNOWN
exercise_findings: [string]
corrective_actions: [string]
change_record: [string]
unknown_owner: string | null
validation_action: string | null
```

### External Mutation Approval Record

```yaml
target: "https://github.com/magnus919/agent-skills/issues/159#issuecomment-5086185139"
scope: "Correct factual attributions, typo, and invalid artifact links only"
rollback:
  original_body_backup: string
  restore_operation: string
approved_by: string
approved_at: datetime
approved_text_hash: string
```

No GitHub mutation may occur unless every field is populated and approval is explicit in the conversation.

## Dependency and Delivery Order

```text
US-001 Restore templates --+
                           +--> US-002 Rebuild evidence --> US-003 Correct synthesis
Scratch dossier -----------+                                  |
                                                              +--> US-005 Implement skill
Explicit user approval --> US-004 Correct GitHub record       |        |
                                                                       +--> US-006 Artifacts
                                                                       +--> US-007 Evals
                                                                       +--> US-008 Validate and clean
```

Rules:

1. Do not author normative skill instructions from the current synthesis before US-002 and US-003 pass.
2. US-004 can proceed only after explicit approval and can otherwise remain BLOCKED without blocking local skill implementation.
3. Do not remove scratch evidence until US-002 preservation and US-008 cleanup checks pass.
4. Do not claim issue #159 complete until US-005 through US-008 pass and US-004 is either completed or explicitly waived by the user.

## Review-Finding Traceability

| Review finding | Remediation requirements |
|---|---|
| Canonical templates overwritten | US-001, AC-008.5 |
| Unsupported CISA claims | Source Authority Contract, US-002, US-003, NFR-001, NFR-002 |
| Unverified evidence marked verified | AC-002.1 through AC-002.6, AC-003.5 |
| Unauthorized GitHub mutation | US-004, External Mutation Approval Record |
| Missing state-modification safeguard | AC-005.4, NFR-004, AC-007.7 |
| Completion condition underspecified | AC-005.9, AC-006.3, AC-007.6 |
| Fragmented/false durable preservation | AC-001.3, US-002, AC-008.6 |
| Scope drift and inconsistent lifecycle | Out of Scope, AC-003.3, AC-005.2, US-006 |
| Original issue not implemented | US-005 through US-008 |

## Assumptions & Open Questions

| # | Assumption / Question | Impact if Wrong | Resolution |
|---|---|---|---|
| 1 | The user wants a full remediation and delivery spec, not immediate implementation | Work may exceed the intended scope | This artifact stops at Gate 1 pending review |
| 2 | `pace-planning/` contains only artifacts created during the flawed research pass | Cleanup could delete someone else's work | Verify provenance and current worktree before deletion |
| 3 | A tracked issue-specific evidence file is desirable inside the final `pace-plan` skill | A public skill may carry unnecessary research process detail | At decomposition, choose focused `references/evidence-base.md` only if it materially helps future maintenance; otherwise preserve evidence in the approved issue/PR record |
| 4 | The existing GitHub comment should be corrected rather than silently deleted | The owner may prefer deletion or a follow-up correction | Ask for explicit target/scope/rollback approval and preferred correction mode |
| 5 | CISA's publication date and footer date differ (`2024` URL/publication, `As of 2023` footer) | Citation metadata could be misleading | Record both publication listing and document footer metadata |
| 6 | No executable script is needed for the skill | A future concrete need may emerge | Keep scripts out of scope until a demonstrated repetitive computation requires one |

## Gate 1 Review Checklist

- [x] Every acceptance criterion has a binary PASS/FAIL test.
- [x] Every review finding maps to at least one acceptance criterion.
- [x] External mutation remains separately approval-gated.
- [x] Source doctrine and design synthesis are explicitly distinguished.
- [x] Original issue requirements are represented without adding vendor-specific behavior.
- [x] Required README, references, templates, evals, and validation commands are covered.
- [x] Edge cases include missing tiers, shared dependencies, mismatched endpoints, absent authority, unsafe activation, inaccessible sources, and concurrent worktree changes.

## Revision History

| Version | Date | Author | Change |
|---|---|---|---|
| 0.1.0 | 2026-07-26 | OpenCode | Initial remediation and delivery specification |
| 1.0.0 | 2026-07-26 | OpenCode | Approved after implementation, independent review, and repository-boundary verification |
