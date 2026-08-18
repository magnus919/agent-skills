# Data-cleaning methodology

## Definition

There is no universal clean dataset. Define quality relative to a use case, data contract, and unit of observation. Record intended grain, keys, units, temporal coverage, acceptable error rate, and the decision the data supports.

## Lifecycle

**Scope → acquire → preserve → profile → diagnose → decide → transform → validate → review → publish → monitor.**

### Scope and preservation

Write a brief naming consumer, source, time boundary, privacy constraints, and failure criteria. Capture source identity, retrieval time, content hash, encoding, delimiter, schema, and tool versions. Keep immutable raw input, a staged copy, and rejects/quarantine output.

### Profile and diagnose

Inspect structure, field-level nullness/cardinality/types/ranges, record duplicates, relational keys, temporal freshness, units, text, and distributions. Compare with a known-good baseline. A profile is a hypothesis generator, not permission to auto-fix: rare, new, or extreme values may be real.

### Decide and transform

Prefer: preserve valid observations; standardize representation; repair only when the corruption mechanism is defensible; impute only with a stated missingness method and fit boundary; quarantine unsafe values; escalate semantic ambiguity. Keep original and normalized values when change is lossy. Make transformations deterministic and idempotent.

### Validate and release

Reconcile counts, sums, key coverage, category counts, and time ranges. Inspect every class of changed or rejected record. Use holdout/time-split checks when rules are learned. Domain approval is required for deletion, imputation, entity matching, unit conversion, and business-rule changes.

## Audit record

For each rule retain: ID, input columns, predicate, action, before/after counts, affected identifiers or privacy-safe sample, rationale, confidence, owner, timestamp, code/version, and rollback path. A report that only says “cleaned successfully” is not auditable.
