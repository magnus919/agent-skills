# Search portfolio collection boundaries

Read before specifying a cross-property search dashboard. SEO owns search-source interpretation; `product-analytics-and-measurement/references/portfolio-measurement.md` owns metric/event contracts and `data-engineering` owns implementation. A shared dashboard is possible; a person-level Google impression-to-sale join is not.

## Source decision

Record site/property registry and overlap first. Search Console Domain properties cover subdomains/protocols; separate unrelated registrable domains need appropriate ownership/access topology. Google documents 1,000 properties per account. Do not assume service accounts bypass this limit or propose account proliferation to evade restrictions.

For API collection, preserve request dimensions/filters/date/type, row counts and pagination receipts. Current documentation allows 25,000 rows/request and up to 50,000 rows/day/search type/property, with internal top-row selection. Exhausted pagination does not establish full long-tail coverage. Rate and load quotas both apply: documented per-site and per-user QPM are 1,200, alongside project limits. Retry/backoff and query scheduling must respect actual quota errors.

Native BigQuery bulk export can avoid the API row cap for available performance data, but does not disclose anonymized query text. Setup requires property ownership, billing and specified permissions, unique dataset per property, region choice and ongoing export monitoring. It starts prospectively without historical backfill; use API history with its limitations if needed. ExportLog records successful exports, not failed attempts. Verify expected date partitions and dashboard freshness rather than treating an absent error log as success; source retry windows are finite (documented around a week).

Retain anonymous buckets in totals and report visible-query coverage. Choose authoritative property coverage to avoid double counting nested properties. Sum compatible numerators/denominators before computing CTR; never join query-level search rows directly to page-level sessions and multiply visits. Mark incomplete, stale and privacy-suppressed data distinctly from zeros. No forecast or attribution model may silently replace observed source facts.

## Preflight and acceptance

Record documented versus account-observed limits, verification date and owner. Test revisions, missing days, overlap, anonymous buckets, timezone boundaries, pagination truncation and quota failures using fixtures. A schema-valid export or green API response is not completeness evidence. Route consolidated storage, bounded batch ingestion, partitioning, IAM and infrastructure costs to their owning skills; request authorization before configuring exports or access.

## Primary sources

Documentation reviewed 2026-11-06; recheck limits before implementation.
- https://support.google.com/webmasters/answer/34592?hl=en — property scope/count.
- https://developers.google.com/webmaster-tools/v1/how-tos/all-your-data — API data retrieval and limits.
- https://developers.google.com/webmaster-tools/limits — rate/load quotas.
- https://support.google.com/webmasters/answer/12917675?hl=en — bulk export setup.
- https://support.google.com/webmasters/answer/12917991?hl=en — export operation/troubleshooting.
- https://support.google.com/webmasters/answer/12917174?hl=en — tables, fields and privacy buckets.
