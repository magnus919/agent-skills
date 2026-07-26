# Raleigh Fire Reports and Inspections

## Source Contract Review

Reviewed 2026-07-26:

| Source | Contract | Role |
|---|---|---|
| Raleigh referral | `https://raleighnc.gov/fire/services/update-your-fire-contact-information` | Official public referral to the RFD Report System |
| ArcGIS item | `c983765e304a41d19087c8d95aa46d54` | Authoritative rolling fire-incident summaries |
| ArcGIS layer | `https://services.arcgis.com/v400IkDOw1ad7Yad/arcgis/rest/services/Fire_Incidents_Past_Month/FeatureServer/0` | Query-capable JSON/GeoJSON/PBF layer |
| RFD root | `http://rfdreports.net/` | Server-rendered report and inspection forms |

The ArcGIS layer advertises `Query` capability, UTC date fields, and the required report fields. Exact-date queries use a half-open UTC interval; exact incident-number queries use escaped equality. The command requests only `incident_number`, dispatch/arrival/clear timestamps, address, station, platoon, and current classification fields, without geometry. Results are capped at 200 and fail rather than paginate or silently truncate.

The RFD site exposed no client-visible JSON or API description during review. Content negotiation and common API paths returned HTML or 404 responses. Its root forms submit directly to these fixed contracts:

| Method | Path | Exact parameters |
|---|---|---|
| POST | `/fd_date.php` | `date` |
| GET | `/fd_incidentreport.php` | `incidentnumber`, `incidentdate` |
| POST | `/fd_inspection_business_name.php` | `fd_business` |
| POST | `/fd_inspection_business_address.php` | `fd_address` |

The RFD root displays a City disclaimer covering completeness, accuracy, timeliness, and warranties; no separate site-specific terms link was exposed by the reviewed page. `robots.txt` disallows `/inspection`. This adapter does not crawl, enumerate, paginate, or discover URLs. It performs one explicit user lookup at a time. Inspection result pages contain report and invoice links; report identifiers and validated source links are preserved, while invoice links are discarded and never followed or emitted.

## Transport Gate

RFD did not provide a usable TLS endpoint during review. The general Raleigh HTTP client remains HTTPS-only. A separate RFD client permits only `http://rfdreports.net` on the default port and only the four contracts above. It rejects redirects, extra parameters, alternate hosts, arbitrary paths, oversized responses, and unrecognized HTML.

Every RFD operation requires `--acknowledge-insecure-rfd`. This acknowledgement is invocation-local and is never inferred from configuration. Date fallback additionally requires `--allow-rfd-fallback` and runs only after an exact ArcGIS date query returns no records. Inspection business names and addresses cross the network unencrypted.

## Commands

```bash
# Structured ArcGIS only
scripts/raleigh fire reports --date 2026-07-24
scripts/raleigh fire reports --incident-number 26-032170

# One exact narrative after the ArcGIS incident resolves its date
scripts/raleigh fire reports --incident-number 26-032170 \
  --include-narrative --acknowledge-insecure-rfd

# Date fallback only if ArcGIS returns no records
scripts/raleigh fire reports --date 2026-07-24 \
  --allow-rfd-fallback --acknowledge-insecure-rfd

# RFD inspection forms
scripts/raleigh fire inspections --business "Example Market" \
  --acknowledge-insecure-rfd
scripts/raleigh fire inspections --address "100 Example St" \
  --acknowledge-insecure-rfd
```

## Failure Policy

- Empty or whitespace-only selectors are rejected before network access.
- Missing ArcGIS fields, invalid features, or a result-cap overflow fail visibly.
- Changed RFD headers, malformed rows, invalid links, mismatched narrative identifiers, and error pages fail visibly.
- Empty ArcGIS output is missing evidence, not proof that no report exists; the rolling feed may lag.
- Empty recognized RFD tables are valid no-result responses.

## Exclusions

No bulk crawling, report enumeration, authentication, invoice retrieval or payment, private contact access, write operation, arbitrary URL traversal, or inspection-report detail retrieval is implemented.
