# Fault isolation

Write one leading hypothesis per branch. For each, state the predicted
observation, least-intrusive decisive test, mutation or safety effect, result,
and next branch. Keep power, topology, electrical levels, timing, protocol,
driver, and application assumptions as separate layers.

| Observation | Prediction to test first | Decisive evidence |
|---|---|---|
| Rail correct at rest, resets under load | supply impedance or transient current | scope rail during event; measure source current |
| I2C line never rises | short, unpowered device, wrong rail, or held line | resistance/power isolation and scope idle level |
| Slow rise, marginal high | excessive C, duplicate/weak pull-up, probe loading | measured `tr`, effective pull-up, repeat with low-C probe |
| Address ACKs, identity wrong | address notation, wrong device, pointer/order | documented identity register and raw capture |
| NAK after reset only | readiness/reset timing or power sequence | reset-to-first-command timing and status polling |
| Bus hangs in software | missing timeout or unsupported stretch | captured SCL/SDA ownership and bounded wait result |
| Probe changes behavior | probe capacitance/ground inductance/loading | compare probe attachments and saved waveforms |

Do not “fix” a symptom by increasing speed, disabling brownout, erasing state,
or adding stronger pull-ups before measuring the layer that failed. Close a
hypothesis only when an observation discriminates it from its nearest rival.
Record absent schematics, datasheets, captures, or labels as blocked evidence.

For an intermittent issue, capture a failing and passing event with the same
trigger and settings. Compare timing, rail droop, ACK position, reset reason,
temperature, and mechanical state. Change one variable at a time and preserve
the firmware, wiring, and instrument revisions.

Exit when the failure is reproduced or bounded to a missing artifact, the next
test has a predicted outcome, and recovery leaves the system in a known state.

## Test quality and localization

Name the observation before running the test. “Read returned zero” is a result;
“device absent” is an inference requiring address, power, reset, and scan-method
evidence. “Continuity passed” is a result; “solder joint good” exceeds what that
test establishes. For each inference, list the nearest competing cause and the
evidence that excludes it.

For intermittent faults, preserve passing and failing captures with the same
trigger, settings, firmware, and physical state. If attaching a probe makes a
fault disappear, treat the probe as a possible pull-up, capacitance, ground
return, or mechanical stabilizer. Remove it and repeat before changing the
circuit. If reducing I2C speed helps, classify it as a timing or signal-
integrity clue, not a root-cause fix.

After three non-converging tests, escalate in a bounded way: identify the
missing exact schematic, datasheet, capture, or known-good comparison; state
the safe next acquisition; and stop the branch until it exists.
