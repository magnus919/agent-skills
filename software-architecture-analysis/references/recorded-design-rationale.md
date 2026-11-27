# Explain what the system does and why it was designed that way

A current implementation can establish a mechanism. It usually cannot establish
what motivated the people who chose it. Answer the part the reader needs and
keep the two sources of evidence separate.

1. **Pin the question.** Identify the component, behavior, and relevant
   revision or environment. For "how," trace the current entry point, work,
   dependencies, and observable outcome. Label runtime behavior inferred from
   code separately from behavior observed in a reproduction.
2. **Look for a decision if the question is "why."** Find the first relevant
   decision and later changes. Read the accepted decision record, linked issue,
   merged PR discussion, or contemporaneous notes where accessible. A shallow
   checkout may not have the relevant history. Read enough authorized history
   to locate the decision, not unrelated repositories or conversations.
3. **Separate initial and current rationale.** Record what was stated, by
   whom or which decision body, at what time, and the scope of that statement.
   A proposal in a comment is not an accepted decision. Check whether a newer
   record supersedes it and whether today's implementation still meets the
   original constraint. If records conflict, present the conflict rather than
   silently treating the newest remark as authoritative.
4. **Hand back a usable explanation.** Lead with the current mechanism, then
   the reason if recorded. Label a plausible engineering reason as inference
   and say what is unknown. Link to the smallest set of dated records and
   current implementation evidence that supports the conclusion. Stop there
   if the request is read-only; route a new design decision to its owner.

## Example: why does export publication wait?

At the revision under review, the exporter stages an artifact; a separate
publisher checks readiness before it exposes a link. That is the mechanism
from the current implementation. An accepted decision record says the team
introduced the boundary to stop customers opening partial files. A PR comment
also proposed smoothing peak CPU usage, but the accepted record makes no
such claim. State the partial-file rationale as recorded. Leave the
performance explanation as a hypothesis unless corroborated. If a later PR
replaces the readiness check with a storage event and records no reason, do
not attribute that replacement to the original authors or claim it has the
same effect without tracing the new behavior.
