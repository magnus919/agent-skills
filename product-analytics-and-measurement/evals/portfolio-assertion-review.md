# Portfolio assertion review examples

Rubric challenges, not behavioral execution evidence. Existing IDs/assertions remain unchanged.

## portfolio-overlap-grain

- Assertion: Defines an overlap policy to prevent duplicate property totals.
  - Satisfying: Use authoritative Domain coverage and exclude overlapping prefix totals.
  - Contradictory: Sum both property totals.
  - Omitted: The answer gives no relevant calculation, field, or decision for this assertion.

- Assertion: Aggregates query rows to compatible page/date grain before joining sessions.
  - Satisfying: Aggregate queries to page/date before joining daily sessions.
  - Contradictory: Attach full daily sessions to every query row and sum.
  - Omitted: The answer gives no relevant calculation, field, or decision for this assertion.

- Assertion: Computes portfolio CTR from summed compatible clicks and impressions.
  - Satisfying: CTR = sum(clicks)/sum(impressions) at compatible scope.
  - Contradictory: Average site CTR percentages equally.
  - Omitted: The answer gives no relevant calculation, field, or decision for this assertion.

## partner-outcome-unknown

- Assertion: Distinguishes missing partner integration from measured zero sales.
  - Satisfying: No integration means unknown sale count.
  - Contradictory: Missing partner data means zero sales.
  - Omitted: The answer gives no relevant calculation, field, or decision for this assertion.

- Assertion: Specifies idempotency for duplicate callbacks.
  - Satisfying: Use stable event IDs and idempotent processing.
  - Contradictory: Count every retry as another sale.
  - Omitted: The answer gives no relevant calculation, field, or decision for this assertion.

- Assertion: Links refunds or corrections to earlier outcome events rather than counting both as collected revenue.
  - Satisfying: Refund references original event and reduces collected net revenue.
  - Contradictory: Count sale and refund as positive revenue.
  - Omitted: The answer gives no relevant calculation, field, or decision for this assertion.

## portfolio-privacy-scale

- Assertion: Rejects covert identity stitching after consent refusal.
  - Satisfying: Do not bypass refused consent with server-side identification.
  - Contradictory: Use server-side stitching to evade refusal.
  - Omitted: The answer gives no relevant calculation, field, or decision for this assertion.

- Assertion: Identifies a live union over 1,200 BigQuery resources as requiring bounded consolidation against documented limits.
  - Satisfying: Consolidate in bounded batches; 1,200 resource references exceed the documented 1,000 limit.
  - Contradictory: A 1,200-table live BigQuery union is always supported.
  - Omitted: The answer gives no relevant calculation, field, or decision for this assertion.

- Assertion: Does not treat absent CrUX coverage as a performance pass.
  - Satisfying: Absent CrUX data means unknown field performance.
  - Contradictory: No CrUX entry proves the site is fast.
  - Omitted: The answer gives no relevant calculation, field, or decision for this assertion.
