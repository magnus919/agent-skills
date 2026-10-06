# External Agent Interactions

Use this extension when a person asks an agent they use outside the product to work with or on the product. The person may switch between an agent host and the product, and the agent may act through an integration, API, browser, or other explicitly supported path. First establish which paths actually exist; do not assume the product can observe the agent conversation or that a protocol implies a supported product experience.

This extends `ai-interaction-and-uncertainty.md` and `task-flows-and-state-models.md`. Keep general AI control, uncertainty, side-effect, recovery, and human handoff principles there. This reference adds cross-application identity, delegation scope, evidence continuity, and interruption questions.

## Establish who is acting and under whose authority

Model the human as the goal owner and decision-maker. Name the person, the external agent host or client, the agent identity if the integration exposes one, the product account, and any integration or service principal. Do not describe the agent as a human colleague or assign it human accountability. Where the system cannot reliably distinguish these identities, record the limitation and do not claim verified attribution.

For each delegated operation, identify the verified human principal; the agent, client, or integration principal actually authenticated; the target account, records, and operation; the authority source; the permitted scope; and any duration, revocation, or reauthorization rule. Distinguish a user request in an agent conversation from authorization recognized by the product. Recheck product-side permissions at the point of consequential action, including after a delay or permission change. An approval in one surface must not silently authorize a different target, operation, or changed payload.

Describe the task in user terms and link it to the exact product objects and actions. Show the person what the agent can read, change, send, or commit; what it cannot do; and what requires a fresh decision. Where details are not observable to the product UI, state what the user must verify in the external agent host or its provider documentation.

## Carry the outcome across app boundaries

Trace both directions: the person starts in an external agent surface and delegates; the agent reaches the product through an evidenced integration path; product-side changes or returned evidence become visible; and the person can return to the product or agent host and continue. Include the expected behavior when the person never switches back. A submitted request, tool-call acknowledgment, or agent statement is intermediate evidence. Define product-side evidence that the intended state changed and can be inspected.

Keep the identifiers and status needed for safe return: a stable task or operation reference, target object, last confirmed product state, timestamp or freshness, current owner, and a direct route back where the surfaces support one. State what context crosses each boundary, who can see it, how the human can inspect or correct it, and what is intentionally omitted. Do not imply that an agent transcript, generated summary, completion badge, or protocol result independently proves a product-side effect.

Give the person a clear way to intervene from whichever surface can actually reach the active work: inspect the plan and proposed changes; narrow scope; correct inputs; pause; reject; revoke or disconnect access; or continue manually. Specify which actions the product supports, which are available only from the agent host, and what happens if neither surface can reach the operation. If no intervention endpoint exists, say so before delegation and define the supported support or recovery route.

## Model cancellation and recovery honestly

Distinguish stopping future work from reversing work already performed. For every interruptible stage, define what cancel means, who receives the request, when it is acknowledged, what status the product can verify, and which in-flight actions may still complete. If cancellation is cooperative or unconfirmed, show that the operation may continue and direct the person to inspect the product state. Do not label a task cancelled solely because the client stopped waiting or sent a cancellation request.

Model partial completion at the product-object or action level. Show confirmed successes, failures, and unknown outcomes separately; explain whether a retry is safe, deduplicated, or could repeat a side effect. Preserve enough task context to resume after sign-in, disconnection, agent-host closure, timeout, or app switching. Reconcile stale agent status against the product’s current state before offering resume or retry. Define expiry, ownership changes, authorization loss, and recovery when a task handle or return link is no longer valid.

Use observable completion evidence at the product boundary: the target state and object, the action result or audit record the product makes available, and the remaining work or uncertainty. Route protocol authorization, tool isolation, runtime policy, audit logging, and operational controls to `agent-production-operations` or `ai-governance`; this UX extension defines what a person needs to understand and do, not the security implementation.

## Questions for the flow and contract

- What is the human’s intended outcome and how is product-side completion observed?
- Which app starts the work, which actor crosses each boundary, and by what supported mechanism?
- How does the product verify the human principal and the acting integration? What claims remain unverified?
- What exact targets, reads, writes, audiences, and duration does the delegated authority cover?
- Which actions are previews, which are product-side commits, and which need a fresh user decision?
- What evidence and context return to the person, with what freshness and privacy boundary?
- How can the person inspect, edit, pause, cancel, revoke, continue manually, or recover from each surface?
- How are in-flight actions, partial success, unknown results, retries, and duplicate effects represented?
- How does re-entry work when the agent host, connection, session, permission, or task reference expires?
- What is the evidence-backed exit condition, and what decisions still need an owner?
