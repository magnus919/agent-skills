# Diagnose collective failure

Classify the observed symptom, name competing explanations, find the first
boundary where behavior diverged, and choose one discriminating probe. Use
systematic-debugging for a live defect. Do not blame a model or add another
reviewer before checking inputs, interfaces and actual effects.

| Symptom | Hypothesis | Discriminating evidence | Bounded intervention |
|---|---|---|---|
| Repeated proof of already established proof | Verification has become a self-perpetuating objective | Pinned acceptance is satisfied; new checks add no decision-relevant evidence | Close at accepted sufficiency or ask acceptance owner to resolve the exact gap |
| Many handoffs; little accepted delivery | Coordination overhead or bottleneck | Same task mix, rising review/queue cost, stalled milestones | Remove redundant boundary or backpressure intake |
| Helpful dependencies consume the original job | Local scope expansion lost intent | Each proposed dependency lacks a required-outcome link | Reconstruct intent; defer optional scope to its owner |
| Agent acts after a peer's GO | Authority laundering or uninformed approval | Trace origin, actual grant and decision packet | Enforce grant; route missing decision context to correct owner |
| Agents all agree on an unsupported fact | Shared-source error or conformity | Initial independent evidence versus post-discussion revisions | Preserve initial findings; inspect contradictory source or execute real check |
| Correction disappears after restart | Stale shared lesson reinfects consumers | Source/version lineage and actual retrieved context | Correct source and affected derivatives; verify fresh-session adoption |
| Everyone waits on everyone | Circular dependency or missing wake-up | Wait-for edges, lease and wake state | Break one owned dependency, repair wake path or escalate |
| Every branch green, integrated journey wrong | Interface divergence or stale acceptance | Combined candidate and input versions | Reconcile semantics; rerun affected integrated checks |

## Recursive proof loops without weakening assurance

Freeze acceptance and evidence sufficiency before production where possible.
For every additional check ask: which unresolved claim does it observe, what
failure could it detect, who uses its result, and when is enough enough? Replace
manual ceremony with an appropriate executable invariant only when the failure
mechanism is understood. Preserve mandatory security/domain checks. A costly
verification stage may be doing necessary work; compare risk, task mix and
escaped defects before simplifying it. Never mark evidence complete because the
budget ran out; report the missing evidence and stop or escalate.

## Social convergence is not acceptance

Retain independent initial assessments where diversity is the point. During
exchange require evidence for consequential changes, and preserve unresolved
disagreement. A different persona or model does not establish statistical or
institutional independence. [Cost of Consensus](https://arxiv.org/abs/2605.00914v1)
finds harms in a specific small-model homogeneous debate setup; do not generalize
that all debate fails. Route actual debate operation to agent-council.

[MAST v3](https://arxiv.org/abs/2503.13657v3) separates design, inter-agent alignment
and verification failures. It is a useful classification aid, not a diagnosis of
this fleet or a calibrated online detector. The table above is our synthesis,
informed by that taxonomy and the supplied video; it is not a new research taxonomy.

## Stop and document

One pass ends with observed discrepancies assigned to owners, the hypothesis and
probe recorded, and affected work safely continued/held. Three non-converging
passes, exhausted budget or missing authority require a durable handoff. Retain
failure/timeout evidence. Never create permanent rules from one unexplained event.
