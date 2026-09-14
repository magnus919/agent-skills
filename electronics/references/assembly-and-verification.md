# Assembly and verification

Acceptance is a chain from physical workmanship to observed behavior.

## Unpowered inspection

Inspect orientation, reference designators, solder bridges, wetting, lifted
pads, connector seating, strain relief, and selectable pull-ups/address links.
Check intended continuity and rail-to-rail/signal shorts with power removed;
discharge capacitors first. Compare the assembly against the current BOM,
schematic, layout, and assembly revision. Photograph or annotate anomalies.

## Controlled first power

Use a current-limited source when appropriate. Start with loads disabled and
measure rail voltage, startup/steady current, reset behavior, and temperature.
Add peripherals and outputs one at a time. Verify idle levels before enabling
drivers. A current limit is a protective aid, not a replacement for a supply
budget or fault analysis.

## Functional acceptance

Require an identity-level check for each bus device, a known input/output
response, and documented reset and power-cycle behavior. For I2C, retain the
raw capture or transaction log, address convention, measured rise time,
effective pull-up, and recovery result. For analog or timed behavior, record
calibration/reference, sample conditions, tolerance, and measurement setup.

Repeat critical tests after mechanical handling and any relevant thermal or
power condition. Record exact board/component/firmware revisions and every
open risk. “It worked once” is not an acceptance criterion.

| Failure at acceptance | Containment | Evidence needed before release |
|---|---|---|
| Rail short or excess startup current | power off; isolate branch; inspect orientation/bridges | corrected inspection and current trace |
| Correct rail, wrong idle state | disable load; check reset pulls and external straps | schematic-to-measured state comparison |
| Bus responds but identity fails | stop application writes; preserve raw capture | documented identity read and address convention |
| Intermittent after handling | repeat visual/continuity and capture under movement | reproducible mechanical condition or closure |
| Recovery leaves line low | keep controller quiescent; reset/power-cycle holder | before/after line capture and owner |

Release requires a named disposition for every failure: fixed and retested,
accepted with an explicitly bounded risk, or blocked pending an artifact or
measurement. A passing functional test cannot waive an unresolved electrical
limit.

The acceptance artifact is complete when another operator can reproduce the
test, distinguish design evidence from instrument setup, and see the rollback
or recovery path for every state-changing test.

## Acceptance stage record

At inspection, record component reference, defect class, image identifier, and
disposition. At unpowered test, record meter mode, lead resistance, test points,
and measured values; a continuity beep alone is insufficient. At first power,
record current-limit setting, source voltage, startup peak, steady current,
rail ripple, reset reason, and temperature. At functional test, record stimulus,
expected response, actual response, repeat count, and environmental condition.

For a soldered I2C connector, visual inspection may show correct pin placement,
while end-to-end resistance proves only a low-current path. Far-end idle voltage,
rise time with the actual probe, and identity readback establish separate facts.
If those disagree, retain all results and localize the defect instead of marking
the connector “passed.”

Release is a disposition, not a checkbox: passed and repeatable, accepted with
an explicitly bounded risk and owner, or blocked pending evidence. Rework must
repeat the tests affected by the rework.
