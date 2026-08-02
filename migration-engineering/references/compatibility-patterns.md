# Compatibility Patterns

Detailed patterns for forward and backward compatibility by migration type.
Load this reference when designing the compatibility surface for a specific
migration.

## Schema compatibility

### Forward compatibility (old readers, new writers)

Old readers must be able to consume data written by the new schema. This is the
more common constraint: you control the writer deployment but cannot upgrade
every reader simultaneously.

**Patterns:**
- Add columns as nullable or with defaults. Old readers ignore unknown columns.
- Never rename a column in place. Add the new column, dual-write both old and
  new names during the compatibility window, then drop the old column after all
  readers have migrated.
- Never change a column type in place. Add a new column with the target type,
  dual-write to both, migrate readers, backfill the new column from the old,
  then drop the old column.
- Use views or computed columns to present a stable interface while the
  underlying schema changes.

### Backward compatibility (new readers, old writers)

New readers must be able to consume data written by the old schema. This applies
when readers are deployed before writers or when you cannot control writer
upgrade order.

**Patterns:**
- New readers treat new columns as optional. Missing columns must not cause
  errors.
- New readers must handle the old enum values, old units, old precision.
- Consider a compatibility adapter layer that translates old-format data to
  new-format before it reaches the new reader.

## Data compatibility

### Dual-write patterns

Both old and new stores receive writes during the transition.

**Patterns:**
- **Synchronous dual-write:** Write to both stores in the same transaction or
  unit of work. Strong consistency; adds latency and a failure mode (what if one
  write succeeds and the other fails?).
- **Asynchronous dual-write:** Write to the primary store, then publish an event
  that the secondary store consumes. Eventual consistency; the secondary store
  lags behind the primary. Acceptable when the lag is bounded and monitored.
- **Change-data-capture (CDC):** The secondary store tails the primary's write-
  ahead log or change stream. No application code change; the CDC pipeline must
  be monitored for lag and errors.

### Dual-read patterns

Both old and new stores are read during the transition for comparison.

**Patterns:**
- **Shadow read:** Read from the new store in parallel with the old store;
  compare results; use the old store's result for the response. Log mismatches.
- **Percentage read:** Route a configurable percentage of reads to the new
  store. Increase over time as confidence grows.
- **Consumer-driven read:** Individual consumers opt into reading from the new
  store. Track per-consumer migration status.

## API compatibility

### Additive changes (safe)

- Adding a new endpoint or field.
- Adding an optional query parameter.
- Adding a new enum value (if consumers handle unknown values gracefully).
- Adding a new response header.

### Breaking changes (require compatibility window)

- Removing an endpoint, field, or enum value.
- Renaming a field or endpoint.
- Changing a field type or response shape.
- Changing authentication requirements.
- Changing error response format.
- Changing rate limits downward.

For breaking changes, use the expand/contract pattern: add the new interface
alongside the old, give consumers a migration window, track consumer migration,
then remove the old interface.

## Infrastructure compatibility

### Network continuity

- DNS migration: lower TTL before the change, dual-publish old and new records
  during the transition, verify propagation before removing old records.
- Certificate rotation: deploy new certificates before old ones expire; both
  old and new certificates must be valid during the overlap window.
- Service discovery: register the new service instance before deregistering the
  old one.

### Data-plane continuity

- Database connection strings: dual-configure applications with both old and new
  connection parameters; switch via configuration, not code deploy.
- Message broker migration: dual-publish to old and new brokers; dual-consume
  during the transition; verify no message loss before shutting down the old
  broker.
