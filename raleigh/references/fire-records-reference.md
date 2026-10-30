# Raleigh Fire Records and Public-Records Routing

Current fire-report guidance. `references/fire-reports-reference.md` is a
pre-retirement snapshot kept byte-identical only because a frozen evaluation
artifact pins its hash; do not follow its RFD forms or `--rfd` flags. For
incident-level data (2007–present, 2026 classification transition) read
`references/fire-reference.md`.

## Current Sources

Reviewed 2026-10-30:

| Source | Contract | Role |
|---|---|---|
| ArcGIS item | `c983765e304a41d19087c8d95aa46d54` | Rolling fire-incident summaries, past month |
| ArcGIS layer | `https://services.arcgis.com/v400IkDOw1ad7Yad/arcgis/rest/services/Fire_Incidents_Past_Month/FeatureServer/0` | Query-capable JSON/GeoJSON/PBF layer |
| Published index | `https://raleighnc.gov/fire/services/fire-reports` | Official aggregate reports and public-records routing |
| Public-records portal | `https://raleighnc.nextrequest.com/` | Submission portal for records not published elsewhere |

The ArcGIS layer advertises `Query` capability, UTC date fields, and the required report fields. Exact-date queries use a half-open UTC interval; exact incident-number queries use an escaped equality. The command requests only `incident_number`, dispatch/arrival/clear timestamps, address, station, platoon, and current classification fields, without geometry. Results are capped at 200 and fail rather than paginate or silently truncate.

## Retired RFD Report System

The former RFD Report System at `rfdreports.net` is gone. Verified 2026-10-30:

| Probe | Observed result |
|---|---|
| `GET http://rfdreports.net/` | `301` to `http://raleighnc.gov/fire/services/fire-reports`, 82-byte stub body |
| `GET https://rfdreports.net/` | same `301` to the same `http:` target |
| `GET /fd_date.php` | `404`, empty body |
| `POST /fd_date.php` | `405`, empty body |
| `GET` or `POST /fd_incidentreport.php` | `404` / `405` |
| `GET` or `POST /fd_inspection_business_name.php` | `404` / `405` |
| `GET` or `POST /fd_inspection_business_address.php` | `404` / `405` |
| `GET` or `POST /fd_report.php` | `404` / `405` |
| `GET` or `POST /fd_invoice.php` | `404` / `405` |

Every path is absent for reads and method-rejected for submissions. The root redirects to the City page instead of serving a form, and the responding host varies between probes (`Server: awselb/2.0` with `WAFRule: 5` on 2026-10-29, `Server: ip-10-12x-…ec2.internal` on 2026-10-30): a load balancer with no application behind it, not a transient outage or an IP-level block. Earlier incarnations of this skill implemented date fallback, incident narratives, and business/address inspection search against four HTML contracts over plain HTTP with an acknowledgement gate; all of it was removed rather than repointed.

## Successor Path

`https://raleighnc.gov/fire/services/fire-reports` still answers `200` and still links the published report index, but it now routes record-level requests to the City's Public Records Request Portal at `https://raleighnc.nextrequest.com/` (contact `PublicRecords.Request@raleighnc.gov`). The portal root answers `204` with no body: it is a JavaScript application behind its own sign-in, with no read-only query API. This skill does not submit records requests, authenticate, or scrape the portal, so incident narratives and fire inspection history are out of scope.

If a caller needs them, the honest answer is that the City requires a public-records request through that portal. Do not reconstruct the old adapter, and do not treat the dead host as a temporary failure.

## Commands

```bash
# Published aggregate reports (official index, no scraping)
scripts/raleigh fire reports --year 2025 --quarter 1

# Exact ArcGIS incident-report summary by date or incident number
scripts/raleigh fire reports --date 2026-07-24
scripts/raleigh fire reports --incident-number 26-032170
```

`--year`/`--quarter` select the published index and cannot be combined with `--date`/`--incident-number`. With no selector, the command returns the published index. There is no narrative, inspection, or insecure-HTTP flag on this command group.

## Failure Policy

- Empty or whitespace-only selectors are rejected before network access.
- Non-canonical dates are rejected before network access.
- Missing ArcGIS fields, invalid features, or a result-cap overflow fail visibly.
- Empty ArcGIS output is missing evidence, not proof that no report exists; the rolling feed may lag RFD's own records, and the published aggregates are the citable totals.

## Exclusions

No bulk crawling, report enumeration, authentication, invoice retrieval or payment, private contact access, public-records submission, write operation, arbitrary URL traversal, or inspection-report detail retrieval is implemented.
