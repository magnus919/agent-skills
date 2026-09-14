# Task Flows and State Models

Model one meaningful outcome at a time. A flow starts with entry conditions and ends with observable completion evidence, not merely a button press. Include decisions, alternative and exception paths, cancellation, interruption and re-entry, recovery, irreversible actions, side effects, permissions, ownership changes, and stale or conflicting data where the system can create them.

## Force-Driven State Applicability

Do not require a fixed inventory. Consider a state only when a force makes it relevant:

| Force | States or questions to consider |
|---|---|
| First use, no records, or no results | Initial or empty; what explains the absence and next action? |
| Fetching, background work, or delayed commit | Loading, partial, pending, cancellation, and status visibility. |
| User input or business rules | Validation timing, preservation of input, correction path. |
| Role, ownership, or authorization changes | Permission denied, reduced capability, request/escalation, audit path. |
| Network, sync, or cache | Offline/degraded, stale, conflict, retry, deduplication, re-entry. |
| Mutation or destructive effect | Confirmation, undo, delayed commit, partial commit, irreversible warning, completion proof. |
| System failure | Recoverable or unrecoverable failure, support route, retained context. |

Record why a likely state is not applicable when its omission would create risk. Use `templates/task-flow-state-model.md` for transitions and `templates/screen-state-inventory.md` for the resulting inventory. Diagrams are optional; readable tables are sufficient.

## Completion across roles

Trace a task beyond the initiating person's submission when another person must act. Name each actor, the handoff, what that actor receives, required authentication or account setup, the acceptance or rejection decision, resulting permissions/state, and recovery if the handoff expires or fails. Separate delivery evidence from outcome evidence. For example, sending an invitation is intermediate; the recipient still needs a valid acceptance path and the intended membership/access state. If that part is outside the approved scope, identify its owner and dependency explicitly instead of declaring the whole task complete.
