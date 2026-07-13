# Engineering Handoff

Handoff is a traceable behavior package, not a mockup link or presentation. It should let implementation and verification reconstruct what the user can observe, where the evidence came from, which decisions remain open, and how to prove the delivered boundary matches the approved contract.

## Required Package

Include:

- approved outcome and scope, affected users/roles, and evidence trace;
- information architecture and terminology decisions;
- task flows, state/transition inventory, recovery, permission, and side-effect models;
- interface contracts and content requirements;
- accessibility requirements routed to `web-accessibility`, with the expected evidence boundary;
- usability evidence, negative cases, fidelity limits, and untested paths;
- data/content/service dependencies, ownership, freshness, fallback, and failure behavior;
- telemetry purpose and minimum event contract where evidence requires it;
- implementation risks, unresolved decisions, owners, and gates;
- observable acceptance criteria and deployed-boundary verification plan.

Do not attach a pile of artifacts without a navigation surface. `templates/engineering-handoff.md` is the index and gate record; link every supporting artifact from it.

## Observable Acceptance Criteria

Write criteria at the user-facing or deployed boundary. A useful criterion identifies:

1. entry condition, role, permission, and relevant data state;
2. action or external event;
3. visible behavior and state transition;
4. persistence or side effect, including partial/failure behavior;
5. recovery, interruption/re-entry, and completion evidence where applicable;
6. accessibility expectation and routed test evidence;
7. exact environment, fixture, observation, and result record.

Avoid “works well,” “is intuitive,” “is responsive,” or “is accessible.” Replace them with observable behavior. Do not force a binary criterion when the open decision genuinely needs research; record the decision and gate instead.

## Dependency Contract

For each content, data, service, policy, permission, or platform dependency, record:

| Field | Question |
|---|---|
| Provider/owner | Who can answer and change it? |
| Contract/source | What schema, content source, policy, or platform behavior is expected? |
| Freshness and availability | When can it be stale, delayed, missing, or revoked? |
| Failure/fallback | What does the person see and retain when it fails? |
| Privacy/security boundary | What data or authority crosses the boundary? |
| Verification | How will implementation and deployed behavior be checked? |

A dependency without an owner or fallback is an unresolved design risk, not an engineering detail.

## Handoff Review

Run a walkthrough using at least one normal path and the highest-risk permission, interruption, partial-commit, stale/conflict, or failure path. Trace each behavior backward to evidence or an explicit assumption and forward to an acceptance criterion. Confirm no mockup-only state, inaccessible interaction, placeholder content, or simulated side effect is represented as complete.

Classify findings:

- **Blocking:** implementation would invent consequential behavior, expose unsafe data/action, omit required recovery, or lack a testable contract.
- **Conditional:** an owner and resolution gate exist and implementation can proceed without guessing past that gate.
- **Nonblocking:** clarification improves maintainability without changing behavior or risk.

## Deployed-Boundary Verification

Component or prototype success does not prove integration behavior. Name the actual delivery boundary, supported environment, fixture, steps, expected observation, evidence capture, and cleanup. Include permissions, persistence, external effects, responsive behavior, and accessibility environment where relevant. Record failed, blocked, and not-applicable results instead of converting absent evidence into a pass.

After approval, pass the interaction contracts and criteria to [spec-driven-development](../../spec-driven-development/SKILL.md) for formal software specification and delivery gates. Keep UX evidence linked rather than flattening it into implementation prose.
