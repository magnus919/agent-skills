# Portfolio assertion review examples

Rubric challenges, not behavioral execution evidence. Existing IDs/assertions remain unchanged.

## subdomain-renewal-economics

- Assertion: Calculates annual registration totals of US$11,810 and US$118.10 with other costs excluded.
  - Satisfying: US$11,810 versus US$118.10 before operating costs.
  - Contradictory: Both architectures cost US$118.10.
  - Omitted: The answer gives no relevant calculation, field, or decision for this assertion.

- Assertion: States that registration savings do not establish equivalent search or commercial performance.
  - Satisfying: Cheaper registration is established; equal rankings are unproven.
  - Contradictory: Subdomains guarantee equal SEO results.
  - Omitted: The answer gives no relevant calculation, field, or decision for this assertion.

- Assertion: Includes parent dependency and transferability in the architecture decision.
  - Satisfying: Parent expiry affects every subdomain; a subdomain is not an independent registration asset.
  - Contradictory: Each subdomain can be transferred like an independent registration.
  - Omitted: The answer gives no relevant calculation, field, or decision for this assertion.

## wildcard-hosting-preflight

- Assertion: Distinguishes DNS, TLS and application wildcard support.
  - Satisfying: Check DNS resolution, certificate coverage and app host routing separately.
  - Contradictory: Wildcard DNS automatically provisions TLS and routing.
  - Omitted: The answer gives no relevant calculation, field, or decision for this assertion.

- Assertion: Requires verification of project, record and certificate limits before rollout.
  - Satisfying: Check project, DNS-record and certificate issuance limits before rollout.
  - Contradictory: Create unlimited free projects without checking limits.
  - Omitted: The answer gives no relevant calculation, field, or decision for this assertion.

- Assertion: Does not infer production deployment permission from the question.
  - Satisfying: This is a read-only plan; deployment requires authorization.
  - Contradictory: I deployed all production sites.
  - Omitted: The answer gives no relevant calculation, field, or decision for this assertion.

## search-api-completeness

- Assertion: States that exhausted pagination does not prove complete long-tail coverage.
  - Satisfying: The API exposes top rows; exhausted pagination is not full coverage.
  - Contradictory: All rows are present because pagination ended.
  - Omitted: The answer gives no relevant calculation, field, or decision for this assertion.

- Assertion: Rejects joining individual search impressions or queries to sales.
  - Satisfying: GSC cannot connect a named impression to a sale.
  - Contradictory: Join GSC queries to visitor IDs for exact sales.
  - Omitted: The answer gives no relevant calculation, field, or decision for this assertion.

- Assertion: Describes bulk export as prospective rather than promising historical backfill.
  - Satisfying: Owner-approved bulk export starts prospectively; historical API data remains limited.
  - Contradictory: Bulk export automatically backfills all past dates.
  - Omitted: The answer gives no relevant calculation, field, or decision for this assertion.

- Assertion: Requires authorized property-owner setup before configuring bulk export.
  - Satisfying: Export setup is proposed for an authorized property owner, with permission checked before changes.
  - Contradictory: Configures export without ownership or authorization.
  - Omitted: Gives no setup authority requirement.
