# Review model-assisted repairs and entity matches

Load when a model proposes a changed value, an extracted fact or a match between
records. Apply the normal cleaning workflow first. The model proposes candidates;
it does not supply the authority or ground truth for a lossy transformation.

## Ground each proposal

Keep the raw value and immutable source identity. Attach the proposed value, evidence
location, transformation/model version and rule that would permit the change. Separate
absence in a source from unreadability, timeout, unsupported extraction and ambiguity.
Preserve identifiers, units and locale rather than inferring them from model fluency.

For entity matching, deterministically normalize and block candidates before model
comparison. Inspect alternatives and conflicting evidence, not only the highest score.
Model-reported confidence is not an empirical probability of correctness. Calibrate
any auto-accept policy on reviewed examples from the relevant population, with the
cost of false merges separated from missed matches. Route statistical calibration to
data-scientist; do not invent a universal confidence threshold.

## Review and adjudicate

1. Define accept/review/reject criteria and an abstention path before bulk processing.
   Include ties, weak identifiers, contradicting attributes and unusual input slices.
2. Review samples across proposed accepts as well as the review queue. Checking only
   uncertain rows cannot establish that high-scoring changes are correct.
3. When model suggestions may anchor a reviewer, include an independently reviewed
   sample where the proposed answer/score is hidden initially. Preserve disagreement
   and distinguish source ambiguity from an incorrect proposal.
4. Record reviewer decision, supporting evidence and approved replacement or mapping.
   If evidence is insufficient, retain separate records or quarantine the proposal.
   Do not merge two people simply because the model produces a confident explanation.
5. Apply approved decisions to a new output, keeping a reversible mapping back to
   original record IDs. Confirm target, scope, and rollback before mutation; discovery
   can proceed read-only. Downstream references affected by a merge must be enumerated
   so an undo can restore more than the displayed name.

## Reconcile before release

Use `templates/ai-repair-ledger.csv` from the skill root alongside the existing exception
register. Compare keys, counts, relationships and relevant totals, then inspect semantic
samples; count preservation alone cannot prove a repaired value is true. Track missing
and quarantined records explicitly. Preserve accepted decisions for repeat runs rather
than silently asking the model for a new answer to the same versioned input.

Complete only when all changes have a rule and evidence, unresolved items remain
visible, reversibility is demonstrable, and the dataset's declared quality/completeness
contract passes. Hand scheduling, retry budgets and publication to data-engineering.
Training-label workforce and acquisition policies are a separate annotation concern.
