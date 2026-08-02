# Reconciliation Plan Template

Design a reconciliation strategy for a data migration. Fill one template per
data source/target pair.

## Data scope

| Field | Value |
|---|---|
| Source system | |
| Target system | |
| Data domain (tables, collections, keyspaces) | |
| Estimated record count | |
| Primary key or natural key | |

## Reconciliation dimensions

### Completeness

| Field | Value |
|---|---|
| Method | Row count comparison / Key-space scan / Checksum comparison |
| Frequency | |
| Pass threshold | (e.g., "exact match", "within 0.01%") |

### Accuracy

| Field | Value |
|---|---|
| Method | Field-level comparison / Hash comparison / Sample verification |
| Sample size (if sampled) | |
| Fields compared | |
| Tolerance per field | (e.g., "amount: within 0.01", "timestamp: within 1s") |
| Frequency | |

### Timeliness

| Field | Value |
|---|---|
| Lag tolerance | (e.g., "target within 5 seconds of source") |
| Measurement method | |
| Frequency | |

### Consistency

| Field | Value |
|---|---|
| Related-record checks | (e.g., "every order has matching line items") |
| Referential-integrity checks | |
| Frequency | |

## Reconciliation failure protocol

| Condition | Action |
|---|---|
| Completeness check fails | |
| Accuracy check fails | |
| Timeliness check fails | |
| Consistency check fails | |

## Reconciliation run log

| Run timestamp | Completeness result | Accuracy result | Timeliness result | Consistency result | Overall | Action taken |
|---|---|---|---|---|---|---|
| | | | | | | |
