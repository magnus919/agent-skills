# Compatibility Matrix Template

Build a compatibility matrix for a multi-consumer migration. Each row is a
consumer or dependency; each column is a migration phase.

## Matrix

| Consumer / Dependency | Current interface | Expand compatible? | Compatibility window status | Cutover ready? | Contract safe? | Notes |
|---|---|---|---|---|---|---|
| | | | | | | |
| | | | | | | |
| | | | | | | |

## Column definitions

- **Consumer / Dependency:** The system, service, team, or external partner
  that depends on the interface being migrated.
- **Current interface:** What the consumer uses today (e.g., "REST v1
  /orders", "Postgres orders table", "us-east-1 ECS cluster").
- **Expand compatible?:** Can this consumer continue to operate when the new
  interface is added alongside the old? "Yes" means no action required from
  the consumer during the expand phase. "No" means the consumer must take
  action before or during expand.
- **Compatibility window status:** The consumer's progress toward migrating to
  the new interface. Values: "Not started", "In progress (N% complete)",
  "Migrated — monitoring", "Migrated — verified".
- **Cutover ready?:** Has this consumer verified that it works correctly with
  the new interface and is prepared for the old interface to be removed?
- **Contract safe?:** Can the old interface be removed without breaking this
  consumer? Must be "Yes" for all consumers before the contract phase.
- **Notes:** Contact person, migration deadline, special requirements, or
  known issues.

## Consumer communication log

| Date | Consumer | Message | Response |
|---|---|---|---|
| | | | |
