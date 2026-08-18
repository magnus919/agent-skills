# CLI and interactive remediation

## csvkit and Miller

Use csvkit for quick inspection, statistics, conversion, filtering, joins, and SQL-like commands. Make parser behavior explicit: delimiter sniffing and type inference can be wrong, so set delimiter/encoding and disable inference when identifiers or mixed types require preservation. Use Miller for streaming reshaping and querying of CSV/TSV/JSONL when a full in-memory DataFrame is inappropriate. After conversion, reconcile headers, row counts, key sets, types, and totals.

## OpenRefine

Use OpenRefine when a human needs facets, clustering, transformations, reconciliation, and reviewable undo/redo. Start with a small pilot, inspect candidates, and export the operation history or project archive. Some single-cell edits are not captured as reusable operations. A filtered visible view can produce a partial export: verify the export scope explicitly. Reconciliation remains semi-automated and requires human judgment for ambiguous candidates.

## Declarative monitoring

Use whylogs for mergeable longitudinal profiles and drift summaries when row-level evidence is unnecessary, with telemetry/privacy settings reviewed. Use SodaCL, dbt tests, or Deequ when the source boundary is SQL or Spark and checks need history, thresholds, or distributed execution. These tools validate encoded assertions; they do not select safe repairs. Pin versions and record disabled/skipped checks as accepted debt.
