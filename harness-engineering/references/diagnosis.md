# Diagnose before prescribing

Start with a representative failed task and its intended user outcome. Reconstruct
intent → loaded context → action → result → state update → completion decision.
Record the first divergence, not just the last error.

| Symptom | Competing hypotheses | Discriminating probe |
|---|---|---|
| Wrong implementation | Ambiguous intent; stale docs; missing domain constraint | Compare accepted behavior with context actually loaded |
| Repeated tool failures | Bad schema; misleading errors; service down; denied authority | Exercise the same authorized call with controlled inputs |
| Restart repeats work | Missing checkpoint; stale summary; wrong revision | Interrupt, reopen, reconcile state against repo and evidence |
| False completion | Weak check; wrong surface; stale evidence; self-review bias | Run the user journey on the candidate revision |
| Slow/expensive work | Context overload; retries; idle services; unnecessary graph | Attribute latency and tokens by stage |
| Parallel conflicts | Shared files; competing goals; replayed side effects | Inspect ownership and side-effect records |

An audit inventories mechanisms and unknowns. It must not assign a causal
bottleneck from a lowest checklist score. The bundled audit does not follow every
routing link or discover remote stores; record those manually when present.
Absence of a progress file is not absence of durable state.

Deliver: task and revision, observed failure, supporting trace references,
alternative explanations, proposed intervention, falsification probe, rollback,
and a bounded next step. Stop after three non-converging passes and report missing
evidence. Do not add an entire harness when one tool error is the active defect.

## Evidence packet and first-divergence analysis

Record task/candidate/contract identity and the sequence of context/action/result/
checkpoint decisions. Identify the earliest unsupported transformation: a vague
requirement expanded incorrectly, a correct requirement absent from context, an
available tool misselected, a denied call retried unsafely, or an unobserved effect
reported as verified. The final stack trace can be downstream of that mistake.

Require the diagnostic probe to distinguish at least two hypotheses. For example,
"the agent forgot the test command" versus "the command cannot test the actual
storage path" calls for inspecting the loaded command and its observed surface;
adding another instruction does not discriminate between them.

Hold input and candidate identity stable when reproducing. A different seed,
service state, or fixture can make the failure disappear without validating a fix.
Record repeated outcome variability and unavailable evidence explicitly.

## Minimal failure attribution record

- Expected versus observed user behavior and where each was observed.
- First divergence and source/trace reference.
- Candidate cause, competing explanation, and discriminating probe.
- Probe outcome and what remains unknown.
- Smallest intervention, expected outcome, and rollback.
- Same-task rerun, negative challenge, interruption/recovery if relevant.
- Supported conclusion and next owner.

Do not overfit a harness to one failure. Turn a repeated class into a challenge
case or invariant only when the scope and observation support that promotion.
If the model lacks task competence after adequate context/tools/environment and
verification, report that remaining hypothesis rather than forcing a harness
explanation. Stop at the bounded evidence gap when no probe can resolve it.
