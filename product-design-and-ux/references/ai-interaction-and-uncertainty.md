# AI Interaction and Uncertainty

Use this reference when a product includes generated content, predictions, recommendations, classification, conversational input, retrieval, or an AI system that can call tools. It extends the general task-flow, state-model, interface-contract, usability, and handoff workflow. It does not select models, implement evaluation or telemetry systems, define organization-wide governance, or operate production agents.

## Entry boundary

Start with an approved outcome and evidence. Record the task, affected roles, decision owner, system role, relevant data/context sources, freshness, constraints, and what remains human-controlled. State whether the system assists, drafts, recommends, ranks, predicts, routes, or executes. If the problem, scope, or success measure is unvalidated, route upstream to `product-discovery`, `product-methodology`, or `ai-operating-economics`.

## Choose the control boundary

Treat interaction mode as a hypothesis. Compare a conventional interaction, AI assistance, AI recommendation, and AI execution against:

| Force | Questions |
|---|---|
| Stakes and reversibility | What is the harm of a wrong output or action? Can a person inspect, edit, undo, or contain it? |
| Ambiguity and observability | Can the user and reviewer recognize an unsupported or wrong result? What evidence is available? |
| Frequency and review burden | How often does the task occur? Does review remove the claimed benefit or create a new queue? |
| Data and context | Are inputs permitted, current, complete, and relevant? How are conflicts and missing context shown? |
| Authority and side effects | Which actions are drafts or recommendations, and which cross an external commit boundary? |
| User capability and access | What expertise, language, modality, and assistive input must the flow support? |

Higher stakes, weak observability, irreversible effects, or unclear authority generally require a meaningful human review or approval point. A good offline score or pilot result does not by itself authorize broader autonomy. Record the selected boundary, alternatives, evidence, owner, and revisit trigger.

## Make uncertainty useful

Specify behavior for evidence that is weak, conflicting, missing, stale, outside the supported task, or unsafe. The interface should make the limitation actionable: ask for clarification, show the relevant source or input boundary where it is available, offer a safe fallback, preserve the user’s work, or escalate. Do not invent a confidence number, rationale, citation, or “understanding” claim merely to make an answer feel certain.

Separate:

- **Draft or suggestion:** the person can inspect and edit it; no external effect is implied.
- **Decision support:** the system presents evidence and tradeoffs; the authorized person makes the decision.
- **Action:** the system may cause a side effect only after the defined authorization, validation, and commit boundary.

For each output, define the correction, edit, reject, retry, clarify, source-inspection, fallback, and escalation actions that are actually supported. Preserve relevant input and context through those paths.

## Model states and recovery

Add only states forced by the task and system boundary. Typical AI-specific states include pending or streaming, partial, complete, unsupported or uncertain, stale/conflicting context, blocked by permission or policy, failed, escalated, corrected, and committed. For each state, specify the visible status, retained work, permitted actions, transition, and completion evidence.

When an AI system uses tools or multiple steps, distinguish each successful side effect from the overall workflow. Define preview, approval, authorization re-check, cancellation, retry/deduplication, undo where it is real, and the recovery path after partial completion. Never show a successful completion state before the external effect is confirmed.

## Grounding and freshness

For retrieval, recommendations, or decisions that depend on external information, record the source owner, retrieval/context boundary, freshness expectation, conflict behavior, and what the user can inspect. A source link or citation is an affordance for verification; it is not proof that the generated claim follows from the source. If context is unavailable, stale, or contradictory, expose that condition and route to clarification, fallback, or review.

## Opt-out and human handoff

Offer an understandable opt-out or alternate path when AI participation is optional, consequential, inaccessible, or not useful. Explain what opting out changes and retain enough task context for the alternate path without silently continuing AI processing. For escalation, state the trigger, destination, expected handoff time or status if known, and what summary/context is transferred. Let the person inspect and correct the handoff summary; do not present a generated summary as a complete transcript or verified fact set.

## Feedback as evidence

Design the smallest useful feedback signal: accepted, edited, rejected, corrected, escalated, task completed, or optional reason. Tell the person the purpose, retention, and whether content is being captured; minimize data and do not request secrets or unnecessary personal information. Treat a rating as a preference or experience signal until independently checked. Route event schema, privacy, statistical inference, and model evaluation to `product-analytics-and-measurement`, `agent-evals-and-observability`, `data-scientist`, or `ai-governance` as appropriate.

Define the improvement loop: signal → triage → representative fixture or test case → proposed UX/content/context/model change → independent evaluation → release decision. A feedback signal alone is not permission to change behavior or evidence that the change improved correctness.

## Acceptance for model, prompt, or retrieval changes

When a model, system prompt, retrieval index, ranking method, tool policy, or grounding source changes, rerun the approved behavior boundary. Use authorized representative fixtures covering:

- normal and ambiguous inputs;
- unsupported, stale, conflicting, and out-of-distribution inputs;
- permission, privacy, unsafe-output, and escalation paths;
- interruption, retry, partial side effect, and re-entry;
- review burden, latency, and any user-visible fallback.

Record the version/change identifier, fixture provenance, expected observable behavior, evidence captured, and limitations. Compare user outcome and countermetrics against the declared baseline; do not substitute benchmark scores, output count, or self-reported success. Route statistical design and model-quality thresholds to the owning specialists.

## Handoff checklist

Before engineering handoff, confirm that the linked artifacts state:

- AI role, authority, human review, and prohibited side effects;
- input/context ownership, freshness, privacy, and missing/conflicting behavior;
- output form, uncertainty language, grounding affordance, correction, fallback, and escalation;
- pending, partial, failed, blocked, and committed states with recovery and completion evidence;
- feedback purpose, notice/consent, minimization, retention owner, and improvement trigger;
- fixtures and deployed checks for model/prompt/retrieval/tool changes;
- unresolved decisions, owners, and revisit gates.

Use the general `templates/interface-contract.md` for the complete interaction contract and `templates/ai-interaction-contract.md` for these AI-specific additions. Pass approved behavior to `spec-driven-development`; do not turn this reference into a model or runtime operations manual.
