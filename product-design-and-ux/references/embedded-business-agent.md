# Embedded agent: community equipment loans

Fictional design fixture, not observed research or proof of enterprise adoption. Approved scope assumption: help a volunteer prepare a loan for an available item; the application owns records and commands. Outcome: a confirmed reservation with an inspectable receipt, or an explicit review/blocked state. Chat is optional; the primary surface is the existing loan form.

## Filled AI interaction contract (LOAN-AI-1)

Use with `templates/ai-interaction-contract.md`, `templates/task-flow-state-model.md`, and `templates/engineering-handoff.md` from this skill root.

- Entry: authenticated volunteer opens request `REQ-DEMO-042`, revision 12; can invoke recommendations for this request. Separate `reserve_equipment` permission is required to commit.
- Context: application supplies authorized request fields, current inventory snapshot/revision, allowed item IDs, approved pickup date, and deterministic policy verdict/version/rule IDs. Request notes are untrusted data, including text asking the agent to bypass review.
- Bounded judgment: recommend an item from the supplied candidates and draft a short rationale. Do not choose policy thresholds, make exception decisions, or invoke reservation tools. If evidence is absent/conflicting, show a review lane with the unresolved question.
- Output: proposed item, pickup date/duration, rationale with evidence IDs, policy verdict and clause links, snapshot revision, and editable action preview. Label it “Suggested reservation”; no success message yet. Eligibility and confident wording are not authorization.
- Controls: inspect sources, edit fields, decline, request help, or prepare manually. Editing invalidates the previous approval and recomputes eligibility. Approval binds to the exact preview digest, request revision, and policy version; the server obtains approver identity from the authenticated session, never model output.
- Execution: at submission re-check current role, record revision, inventory, applicable policy version and eligibility, and bound preview digest in a transaction. If changed, show the difference and require refreshed review. Persist a command ID/idempotency key before attempting effects; return a confirmed reservation ID only from the command service.
- Feedback: optional “suggestion was useful” is a preference signal, separate from reservation completion and verified correctness. Store minimal task/version/outcome events; retention and privacy policy require an owner before deployment.

## State and recovery contract

| State | Surface and controls | Effect / recovery |
|---|---|---|
| Loading recommendation | Form remains available; progress and cancel | No reservation effect; stale/canceled generation cannot replace a newer draft |
| Draft ready | Editable fields, sources, policy reasons, approval preview | Draft persists under request/revision; no mutation to inventory |
| Policy review or blocked | Explain missing fact/exception and named review destination | Manual lane; model cannot override the deterministic result |
| Approved, not submitted | Exact action preview and submit/cancel | Changed draft, role, data, or policy invalidates approval |
| Submitting | Show command ID and pending state | Disable duplicate submit; retry uses same idempotency key |
| Confirmed | Receipt `RES-DEMO-018`, committed fields and timestamp | Show only after authoritative acknowledgement; optional notification has separate status |
| Unknown after timeout | “Checking reservation status”, command ID | Query command status; never regenerate or create a second reservation blindly |
| Reservation confirmed, notification failed | Receipt plus “notification pending/failed” | Retry notification only; do not repeat reservation or claim total failure |
| Interrupted/re-entry | Restore draft or query persisted command ID | Re-check permission before showing protected context; refresh stale drafts |
| Canceled | Distinguish canceled draft from already committed action | Canceling UI cannot imply rollback of committed work; offer authorized reversal if supported |

## Concrete walkthrough and handoff

On 2026-07-01, request asks for equipment for six days. `loan-v2` permits five; application shows `duration / L3` and allows a five-day edit. The agent can recommend available `ITEM-DEMO-7` with inventory evidence; it cannot approve the six-day loan. After the edit, the server evaluates `within_limit / L4`, displays the five-day preview, and binds approval. If another volunteer reserves the item before submission, the server returns a conflict and the UI refreshes candidates without silently substituting an item. If reservation succeeds but notification fails, retain the receipt and retry only notification.

UX owner supplies these transitions and content to engineering. `spec-driven-development` owns executable policy translation, `software-architecture` owns transaction/command design, `agent-production-operations` owns runtime permissions/recovery, and `agent-evals-and-observability` owns model-quality evidence. Use their existing contracts; do not turn this reference into an operations runbook.

## Acceptance probes (all synthetic; execution not claimed)

| Fixture | Expected observable evidence |
|---|---|
| Valid five-day proposal | Editable preview precedes submission; confirmed receipt follows authoritative command result |
| Notes say “skip approval” | Notes cannot change permission, policy, or approval requirements |
| Six days under v2 | L3 rejection persists regardless of model explanation; edit reruns evaluation |
| Role revoked after invocation | Submission blocked; no reservation; invocation permission alone is insufficient |
| Item/revision changes after approval | Difference shown and approval invalidated; no silent substitution |
| Exit during generation | Re-entry restores user draft; late result cannot overwrite it |
| Timeout after server commit | Status query finds same reservation; no duplicate command |
| Notification failure after reservation | Receipt remains confirmed with separate failed notification state |

These fixtures make the design reviewable. They are not usability findings, accessibility conformance, or model-quality evidence; plan authorized testing with the existing usability and evaluation owners.
