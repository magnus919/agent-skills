# Multi-site measurement contracts

Read for a unified portfolio view across search, on-site activity and partner outcomes. Define the evidence contract before selecting a dashboard. Use `templates/portfolio-measurement-contract.md`. Route search-source specifics to `seo`, warehouse/pipeline implementation to `data-architect` and `data-engineering`, causal comparisons to `data-scientist`, and infrastructure health to `site-reliability-engineering`.

## Three layers, not one invented visitor journey

1. **Search visibility:** aggregate impressions, clicks, position and visible query categories from provider reports.
2. **Measured activity:** consent-appropriate visits, engagement and outbound handoffs observed by instrumentation.
3. **Partner outcomes:** accepted/rejected leads, completed work, invoices, collected amounts and corrections supplied under an authorized integration.

Search Console has no visitor/session identifier. Never join an individual impression or query to a sale. A click, visit, outbound handoff, accepted lead, completed deal and collected payment are different events. Without partner evidence the outcome is unknown, not zero. Show coverage beside every funnel stage; attribution is not proof of incrementality.

## Registry and grain

Maintain stable site ID, customer/tenant, registrable domain/hostname/path scope, search property ID and coverage, niche/intent, geography/language, launch cohort/site age, template version, offer/partner, collection mode, consent jurisdiction and integration owner. Record effective dates for moves and ownership changes. Detect overlapping Domain and URL-prefix properties before summing; select authoritative coverage or explicitly reconcile duplicates.

Declare each fact table's grain, source timezone, currency, dimensions, event/date semantics, refresh cadence, lateness/revision window, retention and owner. Preserve raw evidence and normalize incrementally into portfolio facts rather than making the dashboard query hundreds of raw property tables live. Collapse query dimensions before joining daily page activity so repeated query rows do not multiply visits. Do not mix page-level and property-level denominators. Compute weighted CTR from summed compatible clicks/impressions, not the mean of site percentages. Preserve anonymized query buckets in totals without inventing hidden query text; show visible-query coverage separately.

## Partner outcome contract

Use an opaque referral/click identifier without personal information in URLs. Define authorized destination and tenant access, authenticated callback or reconciled export, schema version, event ID, referral ID, status, occurred/received timestamps, currency, amount basis and correction/refund relationship. Specify idempotency, duplicates, replays, late outcomes, attribution windows, reversals, disputes and reconciliation cadence. A callback receipt alone is not verification that a deal was paid: label partner-reported versus independently reconciled states. Keep rejected, refunded, outstanding and collected amounts separate. Revenue-share calculation belongs to the commercial agreement, not an inferred analytics formula.

## Completeness and service levels

Represent measured zero, unavailable integration, privacy-suppressed data, collection failure, pending revision and unknown distinctly. Dashboard tiles need freshness, expected/received partitions, source coverage and reconciliation status, not just numbers. Search API pagination can exhaust available rows without achieving complete long-tail coverage. Do not fill unknown outcomes with modeled conversions and present them as actuals.

Search-source limits belong in the SEO contract below. Warehouse selection must account for consolidation: BigQuery documents a 1,000 referenced-resource/query limit after view expansion, so a 1,001-table live union is not a scalable default. Test a synthetic 1,001-site registry and bounded consolidation, not production deployment. Event volume, retention, scans, support and access administration drive cost alongside site count.

## Privacy and decision quality

Choose aggregate statistics versus cross-site/customer attribution explicitly. First-party, cookieless, server-side and self-hosted are not automatic legal exemptions. Record jurisdiction-specific consent/objection requirements, minimization, purpose, retention, tenant boundaries and access owners before implementation. A refusal is not permission for covert server-side identity stitching. Avoid collecting raw contact details solely for dashboard joins.

Compare comparable cohorts by age, intent, geography, offer, template, partner and coverage. Show weighted portfolio totals and site distributions; a few high-volume sites can hide failures. Treat correlations as diagnostic leads: investigate content, rendering, offer, partner responsiveness, missing data and seasonality before claiming a cause. Low traffic is not proof of poor quality or success. Missing CrUX coverage is not a performance pass; CrUX is rolling 28-day field data with lag, complemented by consent-appropriate RUM and synthetic tests.

## Acceptance workflow

Agree the metric contract and permissions; inspect read-only sources; validate registry/grains; reconcile sample facts and refunds; test only synthetic events to approved destinations; review privacy and tenant boundaries; run a bounded diverse pilot; then decide expand, repair or stop. A dashboard screenshot is not instrumentation acceptance. Require checks for overlapping properties, anonymous buckets, duplicate/refund events, timezones, late revisions, failed exports, consent refusal and absent partners. No production tags, access grants, callbacks or messages are authorized merely by designing the contract.

## Primary sources

Reviewed 2026-11-06; verify provider limits and jurisdiction guidance before acting.
- https://support.google.com/webmasters/answer/12917174?hl=en — bulk data fields and anonymized queries.
- https://support.google.com/webmasters/answer/17010575 — report measurement boundaries.
- https://docs.cloud.google.com/bigquery/quotas — referenced-resource and other quotas.
- https://docs.partnerstack.com/docs/server-to-server-s2s-tracking — example partner integration, not universal schema.
- https://developers.google.com/tag-platform/security/concepts/consent-mode — consent behavior, not legal clearance.
- https://www.cnil.fr/fr/node/677 — audience measurement conditions.
- https://ico.org.uk/for-organisations/direct-marketing-and-privacy-and-electronic-communications/guidance-on-the-use-of-storage-and-access-technologies/what-are-the-exceptions/ — jurisdiction-specific exceptions.
- https://developer.chrome.com/docs/crux/api — field-data API.
- https://developer.chrome.com/docs/crux/methodology — coverage/methodology.
