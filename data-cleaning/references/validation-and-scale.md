# Validation, contracts, and scale

Layer checks: transport (readability/hash), structure (headers/width/types), field (nulls/ranges/regex/units), record (keys/cross-field), relation (cardinality/referential integrity), dataset (grain/counts/totals/freshness/drift), and semantic owner review. Prefer checks that return failing records.

Use `templates/schema-contract.yml` as a neutral contract mapped to Pandera, Great Expectations, Frictionless, dbt, SQL, or another engine. A current profile should be compared with a versioned baseline; new categories can be legitimate evolution, while null-rate shifts can signal incidents. Avoid universal thresholds without context.

For scale: sample reconnaissance, validate invariants fully; stream/chunk files; push work to warehouses; use lazy plans; block entity candidates; partition only when the key preserves the contract; persist bounded metrics and failures. Report truncation.

Gates: pre-transform input/profile/plan; post-transform readable output, explained grain changes, accounted rejects, passing keys/rules, reconciled metrics; release report, provenance, reviewer decision, and reproducible rerun. Profiles and failure samples may contain sensitive data: minimize, redact, aggregate, and control retention.
