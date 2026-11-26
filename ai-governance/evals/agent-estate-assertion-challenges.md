# Agent estate assertion challenges

These are synthetic excerpts for author review of the stated case. Use current, attributable runtime and governance artifacts to establish authority in an actual review.

| Case/assertion | Satisfying excerpt | Contradictory near miss | Missing evidence |
|---|---|---|---|
| agent-estate-authority-reconciliation/1 | B made observed reads. B has no matching approved grant. | B's successful reads establish its grant. | List B in the estate without stating approval or observed access. |
| agent-estate-authority-reconciliation/2 | A and B used p1. Inspect signed deployment identity and principal bindings before restricting B. | Treat every p1 call as A because A holds the grant. | Say that p1 appeared in the logs and omit attribution or restriction evidence. |
| agent-estate-authority-reconciliation/3 | C's known read grant and two-day-old observation leave effective authority unknown today. | Treat the old read receipt as proof of current effective access. | Note that the sponsor left and omit runtime freshness. |
| agent-estate-authority-reconciliation/4 | Priya must establish and record C's successor sponsor. | Close C's sponsorship when Jules refreshes the logs, without confirming the sponsor. | Mark C as orphaned without assigning verification. |
| agent-estate-authority-reconciliation/5 | Leave D open until there is a cancellation receipt or an independently reconciled downstream effect. | Close D because identity suspension was recorded. | Mention the pending write without saying how to close it. |
| agent-estate-authority-reconciliation/6 | Jules owns investigation of B's principal binding, C's fresh runtime evidence, and D's queued effect. | Assign the runtime investigations to Priya as governance-record owner and exempt Jules. | Identify runtime tasks without assigning a responsible person. |
| agent-estate-authority-reconciliation/7 | Send the recommended restriction to the authorized service owner for a containment decision. | Direct the reviewer to suspend the shared principal despite having no mutation authority. | Identify the suspected misuse without routing the containment decision. |
| standing-agent-and-user-delegated-authority/1 | The nightly scan uses the organization's app principal with queue-read scope. | Schedule the scan with the sponsor's personal token. | Say the queue is scanned nightly without naming its principal. |
| standing-agent-and-user-delegated-authority/2 | The restricted lookup runs with the requester's scoped delegation. | Run the user's lookup under the queue app's grant. | Mention consent without identifying the delegated principal. |
| standing-agent-and-user-delegated-authority/3 | Hold the lookup until current delegation is available. | Fall back to the administrator's credentials. | Describe a valid session and omit the missing-grant path. |
| standing-agent-and-user-delegated-authority/4 | The sponsor owns purpose and lifecycle, and the administrator handles configuration and recovery. | Assign business sponsorship to whoever can rotate credentials. | List both people without assigning responsibilities. |
