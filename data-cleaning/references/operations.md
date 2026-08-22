# Cleaning operations and failure modes

## Missing values
Distinguish unknown, not applicable, not collected, refused, suppressed, and structurally absent. Map sentinels only with source evidence and counts. Dropping requires an explicit bias and count-loss rationale. Imputation requires a method, fit boundary, retained indicator, and sensitivity check.

## Duplicates and entities
Define duplicates at the intended grain. Check exact duplicates, duplicate keys, and near-duplicates separately. For conflicts, document survivorship or quarantine. Fuzzy matching generates candidates, not truth: retain fields, scores, thresholds, decisions, and review.

## Types, dates, units
Declare number locale, date format, timezone, and error policy. Quarantine parse failures. Convert units only when both units are known; preserve original unit and conversion. Check cross-field rules such as start ≤ end and subtotal = components.

## Text and categories
Normalize Unicode and whitespace conservatively, preserving source text. Use versioned code lists with unknown/unmapped states. Do not collapse rare categories merely because they are rare.

## Outliers, joins, reshape
Investigate outliers before clipping or deletion. Before joins, assert key uniqueness and expected cardinality, measure unmatched keys and row multiplication, and reconcile totals. For pivot/melt, state the unique key and aggregation rule.

## Failure modes
- Silent coercion turns bad values into nulls.
- Leakage learns imputation, encodings, or deduplication from holdout/future data.
- Over-cleaning deletes valid rare events.
- Many-to-many joins masquerade as new observations.
- Weak identifiers create false duplicate/entity matches.
- Locale and timezone assumptions corrupt values.
- Replacement characters or mojibake are repaired without evidence.
- Schema drift passes parsing but violates downstream assumptions.
- Non-idempotent steps change already-clean data on rerun.
- Unbounded profiling exhausts resources before a plan exists.
