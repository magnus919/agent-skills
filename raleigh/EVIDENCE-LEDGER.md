# Raleigh v2 Evidence Ledger

## Intent

- Implement the `raleigh-v2` milestone as a read-only, bounded Raleigh civic-data CLI.
- Preserve the legacy command contract while adding live catalog discovery, imagery, geocoding, transit, development, civic-content, and meetings adapters.
- Expose only guest-public data and verify behavior at deterministic and live service boundaries.

## Inspected artifacts

- `raleigh/scripts/raleighlib/core.py`: HTTPS host allowlist, read-only method policy, bounded redirects, response caps, cache behavior, and atomic file writes.
- `raleigh/scripts/raleighlib/hub.py`: live Hub discovery, pagination, normalization, caching, and title resolution.
- `raleigh/scripts/raleighlib/arcgis.py`: ArcGIS metadata, pagination, query, download, and Esri-to-GeoJSON conversion.
- `raleigh/scripts/raleighlib/imagery.py`: ImageServer metadata, export, identify, and statistics.
- `raleigh/scripts/raleighlib/geocode.py`: forward, reverse, suggestion, and batch geocoding.
- `raleigh/scripts/raleighlib/transit.py`: bounded GTFS archive parsing and GTFS-Realtime decoding.
- `raleigh/scripts/raleighlib/development.py`: guest-public EnerGov search, permit detail, and inspection output allowlists.
- `raleigh/scripts/raleighlib/civic.py`: paginated RaleighNC.gov JSON:API filtering and RSS.
- `raleigh/scripts/raleighlib/meetings.py`: upcoming and historical eSCRIBE meeting retrieval.
- `raleigh/scripts/raleighlib/cli.py`: argument compatibility, JSON output, safe downloads, and type-aware catalog validation.
- `raleigh/tests/test_raleigh.py`: deterministic contract, safety, adapter, and CLI tests.
- `raleigh/evals/evals.json`: five output-quality cases.
- `raleigh/tests/fixtures/`: deterministic GTFS, GTFS-Realtime, eSCRIBE, and API fixtures.

## Design decisions

- A modular `raleighlib` package replaces the monolithic implementation while the extensionless `scripts/raleigh` entrypoint remains the public interface.
- Hub discovery includes datasets, documents, and applications, but `catalog-check` validates only ArcGIS `FeatureServer`, `MapServer`, and `ImageServer` records with defined metadata contracts.
- The host allowlist includes the fixed Raleigh, Wake County, GoRaleigh, eSCRIBE, Tyler, and ArcGIS service hosts used by discovered public records. Only HTTPS default port 443 is accepted. Redirect targets are checked before requests, and sensitive headers and bodies are not preserved across origins.
- Non-GET methods are rejected except for host-and-path-scoped read-only ArcGIS queries and batch geocoding, EnerGov searches, and the eSCRIBE historical-meetings page method.
- Civic filtering is client-side after bounded JSON:API pagination because Raleigh rejects the attempted server-side full-text/date filter structures.
- EnerGov output is normalized to explicit guest-visible scalar subfields; nested email, phone, and unrelated backend fields are not returned.
- The vendored GTFS-Realtime binding was regenerated from `gtfs-realtime.proto` using protoc 31.1 and requires `google.protobuf>=6.31.1,<7`. No runtime-version bypass remains.
- Static GTFS extraction enforces per-member and aggregate expansion caps; output writes use atomic no-replace publication without `--force`, reject destination symlinks and races, and CSV export neutralizes spreadsheet formulas.

## Deterministic verification

- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest raleigh/tests/test_raleigh.py`: **189 tests passed**.
- `ruby scripts/validate-skills.rb`: **107 canonical skills validated**.
- `ruby scripts/test-validate-skill-quality.rb`: **19 runs, 159 assertions, 0 failures**.
- `ruby scripts/validate-skill-quality.rb --base origin/main`: **1 changed skill, 0 errors, 0 warnings**.
- `python3 scripts/test-eval-coverage.py`: **18 tests passed**.
- `python3 scripts/eval-coverage.py --modified-from origin/main`: ratchet passed.
- `python3 scripts/check-artifacts.py`: all generated-artifact checks passed.
- `ruby scripts/test-gen-llms-txt.rb`: **5 runs, 45 assertions, 0 failures**.
- `git diff --check`: passed.
- `skills-ref validate raleigh`: not run because `skills-ref` is not installed; the repository validator above passed.

## Live verification

The following public service boundaries were exercised successfully on 2026-07-23:

- Hub catalog discovery returned normalized IDs, titles, types, and canonical URLs.
- `catalog-check --full --json` checked **190 ArcGIS service records with 0 failures**; non-service documents and applications were intentionally skipped.
- Feature querying returned a valid GeoJSON `FeatureCollection`.
- ImageServer identify and statistics returned structured responses; a bounded 64x64 export wrote a 2,308-byte image.
- Forward and reverse geocoding returned structured matches; suggestions returned a `magicKey`.
- Batch geocoding wrote two rows, one matched and one unmatched, while preserving source-row columns and identities.
- Static GTFS route parsing returned live route data.
- GTFS-Realtime vehicle positions and trip updates each returned a timestamped response envelope with a live entity; alerts returned a timestamped envelope with a valid empty entity list.
- EnerGov permit search resolved `BLDNR-009249-2022`; detail and bounded inspections returned normalized guest-public fields without inspector email addresses.
- RaleighNC.gov news, events, projects, and RSS returned live filtered content.
- eSCRIBE returned upcoming meetings and historical meetings for 2025.
- Sampled live and cached catalog checks passed before the full check.

## Security and privacy verification

- Deterministic tests cover HTTPS-only default-port enforcement, implicit-body POST enforcement, host-scoped POST and redirect policy, cross-origin body rejection, atomic no-clobber races, predictable temporary-file symlinks, response and pagination bounds, CSV formula neutralization, strict public civic status, and nested EnerGov scalar normalization.
- Public development output was inspected for nested backend and contact fields; search, permit detail, and inspections emit only explicit scalar projections.
- No API keys or authenticated endpoints are required.

## Remaining boundaries

- Upstream public services may change after this verification date; catalog validation and deterministic fixtures are the detection mechanisms.
- `skills-ref` remains unavailable locally, so only the repository's canonical skill validator was exercised.
- No commit, push, pull request, CI run, deployment, or merge is claimed by this ledger.

## Issue 124 Addendum: Fire Protection Proximity

### Intent

- Add read-only Wake County MAR fire-protection lookup by address or CSAID.
- Return only source-provided station ranks, road-network distances, ISO values, and nearest-hydrant distance.
- Reject ambiguous address resolution and detectable source drift instead of guessing.

### Design decisions

- `--address` uses the official Raleigh locator, then resolves the geocoded point through the public Wake County MAR Addresses layer. An exact structured street/subaddress match wins; otherwise a unique base address is preferred. A tied top geocoder result or multiple eligible CSAIDs is an error.
- `--csaid` queries the official fire-protection table directly.
- Required source fields are checked on each lookup. Extra fields are tolerated; missing required fields and inconsistent hydrant distances fail clearly.
- Distance units remain `null` in JSON because the source metadata does not advertise units. Raw distance values are not converted or labeled with guessed units.
- Hydrant locations are not claimed or returned because the source exposes only `Hydrant_Distance`.

### Verification

- `python3 -m pytest tests/test_raleigh.py`: **308 passed** with one pre-existing import deprecation warning.
- `python3 -m ruff check raleigh/scripts/raleighlib/fire_protection.py raleigh/scripts/raleighlib/cli.py`: passed.
- `python3 scripts/validate-evals.py raleigh`: all 8 repository eval manifests validated.
- `ruby scripts/validate-skills.rb`: **107 canonical skills validated**.
- `ruby scripts/validate-skill-quality.rb --base origin/main`: **1 changed skill, 0 errors, 0 warnings**.
- `python3 scripts/eval-coverage.py --modified-from origin/main`: ratchet passed; Raleigh remains schema-valid.
- `git diff --check`: passed.
- Live `fire protection --address "222 W Hargett St, Raleigh" --json`: resolved CSAID `2734541` and returned three ranked stations from item `8ab8c4f1a8eb473bacfcc1a1c1980b6c`.
- Live `fire protection --address "222 W Hargett St STE 106, Raleigh" --json`: resolved the explicit suite to CSAID `5131326`, not the building-level CSAID.
- Live `fire protection --csaid 2734541 --json`: returned the same station and hydrant source values.

### Remaining boundaries

- The service is updated nightly, so future upstream changes remain outside this verification window; required-field checks provide bounded drift detection.
- No emergency-response accuracy, distance unit, hydrant location, commit, push, pull request, CI run, deployment, or merge is claimed.

## Issue 125 Addendum: Guarded Fire Reports and Inspections

### Intent and authority

- Add exact Raleigh fire-report lookup through the authoritative ArcGIS past-month layer.
- Permit RFD HTML fallback, one-record narratives, and business/address inspection searches only through explicit, invocation-local acknowledgement of unencrypted HTTP.
- Modify the local Raleigh skill only. No publish, deploy, merge, authentication, payment, or write authority was used.

### Source-contract evidence

- Reviewed the official Raleigh referral, ArcGIS item `c983765e304a41d19087c8d95aa46d54`, live layer metadata, RFD root forms, root disclaimer, reported robots boundary, and transport behavior on 2026-07-26.
- The ArcGIS layer advertises `Query`, UTC date fields, JSON/GeoJSON/PBF, and the documented incident fields. Exact queries request only the report output fields and no geometry.
- Live RFD contracts matched `POST /fd_date.php`, `GET /fd_incidentreport.php`, `POST /fd_inspection_business_name.php`, and `POST /fd_inspection_business_address.php`.
- RFD exposed plain HTTP only during review. The isolated client rejects redirects, alternate origins, ports, paths, parameters, oversized bodies, empty inputs, and unrecognized HTML. The general HTTPS allowlist was not relaxed.
- Inspection result pages exposed report and invoice links. Invoice links are discarded and never followed or emitted. Upstream links with unescaped `#` values are rebuilt only from validated row fields and the fixed report path.

### Verification

- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest raleigh/tests/test_raleigh.py`: **335 tests passed**.
- `python3 -m unittest raleigh.tests.test_raleigh.FireReportTests raleigh.tests.test_raleigh.RFDReportAdapterTests`: **27 focused tests passed**.
- `python3 -m ruff check raleigh/scripts/raleighlib/fire.py raleigh/scripts/raleighlib/rfd_reports.py raleigh/scripts/raleighlib/cli.py`: passed.
- `python3 scripts/validate-evals.py raleigh`: **11 eval manifests validated**.
- `ruby scripts/validate-skills.rb`: **110 canonical skills validated**.
- `ruby scripts/validate-skill-quality.rb --base origin/main`: **1 changed skill, 0 errors, 0 warnings**.
- `python3 scripts/eval-coverage.py --modified-from origin/main`: ratchet passed; Raleigh remains schema-valid.
- Live `fire reports --date 2026-07-24 --json`: returned exact-date ArcGIS records with authoritative source labels and the canonical layer URL.
- Live `fire reports --incident-number 26-032170 --include-narrative --acknowledge-insecure-rfd --json`: resolved one ArcGIS incident and fetched exactly one matching RFD narrative with an insecure-transport warning.
- Live `fire inspections --business "WALMART #5118" --acknowledge-insecure-rfd --json`: returned three inspection records, preserved the `#5118` business identifier in canonical report links, and emitted no invoice URLs or identifiers.
- The first live ArcGIS run exposed an invalid `outSR=None` parameter; the implementation was corrected to use ArcGIS's valid default and the live command then passed.
- The first live inspection run exposed upstream unescaped `#` fragments; canonical reconstruction and a regression fixture were added before the live command passed.

### Remaining boundaries

- RFD is an insecure, fragile HTML source. Acknowledgement does not make transport secure; it only makes the risk explicit.
- Upstream schemas, selectors, forms, and availability can change after the verification date. Required-field and parser-contract checks fail visibly when detectable.
- Deterministic fixtures exercise results, no-results, schema/markup changes, service/error pages, malformed fragments, and recent-record fallback. They do not prove future upstream stability.
- No bulk enumeration, authenticated action, invoice retrieval or payment, private contact access, inspection-detail retrieval, write operation, commit, push, pull request, CI run, deployment, or merge is claimed.

## Issue 126 Addendum: Official Police and Fire Aggregate Statistics

### Intent and authority

- Expose official RPD and RFD published statistics and report indexes without presenting incident-row calculations as official totals.
- Preserve RFD medical totals as aggregate-only data that cannot be joined to or used to infer excluded incident records.
- Modify the local Raleigh skill only. No publish, deploy, merge, document download, or PDF-extraction authority was used.

### Inspected artifacts and decisions

- Reviewed issue `#126`, the official RPD crime-data page, the official RFD statistics page, their Drupal JSON:API service nodes and included paragraph resources, existing police/fire adapters, CLI routing, tests, references, and recent fire-report commit `4eaf5aa`.
- The official pages expose one stable structured boundary: service-node JSON:API responses with included HTML fragments. RFD publishes current incident totals and sprinkler-save tables inline; RPD currently publishes document links only.
- Chose one shared JSON:API adapter over separate page scrapers. Rejected incident-row aggregation because source coverage differs, and rejected PDF parsing because no stable tested extraction contract exists.
- Returned documents are restricted by agency to the official Raleigh page or City government-cloud PDF path, sanitized, checked for traversal and malformed URL components, and availability-probed with `HEAD`. Redirect targets must satisfy the same agency-specific contract.
- Fire `reports --date/--incident-number` remains the existing incident-report mode. `fire reports --year/--quarter` and no-selector mode use the aggregate publication index.

### Files changed

- Added `scripts/raleighlib/public_safety_stats.py`, representative police/fire JSON:API fixtures, and `references/public-safety-statistics-reference.md`.
- Updated `scripts/raleighlib/core.py`, `scripts/raleighlib/cli.py`, `tests/test_raleigh.py`, `SKILL.md`, `README.md`, police/fire references, and `evals/evals.json`.

### Verification

- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest raleigh/tests/test_raleigh.py`: **364 tests passed**.
- `python3 -m ruff check raleigh/scripts/raleighlib/core.py raleigh/scripts/raleighlib/public_safety_stats.py raleigh/scripts/raleighlib/cli.py`: passed.
- `python3 scripts/validate-evals.py raleigh`: **11 eval manifests validated**.
- `ruby scripts/validate-skills.rb`: **110 canonical skills validated**.
- `ruby scripts/validate-skill-quality.rb --base HEAD`: **1 changed skill, 0 errors, 0 warnings**.
- `python3 scripts/eval-coverage.py --modified-from HEAD`: ratchet passed; Raleigh remains schema-valid.
- Live `police reports --year 2025 --quarter 4 --json`: returned the official `Q4 stats` label and canonical government-cloud PDF URL after an availability probe.
- Live `police stats --year 2025 --json`: returned the annual and quarterly publication index with an explicit document-only warning and no fabricated totals.
- Live `fire stats --year 2026 --json`: returned seven official published categories, including medical `7,882`, source revision/retrieval metadata, the annual document URL, and the aggregate-only privacy warning.
- Live `fire reports --year 2025 --quarter 1 --json`: returned the canonical official quarterly page.
- Live `fire reports --date 2026-07-24 --json`: exercised the unchanged ArcGIS incident-report path successfully.
- Review passes found and then verified fixes for terminal-control handling, path traversal and URL components, empty or missing sections and tables, document availability, redirect targets, malformed or ambiguous JSON:API relationships, and eval coverage.

### Remaining boundaries and follow-up triggers

- PDF contents were not parsed or semantically verified. Add extraction only after a stable format and representative regression fixtures exist.
- `HEAD` availability confirms reachability at request time, not document correctness or future availability.
- Upstream node IDs, headings, table headers, publication labels, or origins may change. Detectable changes fail visibly; revise the adapter and fixtures only after re-verifying the official source contract.
- No model-backed eval run, CI run, commit, push, pull request, deployment, release, or merge is claimed.
- Roll back the aggregate adapter and CLI wiring if the official site removes JSON:API access or publication links cannot be validated without broadening the trust boundary.
