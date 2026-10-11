# Hardware test automation

Load when planning repeatable target tests, a remote bench, fault injection, or an agent-driven build/flash/test loop. These are design procedures, not a commissioned bench or permission to operate hardware. Fill `templates/hardware-test-plan.md` first. Use the existing native framework tools; add orchestration only for an observed gap.

## Turn requirements into observable contracts

For each requirement, record the stimulus, initial state, observation point, expected result, tolerance/deadline source, cleanup, and evidence artifact. Assign the fastest tier that can establish the claim. Keep unverified limits `UNKNOWN`; resolve them before executing the affected case.

| Tier | Suitable evidence | Cannot establish alone |
|---|---|---|
| Host | Parser vectors, conversions, state transitions with controlled dependencies | Pin timing, electrical behavior, radio or real flash persistence |
| Target | Chip-dependent behavior, NVS/reboot, peripheral driver integration | Attached load behavior or deployed environment |
| Bench | Real firmware with instruments, simulated peers, controlled AP/broker | All field interference, placement, or service behavior |
| Field | End-to-end behavior in the intended installation | Exhaustive robustness or production certification |

This tier vocabulary comes from [Andreas Spiess's presentation](https://www.youtube.com/watch?v=HmNyyT2poF8). It is a planning aid, not a standard requiring every project to use every tier. A simulator belongs in the host tier and must name its supported chip/peripherals. Preserve the tests that establish physical claims even when host tests pass.

## Prefer supported testing mechanisms

[ESP-IDF's pytest guide](https://docs.espressif.com/projects/esp-idf/en/stable/esp32/contribute/esp-idf-tests-with-pytest.html) documents serial expectations, target/config parametrization, and multi-DUT tests. Test collection is part of the evidence: retain selected IDs, chip, configuration, and received results. `expect` interprets regular expressions; use `expect_exact` for literals. Neither establishes behavior outside its observation point.

[pytest-embedded services](https://espressif-docs.readthedocs-hosted.com/projects/pytest-embedded/en/latest/concepts/services.html) can automatically detect ports and flash firmware. Before invocation, pin the board/port, target, build directory, enabled services, reset/erase behavior, and recovery plan. Treat test setup as hardware mutation, not read-only discovery. Inspect installed-version help and implementation where reset semantics are unresolved; never let automatic detection choose among unconfirmed boards. Skipping flashing requires independent running-image identity evidence, not just a local artifact hash.

[ESP-IDF host applications](https://docs.espressif.com/projects/esp-idf/en/stable/esp32/api-guides/host-apps.html) are experimental, with limited component support and scheduler/mocking differences. Compile the production parser or other portable logic into the host test instead of testing a separately rewritten algorithm. Do not infer multicore or interrupt behavior from host scheduling. [Unity multi-stage tests](https://docs.espressif.com/projects/esp-idf/en/stable/esp32/api-guides/unit-tests.html) support behavior spanning resets; identify the completed stage and reset cause rather than treating a disconnect as success.

For other frameworks, use their supported test tools from `references/native-tool-workflows.md`. Do not transplant ESP-IDF fixtures, partition assumptions, or test menus into another framework.

## Commission and own the bench

Confirm the target, scope, and rollback path before acting. Read-only discovery may proceed without confirmation. Existing authorization can cover a defined sequence; it does not cover additional devices, networks, irreversible security changes, or destructive cleanup.

1. Map each DUT (device under test), peer, power switch, instrument channel, USB identity, port, and physical connection. Validate voltage levels and inactive output states from exact artifacts.
2. Reserve the entire shared resource set for the run. Separate worktrees or containers do not isolate a shared board, AP, broker, relay, or USB hub. A second worker must wait or use separately commissioned resources.
3. Demonstrate the observation path with a known stimulus/reference. Demonstrate that an intentional benign mismatch is detected. A silent sensor or stale serial buffer must not report pass.
4. Exercise the intended reset/recovery path, distinguish software reset from actual supply removal, and check back-power through USB or instruments before claiming a cold power-cycle. Preserve NVS/calibration state unless the case explicitly authorizes changing it.
5. Capture fixture versions, topology, calibration provenance, and baseline state. Recheck after topology changes or suspect failures; commissioning is evidence at a point in time, not immunity to future fixture faults.
6. Define cleanup and interruption behavior before testing. If safe state cannot be confirmed after a timeout, quarantine the bench and report it; do not release it as ready.

For a shared lab, [labgrid's distributed setup](https://labgrid.readthedocs.io/en/latest/getting_started.html) illustrates stable USB matching and acquired resource places. It is an optional architecture, not a dependency of this skill. [Its fixture guidance](https://labgrid.readthedocs.io/en/latest/usage.html) warns that cached state-changing fixtures do not repeat transitions when requested again. Make transitions explicit. [pytest teardown rules](https://docs.pytest.org/en/stable/how-to/fixtures.html) require handling partial setup: cleanup after `yield` does not run when that fixture fails before yielding. Register cleanup after each successful mutation or keep state changes in separate fixtures; verify restoration on setup failure, test failure, and cancellation. Process termination may bypass cleanup, so define an operator or hardware fallback.

## Use independent oracles

A firmware message such as `relay ON` proves that message was emitted. Establish contact switching with an electrically safe observation; establish MQTT delivery with a broker/subscriber observation; establish decoded measurements with independently specified packet vectors or a reference instrument. Give runs and stimuli unique IDs, separate old buffered output/retained messages, and correlate observations to the current stimulus. Retain raw readings before transformations.

Do not derive expected values from the same parser under test. Include valid captured vectors, boundary values, malformed inputs, and a known failing case for the oracle. Review tests and requirements separately from firmware fixes. A change to an expected result needs a requirement/evidence reason and a versioned rubric change; never relax a test solely to turn it green.

Firmware hooks can expose identity, stage, reset cause, or raw samples. Record differences from the production build and keep hooks from bypassing authentication or enabling unintended actuation. [ESP-IDF heap debugging](https://docs.espressif.com/projects/esp-idf/en/stable/esp32/api-reference/system/heap_debug.html) documents instrumentation overhead and incomplete traces. Recheck timing, current, and memory acceptance on the intended release configuration; a trace overflow is incomplete evidence. [Application tracing](https://docs.espressif.com/projects/esp-idf/en/stable/esp32/api-guides/app_trace.html) also buffers data: a trace timeout alone is not proof the application stopped.

## Inject faults at the layer being claimed

Use a dedicated test network and preserve a management/recovery connection independent of the interface being disrupted. Record where each fault is injected, verify it took effect, and verify restoration.

| Fault | Injection/observation contract |
|---|---|
| AP loss or provisioning interruption | Control a dedicated AP; observe association/provisioning state and return to operation after restoration |
| Broker outage, delay, or connection reset | Control a test broker or proxy; observe reconnect and delivery at a subscriber, including duplicate/loss policy |
| DHCP/DNS/time/TLS failure | Control the named service independently; distinguish it from radio failure; retain certificate validation |
| Invalid sensor/protocol data | Use electrically compatible simulator/vectors; check rejection and recovery, not just lack of crash |
| Reset or update interruption | Use disposable hardware and the recorded power/recovery path; check image and persistent data after reboot |

[Toxiproxy](https://github.com/Shopify/toxiproxy) can impair TCP connections routed through it. It does not by itself establish RF loss, AP disassociation, UDP/DNS faults, or BLE behavior. Verify which traffic traverses the proxy. An application-service outage and a radio outage need distinct evidence. Derive schedules and deadlines from requirements or characterized behavior; retain seeds and exact injected events where applicable.

## Test the actual recovery contract

[ESP-IDF OTA documentation](https://docs.espressif.com/projects/esp-idf/en/stable/esp32/api-reference/system/ota.html) ties rollback to OTA partitions, configuration, state, and application confirmation. Test the configured path: confirm a healthy candidate; reboot an unconfirmed candidate; reject a failing candidate; inspect selected image and persistent data afterward. Anti-rollback can exclude an older image, so a saved binary alone is not a recovery guarantee. Do not exercise eFuse changes as ordinary fault injection. OTA completion or an HTTP success does not prove the candidate booted or recovered.

## Bound the feedback loop and preserve evidence

Freeze required case IDs and acceptance criteria before a firmware candidate. Record retry/flash limits and stopping conditions based on the project's risk and time budget; no universal iteration count is implied. Run relevant host checks before slower physical checks, then execute every required physical/field case for final acceptance. Impact-based subsets help iteration but cannot silently omit required acceptance cases.

For each attempt retain source revision/dirty state, toolchain/container identity, sdkconfig and partitions, image digests and generated flash arguments, DUT/fixture identity, selected case IDs, fault events, raw observations, timestamps, resets, cleanup outcome, and verdicts. Bind the flashed artifacts to the build and confirm the running image. Debug symbols must match the failing image. Redact credentials without discarding non-secret diagnostics.

Classify outcomes separately:

- **Product failure:** valid observation contradicts the requirement.
- **Fixture/infrastructure error:** prerequisites, control, or observation failed.
- **Inconclusive/not run:** required evidence is absent, skipped, stale, or mismatched.
- **Pass:** valid evidence satisfies the named requirement under recorded conditions.

Preserve the first failure and every rerun; a later pass does not erase intermittent failure. Diagnose one hypothesis at a time. Stop on unsafe electrical state, identity mismatch, lost fixture ownership, unconfirmed cleanup, exhausted budget, or repeated failure without a new evidenced hypothesis. Report the unresolved case and recovery state. Passing the selected tests establishes those contracts under those conditions, not general device reliability or permission to ship.
