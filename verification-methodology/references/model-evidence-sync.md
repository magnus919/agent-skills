# Keep model evidence current as the implementation changes

Use this when a formal model or state diagram supports a claim about a system.
The checker can establish what happened in the model. Separate evidence is
needed to show that the implementation still behaves as modeled.

## Establish what was checked

- Name the user-visible promise, a violation that would matter, and the scope
  of the conclusion. Pin the model and code revisions, checker and configuration,
  plus evidence of the run.
- Map modeled actions to actual readers, writers, and transaction or concurrency
  boundaries. Record assumptions and excluded behaviors such as timeouts,
  recovery, worker counts, or other side effects. Mark finer details as out of
  scope rather than pretending that they were checked.
- Check that the configured scope actually reaches the relevant starting states
  and transitions. A green initial-state check or a run that explores no eligible
  starts cannot establish a promise about later behavior.
- Check that a meaningful negative control fails. In a disposable model or test
  fixture, deliberately remove a protection the promise relies on and expect a
  counterexample for the named rule. A passing negative control can mean that
  the check cannot see the problem, not that the system is safe.

## Decide what a change invalidates

Compare the candidate with the last verified mapping. Check for new writers,
alternate paths, moved atomic boundaries, and changes to scheduling, faults, or
bounds. Widen the review past touched files only where the change can affect the
property.

| Finding | Response |
|---|---|
| Intended and approved behavior changed | Version the promise and record the approval. Revisit the property, model, and implementation checks together. |
| Promise unchanged; the model misses or misrepresents a real path | Keep the prior result as historical evidence. Hold the current implementation claim and repair or justify the mapping before relying on the model again. |
| A concrete implementation check contradicts the promise | Report the defect with the smallest relevant trace. Fix or escalate it; do not change the property to get a pass. |
| The checker stopped or the behavior lies outside its bounds | Identify the exact unchecked claim. Keep it out of the pass; decide whether to expand coverage or get independent evidence. |

For a witness, explain the sequence of actions in domain terms and retain its raw
trace. State diagram projections can hide internal transitions and a single
witness does not enumerate all failing histories. Record the scope and results
of the new model check, the negative control, and the concrete implementation
check separately. Update the verified mapping only when the evidence agrees.

## Check what a diagram implies

When readers will rely on a simplified diagram to make a decision, test the
simplification separately from the model result. Compare the starts and
transitions that the diagram implies with the same bounded source evidence,
in both directions: does the picture allow a path the source excludes, or
omit a path that would change the reader's decision? Check guards and coupled
updates, particularly when several regions are drawn as independent.

For example, an editor sends a save only after a connection returns. A diagram
with separate connection and save regions makes the send arrow look available
while offline. Check that path against the trace, then add the missing
condition or draw the coupled states together. If the source cannot resolve
the discrepancy, label the diagram illustrative and do not use it to settle
the promise. Correcting the diagram does not prove the running app behaves
the same way.

## Example: an export gains a second completion path

An export service must not emit two delivery receipts for the same export. The
existing evidence covers two workers, one retry, and a completion helper that
atomically claims the right to issue the receipt. A new reconciliation worker
writes completion without using that helper. The model still passes, but it has
no reconciliation action. That result says nothing about the new path.

Find out whether the reconciliation path can issue a receipt. If it can, check
the race between it and the normal worker at the actual storage boundary. Include
that path in the model or show why the existing abstraction faithfully covers
it; retain a negative control that can produce two receipts if atomic claiming
is removed. If a check times out, record the open claim rather than reporting it
as satisfied. Keep deployment and broader concurrency claims separate from the
bounded result.
