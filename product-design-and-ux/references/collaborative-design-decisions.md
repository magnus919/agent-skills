# Collaborative Design Decisions

Read when a person and an agent are exploring an interface, reviewing a mockup,
or extending a previously approved flow. This is a design collaboration method,
not evidence that an attractive interface is usable or that product demand exists.

## Start from the current stage

Inspect authorized project artifacts before asking questions already answered.
Reuse the approved product scope, user research, brand guidance and component
inventory. Ask only questions whose answers could materially change the next
artifact. Accept a person's rough explanation or dictated brief, summarize the
constraints back, and separate known facts from proposals and open questions.
Do not require a long questionnaire or technical design vocabulary before showing
something useful. If the task is bounded and direction already approved, proceed
within it rather than reopening discovery.

| Stage | Human judgment needed | Agent contribution |
|---|---|---|
| Frame | Who is using this, for what outcome, and what must they notice first? | Restate the task and hierarchy; flag missing consequential constraints. |
| Explore | Which aspects of these references work or fail for this task? | Offer a small set of meaningfully different flow/layout directions, with tradeoffs. |
| Refine | Is the issue sequence, content, hierarchy, density, or visual treatment? | Change the relevant layer of an editable prototype; preserve settled choices. |
| Decide | What is accepted, for which users/states, and what remains untested? | Record the decision, rationale, exact artifact revision and bounded scope. |
| Extend | Does this new requirement fit the existing decision or need an exception? | Reuse the approved pattern and ask only about the mismatch. |

These are example questions, not a mandatory script. Ask one or a small related
set, then use the answer. Stop exploring when an authorized direction is sufficient
for the next step, or report a bounded unresolved decision instead of endless variants.

## References are evidence for a conversation

Compare complete task flows when sequence and recovery matter, not only attractive
screens. For each reference, record the particular property under discussion:
information hierarchy, navigation, pacing, density, language, or visual treatment.
A person liking a reference does not establish usability or permission to copy its
branding, proprietary assets, or interaction defects. Use permitted references and
synthetic content; do not upload private customer material without authorization.

Separate preference from evidence: 'the owner prefers this grouping' is different
from 'users found the task faster.' Treat an unfamiliar pattern as a hypothesis.
Route visual identity decisions to `brand-designer`; keep task behavior here.

## Use an editable artifact to resolve uncertainty

Choose the cheapest artifact that exposes the decision: a flow diagram, wireframe,
clickable prototype, component story or small coded mockup. A separate design app
is not required. A flat generated image may communicate mood but cannot establish
interaction, semantics, responsive behavior or recovery.

Use representative content and the states implicated by the task. Preserve an
inspectable prior revision so the person can compare changes. Diagnose what feedback
means before regenerating everything. If a requested visual change would hide an
important action, break accessibility or alter approved behavior, explain the
tradeoff and propose a safe alternative. Visual approval alone is not validation.

## Make approval useful on the next task

Use `templates/design-decision-record.md` for consequential decisions, or equivalent
fields in the project's existing design record. Do not create a competing source
of truth. Keep small records near the flow/component they govern; a project-wide
prompt is not a substitute for component examples and explicit scope.

Record proposed, approved, superseded and unresolved choices separately. Only mark
approval when the person actually provided it; record exactly what it covered.
An accepted mockup is not permission to deploy, publish or change unrelated screens.
Examples can illustrate guidance without every detail becoming an immutable rule.
If guidance conflicts or is stale, expose the conflict rather than silently choosing.

## Worked example: extend an onboarding flow

The owner approves the three-step account flow and its progress indicator, but has
not approved the draft illustration. Preserve the approved sequence and label the
illustration exploratory. When adding an invitation step, reuse established labels
and navigation components; ask whether invitation is required for completion rather
than reopening the palette. Prototype skip/re-entry behavior with synthetic data,
then hand off the resulting state contract. Do not call it user-tested unless a
real authorized study supports that claim.

## Handoff and completion

Deliver the selected artifact revision, reusable pattern/component mapping,
acceptance scope, open questions, and verification plan. Hand implementation to
`frontend-engineering` and visual identity to `brand-designer`. Check implementation
against the approved flow and relevant states, not just a hero screenshot. Report
remaining uncertainty and stop when the next owner can act without guessing.
