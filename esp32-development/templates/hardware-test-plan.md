# Hardware test plan and run record

Fill unknown fields explicitly; resolve execution prerequisites before using hardware. This worksheet is not an executable configuration or authorization.

## Scope and authority

- Product behavior and requirement revision:
- Authorized DUTs, peers, bench operations, network, and validity period:
- Excluded operations; destructive/security changes requiring a separate directive:
- Target/scope/recovery confirmation evidence:
- Owner and exclusive resource reservation:
- Stop conditions and retry/flash budget with rationale:
- Safe inactive state and fallback if the runner disappears:

## Identity and reproducibility

- Exact board/SoC/module/revision and authoritative schematic/datasheets:
- USB identity, port, bench slot, power switch, instrument channels:
- Firmware source revision and dirty state:
- Toolchain/container/framework/test plugin versions:
- Build configuration, partition table, generated flash arguments:
- Image digests; build/run artifact provenance:
- Running-image confirmation method/result:
- Debug-symbol identity and release/test-hook differences:

## Commissioning

| Check | Method/source | Observed evidence | Status |
|---|---|---|---|
| Electrical limits, wiring, output inactive state | | | |
| Known stimulus/reference detected | | | |
| Deliberate benign mismatch fails | | | |
| DUT/peer/port/instrument mapping | | | |
| Reset and actual power removal; back-power checked | | | |
| Management path survives test-network disruption | | | |
| Cleanup on partial setup/failure/interruption | | | |

Record commissioning date/topology and when it must be rechecked.

## Requirement-to-test matrix

| Requirement ID | Case ID | Host/target/bench/field | Initial state and stimulus | Independent oracle/observation | Expected result | Limit/deadline source | Artifact |
|---|---|---|---|---|---|---|---|
| | | | | | | | |

- Frozen required case roster and selection rules:
- Captured vector/reference provenance; negative oracle check:
- Run/stimulus correlation; stale serial/retained-message handling:
- Fault layer, route, schedule/seed, proof of injection and restoration:
- Persistent-data preconditions and preservation/migration checks:
- OTA candidate confirmation/rejection/unconfirmed-reboot checks, if applicable:
- Unavailable field/instrument tests, coverage implications, owner:

## Attempt record (repeat without overwriting failures)

- Run ID, candidate revision/digests, DUT and fixture identities:
- Selected/collected case IDs and received result IDs:
- Setup/reset/fault timestamps; clock/correlation method:
- Raw log/measurement paths and digests:
- Observations versus expected result, with units:
- Per-case result: pass / product failure / fixture error / inconclusive / not run:
- Failure hypothesis, evidence, one changed variable, rerun relationship:
- Cleanup result and final power/network/DUT state:
- NVS/calibration/user-data state after reset/update/rollback:
- Missing evidence and remaining acceptance cases:

## Acceptance

- Every required case accounted for on the intended artifact/configuration:
- Product failures resolved with preserved history:
- Fixture errors and missing evidence resolved or explicitly blocking acceptance:
- Physical and field claims supported at their observation boundary:
- Recovery and safe final state confirmed:
- Authorized next action and accountable decision owner:
