# Third-Party Dependency Reliability

Use this reference when a service relies on a vendor, managed platform, external API, identity provider, payment processor, DNS, CDN, messaging system, or other dependency outside the team's direct control.

## Source anchors

Synthesized from *Seeking SRE*, “Working with Third Parties Shouldn’t Suck,” “SRE as a Success Culture,” “Engineering for Data Durability,” and “Introduction to Machine Learning for SRE,” with dependency and overload practices from *The Site Reliability Workbook*, “Managing Load” and “Data Processing Pipelines.”

## Dependency record

For each important dependency, record:

- user journeys and SLOs affected;
- owner on both sides and escalation path;
- vendor SLO, quotas, rate limits, maintenance model, and support boundaries;
- observed latency, errors, freshness, correctness, and availability from your service boundary;
- credential, quota, region, API-version, and account failure modes;
- fallback, cache, queue, degraded mode, or alternate-provider plan;
- data, privacy, and exit implications;
- last failure exercise and unresolved repairs.

A vendor dashboard is useful evidence but is not the service's user-visible boundary. Providers can report healthy while a regional route, credential, quota, integration version, or client-side timeout is failing.

## Buy, build, or adopt

Classify the dependency before debating implementation:

1. How critical is it to a user journey?
2. How likely and severe are its failure modes?
3. Can the team mitigate or substitute it?
4. What operational and security expertise does each option require?
5. What is the cost of exit, migration, or data recovery?

Criticality and substitutability determine how much redundancy, contract, testing, and internal expertise are justified. Do not build a replacement merely to avoid every external dependency, and do not accept a single provider as harmless because it is popular.

## Failure behavior

Design and test the client behavior explicitly:

- bounded timeouts aligned with the user journey;
- retries only for safe and retryable operations, with exponential backoff and a cap;
- circuit breaking or admission control to prevent retry storms;
- idempotency and deduplication for retried writes;
- queueing or asynchronous completion when delay is acceptable;
- cache or last-known-good behavior where correctness permits;
- clear degraded response and support communication;
- manual or alternate-provider path for critical operations.

If no fallback is feasible, say so. An undocumented dependency with no mitigation is a reliability risk, not an “external limitation.”

## Review and exercise

Review dependency health on a fixed cadence and after incidents. Run failure exercises for the most consequential paths, including provider outage, partial outage, elevated latency, quota exhaustion, expired credentials, malformed responses, and loss of the provider's status API. Verify that alarms, escalation, user messaging, data reconciliation, and recovery actually work.

## Agent procedure

Use this reference with `slo-sli-framework.md`, `reliability-design-and-change.md`, and `templates/reliability-design-review.md`. Report provider claims separately from measurements taken at the service boundary. Treat “no alternative” as an explicit risk requiring an owner and review date.
