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
