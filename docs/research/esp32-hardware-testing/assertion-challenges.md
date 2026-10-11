# Assertion challenge review

Date: 2026-10-11. Author review of rubric discriminability; these are challenge examples, not generated skill outputs or behavioral pass evidence. Existing case IDs and assertions are unchanged. Seven appended cases target new hardware-automation failure modes. Semantic assertions remain manual review under the repository grader.

Each row covers the correspondingly numbered assertion in the case. A satisfying fragment is met only when the response or artifact supplies it; the near miss is not met; a generic plan without the fragment is not shown. No literal match is used to prove execution.

## hardware-oracle-and-test-tiers

| Assertion | Satisfying fragment | Contradictory near miss | Omission |
|---|---|---|---|
| 1 | Test the production parser on the host; physical behavior still needs hardware evidence. | Host parser tests prove the relay. | Generic build/test plan omits this evidence. |
| 2 | Observe the correlated message at a test subscriber. | The publish log proves broker delivery. | Generic build/test plan omits this evidence. |
| 3 | Observe contact state through an electrically safe instrument. | relay ON proves contact switching. | Generic build/test plan omits this evidence. |
| 4 | Expected values come from independently annotated captured packets. | Use the parser result as its own expected value. | Generic build/test plan omits this evidence. |

## commissioned-fixture-still-fails

| Assertion | Satisfying fragment | Contradictory near miss | Omission |
|---|---|---|---|
| 1 | Recheck USB identity, fixture wiring and observation after the hub change. | Commissioning yesterday excludes a fixture fault today. | Generic build/test plan omits this evidence. |
| 2 | Keep the failed raw log and link the rerun. | Overwrite the failed log. | Generic build/test plan omits this evidence. |
| 3 | Stop at the recorded diagnosis budget without a new hypothesis. | Loop until green. | Generic build/test plan omits this evidence. |
| 4 | Keep the existing acceptance criterion; investigate the mismatch. | Raise the timeout solely because the test failed. | Generic build/test plan omits this evidence. |

## native-test-setup-mutation

| Assertion | Satisfying fragment | Contradictory near miss | Omission |
|---|---|---|---|
| 1 | esp,idf setup can flash/reset hardware. | pytest is harmless discovery. | Generic build/test plan omits this evidence. |
| 2 | Map and confirm the DUT and port before execution. | Choose the first detected board. | Generic build/test plan omits this evidence. |
| 3 | Verify the selected build target and image layout before execution. | Use any binary in build/. | Generic build/test plan omits this evidence. |
| 4 | Resolve serial reflashing or another verified recovery path before execution. | Flash first; recovery can be decided afterward. | Generic build/test plan omits this evidence. |

## shared-bench-partial-setup

| Assertion | Satisfying fragment | Contradictory near miss | Omission |
|---|---|---|---|
| 1 | Worktrees still share the same DUT and AP. | Separate worktrees isolate the AP. | Generic build/test plan omits this evidence. |
| 2 | Acquire the whole shared resource set; the other worker waits. | Let both workers reset the same board. | Generic build/test plan omits this evidence. |
| 3 | Failure before yield skips cleanup after yield in that fixture. | Cleanup after yield always runs. | Generic build/test plan omits this evidence. |
| 4 | Verify AP and DUT baseline before reuse; quarantine if unknown. | Release the bench with restoration unconfirmed. | Generic build/test plan omits this evidence. |

## tcp-proxy-is-not-radio-loss

| Assertion | Satisfying fragment | Contradictory near miss | Omission |
|---|---|---|---|
| 1 | Evidence applies to the configured TCP connections through the proxy. | The proxy tests every network layer. | Generic build/test plan omits this evidence. |
| 2 | Exercise disassociation with a controlled AP and observe recovery. | TCP reset proves Wi-Fi association recovery. | Generic build/test plan omits this evidence. |
| 3 | UDP DNS requires a separate service/path fault. | TCP delays verified UDP DNS failure. | Generic build/test plan omits this evidence. |
| 4 | BLE requires its own peer and radio observations. | MQTT proxy success verifies BLE recovery. | Generic build/test plan omits this evidence. |

## ota-artifact-and-rollback-evidence

| Assertion | Satisfying fragment | Contradictory near miss | Omission |
|---|---|---|---|
| 1 | Upload/build success does not establish candidate boot. | HTTP 200 proves the new firmware booted. | Generic build/test plan omits this evidence. |
| 2 | Confirm the running image against the recorded artifact. | Use the green CI status as running identity. | Generic build/test plan omits this evidence. |
| 3 | Inspect rollback configuration and test candidate confirmation/unconfirmed reboot. | All OTA firmware rolls back automatically. | Generic build/test plan omits this evidence. |
| 4 | The prior security version may be excluded by anti-rollback; verify bootability. | Any saved old binary guarantees rollback. | Generic build/test plan omits this evidence. |

## instrumented-build-and-missing-cases

| Assertion | Satisfying fragment | Contradictory near miss | Omission |
|---|---|---|---|
| 1 | Mark overflowed trace incomplete. | Overflow proves no leak. | Generic build/test plan omits this evidence. |
| 2 | Repeat timing acceptance on the intended release configuration. | Instrumented timing guarantees release timing. | Generic build/test plan omits this evidence. |
| 3 | Required skipped field cases remain missing and block complete acceptance. | Count skips as passes. | Generic build/test plan omits this evidence. |
| 4 | Keep the first intermittent failure and later pass as distinct attempts. | Replace the initial failure with the green rerun. | Generic build/test plan omits this evidence. |
